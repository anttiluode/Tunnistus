import sim, numpy as np
from g3 import classify, excitable
for S,C in [(1.43,1.428),(-0.232,-0.23),(-0.546,-0.548),(-1.388,-1.386),(-1.988,-1.99)]:
    for i in range(34):
        m=(S+C)/2; k=classify(m,4000)[0]
        if k=='S': S=m
        elif k=='C': C=m
        else: print('  odd at',m,classify(m,4000)); break
    print('S',repr(S),'C',repr(C),'gap',abs(S-C), 'c1 at boundary', 0.5+0.1*S)
