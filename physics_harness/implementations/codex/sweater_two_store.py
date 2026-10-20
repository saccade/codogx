"""Codex numerical cross-check of Claude's CL-180/181 equations.
Captured from the independent NumPy/SciPy check run in this conversation.
This is NOT Claude's original implementation; that remains unavailable.
"""
import sys, json
import numpy as np
from scipy.linalg import expm
from scipy.integrate import solve_ivp
case=json.load(open(sys.argv[1],encoding='utf-8'))
p=case['inputs']
cs,cb=p['skin_capacity'],p['bulk_capacity']
gh,gi,gr=p['hot_conductance'],p['inner_conductance'],p['room_conductance']
A=np.array([[-(gh+gi)/cs,gi/cs],[gi/cb,-gi/cb]])
B=np.array([gh/cs,0.])
C=np.array([[-(gr+gi)/cs,gi/cs],[gi/cb,-gi/cb]])
carry=expm(C*p['carry_s'])
hold=np.array([cs,cb])
def hot(t):
 return np.linalg.solve(A,(expm(A*t)-np.eye(2))@(B*p['plateau_K']))
def cold(t):
 sol=solve_ivp(lambda time,x:A@x+B*min(time*p['ramp_K_per_s'],p['plateau_K']),
     (0,t),[0.,0.],rtol=1e-11,atol=1e-12,max_step=.2)
 if not sol.success: raise RuntimeError(sol.message)
 return sol.y[:,-1]
x=hot(10); y=carry@x
observations={'skin_door':float(x[0]),'bulk_door':float(x[1]),
 'skin_neck':float(y[0]),'bulk_neck':float(y[1]),
 'heat_lost':float(hold@(x-y)),
 'net_heat_inward':float(cb*(y[1]-x[1]))}
for t in p['cold_times_s']:
 observations[f'cold_{t}_retained_K']=float(hold@(carry@cold(t))/sum(hold))
for t in p['hot_times_s']:
 observations[f'hot_{t}_retained_K']=float(hold@(carry@hot(t))/sum(hold))
# With the room path closed, redistribution must conserve the total heat.
internal=np.array([[-gi/cs,gi/cs],[gi/cb,-gi/cb]])
residual=abs(float(hold@(expm(internal*15)@x-x)))
observations['redistribution_residual_J']=residual
checks={'heat_does_not_grow_on_carry':bool(hold@y<=hold@x),
        'closed_redistribution_conserves_heat':residual<1e-8}
print(json.dumps({'schema_version':1,'case_id':case['case_id'],
 'implementation':'codex','observations':observations,'checks':checks}))
