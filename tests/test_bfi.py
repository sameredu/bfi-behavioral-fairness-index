"""Unit tests for bfi_iabft — verify the theoretical properties hold in code."""

import numpy as np
import pytest

from bfi_iabft import (
    BFIWeights, bfi, bfi_extended, normalize_divergence,
    decision_tier, stability_distance, signal_entropy,
    recommend_weights, lipschitz_constants, TAU1, TAU2,
)


def test_weights_simplex():
    w = BFIWeights()
    assert abs(w.alpha + w.beta + w.gamma - 1.0) < 1e-9
    with pytest.raises(ValueError):
        BFIWeights(0.5, 0.5, 0.5)          # sums to 1.5
    with pytest.raises(ValueError):
        BFIWeights(-0.1, 0.6, 0.5)         # negative weight


def test_normalize_divergence_range():
    assert normalize_divergence(0.0) == 0.0
    assert 0.0 < normalize_divergence(1.0) < 1.0
    assert normalize_divergence(1e6) < 1.0      # asymptotes to 1


def test_t1_boundedness():
    """Theorem T1: BFI in [0, 1] for all inputs in the cube."""
    rng = np.random.default_rng(0)
    p, r, d = rng.uniform(0, 1, 10000), rng.uniform(0, 1, 10000), rng.uniform(0, 1, 10000)
    s = bfi(p, r, d)
    assert np.all(s >= -1e-12) and np.all(s <= 1 + 1e-12)


def test_t2_monotonicity():
    """Theorem T2: increasing in P and R, decreasing in D_hat."""
    w = BFIWeights()
    base = bfi(0.5, 0.5, 0.5, w)
    assert bfi(0.6, 0.5, 0.5, w) > base       # dP > 0
    assert bfi(0.5, 0.6, 0.5, w) > base       # dR > 0
    assert bfi(0.5, 0.5, 0.6, w) < base       # dD < 0


def test_t3_equivalence():
    """Theorem T3: identical evidence -> identical score."""
    assert bfi(0.4, 0.7, 0.2) == bfi(0.4, 0.7, 0.2)


def test_t4_lipschitz_l1():
    """Theorem T4: |dBFI| <= L1 * ||eps||_1 with L1 = max(alpha,beta,gamma)."""
    w = BFIWeights()
    L1 = lipschitz_constants(w)["L1"]
    rng = np.random.default_rng(1)
    for _ in range(1000):
        x = rng.uniform(0, 1, 3)
        y = rng.uniform(0, 1, 3)
        d = abs(bfi(*x, w) - bfi(*y, w))
        norm1 = np.sum(np.abs(np.array(x) - np.array(y)))
        assert d <= L1 * norm1 + 1e-9


def test_lipschitz_constants_values():
    Ls = lipschitz_constants(BFIWeights())
    assert abs(Ls["L1"] - 0.34) < 1e-9
    assert abs(Ls["L2"] - np.sqrt(0.33**2 + 0.33**2 + 0.34**2)) < 1e-9
    assert abs(Ls["Linf"] - 1.0) < 1e-9


def test_decision_tiers():
    assert decision_tier(0.90) == "auto"
    assert decision_tier(0.70) == "review"
    assert decision_tier(0.30) == "none"
    assert decision_tier(TAU2) == "auto"      # boundary inclusive
    assert decision_tier(TAU1) == "review"


def test_stability_distance():
    assert abs(stability_distance(0.60) - 0.0) < 1e-9
    assert abs(stability_distance(0.70) - 0.10) < 1e-9     # min(0.10, 0.10)


def test_extended_reduces_to_linear():
    """delta = 0 -> BFI+ equals the linear BFI (Theorem T0 leading order)."""
    w = BFIWeights()
    assert bfi_extended(0.5, 0.5, 0.3, w, delta=0.0) == bfi(0.5, 0.5, 0.3, w)


def test_extended_interaction_changes_score():
    w = BFIWeights()
    base = bfi(0.8, 0.8, 0.2, w)
    ext = bfi_extended(0.8, 0.8, 0.2, w, delta=0.1)
    assert ext != base


def test_recommend_weights_near_uniform_for_uniform_signals():
    rng = np.random.default_rng(2)
    p, r, d = rng.uniform(0, 1, 5000), rng.uniform(0, 1, 5000), rng.uniform(0, 1, 5000)
    w = recommend_weights(p, r, d)
    assert abs(w.alpha + w.beta + w.gamma - 1.0) < 1e-9
    # all weights should be in a sensible band for near-uniform signals
    for v in (w.alpha, w.beta, w.gamma):
        assert 0.2 < v < 0.45
