import numpy as np, box, model, json
from e3 import cmp, rec
P=dict(d_used=True)
rng=np.random.default_rng(1)
cmp('U=2',{'units':[2.0]},**P)
cmp('long',{'units':[1.0],'ticks':9000},**P)
outs=['U.p','V.p','V.r','V.s']+[f'Z.p{i}' for i in range(16)]; ins=['V.a','V.c','V.d','X.a','Z.b']
for trial in range(8):
    n=int(rng.integers(2,5)); units=[float(np.round(rng.uniform(-1,3),2)) for _ in range(n)]
    edges=[[f'{rng.integers(n)}:{rng.choice(outs)}',f'{rng.integers(n)}:{rng.choice(ins)}',float(np.round(rng.normal(0,1.0),2))] for _ in range(rng.integers(2,7))]
    inj={}
    for _ in range(4):
        inj.setdefault(f'{rng.integers(n)}:{rng.choice(ins)}',[]).append([int(rng.integers(0,1000)),float(np.round(rng.normal(0,3),2))])
    r=[f'{u}:{o}' for u in range(n) for o in outs]
    cmp(f'rand{trial} n={n}',{'units':units,'edges':edges,'inject':inj,'record':r,'ticks':1200,'settle':int(rng.integers(0,300))},**P)
