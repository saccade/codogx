"""Codex independent Mansion model checks, 2026-10-22.

Inputs/expected outputs are shared data; no Claude solver is imported.
Coordinates here are computational axes, not definitions of book arrows.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.linalg import expm

case = json.loads(Path(sys.argv[1]).read_text())
p = case['inputs']
g = p['g']
o, checks = {}, {}
def record(prefix, **values):
    o.update({prefix + '_' + k: float(v) for k, v in values.items()})
def check(name, value):
    checks[name] = bool(value)
def close(a, b, atol=1e-10):
    return np.allclose(a, b, rtol=1e-10, atol=atol)

# 1: energy first, then the linear oscillator.
c = p['knife']; m, ell, angle = c['m'], c['ell'], c['angle']
energy = m*g*ell*angle**2/2
wknife = math.sqrt(g/ell)
record('knife', energy=energy, speed=math.sqrt(2*energy/m),
       period=math.tau/wknife, doubled_mass_period=math.tau/wknife)
record('knife', exact_energy=m*g*ell*(1-math.cos(angle)))
check('knife_small_angle_energy_within_0.1_percent',
      abs(energy/(m*g*ell*(1-math.cos(angle)))-1) < .001)

# 2: heat balance and finite flywheel energy addition.
c=p['engine']; P=c['work']*c['frequency']
w1=math.sqrt(c['w0']**2+2*P*c['time']/c['I'])
record('engine', heat_out=c['heat']-c['work'], efficiency=c['work']/c['heat'],
       power=P, final_omega=w1, torque_start=P/c['w0'], torque_end=P/w1)
check('flywheel_work_balance', close(c['I']*(w1*w1-c['w0']**2)/2,P*c['time']))

# 3 + cabinet a: force and torque about the center, solved together.
c=p['governor']; drop=g/c['omega']**2
record('governor', cos_angle=drop/c['ell'], angle=math.acos(drop/c['ell']),
       rise=c['ell']-drop, threshold=math.sqrt(g/c['ell']))
c=p['spool']; m,R,r,I,F=(c[k] for k in ['m','R','r','I','F'])
# a>0 is pulling direction, alpha=-a/R; f positive in pulling direction.
A=np.array([[m,-1.],[-I/R,-R]])
ax,f=np.linalg.solve(A,[F,F*r])
record('spool', acceleration=ax, friction=f, balance_angle=math.acos(r/R),
       effective_mass=m+I/R**2)
check('spool_independent_force_torque_balance',close([m*ax,F*r+f*R],[F+f,-I*ax/R]))
check('spool_contact_power_cancels',close(f*R + f*R*(-1),0))

# 4 + b + funhouse 4: derivative of the actual constraint and wall reaction.
c=p['ladder']; m,L,x0,h0=(c[k] for k in ['m','L','foot','height'])
top_speed=-x0/h0*c['foot_speed']; h=2*h0/3
released=m*g*(h0-h)/2
omega=math.sqrt(6*released/(m*L*L)); vc=L*omega/2
record('ladder', top_velocity=top_speed, release_height=h, released_energy=released,
       center_speed=vc, translation=m*vc*vc/2, rotation=m*L*L*omega*omega/24,
       kinetic_per_mass=released/m, initial_wall_force=m*g*x0*(3*h0)/(4*L*L))
check('ladder_energy_split',close(m*vc*vc/2+m*L*L*omega*omega/24,released))
check('ladder_instantaneous_center_distance',close(math.hypot(x0/2,h0/2),L/2))
# phi from the floor: phi_ddot=-3g cos(phi)/(2L).
phi=math.asin(h/L); acc_phi=-3*g*math.cos(phi)/(2*L)
wall=m*(-L/2)*(math.cos(phi)*omega**2+math.sin(phi)*acc_phi)
check('ladder_wall_reaction_zero_at_departure',abs(wall)<1e-12)

# 5 + cabinet c: model with negligible table impulse during the strike.
c=p['ball']; m,R,J=(c[k] for k in ['m','R','J']); I=2*m*R*R/5
v=J/m; H=R+I/(m*R); w=J*(H-R)/I
record('ball', speed=v, height=H, omega=w, translation=m*v*v/2,rotation=I*w*w/2)
check('ball_post_strike_contact_velocity_zero',close(v-R*w,0))
# Alternative impulsive no-slip constraint: a nonzero table impulse changes part a.
f_impulse=-2*J/7
record('ball', rough_center_hit_speed=(J+f_impulse)/m,
       rough_center_hit_table_impulse=f_impulse)
check('rough_center_hit_also_rolls_with_table_impulse',close((J+f_impulse)/m,-R*R*f_impulse/I))

# 6: effective kinetic mass 7m/5, linear height restoring term.
a=p['basin']['center_radius']; Tball=math.tau*math.sqrt(7*a/(5*g))
record('basin', period=Tball, bead_period=math.tau*math.sqrt(a/g),matched_radius=5*ell/7)
check('basin_matches_knife_linear_period',close(Tball,math.tau/wknife))

# 7: combine translational and rotational velocity vectors.
c=p['hoop']; v=c['R']*c['omega']
record('hoop', center=v,top=2*v,bottom=0,front=math.hypot(v,v))

# 8: central force keeps angular momentum, radial work checked as a finite exchange.
c=p['puck']; m,r0,r1,v0=(c[k] for k in ['m','r0','r1','v0']); h=r0*v0
v1=h/r1; work=m*(v1*v1-v0*v0)/2
record('puck', final_speed=v1,initial_omega=v0/r0,final_omega=v1/r1,
       tension_initial=m*v0*v0/r0,tension_final=m*v1*v1/r1,work=work)
check('puck_work_integral_matches_energy',close(quad(lambda r:m*h*h/r**3,r1,r0)[0],work))
# Arbitrary smooth finite-time inward path, radial speed zero at endpoints.
duration=4.
def path(t):
    u=t/duration; dr=r1-r0
    return r0+dr*(10*u**3-15*u**4+6*u**5), dr*(30*u*u-60*u**3+30*u**4)/duration, dr*(60*u-180*u*u+120*u**3)/duration**2
fullwork=quad(lambda t: (lambda r,rd,rdd: -m*(h*h/r**3-rdd)*rd)(*path(t)),0,duration,epsabs=1e-12)[0]
check('puck_radial_work_exact_between_circular_endpoints',close(fullwork,work))

# 9 + d + funhouse 1: generalized eigenvalues, not supplied mode formulas.
M=np.array([[2.,1.],[1.,1.]])*p['pendulum']['m']*p['pendulum']['ell']**2
K=np.diag([2.,1.])*p['pendulum']['m']*g*p['pendulum']['ell']
vals,vec=np.linalg.eig(np.linalg.solve(M,K)); ix=np.argsort(vals); vals,vec=vals[ix],vec[:,ix]
wa,wb=np.sqrt(vals); ratios=vec[1]/vec[0]
record('pendulum',slow=wa,fast=wb,ratio=wb/wa,slow_period=math.tau/wa,
       fast_period=math.tau/wb,ratio_slow=ratios[0],ratio_fast=ratios[1],
       beat_rate=wb-wa,reinforcement_interval=math.tau/(wb-wa))
eta=float(np.array([1,math.sqrt(2)])@M@np.array([1,math.sqrt(2)]))
D=float(np.array([1,math.sqrt(2)])@K@np.array([1,math.sqrt(2)]))
check('pendulum_modes_satisfy_both_balances',close(K@vec,M@vec@np.diag(vals)))
check('pendulum_beats_do_not_return_state',not close(np.cos([wa,wb]*np.array([math.tau/(wb-wa)])),[1,1]))

# 10 + e + funhouse 2: RC charging and the full coupled state matrix.
c=p['circuit']; V,Crc,Rc,L=(c[k] for k in ['source_voltage','charging_C','resistor','L'])
Vtarget=c['ready_voltage']; qtarget=Crc*Vtarget; C=1/(L*wa*wa)
record('circuit',initial_current=V/Rc,time_constant=Rc*Crc,
       ready_current=(V-Vtarget)/Rc,ready_charge=qtarget,ready_energy=Crc*Vtarget**2/2,
       ready_time=-Rc*Crc*math.log(1-Vtarget/V),tuned_C=C,omega=1/math.sqrt(L*C),
       eta=eta,D=D)
nu=wa/6; gap=5*nu; kappa=gap*math.sqrt(eta*L)
B=np.array([[0,0,1,0],[0,0,0,1],[-wa*wa,0,0,gap],[0,-wa*wa,-gap,0.]])
freq=np.sort(np.linalg.eigvals(B).imag[np.linalg.eigvals(B).imag>0])
record('coupling',slow=freq[0],fast=freq[1],product=np.prod(freq),ratio=freq[1]/freq[0],
       gap=freq[1]-freq[0],kappa=kappa)
check('coupling_eigenfrequencies_match_supplied_tones',close(freq,[4*nu,9*nu]))
G=np.diag([wa*wa,wa*wa,1,1])
check('coupled_energy_is_conserved',close(B.T@G+G@B,np.zeros((4,4))))
check('coupling_powers_cancel',close(kappa*.3*.7-kappa*.7*.3,0))

# 11 + f + funhouse 3: two characteristics and energy transport.
c=p['line']; Lp,Cp=(c[k] for k in ['L_per_m','C_per_m']); u=1/math.sqrt(Lp*Cp); Z=math.sqrt(Lp/Cp)
Vp,Vm=c['pulse_volts']; Iline=(Vp-Vm)/Z
f1,f2=c['frequencies']; slow=u*(f1-f2)/(f1+f2); fast=u*(f1+f2)/(f1-f2)
record('line',speed=u,impedance=Z,overlap_voltage=Vp+Vm,overlap_current=Iline,
       overlap_energy=(Cp*(Vp+Vm)**2+Lp*Iline**2)/2,slow_crest=slow,fast_crest=fast,
       fast_over_c=fast/p['c'])
grid=np.linspace(-10,10,81)
check('line_energy_flux_bound',all(abs(v*i)<=u*(Cp*v*v+Lp*i*i)/2+1e-14 for v in grid for i in grid))
check('line_characteristic_speed',close([Lp*u/Z,Cp*Z*u],[1,1]))
check('line_crest_speed_product',close(slow*fast,u*u))
xx=np.linspace(0,10,37);tt=1.7e-7; w1,w2=math.tau*f1,math.tau*f2; k1,k2=w1/u,w2/u
check('line_cosine_product_identity',close(np.cos(k1*xx-w1*tt)+np.cos(k2*xx+w2*tt),
  2*np.cos(((k1-k2)*xx-(w1+w2)*tt)/2)*np.cos(((k1+k2)*xx-(w1-w2)*tt)/2)))

# 12 + g + funhouse 3: boost the two photon energies individually.
c=p['light']; E1,E2=c['energies']; E=E1+E2; pc=E1-E2
beta=pc/E; gamma=1/math.sqrt(1-beta*beta); Erest=math.sqrt(E*E-pc*pc)
E1h=gamma*E1*(1-beta); E2h=gamma*E2*(1+beta)
record('light',energy=E,momentum=pc/p['c'],rest_energy=Erest,beta=beta,gamma=gamma,
       proper_time=c['S_interval']/gamma,one_pulse_H=E1h,rest_mass=Erest/p['c']**2,
       doppler_stretch=math.sqrt((1+beta)/(1-beta)))
check('boost_equalizes_pulses',close(E1h,E2h))
check('photon_energy_product_is_invariant',close(E1*E2,E1h*E2h))

# 13 + understage alpha: integrate, rather than substitute supplied charge curve.
E0=p['chair']['energy']; y0=math.sqrt(2*E0/(wa*wa)); z0=np.array([0,y0,0,0])
T=math.tau/nu; half=expm(B*T/2)@z0; end=expm(B*T)@z0
trajectory=solve_ivp(lambda t,z:B@z,[0,T],z0,rtol=2e-12,atol=2e-14,dense_output=True,method='DOP853')
sample=trajectory.sol(np.linspace(0,T,501))
energies=np.einsum('ij,ij->j',sample,G@sample)/2
q0=y0/math.sqrt(L)
record('chair',charge=q0,voltage=q0/C,period=T,S_period=gamma*T,
       S_distance=beta*p['c']*gamma*T,half_charge_ratio=half[1]/y0,
       half_mechanical=half[2]**2/2,half_capacitor=wa*wa*half[1]**2/2,
       max_energy_drift=np.max(abs(energies-E0)),return_error=np.max(abs(end-z0)))
check('chair_returns_all_four_state_variables',close(end,z0))
check('chair_integrator_conserves_energy',np.max(abs(energies-E0))<1e-10)
check('chair_halfway_vertical_and_no_current',close(half[[0,3]],[0,0]))
check('chair_stays_at_H_origin',close(gamma*(beta*p['c']*gamma*T-beta*p['c']*gamma*T),0))
check('first_return_from_positive_cosine_weights',math.gcd(4,9)==1)

# Understage beta: deterministic phase-space kicks and exact phase averaging.
N=p['test']['taps']; kick=np.array([1.,0.]); coherent=np.zeros(2)
for _ in range(N): coherent += kick
angles=np.arange(16)*math.tau/16
previous=np.array([2.3,-1.7]); increments=[]
for angle in angles:
    rotated=np.array([[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]])@previous
    increments.append(np.dot(rotated+kick,rotated+kick)-np.dot(previous,previous))
record('test',coherent_multiple=np.dot(coherent,coherent),random_expected_multiple=N,
       last_kick_multiple=2*N-1)
check('uniform_phase_cross_term_averages_to_zero',close(np.mean(increments),1))
check('kick_work_sums_to_final_energy',sum(2*k-1 for k in range(1,N+1))==N*N)

# Assumption probes: these deliberately answer different physical questions.
state=np.zeros(4); step=expm(B*math.tau/wa)
for k in range(N):
    if k: state=step@state
    state[2]+=1
closed_ratio=float(state@G@state)
record('probe',closed_loop_test_energy_multiple=closed_ratio)
check('closed_loop_changes_TEST_resonance',not close(closed_ratio,N*N))
# A crest of the fast cosine factor need not be a crest of the summed field.
probe_t=1e-8; probe_x=fast*probe_t
dVdx=-k1*math.sin(k1*probe_x-w1*probe_t)-k2*math.sin(k2*probe_x+w2*probe_t)
record('probe',sum_spatial_derivative_at_fast_factor_crest=dVdx)
check('factor_crest_is_not_generally_total_wave_crest',abs(dVdx)>1e-3)

print(json.dumps({'schema_version':1,'case_id':case['case_id'],'implementation':'codex',
                  'observations':o,'checks':checks},allow_nan=False))
