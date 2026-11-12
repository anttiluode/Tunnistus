import numpy as np, box, model, json
BOXP=dict()
rec=['0:V.p','0:V.r','0:V.s','0:U.p']+[f'0:Z.p{i}' for i in range(16)]
def cmp(name, spec, **kw):
    spec=dict(spec); spec.setdefault('record',rec); spec.setdefault('ticks',1500)
    b=box.run(spec); p=dict(BOXP); p.update(kw); m=model.run(spec,**p)
    out=[]
    for k in spec['record']:
        d=np.abs(np.array(b[k])-np.array(m[k]))
        if d.max()>1e-6: out.append((k,round(float(d.max()),4),int(np.argmax(d>1e-6))))
    print(name,'OK' if not out else out[:6]); return b,m
if __name__=='__main__':
    cmp('base',{'units':[1.0]})
    for k in (0.0,0.3,0.6,1.3,1.6,2.0,3.0,-1.0): cmp(f'U.k1={k}',{'units':[k]})
    for port in ('V.a','V.c','V.d','X.a','Z.b'):
        for val in (0.7,-1.3):
            cmp(f'inj {port} {val}',{'units':[1.0],'inject':{'0:'+port:[[300,val],[301,val],[640,val],[777,val*2]]}})
    cmp('inj V.d sustained',{'units':[1.0],'inject':{'0:V.d':[[t,0.8] for t in range(200,900)]}})
    cmp('settle',{'units':[1.0,0.4],'settle':333,'edges':[['0:Z.p0','1:V.c',-2.0],['1:V.p','0:X.a',0.3],['0:V.r','1:Z.b',0.5],['1:V.s','0:V.a',0.2],['0:U.p','1:V.d',1.0]],'record':rec+['1:V.p','1:Z.p0','1:Z.p2','1:V.r']})
    print(box.status())
