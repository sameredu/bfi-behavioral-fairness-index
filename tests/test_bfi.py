"""Unit tests for the gated BFI (run: python -m pytest tests/ or python tests/test_bfi.py)."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import numpy as np
from pipeline import bfi, bfi_linear, grad, tier, W, TAU1, TAU2, P_GATE

rng = np.random.default_rng(0)


def test_representation_properties():
    for _ in range(500):
        w = rng.dirichlet([1, 1, 1]); Z = rng.random((200, 3)); Z2 = rng.random((200, 3)); lam = rng.random(200)
        b = bfi(*Z.T, w)
        assert b.min() >= -1e-12 and b.max() <= 1 + 1e-12                       # A1
        g = grad(*Z.T, w)
        assert (g[:, 0] > 0).all() and (g[:, 1] > 0).all()                       # A2, A3
        assert (g[Z[:, 0] < 1, 2] < 0).all()                                     # A4' (P < 1)
        assert np.allclose(bfi(1, Z[:, 1], Z[:, 2], w), bfi(1, Z[:, 1], 0, w))   # A4' (P = 1)
        assert abs(bfi(0, 0, 1, w)) < 1e-12 and abs(bfi(1, 1, 0, w) - 1) < 1e-12 # A6b
        mixP = bfi(lam * Z[:, 0] + (1 - lam) * Z2[:, 0], Z[:, 1], Z[:, 2], w)    # A6' in P
        assert np.allclose(mixP, lam * b + (1 - lam) * bfi(Z2[:, 0], Z[:, 1], Z[:, 2], w))
        mixRC = bfi(Z[:, 0], lam * Z[:, 1] + (1 - lam) * Z2[:, 1], lam * Z[:, 2] + (1 - lam) * Z2[:, 2], w)
        assert np.allclose(mixRC, lam * b + (1 - lam) * bfi(Z[:, 0], Z2[:, 1], Z2[:, 2], w))  # A6' in (R, C)


def test_lipschitz_bounds():
    Z = rng.random((100000, 3)); Z2 = rng.random((100000, 3)); a, b_, c = W
    d = np.abs(bfi(*Z.T) - bfi(*Z2.T))
    assert (d <= max(a + c, b_, c) * np.abs(Z - Z2).sum(1) + 1e-12).all()
    assert (d <= np.sqrt((a + c) ** 2 + b_ ** 2 + c ** 2) * np.linalg.norm(Z - Z2, axis=1) + 1e-12).all()


def test_gate_and_tiers():
    assert tier(np.array([0.70]), np.array([0.0]))[0] == 'none'
    assert tier(np.array([0.70]), np.array([P_GATE]))[0] == 'review'
    assert tier(np.array([TAU2]), np.array([0.0]))[0] == 'auto'
    # with no disruption evidence the gated index cannot reach the auto tier
    assert bfi(0, 1, 0) < TAU2


def test_linear_special_case():
    Z = rng.random((1000, 3))
    assert np.allclose(bfi(*Z.T) - bfi_linear(*Z.T), W[2] * Z[:, 0] * Z[:, 2])


if __name__ == '__main__':
    for f in [test_representation_properties, test_lipschitz_bounds, test_gate_and_tiers, test_linear_special_case]:
        f(); print('PASS', f.__name__)
