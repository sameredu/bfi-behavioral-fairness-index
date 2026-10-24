"""All empirical results of the paper (v3). Writes results.json and sessions_scored.csv."""
import json, numpy as np, pandas as pd
from math import erf, sqrt
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from load import load
from pipeline import *

Phi = lambda t: 0.5 * (1 + erf(t / sqrt(2)))
rng = np.random.default_rng(2026)
out = {}
S = score(signals(load()))
n = len(S)
out['n'] = n
out['R_observed'] = int(S.R_obs.sum()); out['D_observed'] = int(S.D_obs.sum())
out['BFI_range'] = [round(S.BFI.min(), 3), round(S.BFI.max(), 3)]
out['tiers_gated'] = S.tier.value_counts().to_dict()
out['tiers_nogate'] = S.tier_nogate.value_counts().to_dict()
out['gate_moved'] = int(((S.tier_nogate == 'review') & (S.tier == 'none')).sum())
out['tiers_by_exam'] = pd.crosstab(S.exam, S.tier).to_dict()


def H(x, b=10):
    h, _ = np.histogram(x, bins=b, range=(0, 1)); p = h[h > 0] / h.sum()
    return round(float(-(p * np.log(p)).sum() / np.log(b)), 3)


out['entropy'] = {k: H(S[k]) for k in ['P', 'R', 'C']}
out['corr'] = {'P_C': round(S.P.corr(S.C), 3), 'P_R': round(S.P.corr(S.R), 3), 'R_C': round(S.R.corr(S.C), 3)}
dis = S.unans_ratio > 0
obs = S.D_obs
out['Dhat_dis_vs_clean_observed'] = [round(S[dis & obs].Dhat.mean(), 3), round(S[~dis & obs].Dhat.mean(), 3)]
cons = 1 - (1 - S.P) * S.Dhat
out['consistency_term_dis_vs_clean'] = [round(cons[dis].mean(), 3), round(cons[~dis].mean(), 3)]
# linear comparison: penalty of old consistency term
old = score(signals(load()))  # same signals
out['linear_consistency_dis_vs_clean'] = [round((1 - S.Dhat)[dis].mean(), 3), round((1 - S.Dhat)[~dis].mean(), 3)]

# ---- stability: 100 Gaussian draws per session on (P, R, Dhat), clipped ----
Z = S[['P', 'R', 'Dhat']].to_numpy(); sig = 0.05
t0 = tier(S.BFI.to_numpy(), S.P.to_numpy())
t0_ng = tier(S.BFI.to_numpy())
flips = flips_ng = 0; dev = []
for _ in range(100):
    Zn = np.clip(Z + rng.normal(0, sig, Z.shape), 0, 1)
    b = bfi(Zn[:, 0], Zn[:, 1], Zn[:, 2])
    dev.append(b - S.BFI.to_numpy())
    flips += (tier(b, Zn[:, 0]) != t0).sum(); flips_ng += (tier(b) != t0_ng).sum()
dev = np.concatenate(dev); tot = 100 * n
def wilson(k, m, z=1.96):
    p = k / m; d = 1 + z * z / m; c = p + z * z / (2 * m); h = z * sqrt(p * (1 - p) / m + z * z / (4 * m * m))
    return [round((c - h) / d, 4), round((c + h) / d, 4)]
g = grad(S.P.to_numpy(), S.R.to_numpy(), S.Dhat.to_numpy()); gn = np.linalg.norm(g, axis=1)
rho = np.minimum(abs(S.BFI - TAU1), abs(S.BFI - TAU2)).to_numpy()
out['dBFI_sd_obs'] = round(dev.std(), 4); out['dBFI_sd_pred_mean'] = round(float(np.sqrt(np.mean((sig * gn) ** 2))), 4)
out['share_dev_gt_0.017'] = round(float((abs(dev) > 0.017).mean()), 3)
out['flip_rate_nogate'] = round(flips_ng / tot, 4); out['flip_rate_nogate_CI'] = wilson(flips_ng, tot)
out['flip_pred_nogate'] = round(float(np.mean([Phi(-r / (sig * q)) for r, q in zip(rho, gn)])), 4)
out['flip_rate_gated'] = round(flips / tot, 4); out['flip_rate_gated_CI'] = wilson(flips, tot)
out['rho_lt_0.05'] = round(float((rho < 0.05).mean()), 3)
out['grad_norm_range'] = [round(gn.min(), 3), round(gn.max(), 3)]

# ---- weight sensitivity ----
ch = []
for k in range(3):
    for d in (-0.05, 0.05):
        w = W.copy(); w[k] += d; w = np.clip(w, 1e-6, None); w /= w.sum()
        ch.append(round(float((tier(bfi(S.P, S.R, S.Dhat, w), S.P) != S.tier).mean()), 4))
out['weight_sens'] = ch
for lam in (0.3, 0.7):
    S2 = score(signals(load(), lam=lam)); out[f'lambda_{lam}_changed'] = int((S2.tier != S.tier).sum())
for imp in (0.0, 0.5):
    S2 = score(signals(load(), impute=imp)); out[f'impute_{imp}_changed'] = int((S2.tier != S.tier).sum())

# ---- validity ----
clean = S[(S.score_frac.notna()) & (S.unans_ratio == 0)]
def other_ability(r):
    o = clean[(clean.student == r.student) & (clean.exam != r.exam)]
    return o.score_frac.mean() if len(o) else np.nan
S['ability_other'] = S.apply(other_ability, axis=1)
d = S.dropna(subset=['ability_other'])
out['n_ability_sessions'] = len(d); out['n_ability_students'] = int(d.student.nunique())
for k in ['P', 'BFI']:
    r, p = spearmanr(d[k], d.ability_other); out[f'spearman_{k}'] = [round(r, 3), round(p, 4)]
low = S[(S.score_frac < 0.6) & S.ability_other.notna()].copy(); low['infra'] = (low.ability_other >= 0.7).astype(int)
out['low_n'] = len(low); out['low_infra'] = int(low.infra.sum()); out['low_students'] = int(low.student.nunique())
out['infra_tiers'] = low[low.infra == 1].tier.value_counts().to_dict()
out['ability_tiers'] = low[low.infra == 0].tier.value_counts().to_dict()
low['BFI_linear'] = bfi_linear(low.P, low.R, low.Dhat)
cands = {'BFI (gated, Eq. 3)': low.BFI, 'BFI linear (previous draft)': low.BFI_linear,
         'P + R only': (low.P + low.R) / 2, 'P': low.P, 'Unanswered share u': low.unans_ratio,
         'Any unanswered item': (low.unans_ratio > 0).astype(float)}
y = low.infra.to_numpy(); B = 5000; bs = {k: [] for k in cands}; diff = []
for _ in range(B):
    i = rng.integers(0, len(low), len(low))
    if y[i].min() == y[i].max():
        continue
    for k, v in cands.items():
        bs[k].append(roc_auc_score(y[i], v.to_numpy()[i]))
    diff.append(bs['BFI (gated, Eq. 3)'][-1] - bs['Any unanswered item'][-1])
out['auc'] = {k: [round(roc_auc_score(y, v), 3)] + [round(x, 3) for x in np.percentile(bs[k], [2.5, 97.5])] for k, v in cands.items()}
out['auc_diff_vs_flag'] = [round(x, 3) for x in np.percentile(diff, [2.5, 50, 97.5])]
json.dump(out, open('results.json', 'w'), indent=1, default=str)
S.to_csv('sessions_scored.csv', index=False)
print(json.dumps(out, indent=1, default=str))
