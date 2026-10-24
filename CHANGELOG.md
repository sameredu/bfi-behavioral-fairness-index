# Changelog

All notable changes to this repository. Each release states what triggered it. Releases 2.0.0–3.2.0 come from internal review of the code and the manuscript before submission, not from peer review.

## [2.0.0] — 2026-10-24
**Trigger:** internal pre-submission audit of v1.0 against the manuscript.
- v1.0 analysis used a placeholder recovery signal (`R = 1 − P`) and could not reproduce the numbers in the first manuscript; replaced by the full pipeline (`src/load.py`, `src/pipeline.py`, `src/analyze.py`, `src/validity*.py`, `src/run_all.py`).
- Disruption evidence P documented as rule-based (noisy-OR of unanswered share, entry latency, short-session flag); the dataset contains no connectivity logs, so no classifier is trained on rule-derived labels.
- The noise claim "max |ΔBFI| ≤ 0.017" was incorrect under Gaussian noise; replaced by the exact flip-probability formula (Theorem T5), checked by simulation.
- The two sittings of the supplementary examination are handled separately when computing entry latency.

## [1.0] — 2026-06-18
- Initial public release accompanying the first manuscript (linear BFI, synthetic simulation, figure scripts).
- Superseded: its real-data analysis does not reproduce the reported numbers. Do not use v1.0 to reproduce the paper.
