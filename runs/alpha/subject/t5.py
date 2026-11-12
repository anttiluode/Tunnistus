import sim, box, numpy as np
# unit1 receives a single source through V.c at weight 10 => c1 = 0.5+0.1*(0+10*src) at tick0 (U=0)
c1s=np.linspace(-3,3,600001)
for src in ['V.r','V.s','V.p','U.p','Z.p0']:
    spec={'units':[1.0,0.0],'edges':[[f'0:{src}','1:V.c',1.0]],'record':['1:V.p',f'0:{src}'],'ticks':3}
    b=box.run(spec); m=sim.run(spec)
    # invert tick0: y=c1 - tanh(4*c1)  (a=0,u=-0.1) not monotone; just compare candidates
    print(src,'box 1:V.p',np.round(b['1:V.p'],5),'model',np.round(m['1:V.p'],5),'recorded src',np.round(b[f'0:{src}'],4))
    for cand in [0.0,0.2965453866853446,-1.0,0.8739509815096245,1.0]:
        c1=0.5+0.1*cand; print('    if src(t=-1)=%.4f -> %.5f'%(cand,c1-np.tanh(4*c1)))
