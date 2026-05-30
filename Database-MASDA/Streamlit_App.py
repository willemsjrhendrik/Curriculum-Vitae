import os
import streamlit as st
import mysql.connector
import pandas as pd
import plotly.graph_objects as go
from nilearn import datasets, surface
from stmol import showmol
import py3Dmol
import requests

# --- CONFIGURATION ---
st.set_page_config(page_title="MASDA Navigator v3", layout="wide")


@st.cache_resource
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME", "masda")
    )


# Bilateral MNI coordinates for "Bigger Regions"
REGION_BASE_COORDS = {
    "Prefrontal Cortex":  [15,  45,  30],
    "Amygdala":           [25,  -5, -20],
    "Hippocampus":        [25, -20, -15],
    "Cingulate Cortex":   [ 8,  10,  35],
    "Basal Ganglia":      [20,   5,   0],
    "Thalamus":           [15, -15,  10],
    "Insular Cortex":     [35,  10,   5],
    "Midbrain":           [ 5, -25, -15],
    "Brainstem":          [ 5, -35, -30],
    "Parietal Cortex":    [20, -50,  40],
}

CIRCUIT_LINE_COLORS = {
    "Dorsal Executive System":      "#00FFFF",
    "Ventral Affective System":     "#FF00FF",
    "Salience Network":             "#FFA500",
    "Default Mode Network (DMN)":   "#00FF00",
    "Central Executive Network":    "#1E90FF",
    "Fear/Threat Circuit":          "#FF4500",
    "Mesolimbic Reward Circuit":    "#FFD700",
}


# --- HELPERS ---
def fetch_pdb_id(gene_symbol):
    """Dynamically find the best experimental structure for the gene."""
    try:
        url = "https://search.rcsb.org/rcsbsearch/v2/query"
        query = {
            "query": {
                "type": "terminal",
                "service": "text",
                "parameters": {"value": f"{gene_symbol}"}
            },
            "return_type": "entry"
        }
        r = requests.post(url, json=query, timeout=5)
        return r.json()['result_set'][0]['identifier']
    except Exception:
        return None


def render_protein(pdb_id):
    """Molecular viewer for the protein structure."""
    view = py3Dmol.view(query=f'pdb:{pdb_id}')
    view.setStyle({'cartoon': {'color': 'spectrum'}})
    view.addSurface(py3Dmol.VDW, {'opacity': 0.3, 'color': 'white'})
    view.spin(True)
    showmol(view, height=400, width=500)


@st.cache_data
def get_brain_mesh_data():
    fsaverage = datasets.fetch_surf_fsaverage(mesh='fsaverage5')
    return (
        surface.load_surf_mesh(fsaverage.pial_left),
        surface.load_surf_mesh(fsaverage.pial_right)
    )


def format_bool(df):
    """Converts 1/0 or True/False into string True/False for display."""
    if not df.empty and 'is_approved' in df.columns:
        df['is_approved'] = df['is_approved'].apply(
            lambda x: "True" if x == 1 or x is True else "False"
        )
    return df


