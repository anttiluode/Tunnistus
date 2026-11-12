import sim, numpy as np
def case(U=1.0, **over):
    tr=sim.run({'units':[U],'record':sim.ZS(),'ticks':9000},**over)
    z=sim.zsum(tr); bt=sim.beats(z); b2=bt[bt>=4500]
    d=np.diff(b2)
    return ('silent' if len(b2)<3 else round(float(d.mean()),3)), len(bt), len(b2), (sorted(set(d.tolist()))[:8] if len(b2)>1 else None), bt[:4]
cases={'base':{}, 'a':dict(Vk10=80),'b':dict(Vk10=25),'c':dict(extra=1),'d':dict(Vk9=0.3),'e':dict(Vk9=0.03),'f':dict(Vk3=6.0),
       'g':dict(Vk10=80,extra=2),'h':dict(Vk9=0.3,U=1.6)}
for k,v in cases.items(): print(k, v, case(**v))
# robustness: v2/v3 initial and neighbours
for k,v in {'a79':dict(Vk10=79),'a81':dict(Vk10=81),'b24':dict(Vk10=24),'b26':dict(Vk10=26),'d.29':dict(Vk9=.29),'d.31':dict(Vk9=.31),'e.02':dict(Vk9=.02),'e.04':dict(Vk9=.04),'h1.5':dict(Vk9=.3,U=1.5),'h1.7':dict(Vk9=.3,U=1.7),'U1.6':dict(U=1.6)}.items(): print(k, case(**v))
