"""Constant and changing capture: kinematics, charge pulses, driven motion. Codex.

SI magnitudes at every numerical boundary. Voltage is the signed terminal drop
E = kappa*omega; generated EMF along positive current is its opposite.
"""

from dataclasses import dataclass
import numpy as np
from scipy.integrate import solve_ivp


@dataclass(frozen=True)
class CaptureLaw:
    mode: str = 'constant'
    base: float = .5
    ripple: float = .8

    def kappa(self, theta):
        theta = np.asarray(theta)
        if self.mode == 'constant':
            return np.zeros_like(theta) + self.base
        if self.mode == 'ripple':
            return self.base * (1 + self.ripple*np.cos(theta))
        if self.mode == 'ring':
            return -self.base*np.sin(theta)
        raise ValueError(self.mode)

    def slope(self, theta):
        theta = np.asarray(theta)
        if self.mode == 'constant':
            return np.zeros_like(theta)
        if self.mode == 'ripple':
            return -self.base*self.ripple*np.sin(theta)
        if self.mode == 'ring':
            return -self.base*np.cos(theta)
        raise ValueError(self.mode)

    def linkage(self, theta):
        theta = np.asarray(theta)
        if self.mode == 'constant':
            return self.base*theta
        if self.mode == 'ripple':
            return self.base*(theta + self.ripple*np.sin(theta))
        if self.mode == 'ring':
            return self.base*np.cos(theta)
        raise ValueError(self.mode)


def prescribed(law, omega0=1., alpha=.2, theta0=.3, duration=6., count=1201):
    t = np.linspace(0, duration, count)
    theta = theta0 + omega0*t + alpha*t*t/2
    omega = omega0 + alpha*t
    k = law.kappa(theta)
    voltage = k*omega
    extra = law.slope(theta)*omega*omega
    return dict(t=t, theta=theta, omega=omega, kappa=k,
                linkage=law.linkage(theta), voltage=voltage,
                shortcut=k*alpha, extra=extra, climb=k*alpha+extra,
                frozen_linkage=law.linkage(theta0)+float(law.kappa(theta0))*(theta-theta0))


def pulse_current(t, charge, center, width):
    phase = (np.asarray(t) - (center-width/2))/width
    return np.where((phase >= 0) & (phase <= 1),
                    2*charge/width*np.sin(np.pi*phase)**2, 0.)


def charge_pulse(law, charge=.2, center=.5, width=.3, duration=3.,
                 inertia=.1, theta0=.3, omega0=1., rtol=2e-10):
    if not (0 <= center-width/2 < center+width/2 <= duration):
        raise ValueError('The whole pulse must fit inside the experiment.')
    def rhs(t, y):
        theta, spin, q, work = y
        current = float(pulse_current(t, charge, center, width))
        torque = float(law.kappa(theta))*current
        return [spin/inertia, torque, current, torque*spin/inertia]
    t = np.linspace(0, duration, 1201)
    sol = solve_ivp(rhs, (0, duration), [theta0, inertia*omega0, 0., 0.],
                    t_eval=t, method='DOP853', rtol=rtol, atol=rtol/100,
                    max_step=width/12)
    if not sol.success:
        raise RuntimeError(sol.message)
    theta, spin, q, work = sol.y
    kinetic = spin*spin/(2*inertia)
    return dict(t=t, theta=theta, omega=spin/inertia, q=q,
                current=pulse_current(t, charge, center, width),
                kappa=law.kappa(theta), added_spin=spin-spin[0], work=work,
                kinetic=kinetic, frozen_spin=float(law.kappa(theta0))*q,
                energy_error=kinetic-kinetic[0]-work)


def driven(law, drive=1.2, frequency=2/3, damping=.5, inertia=1.,
           current=1., duration=180., max_step=.04, theta0=.2):
    """A DC-fed shaft with a separate sinusoidal torque drive and damping.

    Ring capture makes the DC torque a pendulum-like restoring torque.
    The periodic torque drive supplies the extra degree of freedom for chaos.
    The tangent comparison holds the forcing phase fixed.
    """
    def rhs(t, y):
        theta, omega, motor_work, drive_work, heat, dtheta, domega = y
        motor = float(law.kappa(theta))*current
        forcing = drive*np.cos(frequency*t)
        accel = (motor+forcing-damping*omega)/inertia
        return [omega, accel, motor*omega, forcing*omega, damping*omega*omega,
                domega, (current*float(law.slope(theta))*dtheta-damping*domega)/inertia]
    t = np.linspace(0, duration, round(duration/.04)+1)
    y0 = [theta0, 0., 0., 0., 0., 1., 0.]
    sol = solve_ivp(rhs, (0, duration), y0, t_eval=t, dense_output=True,
                    method='DOP853', rtol=2e-10, atol=2e-12, max_step=max_step)
    if not sol.success:
        raise RuntimeError(sol.message)
    # Separate nearby trajectory; its finite displacement eventually saturates.
    nearby = solve_ivp(lambda t,y: rhs(t, [*y,0.,0.,0.,1.,0.])[:2],
                       (0, duration), [theta0+1e-8, 0.], t_eval=t,
                       method='DOP853', rtol=2e-10, atol=2e-12, max_step=max_step)
    theta, omega, wm, wd, heat, dtan, wtan = sol.y
    burn = min(40., duration/3)
    mask = t >= burn
    # Normalize sweep with 1 s, making the norm a dimensionless state-space norm.
    stretch = np.hypot(dtan, wtan*1.)
    estimate = (np.log(stretch[-1])-np.log(stretch[mask][0]))/(t[-1]-t[mask][0])
    ticks = np.arange(np.ceil(burn*frequency/(2*np.pi)),
                      duration*frequency/(2*np.pi))*2*np.pi/frequency
    points = sol.sol(ticks)[:2]
    separation = np.hypot(np.angle(np.exp(1j*(theta-nearby.y[0]))),
                          (omega-nearby.y[1])*1.)
    kinetic = inertia*omega*omega/2
    return dict(t=t, theta=theta, omega=omega, nearby_theta=nearby.y[0],
                separation=separation, poincare=points, stretch=stretch,
                lyapunov=float(estimate), energy_error=kinetic-wm-wd+heat,
                motor_work=wm, drive_work=wd, heat=heat,
                kappa=law.kappa(theta), voltage=law.kappa(theta)*omega)
