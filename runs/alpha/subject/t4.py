import sim, box, numpy as np
from t2 import cmp, rec1
rng=np.random.default_rng(1)
outs=['U.p','V.p','V.r','V.s']+[f'Z.p{i}' for i in range(16)]
ins=['V.a','V.c','V.d','X.a','Z.b']
for trial in range(12):
    n=int(rng.integers(2,6))
    units=[float(np.round(rng.uniform(-1,4),2)) for _ in range(n)]
    edges=[[f'{rng.integers(n)}:{rng.choice(outs)}',f'{rng.integers(n)}:{rng.choice(ins)}',float(np.round(rng.normal(0,0.4),2))] for _ in range(int(rng.integers(1,8)))]
    inj={}
    for _ in range(3):
        inj.setdefault(f'{rng.integers(n)}:{rng.choice(ins)}',[]).append([int(rng.integers(0,1500)),float(np.round(rng.normal(0,3),2))])
    rec=sum([rec1(u) for u in range(n)],[])
    spec={'units':units,'edges':edges,'inject':inj,'record':rec,'ticks':2500,'settle':int(rng.choice([0,0,137,1000]))}
    if trial in (4,11):
        print(units,edges,inj,spec['settle'])
        spec['ticks']=12
        m=sim.run(spec); b=box.run(spec)
        for k in rec:
            if np.abs(np.array(m[k])-np.array(b[k])).max()>1e-9: print(k,'\n model',np.round(m[k],4),'\n box  ',np.round(b[k],4))
