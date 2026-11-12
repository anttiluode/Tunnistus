import sim, numpy as np
np.set_printoptions(linewidth=200)
tr=sim.run({'units':[1.0],'record':['0:V.p','0:V.r','0:V.s']+sim.ZS(),'ticks':3000})
z=sim.zsum(tr); bt=sim.beats(z); t0=bt[-3]-8
print('beats',bt[-5:])
print(' t   Zsum   V.p   n   u(V.r)  V.s')
for t in range(t0,t0+70):
    p=tr['0:V.p'][t]; print(t, round(z[t],3), round(p,4), int(5+50*(p or .1)), round(tr['0:V.r'][t],4), tr['0:V.s'][t])
# static map: n -> zsum
print('map n -> Zsum')
for n in range(-30,100):
    print(n, round(float(sim.pattern(n)[:4].sum()),3), end=' | ')
