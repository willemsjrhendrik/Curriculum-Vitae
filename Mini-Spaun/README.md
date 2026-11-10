# Mini-Spaun, part 1: semantic pointers in spiking neurons

A step-by-step notebook that rebuilds two core ideas behind **Spaun** (Eliasmith et al., 2012), using **torchhd** for vector symbolic operations and **brian2** for spiking neurons:

1. **Semantic Pointer Architecture (SPA):** concepts as high-dimensional vectors that can be bound, bundled and unbound.
2. **Neural Engineering Framework (NEF):** how a population of spiking neurons can represent such vectors, and how they can be read back out.

The notebook ends with a population of LIF neurons that represents torchhd concepts and bound scenes, with interactive figures of its activity.

## Requirements

- Python 3.12+
- `numpy`, `matplotlib`, `pandas`
- `torch`, `torchhd`
- `brian2`
- `plotly`, `nbformat` (interactive figures)

## Notebook overview

### Part A: Semantic pointers (torchhd)

| Step | Goal | Key result |
|---|---|---|
| 1 | Build a vocabulary of HRR vectors; bind, bundle and unbind a scene | Unbinding COLOR from *COLOR ⊛ RED + SHAPE ⊛ CIRCLE* retrieves RED |
| 2 | Understand why the other bound pair stays hidden | A bound vector resembles neither of its parts (conjunctive coding) |
| 3 | Vary dimensionality D | Signal stays constant; noise shrinks roughly as 1/√D |
| 4 | Bundle more role–filler pairs | A capacity limit emerges from the representation itself |

### Part B: One number in spiking neurons (brian2)

| Step | Goal | Key result |
|---|---|---|
| 5 | Build a population of LIF neurons with encoders, intercepts and gains | NEF encoding: J = gain · (encoder · x − intercept) + 1 |
| 6 | Measure tuning curves | Heterogeneous, rectified, monotonic tuning (ON/OFF families) |
| 7 | Compute linear decoders with least squares | A weighted sum of firing rates recovers x |
| 8–9 | Separate training from testing | Decoders generalise to values they were not fitted on |
| 10–11 | Add trial-to-trial noise | Decoding error ≈ noise SD × decoder norm |
| 12–13 | Regularise the decoders and sweep λ | Optimal λ ≈ (training trials) × (noise variance) |

### Part C: Vectors in spiking neurons

| Step | Goal | Key result |
|---|---|---|
| 14 | 2D population with unit-vector encoders (preferred directions) | Cosine tuning, as in Georgopoulos' motor cortex recordings; accurate decoding of new directions |
| 15 | 16D population (400 neurons) presented with torchhd concepts | Each concept is decoded correctly (cosine ≈ 0.99), also with noise; the similarity structure of the vocabulary is preserved (cf. RSA) |
| 15i | Present a bound scene to the population, decode it, then unbind | RED is retrieved from the decoded scene almost exactly as from the original scene |

### Figures

Interactive Plotly figure of the population's activity for each concept, each bound pair and the full scene, with pattern similarity (mean-centred correlation across neurons) between combinations and their parts:

- **Binding** produces a new activity pattern, dissimilar to its parts.
- **Bundling** keeps the parts recognisable in the population's activity.

## Main takeaways

- Concepts are **patterns of activity** across a population, not single "concept neurons".
- A neuron's **encoder** corresponds to its synaptic weights (its preferred direction); **decoders** correspond to the synaptic weights a downstream population would use to read it out.
- Representation quality is limited by **noise** (controlled by regularised decoders) and by **dimensionality** (chance similarity between random concepts).
- A population of spiking neurons can carry a **structured scene** without destroying the information inside it.

## Next steps (part 2, separate notebook)

- **Connections between populations:** weights W = encoders_B · decoders_Aᵀ, so population B represents what A represents
- **Computing with connections:** transformations and binding performed by neurons
- **Working memory** with recurrent connections
- **Action selection** with a basal ganglia circuit
- **A small task end to end**

## References

- Eliasmith, C. et al. (2012). A large-scale model of the functioning brain. *Science*, 338(6111), 1202–1205.
- Eliasmith, C. & Anderson, C. H. (2003). *Neural Engineering: Computation, Representation, and Dynamics in Neurobiological Systems*. MIT Press.
- Georgopoulos, A. P., Schwartz, A. B. & Kettner, R. E. (1986). Neuronal population coding of movement direction. *Science*, 233(4771), 1416–1419.
- Kriegeskorte, N., Mur, M. & Bandettini, P. (2008). Representational similarity analysis – connecting the branches of systems neuroscience. *Frontiers in Systems Neuroscience*, 2, 4.

## AI usage

This notebook was developed as a learning exercise with an AI tutor (Claude, Anthropic). The AI explained concepts, broke the work into small steps, and reviewed my code; I wrote most of the code myself and fixed my own errors based on that feedback.

All code was run, checked and interpreted by me. Explanations and biological interpretations in the markdown cells are partly based on the AI's explanations, so they may contain simplifications or errors. Please check them against the references above before relying on them.