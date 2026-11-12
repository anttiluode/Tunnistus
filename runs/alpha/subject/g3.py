import sim, numpy as np
def beats_of(U,T=6000,inj=None):
    spec={'units':[U],'record':sim.ZS(),'ticks':T}
    if inj: spec['inject']=inj
    return sim.beats(sim.zsum(sim.run(spec)))
def classify(U,T=6000):
    bt=beats_of(U,T); late=bt[bt>1000]
    if len(late)==0: return 'S',None
    d=np.diff(bt[bt>=T//2])
    if len(d)<2 or bt[-1]<T-400: return '?',len(late)
    return 'C',(round(float(d.mean()),3),sorted(set(d.tolist())))
def excitable(U):
    out=[]
    for t0 in range(2000,2016):
        bt=beats_of(U,5000,{'0:V.c':[[t0,-10.0],[t0+1,-10.0]]}); late=bt[bt>1000]
        out.append((len(late), (late-t0).tolist()[:3]))
    return out
if __name__=='__main__':
    for lo,hi in [(1.4,1.45),(-0.25,-0.2),(-0.55,-0.5),(-1.4,-1.35),(-2.0,-1.95)]:
        print('boundary',lo,hi)
        for U in np.round(np.linspace(lo,hi,26),4):
            print('  ',U,classify(U))
    print('excitable 1.5:',excitable(1.5)); print('excitable 2.0:',excitable(2.0)); print('exc -0.3',excitable(-0.3))
