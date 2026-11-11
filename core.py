"""The original Perception Lab loop (ecg.json), node by node, as a family of machines.

Referee side. A subject never sees this file: it gets kit/rules.py, a renamed transcription of the
five archived node classes, and a black box served by referee/server.py.

Scheduler (perception_lab_hostv10, reproduced in GeometricNeuronOriginReview/experiments/harness.py):
every tick, all edges are read from the nodes' current outputs, then every node steps. So each edge
is a one-tick delay and the loop coupler -> board -> image-to-vector -> splitter -> coupler is 4 ticks.

A unit is one copy of the five nodes. Units may be joined by extra signal edges, port to port,
exactly as the host allows. `Params` holds everything a secret mutation may change; the defaults are
the archived machine (tests/test_core.py checks beat ticks against the GeometricNeuronV28 fixture).
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

O0 = 0.8739509815096245          # coupler output_value saved in ecg.json


@dataclass(frozen=True)
class Params:
    # coupler, as saved in ecg.json
    setpoint: float = 0.5
    gain: float = 1.0
    sharpness: float = 3.0
    dead_zone: float = 0.1
    mode: str = "edge_of_chaos"
    integral_gain: float = 0.01
    integral_state: float = 1.1636187981416324
    integral_limit: float = 0.5
    target_variance: float = 0.1
    variance_window: int = 50
    image_gain_state: float = 1.0
    # board, image-to-vector, splitter
    size: int = 256
    output_dim: int = 256
    num_outputs: int = 16
    scale: float = 1.0
    # constants that are literals in the archived code
    sp_scale: float = 0.1        # setpoint += setpoint_mod * 0.1
    amp: float = 10.0            # amplified = setpoint + error * (1 + |var_error| * 10)
    q_base: float = 5.0          # square_size = int(5 + size_in * 50)
    q_gain: float = 50.0
    # structure a mutation may change
    extra_latches: int = 0       # hidden one-tick pass-through stages between board and vector
    gain_mod_live: bool = False  # archived code computes effective_gain and never uses it


SRC_PORTS = ["const.signal", "coupler.signal_out", "coupler.error", "coupler.regime"] + \
            [f"splitter.out_{i}" for i in range(16)]
DST_PORTS = ["coupler.signal_in", "coupler.setpoint_mod", "coupler.gain_mod",
             "board.square_size", "splitter.scale_mod"]

_VEC = {}


def vec(q, size, dim, n_out):
    """First n_out entries of the image-to-vector output for a board with square size q.
    INTER_AREA at an integer factor is a block mean; the archive works in float32."""
    key = (q, size, dim, n_out)
    v = _VEC.get(key)
    if v is None:
        y, x = np.mgrid[0:size, 0:size]
        with np.errstate(divide="ignore"):
            pat = (((x // q) + (y // q)) % 2).astype(np.float32)
        side = int(np.ceil(np.sqrt(dim)))
        b = size // side
        assert b * side == size, "size must be a multiple of the vector grid side"
        tiny = pat.reshape(side, b, side, b).mean(axis=(1, 3), dtype=np.float32)
        flat = tiny.flatten()[:dim]
        mx = np.max(np.abs(flat))
        if mx > 0:
            flat = flat / mx
        v = np.zeros(n_out)
        k = min(len(flat), n_out)
        v[:k] = flat[:k].astype(np.float64)
        _VEC[key] = v
    return v


class Unit:
    def __init__(self, const, p: Params):
        self.p, self.const = p, float(const)
        self.hist = []                       # deque(maxlen=200) in the archive
        self.integral = p.integral_state
        self.out = O0 * 1.0                  # coupler.signal_out
        self.err = 0.0
        self.regime = 0.0
        self.board = None                    # square size of the latched board image (None: blank)
        self.latch = [None] * p.extra_latches
        self.vecq = None                     # square size behind the latched vector
        self.outs = np.zeros(p.num_outputs)  # splitter outputs

    def read(self, port):
        node, name = port.split(".")
        if node == "const":
            return self.const
        if node == "coupler":
            return {"signal_out": self.out, "error": self.err, "regime": self.regime}[name]
        i = int(name[4:])
        return float(self.outs[i]) if i < len(self.outs) else 0.0

    def step(self, inp):
        """inp: dict port -> list of incoming values (already weighted). All nodes step at once."""
        p = self.p
        # ---- splitter (reads the vector latched last tick)
        mod = inp.get("splitter.scale_mod")
        sc = p.scale * (1.0 + sum(mod)) if mod else p.scale
        new_outs = (vec(self.vecq, p.size, p.output_dim, p.num_outputs) * sc
                    if self.vecq is not None else np.zeros(p.num_outputs))
        # ---- image-to-vector (reads the board image latched last tick, through any hidden stages)
        chain = [self.board] + self.latch
        new_vecq, new_latch = chain[-1], chain[:-1]
        # ---- board
        s = sum(inp.get("board.square_size", [])) or 0.1
        new_board = int(p.q_base + s * p.q_gain)
        # ---- coupler
        sig = inp.get("coupler.signal_in")
        if sig:
            value = float(sum(sig))
            sp = p.setpoint + p.sp_scale * sum(inp.get("coupler.setpoint_mod", []))
            gm = inp.get("coupler.gain_mod")
            eff_gain = p.gain * (1.0 + sum(gm) * 0.5) if (gm and p.gain_mod_live) else p.gain
            self.hist.append(value)
            if len(self.hist) > 200:
                self.hist.pop(0)
            if p.mode == "edge_of_chaos":
                var = float(np.var(self.hist[-p.variance_window:])) if len(self.hist) > 10 else 0.0
                ve = var - p.target_variance
                e = value - sp
                if ve > 0:
                    o = sp + (2.0 / (1.0 + np.exp(-e * p.sharpness)) - 1.0) / p.sharpness
                    self.regime = -1.0
                else:
                    amplified = sp + e * (1.0 + abs(ve) * p.amp)
                    o = sp + np.tanh((amplified - sp) * 2.0)
                    self.regime = 1.0
                self.err = ve
                if len(self.hist) > 20:
                    self.integral = self.integral * 0.99 + float(np.mean(self.hist[-50:])) * 0.01
            elif p.mode == "regulate":
                e = value - sp
                if abs(e) < p.dead_zone:
                    self.regime, o = 0.0, value
                else:
                    c = 2.0 / (1.0 + np.exp(-e * p.sharpness)) - 1.0
                    self.integral = float(np.clip(self.integral + e * p.integral_gain,
                                                  -p.integral_limit, p.integral_limit))
                    o = sp + c / p.sharpness - self.integral
                    self.regime = -float(np.sign(e))
                self.err = e
            else:
                o = np.tanh(value * p.sharpness) / p.sharpness
                self.err = self.regime = 0.0
            self.out = float(o * eff_gain)
        self.outs, self.vecq, self.latch, self.board = new_outs, new_vecq, new_latch, new_board


INTERNAL = [("const.signal", "coupler.setpoint_mod")] + \
           [(f"splitter.out_{i}", "coupler.signal_in") for i in range(4)] + \
           [("coupler.signal_out", "board.square_size")]


def simulate(consts, edges=(), inject=None, record=(), ticks=1000, settle=0, params=None):
    """consts: one constant per unit.  edges: (src unit, src port, dst unit, dst port, weight).
    inject: {(unit, dst port): sequence over ticks} added to that port.  record: (unit, src port).
    settle: ticks run first with the extra edges and injections silent (not recorded).
    params: one Params for all units, or a list."""
    n = len(consts)
    ps = params if isinstance(params, (list, tuple)) else [params or Params()] * n
    units = [Unit(c, p) for c, p in zip(consts, ps)]
    inject = {k: np.asarray(v, float) for k, v in (inject or {}).items()}
    rec = {r: np.zeros(ticks) for r in record}
    for t in range(-settle, ticks):
        ins = [dict() for _ in range(n)]
        for u, unit in enumerate(units):
            for s, d in INTERNAL:
                ins[u].setdefault(d, []).append(unit.read(s))
        if t >= 0:
            for ju, jp, iu, ip, w in edges:
                ins[iu].setdefault(ip, []).append(units[ju].read(jp) * w)
            for (u, port), seq in inject.items():
                if t < len(seq) and seq[t] != 0.0:
                    ins[u].setdefault(port, []).append(float(seq[t]))
        for u, unit in enumerate(units):
            unit.step(ins[u])
        if t >= 0:
            for (u, port), arr in rec.items():
                arr[t] = units[u].read(port)
    return rec


def beats(signal, thr=3.0):
    """Beat onsets: ticks where the signal (out_0 + out_1 + out_2 + out_3) rises above thr."""
    loud = np.asarray(signal) > thr
    return np.flatnonzero(loud[1:] & ~loud[:-1]) + 1
