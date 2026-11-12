import sim, numpy as np
np.set_printoptions(linewidth=220, suppress=True)
for name,over in {'d':dict(Vk9=0.3),'e':dict(Vk9=0.03),'d31':dict(Vk9=0.31)}.items():
    tr=sim.run({'units':[1.0],'record':['0:V.p','0:V.r','0:V.s']+sim.ZS(),'ticks':9000},**over)
    z=sim.zsum(tr)
    print(name,'early Z',np.round(z[:80],2)); print(' late Z',np.round(z[-24:],3),'late p',np.round(tr['0:V.p'][-12:],4),'u',np.round(tr['0:V.r'][-3:],4),'s',tr['0:V.s'][-1], 'max late', z[4500:].max())
# U scan
def per(U,T=6000,**over):
    tr=sim.run({'units':[U],'record':sim.ZS(),'ticks':T},**over); z=sim.zsum(tr); bt=sim.beats(z); b2=bt[bt>=T//2]
    return (round(float(np.diff(b2).mean()),2) if len(b2)>=3 else 0), len(bt[bt>1000])
res=[]
for U in np.round(np.arange(-2,6.001,0.05),3):
    res.append((U,)+per(U))
print(' '.join(f'{u}:{p}' for u,p,n in res))
