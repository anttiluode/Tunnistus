import model, numpy as np, sys
def robust(S, t0s=range(2000,2100), tail=900):
    r=model.run({'units':[S],'record':model.ZP(),'ticks':4000})
    if [x for x in model.beats(model.zsum(r)) if x>1000]: return 'clock'
    fails=0
    for t0 in t0s:
        r=model.run({'units':[S],'record':model.ZP(),'ticks':t0+tail,'inject':{'0:V.c':[[t0,-10.0],[t0+1,-10.0]]}})
        n=len([x for x in model.beats(model.zsum(r)) if x>1000])
        if n!=1: fails+=1
    return fails
for S in [float(x) for x in sys.argv[1:]]: print(S, robust(S), flush=True)
