import sim, numpy as np
from g3 import classify
Bs=[(1.4295236004116596,+1),(-0.2307455441103666,-1),(-0.5472541206894092,+1),(-1.3861460236160198,-1),(-1.9892580288272005,+1)]
for B,sgn in Bs:
    S=round(B+sgn*1e-9,12); C=round(B-sgn*1e-9,12)
    z=sim.zsum(sim.run({'units':[S],'record':sim.ZS(),'ticks':3000}))
    print('B',B,'S',S,'C',C,'clock',classify(C,20000),'silent late Z',np.round(z[-10:],3), 'late Z range',z[1500:].min(),z[1500:].max())
    bad=0; resp=set()
    for t0 in range(1500,1640):
        bt=sim.beats(sim.zsum(sim.run({'units':[S],'inject':{'0:V.c':[[t0,-10.0],[t0+1,-10.0]]},'record':sim.ZS(),'ticks':4500})))
        late=bt[bt>1000]; resp.add(tuple((late-t0).tolist()))
        if len(late)!=1: bad+=1
    print('   phases bad',bad,'responses',sorted(resp)[:6])
