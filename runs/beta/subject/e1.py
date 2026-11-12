import numpy as np, box, model, json
spec={'units':[1.0],'record':['0:V.p','0:V.r','0:V.s','0:U.p']+model.ZP()+['0:Z.p4','0:Z.p15'],'ticks':3000}
b=box.run(spec); m=model.run(spec)
json.dump(b,open('e1_box.json','w'))
for k in spec['record']:
    B=np.array(b[k]);M=np.array(m[k]); d=np.abs(B-M)
    print(k,'maxdiff',d.max(),'first diff tick',int(np.argmax(d>1e-9)) if d.max()>1e-9 else None)
zb=model.zsum(b); zm=model.zsum(m)
print('box beats',model.beats(zb)[:40]); print('mod beats',model.beats(zm)[:40])
np.set_printoptions(linewidth=200,precision=4,suppress=True)
print('box Vp',np.array(b['0:V.p'][:40])); print('mod Vp',np.array(m['0:V.p'][:40]))
print('box z',zb[:40]); print('mod z',zm[:40])
print('box r',np.array(b['0:V.r'][:40])); print('mod r',np.array(m['0:V.r'][:40]))
print(box.status())
