import json, numpy as np, rules, model
g = rules.Graph(json.load(open('graph.json')))
ref=[]
for t in range(400):
    g.step(); V=g.nodes['V']; Z=g.nodes['Z']
    ref.append([V.v1, V.v2, V.v3]+[Z.out(f'p{i}') for i in range(4)])
ref=np.array(ref)
r = model.run({'units':[1.0],'record':['0:V.p','0:V.r','0:V.s']+model.ZP(),'ticks':400})
m=np.array([r[k] for k in r]).T
print(np.abs(ref-m).max(axis=0))
print(ref[:30,0]); print(ref[:30,3:].sum(1))
