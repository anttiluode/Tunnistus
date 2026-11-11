"""kit/rules.py (what a subject reads) and core.py (what the box runs) must be the same machine
at default parameters, bit for bit, including under injected pulses on every signal input."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "kit"))
import core  # noqa: E402
import rules  # noqa: E402

PORTS = {("V", "a"): "coupler.signal_in", ("V", "c"): "coupler.setpoint_mod", ("V", "d"): "coupler.gain_mod",
         ("X", "a"): "board.square_size", ("Z", "b"): "splitter.scale_mod"}
OUTS = {("V", "p"): "coupler.signal_out", ("V", "r"): "coupler.error", ("V", "s"): "coupler.regime",
        ("Z", "p0"): "splitter.out_0", ("Z", "p3"): "splitter.out_3", ("Z", "p9"): "splitter.out_9"}


def main():
    T = 700
    rng = np.random.default_rng(1)
    inj = {k: np.where(rng.random(T) < 0.02, rng.normal(0, 2, T), 0.0) for k in PORTS}
    g = rules.Graph(json.loads((ROOT / "kit" / "graph.json").read_text()))
    a = np.zeros((T, len(OUTS)))
    for t in range(T):
        g.step({k: v[t] for k, v in inj.items() if v[t] != 0.0})
        a[t] = [g.nodes[n].out(p) for n, p in OUTS]
    rec = core.simulate([1.0], inject={(0, PORTS[k]): v for k, v in inj.items()},
                        record=[(0, p) for p in OUTS.values()], ticks=T)
    b = np.stack([rec[(0, p)] for p in OUTS.values()], axis=1)
    assert np.array_equal(a, b), f"max difference {np.abs(a - b).max()}"
    print("kit/rules.py matches core.py on", T, "ticks with random pulses on all five signal inputs")


if __name__ == "__main__":
    main()
