"""Robustness analyses requested in review: recovery availability, real-time variant, threshold sensitivity."""
import json, numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
import pipeline as pl
S = pd.read_csv('sessions_scored.csv')
low = lambda d: d[(d.score_frac < 0.6) & d.ability_other.notna()]
out = {}
# 1) recovery observed vs default
for k, g in S.groupby('R_obs'):
    L = low(g); y = L.ability_other >= 0.7
    out[f'R_obs={k}'] = {'n': len(g), 'tiers': g.tier.value_counts().to_dict(), 'low_n': len(L), 'low_infra': int(y.sum()),
                         'infra_actioned': int(((L.tier != 'none') & y).sum())}
# 2) real-time variant: no future information (R fixed at 0.5 for every session)
b_rt = pl.bfi(S.P, 0.5, S.Dhat); t_rt = pl.tier(b_rt, S.P)
L = low(S.assign(BFI_rt=b_rt, tier_rt=t_rt)); y = L.ability_other >= 0.7
out['realtime'] = {'tiers': pd.Series(t_rt).value_counts().to_dict(), 'changed_vs_retrospective': int((t_rt != S.tier).sum()),
                   'AUC': round(roc_auc_score(y, L.BFI_rt), 3), 'infra_actioned': int(((L.tier_rt != 'none') & y).sum()),
                   'infra_tiers': L[y].tier_rt.value_counts().to_dict()}
# 3) threshold sensitivity
rows = []
for t1 in (0.55, 0.60, 0.65):
    for t2 in (0.75, 0.80, 0.85):
        pl.TAU1, pl.TAU2 = t1, t2
        t = pl.tier(S.BFI.to_numpy(), S.P.to_numpy()); Lt = low(S.assign(t=t)); y = Lt.ability_other >= 0.7
        rows.append({'tau1': t1, 'tau2': t2, 'auto': int((t == 'auto').sum()), 'review': int((t == 'review').sum()),
                     'changed': int((t != S.tier).sum()), 'infra_auto': int(((Lt.t == 'auto') & y).sum()),
                     'infra_actioned': int(((Lt.t != 'none') & y).sum()), 'ability_auto': int(((Lt.t == 'auto') & ~y).sum())})
pl.TAU1, pl.TAU2 = 0.60, 0.80
out['thresholds'] = rows
json.dump(out, open('results_robustness.json', 'w'), indent=1, default=str)
print(json.dumps(out, indent=1, default=str))
