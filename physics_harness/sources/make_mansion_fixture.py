"""Record independently specified regression baselines; never imported by solver."""
import hashlib
import json
import math
from pathlib import Path

root=Path(__file__).resolve().parents[1]
inputs={
 'g':10.,'c':3e8,
 'knife':{'m':1.,'ell':1.,'angle':.1},
 'engine':{'heat':15.,'work':3.,'frequency':1.,'I':.5,'w0':4.,'time':4.},
 'governor':{'m_each':1.,'ell':.5,'omega':5.},
 'spool':{'m':2.,'R':.2,'r':.12,'I':.04,'F':6.},
 'ladder':{'m':8.,'L':3.,'foot':1.8,'height':2.4,'foot_speed':.4},
 'ball':{'m':1.,'R':.05,'J':2.},
 'basin':{'center_radius':5/7},
 'hoop':{'R':.25,'omega':8.},
 'puck':{'m':.5,'r0':.6,'r1':.3,'v0':2.},
 'pendulum':{'m':1.,'ell':1.},
 'circuit':{'source_voltage':6.,'charging_C':.1,'resistor':20.,'ready_voltage':4.,'L':.1},
 'line':{'L_per_m':.5e-6,'C_per_m':.2e-9,'pulse_volts':[6.,6.],'frequencies':[5e6,4e6]},
 'light':{'energies':[.080,.020],'S_interval':10.},
 'chair':{'energy':.080},'test':{'taps':100}}
r2=math.sqrt(2);wa=math.sqrt(10*(2-r2));wb=math.sqrt(10*(2+r2))
nu=wa/6;period=math.tau/nu;cap=1/(.1*wa**2)
baseline={
 'knife_energy':(.05,'J'),'knife_speed':(math.sqrt(.1),'m/s'),
 'knife_period':(math.tau/math.sqrt(10),'s'),
 'knife_doubled_mass_period':(math.tau/math.sqrt(10),'s'),
 'engine_heat_out':(12,'J'),'engine_efficiency':(.2,'1'),'engine_power':(3,'W'),
 'engine_final_omega':(8,'rad/s'),'engine_torque_start':(.75,'N m'),
 'engine_torque_end':(.375,'N m'),
 'governor_cos_angle':(.8,'1'),'governor_angle':(math.acos(.8),'rad'),
 'governor_rise':(.1,'m'),'governor_threshold':(math.sqrt(20),'rad/s'),
 'spool_acceleration':(.8,'m/s^2'),'spool_friction':(-4.4,'N along pull'),
 'spool_balance_angle':(math.acos(.6),'rad'),'spool_effective_mass':(3,'kg'),
 'ladder_top_velocity':(-.3,'m/s upward'),'ladder_release_height':(1.6,'m'),
 'ladder_released_energy':(32,'J'),'ladder_center_speed':(math.sqrt(6),'m/s'),
 'ladder_translation':(24,'J'),'ladder_rotation':(8,'J'),
 'ladder_kinetic_per_mass':(4,'J/kg'),'ladder_initial_wall_force':(28.8,'N'),
 'ball_speed':(2,'m/s'),'ball_height':(.07,'m'),'ball_omega':(40,'rad/s'),
 'ball_translation':(2,'J'),'ball_rotation':(.8,'J'),
 'ball_rough_center_hit_speed':(10/7,'m/s'),'ball_rough_center_hit_table_impulse':(-4/7,'N s along cue'),
 'basin_period':(math.tau/math.sqrt(10),'s'),
 'basin_bead_period':(math.tau/math.sqrt(14),'s'),'basin_matched_radius':(5/7,'m'),
 'hoop_center':(2,'m/s'),'hoop_top':(4,'m/s'),'hoop_bottom':(0,'m/s'),
 'hoop_front':(math.sqrt(8),'m/s'),
 'puck_final_speed':(4,'m/s'),'puck_initial_omega':(10/3,'rad/s'),
 'puck_final_omega':(40/3,'rad/s'),'puck_tension_initial':(10/3,'N'),
 'puck_tension_final':(80/3,'N'),'puck_work':(3,'J'),
 'pendulum_slow':(wa,'rad/s'),'pendulum_fast':(wb,'rad/s'),
 'pendulum_ratio':(1+r2,'1'),'pendulum_ratio_slow':(r2,'1'),
 'pendulum_ratio_fast':(-r2,'1'),'pendulum_slow_period':(math.tau/wa,'s'),
 'pendulum_fast_period':(math.tau/wb,'s'),
 'pendulum_beat_rate':(wb-wa,'rad/s'),
 'pendulum_reinforcement_interval':(math.tau/(wb-wa),'s'),
 'circuit_initial_current':(.3,'A'),'circuit_time_constant':(2,'s'),
 'circuit_ready_current':(.1,'A'),'circuit_ready_charge':(.4,'C'),
 'circuit_ready_energy':(.8,'J'),'circuit_ready_time':(2*math.log(3),'s'),
 'circuit_tuned_C':(cap,'F'),'circuit_omega':(wa,'rad/s'),
 'circuit_eta':(4+2*r2,'kg m^2'),'circuit_D':(40,'N m/rad'),
 'coupling_slow':(2*wa/3,'rad/s'),'coupling_fast':(1.5*wa,'rad/s'),
 'coupling_product':(wa**2,'s^-2'),'coupling_ratio':(9/4,'1'),
 'coupling_gap':(5*wa/6,'rad/s'),'coupling_kappa':(5*math.sqrt(4)/6,'N m/A'),
 'line_speed':(1e8,'m/s'),'line_impedance':(50,'ohm'),
 'line_overlap_voltage':(12,'V'),'line_overlap_current':(0,'A'),
 'line_overlap_energy':(14.4e-9,'J/m'),'line_slow_crest':(1e8/9,'m/s'),
 'line_fast_crest':(9e8,'m/s'),'line_fast_over_c':(3,'1'),
 'light_energy':(.1,'J'),'light_momentum':(2e-10,'kg m/s'),
 'light_rest_energy':(.08,'J'),'light_beta':(.6,'1'),'light_gamma':(1.25,'1'),
 'light_proper_time':(8,'s'),'light_one_pulse_H':(.04,'J'),
 'light_rest_mass':(.08/9e16,'kg'),'light_doppler_stretch':(2,'1'),
 'chair_charge':(math.sqrt(2*cap*.08),'C'),
 'chair_voltage':(math.sqrt(2*.08/cap),'V'),'chair_period':(period,'s'),
 'chair_S_period':(1.25*period,'s'),'chair_S_distance':(1.8e8*1.25*period,'m'),
 'chair_half_charge_ratio':(5/13,'1'),'chair_half_mechanical':(.08*144/169,'J'),
 'chair_half_capacitor':(.08*25/169,'J'),'chair_max_energy_drift':(0,'J'),
 'chair_return_error':(0,'scaled state'),
 'test_coherent_multiple':(10000,'E1'),'test_random_expected_multiple':(100,'E1'),
 'test_last_kick_multiple':(199,'E1')}
