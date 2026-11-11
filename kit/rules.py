import numpy as np


class Node:
    ins = {}

    def __init__(self):
        self.buf = {}

    def clear(self):
        self.buf = {k: [] for k in self.ins}

    def put(self, port, value, kind, w):
        if port not in self.buf:
            return
        if kind == "s":
            try:
                f = float(value)
                if not np.isfinite(f):
                    f = 0.0
            except (ValueError, TypeError):
                f = 0.0
            self.buf[port].append(f * w)
        elif value is not None:
            self.buf[port].append(value)

    def get(self, port, how="sum"):
        v = self.buf.get(port, [])
        if not v:
            return None
        if how == "sum" and isinstance(v[0], (int, float)):
            r = np.sum(v)
            return r if np.isfinite(r) else 0.0
        return v[0]

    def step(self):
        pass

    def out(self, port):
        return None


class K0(Node):
    ins = {}
    outs = {"p": "s"}

    def __init__(self, k1=1.0):
        super().__init__()
        self.k1 = float(k1)

    def out(self, port):
        return self.k1 if port == "p" else None


class K1(Node):
    ins = {"a": "s", "b": "m", "c": "s", "d": "s"}
    outs = {"p": "s", "q": "m", "r": "s", "s": "s"}

    def __init__(self):
        super().__init__()
        self.k1 = 0.5
        self.k2 = 1.0
        self.k3 = 3.0
        self.k4 = 0.1
        self.k5 = 0
        self.k6 = 0.01
        self.k7 = 0.0
        self.k8 = 0.5
        self.k9 = 0.1
        self.k10 = 50
        self.k11 = 1.0
        self.v0 = 0.0
        self.v1 = 0.0
        self.v2 = 0.0
        self.v3 = 0.0
        self.h = []

    def f(self, x, c, k):
        return 2.0 / (1.0 + np.exp(-(x - c) * k)) - 1.0

    def m0(self, x, c):
        e = x - c
        if abs(e) < self.k4:
            self.v3 = 0.0
            y = x
        else:
            g = self.f(e, 0.0, self.k3)
            self.k7 += e * self.k6
            self.k7 = np.clip(self.k7, -self.k8, self.k8)
            y = c + g / self.k3 - self.k7
            self.v3 = -np.sign(e)
        self.v2 = e
        return y * self.k2

    def m1(self, x, c):
        if len(self.h) > 10:
            z = np.var(np.array(self.h[-self.k10:]))
        else:
            z = 0.0
        u = z - self.k9
        if u > 0:
            e = x - c
            y = c + self.f(e, 0.0, self.k3) / self.k3
            self.v3 = -1.0
        else:
            e = x - c
            w = c + e * (1.0 + abs(u) * 10.0)
            y = c + np.tanh((w - c) * 2.0)
            self.v3 = 1.0
        self.v2 = u
        if len(self.h) > 20:
            self.k7 = self.k7 * 0.99 + np.mean(self.h[-50:]) * 0.01
        return y * self.k2

    def m2(self, x):
        y = np.tanh(x * self.k3) / self.k3
        self.v2 = 0.0
        self.v3 = 0.0
        return y * self.k2

    def step(self):
        a = self.get("a", "sum")
        c = self.get("c", "sum")
        d = self.get("d", "sum")
        c1 = self.k1
        if c is not None:
            c1 += float(c) * 0.1
        g1 = self.k2
        if d is not None:
            g1 *= (1.0 + float(d) * 0.5)
        if a is not None:
            x = float(a)
            self.v0 = x
            self.h.append(x)
            if len(self.h) > 200:
                self.h.pop(0)
            if self.k5 == 0:
                self.v1 = self.m0(x, c1)
            elif self.k5 == 1:
                self.v1 = self.m1(x, c1)
            else:
                self.v1 = self.m2(x)
        b = self.get("b", "first")
        if b is not None:
            t = 1.0 + self.v3 * 0.3
            self.k11 = 0.95 * self.k11 + 0.05 * t

    def out(self, port):
        if port == "p":
            return self.v1
        if port == "q":
            b = self.get("b", "first")
            return None if b is None else np.clip(b * self.k11, 0, 1)
        if port == "r":
            return self.v2
        if port == "s":
            return self.v3
        return None


