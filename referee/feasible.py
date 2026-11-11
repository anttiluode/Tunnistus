"""Is a secret mutant solvable? Runs the sweep baseline on it and prints only pass/fail and cost,
never the mutant's parameters. Usage: python referee/feasible.py SEED [SEED ...]"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import baseline  # noqa: E402
from box import Box, g3_score, g4_score, g5_score  # noqa: E402
from mutants import draw  # noqa: E402


def attempt(seed):
    p, _ = draw(seed)
    b = Box(p)
    t = time.time()
    out = {"seed": seed, "g3": False, "g4": False, "g5_level": 0}
    g3, _, _ = baseline.solve_g3(b.run)
    if g3:
        s3 = g3_score(b, g3)
        out.update(g3=s3["pass"], g3_change=s3["change"], cost_g3=b.cost)
        g4 = baseline.solve_g4(b.run, g3["silent"] + 0.15)
        if g4:
            s4 = g4_score(b, g4, 99)
            out.update(g4=s4["pass"], g4_bits=s4["bits"], cost_g4=b.cost)
            g5 = baseline.solve_g5(b.run, g4, g3["clock"] - 0.3)
            if g5:
                s5 = g5_score(b, g5, 99)
                out.update(g5_level=s5["level"])
    out.update(cost=b.cost, seconds=round(time.time() - t))
    return out


if __name__ == "__main__":
    for s in sys.argv[1:]:
        print(json.dumps(attempt(int(s))), flush=True)
