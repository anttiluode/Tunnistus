"""Client for the box. The address is read from the file box_url.txt next to this file."""
import json
import urllib.error
import urllib.request
from pathlib import Path

URL = (Path(__file__).resolve().parent / "box_url.txt").read_text().strip()


def _post(path, obj):
    req = urllib.request.Request(URL + path, json.dumps(obj).encode(), {"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(json.loads(e.read())["error"]) from None


def run(spec):
    """One experiment. Returns {recorded address: list of floats, one per tick}."""
    return _post("/run", spec)


def commit(answers):
    """Gates 0, 1 and 2, together, once. Returns {"recorded": true} and nothing else."""
    return _post("/commit", answers)


def submit(gate, answer):
    """Gates 3, 4 and 5. The construction is tested on the box and the result returned."""
    return _post("/submit", {"gate": gate, "answer": answer})


def status():
    with urllib.request.urlopen(URL + "/", timeout=60) as r:
        return json.loads(r.read())