class K2(Node):
    ins = {"a": "s"}
    outs = {"p": "m"}

    def __init__(self, k1=256):
        super().__init__()
        self.k1 = int(k1)
        self.v = np.zeros((self.k1, self.k1, 3), dtype=np.float32)

    def step(self):
        a = self.get("a", "sum") or 0.1
        n = int(5 + a * 50)
        y, x = np.mgrid[0:self.k1, 0:self.k1]
        with np.errstate(divide="ignore"):
            g = ((x // n) + (y // n)) % 2
        self.v = np.stack([g] * 3, axis=-1).astype(np.float32)

    def out(self, port):
        return self.v if port == "p" else None


class K3(Node):
    ins = {"a": "m"}
    outs = {"p": "v"}

    def __init__(self, k1=256):
        super().__init__()
        self.k1 = int(k1)
        self.v = np.zeros(self.k1, dtype=np.float32)

    def step(self):
        m = self.get("a", "first")
        if m is None:
            return
        if m.ndim == 3:
            m = np.mean(m, axis=2)
        s = int(np.ceil(np.sqrt(self.k1)))
        b = m.shape[0] // s
        t = m.reshape(s, b, s, b).mean(axis=(1, 3), dtype=np.float32)
        f = t.flatten()
        if len(f) >= self.k1:
            self.v = f[:self.k1]
        else:
            self.v = np.zeros(self.k1, dtype=np.float32)
            self.v[:len(f)] = f
        mx = np.max(np.abs(self.v))
        if mx > 0:
            self.v = self.v / mx

    def out(self, port):
        return self.v if port == "p" else None


class K4(Node):
    ins = {"a": "v", "b": "s"}

    def __init__(self, k1=16, k2=1.0):
        super().__init__()
        self.k1 = int(k1)
        self.k2 = float(k2)
        self.outs = {f"p{i}": "s" for i in range(self.k1)}
        self.v = np.zeros(self.k1, dtype=np.float32)
        self.o = {}

    def step(self):
        a = self.get("a", "first")
        b = self.get("b", "sum")
        s = self.k2
        if b is not None:
            s *= (1.0 + b)
        if a is None:
            self.v[:] = 0
            return
        if len(a) != self.k1:
            z = np.zeros(self.k1, dtype=np.float32)
            n = min(len(a), self.k1)
            z[:n] = a[:n]
            a = z
        self.v = a * s
        for i in range(self.k1):
            self.o[f"p{i}"] = float(self.v[i])

    def out(self, port):
        if port.startswith("p"):
            return self.o.get(port, 0.0)
        return None


KINDS = {"K0": K0, "K1": K1, "K2": K2, "K3": K3, "K4": K4}


class Graph:
    def __init__(self, spec):
        self.nodes = {}
        for n in spec["nodes"]:
            node = KINDS[n["kind"]]()
            for k, v in n.get("state", {}).items():
                if hasattr(node, k):
                    setattr(node, k, v)
            self.nodes[n["id"]] = node
        self.edges = [(self.nodes[e["from"][0]], e["from"][1], self.nodes[e["to"][0]], e["to"][1],
                       e.get("w", 1.0)) for e in spec["edges"]]
        self.t = 0

    def step(self, extra=None):
        for node in self.nodes.values():
            node.clear()
        for s, sp, d, dp, w in self.edges:
            d.put(dp, s.out(sp), s.outs[sp], w)
        for (nid, port), value in (extra or {}).items():
            self.nodes[nid].put(port, value, "s", 1.0)
        for node in self.nodes.values():
            node.step()
        self.t += 1
