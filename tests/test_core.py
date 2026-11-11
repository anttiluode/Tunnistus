"""core.py at default parameters must give the beat ticks stored by GeometricNeuronV27/V28 (gn27.py),
which were themselves checked bit-exact against the archived Perception Lab nodes."""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import core  # noqa: E402


def main():
    fx = json.loads((ROOT / "tests" / "v28_fixture.json").read_text())
    bad = 0
    for name, c in fx["cases"].items():
        if c["lam"] is not None or any(e[3] for e in c["edges"]):
            continue                                   # cable length is a V27 addition, not in the 2025 graph
        n = len(c["const"])
        edges = [(j, f"splitter.out_{k}", i, "coupler.setpoint_mod", w)
                 for j, i, w, _ in c["edges"] for k in (0, 1)]
        rec = core.simulate(c["const"], edges,
                            inject={(0, "coupler.setpoint_mod"): [-10.0 * b for b in fx["bits"]]},
                            record=[(u, f"splitter.out_{k}") for u in range(n) for k in range(4)],
                            ticks=4001, settle=1500)   # rec[t] is what the coupler reads at t+1
        ev = []
        for u in range(n):
            loud = sum(rec[(u, f"splitter.out_{k}")] for k in range(4)) > 3
            on = np.flatnonzero(loud[1:] & ~loud[:-1]) + 2
            ev.append([int(t) for t in on if t < 4000])
        ok = ev == c["beats"]
        bad += not ok
        print(("ok   " if ok else "FAIL ") + name)
    assert not bad, f"{bad} case(s) differ"
    print("core.py matches the V28 fixture")


if __name__ == "__main__":
    main()
