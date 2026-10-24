"""Figures 2-4 of the paper (v3). Figure 1 is drawn by make_figure1_pipeline.py."""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from math import erf, sqrt
from pipeline import *
B1,O2,INK,MUT='#2a78d6','#eb6834','#2b2b2b','#8a8a85'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'axes.spines.top':False,'axes.spines.right':False,
  'axes.edgecolor':MUT,'axes.labelcolor':INK,'xtick.color':INK,'ytick.color':INK,'axes.grid':True,'grid.color':'#e6e6e3','grid.linewidth':0.6})
S=pd.read_csv('sessions_scored.csv'); rng=np.random.default_rng(7); Phi=np.vectorize(lambda t:0.5*(1+erf(t/sqrt(2))))
# ---- Figure 2: response over (P, Dhat) at R = 0.5 ----
P=np.linspace(0,1,201); Dh=np.linspace(0,0.5,201); PP,DD=np.meshgrid(P,Dh); Zb=bfi(PP,0.5,DD)
fig,ax=plt.subplots(figsize=(4.6,3.4)); ax.grid(False)
cf=ax.contourf(PP,DD,Zb,levels=np.arange(0.15,1.0001,0.05),cmap='Blues')
cs=ax.contour(PP,DD,Zb,levels=[TAU1,TAU2],colors=INK,linewidths=1.2,linestyles='--'); ax.clabel(cs,fmt={TAU1:'τ₁ = 0.60',TAU2:'τ₂ = 0.80'},fontsize=8)
ax.axvline(P_GATE,color=O2,lw=1.5); ax.text(P_GATE+0.01,0.47,'evidence gate\nP = 0.05',color=INK,fontsize=7.5,va='top')
cb=fig.colorbar(cf,ax=ax); cb.set_label('BFI'); ax.set_xlabel('Disruption evidence P'); ax.set_ylabel('Divergence D̂')
fig.tight_layout(); fig.savefig('Figure2_BFI_response.png',dpi=300)
# ---- Figure 3 ----
fig,ax=plt.subplots(1,2,figsize=(7.2,2.9))
a=ax[0]; a.hist(S.BFI,bins=np.arange(0.2,1.0001,0.025),color=B1,edgecolor='white',linewidth=1)
top=a.get_ylim()[1]*1.3; a.set_ylim(0,top)
for t in (TAU1,TAU2): a.axvline(t,color=INK,lw=1,ls='--')
n=S.tier.value_counts()
for x,lab,k in [(0.40,'No action','none'),(0.70,'Review','review'),(0.90,'Auto','auto')]:
    a.text(x,top*0.98,f'{lab}\nn = {n.get(k,0)}',ha='center',va='top',fontsize=8,color=INK)
a.set_xlabel('BFI'); a.set_ylabel('Sessions'); a.set_title('(a) BFI distribution (gated tiers)',fontsize=9,loc='left')
Z=S[['P','R','Dhat']].to_numpy(); b0=S.BFI.to_numpy(); t0=tier(b0)
gn=np.linalg.norm(grad(*Z.T),axis=1); rho=np.minimum(abs(b0-TAU1),abs(b0-TAU2)); zz=rho/(0.05*gn)
fl=np.zeros(len(S))
for _ in range(400): fl+=(tier(bfi(*(Z+rng.normal(0,0.05,Z.shape)).T))!=t0)
fl/=400
bins=np.arange(0,4.01,0.4); mid=(bins[:-1]+bins[1:])/2
obs=[fl[(zz>=l)&(zz<h)].mean() if ((zz>=l)&(zz<h)).sum()>=5 else np.nan for l,h in zip(bins[:-1],bins[1:])]
x=np.linspace(0,4,200); b=ax[1]
b.plot(x,Phi(-x),color=INK,lw=2,label='Theorem T5: Φ(−z)'); b.plot(mid,obs,'o',color=O2,ms=6,mec='white',mew=1.5,label='Observed (400 draws/session)')
b.set_xlabel('Standardized distance z = ρ(s) / (σ‖∇BFI‖₂)'); b.set_ylabel('Tier-flip probability'); b.set_title('(b) Decision stability, σ = 0.05',fontsize=9,loc='left'); b.legend(frameon=False,fontsize=8)
fig.tight_layout(); fig.savefig('Figure3_decision_stability.png',dpi=300)
# ---- Figure 4 ----
low=S[(S.score_frac<0.6)&S.ability_other.notna()].copy(); low['infra']=low.ability_other>=0.7
d=S[S.score_frac.notna()&S.ability_other.notna()]
fig,ax=plt.subplots(1,2,figsize=(7.2,2.9)); a=ax[0]
for dis,c,lab in [(False,B1,'No unanswered items'),(True,O2,'Unanswered items present')]:
    q=d[(d.unans_ratio>0)==dis]; a.scatter(q.ability_other,q.score_frac+rng.uniform(-.01,.01,len(q)),s=16,color=c,edgecolor='white',linewidth=0.6,label=lab)
a.axhline(0.6,color=MUT,lw=1,ls=':'); a.axvline(0.7,color=MUT,lw=1,ls=':')
a.set_xlabel('Score on other undisrupted assessments'); a.set_ylabel('Recorded session score'); a.set_title('(a) Recorded score vs. own ability',fontsize=9,loc='left')
a.legend(frameon=True,facecolor='white',edgecolor='none',framealpha=1,fontsize=7.5,loc='center left',bbox_to_anchor=(0.0,0.38))
b=ax[1]
for k,g in enumerate([True,False]):
    q=low[low.infra==g]; b.scatter(k+rng.uniform(-.12,.12,len(q)),q.BFI,s=22,color=B1,edgecolor='white',linewidth=0.8)
for t in (TAU1,TAU2): b.axhline(t,color=INK,lw=1,ls='--')
b.set_xticks([0,1]); b.set_xticklabels([f'Infrastructure-consistent\n(n = {int(low.infra.sum())})',f'Ability-consistent\n(n = {int((~low.infra).sum())})'],fontsize=8)
b.set_xlim(-0.5,1.5); b.set_ylabel('BFI'); b.set_title('(b) BFI of low-score sessions (< 0.60)',fontsize=9,loc='left')
fig.tight_layout(); fig.savefig('Figure4_validity.png',dpi=300)
print('ok')
