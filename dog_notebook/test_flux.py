from dataclasses import replace

import numpy as np
import pytest

from flux import ChargeInFlux, View, explore, marks, state_at

case = ChargeInFlux()                    # 1 coulomb, 1 lump, 3 cat, 5 weber*stroke/sheet
times = (0, 0.3, 0.7, 1.9, 5.2)


def test_the_bend_keeps_the_speed_and_the_punch():
    for t in times:
        s = state_at(case, t)
        assert np.hypot(*s.velocity) == pytest.approx(3)
        assert s.punch == pytest.approx(9 / 2)


def test_the_push_is_square_to_the_velocity():
    for t in times:
        s = state_at(case, t)
        assert np.dot(s.push, s.velocity) == pytest.approx(0, abs=1e-12)
        assert np.hypot(*s.push) == pytest.approx(15)      # coulomb, cat, weber*stroke/sheet, crossed


def test_the_circle_has_the_radius_mass_speed_over_charge_field():
    for t in times:
        assert np.hypot(*state_at(case, t).place) == pytest.approx(3 / 5)


def test_senses():
    assert state_at(case, 0).bend == -5                               # back around
    assert state_at(replace(case, charge=(-1, 'coulomb')), 0).bend == 5
    assert state_at(replace(case, field=(-5, 'weber*stroke/sheet')), 0).bend == 5


def test_no_flux_goes_straight_on():
    s = state_at(replace(case, field=(0, 'weber*stroke/sheet')), 2)
    np.testing.assert_allclose(s.place, (6, 0))


def test_the_same_case_in_other_units():
    si = replace(case, speed=(3, 'meter/second'), field=(5, 'tesla*stroke'), mass=(1, 'kilogram'))
    for a, b in zip(state_at(case, 0.7), state_at(si, 0.7)):
        np.testing.assert_allclose(a, b)


def test_scrubbing_order_does_not_matter():
    first = state_at(case, 1.5)
    state_at(case, 0.2)
    np.testing.assert_array_equal(state_at(case, 1.5).place, first.place)


def test_one_mark_per_weber():
    for field in (2, 5, 13):
        group = marks(field, scale=1, width=4)
        spacing = 1 / np.sqrt(field)
        side = np.sqrt(len(group)) * spacing             # meters of page the marks cover
        assert len(group) / side**2 == pytest.approx(field)


def test_stills_are_separate_snapshots():
    view = View(pixels=160)
    first = view.still(case, 0.3)
    kept = first.tobytes()
    view.still(case, 1.1)
    assert first.tobytes() == kept and first.size == (160, 160)


def test_a_knob_sets_out_again_and_units_keep_the_instant():
    panel = explore(case, View(pixels=160))
    knobs = panel.controls
    knobs['time'].value = 40
    knobs['system'].value = 'SI'
    assert knobs['time'].value == 40
    assert '4.5 joule' in panel.readout.value
    knobs['field'].value = -5
    assert knobs['time'].value == 0
    assert 'forward around' in panel.readout.value
