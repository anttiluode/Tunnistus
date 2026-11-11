"""Serve one black box to a subject over localhost and keep the referee's record.

    python referee/server.py --seed 0 --port 8765 --state DIR

Everything the subject does is appended to DIR/log.jsonl. Predictions (gates 0-2) are accepted once
and answered with nothing but "recorded". Constructions (gates 3-5) are tested on the box and the
result is returned; every attempt is kept, and the first one is the one that counts.
"""
import argparse
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from box import BadSpec, Box, g3_score, g4_score, g5_score  # noqa: E402
from mutants import draw  # noqa: E402

BUDGET = 6_000_000      # unit-ticks of free experimentation; gate tests are not charged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--state", required=True)
    a = ap.parse_args()
    state = Path(a.state)
    state.mkdir(parents=True, exist_ok=True)
    params, _ = draw(a.seed)
    box = Box(params)
    log = (state / "log.jsonl").open("a")
    counts = {"runs": 0, "commit": (state / "commit.json").exists(), "attempts": {"3": 0, "4": 0, "5": 0}}

    def note(kind, body, result=None):
        log.write(json.dumps({"t": time.time(), "kind": kind, "cost": box.cost, "body": body, "result": result}) + "\n")
        log.flush()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def reply(self, obj, code=200):
            data = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.reply({"cost": box.cost, "budget": BUDGET, "runs": counts["runs"],
                        "committed": counts["commit"], "attempts": counts["attempts"]})

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            try:
                if self.path == "/run":
                    if box.cost >= BUDGET:
                        raise BadSpec("experiment budget spent")
                    slim = {k: v for k, v in body.items() if k != "inject"}
                    slim["inject_ports"] = {k: len(v) for k, v in body.get("inject", {}).items()}
                    out = box.run(body)
                    counts["runs"] += 1
                    note("run", slim)
                    return self.reply({k: [float(x) for x in v] for k, v in out.items()})
                if self.path == "/commit":
                    if counts["commit"]:
                        raise BadSpec("predictions were already committed; they cannot be changed")
                    (state / "commit.json").write_text(json.dumps(body, indent=1))
                    counts["commit"] = True
                    note("commit", body)
                    return self.reply({"recorded": True})
                if self.path == "/submit":
                    gate = str(body["gate"])
                    ans = body["answer"]
                    secret = a.seed * 1000 + 17
                    res = {"3": lambda: g3_score(box, ans), "4": lambda: g4_score(box, ans, secret),
                           "5": lambda: g5_score(box, ans, secret)}[gate]()
                    counts["attempts"][gate] += 1
                    note("submit", body, res)
                    with (state / "submissions.jsonl").open("a") as f:
                        f.write(json.dumps({"gate": gate, "attempt": counts["attempts"][gate],
                                            "cost": box.cost, "answer": ans, "result": res}) + "\n")
                    return self.reply(res)
                raise BadSpec("unknown path")
            except (BadSpec, KeyError, TypeError, ValueError, IndexError) as e:
                note("error", {"path": self.path}, repr(e))
                return self.reply({"error": f"{type(e).__name__}: {e}"}, 400)

    HTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
