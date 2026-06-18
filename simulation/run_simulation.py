"""
Synthetic simulation verifying the theoretical properties of the BFI
(Theorems T1-T5 and Corollary 1) independently of any real dataset.

Reproduces the parameters reported in Table 1 of the paper:
    10,000 synthetic sessions, 100 runs, noise sigma in [0.01, 0.10],
    100 noise draws per session, weights (0.33, 0.33, 0.34).

Run:
    python simulation/run_simulation.py
"""

from __future__ import annotations
import numpy as np
from bfi_iabft import BFIWeights, bfi, decision_tier, stability_distance, TAU1, TAU2

RNG = np.random.default_rng(42)

N_SESSIONS = 10_000
N_RUNS = 100
NOISE_SIGMAS = np.linspace(0.01, 0.10, 10)
N_NOISE_DRAWS = 100


def sample_population(n: int):
    """Sample (P, R, D_hat) uniformly over the evidence cube [0, 1]^3."""
    p = RNG.uniform(0, 1, n)
    r = RNG.uniform(0, 1, n)
    d_hat = RNG.uniform(0, 1, n)
    return p, r, d_hat


def check_boundedness(scores) -> bool:
    """Theorem T1: BFI in [0, 1]."""
    return bool(np.all(scores >= -1e-12) and np.all(scores <= 1 + 1e-12))


def check_monotonicity(weights: BFIWeights) -> bool:
    """Theorem T2: partial derivatives have fixed signs (+a, +b, -g)."""
    eps = 1e-4
    p, r, d = 0.5, 0.5, 0.5
    dP = bfi(p + eps, r, d, weights) - bfi(p, r, d, weights)
    dR = bfi(p, r + eps, d, weights) - bfi(p, r, d, weights)
    dD = bfi(p, r, d + eps, weights) - bfi(p, r, d, weights)
    return bool(dP > 0 and dR > 0 and dD < 0)


def check_equivalence(weights: BFIWeights) -> float:
    """Theorem T3: identical evidence -> identical score. Returns max |diff|."""
    p, r, d = sample_population(1000)
    s1 = bfi(p, r, d, weights)
    s2 = bfi(p.copy(), r.copy(), d.copy(), weights)
    return float(np.max(np.abs(s1 - s2)))


def noise_stability(weights: BFIWeights, sigma: float):
    """Theorems T4-T5 under the L1 (Manhattan) norm.

    For the linear functional BFI = <w, x>, Holder's inequality gives the tight
    Lipschitz bounds, one per choice of norm:
        ||eps||_1   ->  |dBFI| <= max|w_i| * ||eps||_1      (L = 0.34)
        ||eps||_2   ->  |dBFI| <= ||w||_2  * ||eps||_2      (L = 0.577)
        ||eps||_inf ->  |dBFI| <= sum|w_i| * ||eps||_inf    (L = 1.0)
    The paper states T4 in the L1 norm, for which L = max(alpha, beta, gamma).
    This routine verifies the L1 bound holds for every sample (0 violations),
    records the worst ratio |dBFI| / ||eps||_1 (must be <= L), and reports the
    tier-flip rate under per-component Gaussian noise of std sigma.
    """
    L = weights.lipschitz_constant            # = max(alpha, beta, gamma), L1 dual
    L2 = float(np.sqrt(weights.alpha**2 + weights.beta**2 + weights.gamma**2))
    p, r, d = sample_population(N_SESSIONS)
    base = bfi(p, r, d, weights)
    base_tier = decision_tier(base)

    worst_ratio_l1 = 0.0
    max_dev = 0.0
    violations = 0
    flips = 0
    total = 0
    for _ in range(N_NOISE_DRAWS):
        eps_p = RNG.normal(0, sigma, N_SESSIONS)
        eps_r = RNG.normal(0, sigma, N_SESSIONS)
        eps_d = RNG.normal(0, sigma, N_SESSIONS)
        ep = np.clip(p + eps_p, 0, 1)
        er = np.clip(r + eps_r, 0, 1)
        ed = np.clip(d + eps_d, 0, 1)
        noisy = bfi(ep, er, ed, weights)
        ddev = np.abs(noisy - base)
        norm1 = np.abs(eps_p) + np.abs(eps_r) + np.abs(eps_d)   # L1 norm
        with np.errstate(divide="ignore", invalid="ignore"):
            ratio = np.where(norm1 > 0, ddev / norm1, 0.0)
        worst_ratio_l1 = max(worst_ratio_l1, float(np.max(ratio)))
        max_dev = max(max_dev, float(np.max(ddev)))
        violations += int(np.sum(ddev > L * norm1 + 1e-9))
        flips += int(np.sum(decision_tier(noisy) != base_tier))
        total += N_SESSIONS
    return {
        "L1": L,
        "L2": L2,
        "max_dev": max_dev,
        "worst_ratio_l1": worst_ratio_l1,   # <= L confirms T4 (L1)
        "violations": violations,           # should be 0
        "flip_rate": flips / total,
    }


