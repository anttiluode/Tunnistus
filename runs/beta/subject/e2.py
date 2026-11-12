import numpy as np, json, math, model
b=json.load(open('e1_box.json'))
vp=np.array(b['0:V.p']); r=np.array(b['0:V.r']); s=np.array(b['0:V.s']); z=model.zsum(b)
T=len(vp)
# V: vp[t] from a=z[t-1], u=r[t]
c1=0.6
# branch u<=0
res={}
for lit2 in (2,3):
  for lit10 in (10,20):
    err=[]
    for t in range(1,T):
        if r[t]<=0:
            e=z[t-1]-c1; err.append(abs(c1+math.tanh(e*(1+abs(r[t])*lit10)*lit2)-vp[t]))
    print('low branch lit2',lit2,'lit10',lit10,'n',len(err),'maxerr',max(err))
for k3 in (2,3,4,6):
    err=[abs(c1+math.tanh((z[t-1]-c1)*k3/2)/k3-vp[t]) for t in range(1,T) if r[t]>0]
    print('high branch k3',k3,'n',len(err),'max',max(err))
print('s vs sign r consistent:',all((s[t]==-1)==(r[t]>0) for t in range(T)))
# variance window
h=[0.0]+list(z[:-1])   # a at tick t = z[t-1], a(0)=0
for k9 in (0.1,):
  for k10 in range(20,81):
    for minlen in (10,):
      err=0
      for t in range(11,T):
        hh=h[max(0,t+1-200):t+1]
        err=max(err,abs(np.var(hh[-k10:])-k9-r[t]))
      if err<1e-6: print('k10',k10,'ok',err)
# X/Y/Z: z[t] from vp[t-D]
for D in (3,4,5):
  for x5 in (5,):
    for x50 in (40,50,60):
      err=0
      for t in range(D+2,T):
        n=int(x5+(vp[t-D] or 0.1)*x50); err=max(err,abs(model.yz(n)[:4].sum()-z[t]))
      print('D',D,'x50',x50,'err',err)
