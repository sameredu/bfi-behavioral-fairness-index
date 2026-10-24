import pandas as pd, numpy as np, re, glob, os
import os
D=os.environ.get('IABFT_DATA','./data')
ORDER=[('Midterm1','M1','mixed'),('Midterm2_Theory','M2T','theory'),('Midterm2_Practical','M2P','practical'),
       ('Final_Theory','FT','theory'),('Final_Practical','FP','practical'),('Supp_Theory','ST','theory'),('Supp_Practical','SP','practical')]
def dur(s):
    s=str(s); h=re.search(r'(\d+)\s*hour',s); m=re.search(r'(\d+)\s*min',s); se=re.search(r'(\d+)\s*sec',s)
    return (int(h.group(1)) if h else 0)*60+(int(m.group(1)) if m else 0)+(int(se.group(1)) if se else 0)/60
def load():
    rows=[]
    for k,(name,code,kind) in enumerate(ORDER):
        df=pd.read_excel(f'{D}/DataBase_WEB_{name}_Anonymized.xlsx')
        qs=[c for c in df.columns if c.startswith('Q')]
        qmax=np.array([float(c.split('max')[1]) for c in qs])
        st=pd.to_datetime(df.Start_Time,format='%d %B %Y, %I:%M %p'); en=pd.to_datetime(df.End_Time,format='%d %B %Y, %I:%M %p')
        day=st.dt.date  # supplementary exams ran in two sittings on different days
        open_d=st.groupby(day).transform('min'); close_d=en.groupby(day).transform('max')
        V=df[qs].astype(str).apply(lambda c:c.str.strip())
        unans=(V=='Unanswered').values; ng=(V=='Needs_Grading').values
        num=V.apply(pd.to_numeric,errors='coerce').values
        graded_all=~np.isnan(num).any(axis=1) & ~unans.any(axis=1) | (~ng.any(axis=1))
        score=np.where(unans,0,num)
        tot=pd.to_numeric(df.filter(like='Total_Score').iloc[:,0],errors='coerce')
        tmax=float(df.filter(like='Total_Score').columns[0].split('max')[1])
        for i in range(len(df)):
            # weight by question max
            ans_w=1-(qmax*unans[i]).sum()/qmax.sum()
            fully_graded= not ng[i].any()
            # answered-item accuracy over auto-graded items that reached the server
            # (disruption-insensitive by construction: unanswered and ungraded items are excluded)
            gm=~np.isnan(num[i]) & ~unans[i]
            acc=(num[i][gm].sum()/qmax[gm].sum()) if gm.any() and qmax[gm].sum()>0 else np.nan
            rows.append(dict(student=df.Student_Label[i],section=df.Section[i],exam=code,kind=kind,order=k,
                n_q=len(qs),unans_ratio=unans[i].mean(),answered_w=ans_w,
                latency=(st[i]-open_d[i]).total_seconds()/60, duration=dur(df.Duration[i]), window=(close_d[i]-open_d[i]).total_seconds()/60,
                ended_at_close=(close_d[i]-en[i]).total_seconds()/60<=1,
                score_frac=(tot[i]/tmax) if fully_graded and not np.isnan(tot[i]) else np.nan,
                fully_graded=fully_graded, acc=acc, n_acc_items=int(gm.sum())))
    return pd.DataFrame(rows)
if __name__=='__main__':
    S=load(); S.to_csv('sessions.csv',index=False)
    print(len(S)); print(S.groupby('exam').agg(n=('student','size'),window=('window','first'),lat_med=('latency','median'),
      dur_med=('duration','median'),anyunans=('unans_ratio',lambda x:(x>0).mean()),gt50=('unans_ratio',lambda x:(x>0.5).mean()),
      allun=('unans_ratio',lambda x:(x==1).mean()),graded=('fully_graded','mean'),score=('score_frac','mean')).round(3))
