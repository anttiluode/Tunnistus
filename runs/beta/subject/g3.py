import numpy as np, model
def classify(k, T=5000):
    r=model.run({'units':[k],'record':model.ZP(),'ticks':T})
    b=[x for x in model.beats(model.zsum(r)) if x>1000]
    if len(b)>=3:
        d=np.diff(b); return ('clock', float(d.mean()), int(d.min()), int(d.max()))
    if len(b)>0: return ('odd',len(b))
    res=[]
    for t0 in (2000,2001,2002,2003,2004,2013,2500):
        r=model.run({'units':[k],'record':model.ZP(),'ticks':T,'inject':{'0:V.c':[[t0,-10.0],[t0+1,-10.0]]}})
        b=[x for x in model.beats(model.zsum(r)) if x>1000]; res.append(len(b))
    return ('silent',res)
if __name__=='__main__':
    import sys
    lo,hi,n=map(float,sys.argv[1:4])
    for k in np.round(np.linspace(lo,hi,int(n)),4): print(k, classify(float(k)), flush=True)
