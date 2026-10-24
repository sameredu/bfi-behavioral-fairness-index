import pandas as pd, numpy as np, json
from math import erf,sqrt
from load import load
from pipeline import *
rng=np.random.default_rng(2026)
S=signals(load()); S['BFI']=bfi(S); S['tier']=tier(S.BFI)
out={}
out['n']=len(S); out['R_observed']=int(S.R_obs.sum())
out['tiers']=S.tier.value_counts().to_dict()
out['tiers_by_exam']=pd.crosstab(S.exam,S.tier).to_dict()
out['BFI_range']=[float(S.BFI.min()),float(S.BFI.max())]
def H(x,b=10):
    h,_=np.histogram(x,bins=b,range=(0,1)); p=h[h>0]/h.sum(); return float(-(p*np.log(p)).sum()/np.log(b))
out['entropy']={k:H(S[k]) for k in ['P','R','C']}
out['corr']=S[['P','R','C']].corr().round(3).to_dict()
# stability: 100 gaussian draws on (P,R,C), clipped
Z=S[['P','R','C']].to_numpy(); sig=0.05; flips=0; tot=0; pred=[]
rho=np.minimum(abs(S.BFI-TAU1),abs(S.BFI-TAU2)).to_numpy()
t0=tier(S.BFI)
for _ in range(100):
    Zn=np.clip(Z+rng.normal(0,sig,Z.shape),0,1); t1=tier(Zn@W); flips+=(t1!=t0).sum(); tot+=len(t0)
Phi=lambda t:0.5*(1+erf(t/sqrt(2)))
p_pred=np.mean([Phi(-r/(sig*np.linalg.norm(W))) for r in rho])
fr=flips/tot; z=1.96; n=tot
ci=((fr+z*z/(2*n)-z*sqrt(fr*(1-fr)/n+z*z/(4*n*n)))/(1+z*z/n),(fr+z*z/(2*n)+z*sqrt(fr*(1-fr)/n+z*z/(4*n*n)))/(1+z*z/n))
out['flip_rate']=fr; out['flip_wilson']=ci; out['flip_pred_unclipped']=p_pred
out['rho_lt_0.05']=float((rho<0.05).mean())
# weight sensitivity +-0.05 (projected to simplex)
ch=[]
for k in range(3):
    for d in (-0.05,0.05):
        w=W.copy(); w[k]+=d; w=np.clip(w,1e-6,None); w/=w.sum(); ch.append(float((tier(Z@w)!=t0).mean()))
out['weight_sens_max']=max(ch); out['weight_sens']=ch
json.dump(out,open('results_core.json','w'),indent=1,default=float)
S.to_csv('sessions_scored.csv',index=False)
print(json.dumps(out,indent=1,default=float))
