import json
import numpy as np
from scipy.linalg import expm
from pathlib import Path

# Short onset of ideal guided cap lift: constant uniform pressure.
m=1.; area=1e-4; gauge=120000.; weight=10.
force=gauge*area; dt=.01
v=(force-weight)*dt/m
rise=(force-weight)*dt**2/(2*m)
cap={'force':force,'net_force':force-weight,'added_movement':m*v,'pace':v,'rise':rise,'gas_work':force*rise,'heft':weight*rise,'punch':m*v*v/2}
assert abs(cap['gas_work']-cap['heft']-cap['punch'])<1e-15

# Two point weights, slowly moved out at fixed angular speed.
mw=1.; r0=.2; r1=.3; omega=10.
i0=2*mw*r0**2; i1=2*mw*r1**2
roll0=i0*omega; roll1=i1*omega
hook0=i0*omega**2/2; hook1=i1*omega**2/2
engine_work=omega*(roll1-roll0)
link_work=mw*omega**2*(r1*r1-r0*r0)
gov={'initial_roll':roll0,'final_roll':roll1,'initial_hook':hook0,'final_hook':hook1,'engine_work':engine_work,'link_work':link_work}
assert abs(engine_work-(hook1-hook0)-link_work)<1e-12

# Diaphragm plus isothermal fixed-volume gas snapshots.
A=.001; k=10000.; f0=100.; travel=.001
f1=f0-k*travel
p0=f0/A; p1=f1/A
spring_work=f0*travel-k*travel**2/2
mass0=.010; mass1=.0095; pabs0=200000.; ambient=100000.
pabs1=pabs0*mass1/mass0
assert abs((pabs1-ambient)-p1)<1e-9
diaph={'start_gauge':p0,'new_gauge':p1,'spring_work':spring_work,'mass_start_g':mass0*1000,'mass_end_g':mass1*1000}

# Small-perturbation governor loop, after a one-unit addition of roll.
# z stores excess roll; y is sleeve closure; f is excess drive torque.
# Time and the three variables are scaled; both response lags are 1.
checks={}
for gain in (1.,4.):
    B=np.array([[0.,0.,1.],[1.,-1.,0.],[0.,-gain,-1.]])
    vals=np.linalg.eigvals(B)
    poly=np.poly(B)
    assert np.allclose(poly,[1,2,1,gain])
    checks[str(int(gain))]={'eigenvalues':[[float(x.real),float(x.imag)] for x in vals], 'samples':{str(t):float((expm(B*t)@np.array([1.,0.,0.]))[0]) for t in (0,2,4,6,10)}}
assert max(v[0] for v in checks['1']['eigenvalues'])<0
assert max(v[0] for v in checks['4']['eigenvalues'])>0
out={'cap':cap,'governor_work':gov,'diaphragm':diaph,'loop':checks}
Path('/workspace/scratch/c6c5d3f3995e/valves/checks.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
