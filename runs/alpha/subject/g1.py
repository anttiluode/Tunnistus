import rules, json, copy, numpy as np, warnings
warnings.filterwarnings('ignore')
base=json.load(open('graph.json'))
def vp(spec,T=400):
    g=rules.Graph(spec); out=[]
    for i in range(T): g.step(); out.append(g.nodes['V'].v1)
    return np.array(out)
ref=vp(base)
tests={'V.k1':[0.4,0.7],'V.k2':[0.8,1.2],'V.k3':[2.0,6.0],'V.k4':[0.0,0.5,5.0],'V.k6':[0.0,1.0],'V.k7':[0.0,-3.0,10.0],'V.k8':[0.0,5.0],
       'V.k9':[0.03,0.3],'V.k10':[25,80],'V.k11':[0.0,3.0],'X.k1':[128,512],'Y.k1':[64,1024],'Z.k1':[2,8,32],'Z.k2':[0.5,1.5]}
for key,vals in tests.items():
    nid,k=key.split('.'); res=[]
    for v in vals:
        s=copy.deepcopy(base)
        for n in s['nodes']:
            if n['id']==nid: n['state'][k]=v
        try: res.append(bool(np.abs(vp(s)-ref).max()>1e-12))
        except Exception as e: res.append('ERR '+type(e).__name__)
    print(key, vals, res, '=>', 'LIVE' if any(r is True for r in res) else 'DEAD')
