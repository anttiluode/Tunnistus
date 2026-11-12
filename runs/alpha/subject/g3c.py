import sim, box, numpy as np
B=-0.2307455441103666
S=round(B-1e-9,12); C=round(B+1e-9,12); print(repr(S),repr(C),C-S)
for eng,name in ((sim,'model'),(box,'box')):
    z=sim.zsum(eng.run({'units':[S],'record':sim.ZS(),'ticks':20000})); bt=sim.beats(z); print(name,'silent: beats',bt, 'late Z',np.round(z[-6:],3))
    z=sim.zsum(eng.run({'units':[C],'record':sim.ZS(),'ticks':20000})); bt=sim.beats(z); d=np.diff(bt[bt>1000]); print(name,'clock: n',len(bt),'ISIs',sorted(set(d.tolist())),'last',bt[-1])
    for t0 in ([1000,1001,1500,2003,3337,7001] if eng is box else range(1000,1012)):
        z=sim.zsum(eng.run({'units':[S],'inject':{'0:V.c':[[t0,-10.0],[t0+1,-10.0]]},'record':sim.ZS(),'ticks':9000})); bt=sim.beats(z); print(name,'push at',t0,'beats',bt[bt>900])
    # also with settle, as a referee might do
    z=sim.zsum(eng.run({'units':[S],'inject':{'0:V.c':[[100,-10.0],[101,-10.0]]},'record':sim.ZS(),'ticks':5000,'settle':1500})); print(name,'settle push',sim.beats(z))
print(box.status())
