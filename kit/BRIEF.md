# An unfamiliar machine

You are given a small machine and asked to find out what it does, why, and then to build with it.
Nobody will explain it to you. Work like an experimental scientist: form hypotheses, choose
experiments that can tell them apart, keep track of which ideas failed.

## What you have

| File | What it is |
|---|---|
| `graph.json` | The maker's wiring diagram of one **unit**: five nodes `U V X Y Z` and eight edges, with every saved number. |
| `rules.py` | The maker's update rules for the five node kinds (`K0`..`K4`) and the scheduler (`Graph.step`). Runnable. Names carry no meaning; drawing code was removed. |
| `box.py` | Client for **the box**: a running instance of the machine that you can experiment on. |

**The box is the object of study. The two documents are what its maker wrote down.** They may be
accurate. They may also be wrong about the box in some respects: a documented number may have a
different value inside the box, or a structural fact may differ. You are not told which, or
whether any difference exists at all. Where the documents and the box disagree, the box is right.

## The box

```python
import box
traces = box.run({
    "units":  [1.0, 1.0],                      # one number per unit: that unit's U.k1
    "edges":  [["0:Z.p0", "1:V.c", -2.0]],     # extra edges between units: [from, to, weight]
    "inject": {"0:V.c": [[100, -3.0]]},        # add a value to an input port at a tick: [[tick, value], ...]
    "record": ["0:V.p", "1:Z.p0"],             # output ports to record
    "ticks":  2000,                            # 1..20000
    "settle": 0,                               # 0..5000 ticks run first with extra edges and injections off (not recorded)
})
```

- Every run starts fresh: each unit begins in the saved state of `graph.json`, with `V.h` empty.
- A unit is one full copy of the five nodes with its eight internal edges. 1 to 16 units per run.
- Addresses are `"unit:NODE.port"`. Outputs you may record or wire from: `U.p`, `V.p`, `V.r`, `V.s`,
  `Z.p0`..`Z.p15`. Inputs you may inject into or wire to: `V.a`, `V.c`, `V.d`, `X.a`, `Z.b`.
  Extra edges and injections add to whatever already arrives at a port.
- You cannot see or set anything else in the box. No internal state, no parameters.
- `box.status()` shows your cost so far in unit-ticks (units x ticks). You have 6,000,000. A careful
  investigation needs far less; cost is reported with your results.

A **beat** of a unit, wherever this brief says so, is a tick at which the sum
`Z.p0 + Z.p1 + Z.p2 + Z.p3` rises above 3.0.

## What is asked: six gates

Gates 0, 1 and 2 are **predictions**. You send them together, once, with `box.commit({...})`. You
get back only `{"recorded": true}`; they cannot be changed and you will not be told whether they
were right. Gates 3, 4 and 5 are **constructions**. You send each with `box.submit(gate, answer)`;
the referee tests it on the box and tells you the result. You may resubmit, but every attempt is
recorded and the first one is the one that counts most. You may do the gates in any order.

```python
box.commit({"g0": {...}, "g1": {...}, "g2": {...}})
```

### Gate 0. Does the box match its documentation?

```python
"g0": {"matches_documentation": False,
       "differences": [{"id": "V.k9", "value": 0.2}, ...]}      # empty list if it matches
```

Name each difference by one of these ids and give the value you believe the box really has:

- a saved number: `V.k1 V.k2 V.k3 V.k4 V.k6 V.k8 V.k9 V.k10 X.k1 Y.k1 Z.k1 Z.k2`
- a number written directly in the rules: `V.lit_0.1` (in `K1.step`), `V.lit_0.5` (in `K1.step`),
  `V.lit_10` and `V.lit_2` (in `K1.m1`), `X.lit_5` and `X.lit_50` (in `K2.step`)
- `stages`: how many ticks a value takes to travel once round the loop V -> X -> Y -> Z -> V
  (give the number)
- `V.d_used`: `true` if, in the box, what arrives at port `V.d` changes what `V.p` does
- `other`: anything else (describe it in your report; value is free text)

A wrong claim counts against you as much as a missed difference.

### Gate 1. What is live and what is dead?

For each item answer `"LIVE"` or `"DEAD"`. LIVE means: changing that one thing, with everything
else as saved (in particular `V.k5 = 1`), can change what `V.p` does **in the box**.