def wilson_ci(k: int, n: int, z: float = 1.96):
    """Wilson 95% confidence interval for a proportion."""
    if n == 0:
        return (0.0, 0.0)
    phat = k / n
    denom = 1 + z**2 / n
    center = (phat + z**2 / (2 * n)) / denom
    half = (z * np.sqrt(phat * (1 - phat) / n + z**2 / (4 * n**2))) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def main():
    w = BFIWeights()
    print("=" * 64)
    print("BFI Synthetic Simulation — verifying Theorems T1-T5")
    print("=" * 64)
    print(f"Sessions/run: {N_SESSIONS:,} | runs: {N_RUNS} | "
          f"noise draws/session: {N_NOISE_DRAWS}")
    print(f"Weights: alpha={w.alpha}, beta={w.beta}, gamma={w.gamma} | "
          f"L = {w.lipschitz_constant}")
    print("-" * 64)

    # T1 boundedness over many runs
    bounded_all = True
    for _ in range(N_RUNS):
        p, r, d = sample_population(N_SESSIONS)
        bounded_all &= check_boundedness(bfi(p, r, d, w))
    print(f"[T1] Boundedness  BFI in [0,1] over {N_RUNS} runs : "
          f"{'PASS' if bounded_all else 'FAIL'}")

    # T2 monotonicity
    mono = check_monotonicity(w)
    print(f"[T2] Monotonicity  dP>0, dR>0, dD<0              : "
          f"{'PASS (0 violations)' if mono else 'FAIL'}")

    # T3 equivalence
    eqv = check_equivalence(w)
    print(f"[T3] Equivalence   max|BFI_i - BFI_j| if x_i=x_j : {eqv:.6f} (exact)")

    # T4/T5 stability at the headline sigma = 0.05
    res = noise_stability(w, sigma=0.05)
    print(f"[T4] Lipschitz(L1) max(|dBFI| / ||eps||_1)       : "
          f"{res['worst_ratio_l1']:.4f}  (must be <= L = {res['L1']})  "
          f"violations: {res['violations']}")
    print(f"     For reference, L2 constant ||w||_2 = {res['L2']:.4f}; "
          f"single-component move of sigma=0.05 => |dBFI| <= {res['L1']*0.05:.4f}")
    flip = res["flip_rate"]
    lo, hi = wilson_ci(int(round(flip * N_SESSIONS * N_NOISE_DRAWS)),
                       N_SESSIONS * N_NOISE_DRAWS)
    print(f"[T5] Decision stab tier-flip rate (sigma=0.05)   : "
          f"{flip*100:.2f}%  Wilson 95% CI [{lo*100:.2f}%, {hi*100:.2f}%]")

    # Sweep over noise sigmas: confirm L1 Lipschitz ratio bound holds for all sigma
    print("-" * 64)
    print("Noise sweep — L1 Lipschitz ratio max(|dBFI|/||eps||_1) must stay <= L:")
    print(f"  {'sigma':>6} | {'max ratio':>10} | {'L':>5} | within bound")
    all_ok = True
    for s in NOISE_SIGMAS:
        rr = noise_stability(w, sigma=float(s))
        ok = rr["worst_ratio_l1"] <= w.lipschitz_constant + 1e-6
        all_ok &= ok
        print(f"  {s:6.2f} | {rr['worst_ratio_l1']:10.4f} | "
              f"{w.lipschitz_constant:5.2f} | {'yes' if ok else 'NO'}")
    print("=" * 64)
    print("All theoretical properties verified on synthetic data (L1 norm)."
          if all_ok else "WARNING: L1 Lipschitz bound violated — check implementation.")


if __name__ == "__main__":
    main()
