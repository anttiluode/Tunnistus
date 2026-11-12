# NOTES

## 1. Reading the documents
- Unit: U (constant k1) -> V.c ; V.p -> X.a ; X -> Y -> Z ; Z.p0..p3 summed -> V.a. Every node is one tick, so documented loop = 4 ticks.
- X draws a checkerboard with cell n = int(5 + 50*V.p); Y averages 16x16-pixel blocks and normalises by the max; Z passes the first 16 blocks.
  So Z.p0+..+p3 is a fixed, non-monotonic function z(n) (table printed by my scripts): ~4 for |n|<=10, 3.16 at n=-12, 2.53 at n=13/-14, falls to 0 at n>=64.
- V (k5=1, rule m1): target c1 = k1 + 0.1*c. u = var(last k10 inputs) - k9.
  u>0 (input has been varying): y = c1 + tanh(1.5 e)/3  (gain 0.5, gentle)
  u<=0 (input has been calm):  y = c1 + tanh(2 e (1+lit10*|u|)) (gain >= 2, violent)
- Documented dead things: V.d (g1 computed, never used), k4/k6/k8 (only in m0), k7 (written, never read for output), k11 (only q port).
- model.py: fast equivalent, verified against rules.py to 1e-16 over 400 ticks.

## 2. Box vs documents
- H: box == docs. Exp e1: default unit, 3000 ticks. FALSE: box beats every 42 ticks, documented model every 59. Differs from tick 0.
- e2 (fit each sub-function from the box traces, using V.r as the directly visible u):
  - low branch fits exactly only with lit_10 = 20 (lit_2=2). (First thought lit_2=3 or k9=0.2 from the tick-0 value alone; V.r = -0.1 ruled out k9, the later ticks ruled out lit_2=3.)
  - high branch exact with k3 = 3.
  - V.r reproduced exactly with variance window k10 = 32 (only value 20..80 that fits), k9 = 0.1.
  - Z(t) is function of V.p(t-4), not t-3 -> one extra tick in the loop: stages = 5. X/Y/Z map itself (5, 50, sizes) exact.
- e3/e4: U.k1 in {-1..3}: exact (so k1=0.5, lit_0.1=0.1). Injection into V.a, V.c, X.a, Z.b: exact with extra stage placed after X (timing of X.a and Z.b injections consistent).
  V.d injection changes V.p in the box: V.p multiplied by (1+0.5 d) exactly -> V.d is USED, with lit_0.5 = 0.5 as written.
  A small mismatch at U.k1=2 was my own float rounding (tanh vs the sigmoid form); fixed by copying arithmetic exactly.
- e5: 8 random multi-unit networks with random edges/injections/settle + a 9000 tick run: all 20 outputs of every unit exact.
- Conclusion: 4 differences: V.k10=32, V.lit_10=20, stages=5, V.d used. Nothing else visible.
  Cannot test: k4,k6,k8,k7,k11 (invisible if dead, and outputs are fully explained without them).

## 3. Mechanism (box)
Beat at t=0 (z=3.16). The big swing sits in V's 32-tick variance window, so V is in gentle mode and the loop relaxes to a small 2-value ripple (z 1.0/1.31).
At tick ~33 the swing leaves the window, variance < 0.1, V flips to violent mode: V.p jumps to 1.6 (n=84, z=0); 5 ticks later the zero returns, V answers -0.35 (n=-12),
5 ticks later z=3.16 = next beat. Period = 32 + 2*5 = 42. (docs: 50 + 2*4 + 1 = 59.)

## 4. Gates 0-2 committed (commit_answer.json). g2 from model: a 93, b 35, c 44, d silent, e silent, f silent, g 97, h 46.
 d/e/f are 'silent' only by the >3.0 definition (rebounds reach 2.53); robust to random early perturbations in the model.