def build_3d_viz(disorder_hubs, circuits_with_nodes):
    (coords_l, faces_l), (coords_r, faces_r) = get_brain_mesh_data()
    fig = go.Figure()

    # 1. Brain mesh (transparent shell)
    mesh_cfg = dict(color='lightgray', opacity=0.05, hoverinfo='skip', showlegend=False)
    fig.add_trace(go.Mesh3d(
        x=coords_l[:, 0], y=coords_l[:, 1], z=coords_l[:, 2],
        i=faces_l[:, 0], j=faces_l[:, 1], k=faces_l[:, 2], **mesh_cfg
    ))
    fig.add_trace(go.Mesh3d(
        x=coords_r[:, 0], y=coords_r[:, 1], z=coords_r[:, 2],
        i=faces_r[:, 0], j=faces_r[:, 1], k=faces_r[:, 2], **mesh_cfg
    ))

    state_colors = {
        'Hyperactive':  '#ff4b4b',
        'Hypoactive':   '#1f77b4',
        'Dysregulated': '#ffa500',
    }
    plotted_nodes = {}  # {RegionName: HexColor}

    # 2. Draw circuit edges
    for circ_name, nodes in circuits_with_nodes.items():
        line_color = CIRCUIT_LINE_COLORS.get(circ_name, "black")
        for side in [-1, 1]:
            edge_x, edge_y, edge_z = [], [], []
            side_coords = []
            for node_name in nodes:
                if node_name in REGION_BASE_COORDS:
                    pos = REGION_BASE_COORDS[node_name]
                    x, y, z = pos[0] * side, pos[1], pos[2]
                    side_coords.append([x, y, z])
                    status = disorder_hubs.get(node_name)
                    plotted_nodes[node_name] = state_colors.get(status, "#d3d3d3")

            if len(side_coords) > 1:
                for i in range(len(side_coords)):
                    for j in range(i + 1, len(side_coords)):
                        p1, p2 = side_coords[i], side_coords[j]
                        edge_x += [p1[0], p2[0], None]
                        edge_y += [p1[1], p2[1], None]
                        edge_z += [p1[2], p2[2], None]
                fig.add_trace(go.Scatter3d(
                    x=edge_x, y=edge_y, z=edge_z,
                    mode='lines',
                    line=dict(color=line_color, width=4),
                    name=circ_name,
                    legendgroup=circ_name,
                    showlegend=(side == -1),
                    opacity=0.6
                ))

    # 3. Plot region nodes
    node_x, node_y, node_z, node_colors, node_text = [], [], [], [], []
    for side in [-1, 1]:
        for name, node_clr in plotted_nodes.items():
            pos = REGION_BASE_COORDS[name]
            node_x.append(pos[0] * side)
            node_y.append(pos[1])
            node_z.append(pos[2])
            node_colors.append(node_clr)
            node_text.append(name)

    fig.add_trace(go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers+text',
        marker=dict(size=12, color=node_colors, opacity=0.9, line=dict(width=1, color='white')),
        text=node_text,
        textfont=dict(color='black', size=11),
        textposition="top center",
        showlegend=False
    ))

    # 4. Activity state legend entries
    for state, clr in state_colors.items():
        fig.add_trace(go.Scatter3d(
            x=[None], y=[None], z=[None],
            mode='markers',
            marker=dict(size=10, color=clr),
            name=state
        ))

    fig.update_layout(
        scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, bgcolor='white'),
        margin=dict(l=0, r=0, b=0, t=0),
        height=600,
        legend=dict(title="Pathology", yanchor="top", y=0.9, xanchor="left", x=0.05)
    )
    return fig


# --- APP LAYOUT ---
st.title("MASDA: From Disorder to Channel")

conn = get_db_connection()
conn.ping(reconnect=True, attempts=3, delay=1)

nav_mode = st.sidebar.radio(
    "Navigation Perspective",
    ["Clinical Discovery", "Anatomical Discovery", "System Discovery"]
)


