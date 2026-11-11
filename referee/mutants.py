"""Secret mutations of the machine. A seed picks which documented facts are false for a box.
seed 0 is the archived machine, unchanged."""
from dataclasses import replace

import numpy as np

from core import Params

# option -> (Params field, values, the id a subject must name, how to report its value)
OPTIONS = {
    "window":   ("variance_window", [32, 40, 64, 72], "V.k10"),
    "stages":   ("extra_latches", [1, 2], "stages"),
    "target":   ("target_variance", [0.07, 0.14], "V.k9"),
    "c_scale":  ("sp_scale", [0.08, 0.12], "V.lit_0.1"),
    "sharp":    ("sharpness", [2.5, 4.0], "V.k3"),
    "amp":      ("amp", [4.0, 20.0], "V.lit_10"),
    "q_gain":   ("q_gain", [45.0, 55.0], "X.lit_50"),
    "d_live":   ("gain_mod_live", [True], "V.d_used"),
}
TIMING = ["window", "stages"]
OTHER = ["target", "c_scale", "sharp", "amp", "q_gain"]


def draw(seed):
    """Returns (Params, truth) where truth maps the subject-facing id to the box's real value."""
    if seed == 0:
        return Params(), {}
    rng = np.random.default_rng(seed)
    names = list(rng.choice(TIMING, size=int(rng.integers(1, 3)), replace=False)) + \
        list(rng.choice(OTHER, size=int(rng.integers(1, 3)), replace=False))
    if rng.random() < 0.5:
        names.append("d_live")          # a documented-dead port that is alive in the box
    p, truth = Params(), {}
    for n in names:
        field, values, ident = OPTIONS[n]
        v = values[int(rng.integers(len(values)))]
        p = replace(p, **{field: v})
        truth[ident] = (4 + v) if n == "stages" else v
    return p, truth
