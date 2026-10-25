# Changelog

All notable changes to this repository. Each release states what triggered it. Releases 2.0.0–3.2.0 come from internal review of the code and the manuscript before submission, not from peer review.

## [3.2.1] — 2026-10-25
- Repository renamed from `iabft-behavioral-fairness-index` to `bfi-behavioral-fairness-index`; repository links in `CITATION.cff`, `docs/` and `.zenodo.json` updated.
- Removed `docs/GITHUB_UPLOAD_INSTRUCTIONS.md` (one-off setup notes).
- No change to the code, the index or any reported number.

## [3.2.0] — 2026-10-24
**Trigger:** preparation of the manuscript's final figures.
- Figure 1 redrawn at the manuscript's text width (6.33 in) so that no label is scaled down; the arrows now show which feature feeds which signal.
- `make_figure1_pipeline.py` asserts that every formula and threshold drawn in the figure matches `src/pipeline.py`; the script fails if they diverge.
- Figure 1 exported as PNG, PDF and SVG (vector formats for publication).
- Added `.zenodo.json` (authors, ORCIDs, license, related identifiers) for the Zenodo–GitHub integration.
- No change to the index, the data pipeline or any reported number.

## [3.1.0] — 2026-10-24
**Trigger:** pre-submission review comments on the manuscript (reliance on future information, threshold choice, generalizability).
- `src/robustness.py`: results split by observed vs imputed recovery; a real-time variant that uses no future information (R = 0.5 for every session); a 3 × 3 grid of thresholds (τ₁ ∈ {0.55, 0.60, 0.65}, τ₂ ∈ {0.75, 0.80, 0.85}).
- `run_all.py` runs the new analyses; all earlier results are unchanged.

## [3.0.0] — 2026-10-24
**Trigger:** re-running v2.0.0 on the real data showed a conflict between two axioms: the unconditional consistency axiom (A4) penalized exactly the sessions that the disruption axiom (A2) is meant to protect (r(P, 1 − D̂) = −0.55). The paper's emphasis also shifted from formal theory alone toward empirical validation on the examination data.
- **Index changed** to the gated form BFI = αP + βR + γ[1 − (1 − P)D̂] (conditional consistency, Axiom A4), characterized by a new representation theorem.
- Divergence D̂ is now computed from answered-item accuracy, which connectivity loss does not distort; missing values take the cohort median.
- Decision rule: evidence gate (no instructor review when P < 0.05).
- Equal weights of 1/3 (centre of the simplex) replace 0.33/0.33/0.34.
- `tests/test_bfi.py`: numerical tests of Axioms A1–A6, the Lipschitz bounds and the gate.
- `src/ablation.py`: reproduces the linear specification for comparison.
- Removed the stand-alone linear modules (`src/bfi.py`, `simulation/`), which no longer match the paper.

## [2.0.0] — 2026-10-24
**Trigger:** internal pre-submission audit of v1.0 against the manuscript.
- v1.0 analysis used a placeholder recovery signal (`R = 1 − P`) and could not reproduce the numbers in the first manuscript; replaced by the full pipeline (`src/load.py`, `src/pipeline.py`, `src/analyze.py`, `src/validity*.py`, `src/run_all.py`).
- Disruption evidence P documented as rule-based (noisy-OR of unanswered share, entry latency, short-session flag); the dataset contains no connectivity logs, so no classifier is trained on rule-derived labels.
- The noise claim "max |ΔBFI| ≤ 0.017" was incorrect under Gaussian noise; replaced by the exact flip-probability formula (Theorem T5), checked by simulation.
- The two sittings of the supplementary examination are handled separately when computing entry latency.

## [1.0] — 2026-06-18
- Initial public release accompanying the first manuscript (linear BFI, synthetic simulation, figure scripts).
- Superseded: its real-data analysis does not reproduce the reported numbers. Do not use v1.0 to reproduce the paper.
