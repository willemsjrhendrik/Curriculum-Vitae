# MASDA: Multi-scale Affective System and Disorder Atlas



\## The Problem: The Scale Gap



In psychiatry and neuroscience, researchers typically work at a single level of analysis. Psychiatrists may focus on disorders and symptoms, neuroscientists on circuits, and molecular biologists on cells and genes. When studying affective disorders, this \*\*scale gap\*\* quickly becomes a hurdle — there is no unified map that connects them all.



\## What MASDA Does



MASDA achieves \*\*mechanistic continuity\*\* across scales. It allows a researcher to start with a high-level ICD-11 normalized disorder and navigate a single, logical path down to a specific ion channel in a specific cell cluster — bridging clinical psychiatry and molecular neuroscience in one interface.



The main navigation chain:



```

Disorder (ICD-11) → Circuit → Brain Region → Cell Type → Ion Channel → Therapeutics

```



Associative junction tables capture \*\*state-dependent pathology\*\*, defining how a disease specifically alters each structure (e.g. hyperactivation, hypoactivation, dysregulation).



\## Data Sources



\- \*\*Cell type data\*\*: Allen Brain Cell Atlas (ABC Atlas) and Siletti et al.

\- \*\*Clinical classifications\*\*: ICD-11 (WHO)

\- \*\*Pharmaceutical data\*\*: Drug-gene interaction database



\## Technical Stack



| Component | Technology |

|---|---|

| Database | MySQL (relational schema) |

| Data ingestion | Python + Polars (chosen over Pandas to prevent memory overload on large datasets) |

| Interface | Streamlit |

| 3D brain visualisation | Plotly + Nilearn (fsaverage mesh) |

| Protein structure viewer | py3Dmol + stmol |



\## Example: Bipolar Disorder



To illustrate MASDA's logic chain, consider \*\*Bipolar Disorder\*\* — a mood disorder marked by extreme oscillations between mania and depression, commonly treated with drugs such as Lamotrigine.



1\. \*\*Disorder level\*\*: Select Bipolar Disorder (ICD-11)

2\. \*\*Circuit level\*\*: Key circuits include the \*Ventral Affective System\* and \*Dorsal Executive System\*, visualised in an interactive 3D brain

3\. \*\*Region level\*\*: Certain hubs show pathological activity states — e.g. the ventral striatum (basal ganglia) shows \*\*hyperactivation\*\*, driving manic phases

4\. \*\*Cell level\*\*: Within the basal ganglia, specific cell clusters are identified — e.g. an inhibitory neuron in the nucleus accumbens (part of the ventral striatum)

5\. \*\*Molecular level\*\*: MASDA surfaces putative molecular targets and linked therapeutics — in this case successfully identifying \*\*Lamotrigine\*\* among the results



This illustrates how MASDA closes the scale gap between high-level clinical disorders and molecular targets, enabling more efficient research into complex affective disorders.



\## Running Locally



\### Prerequisites

\- Python 3.9+

\- MySQL server with the MASDA database loaded



\## Navigation Modes



The interface offers three entry points depending on your research perspective:



\- \*\*Clinical Discovery\*\* — start from a disorder and drill down to molecular targets

\- \*\*Anatomical Discovery\*\* — start from a brain region and explore linked disorders and cell types

\- \*\*System Discovery\*\* — start from a functional circuit and explore its components and pathology



