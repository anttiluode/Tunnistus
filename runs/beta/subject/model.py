"""Fast offline model of the documented unit (single or multi-unit), parameterised."""
import numpy as np, json, math
_cache = {}
def yz(n, xk1=256, yk1=256):
    key = (n, xk1, yk1)
    if key in _cache: return _cache[key]
    y, x = np.mgrid[0:xk1, 0:xk1]
    with np.errstate(divide="ignore"):
        g = ((x // n) + (y // n)) % 2
    m = g.astype(np.float32)
    s = int(np.ceil(np.sqrt(yk1))); b = m.shape[0] // s
    t = m[:s*b,:s*b].reshape(s, b, s, b).mean(axis=(1, 3), dtype=np.float32)
    f = t.flatten()
    if len(f) >= yk1: v = f[:yk1]
    else:
        v = np.zeros(yk1, dtype=np.float32); v[:len(f)] = f
    mx = np.max(np.abs(v))
    if mx > 0: v = v / mx
    _cache[key] = v[:16].astype(float)
    return _cache[key]

DOC = dict(k10=50, lit10=10.0, extra_xy=0, d_used=False)
DEF = dict(k1=0.5,k2=1.0,k3=3.0,k9=0.1,k10=32,lit01=0.1,lit05=0.5,lit10=20.0,lit2=2.0,x5=5,x50=50,
           zk2=1.0,extra_xy=1,d_used=True,hmax=200,minlen=10,v1=0.8739509815096245, zin=4)

class Unit:
    def __init__(s, uk1=1.0, **kw):
        p = dict(DEF); p.update(kw); s.P = p; s.uk1 = uk1
        s.v1 = p['v1']; s.h = []
        s.xn = None   # X output (n) ; None = zeros grid
        s.pipe = [None]*p['extra_xy']  # extra stages between X and Y
        s.yv = np.zeros(16)   # Y output
        s.zo = np.zeros(16)   # Z output
        s.v2 = 0.2965453866853446; s.v3 = -1.0
    def out(s, port):
        if port == 'U.p': return s.uk1
        if port == 'V.p': return s.v1
        if port == 'V.r': return s.v2
        if port == 'V.s': return s.v3
        if port.startswith('Z.p'): return s.zo[int(port[3:])]
    def step(s, inp):
        """inp: dict port->extra summed value (may be absent)."""
        P = s.P
        # gather inputs from previous state
        a = float(sum(s.zo[:P['zin']])) + inp.get('V.a', 0.0)
        c = s.uk1 + inp.get('V.c', 0.0)
        d = inp.get('V.d', None)
        xa = s.v1 + inp.get('X.a', 0.0)
        zb = inp.get('Z.b', None)
        ya = s.pipe[-1] if s.pipe else s.xn
        za = s.yv
        # V
        c1 = P['k1']; c1 += float(c) * P['lit01']
        g1 = P['k2']
        if d is not None and P['d_used']: g1 *= (1.0 + d * P['lit05'])
        s.h.append(a)
        if len(s.h) > P['hmax']: s.h.pop(0)
        z = np.var(np.array(s.h[-int(P['k10']):])) if len(s.h) > P['minlen'] else 0.0
        u = z - P['k9']; e = a - c1
        if u > 0:
            y = c1 + (2.0/(1.0+np.exp(-(e-0.0)*P['k3']))-1.0) / P['k3']; s.v3 = -1.0
        else:
            w = c1 + e*(1.0+abs(u)*P['lit10']); y = c1 + np.tanh((w-c1)*P['lit2']); s.v3 = 1.0
        s.v2 = u
        newv1 = y * g1
        # X
        aa = xa or 0.1
        newxn = int(P['x5'] + aa * P['x50'])
        # Y
        newyv = yz(ya) if ya is not None else s.yv  # zeros grid -> mx=0 -> zeros
        if ya is None: newyv = np.zeros(16)
        # Z
        sc = P['zk2'] * (1.0 + zb) if zb is not None else P['zk2']
        s.zo = np.asarray(za, dtype=np.float32).astype(float) * sc if True else None
        s.zo = (np.asarray(za, dtype=np.float32) * np.float32(sc)).astype(float) if False else np.asarray(za)*sc
        if s.pipe:
            s.pipe = [s.xn] + s.pipe[:-1]
        s.v1 = newv1; s.xn = newxn; s.yv = newyv

def run(spec, **kw):
    units = [Unit(k, **kw) for k in spec['units']]
    edges = [(int(f.split(':')[0]), f.split(':')[1], int(t.split(':')[0]), t.split(':')[1], w) for f, t, w in spec.get('edges', [])]
    inj = {}
    for addr, lst in spec.get('inject', {}).items():
        for tk, val in lst: inj.setdefault(int(tk), []).append((int(addr.split(':')[0]), addr.split(':')[1], val))
    rec = {r: [] for r in spec.get('record', [])}
    def tick(t, on):
        inps = [dict() for _ in units]
        if on:
            for fu, fp, tu, tp, w in edges:
                inps[tu][tp] = inps[tu].get(tp, 0.0) + units[fu].out(fp) * w
            for tu, tp, val in inj.get(t, []):
                inps[tu][tp] = inps[tu].get(tp, 0.0) + val
        for u, i in zip(units, inps): u.step(i)
    for t in range(spec.get('settle', 0)): tick(-1, False)
    for t in range(spec['ticks']):
        tick(t, True)
        for r in rec:
            ui, p = r.split(':'); rec[r].append(float(units[int(ui)].out(p)))
    return rec

def beats(tr, thr=3.0):
    s = np.asarray(tr); return [i for i in range(1, len(s)) if s[i] > thr and s[i-1] <= thr]
def zsum(rec, u=0): return np.sum([rec[f'{u}:Z.p{i}'] for i in range(4)], axis=0)
ZP = lambda u=0: [f'{u}:Z.p{i}' for i in range(4)]
