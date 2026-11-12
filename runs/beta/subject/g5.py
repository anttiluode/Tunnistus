import numpy as np, model, g4
def build(K=8, dynamic=True, settle=1500, Ur=30.0, Ug=1.0, wx=-0.3578, observe=4000):
    ans=g4.memory(K=K); ans['settle']=settle
    R,G=K,K+1
    ans['units']=ans['units']+[Ur,Ug]
    mem_edges=[[f'0:Z.p{i}',f'{R}:X.a',wx] for i in range(4)]
    if dynamic: gate_edges=[[f'{G}:V.s',f'{R}:V.d',2.0],[f'{G}:V.s',f'{R}:X.a',-1.3]]
    else:       gate_edges=[[f'{G}:U.p',f'{R}:V.d',-2.0/Ug],[f'{G}:U.p',f'{R}:X.a',1.3/Ug]]
    ans['edges']=ans['edges']+mem_edges+gate_edges
    ans.update(reader=R, gate=G, observe=observe)
    return ans, mem_edges, gate_edges
def trial(ans, pattern, run=model.run, cut=None):
    lap=ans['lap']; R=ans['reader']; T=lap+ans['observe']
    H=int(np.ceil(2000/lap)); T=max(T, 2*H*lap+ans['read']['offset']+lap)
    edges=[e for e in ans['edges'] if not (cut and e in cut)]
    inj=[[i,ans['write']['amp']] for i,b in enumerate(pattern) if b]
    rp=[f'{R}:Z.p{i}' for i in range(4)]
    spec={'units':ans['units'],'edges':edges,'settle':ans['settle'],'ticks':T,'record':list(ans['read']['ports'])+rp,'inject':{ans['write']['port']:inj} if inj else {}}
    r=run(spec); s=np.sum([r[p] for p in ans['read']['ports']],axis=0); zr=np.sum([r[p] for p in rp],axis=0)
    allb=model.beats(zr); b=tuple(x for x in allb if lap<=x<lap+ans['observe'])
    ok=True
    for h in (H,2*H):
        t0=h*lap+ans['read']['offset']; ok &= bool(((s[t0:t0+lap]>ans['read']['thr']).astype(int)==np.array(pattern)).all())
    return b, ok, allb, (zr[0]>3.0)
def evaluate(ans, mem_edges, gate_edges, pats, run=model.run):
    trains=[]; res=dict(mem_ok=True, cutgate=0, cutmem=0, pre=0)
    for p in pats:
        b,ok,allb,z0=trial(ans,p,run); trains.append(b); res['mem_ok']&=ok; res['pre']+=len(allb)-len(b)
        res['cutgate']+=len(trial(ans,p,run,cut=gate_edges)[2]); res['cutmem']+=len(trial(ans,p,run,cut=mem_edges)[2])
    res['distinct']=len(set(trains)); res['nbeats']=[len(t) for t in trains]
    return res
if __name__=='__main__':
    for dyn in (False, True):
        ans,me,ge=build(dynamic=dyn)
        for seed in range(3): print('dynamic' if dyn else 'const', seed, evaluate(ans,me,ge,g4.patterns(ans['lap'],seed)), flush=True)
