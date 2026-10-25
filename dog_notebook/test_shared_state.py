from dataclasses import replace
from fractions import Fraction

import numpy as np
import pytest
from pint import DimensionalityError

from ledger import number
from pendulum import Pendulum, View, state_at, picture


def test_unit_scales_are_exact():
    assert number((5, 'hand'), 'meter') == Fraction(1, 2)
    assert number((1, 'dog'), 'cat') == 10
    assert number((1, 'dog/second'), 'hand/second²') == 100


def test_a_quantity_mismatch_is_exposed():
    with pytest.raises(DimensionalityError):
        number((1, 'lump'), 'meter')


def test_equivalent_units_make_the_same_swing():
    hands = Pendulum(length=(10, 'hand'))
    meters = replace(hands, length=(1, 'meter'))
    np.testing.assert_allclose(state_at(hands, 0.7), state_at(meters, 0.7))


def test_scrubbing_reuses_one_trajectory():
    case = Pendulum()
    first = state_at(case, 1.5)
    trajectory = case.trajectory
    evaluations = trajectory.nfev
    state_at(case, 0.2)
    assert state_at(case, 1.5) == first
    assert case.trajectory is trajectory
    assert trajectory.nfev == evaluations


def test_mass_changes_energy_and_keeps_the_motion():
    light = state_at(Pendulum(mass=(1, 'lump')), 0.4)
    heavy = state_at(Pendulum(mass=(2, 'lump')), 0.4)
    assert heavy.angle == light.angle
    assert heavy.sweep == light.sweep
    assert heavy.heft == 2 * light.heft
    assert heavy.hook == 2 * light.hook


def test_energy_stays_with_the_pendulum():
    case = Pendulum(release=(1.2, 'stroke'))
    initial = state_at(case, 0)
    energies = [sum(state_at(case, t)[3:]) for t in np.linspace(0, 6, 101)]
    np.testing.assert_allclose(energies, initial.heft, rtol=1e-8)


def test_book_gravity_sets_the_period():
    case = Pendulum(release=(0.001, 'stroke'))
    quarter_period = np.pi / (2 * np.sqrt(10))
    assert abs(state_at(case, quarter_period).angle) < 1e-9
    slower = replace(case, gravity=(0.25, 'dog/second'))
    assert abs(state_at(slower, 2 * quarter_period).angle) < 1e-9


def test_zoom_changes_the_picture_and_keeps_the_state():
    case = Pendulum()
    state = state_at(case, 0.4)
    small = picture(case, state, scale=4)
    large = picture(case, state, scale=6)
    assert large[2].get_length() == pytest.approx(1.5 * small[2].get_length())
    assert state_at(case, 0.4) == state


def test_a_still_owns_its_pixels_and_the_camera_is_reused():
    case = Pendulum()
    view = View(pixels=240)
    camera = view.camera
    first = view.still(case, 0)
    saved = np.array(first)
    view.still(case, 0.5)
    assert view.camera is camera
    np.testing.assert_array_equal(first, saved)
    reference = View(pixels=240).still(case, 0)
    np.testing.assert_array_equal(view.still(case, 0), reference)
