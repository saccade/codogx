"""Small physical checks for two independent accounts. Codex."""

from dataclasses import replace

import numpy as np
import pytest
from pint import DimensionalityError
from numpy.testing import assert_allclose

from ring import (Ring, add_forces, follow_flux, area_arrow, state_at, rotate,
                  winding, shadow_areas, shaft, torque_about_shaft, across_shaft)
from units import q


@pytest.mark.parametrize('n', [2, 5, 25, 36])
def test_both_accounts_for_several_orientations(n):
    case = Ring(windings=n)
    for heading in [0, .4, 2.1]:
        case = replace(case, heading=(heading, 'stroke'))
        for angle in [0, .3, np.pi/2, 2.8, 4.7]:
            force, flux = add_forces(case, angle), follow_flux(case, angle)
            assert_allclose(force.moment, flux.moment, rtol=1e-5, atol=2e-8)
            assert_allclose(force.net, 0, atol=2e-12)


def test_signed_shadows_have_the_known_area():
    case = Ring()
    expected = np.pi*(1**2 + .2**2/2)
    assert_allclose(area_arrow(case), [0, 0, expected], atol=2e-5)


def test_refining_the_wire_reduces_the_difference():
    errors = []
    for pieces in [16, 32, 64, 128]:
        state = state_at(Ring(samples_per_winding=pieces), .7)
        errors.append(np.linalg.norm(state.forces.moment-state.flux.moment))
    assert np.all(np.diff(errors) < 0)
    assert errors[-1] < errors[0]/50


def test_flux_work_matches_local_force_work():
    case, angle = Ring(heading=(.7, 'stroke')), .6
    force = add_forces(case, angle)
    delta = 1e-5
    before = follow_flux(case, angle-delta).linked
    after = follow_flux(case, angle+delta).linked
    flux_work = case.values['current']*(after-before)
    force_work = torque_about_shaft(case, force.moment)*(2*delta)
    assert_allclose(flux_work, force_work, rtol=1e-5)


def test_translation_keeps_the_flux():
    case = Ring()
    points = winding(case)[0]
    assert_allclose(shadow_areas(points+[5,-3,2]), shadow_areas(points), atol=1e-12)


def test_current_reversal_and_zero_current():
    case = Ring()
    for account in [add_forces, follow_flux]:
        plus = account(case, .8).moment
        minus = account(replace(case, current=(-2, 'ampere')), .8).moment
        zero = account(replace(case, current=(0, 'ampere')), .8).moment
        assert_allclose(minus, -plus, atol=1e-12)
        assert_allclose(zero, 0, atol=1e-12)


def test_the_extra_windings_do_not_multiply_the_external_moment():
    first = state_at(Ring(windings=25), .6)
    second = state_at(Ring(windings=36), .6)
    assert_allclose(first.forces.moment, second.forces.moment, atol=1e-11)
    assert_allclose(first.flux.linked, second.flux.linked, rtol=1e-7)


def test_three_four_five_and_the_turn_back():
    case = Ring()
    angle = np.arccos(4/5)
    face_on = follow_flux(case, 0).linked
    state = state_at(case, angle)
    assert_allclose(state.flux.linked, .8*face_on, atol=1e-12)
    assert_allclose(torque_about_shaft(case, state.flux.moment),
                    -.6*case.values['current']*face_on, rtol=1e-9)
    home = state_at(case, 2*np.pi)
    assert_allclose(home.flux.linked, face_on, atol=1e-12)
    assert_allclose(home.flux.moment, 0, atol=1e-9)


def test_foot_and_hand_describe_the_same_ring():
    hands = Ring()
    feet = replace(hands, radius=(1/.3048, 'foot'), tube=(.2/.0254, 'inch'))
    assert_allclose(state_at(hands, .7).forces.moment,
                    state_at(feet, .7).forces.moment, atol=1e-11)


def test_stroke_stays_in_the_work_balance():
    assert q(2, 'ampere')*q(3, 'weber') == q(6, 'thump')
    assert (q(6, 'thump')/q(2, 'stroke')).to('crank').magnitude == 3
    assert (q(1, 'tesla * stroke')*q(2, 'sheet')/q(1, 'stroke')).to('weber').magnitude == 2
    with pytest.raises(DimensionalityError):
        q(1, 'crank').to('thump')


def test_flat_ring_has_the_familiar_moment():
    case = Ring(tube=(0, 'hand'), radius=(10, 'hand'))
    state = state_at(case, np.pi/2)
    assert_allclose(state.forces.moment, [0, -2*np.pi, 0], atol=1e-11)
    assert_allclose(state.flux.moment, [0, -2*np.pi, 0], rtol=1e-6)


def test_camera_frames_belong_to_their_call():
    from view import RingView
    view, case = RingView(pixels=400), Ring()
    first = view.still(case, .3)
    before = np.array(first).copy()
    view.still(case, 1.2)
    assert_allclose(np.array(first), before)
    assert_allclose(np.array(view.still(case, .3)), before)


def test_controls_keep_the_pose_and_update_both_accounts():
    from panel import explore
    from view import RingView
    panel = explore(Ring(), RingView(pixels=400))
    c = panel.controls
    assert c['angle'].value == np.arccos(4/5)
    c['triangle'].click()
    angle = c['angle'].value
    c['windings'].value = 36
    assert c['angle'].value == angle
    assert 'N·m' in panel.comparison.value
    c['current'].value = 0
    assert '0 N·m' in panel.comparison.value
    c['heading'].value = 1
    c['edge'].click()
    assert c['angle'].value == np.pi/2
    c['play'].value = 400
    assert c['angle'].value == .4


def test_flux_responds_to_world_axis_turns():
    case = Ring(heading=(.8, 'stroke'))
    state = state_at(case, .9)
    assert abs(state.flux.moment[0]) > .1
    assert abs(state.flux.moment[1]) > .1
    assert_allclose(np.dot(state.flux.moment, shaft(case)),
                    torque_about_shaft(case, state.forces.moment), rtol=1e-5)


def test_heading_changes_world_components_and_keeps_moment_about_shaft():
    for heading in [0, .8, 2.1]:
        case = Ring(heading=(heading, 'stroke'))
        state = state_at(case, .9)
        assert_allclose(across_shaft(case, state.forces.moment), 0, atol=1e-10)
        assert_allclose(across_shaft(case, state.flux.moment), 0, atol=1e-8)


def test_torque_readings_give_a_size_and_sense_on_both_sides():
    from comparison import torque_reading, flux_reading
    case = Ring()
    for angle in [.6, 2*np.pi-.6]:
        moment = add_forces(case, angle).moment
        words = torque_reading(case, torque_about_shaft(case, moment), 'crank')
        assert 'back toward alignment' in words
        assert words[0].isdigit()
        assert '-' not in words
        reversed_case = replace(case, current=(-2, 'ampere'))
        reversed_words = torque_reading(reversed_case, torque_about_shaft(reversed_case, -moment), 'crank')
        assert 'toward opposite alignment' in reversed_words
    assert flux_reading(-3.2) == '3.2 weber in the reverse sense'


def test_sweep_torque_matches_the_shaft_part_of_the_total_moment():
    for heading in [0, .8, 2.1]:
        case = Ring(heading=(heading, 'stroke'))
        for angle in [.3, 1.5, 3.9]:
            flux = follow_flux(case, angle)
            assert_allclose(flux.torque, torque_about_shaft(case, flux.moment), atol=1e-12)