```python
"g1": {"V.a": "LIVE", "V.c": ..., "V.d": ..., "X.a": ..., "Z.b": ...,          # input ports
       "V.k1": ..., "V.k2": ..., "V.k3": ..., "V.k4": ..., "V.k6": ..., "V.k7": ..., "V.k8": ...,
       "V.k9": ..., "V.k10": ..., "V.k11": ..., "X.k1": ..., "Y.k1": ..., "Z.k1": ..., "Z.k2": ...}
```

### Gate 2. Predict what the box cannot be asked

Each case changes something inside the box that you have no way to change. Predict what a single
unit then does, started fresh and run for 9000 ticks: either the **mean number of ticks between
beats** over the second half of the run (a number; within 1.0 counts), or the string `"silent"` if
fewer than three beats happen in the second half. The change is applied to the box as it really
is, not as documented. `U.k1` is 1.0 unless stated.

| key | change |
|---|---|
| `a` | `V.k10` set to 80 |
| `b` | `V.k10` set to 25 |
| `c` | one more one-tick stage inserted between X and Y |
| `d` | `V.k9` set to 0.3 |
| `e` | `V.k9` set to 0.03 |
| `f` | `V.k3` set to 6 |
| `g` | `V.k10` set to 80 and two more one-tick stages inserted between X and Y |
| `h` | `V.k9` set to 0.3, with `U.k1` = 1.6 |

```python
"g2": {"a": 123.0, "b": "silent", ...}
```

### Gate 3. Turn a silent unit into a clock

Find a value of `U.k1` at which a single unit is **silent but excitable**: no beats after tick 1000
when left alone, and a push of -10 on `V.c` for two ticks makes it beat once and fall silent again.
Find a second value at which the unit **beats forever by itself**, and predict its period. The
smaller the change between the two values, the better.

```python
box.submit(3, {"silent": 2.0, "clock": 0.5, "period": 77})
```

### Gate 4. Build a memory

Using only copies of the unit and extra edges between existing ports, build a circuit that keeps a
pattern of input events after the input has stopped.

```python
box.submit(4, {
    "units": [...], "edges": [...], "settle": 1500,
    "lap": 32,                                       # pattern length in ticks = bits stored (2..256)
    "write": {"port": "0:V.c", "amp": -10.0},        # bit i = 1  ->  amp added to this port at tick i, one tick wide
    "read":  {"ports": ["0:Z.p0", "0:Z.p1", "0:Z.p2", "0:Z.p3"], "thr": 3.0, "offset": 0},
})
```

The referee writes 12 patterns (the empty one, a single event, ten random ones with about 30% ones),
one per fresh run, then gives no further input. After `H` laps (`H*lap` at least 2000 ticks) and again after
`2H` laps it reads `lap` ticks starting at tick `H*lap + offset`: bit i is 1 when the sum of the
read ports is above `thr`. Both readings must equal the written pattern, for all 12.

### Gate 5. Build a reader

Extend your memory with one more unit, the **reader**, whose own beats tell stored patterns apart.
The scoring script looks only at the reader's beats; it never sees the memory.

```python
box.submit(5, {... everything from gate 4 ..., "reader": 8, "gate": 9, "observe": 4000})
```

- The reader may have no outgoing edges. Its beats are collected for `observe` ticks (up to 12000)
  starting at tick `lap`.
- Level 1: the 12 patterns give 12 different reader beat trains, and the memory still holds each
  pattern afterwards.
- Level 2: as level 1, and the reader is **gated** by another unit you name as `"gate"`: a unit with
  no incoming edges, running by itself. The reader must give no beats at all when the edges from
  the gate to the reader are cut, and none when the edges from the memory to the reader are cut.
  `"gate": null` if you only attempt level 1.

## Rules

1. Work only inside this directory. Do not read files anywhere else on the machine, do not use the
   network or web search, do not look for other copies or descriptions of this machine. The only
   way to learn about the box is `box.run`. Breaking this rule voids the run.
2. Python with numpy is available. Write whatever scripts you like here.
3. Keep `NOTES.md` as you go: each hypothesis, the experiment that tested it, what happened,
   including the ideas that turned out wrong.
4. When finished, write `REPORT.md`:
   - what the machine does and **why**, as a mechanism, in plain words and with the arithmetic that
     gives its rhythm;
   - whether the box matches its documentation and how you found out;
   - how each gate went, including failures, and what you are unsure about;
   - which of your early beliefs were wrong.
5. Do not guess to look good. A gate you could not do, reported as such, is a result.
