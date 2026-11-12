import sim, numpy as np, sys
def badcount(S, rng=range(1500,1640)):
    bad=0; resp={}
    for t0 in rng:
        bt=sim.beats(sim.zsum(sim.run({'units':[S],'inject':{'0:V.c':[[t0,-10.0],[t0+1,-10.0]]},'record':sim.ZS(),'ticks':t0+2500})))
        late=bt[bt>1000]; r=tuple((late-t0).tolist()); resp[r]=resp.get(r,0)+1
        if len(late)!=1: bad+=1
    return bad,resp
if __name__=='__main__':
    for S in [float(x) for x in sys.argv[1:]]:
        z=sim.zsum(sim.run({'units':[S],'record':sim.ZS(),'ticks':3000}))
        print(S, badcount(S), 'late Z uniq', sorted(set(np.round(z[2000:],3).tolist())))
