import sim, numpy as np, math, sys
from g4 import memory, patterns
def answer(N=14, R=50.346, wm=-33.0, wg=-34.0, observe=3600):
    a=memory(N); reader=N; gate=N+1
    a['units']=a['units']+[R,1.0]
    a['edges']=a['edges']+[[f'0:Z.p0',f'{reader}:V.c',wm],[f'{gate}:Z.p0',f'{reader}:V.c',wg]]
    a.update(reader=reader,gate=gate,observe=observe); return a
def run(a, eng, pat, cut=None):
    lap=a['lap']; r=a['reader']; g=a['gate']
    edges=a['edges']
    if cut=='gate': edges=[e for e in edges if not (e[0].startswith(f'{g}:') and e[1].startswith(f'{r}:'))]
    if cut=='mem':  edges=[e for e in edges if not (e[1].startswith(f'{r}:') and not e[0].startswith(f'{g}:'))]
    H=math.ceil(max(2000, lap+a['observe'])/lap); T=H*lap+a['read']['offset']+lap
    spec={'units':a['units'],'edges':edges,'settle':a['settle'],
          'inject':{a['write']['port']:[[int(i),a['write']['amp']] for i in np.where(pat)[0]]},
          'record':a['read']['ports']+[f'{r}:Z.p{k}' for k in range(4)],'ticks':T}
    tr=eng.run(spec)
    z=np.sum([tr[f'{r}:Z.p{k}'] for k in range(4)],axis=0); bt=sim.beats(z); bt=bt[(bt>=lap)&(bt<lap+a['observe'])]
    zm=np.sum([tr[p] for p in a['read']['ports']],axis=0); s=H*lap+a['read']['offset']
    held=np.array_equal((zm[s:s+lap]>3).astype(int),pat)
    return tuple(bt.tolist()), held
def decode(bt, lap=56):
    out=np.zeros(lap,int)
    for t in bt:
        k=(t-73)/59           # gate strong tick 70+59k -> reader V at 71+59k -> reader Z at 74+59k ; crossing tick may be 73 or 74
        out[int((11+3*round(k))%lap)]=1
    return out
if __name__=='__main__':
    eng=sim
    if 'box' in sys.argv: import box; eng=box
    a=answer()
    for seed in ([5] if eng is not sim else range(4)):
        pats=patterns(56,seed); trains=[]; ok=True
        for pat in pats:
            bt,held=run(a,eng,pat); trains.append(bt)
            cg=run(a,eng,pat,'gate')[0]; cm=run(a,eng,pat,'mem')[0]
            dec=decode(bt)
            print(' ones',pat.sum(),'reader beats',len(bt),'held',held,'cut-gate beats',len(cg),'cut-mem beats',len(cm),'decoded==pattern',np.array_equal(dec,pat), 'first',bt[:3])
        print('seed',seed,'distinct trains',len(set(trains)),'of',len(trains))
    if eng is not sim: print(box.status())
