"""
bfi_iabft — Behavioral Fairness Index (Infrastructure-Aware Behavioral Fairness Theory).

A small, dependency-light implementation of the Behavioral Fairness Index (BFI)
introduced in:

    Yaghi, S., & AbuSamra, A. A. (2026).
    Infrastructure-Aware Behavioral Fairness Theory: An Axiomatic Foundation
    for Fair Educational Decision Systems.

The BFI is an individual-level, infrastructure-aware fairness score for automated
educational decisions:

    BFI_i = alpha * P_i + beta * R_i + gamma * (1 - D_hat_i),   alpha + beta + gamma = 1

Public API
----------
- BFIWeights            : simplex weights with Lipschitz constant (L1)
- bfi                   : the Behavioral Fairness Index (Eq. 5)
- bfi_extended          : bounded-interaction extension BFI+ (Eq. 10, Section 7.1)
- normalize_divergence  : D_hat = D / (1 + D)  (Eq. 4)
- decision_tier         : three-tier rule (auto / review / none)
- stability_distance    : rho(s) to nearest threshold (Eq. 12)
- signal_entropy        : normalized Shannon entropy of a signal
- recommend_weights     : entropy-proportional weight recalibration (Section 7.2)
- lipschitz_constants   : L1 / L2 / Linf Lipschitz constants for given weights
- TAU1, TAU2            : decision thresholds (0.60, 0.80)
"""

from .core import (
    BFIWeights,
    bfi,
    bfi_extended,
    normalize_divergence,
    decision_tier,
    stability_distance,
    signal_entropy,
    recommend_weights,
    TAU1,
    TAU2,
)
from .core import lipschitz_constants  # noqa: F401  (added below)

__version__ = "1.0.0"

__all__ = [
    "BFIWeights",
    "bfi",
    "bfi_extended",
    "normalize_divergence",
    "decision_tier",
    "stability_distance",
    "signal_entropy",
    "recommend_weights",
    "lipschitz_constants",
    "TAU1",
    "TAU2",
    "__version__",
]
