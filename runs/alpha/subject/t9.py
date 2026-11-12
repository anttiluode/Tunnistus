import sim, box, numpy as np
from t2 import cmp, rec1
# V.d constantly driven, several amplitudes and U: is V.p ever changed?
for U in [1.0,0.3,1.6]:
    for amp in [0.7,-1.5,4.0]:
        spec={'units':[U,1.0],'edges':[['1:U.p','0:V.d',amp]],'record':rec1(0),'ticks':1200}
        m,b=cmp(f'V.d const {amp} U={U}',spec)
        ref=box.run({'units':[U],'record':['0:V.p'],'ticks':1200}) if amp==0.7 else ref
        print('     box V.p identical to no-V.d run:', np.array_equal(b['0:V.p'],ref['0:V.p']))
# time-varying V.d from another unit's Z
cmp('V.d from clock Z',{'units':[1.0,0.9],'edges':[['1:Z.p3','0:V.d',2.0],['1:V.p','0:V.d',-1.0]],'record':rec1(0),'ticks':3000})
# all five inputs driven at once by another clock
cmp('all ports',{'units':[1.0,0.7,1.3],'edges':[['1:Z.p2','0:V.a',0.3],['1:V.p','0:V.c',-0.8],['2:Z.p3','0:X.a',0.2],['2:V.s','0:Z.b',0.15],['1:V.r','0:V.d',1.0]],'record':rec1(0),'ticks':6000,'settle':50})
print(box.status())
