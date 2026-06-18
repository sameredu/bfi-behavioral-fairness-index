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

The source code that implements the Behavioral Fairness Index, runs the synthetic simulation
used to verify Theorems T1–T5, and reproduces all figures and tables is openly available at:

> https://github.com/sameredu/iabft-behavioral-fairness-index

under the MIT license. The repository does not contain the examination data; the analysis
scripts read the dataset files downloaded separately from the Zenodo record above.

## Reproducibility checklist

- [x] Core BFI implementation (`src/bfi.py`)
- [x] Synthetic simulation verifying Theorems T1–T5 (`simulation/run_simulation.py`)
- [x] Figure-generation scripts (`figures/`)
- [x] Empirical analysis entry point (`src/analyze_real_data.py`)
- [x] Fixed random seed (42) for reproducible synthetic results
- [x] Dependency versions pinned (`requirements.txt`)
- [x] Dataset openly archived with a citable DOI (Zenodo)

## Public release note

This repository is released publicly and non-anonymized for reuse and citation.
If the companion manuscript is under double-blind review at any venue, cite the code
and data by DOI in the camera-ready version, and (if the venue requires it during
review) share an anonymized mirror with the editor until acceptance.