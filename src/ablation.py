"""Ablation: linear BFI with unconditional consistency and timing-based divergence
(the specification of the earlier draft). Reproduces the numbers quoted in Sections 4 and 7.3."""
import json, numpy as np, pandas as pd
from sklearn.metrics import roc_auc_score
from load import load
from pipeline import signals, W

def timing_divergence(S, lam=0.5):
    S = S.copy()
    ref = S[S.unans_ratio == 0].groupby('exam').duration.median()
    S['tau'] = np.clip(S.duration / S.exam.map(ref), 0, 1)
    S['end_close'] = S.ended_at_close.astype(float)
    V = S[['tau', 'end_close', 'lat_n']].to_numpy(); pop = V.mean(0); D = np.zeros(len(S))
    for _, g in S.groupby('student'):
        G = pop.copy()
        for a in g.index:
            D[a] = np.linalg.norm(V[a] - G); G = lam * V[a] + (1 - lam) * G
    S['Dhat_t'] = D / (1 + D)
    return S

S = timing_divergence(signals(load()))
S['C_t'] = 1 - S.Dhat_t
S['BFI_lin_t'] = W[0] * S.P + W[1] * S.R + W[2] * S.C_t
sc = pd.read_csv('sessions_scored.csv')[['student', 'exam', 'ability_other']]
S = S.merge(sc, on=['student', 'exam'])
dis = S.unans_ratio > 0
low = S[(S.score_frac < 0.6) & S.ability_other.notna()]
out = {'corr_P_C': round(S.P.corr(S.C_t), 3),
       'C_dis_vs_clean': [round(S[dis].C_t.mean(), 3), round(S[~dis].C_t.mean(), 3)],
       'AUC_linear_timing': round(roc_auc_score(low.ability_other >= 0.7, low.BFI_lin_t), 3)}
json.dump(out, open('results_ablation.json', 'w'), indent=1); print(out)
