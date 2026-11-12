# Tunnistus

**Can an AI work out what an unfamiliar machine does, notice where its documentation is wrong, and then build with it?**

A test bench for that question, built on the original Perception Lab loop (`ecg.json`, the
Geometric Neuron's ancestor), and one interrupted run of it. The idea is ChatGPT's
("the Blind Machine Archaeologist"). The bench and the write-up are by Claude (Fable 5.2).

## Status: stopped early, on purpose

Two blind runs were started. Both were cut off when the usage limit ran out, and they were not
resumed. What exists is real but partial:

| | Box alpha: the original machine | Box beta: secretly altered |
|---|---|---|
| Gate 0: does the box match its documentation? | concluded "matches" (correct) but **never committed** | **4 of 4 hidden changes named, right values, no false alarms** |
| Gate 1: live or dead (19 items) | not committed | **19 / 19** |
| Gate 2: predict 8 changes it could not test | not committed (its notes list 8 predictions; all 8 equal the truth) | **8 / 8** |
| Gate 3: turn a silent relay into a clock | was working on it | **passed, first attempt** |
| Gate 4: build a memory | not reached | **passed, first attempt** (40 bits, held 4000 ticks) |
| Gate 5: build a reader | not reached | **not reached** (cut off while preparing it) |
| Experiments run / cost | 109 / 1,242,174 unit-ticks | 87 / 501,441 (76,955 before committing gates 0-2) |

Only committed answers count. Alpha therefore scores nothing, whatever its notes say.

## What the subject was given

A fresh Fable 5.2 instance with no access to this repository, the Geometric Neuron repositories or
any conversation about them. It got four files (`kit/`):

- `graph.json` and `rules.py`: the five nodes and their update rules, with every name replaced by a
  neutral letter and every comment removed;
- `box.py`: access to a **box**, a running instance it could only poke through ports;
- `BRIEF.md`: the six gates, and a warning that the documentation may or may not be true of the box.

Box alpha is the original machine. Box beta had four things changed in secret:

| What the paper says | What box beta really had |
|---|---|
| variance window 50 | **32** |
| loop of 4 ticks | **5** |
| amplification constant 10 | **20** |
| the gain port is computed and never used | **the gain port is live** |

The last one is the `setpoint_mod` lesson turned into a test: a port everyone would call dead that
is not.

## What happened on box beta

From the subject's own notes (`runs/beta/subject/NOTES.md`), in order:

1. It rebuilt the documented machine as a fast model and checked the box against it. Mismatch at
   once: the box beat every 42 ticks, the paper machine every 59.
2. It used an output port that exposes the variance error to fit each piece separately. Window 32
   was "the only value from 20 to 80 that fits". It first suspected two other constants, and ruled
   both out with later ticks.
3. It injected into every input port. The gain port multiplied the output by exactly `1 + 0.5 d`,
   so it reported the port as live.
4. It checked the corrected model against 8 random multi-unit networks: every output exact.
5. It wrote the rhythm as arithmetic: **32 + 2 x 5 = 42** (for the paper machine, 50 + 2 x 4 + 1 = 59).
6. With that model it predicted eight changes to internals it had no way to try on the box. All
   eight were right, including three that go silent.
7. Relay, clock and a 40-bit ring memory each passed the referee on the first submission.

The comparison that matters: a plain sweep with no model (`baseline.py`) spent 1,254,000 unit-ticks
on box beta, passed gate 3 and failed to find a memory. The subject spent 501,441 and passed gates
0 to 4. The sweep cannot attempt gates 0 and 2 at all.

On box alpha the subject also caught a fault in the bench: the box started two output ports at 0
where `graph.json` saved other values. It was visible only through an extra edge at tick 0. The kit
has been corrected since; the runs used the earlier kit.

## What this does and does not show

- One altered machine, one run, one model. Not a statistic.
- The subject had the documented rules. This tests "find where the paper is wrong and rebuild the
  model", not discovery from nothing.
- The hidden changes were parameter and wiring changes inside a known structure. A changed formula
  was not tried.
- The bench and the subject are the same model family. The mutation was drawn from a seed, but the
  family of mutations was written by Fable.
- Blindness was by instruction (stay in the folder, no network). The experiment log shows what the
  subject ran on the box; it cannot show what files it read.
- Gate 5 was never attempted. Nothing here says a blind subject can build the V28 reader.

## A side result: the rhythm does not depend on the pixel grid

A question raised after a Yang-Mills video: is the beat a property of this particular 256-pixel
grid? `resolution.py` refines the board and the squares together and reads through the same 16 x 16
blocks. Beat period of one unit (None = silent):

| scale | board | constant 0.5 | 1.0 | 1.3 | 1.6 |
|---|---|---|---|---|---|
| 0.5 | 128 | 60 | 59 | 59 | silent |
| 1 (original) | 256 | 60 | 59 | 58.5 | silent |
| 2 | 512 | 60 | 59 | 58 | silent |
| 4 | 1024 | 60 | 60 | 58 | silent |

The clock and the silent relay both survive an eightfold change in resolution, within one tick.
Only the period was measured; the excitation threshold and the ring memory were not rechecked.

## Running it

```
python tests/test_core.py      # the simulator against the stored V28 beat ticks
python tests/test_rules.py     # the renamed rules against the simulator, bit for bit
python tests/test_gates.py     # the gates accept the known V27/V28 circuits
python referee/seal.py --seed 16 --out sealed/box16     # a folder to hand to any AI with a Python sandbox
python referee/score.py --seed 16 --state sealed/box16/record
```

`seal.py` needs no server. Seed 0 is the original machine; other seeds draw other secret changes
(`referee/mutants.py`). The sealed folder is a blindfold, not a lock.

| Path | What |
|---|---|
| `core.py` | the loop, node by node, as a family of machines |
| `kit/` | what a subject receives |
| `referee/` | the box, the six gates, scoring, secret mutations |
| `baseline.py` | the no-model sweep |
| `runs/` | both subjects' notes and scripts, the experiment logs, the scores |
