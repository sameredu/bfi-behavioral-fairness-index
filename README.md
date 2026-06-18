# Behavioral Fairness Index (BFI) — `bfi-iabft`

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Dataset DOI](https://img.shields.io/badge/dataset-10.5281%2Fzenodo.20366538-blue.svg)](https://doi.org/10.5281/zenodo.20366538)
[![Tests](https://img.shields.io/badge/tests-12%20passing-brightgreen.svg)](tests/)

Reference implementation, installable Python package, synthetic simulation, and
figure-reproduction code for:

> **Infrastructure-Aware Behavioral Fairness Theory: An Axiomatic Foundation for Fair Educational Decision Systems**
> Samer Yaghi (University College of Applied Sciences, Gaza; Islamic University of Gaza)
> Aiman A. AbuSamra (Islamic University of Gaza)

The Behavioral Fairness Index (BFI) is an individual-level, infrastructure-aware fairness
score for automated educational decisions:

```
BFI_i = alpha * P_i + beta * R_i + gamma * (1 - D_hat_i),    alpha + beta + gamma = 1
```

where `P` is the disruption probability, `R` the recovery score, and `D_hat` the normalized
behavioral divergence from a learner's historical "Golden Profile". The index is *characterized*
within the class of additive, monotone fairness functionals by a representation theorem (T0),
and satisfies boundedness, monotonicity, equivalence, Lipschitz stability, and noise robustness
(Theorems T1-T5).

## Install

```bash
pip install bfi-iabft                      # from PyPI (after release)
# or, from this repository:
pip install -e .                           # editable install
pip install -e ".[data,figures,dev]"       # with pandas / matplotlib / pytest
```

## Quick start (library)

```python
import bfi_iabft as bfi

w = bfi.BFIWeights(alpha=0.33, beta=0.33, gamma=0.34)
score = bfi.bfi(P=0.9, R=0.9, d_hat=0.05, weights=w)     # -> 0.917
tier  = bfi.decision_tier(score)                          # -> "auto"
rho   = bfi.stability_distance(score)                     # distance to nearest threshold
bfi.lipschitz_constants(w)                                # {'L1':0.34,'L2':0.577,'Linf':1.0}

# bounded-interaction extension (Section 7.1); delta=0 reduces to the linear BFI
bfi.bfi_extended(0.8, 0.8, 0.2, w, delta=0.1)

# entropy-based weight recalibration for a new deployment (Section 7.2)
bfi.recommend_weights(P_array, R_array, Dhat_array)
```

## Quick start (CLI)

```bash
bfi-iabft demo                  # short demonstration
bfi-iabft simulate              # verify Theorems T1-T5 on synthetic data
bfi-iabft analyze --data ./data # analyze the Zenodo dataset (downloaded separately)
```

## Repository structure

```
.
├── bfi_iabft/              # installable package
│   ├── __init__.py         # public API
│   ├── core.py             # BFI, tiers, stability, entropy, Lipschitz constants
│   └── cli.py              # `bfi-iabft` command-line interface
├── simulation/
│   └── run_simulation.py   # synthetic verification of Theorems T1-T5 (Table 1 params)
├── figures/                # scripts that regenerate Figures 1-4
├── src/
│   └── analyze_real_data.py# empirical analysis on the Zenodo dataset
├── tests/
│   └── test_bfi.py         # unit tests (theorems, tiers, stability, constants)
├── pyproject.toml          # packaging / dependencies / console script
├── requirements.txt
├── CITATION.cff
├── LICENSE                 # MIT (code)
└── README.md
```

## Run the tests

```bash
pytest -q
```

## Data availability

The code does **not** include the examination data. The anonymized Web Databases examination
dataset (206 students, 675 sessions across seven assessments) is openly archived on Zenodo
under CC BY 4.0:

- **DOI:** [10.5281/zenodo.20366538](https://doi.org/10.5281/zenodo.20366538)
- **Record:** https://zenodo.org/records/20366538

Download the seven `.xlsx` files into `./data/` and run `bfi-iabft analyze --data ./data`.
The dataset is fully anonymized (sequential labels, salted SHA-256 pseudonymized IDs with the
salt held privately, emails removed, k-anonymity k >= 5). Analysis uses Moodle logs only.

## A note on the Lipschitz constant (norm choice)

For the linear functional `BFI = <w, x>` the tight Lipschitz constant depends on the norm in
which the input perturbation is measured (Holder duality):

| Perturbation norm | Lipschitz constant `L` | value at `w = (0.33, 0.33, 0.34)` |
|-------------------|------------------------|-----------------------------------|
| L1  (L1 norm)     | `max_i |w_i|`          | **0.34** |
| L2  (Euclidean)   | `||w||_2`              | 0.577 |
| Linf              | `sum_i |w_i|`          | 1.0 |

The paper states Theorem T4 in the **L1 norm**, giving `L = max(alpha, beta, gamma) = 0.34`;
the simulation and `tests/test_bfi.py` verify this bound exactly (`max |dBFI| / ||eps||_1 = 0.34`,
zero violations). `bfi.lipschitz_constants()` returns all three constants.

## License & citation

Code: MIT (see `LICENSE`). Dataset: CC BY 4.0 (Zenodo). See `CITATION.cff` to cite the software,
and cite the dataset/paper as in the Data availability section.
