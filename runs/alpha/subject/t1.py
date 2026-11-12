import sim, box, numpy as np
rec=['0:V.p','0:V.r','0:V.s','0:U.p']+[f'0:Z.p{i}' for i in range(16)]
spec={'units':[1.0],'record':rec,'ticks':9000}
m=sim.run(spec); b=box.run(spec)
for k in rec:
    A=np.array(m[k]); B=np.array(b[k]); d=np.abs(A-B)
    nz=np.where(d>1e-9)[0]
    print(k, 'maxdiff',d.max(), 'first diff tick', nz[0] if len(nz) else None)
for name,t in (('model',m),('box',b)):
    z=sim.zsum(t); bt=sim.beats(z)
    print(name,'nbeats',len(bt),'first',bt[:10],'ISI 2nd half',np.diff(bt[bt>=4500])[:20], np.mean(np.diff(bt[bt>=4500])) if (bt>=4500).sum()>1 else None)
print('box V.p[:40]',np.round(b['0:V.p'][:40],3))
print('box Z  [:40]',np.round(sim.zsum(b)[:40],3))
print('box V.r[:40]',np.round(b['0:V.r'][:40],3))
print(box.status())
import pickle; pickle.dump((m,b),open('run1.pkl','wb'))
