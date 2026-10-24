"""
Behavioral Fairness Index (BFI) — core implementation.

Infrastructure-Aware Behavioral Fairness Theory (IABFT).

This module implements the Behavioral Fairness Index defined in:

    BFI_i = alpha * P_i + beta * R_i + gamma * (1 - D_hat_i)

subject to the simplex constraint alpha + beta + gamma = 1, with alpha, beta, gamma > 0.

It also provides:
  - the normalized behavioral divergence  D_hat = D / (1 + D)
  - the three-tier decision rule with thresholds tau1 = 0.60, tau2 = 0.80
  - the Lipschitz constant L = max(alpha, beta, gamma)
  - the bounded-interaction extension  BFI+ = BFI + delta * phi(P, R, C)
  - the stability distance rho(s) to the nearest decision threshold

Companion paper:
    "Infrastructure-Aware Behavioral Fairness Theory: An Axiomatic Foundation
     for Fair Educational Decision Systems."

Author: Samer Yaghi (UCAS / IUG)
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


# Decision thresholds (Section 8 of the paper)
TAU1 = 0.60   # below -> No action ; at/above -> at least Instructor review
TAU2 = 0.80   # at/above -> Automatic intervention


@dataclass(frozen=True)
class BFIWeights:
    """Simplex weights for the BFI functional.

    Enforces alpha + beta + gamma = 1 and non-negativity, consistent with
    Axiom A1 (Bounded Fairness) and Theorem T0 (characterization).
    """
    alpha: float = 0.33
    beta: float = 0.33
    gamma: float = 0.34

    def __post_init__(self) -> None:
        s = self.alpha + self.beta + self.gamma
        if abs(s - 1.0) > 1e-6:
            raise ValueError(f"weights must sum to 1 (got {s:.6f})")
        if min(self.alpha, self.beta, self.gamma) < 0:
            raise ValueError("weights must be non-negative")

    @property
    def lipschitz_constant(self) -> float:
        """L = max(alpha, beta, gamma)  (Theorem T4)."""
        return max(self.alpha, self.beta, self.gamma)


def normalize_divergence(d: np.ndarray | float) -> np.ndarray | float:
    """D_hat = D / (1 + D)  maps [0, inf) -> [0, 1)   (Equation 4)."""
    d = np.asarray(d, dtype=float)
    return d / (1.0 + d)


def bfi(p, r, d_hat, weights: BFIWeights | None = None):
    """Behavioral Fairness Index (Equation 5).

    Parameters
    ----------
    p : disruption probability P in [0, 1]
    r : recovery score R in [0, 1]
    d_hat : normalized behavioral divergence in [0, 1]
    weights : BFIWeights, defaults to (0.33, 0.33, 0.34)

    Returns
    -------
    BFI score(s) in [0, 1]  (bounded by Theorem T1).
    """
    if weights is None:
        weights = BFIWeights()
    p = np.asarray(p, dtype=float)
    r = np.asarray(r, dtype=float)
    d_hat = np.asarray(d_hat, dtype=float)
    return weights.alpha * p + weights.beta * r + weights.gamma * (1.0 - d_hat)


def bfi_extended(p, r, d_hat, weights: BFIWeights | None = None,
                 delta: float = 0.0, phi=None):
    """Bounded-interaction extension BFI+ (Equation 10, Section 7.1).

        BFI+ = alpha*P + beta*R + gamma*(1 - D_hat) + delta * phi(P, R, 1 - D_hat)

    When delta = 0 this reduces exactly to the linear BFI (Theorem T0 leading order).
    Default phi is the disruption-recovery interaction phi = P * R.
    """
    if weights is None:
        weights = BFIWeights()
    p = np.asarray(p, dtype=float)
    r = np.asarray(r, dtype=float)
    d_hat = np.asarray(d_hat, dtype=float)
    base = bfi(p, r, d_hat, weights)
    if delta == 0.0:
        return base
    if phi is None:
        phi = lambda pp, rr, cc: pp * rr  # noqa: E731
    c = 1.0 - d_hat
    return base + delta * phi(p, r, c)


def decision_tier(score):
    """Three-tier decision rule (Section 8 / Figure 1 Decision Layer).

    Returns one of: 'auto', 'review', 'none'.
    Vectorized over array input.
    """
    score = np.asarray(score, dtype=float)
    tiers = np.where(score >= TAU2, "auto",
                     np.where(score >= TAU1, "review", "none"))
    return tiers if tiers.shape else str(tiers)


def stability_distance(score):
    """rho(s) = min(|BFI - tau1|, |BFI - tau2|)   (Equation 12).

    Larger rho => more robust tier assignment (Corollary 1).
    """
    score = np.asarray(score, dtype=float)
    return np.minimum(np.abs(score - TAU1), np.abs(score - TAU2))


def signal_entropy(values, bins: int = 20) -> float:
    """Normalized Shannon entropy of a signal on [0, 1] (Section 7).

    Used to justify / recalibrate the weights: signals with near-equal
    entropy motivate a near-uniform allocation.
    """
    values = np.asarray(values, dtype=float)
    values = values[np.isfinite(values)]
    if values.size == 0:
        return 0.0
    hist, _ = np.histogram(values, bins=bins, range=(0.0, 1.0))
    p = hist / hist.sum() if hist.sum() > 0 else hist
    p = p[p > 0]
    h = -np.sum(p * np.log(p))
    return float(h / np.log(bins))  # normalized to [0, 1]


def recommend_weights(p, r, d_hat) -> BFIWeights:
    """Entropy-proportional weight recalibration (Section 7.2).

    Allocates weight in proportion to each signal's normalized entropy,
    subject to the simplex constraint. Returns calibrated BFIWeights.
    """
    h_p = signal_entropy(p)
    h_r = signal_entropy(r)
    h_c = signal_entropy(1.0 - np.asarray(d_hat, dtype=float))
    total = h_p + h_r + h_c
    if total <= 0:
        return BFIWeights()
    a, b, g = h_p / total, h_r / total, h_c / total
    # round to 2 dp but keep sum == 1
    a, b = round(a, 2), round(b, 2)
    g = round(1.0 - a - b, 2)
    return BFIWeights(alpha=a, beta=b, gamma=g)


if __name__ == "__main__":
    w = BFIWeights()
    print("BFI demo")
    print("  weights:", w, " L =", w.lipschitz_constant)
    for (p, r, dh) in [(0.9, 0.9, 0.05), (0.7, 0.6, 0.30), (0.2, 0.1, 0.70)]:
        s = bfi(p, r, dh, w)
        print(f"  P={p} R={r} D_hat={dh} -> BFI={s:.3f}"
              f"  tier={decision_tier(s)}  rho={stability_distance(s):.3f}")
