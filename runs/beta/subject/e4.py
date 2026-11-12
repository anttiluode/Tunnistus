import numpy as np, box, model, json
from e3 import BOXP, rec
spec={'units':[1.0],'inject':{'0:V.d':[[300,0.7],[301,-1.3],[640,2.0]]},'record':rec,'ticks':700}
b=box.run(spec); m=model.run(spec,**BOXP)
vb=np.array(b['0:V.p']); vm=np.array(m['0:V.p'])
for t in (299,300,301,302): print(t,vb[t],vm[t],vb[t]/vm[t])
for l in (0.5,0.25,1.0,2.0):
    m=model.run(spec,d_used=True,lit05=l,**BOXP)
    print(l, max(np.abs(np.array(b[k])-np.array(m[k])).max() for k in rec))
# U.k1=2 discrepancy
spec={'units':[2.0],'record':rec,'ticks':30}
b=box.run(spec); m=model.run(spec,**BOXP)
print(b['0:V.p'][:12]); print(m['0:V.p'][:12])
for k in ('0:Z.p5','0:Z.p11','0:Z.p0'): print(k,b[k][5:14],m[k][5:14])
