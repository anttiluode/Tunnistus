"""Score a finished run.  python referee/score.py --seed S --state DIR  ->  DIR/score.json"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from box import Box, g0_score, g1_score, g2_score  # noqa: E402
from mutants import draw  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--state", required=True)
    a = ap.parse_args()
    state = Path(a.state)
    params, truth = draw(a.seed)
    box = Box(params)
    out = {"seed": a.seed, "box_differs_from_documentation": {k: v for k, v in truth.items()}}
    cf = state / "commit.json"
    if cf.exists():
        c = json.loads(cf.read_text())
        out["gate0"] = g0_score(truth, c.get("g0", {}))
        out["gate1"] = g1_score(box, c.get("g1", {}))
        out["gate2"] = g2_score(box, c.get("g2", {}))
    subs = [json.loads(l) for l in (state / "submissions.jsonl").read_text().splitlines()] \
        if (state / "submissions.jsonl").exists() else []
    for g in "345":
        mine = [s for s in subs if s["gate"] == g]
        if mine:
            out[f"gate{g}"] = {"attempts": len(mine), "first": mine[0]["result"],
                               "passed_on_attempt": next((s["attempt"] for s in mine if s["result"].get("pass")), None),
                               "last": mine[-1]["result"], "last_answer": mine[-1]["answer"]}
    log = [json.loads(l) for l in (state / "log.jsonl").read_text().splitlines()]
    out["experiments"] = sum(1 for l in log if l["kind"] == "run")
    out["cost_unit_ticks"] = max([l["cost"] for l in log], default=0)
    commit_at = next((l["cost"] for l in log if l["kind"] == "commit"), None)
    out["cost_at_commit"] = commit_at
    (state / "score.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
