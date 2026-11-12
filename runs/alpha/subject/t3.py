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
    try: cmp(f"net{trial} n={n} settle={spec[chr(115)+"ettle"]}",spec)
    except Exception as e: print("skip",type(e).__name__)
# zero-sum at X.a: inject exactly -V.p? can't know; self edge V.p->X.a weight -1 makes a==0 -> 'or 0.1'
cmp('X.a cancel',{'units':[1.0],'edges':[['0:V.p','0:X.a',-1.0]],'record':rec1(0),'ticks':800})
cmp('Z.b=-1 edge',{'units':[1.0,1.0],'edges':[['0:U.p','1:Z.b',-1.0]],'record':rec1(1),'ticks':800})
print(box.status())
