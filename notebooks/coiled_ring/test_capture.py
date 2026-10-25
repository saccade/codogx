"""Capture: linked flux per radian of turning. Claude."""

from dataclasses import replace

import numpy as np
import pytest
from numpy.testing import assert_allclose

from ring import Ring, capture, follow_flux, add_forces, torque_about_shaft, area_arrow, winding
from capture_view import reading, TRIANGLE, EDGE_ON
from units import q

ANGLES = [0, .3, TRIANGLE, np.pi/2, 2.8, 4.7]


@pytest.mark.parametrize('heading', [0, .4, 2.1])
def test_capture_is_what_a_small_turn_catches(heading):
    case = Ring(heading=(heading, 'stroke'))
    small = 1e-6
    for angle in ANGLES:
        caught = follow_flux(case, angle+small).linked - follow_flux(case, angle-small).linked
        assert_allclose(capture(case, angle) * 2*small, caught, rtol=1e-6, atol=1e-11)


def test_the_capture_of_the_current_is_the_torque_from_the_forces():
    case = Ring(current=(-1.5, 'ampere'))
    for angle in ANGLES:
        forces = torque_about_shaft(case, add_forces(case, angle).moment)
        assert_allclose(case.values['current'] * capture(case, angle), forces,
                        rtol=1e-5, atol=1e-8)


@pytest.mark.parametrize('sweep', [-1, 2])
def test_shaft_and_circuit_balance(sweep):
    case = Ring(sweep=(sweep, 'sweep'))
    for angle in ANGLES:
        r = reading(case, angle)
        assert_allclose(r.shaft_power + r.circuit_power, 0, atol=1e-12)


def test_a_voltmeter_reads_the_capture():
    case = Ring(sweep=(-1, 'sweep'))
    ω = case.values['sweep']
    dt = 1e-6
    for angle in ANGLES:
        linkage = [follow_flux(case, angle + ω*t).linked for t in (-dt, dt)]
        voltage = -(linkage[1] - linkage[0]) / (2*dt)
        assert_allclose(voltage / -ω, capture(case, angle), rtol=1e-6, atol=1e-9)


def test_the_worked_ring():
    case = Ring(sweep=(-1, 'sweep'))
    r = reading(case, TRIANGLE)
    assert round(r.linkage, 1) == 2.6
    assert round(r.capture, 1) == -1.9
    assert round(r.torque, 1) == -3.8
    assert round(r.voltage, 1) == -1.9
    assert r.shaft_power > 0                      # a motor, turning toward face-on


def test_edge_on_catches_the_whole_face_on_linkage():
    case = Ring()
    assert_allclose(abs(capture(case, EDGE_ON)), follow_flux(case, 0).linked, rtol=1e-12)
    assert_allclose(capture(case, 0), 0, atol=1e-12)


def test_a_turn_of_slivers_holds_the_area():
    """Half the mean square distance from the axis, over a turn."""
    case = replace(Ring(), samples_per_winding=2048)
    points = winding(case)[0]
    mean_square = np.mean(points[:, 0]**2 + points[:, 1]**2)
    assert_allclose(mean_square, 1 + .2**2/2, rtol=1e-12)
    assert_allclose(mean_square/2 * 2*np.pi, area_arrow(case)[2], rtol=1e-5)


def test_catch_closes_both_laws():
    assert q(1, 'catch * ampere').to('newton * meter / rad').magnitude == pytest.approx(1)
    assert q(1, 'catch * sweep').to('volt').magnitude == pytest.approx(1)
    assert q(1, 'newton * meter / rad / ampere').to('catch').magnitude == pytest.approx(1)
    assert q(1, 'volt * second / rad').to('catch').magnitude == pytest.approx(1)
