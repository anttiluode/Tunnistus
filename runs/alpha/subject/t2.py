import sim, box, numpy as np, json
rec1=lambda u:[f'{u}:V.p',f'{u}:V.r',f'{u}:V.s',f'{u}:U.p']+[f'{u}:Z.p{i}' for i in range(16)]
def cmp(name, spec, **over):
    m=sim.run(spec,**over); b=box.run(spec)
    worst=0; first=None; wk=None
    for k in spec['record']:
        d=np.abs(np.array(m[k])-np.array(b[k]))
        nz=np.where(d>1e-6)[0]
        if len(nz) and (first is None or nz[0]<first): first=nz[0]; wk=k
        worst=max(worst,d.max())
    print(f'{name:40s} maxdiff {worst:.3g} first {first} {wk}')
    return m,b
if __name__=='__main__':
    for U in [-3,-1,0,0.3,0.5,0.8,1.2,1.6,2.0,3.0,5.0,8.0]:
        cmp(f'U={U}',{'units':[U],'record':rec1(0),'ticks':1500})
    for port in ['V.a','V.c','V.d','X.a','Z.b']:
        for amp in [0.3,-0.3,2.0,-2.0,-10.0]:
            inj=[[t,amp] for t in range(300,340)]+[[700,amp],[900,amp],[901,amp]]
            cmp(f'inj {port} {amp}',{'units':[1.0],'inject':{f'0:{port}':inj},'record':rec1(0),'ticks':1500})
