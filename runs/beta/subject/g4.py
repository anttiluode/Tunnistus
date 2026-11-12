import numpy as np, model
def memory(K=8, U=18.0, w=-3.42, amp=-11.7):
    edges=[]
    for k in range(K):
        nx=(k+1)%K
        for i in range(4):
            edges.append([f'{k}:Z.p{i}', f'{k}:V.a', -1.0])      # cancel the unit's own loop
            edges.append([f'{k}:Z.p{i}', f'{nx}:V.c', w])        # ring: beat of k pushes k+1
    return {"units":[U]*K, "edges":edges, "settle":0, "lap":5*K,
            "write":{"port":"0:V.c","amp":amp},
            "read":{"ports":[f"0:Z.p{i}" for i in range(4)],"thr":3.0,"offset":4}}
def test(ans, pattern, run=model.run, Hticks=2000, extra_units=(), extra_edges=(), rec_extra=()):
    lap=ans['lap']; H=int(np.ceil(Hticks/lap)); T=2*H*lap+ans['read']['offset']+lap
    inj=[[i,ans['write']['amp']] for i,b in enumerate(pattern) if b]
    spec={'units':list(ans['units'])+list(extra_units),'edges':list(ans['edges'])+list(extra_edges),'settle':ans['settle'],'ticks':T,
          'record':list(ans['read']['ports'])+list(rec_extra),'inject':{ans['write']['port']:inj} if inj else {}}
    r=run(spec); s=np.sum([r[p] for p in ans['read']['ports']],axis=0)
    ok=True
    for h in (H,2*H):
        t0=h*lap+ans['read']['offset']; bits=(s[t0:t0+lap]>ans['read']['thr']).astype(int)
        ok &= bool((bits==np.array(pattern)).all())
    return ok, r
def patterns(lap, seed=0, n=10):
    rng=np.random.default_rng(seed); P=[[0]*lap]
    one=[0]*lap; one[int(rng.integers(lap))]=1; P.append(one)
    for _ in range(n): P.append([int(x) for x in (rng.random(lap)<0.3)])
    return P
if __name__=='__main__':
    ans=memory()
    lap=ans['lap']
    bad=[]
    for i in range(lap):
        p=[0]*lap; p[i]=1
        if not test(ans,p)[0]: bad.append(i)
    print('single-bit failures',bad)
    print('full',test(ans,[1]*lap)[0],'empty',test(ans,[0]*lap)[0])
    for seed in range(4): print(seed,[test(ans,p)[0] for p in patterns(lap,seed)])
