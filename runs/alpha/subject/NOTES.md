# NOTES (chronological)

## 1. Reading the documents
- Unit = loop V(K1, mode k5=1 -> m1) -> X(K2) -> Y(K3) -> Z(K4) -> V.a (sum of Z.p0..p3). U feeds V.c.
- All nodes step from the previous tick's outputs, so the loop is 4 ticks (V.p(t) -> Z(t+3) -> V.p(t+4)).
- X turns V.p into a checkerboard of cell size n = int(5 + 50*p); Y block-averages to 16x16 and normalises by
  the max; Z keeps the first 16 (top row of blocks). So the loop is a static map n -> Zsum (table in t6.py output):
  Zsum > 3 only for |n| <= 11 (n != 0), falls to 0 for n >= 64, n = 0 gives 0.
- V (m1): c1 = k1 + 0.1*c (=0.6 at U=1); z = variance of last k10=50 inputs; u = z - k9.
  u > 0 ("tight"): p = c1 + tanh(1.5 e)/3.  u <= 0 ("loose"): p = c1 + tanh(2 e (1 + 10|u|)), e = a - c1.
- In the documents V.d only changes a local g1 that is never used; k4,k6,k8 only in m0; k7 written but never read
  in m1; k11 only in the q output. So documented-dead: V.d, k4, k6, k7, k8, k11.
- Wrote sim.py (fast equivalent, pattern cached per n). Verified equal to rules.py for 300 ticks (diff 0.0).

## 2. Box vs documents
- H: box == documents. Test t1.py: default unit, 9000 ticks, all 20 recordable ports: max diff 0.0. Period 59.
- t2.py: U in {-3..8} (12 values) and injections into each of the 5 input ports at 5 amplitudes: all diff 0.0.
  => V.d is dead in the box too (injection up to -10 for 40 ticks changes nothing). k1 / lit_0.1 split confirmed
  by U sweep. X.a injection separates k2 from X.lit_50. Z.b live, X.a live, V.a live, V.c live.
- t3.py random 2-5 unit networks with random edges/injections/settle: 10 of 12 exact, 2 differ ONLY in the first
  tick. t4/t5: the box emits V.r = 0 and V.s = 0 before the first step, where graph.json saves v2=0.2965, v3=-1.0
  (V.p's saved v1 = 0.874 IS loaded). Only visible through an extra edge from V.r / V.s at tick 0 with settle=0.
  After setting v2=v3=0 in sim.py everything agrees.
- Wrong early expectation: I expected to find a planted parameter difference (the brief hints at one); none found
  in any parameter that is observable. k4,k6,k7,k8,k11 cannot be observed through the box at all (dead).

## 3. Mechanism (t6.py)
- Relaxation oscillator. After a beat the big Z values sit in V's 50-tick variance window -> u>0 -> tight mode,
  low gain, loop settles in a small 8-tick cycle (n 43<->48, Zsum 1.3125<->1.0, variance 0.024 < k9).
- When the beat leaves the window (52 ticks later) u<0 -> loose mode, high gain: V.p jumps to 1.58 (n=84, Z=0),
  4 ticks later V sees 0 -> p=-0.34 -> n=-11 -> Zsum 3.47 > 3: beat. 52 + 7 = 59.
- Period ~ k10 + 9 (k10=80 gives 91, extra latencies differ a little).

## 4. Gate 2 (g2.py) model predictions: a 91, b 33, c 61, d silent, e silent, f 60, g 95, h 64.
- d is "silent" because excursions peak at Zsum 2.53 (n=-14), below 3; k9=0.31 would beat (61). Knife-edge but
  the model is bit-exact against the box, so I keep it.

## 5. Gate 3 (g3*.py)
- U scan: clock for U in about [-0.23,1.4295], [-1.386,-1.05..], etc.; silent elsewhere. Boundaries are sharp to
  1e-13 (int() threshold) e.g. 1.42952360041166.
- Wrong idea: use the two sides of a boundary 2e-9 apart. Silent side is NOT a fixed point there (non-beat
  excursions), and the -10 push gives 0 or 2 beats at some phases (8 of 140 push times at U=1.43; box confirmed a
  double beat at -0.2307). Negative-U silent windows are never phase-robust.
- Robustly excitable (140/140 push times, one beat 3 ticks after push) from U >= ~1.47.