source=root/'sources/mansion_pset_261022.tex'
case={'case_id':'mansion-261022-v1','description':'All thirteen main questions and the physics of all three bonus depths; supplied exact linear models.',
 'source':{'url':'https://github.com/saccade/claudog/blob/main/mansion/pset/mansion_pset.tex',
           'git_blob_sha':'fd3c12cc6b217a5323efa4bced7b0c6a9a5ebb80','sha256':hashlib.sha256(source.read_bytes()).hexdigest()},
 'assumptions':['Small-oscillation models are exact within their linearization; finite pendulums need not recur exactly.',
 'Flywheel receives the stated constant power; unloaded ladder release is distinct from the imposed-speed snapshot.',
 'Spool rolls without slipping with sufficient grip; the direction of friction is solved, not assumed.',
 'Cue contact is horizontal; table impulse is negligible during the ideal short strike. This assumption is not explicit in the source and is reviewed separately.',
 'Puck starts and ends on circles; radial work is retained even when shortening is slow.',
 'Transmission line is lossless and nondispersive; its signal speed follows characteristics, not crest speed.',
 'Coupled machine has ideal reciprocal velocity coupling and no loss; pulses and receiver clocks use inertial SR.',
 'TEST supplies equal velocity kicks to one uncoupled oscillator; random phase advances are independent uniform.'],
 'inputs':inputs,'observables':{name:{'expected':value,'unit':unit,'atol':1e-10 if abs(value)>1e-8 or value==0 else 1e-24,'rtol':1e-8} for name,(value,unit) in baseline.items()}}
(root/'cases/mansion.json').write_text(json.dumps(case,indent=2)+'\n')
registry=json.loads((root/'registry.json').read_text())
registry['entries']=[e for e in registry['entries'] if e['case']!='mansion']
registry['entries'] += [
 {'case':'mansion','implementation':'codex','entrypoint':'implementations/codex/mansion.py','status':'available','provenance':'Codex independent force balances, generalized eigenproblem, quadrature and DOP853 integration; source snapshot recorded in fixture.'},
 {'case':'mansion','implementation':'claude','entrypoint':'implementations/claude/mansion.py','status':'missing','provenance':'Claude has reviewed earlier versions, but no original Mansion implementation is registered in this harness. Do not relabel Codex code.'}]
(root/'registry.json').write_text(json.dumps(registry,indent=2)+'\n')