# ──────────────────────────────────────────────────────────────────────────
# PAGE: CLINICAL DISCOVERY
# ──────────────────────────────────────────────────────────────────────────
if nav_mode == "Clinical Discovery":
    dis_list = pd.read_sql("SELECT name FROM disorder ORDER BY name", conn)
    selected_dis = st.sidebar.selectbox("Select Diagnosis", dis_list['name'].tolist())

    # Fetch hub data first so we know what to render
    hubs_raw = pd.read_sql("""
        SELECT br.name AS Hub_Region, cds.activity_state,
               c.name AS Circuit_Name, cds.clinical_significance
        FROM circuit_disorder_state cds
        JOIN brain_region br ON cds.region_id = br.region_id
        JOIN circuit c ON cds.circuit_id = c.circuit_id
        WHERE cds.disorder_id = (SELECT disorder_id FROM disorder WHERE name = %s)
    """, conn, params=[selected_dis])

    # Top row: clinical context (left) and 3D brain (right)
    top_col1, top_col2 = st.columns([1.2, 1])

    with top_col1:
        dis_meta = pd.read_sql(
            "SELECT icd_11_code, definition FROM disorder WHERE name = %s",
            conn, params=[selected_dis]
        )
        if not dis_meta.empty:
            st.header(f"Clinical Profile: {selected_dis}")
            icd_code = dis_meta.iloc[0]['icd_11_code']
            def_text = dis_meta.iloc[0]['definition']

            if "Source: http" in str(def_text):
                st.info(f"**ICD-11 Code:** {icd_code}")
            else:
                st.info(f"**ICD-11 Code:** {icd_code}  \n**Clinical Definition:** {def_text}")

        if not hubs_raw.empty:
            st.subheader("1. Anatomical Hub")
            sel_hub = st.selectbox("Focus Parent Region", hubs_raw['Hub_Region'].unique())
            h_desc = pd.read_sql(
                "SELECT description FROM brain_region WHERE name = %s",
                conn, params=[sel_hub]
            )
            if not h_desc.empty:
                st.write(h_desc.iloc[0]['description'])

            hub_data = hubs_raw[hubs_raw['Hub_Region'] == sel_hub].iloc[0]
            st.info(f"**Pathology & Evidence:** {hub_data['clinical_significance']}")

            st.subheader("2. Cellular Population")
            cells = pd.read_sql("""
                SELECT ct.cell_id, ct.name, ct.class, child.name as Precise_Region
                FROM cell_type ct
                JOIN brain_region child ON ct.region_id = child.region_id
                JOIN brain_region parent ON child.parent_id = parent.region_id
                WHERE parent.name = %s
            """, conn, params=[sel_hub])

            if not cells.empty:
                cell_labels = cells.apply(
                    lambda r: f"{r['name']} ({r['class']}) - {r['Precise_Region']}", axis=1
                ).tolist()
                cell_label = st.selectbox("Resident Cluster", cell_labels)
                c_id = int(cells.iloc[cell_labels.index(cell_label)]['cell_id'])
            else:
                st.write("No clusters found.")
                c_id = None
        else:
            st.warning("No pathological hubs linked.")
            c_id = None

    with top_col2:
        if not hubs_raw.empty:
            circuits_dict = {
                circ: pd.read_sql("""
                    SELECT br.name FROM circuit_region cr
                    JOIN brain_region br ON cr.region_id = br.region_id
                    WHERE cr.circuit_id = (SELECT circuit_id FROM circuit WHERE name = %s)
                """, conn, params=[circ])['name'].tolist()
                for circ in hubs_raw['Circuit_Name'].unique()
            }
            st.plotly_chart(
                build_3d_viz(
                    dict(zip(hubs_raw['Hub_Region'], hubs_raw['activity_state'])),
                    circuits_dict
                ),
                use_container_width=True
            )

    st.divider()

    # Bottom row: drugs (left) and protein structure (right)
    if not hubs_raw.empty and c_id:
        st.subheader("3. Putative Molecular Targets & Therapeutics")
        bot_col1, bot_col2 = st.columns([1, 1])

        with bot_col1:
            genes_df = pd.read_sql("""
                SELECT g.symbol FROM cell_gene_expression cge
                JOIN gene g ON cge.gene_id = g.gene_id
                WHERE cge.cell_id = %s
            """, conn, params=[c_id])
            sel_gene = st.selectbox("Target Ion Channel", genes_df['symbol'].tolist())

            relevant_drugs = pd.read_sql("""
                SELECT DISTINCT d.name, d.is_approved
                FROM drug d
                JOIN drug_gene_interaction dgi ON d.drug_id = dgi.drug_id
                JOIN gene g ON dgi.gene_id = g.gene_id
                JOIN drug_indication di ON d.drug_id = di.drug_id
                JOIN disorder dis ON di.disorder_id = dis.disorder_id
                WHERE g.symbol = %s AND dis.name = %s
            """, conn, params=[sel_gene, selected_dis])

            if not relevant_drugs.empty:
                st.success(f"Therapeutics for {selected_dis} targeting {sel_gene}:")
                st.table(format_bool(relevant_drugs))
            else:
                st.warning("No specific psychiatric drugs indexed for this target/disorder path.")
                with st.expander(f"Show other drugs targeting {sel_gene} (different indications)"):
                    all_drugs = pd.read_sql("""
                        SELECT d.name, d.is_approved FROM drug d
                        JOIN drug_gene_interaction dgi ON d.drug_id = dgi.drug_id
                        JOIN gene g ON dgi.gene_id = g.gene_id
                        WHERE g.symbol = %s
                    """, conn, params=[sel_gene])
                    st.dataframe(format_bool(all_drugs))

        with bot_col2:
            pdb_id = fetch_pdb_id(sel_gene)
            if pdb_id:
                st.write(f"**Atomic Structure: {sel_gene} ({pdb_id})**")
                render_protein(pdb_id)


