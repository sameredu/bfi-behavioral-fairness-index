import pandas as pd, numpy as np, json
from sklearn.metrics import roc_auc_score
from pipeline import *
S=pd.read_csv('sessions_scored.csv')
low=S[(S.score_frac<0.6)&S.ability_other.notna()].copy(); low['infra']=(low.ability_other>=0.7).astype(int)
rng=np.random.default_rng(1); B=5000
cands={'BFI':low.BFI,'P':low.P,'anyUnans':(low.unans_ratio>0).astype(float),'unans_ratio':low.unans_ratio,
       'BFI_noC':(0.5*low.P+0.5*low.R)}
boot={k:[] for k in cands}; diff=[]
y=low.infra.to_numpy()
for _ in range(B):
    i=rng.integers(0,len(low),len(low))
    if y[i].min()==y[i].max(): continue
    for k,v in cands.items(): boot[k].append(roc_auc_score(y[i],v.to_numpy()[i]))
    diff.append(boot['BFI'][-1]-boot['anyUnans'][-1])
res={k:[round(roc_auc_score(y,v),3)]+list(np.round(np.percentile(boot[k],[2.5,97.5]),3)) for k,v in cands.items()}
res['AUC_diff_BFI_minus_anyUnans_CI']=list(np.round(np.percentile(diff,[2.5,50,97.5]),3))
res['infra_tiers']=low[low.infra==1].tier.value_counts().to_dict()
res['nonInfra_tiers']=low[low.infra==0].tier.value_counts().to_dict()
# premise: share of low graded sessions whose student is able elsewhere
res['premise_share']=f"{int(y.sum())}/{len(y)}"
# C penalizes disruption? mean C disrupted vs not
res['mean_C_disrupted']=round(S[S.unans_ratio>0].C.mean(),3); res['mean_C_clean']=round(S[S.unans_ratio==0].C.mean(),3)
# recovery: students disrupted in a graded theory session with later clean graded session
json.dump(res,open('results_validity2.json','w'),indent=1,default=str); print(json.dumps(res,indent=1,default=str))
