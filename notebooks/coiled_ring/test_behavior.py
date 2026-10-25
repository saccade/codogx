"""Check the physical shortcuts, their failures, and the unchanged power ledger."""
import numpy as np
from numpy.testing import assert_allclose
from capture_behavior import CaptureLaw, prescribed, charge_pulse, driven
from display_units import UnitPicker, QuantitySlider, SI_UNITS


def test_constant_capture_same_charge_same_added_spin():
    law=CaptureLaw('constant',.5)
    for center in [.5,2.5]:
        d=charge_pulse(law,center=center)
        assert_allclose(d['q'][-1],.2,atol=1e-8)
        assert_allclose(d['added_spin'],.5*d['q'],atol=1e-12)
        assert_allclose(d['energy_error'],0,atol=2e-9)


def test_variable_capture_changes_pulse_result_without_breaking_energy():
    early,late=[charge_pulse(CaptureLaw('ripple'),center=c) for c in [.5,2.5]]
    assert_allclose(early['q'][-1],late['q'][-1],atol=1e-8)
    assert abs(early['added_spin'][-1]-late['added_spin'][-1])>.1
    for d in [early,late]:assert_allclose(d['energy_error'],0,atol=2e-9)


def test_voltage_climb_includes_the_changing_capture_term():
    for mode in ['constant','ripple','ring']:
        d=prescribed(CaptureLaw(mode),count=12001)
        measured=np.gradient(d['voltage'],d['t'],edge_order=2)
        assert_allclose(measured,d['climb'],atol=2e-6)
    d=prescribed(CaptureLaw('ripple'),alpha=0.)
    assert_allclose(d['shortcut'],0)
    assert np.max(abs(d['climb']))>.1


def test_linkage_derivative_is_capture():
    theta=np.linspace(-4,4,100)
    for mode in ['constant','ripple','ring']:
        law=CaptureLaw(mode)
        measured=(law.linkage(theta+1e-5)-law.linkage(theta-1e-5))/2e-5
        assert_allclose(measured,law.kappa(theta),atol=1e-9)


def test_driven_ring_stretches_nearby_starts_at_both_step_limits():
    for step in [.04,.02]:
        d=driven(CaptureLaw('ring',1.),max_step=step)
        assert d['lyapunov']>.04
        assert_allclose(d['energy_error'],0,atol=1e-7)
    d=driven(CaptureLaw('constant',1.))
    assert abs(d['lyapunov'])<1e-8


def test_unforced_ring_settles_even_though_capture_changes():
    d=driven(CaptureLaw('ring',1.),drive=0.,duration=90.)
    assert abs(d['omega'][-1])<1e-8
    assert abs(d['theta'][-1])<1e-8


def test_unit_changes_preserve_slider_physics_and_si_is_default():
    p=UnitPicker(['length','current','angle'])
    assert p.units==SI_UNITS
    length=QuantitySlider(p,'length','radius',.2,0,.4,.05)
    angle=QuantitySlider(p,'angle','angle',np.pi/2,0,2*np.pi,.01)
    for unit in ['hand','cm','m']:
        p.selectors['length'].value=unit
        assert_allclose(length.si,.2)
    p.selectors['angle'].value='turn'
    assert_allclose(angle.slider.value,.25)
    assert_allclose(angle.si,np.pi/2)
    assert UnitPicker([],{'energy':'thump'}).units['energy']=='thump'
