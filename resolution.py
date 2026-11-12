"""Does the original loop depend on its pixel grid?

Refine the board and the squares together: board N = 256*s, square size q = int((5 + 50*o)*s),
read through the same 16x16 block grid. s = 1 is the archived machine. With s > 1 the square-size
staircase has s times finer steps while the geometry the unit reads stays the same.
Prints the beat period of one unit at four constants (None = silent)."""
import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "referee"))
import core  # noqa: E402
from box import Box  # noqa: E402

for s in (0.5, 1, 2, 4):
    p = replace(core.Params(), size=int(256 * s), q_base=5 * s, q_gain=50 * s)
    print(f"s={s:<4}", {c: Box(p).period(c) for c in (0.5, 1.0, 1.3, 1.6)})
