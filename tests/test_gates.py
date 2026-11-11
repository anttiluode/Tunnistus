"""The gates must accept the circuits already known from GeometricNeuronV27/V28 on the archived
machine (seed 0): relay 1.6 / clock 1.0 at 59 ticks, the ring of eight at weight -6, and the V28
clock-gated reader (ring -> reader -2, clock -> reader -4). And reject obvious non-answers."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "referee"))
from box import Box, g0_score, g1_score, g2_score, g3_score, g4_score, g5_score  # noqa: E402
from mutants import draw  # noqa: E402

B = ["Z.p0", "Z.p1"]


def main():
    box = Box(draw(0)[0])
    assert g3_score(box, {"silent": 1.6, "clock": 1.0, "period": 59})["pass"]
    assert not g3_score(box, {"silent": 1.0, "clock": 1.6, "period": 59})["pass"]
    ring = {"units": [1.6] * 8, "settle": 1500, "lap": 32,
            "edges": [[f"{i}:{p}", f"{(i + 1) % 8}:V.c", -6.0] for i in range(8) for p in B],
            "write": {"port": "0:V.c", "amp": -10.0},
            "read": {"ports": ["0:Z.p0", "0:Z.p1", "0:Z.p2", "0:Z.p3"], "thr": 3.0, "offset": 3}}
    assert g4_score(box, ring, 1)["pass"]
    assert not g4_score(box, dict(ring, edges=ring["edges"][:-2]), 1)["pass"]      # ring cut open
    reader = dict(ring, units=[1.6] * 8 + [1.6, 1.0], reader=8, gate=9, observe=4000,
                  edges=ring["edges"] + [[f"0:{p}", "8:V.c", -2.0] for p in B] + [[f"9:{p}", "8:V.c", -4.0] for p in B])
    r = g5_score(box, reader, 1)
    print("V28 reader on the archived machine:", {k: v for k, v in r.items()})
    assert r["level"] == 2
    t = g1_score(box, {})["rows"]
    assert t["V.d"]["truth"] == "DEAD" and t["V.c"]["truth"] == "LIVE" and t["V.k7"]["truth"] == "DEAD"
    assert g0_score({}, {"matches_documentation": True, "differences": []})["verdict_right"]
    g2 = g2_score(box, {"a": 91, "b": 33, "c": 61, "d": "silent", "e": "silent", "f": 60, "g": 95, "h": 64})
    assert g2["right"] == 8, g2
    mut, truth = draw(6)
    assert g1_score(Box(mut), {})["rows"]["V.d"]["truth"] == "LIVE" and truth["V.d_used"] is True
    print("gates accept the V27/V28 circuits and the known answers on the archived machine")


if __name__ == "__main__":
    main()
