import pandas as pd, numpy as np, json
from scipy.stats import spearmanr, mannwhitneyu
from sklearn.metrics import roc_auc_score
S=pd.read_csv('sessions_scored.csv')
g=S[S.score_frac.notna()].copy()
clean=g[g.unans_ratio==0]
# ability from OTHER undisrupted graded sessions (leave-session-out)
def other_ability(r):
    o=clean[(clean.student==r.student)&(clean.exam!=r.exam)]
    return o.score_frac.mean() if len(o) else np.nan
S['ability_other']=S.apply(other_ability,axis=1)
res={}
# 1) discriminant validity: P should not track ability
d=S.dropna(subset=['ability_other'])
for k in ['P','BFI','unans_ratio']:
    r,p=spearmanr(d[k],d.ability_other); res[f'spearman_{k}_vs_ability']=(round(r,3),round(p,4),len(d))
# 2) criterion: low graded sessions, classified by other-session ability
low=S[(S.score_frac.notna())&(S.score_frac<0.6)].copy()
low['ability_other']=low.apply(other_ability,axis=1)
low=low.dropna(subset=['ability_other'])
low['infra']=(low.ability_other>=0.7).astype(int)
res['low_sessions_with_criterion']=len(low); res['infra_pos']=int(low.infra.sum())
print(low[['student','exam','score_frac','unans_ratio','P','R','C','BFI','ability_other','infra']].round(2).to_string())
if low.infra.nunique()==2:
    for k in ['BFI','P','unans_ratio']:
        res[f'AUC_{k}']=round(roc_auc_score(low.infra,low[k]),3)
    res['AUC_anyUnans']=round(roc_auc_score(low.infra,(low.unans_ratio>0).astype(int)),3)
# 3) recovery descriptive: disrupted graded sessions -> score on later clean graded session
S.to_csv('sessions_scored.csv',index=False)
json.dump(res,open('results_validity.json','w'),indent=1,default=str); print(json.dumps(res,indent=1,default=str))
