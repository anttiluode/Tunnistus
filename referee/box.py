"""The black box and the five gates. The box is core.simulate with hidden Params behind the
renamed ports of kit/BRIEF.md. Gate scoring uses the same box, so a subject is always judged on
the machine it was actually given."""
from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import core  # noqa: E402

SRC = {"U.p": "const.signal", "V.p": "coupler.signal_out", "V.r": "coupler.error", "V.s": "coupler.regime",
       **{f"Z.p{i}": f"splitter.out_{i}" for i in range(16)}}
DST = {"V.a": "coupler.signal_in", "V.c": "coupler.setpoint_mod", "V.d": "coupler.gain_mod",
       "X.a": "board.square_size", "Z.b": "splitter.scale_mod"}
MAX_UNITS, MAX_TICKS, MAX_SETTLE = 16, 20000, 5000
BEAT = ["Z.p0", "Z.p1", "Z.p2", "Z.p3"]     # what the unit itself hears; a beat is this sum rising above 3
BEAT_THR = 3.0


class BadSpec(ValueError):
    pass


def _addr(s, table, n):
    try:
        u, port = s.split(":")
        u = int(u)
    except Exception:
        raise BadSpec(f"address {s!r} is not 'unit:PORT'")
    if not 0 <= u < n:
        raise BadSpec(f"unit {u} out of range in {s!r}")
    if port not in table:
        raise BadSpec(f"{port!r} is not one of {sorted(table)}")
    return u, table[port]


