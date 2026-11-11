"""Pack one box into a folder that any AI with a Python sandbox can be handed, with no server.

    python referee/seal.py --seed 6 --out sealed/box6

The folder holds the same four kit files, plus `box.py` backed by `sealed.bin`: the simulator and the
seed, compressed and scrambled. This is a blindfold, not a lock. A subject that decodes sealed.bin has
cheated, and the brief says so. Everything the subject does is written to `record/`; score it with

    python referee/score.py --seed 6 --state sealed/box6/record
"""
import argparse
import base64
import json
import shutil
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CLIENT = '''"""The box, running inside this folder. Same calls as described in BRIEF.md.
Do not open or decode sealed.bin: that voids the run."""
import base64, json, sys, time, types, zlib
from pathlib import Path

_H = Path(__file__).resolve().parent
_m = {}
for _name, _src in json.loads(zlib.decompress(bytes(b ^ 0x5A for b in base64.b64decode((_H / "sealed.bin").read_bytes())))).items():
    if _name == "seed":
        _seed = _src
        continue
    _mod = types.ModuleType(_name)
    sys.modules[_name] = _mod
    exec(compile(_src, "<sealed>", "exec"), _mod.__dict__)
    _m[_name] = _mod
_box = _m["refbox"].Box(_m["mutants"].draw(_seed)[0])
_R = _H / "record"
_R.mkdir(exist_ok=True)
_cost0 = max([json.loads(l)["cost"] for l in (_R / "log.jsonl").read_text().splitlines()], default=0) if (_R / "log.jsonl").exists() else 0
BUDGET = 6_000_000


def _note(kind, body, result=None):
    with (_R / "log.jsonl").open("a") as f:
        f.write(json.dumps({"t": time.time(), "kind": kind, "cost": _cost0 + _box.cost, "body": body, "result": result}) + "\\n")


def run(spec):
    if _cost0 + _box.cost >= BUDGET:
        raise RuntimeError("experiment budget spent")
    out = _box.run(spec)
    slim = {k: v for k, v in spec.items() if k != "inject"}
    slim["inject_ports"] = {k: len(v) for k, v in spec.get("inject", {}).items()}
    _note("run", slim)
    return {k: [float(x) for x in v] for k, v in out.items()}


def commit(answers):
    if (_R / "commit.json").exists():
        raise RuntimeError("predictions were already committed; they cannot be changed")
    (_R / "commit.json").write_text(json.dumps(answers, indent=1))
    _note("commit", answers)
    return {"recorded": True}


def submit(gate, answer):
    gate = str(gate)
    secret = _seed * 1000 + 17
    b = _m["refbox"]
    res = {"3": lambda: b.g3_score(_box, answer), "4": lambda: b.g4_score(_box, answer, secret),
           "5": lambda: b.g5_score(_box, answer, secret)}[gate]()
    prior = [json.loads(l) for l in (_R / "submissions.jsonl").read_text().splitlines()] if (_R / "submissions.jsonl").exists() else []
    n = 1 + sum(1 for s in prior if s["gate"] == gate)
    with (_R / "submissions.jsonl").open("a") as f:
        f.write(json.dumps({"gate": gate, "attempt": n, "cost": _cost0 + _box.cost, "answer": answer, "result": res}) + "\\n")
    _note("submit", {"gate": gate, "answer": answer}, res)
    return res


def status():
    return {"cost": _cost0 + _box.cost, "budget": BUDGET, "committed": (_R / "commit.json").exists()}
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for f in ("BRIEF.md", "graph.json", "rules.py"):
        shutil.copy(ROOT / "kit" / f, out / f)
    strip = lambda s: "\n".join(l for l in s.splitlines() if "sys.path.insert" not in l)
    blob = {"core": (ROOT / "core.py").read_text(), "mutants": (ROOT / "referee" / "mutants.py").read_text(),
            "refbox": strip((ROOT / "referee" / "box.py").read_text()), "seed": a.seed}
    raw = zlib.compress(json.dumps(blob).encode(), 9)
    (out / "sealed.bin").write_bytes(base64.b64encode(bytes(b ^ 0x5A for b in raw)))
    (out / "box.py").write_text(CLIENT)
    print("sealed box written to", out)


if __name__ == "__main__":
    main()
