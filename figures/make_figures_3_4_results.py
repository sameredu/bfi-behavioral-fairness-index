import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from math import erf,sqrt
from pipeline import *
B1,O2,INK,MUT='#2a78d6','#eb6834','#2b2b2b','#8a8a85'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,
  'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.grid':True,'grid.color':'#e6e6e3','grid.linewidth':0.6})
S=pd.read_csv('sessions_scored.csv'); rng=np.random.default_rng(7)
# ---- Figure 3 ----
fig,ax=plt.subplots(1,2,figsize=(7.2,2.9))
a=ax[0]; a.hist(S.BFI,bins=np.arange(0.2,1.0001,0.025),color=B1,edgecolor='white',linewidth=1); a.set_ylim(0,108)
for t in (TAU1,TAU2): a.axvline(t,color=INK,lw=1,ls='--')
n=S.tier.value_counts()
for x,lab,k in [(0.40,'No action','none'),(0.70,'Review','review'),(0.90,'Auto','auto')]:
    a.text(x,106,f'{lab}\nn = {n.get(k,0)}',ha='center',va='top',fontsize=8,color=INK)
a.set_xlabel('BFI'); a.set_ylabel('Sessions'); a.set_title('(a) BFI distribution, 675 sessions',fontsize=9,loc='left')
# (b) predicted vs observed flip probability by stability distance
Z=S[['P','R','C']].to_numpy(); t0=tier(S.BFI); rho=np.minimum(abs(S.BFI-TAU1),abs(S.BFI-TAU2)).to_numpy()
fl=np.zeros(len(S))
for _ in range(400): fl+=(tier(np.clip(Z+rng.normal(0,0.05,Z.shape),0,1)@W)!=t0)
fl/=400
bins=np.arange(0,0.21,0.02); mid=(bins[:-1]+bins[1:])/2; obs=[fl[(rho>=l)&(rho<h)].mean() if ((rho>=l)&(rho<h)).any() else np.nan for l,h in zip(bins[:-1],bins[1:])]
r=np.linspace(0,0.2,200); pred=[0.5*(1+erf(-x/(0.05*np.linalg.norm(W))/sqrt(2))) for x in r]
b=ax[1]; b.plot(r,pred,color=INK,lw=2,label='Theorem T5 prediction'); b.plot(mid,obs,'o',color=O2,ms=6,mec='white',mew=1.5,label='Observed (400 draws/session)')
b.set_xlabel('Stability distance ρ(s)'); b.set_ylabel('Tier-flip probability'); b.set_title('(b) Decision stability, σ = 0.05',fontsize=9,loc='left'); b.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig('Figure3_decision_stability.png',dpi=300)
# ---- Figure 5 ----
low=S[(S.score_frac<0.6)&S.ability_other.notna()].copy(); low['infra']=low.ability_other>=0.7
d=S[S.score_frac.notna()&S.ability_other.notna()]
fig,ax=plt.subplots(1,2,figsize=(7.2,2.9))
a=ax[0]
for dis,c,lab in [(False,B1,'No unanswered items'),(True,O2,'Unanswered items present')]:
    q=d[(d.unans_ratio>0)==dis]; a.scatter(q.ability_other,q.score_frac+rng.uniform(-.01,.01,len(q)),s=16,color=c,edgecolor='white',linewidth=0.6,label=lab)
a.axhline(0.6,color=MUT,lw=1,ls=':'); a.axvline(0.7,color=MUT,lw=1,ls=':')
a.set_xlabel('Score on other undisrupted assessments'); a.set_ylabel('Recorded session score'); a.set_title('(a) Recorded score vs. own ability',fontsize=9,loc='left'); a.legend(frameon=True,facecolor='white',edgecolor='none',framealpha=1,fontsize=7.5,loc='center left',bbox_to_anchor=(0.0,0.38))
b=ax[1]
for k,(g,lab) in enumerate([(True,f'Infrastructure-consistent\n(n = {int(low.infra.sum())})'),(False,f'Ability-consistent\n(n = {int((~low.infra).sum())})')]):
    q=low[low.infra==g]; b.scatter(k+rng.uniform(-.12,.12,len(q)),q.BFI,s=22,color=B1,edgecolor='white',linewidth=0.8)
for t in (TAU1,TAU2): b.axhline(t,color=INK,lw=1,ls='--')
b.set_xticks([0,1]); b.set_xticklabels([f'Infrastructure-consistent\n(n = {int(low.infra.sum())})',f'Ability-consistent\n(n = {int((~low.infra).sum())})'],fontsize=8)
b.set_xlim(-0.5,1.5); b.set_ylabel('BFI'); b.set_title('(b) BFI of low-score sessions (< 0.60)',fontsize=9,loc='left')
fig.tight_layout(); fig.savefig('Figure4_validity.png',dpi=300)
print('ok')
