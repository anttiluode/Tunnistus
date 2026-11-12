import sim, rules, json, numpy as np, time
# check sim against rules.py for 300 ticks
g = rules.Graph(json.load(open('graph.json')))
ref=[]
t=time.time()
for i in range(300):
    g.step(); ref.append((g.nodes['V'].v1, sum(g.nodes['Z'].out(f'p{j}') for j in range(4)), g.nodes['V'].v2))
print('rules time', time.time()-t)
tr = sim.run({'units':[1.0],'record':['0:V.p','0:V.r']+sim.ZS(),'ticks':300})
ref=np.array(ref)
print(np.abs(ref[:,0]-tr['0:V.p']).max(), np.abs(ref[:,1]-sim.zsum(tr)).max(), np.abs(ref[:,2]-tr['0:V.r']).max())
print(np.round(ref[:60,0],3)); print(np.round(ref[:60,1],3))
