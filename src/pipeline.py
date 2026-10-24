"""BFI pipeline, version 3 (gated consistency).

BFI_i = alpha*P_i + beta*R_i + gamma*[1 - (1 - P_i) * Dhat_i],  alpha, beta, gamma > 0, sum = 1

* P    : disruption evidence, noisy-OR of weighted unanswered share, entry latency, short-session flag
* R    : completion at the learner's next session of the same kind (0.5 if none)
* Dhat : divergence of answered-item accuracy from the learner's own history (EMA Golden Profile);
         computed only from items that reached the server, so disruption does not create divergence.
         Missing (no auto-graded answered items) -> cohort median of observed Dhat.
* the consistency penalty is scaled by (1 - P): it vanishes when disruption evidence is complete (Axiom A4').
Decision layer: auto if BFI >= TAU2; review if TAU1 <= BFI < TAU2 and P >= P_GATE; otherwise none.
"""
import numpy as np, pandas as pd

W = np.array([1/3, 1/3, 1/3])        # centre of the simplex (default, uninformative)
TAU1, TAU2, P_GATE = 0.60, 0.80, 0.05


def signals(S, lam=0.5, impute='median'):
    S = S.copy().sort_values(['student', 'order']).reset_index(drop=True)
    S['lat_n'] = np.clip(S.latency / 30, 0, 1)
    S['short'] = ((S.duration < 5) & (S.unans_ratio > 0)).astype(float)
    u = 1 - S.answered_w
    S['P'] = 1 - (1 - u) * (1 - S.lat_n) * (1 - S.short)
    # recovery: next session of the same kind
    R = np.full(len(S), np.nan)
    for _, g in S.groupby('student'):
        idx = g.index.tolist()
        for a in idx:
            nxt = [b for b in idx if S.order[b] > S.order[a] and
                   (S.kind[b] == S.kind[a] or 'mixed' in (S.kind[a], S.kind[b]))]
            if nxt:
                R[a] = S.answered_w[nxt[0]]
    S['R_obs'] = ~np.isnan(R)
    S['R'] = np.where(np.isnan(R), 0.5, R)
    # Golden Profile on answered-item accuracy (EMA over the learner's previous observed sessions)
    pop = S.acc.mean()
    D = np.full(len(S), np.nan)
    for _, g in S.groupby('student'):
        G = pop
        for a in g.index:
            if np.isnan(S.acc[a]):
                continue
            D[a] = abs(S.acc[a] - G)
            G = lam * S.acc[a] + (1 - lam) * G
    S['D_obs'] = ~np.isnan(D)
    Dh = D / (1 + D)
    fill = np.nanmedian(Dh) if impute == 'median' else float(impute)
    S['Dhat'] = np.where(np.isnan(Dh), fill, Dh)
    S['C'] = 1 - S.Dhat
    return S


def bfi(P, R, Dhat, w=W):
    """Gated BFI (Theorem T0)."""
    a, b, c = w
    return a * P + b * R + c * (1 - (1 - P) * Dhat)


def bfi_linear(P, R, Dhat, w=W):
    """Linear BFI of the previous draft (unconditional consistency), kept for comparison."""
    a, b, c = w
    return a * P + b * R + c * (1 - Dhat)


def grad(P, R, Dhat, w=W):
    a, b, c = w
    return np.stack([a + c * Dhat, np.full_like(np.asarray(P, float), b), -c * (1 - P)], -1)


def tier(b, P=None):
    t = np.where(b >= TAU2, 'auto', np.where(b >= TAU1, 'review', 'none'))
    if P is not None:
        t = np.where((t == 'review') & (np.asarray(P) < P_GATE), 'none', t)
    return t


def score(S, w=W):
    S = S.copy()
    S['BFI'] = bfi(S.P, S.R, S.Dhat, w)
    S['tier'] = tier(S.BFI, S.P)
    S['tier_nogate'] = tier(S.BFI)
    return S
