import sim, box, numpy as np
from g3e import badcount
S=1.4684; C=1.4295
print('model phases 1000..1400:',badcount(S,range(1000,1400)))
z=sim.zsum(sim.run({'units':[S],'record':sim.ZS(),'ticks':3000})); print('silent late Z',np.round(z[2000:2040],3))
for eng,name in ((sim,'model'),(box,'box')):
    z=sim.zsum(eng.run({'units':[S],'record':sim.ZS(),'ticks':20000})); bt=sim.beats(z); print(name,'silent beats',bt)
    z=sim.zsum(eng.run({'units':[C],'record':sim.ZS(),'ticks':20000})); bt=sim.beats(z); d=np.diff(bt[bt>1000]); print(name,'clock n',len(bt),'ISI set',sorted(set(d.tolist())),'first',bt[:5],'last',bt[-1])
for t0 in [1000,1003,1250,2001,2002,2005,2006,3331]:
    z=sim.zsum(box.run({'units':[S],'inject':{'0:V.c':[[t0,-10.0],[t0+1,-10.0]]},'record':sim.ZS(),'ticks':6000})); bt=sim.beats(z); print('box push',t0,bt[bt>900])
print(box.status())
