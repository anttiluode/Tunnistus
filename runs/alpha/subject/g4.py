import sim, numpy as np, math
def memory(N=14, U=17.0, w=-32.6):
    units=[U]*N; edges=[]
    for i in range(N):
        for k in range(4): edges.append([f'{i}:Z.p{k}', f'{i}:V.a', -1.0])   # cancel the unit's own feedback
        edges.append([f'{i}:Z.p0', f'{(i+1)%N}:V.c', w])                    # hop to next unit (4 ticks)
    return {'units':units,'edges':edges,'settle':0,'lap':4*N,
            'write':{'port':'0:V.c','amp':w},
            'read':{'ports':[f'0:Z.p{k}' for k in range(4)],'thr':3.0,'offset':3}}
def patterns(lap, seed=0):
    rng=np.random.default_rng(seed)
    P=[np.zeros(lap,int)]; s=np.zeros(lap,int); s[rng.integers(lap)]=1; P.append(s)
    for _ in range(10): P.append((rng.random(lap)<0.3).astype(int))
    return P
def test(ans, eng, pats, extra_units=None, extra_edges=None, verbose=True):
    lap=ans['lap']; H=math.ceil(2000/lap); ok=True
    for pi,pat in enumerate(pats):
        spec={'units':ans['units'],'edges':ans['edges'],'settle':ans['settle'],
              'inject':{ans['write']['port']:[[int(i),ans['write']['amp']] for i in np.where(pat)[0]]},
              'record':ans['read']['ports'],'ticks':2*H*lap+ans['read']['offset']+lap}
        tr=eng.run(spec); z=np.sum([tr[p] for p in ans['read']['ports']],axis=0)
        for h in (H,2*H):
            s=h*lap+ans['read']['offset']; got=(z[s:s+lap]>ans['read']['thr']).astype(int)
            if not np.array_equal(got,pat): ok=False; 
            if verbose and not np.array_equal(got,pat): print('pattern',pi,'lap',h,'FAIL',pat.sum(),got.sum())
    return ok
if __name__=='__main__':
    import box, sys
    ans=memory()
    for seed in range(3): print('model seed',seed,test(ans,sim,patterns(56,seed)))
    # extremes
    print('model all ones',test(ans,sim,[np.ones(56,int), np.arange(56)%2]))
    if 'box' in sys.argv:
        print('box',test(ans,box,patterns(56,7)+[np.ones(56,int), np.arange(56)%2])); print(box.status())