# ──────────────────────────────────────────────────────────────────────────
# PAGE: ANATOMICAL DISCOVERY
# ──────────────────────────────────────────────────────────────────────────
elif nav_mode == "Anatomical Discovery":
    st.header("Anatomical Discovery")
    st.caption("Note: Gene links represent putative mechanistic targets based on excitatory/inhibitory cell class, not raw transcriptomic counts.")

    region_list = pd.read_sql("""
        SELECT name FROM brain_region
        WHERE parent_id IS NULL AND region_id >= 118
        ORDER BY name
    """, conn)
    sel_region = st.sidebar.selectbox("Select Parent Region", region_list['name'].tolist())

    r_desc = pd.read_sql(
        "SELECT description FROM brain_region WHERE name = %s",
        conn, params=[sel_region]
    )
    if not r_desc.empty:
        st.info(r_desc.iloc[0]['description'])

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Linked Disorders")
        st.table(pd.read_sql("""
            SELECT DISTINCT d.name, cds.activity_state
            FROM disorder d
            JOIN circuit_disorder_state cds ON d.disorder_id = cds.disorder_id
            WHERE cds.region_id = (SELECT region_id FROM brain_region WHERE name = %s)
        """, conn, params=[sel_region]))

    with c2:
        st.subheader("Functional Systems")
        st.table(pd.read_sql("""
            SELECT c.name, c.function_type FROM circuit c
            JOIN circuit_region cr ON c.circuit_id = cr.circuit_id
            WHERE cr.region_id = (SELECT region_id FROM brain_region WHERE name = %s)
        """, conn, params=[sel_region]))

    st.divider()

    res_cells = pd.read_sql("""
        SELECT ct.cell_id, ct.name, ct.class, child.name as Precise_Anatomy
        FROM cell_type ct
        JOIN brain_region child ON ct.region_id = child.region_id
        WHERE child.parent_id = (SELECT region_id FROM brain_region WHERE name = %s)
    """, conn, params=[sel_region])

    if not res_cells.empty:
        cell_labels = res_cells.apply(
            lambda r: f"{r['name']} ({r['class']}) - {r['Precise_Anatomy']}", axis=1
        ).tolist()
        sel_cell_label = st.selectbox("Pick Cluster", cell_labels)
        c_id = int(res_cells.iloc[cell_labels.index(sel_cell_label)]['cell_id'])
        st.table(pd.read_sql("""
            SELECT g.symbol, g.family FROM cell_gene_expression cge
            JOIN gene g ON cge.gene_id = g.gene_id
            WHERE cge.cell_id = %s
        """, conn, params=[c_id]))


# ──────────────────────────────────────────────────────────────────────────
# PAGE: SYSTEM DISCOVERY
# ──────────────────────────────────────────────────────────────────────────
elif nav_mode == "System Discovery":
    st.header("System Discovery")
    st.caption("Note: Gene links represent putative mechanistic targets based on excitatory/inhibitory cell class, not raw transcriptomic counts.")

    circ_list = pd.read_sql("""
        SELECT name FROM circuit
        WHERE name != 'Clinical Anatomical Map'
        ORDER BY name
    """, conn)
    sel_circ = st.sidebar.selectbox("Select System", circ_list['name'].tolist())

    circ_details = pd.read_sql(
        "SELECT function_type, description FROM circuit WHERE name = %s",
        conn, params=[sel_circ]
    )
    if not circ_details.empty:
        f_type = circ_details.iloc[0]['function_type']
        desc = circ_details.iloc[0]['description']
        if pd.notna(desc) and desc.strip():
            st.info(f"**Function:** {f_type} \n\n**Canonical Architecture:** {desc}")
        else:
            st.info(f"**Function:** {f_type}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Involved Disorders")
        sys_dis = pd.read_sql("""
            SELECT DISTINCT d.name FROM disorder d
            JOIN circuit_disorder_state cds ON d.disorder_id = cds.disorder_id
            WHERE cds.circuit_id = (SELECT circuit_id FROM circuit WHERE name = %s)
        """, conn, params=[sel_circ])
        if not sys_dis.empty:
            st.table(sys_dis)

    with c2:
        st.subheader("Parent Nodes")
        sys_regs = pd.read_sql("""
            SELECT br.name, cr.role FROM brain_region br
            JOIN circuit_region cr ON br.region_id = cr.region_id
            WHERE cr.circuit_id = (SELECT circuit_id FROM circuit WHERE name = %s)
            AND br.parent_id IS NULL
        """, conn, params=[sel_circ])
        if not sys_regs.empty:
            st.table(sys_regs)

    st.divider()

    if not sys_regs.empty:
        hub = st.selectbox("Explore Parent Hub", sys_regs['name'].tolist())
        cells = pd.read_sql("""
            SELECT ct.cell_id, ct.name, ct.class FROM cell_type ct
            JOIN brain_region child ON ct.region_id = child.region_id
            WHERE child.parent_id = (SELECT region_id FROM brain_region WHERE name = %s)
        """, conn, params=[hub])

        if not cells.empty:
            cell_labels = cells.apply(
                lambda r: f"{r['name']} ({r['class']})", axis=1
            ).tolist()
            sel_cell_label = st.selectbox("Select Cluster", cell_labels)
            c_id = int(cells.iloc[cell_labels.index(sel_cell_label)]['cell_id'])
            st.table(pd.read_sql("""
                SELECT g.symbol, g.family FROM cell_gene_expression cge
                JOIN gene g ON cge.gene_id = g.gene_id
                WHERE cge.cell_id = %s
            """, conn, params=[c_id]))
