# Encoding Metabolic Networks with Hyperdimensional Computing
![Badge](https://img.shields.io/badge/degree-Master%20of%20Science-teal)
![Badge](https://img.shields.io/badge/year-2025--2026-green)
![Badge](https://img.shields.io/badge/university-UGent-blue)

> Group project. All code is available in the **[group repository](https://github.com/Kermit-UGent/DesignProject25-MetabolismHDC)**.
> My personal contribution is the **Semantic Surprise HDC (ssHDC)** retraining method, described [below](#my-contribution-sshdc).

## About the Project

Cancer cells rewire their metabolism, and the TumorMet repository captures this as patient-specific metabolic networks. These graphs are large and dense, which makes them hard to classify. We explored **Hyperdimensional Computing (HDC)**, a lightweight, brain-inspired approach that encodes each network as a single high-dimensional vector (a *hypervector*), to classify cancer subtypes across brain, kidney, lung, ovary and prostate tissue.

HDC turned out to be a robust and scalable way to embed these networks. Combined with logistic regression or SVM, it matched or outperformed the TumorMet baselines on most datasets. Classification with HDC alone (comparing patients to one average "prototype" per class) still lagged behind, which is the problem ssHDC tries to address.

## My Contribution: ssHDC

Standard HDC builds each class prototype once, by averaging all training patients. This washes out subtle differences between closely related subtypes. I designed **ssHDC**, a retraining method that keeps refining the prototypes based on how hard each patient is to classify.

The idea came from my background in neuroscience. ssHDC translates three brain mechanisms into update rules:

- **Error-related negativity (ERN):** the brain's error signal. ssHDC updates the prototypes not only after a wrong prediction, but also when a correct prediction was uncertain.
- **Semantic surprise (N400):** the brain reacts more strongly to more unexpected input. ssHDC scales each update by how atypical the patient is, so unusual patients cause larger corrections.
- **Reciprocal inhibition:** competing signals suppress each other. ssHDC pulls the correct prototype toward the patient and pushes the wrongly predicted one away.

### Results
Tested on the hardest task in the study, four ovarian cancer subtypes (290 patients, macro F1):

| Edges kept | Cross-validation: baseline → ssHDC | Test set: baseline → ssHDC |
|------------|------------------------------------|----------------------------|
| Top 5% | 38.4% → 54.8% | 43.7% → 45.4% |
| Top 90% | 61.7% → 64.5% | 64.7% → 59.2% |

ssHDC helped when the networks were strongly filtered, but overfitted on dense networks full of uninformative edges. The takeaway: retraining only pays off once the background noise in the network has been removed.

## Authors

| Role | Name |
|------|------|
| Author | Jan P. Nawrocki |
| Author | Pieterjan Vagenende |
| Author | Wouter Vanhoecke |
| Author (ssHDC) | Hendrik Willems |
| Supervisor | Carlos Vigil-Vásquez |
| Supervisor | Prof. Dr. Michiel Stock |

## Academic Context

- **Institution:** Ghent University (UGent) — KERMIT
- **Degree:** Master of Science in Bioinformatics
- **Academic year:** 2025–2026
- **Tools:** Python, torchhd, NetworkX, scikit-learn, Jupyter

## Keywords

`Hyperdimensional computing` `Metabolic networks` `TumorMet` `Cancer subtype classification` `Brain-inspired learning` `ssHDC`
