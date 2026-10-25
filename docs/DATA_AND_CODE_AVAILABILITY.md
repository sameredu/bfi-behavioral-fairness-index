# Data and Code Availability Statement

## Statement (for the manuscript)

The anonymized examination dataset that supports the empirical findings of this study is
openly available in the Zenodo repository under a Creative Commons Attribution 4.0
International (CC BY 4.0) license:

> Yaghi, S., & AbuSamra, A. A. (2026). *Web Databases — Anonymized Moodle Examination
> Dataset for Fairness-Aware Learning Analytics* [Data set]. Zenodo.
> https://doi.org/10.5281/zenodo.20366538

The dataset comprises anonymized Moodle examination logs from 206 undergraduate students
across seven assessment components (675 examination sessions). All personally identifiable
information was removed prior to release: student names were replaced with sequential labels,
student identifiers were pseudonymized with a salted SHA-256 hash (the salt is held privately
by the authors and is not released), email addresses were removed, and k-anonymity (k ≥ 5)
was verified. No network telemetry or device data were collected; the analysis is based solely
on Moodle examination logs.

The source code that implements the Behavioral Fairness Index, tests it against Axioms A1–A6,
and reproduces all figures and tables is openly available at:

> https://github.com/sameredu/bfi-behavioral-fairness-index

under the MIT license. The repository does not contain the examination data; the analysis
scripts read the dataset files downloaded separately from the Zenodo record above.

## Reproducibility checklist

- [x] BFI pipeline (`src/pipeline.py`) and data loader (`src/load.py`)
- [x] One-command reproduction of all results (`src/run_all.py`)
- [x] Unit tests of Axioms A1–A6, Lipschitz bounds and the evidence gate (`tests/test_bfi.py`)
- [x] Ablation of the earlier linear specification (`src/ablation.py`)
- [x] Figure-generation scripts (`figures/`)
- [x] Fixed random seeds (2026, 7, 0)
- [x] Dataset openly archived with a citable DOI (Zenodo)

## Double-blind note

For double-blind review, replace the GitHub and ORCID identifiers above with an
anonymized mirror (e.g., an anonymized GitHub or anonymous.4open.science link) until
acceptance, then de-anonymize in the camera-ready version.
