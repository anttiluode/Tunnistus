import rules, json, copy, numpy as np, warnings, sys
warnings.filterwarnings('ignore')
class KP(rules.Node):
    ins={'a':'m'}; outs={'p':'m'}
    def __init__(s): super().__init__(); s.v=np.zeros((256,256,3),dtype=np.float32)
    def step(s):
        m=s.get('a','first')
        if m is not None: s.v=m
    def out(s,port): return s.v
rules.KINDS['KP']=KP
base=json.load(open('graph.json'))
def case(V={},U=1.0,extra=0,T=9000):
    s=copy.deepcopy(base)
    for n in s['nodes']:
        if n['id']=='V': n['state'].update(V)
        if n['id']=='U': n['state']['k1']=U
    if extra:
        s['edges']=[e for e in s['edges'] if not (e['from'][0]=='X')]
        prev='X'
        for i in range(extra):
            s['nodes'].insert(3+i,{'id':f'P{i}','kind':'KP'}); s['edges'].append({'from':[prev,'p'],'to':[f'P{i}','a']}); prev=f'P{i}'
        s['edges'].append({'from':[prev,'p'],'to':['Y','a']})
    g=rules.Graph(s); z=[]
    for i in range(T):
        g.step(); z.append(sum(g.nodes['Z'].out(f'p{j}') for j in range(4)))
    z=np.array(z); bt=np.where((z[1:]>3)&(z[:-1]<=3))[0]+1; b2=bt[bt>=T//2]
    return 'silent' if len(b2)<3 else float(np.diff(b2).mean()), len(b2)
cases={'a':dict(V={'k10':80}),'b':dict(V={'k10':25}),'c':dict(extra=1),'d':dict(V={'k9':0.3}),'e':dict(V={'k9':0.03}),'f':dict(V={'k3':6.0}),
 'g':dict(V={'k10':80},extra=2),'h':dict(V={'k9':0.3},U=1.6)}
for k in sys.argv[1:]: print(k, case(**cases[k]), flush=True)
