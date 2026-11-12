"""Fast equivalent of rules.py for N units with extra edges / injections, mirroring box.run.
All parameters are overridable through P (dict) so hypotheses about the box can be tested."""
import numpy as np, math

DEF = dict(Vk1=0.5, Vk2=1.0, Vk3=3.0, Vk4=0.1, Vk5=1, Vk6=0.01, Vk7=1.1636187981416324, Vk8=0.5, Vk9=0.1,
           Vk10=50, Vk11=1.0, v1=0.8739509815096245, v2=0.0, v3=0.0,  # box starts V.r,V.s at 0 (docs: 0.2965, -1.0)
           Xk1=256, Yk1=256, Zk1=16, Zk2=1.0,
           lit01=0.1, lit05=0.5, lit10=10.0, lit2=2.0, X5=5, X50=50,
           extra=0,        # extra one-tick stages between X and Y
           d_used=False, nsum=4, hmax=200)

_cache = {}
def pattern(n, Xk1=256, Yk1=256, Zk1=16):
    key = (n, Xk1, Yk1, Zk1)
    if key in _cache: return _cache[key]
    y, x = np.mgrid[0:Xk1, 0:Xk1]
    with np.errstate(divide="ignore"):
        g = ((x // n) + (y // n)) % 2
    m = np.stack([g]*3, axis=-1).astype(np.float32)
    m = np.mean(m, axis=2)
    s = int(np.ceil(np.sqrt(Yk1))); b = m.shape[0] // s
    t = m[:s*b, :s*b].reshape(s, b, s, b).mean(axis=(1, 3), dtype=np.float32)
    f = t.flatten()
    if len(f) >= Yk1: v = f[:Yk1]
    else:
        v = np.zeros(Yk1, dtype=np.float32); v[:len(f)] = f
    mx = np.max(np.abs(v))
    if mx > 0: v = v / mx
    z = np.zeros(Zk1, dtype=np.float32); k = min(len(v), Zk1); z[:k] = v[:k]
    _cache[key] = z
    return z

class Unit:
    def __init__(s, uk1, P):
        s.P = P; s.uk1 = float(uk1)
        s.k7 = P['Vk7']; s.k11 = P['Vk11']
        s.v1 = P['v1']; s.v2 = P['v2']; s.v3 = P['v3']; s.h = []
        s.xv = None            # pattern n currently held by X (None = zeros)
        s.pipe = [None]*P['extra']
        s.yv = np.zeros(P['Zk1'], dtype=np.float32)  # Y out (first Zk1 entries)
        s.zo = np.zeros(P['Zk1'])
    def out(s, port):
        if port == 'U.p': return s.uk1
        if port == 'V.p': return s.v1
        if port == 'V.r': return s.v2
        if port == 'V.s': return s.v3
        if port.startswith('Z.p'): return float(s.zo[int(port[3:])])
        raise KeyError(port)
    def f(s, x, k): return 2.0/(1.0+np.exp(-x*k)) - 1.0
    def step(s, ext):
        P = s.P
        # gather inputs from previous outputs
        a = sum(float(s.zo[i]) for i in range(P['nsum'])) + ext.get('V.a', 0.0)
        c = s.uk1 + ext.get('V.c', 0.0)
        d = ext.get('V.d', None)
        xa = s.v1 + ext.get('X.a', 0.0)
        zb = ext.get('Z.b', None)
        xin = s.xv; yin = s.yv
        # V
        c1 = P['Vk1'] + c*P['lit01']
        g1 = P['Vk2']
        if d is not None: g1 *= (1.0 + d*P['lit05'])
        k2 = g1 if P['d_used'] else P['Vk2']
        x = a
        s.h.append(x)
        if len(s.h) > P['hmax']: s.h.pop(0)
        k3 = P['Vk3']
        if P['Vk5'] == 1:
            z = float(np.var(np.array(s.h[-int(P['Vk10']):]))) if len(s.h) > 10 else 0.0
            u = z - P['Vk9']; e = x - c1
            if u > 0:
                y = c1 + s.f(e, k3)/k3; s.v3 = -1.0
            else:
                w = c1 + e*(1.0 + abs(u)*P['lit10'])
                y = c1 + np.tanh((w - c1)*P['lit2']); s.v3 = 1.0
            s.v2 = u
            s.v1 = float(y*k2)
        elif P['Vk5'] == 0:
            e = x - c1
            if abs(e) < P['Vk4']:
                s.v3 = 0.0; y = x
            else:
                g = s.f(e, k3); s.k7 += e*P['Vk6']; s.k7 = float(np.clip(s.k7, -P['Vk8'], P['Vk8']))
                y = c1 + g/k3 - s.k7; s.v3 = -np.sign(e)
            s.v2 = e; s.v1 = float(y*k2)
        else:
            s.v1 = float(np.tanh(x*k3)/k3*k2); s.v2 = 0.0; s.v3 = 0.0
        # X
        aa = xa or 0.1
        n = int(P['X5'] + aa*P['X50'])
        newx = n
        # extra stages
        if s.pipe:
            s.pipe.append(xin); yin_src = s.pipe.pop(0)
        else:
            yin_src = xin
        # Y
        if yin_src is None: newy = np.zeros(P['Zk1'], dtype=np.float32)
        else: newy = pattern(yin_src, P['Xk1'], P['Yk1'], P['Zk1'])
        # Z
        sc = P['Zk2']
        if zb is not None: sc *= (1.0 + zb)
        s.zo = np.asarray(yin, dtype=np.float64)*sc
        s.xv = newx; s.yv = newy

def run(spec, **over):
    P = dict(DEF); P.update(over)
    units = [Unit(k, P) for k in spec['units']]
    edges = [(int(a.split(':')[0]), a.split(':')[1], int(b.split(':')[0]), b.split(':')[1], w) for a, b, w in spec.get('edges', [])]
    inj = {}
    for addr, lst in spec.get('inject', {}).items():
        ui, port = addr.split(':'); 
        for t, v in lst: inj.setdefault(int(t), []).append((int(ui), port, v))
    rec = {r: [] for r in spec.get('record', [])}
    recp = [(r, int(r.split(':')[0]), r.split(':')[1]) for r in rec]
    settle = spec.get('settle', 0)
    for T in range(-settle, spec['ticks']):
        ext = [dict() for _ in units]
        if T >= 0:
            for su, sp, du, dp, w in edges:
                ext[du][dp] = ext[du].get(dp, 0.0) + units[su].out(sp)*w
            for du, dp, v in inj.get(T, []):
                ext[du][dp] = ext[du].get(dp, 0.0) + v
        for i, u in enumerate(units): u.step(ext[i])
        if T >= 0:
            for r, ui, port in recp: rec[r].append(units[ui].out(port))
    return rec

def beats(tr, thr=3.0):
    """tr: array of Z sum. Rising crossings."""
    tr = np.asarray(tr); return np.where((tr[1:] > thr) & (tr[:-1] <= thr))[0] + 1
ZS = lambda u=0: [f"{u}:Z.p{i}" for i in range(4)]
def zsum(tr, u=0): return np.sum([tr[f"{u}:Z.p{i}"] for i in range(4)], axis=0)
