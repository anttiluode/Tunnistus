import sim, numpy as np
from g3e import badcount
lo,hi=1.468,1.47
for i in range(22):
    m=(lo+hi)/2
    if badcount(m)[0]==0: hi=m
    else: lo=m
print(repr(lo),repr(hi))
