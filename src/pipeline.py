import pandas as pd, numpy as np
W=np.array([0.33,0.33,0.34]); TAU1,TAU2=0.60,0.80
def signals(S, lam=0.5, dvars=('tau','end_close','lat')):
    S=S.copy().sort_values(['student','order']).reset_index(drop=True)
    # --- behavioral features (only what Moodle grade reports contain) ---
    S['lat_n']=np.clip(S.latency/30,0,1)                       # severe late access at >=30 min
    ref=S[S.unans_ratio==0].groupby('exam').duration.median()
    S['tau']=np.clip(S.duration/S.exam.map(ref),0,1)          # time-use ratio vs. undisrupted median
    S['short']=((S.duration<5)&(S.unans_ratio>0)).astype(float) # delayed-entry pattern
    S['end_close']=S.ended_at_close.astype(float)
    S['lat']=S.lat_n
    # --- P: noisy-OR of independent disruption evidence (taxonomy patterns 1-4) ---
    u=1-S.answered_w
    S['P']=1-(1-u)*(1-S.lat_n)*(1-S.short)
    # --- R: completion recovered at the student's NEXT session of the same kind (temporal precedence) ---
    R=np.full(len(S),np.nan)
    for st,g in S.groupby('student'):
        idx=g.index.tolist()
        for a in idx:
            nxt=[b for b in idx if S.order[b]>S.order[a] and (S.kind[b]==S.kind[a] or 'mixed' in (S.kind[a],S.kind[b]))]
            if nxt: R[a]=S.answered_w[nxt[0]]
    S['R_obs']=~np.isnan(R); S['R']=np.where(np.isnan(R),0.5,R)   # 0.5 = uninformative when no later session
    # --- Golden profile: EMA of prior sessions' behavioral style; cold start = population mean ---
    V=S[list(dvars)].to_numpy(); pop=V.mean(0); D=np.zeros(len(S))
    for st,g in S.groupby('student'):
        G=pop.copy()
        for a in g.index:
            D[a]=np.linalg.norm(V[a]-G); G=lam*V[a]+(1-lam)*G
    S['Dhat']=D/(1+D); S['C']=1-S.Dhat
    return S
def bfi(S,w=W): return w[0]*S.P+w[1]*S.R+w[2]*S.C
def tier(b): return np.where(b>=TAU2,'auto',np.where(b>=TAU1,'review','none'))
