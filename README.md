# Behavioral Fairness Index (BFI) — Infrastructure-Aware Behavioral Fairness Theory

Reproduction code for the paper on the Behavioral Fairness Index (Samer Yaghi, UCAS / IUG; Aiman A. AbuSamra, IUG).

```
BFI_i = alpha*P_i + beta*R_i + gamma*[1 - (1 - P_i) * Dhat_i],   alpha, beta, gamma > 0,  alpha + beta + gamma = 1
```

* `P` is disruption evidence: a noisy-OR of the weighted unanswered share, entry latency (30 min or more = 1) and a short-session flag.
* `R` is recovery: the completion share at the learner's next session of the same kind, or 0.5 if there is none.
* `Dhat` is the divergence of answered-item accuracy from the learner's own history (an EMA Golden Profile). It uses only items that reached the server, so a disruption does not create divergence. When it is missing, the cohort median is used.
* The consistency penalty is scaled by `(1 - P)` (Axiom A4, conditional consistency), so it vanishes when the disruption evidence is complete.
* Decision rule: automatic compensation if BFI >= 0.80. Review if 0.60 <= BFI < 0.80 **and** P >= 0.05 (the evidence gate). Otherwise no action.

Theorem T0 states that Axioms A1–A6 hold if and only if the index has this form. `tests/test_bfi.py` checks every axiom numerically.

## Reproduce

```bash
pip install -r requirements.txt
# put the seven .xlsx files from https://doi.org/10.5281/zenodo.20366538 in ./data/
IABFT_DATA=./data python src/run_all.py      # -> results/: results.json, results_ablation.json, Figures 1-4, tests
```

## Layout

```
src/load.py          7 Zenodo files -> one row per session (675)
src/pipeline.py      features, P, R, Dhat, gated BFI, decision rule (Algorithm 1)
src/analyze.py       tiers, stability (Theorem T5), sensitivity, validity, baselines, bootstrap CIs
src/ablation.py      linear BFI with unconditional consistency and timing-based divergence
src/robustness.py    recovery observed vs imputed, real-time variant (R = 0.5), threshold sensitivity
src/run_all.py       runs everything
figures/             Figure 1 (pipeline), Figures 2-4 (response surface, stability, validity)
tests/test_bfi.py    Axioms A1-A6, Lipschitz bounds, evidence gate
```

## Version history

| Version | Change |
|---|---|
| 3.2.0 | Figure 1 redrawn at print width, with labels checked against `pipeline.py` (asserts in the script); PNG, PDF and SVG output |
| 3.1.0 | Robustness analyses: recovery availability, real-time variant, threshold grid |
| 3.0.0 | Conditional-consistency axiom (A4), divergence from answered-item accuracy, evidence gate, equal weights of 1/3, unit tests, ablation |
| 2.0.0 | Replaced the v1 placeholder analysis (`R = 1 - P`) with the actual pipeline; exact flip-probability formula |
| 1.0.0 | Initial release (superseded; could not reproduce the numbers in the first manuscript) |

## Data and license

Dataset (CC BY 4.0): Yaghi, S., & AbuSamra, A. A. (2026). *Web Databases — Anonymized Moodle examination dataset for fairness-aware learning analytics* (Version 1.0.0). Zenodo. https://doi.org/10.5281/zenodo.20366538. It contains Moodle quiz-attempt reports only; no network telemetry was collected.
Code: MIT.