class Box:
    def __init__(self, params: core.Params):
        self.params = params
        self.cost = 0                       # unit-ticks simulated for the subject

    def run(self, spec, params=None, charge=True):
        units = [float(c) for c in spec.get("units", [])]
        n = len(units)
        ticks, settle = int(spec.get("ticks", 1000)), int(spec.get("settle", 0))
        if not 1 <= n <= MAX_UNITS:
            raise BadSpec(f"1 to {MAX_UNITS} units")
        if not 1 <= ticks <= MAX_TICKS or not 0 <= settle <= MAX_SETTLE:
            raise BadSpec(f"ticks 1..{MAX_TICKS}, settle 0..{MAX_SETTLE}")
        edges = []
        for e in spec.get("edges", []):
            ju, jp = _addr(e[0], SRC, n)
            iu, ip = _addr(e[1], DST, n)
            edges.append((ju, jp, iu, ip, float(e[2])))
        inject = {}
        for k, pairs in spec.get("inject", {}).items():
            seq = np.zeros(ticks)
            for t, v in pairs:
                if 0 <= int(t) < ticks:
                    seq[int(t)] += float(v)
            inject[_addr(k, DST, n)] = seq
        record = [_addr(r, SRC, n) for r in spec.get("record", [])]
        if charge:
            self.cost += n * (ticks + settle)
        rec = core.simulate(units, edges, inject, record, ticks, settle, params or self.params)
        return {r: rec[a] for r, a in zip(spec.get("record", []), record)}

    # ---------------------------------------------------------------- helpers
    def beat_ticks(self, spec, unit, params=None):
        s = dict(spec, record=[f"{unit}:{p}" for p in BEAT])
        r = self.run(s, params, charge=False)
        return core.beats(sum(r.values()), BEAT_THR)

    def period(self, const, params=None, T=9000):
        b = self.beat_ticks({"units": [const], "ticks": T}, 0, params)
        late = b[b > T // 2]
        if len(late) < 3:
            return None
        return float(np.diff(late).mean())


# ======================================================================= gate 1: live or dead
PARAM_PROBES = {"V.k1": ("setpoint", 0.55), "V.k2": ("gain", 0.9), "V.k3": ("sharpness", None),
                "V.k4": ("dead_zone", 0.3), "V.k6": ("integral_gain", 0.1), "V.k7": ("integral_state", 0.0),
                "V.k8": ("integral_limit", 0.1), "V.k9": ("target_variance", None),
                "V.k10": ("variance_window", None), "V.k11": ("image_gain_state", 0.5),
                "X.k1": ("size", 128), "Y.k1": ("output_dim", 64), "Z.k1": ("num_outputs", 3),
                "Z.k2": ("scale", 0.9)}
G1_ITEMS = list(DST) + list(PARAM_PROBES)


def g1_truth(box: Box):
    """LIVE if changing that one thing changes V.p, with the loop running and being poked."""
    T = 3000
    rng = np.random.default_rng(7)
    poke = {"0:V.a": [[int(t), float(rng.normal(0, 1))] for t in rng.choice(T, 60, replace=False)],
            "0:V.c": [[int(t), float(rng.normal(0, 3))] for t in rng.choice(T, 60, replace=False)]}
    base_spec = {"units": [1.0], "ticks": T, "record": ["0:V.p"], "inject": poke}
    base = box.run(base_spec, charge=False)["0:V.p"]
    truth = {}
    for port in DST:
        inj = dict(poke)
        extra = [[int(t), float(rng.normal(0, 1))] for t in rng.choice(T, 80, replace=False)]
        inj[f"0:{port}"] = inj.get(f"0:{port}", []) + extra
        truth[port] = not np.array_equal(base, box.run(dict(base_spec, inject=inj), charge=False)["0:V.p"])
    for ident, (field, value) in PARAM_PROBES.items():
        cur = getattr(box.params, field)
        if value is None:
            value = int(cur * 1.5) if isinstance(cur, int) else cur * 1.5
        p = replace(box.params, **{field: value})
        truth[ident] = not np.array_equal(base, box.run(base_spec, p, charge=False)["0:V.p"])
    return truth


def g1_score(box, answer):
    truth = g1_truth(box)
    rows = {k: {"truth": "LIVE" if v else "DEAD", "answer": str(answer.get(k, "")).upper()} for k, v in truth.items()}
    right = sum(r["truth"] == r["answer"] for r in rows.values())
    return {"right": right, "of": len(rows), "rows": rows}


# ======================================================================= gate 0: does the box match the paper?
def g0_score(truth, answer):
    claimed = {d["id"]: d.get("value") for d in answer.get("differences", [])}
    says_match = bool(answer.get("matches_documentation"))
    rows, found, values_ok = {}, 0, 0
    for ident, v in truth.items():
        got = claimed.get(ident)
        hit = ident in claimed
        if isinstance(v, bool):
            ok = hit and bool(got) == v
        elif isinstance(v, int):
            ok = hit and got is not None and float(got) == v
        else:
            ok = hit and got is not None and abs(float(got) - v) <= 0.03 * abs(v)
        found += hit
        values_ok += ok
        rows[ident] = {"truth": v, "claimed": got, "named": hit, "value_ok": bool(ok)}
    false_alarms = {k: v for k, v in claimed.items() if k not in truth}
    return {"verdict_right": says_match == (not truth), "said_match": says_match, "changed": len(truth),
            "named": found, "values_right": values_ok, "false_alarms": false_alarms, "rows": rows}


# ======================================================================= gate 2: predict what the box cannot be asked
def g2_cases(p: core.Params):
    """Interventions on internals the box API cannot reach. Each is applied to THIS box."""
    return {
        "a": ("V.k10 set to 80", 1.0, replace(p, variance_window=80)),
        "b": ("V.k10 set to 25", 1.0, replace(p, variance_window=25)),
        "c": ("one more one-tick stage inserted between X and Y", 1.0, replace(p, extra_latches=p.extra_latches + 1)),
        "d": ("V.k9 set to 0.3", 1.0, replace(p, target_variance=0.3)),
        "e": ("V.k9 set to 0.03", 1.0, replace(p, target_variance=0.03)),
        "f": ("V.k3 set to 6", 1.0, replace(p, sharpness=6.0)),
        "g": ("V.k10 set to 80 and two more stages between X and Y", 1.0,
              replace(p, variance_window=80, extra_latches=p.extra_latches + 2)),
        "h": ("V.k9 set to 0.3, with U.k1 = 1.6", 1.6, replace(p, target_variance=0.3)),
    }


def g2_score(box, answer):
    rows, right = {}, 0
    for key, (text, const, p) in g2_cases(box.params).items():
        true = box.period(const, p)
        got = answer.get(key)
        if true is None:
            ok = isinstance(got, str) and got.lower().startswith("silent")
        else:
            ok = isinstance(got, (int, float)) and abs(float(got) - true) <= 1.0
        right += ok
        rows[key] = {"case": text, "truth": "silent" if true is None else round(true, 2), "predicted": got, "ok": bool(ok)}
    return {"right": right, "of": len(rows), "rows": rows}


# ======================================================================= gate 3: relay -> clock
def g3_score(box, sub):
    cs, cc, pred = float(sub["silent"]), float(sub["clock"]), sub.get("period")
    T = 8000
    b = box.beat_ticks({"units": [cs], "ticks": T}, 0)
    silent = not np.any(b > 1000)
    kick = box.beat_ticks({"units": [cs], "ticks": T, "inject": {"0:V.c": [[4000, -10.0], [4001, -10.0]]}}, 0)
    kick = kick[kick > 1000]
    excitable = len(kick) >= 1 and kick.min() < 4030 and kick.max() < 4100
    true_p = box.period(cc)
    clock = true_p is not None
    period_ok = clock and isinstance(pred, (int, float)) and abs(pred - true_p) <= 1.0
    return {"silent_is_silent": bool(silent), "silent_is_excitable": bool(excitable), "clock_beats": bool(clock),
            "true_period": true_p, "predicted_period": pred, "period_ok": bool(period_ok),
            "change": abs(cc - cs), "pass": bool(silent and excitable and clock and period_ok)}


# ======================================================================= gates 4 and 5: memory, and a reader
def patterns(lap, seed):
    rng = np.random.default_rng(seed)
    pats = [np.zeros(lap, int)]
    one = np.zeros(lap, int)
    one[int(rng.integers(lap))] = 1
    pats.append(one)
    while len(pats) < 12:
        pats.append((rng.random(lap) < 0.3).astype(int))
    return pats


def _check_net(sub):
    lap = int(sub["lap"])
    if not 2 <= lap <= 256:
        raise BadSpec("lap 2..256")
    return lap, int(sub.get("settle", 1500)), max(40, -(-2000 // lap))


def _read(trace_sum, start, lap, thr):
    return (trace_sum[start:start + lap] > thr).astype(int)


def g4_score(box, sub, seed):
    lap, settle, hold = _check_net(sub)
    w, rd = sub["write"], sub["read"]
    off = int(rd.get("offset", 0))
    ticks = 2 * hold * lap + off + lap
    kept = 0
    detail = []
    for pat in patterns(lap, seed):
        spec = {"units": sub["units"], "edges": sub.get("edges", []), "settle": settle, "ticks": ticks,
                "inject": {w["port"]: [[int(t), float(w["amp"])] for t in np.flatnonzero(pat)]},
                "record": list(rd["ports"])}
        tr = sum(box.run(spec, charge=False).values())
        first = _read(tr, hold * lap + off, lap, float(rd["thr"]))
        second = _read(tr, 2 * hold * lap + off, lap, float(rd["thr"]))
        ok = np.array_equal(first, pat) and np.array_equal(second, pat)
        kept += ok
        detail.append({"ones": int(pat.sum()), "kept": bool(ok)})
    return {"kept": kept, "of": 12, "bits": lap, "held_laps": 2 * hold, "held_ticks": 2 * hold * lap,
            "pass": kept == 12, "patterns": detail}


def g5_score(box, sub, seed):
    lap, settle, hold = _check_net(sub)
    n = len(sub["units"])
    reader, gate = int(sub["reader"]), sub.get("gate")
    edges = sub.get("edges", [])
    src = lambda e: int(e[0].split(":")[0])
    dst = lambda e: int(e[1].split(":")[0])
    if any(src(e) == reader for e in edges):
        raise BadSpec("the reader may not feed anything")
    if gate is not None and any(dst(e) == gate for e in edges):
        raise BadSpec("the gate must be autonomous: no edges into it")
    w, rd = sub["write"], sub["read"]
    if int(w["port"].split(":")[0]) in (reader, gate):
        raise BadSpec("write into the memory, not the reader or gate")
    off = int(rd.get("offset", 0))
    obs = min(int(sub.get("observe", 4000)), 12000)
    laps = -(-(lap + obs) // lap) + 1
    ticks = laps * lap + off + lap
    no_gate = [e for e in edges if not (gate is not None and src(e) == gate and dst(e) == reader)]
    no_mem = [e for e in edges if not (dst(e) == reader and src(e) != gate)]

    def trains(ed, want_memory):
        out, intact = [], 0
        for pat in patterns(lap, seed + 1):
            spec = {"units": sub["units"], "edges": ed, "settle": settle, "ticks": ticks,
                    "inject": {w["port"]: [[int(t), float(w["amp"])] for t in np.flatnonzero(pat)]},
                    "record": [f"{reader}:{p}" for p in BEAT] + (list(rd["ports"]) if want_memory else [])}
            r = box.run(spec, charge=False)
            b = core.beats(sum(r[f"{reader}:{p}"] for p in BEAT), BEAT_THR)
            out.append(tuple(int(t) for t in b if lap <= t < lap + obs))
            if want_memory:
                mem = sum(r[p] for p in rd["ports"])
                intact += np.array_equal(_read(mem, laps * lap + off, lap, float(rd["thr"])), pat)
        return out, intact

    full, intact = trains(edges, True)
    distinct = len(set(full))
    res = {"distinct_reader_outputs": distinct, "of": 12, "memory_intact": intact,
           "reader_beats_on_empty": len(full[0]), "reader_beats_total": sum(len(t) for t in full)}
    level = 1 if (distinct == 12 and intact == 12) else 0
    if gate is not None:
        a, _ = trains(no_gate, False)
        b, _ = trains(no_mem, False)
        res["beats_without_gate_wire"] = sum(len(t) for t in a)
        res["beats_without_memory_wire"] = sum(len(t) for t in b)
        if level == 1 and not res["beats_without_gate_wire"] and not res["beats_without_memory_wire"]:
            level = 2
    res["level"] = level        # 0 fail, 1 a tap that copies the memory out, 2 a reader gated by an autonomous unit
    res["pass"] = level >= 1
    return res
