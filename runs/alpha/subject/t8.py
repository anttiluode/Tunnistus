import sim, numpy as np
np.set_printoptions(linewidth=200, suppress=True)
tr=sim.run({'units':[1.0],'record':[f'0:Z.p{i}' for i in range(4)],'ticks':3000})
for k in range(4):
    v=np.array(tr[f'0:Z.p{k}']); print('p%d'%k,'period values from 2830:',np.round(v[2834:2834+62],3))
    print('   max over run',v.max(),'values>0.5 in first 200:',[(t,round(x,3)) for t,x in enumerate(v[:200]) if x>0.5][:30])
