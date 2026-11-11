"""The no-understanding baseline: gates 3, 4 and 5 by sweeps through the box interface alone.

It reads no documentation and forms no model. It knows what the gates ask for (a silent excitable
setting, a clock setting, a ring of units joined beat-wire to port V.c, a reader with two inputs)
because a person wrote those templates in; what it searches is the numbers. It cannot attempt
gates 0, 1 (parameters) or 2, which ask about things the box interface does not expose.

Used two ways: to check that a secret mutant is solvable at all before a subject is given it, and
as the bar an investigating subject has to beat on cost.
"""
from __future__ import annotations

import numpy as np

BEAT = ["Z.p0", "Z.p1", "Z.p2", "Z.p3"]     # a beat: this sum rises above 3
WIRE = ["Z.p0", "Z.p1"]                       # the two outputs that are loud only around a beat


def onsets(run, spec, unit):
    r = run(dict(spec, record=[f"{unit}:{p}" for p in BEAT]))
    loud = sum(np.asarray(r[f"{unit}:{p}"]) for p in BEAT) > 3.0
    return np.flatnonzero(loud[1:] & ~loud[:-1]) + 1


def classify(run, c, T=6000):
    b = onsets(run, {"units": [c], "ticks": T}, 0)
    late = b[b > T // 2]
    if len(late) >= 3:
        d = np.diff(late)
        return ("clock", float(d.mean()), float(d.std()))
    k = onsets(run, {"units": [c], "ticks": T, "inject": {"0:V.c": [[3000, -10.0], [3001, -10.0]]}}, 0)
    k = k[k > 1000]
    if len(k) >= 1 and k.max() < 3100:
        return ("relay", None, None)
    return ("other", None, None)


def solve_g3(run):
    grid = np.round(np.arange(0.0, 3.01, 0.1), 2)
    kinds = [classify(run, c) for c in grid]
    pairs = [(i, i + 1) for i in range(len(grid) - 1)
             if {kinds[i][0], kinds[i + 1][0]} == {"clock", "relay"}]
    if not pairs:
        return None, grid, kinds
    i, j = pairs[0]
    lo, hi = (grid[i], grid[j]) if kinds[i][0] == "clock" else (grid[j], grid[i])   # lo: clock, hi: relay
    k_lo = kinds[i] if kinds[i][0] == "clock" else kinds[j]
    for _ in range(5):
        mid = (lo + hi) / 2
        k = classify(run, mid)
        if k[0] == "clock":
            lo, k_lo = mid, k
        elif k[0] == "relay":
            hi = mid
        else:
            break
    return {"silent": float(hi), "clock": float(lo), "period": k_lo[1]}, grid, kinds


def ring(n, c, w):
    return {"units": [c] * n,
            "edges": [[f"{i}:{p}", f"{(i + 1) % n}:V.c", w] for i in range(n) for p in WIRE]}


def solve_g4(run, relay_c, sizes=(8, 6, 4, 12), seed=0):
    rng = np.random.default_rng(seed)
    for n, w in [(n, w) for n in sizes for w in
                 [-6.0, -5.0, -7.0, -4.0, -8.0, -3.0, -9.0, -10.0, -12.0, -2.0]]:
        net = ring(n, relay_c, w)
        b = onsets(run, dict(net, settle=1500, ticks=1500, inject={"0:V.c": [[0, -10.0]]}), 0)
        if len(b) < 6:
            continue
        gaps = np.diff(b)
        if gaps.std() > 0:
            continue
        lap, off = int(gaps[0]), int(b[0])
        sub = dict(net, settle=1500, lap=lap, write={"port": "0:V.c", "amp": -10.0},
                   read={"ports": [f"0:{p}" for p in BEAT], "thr": 3.0, "offset": off % lap})
        good = True
        for _ in range(3):
            pat = (rng.random(lap) < 0.3).astype(int)
            T = 30 * lap + off + lap
            r = run(dict(net, settle=1500, ticks=T, record=sub["read"]["ports"],
                         inject={"0:V.c": [[int(t), -10.0] for t in np.flatnonzero(pat)]}))
            tr = sum(np.asarray(v) for v in r.values())
            s = 30 * lap + off % lap
            good &= np.array_equal((tr[s:s + lap] > 3.0).astype(int), pat)
        if good:
            return sub
    return None


def solve_g5(run, mem, clock_c):
    n = len(mem["units"])
    reader, gate = n, n + 1
    lap = mem["lap"]
    pat = np.zeros(lap, int)
    pat[::3] = 1
    inj = {"0:V.c": [[int(t), -10.0] for t in np.flatnonzero(pat)]}
    for a in [-2.0, -3.0, -1.0, -4.0, -5.0]:
        for b in [-4.0, -3.0, -2.0, -5.0, -1.0, -6.0]:
            me = [[f"0:{p}", f"{reader}:V.c", a] for p in WIRE]
            ge = [[f"{gate}:{p}", f"{reader}:V.c", b] for p in WIRE]
            units = mem["units"] + [mem["units"][0], clock_c]
            counts = []
            for ed in (mem["edges"] + me + ge, mem["edges"] + me, mem["edges"] + ge):
                counts.append(len([t for t in onsets(run, {"units": units, "edges": ed, "settle": 1500,
                                                           "ticks": 3000, "inject": inj}, reader) if t >= lap]))
            if counts[0] > 0 and counts[1] == 0 and counts[2] == 0:
                return dict(mem, units=units, edges=mem["edges"] + me + ge, reader=reader, gate=gate, observe=4000)
    return None
