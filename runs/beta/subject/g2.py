import numpy as np, model
def per(uk1=1.0, T=9000, **kw):
    r=model.run({'units':[uk1],'record':model.ZP(),'ticks':T},**kw)
    b=[x for x in model.beats(model.zsum(r)) if x>=T//2]
    # beat: rises above 3
    if len(b)<3: return 'silent', len(b)
    d=np.diff(b); return round(float(d.mean()),3), (len(b), int(d.min()), int(d.max()))
if __name__=='__main__':
    print('base',per()); print('doc',per(**model.DOC))
    cases={'a':dict(k10=80),'b':dict(k10=25),'c':dict(extra_xy=2),'d':dict(k9=0.3),'e':dict(k9=0.03),'f':dict(k3=6.0),'g':dict(k10=80,extra_xy=3),'h':dict(k9=0.3,uk1=1.6)}
    for k,v in cases.items(): print(k,v,per(**v))
