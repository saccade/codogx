"""Posited: every cross takes a stroke away, and axis arrows carry one."""

import pytest
from pint import DimensionalityError

from ledger import units as u, at, crossed, lump, meter, registry

q = registry.Quantity


def test_crossing_with_a_meter_is_putting_at_a_lever():
    for unit in u.values():
        assert crossed(meter, unit) == at(u['lever'], unit)


def test_a_meter_crossed_with_a_push_cranks():
    assert crossed(meter, u['push']) == u['crank']


def test_a_sweep_crossed_with_a_meter_runs():
    assert crossed(u['sweep'], meter) == u['cat']


def test_a_sweep_crossed_with_a_run_speeds_up():
    assert crossed(u['sweep'], u['cat']) == u['zoom']


def test_the_blank_cell_is_the_pull_that_keeps_a_ponder_going_round():
    assert crossed(u['sweep'], crossed(u['sweep'], at(lump, meter))) == u['push']


def cross(a, b):
    return a * b / q(1, 'stroke')


def test_charge_velocity_across_flux_pushes():
    v, B = q(3, 'cat'), q(5, 'weber*stroke/sheet')
    assert (q(1, 'coulomb') * cross(v, B)).to('push').magnitude == 15


@pytest.mark.parametrize('strokes', [0, 2])
def test_only_one_stroke_makes_a_push(strokes):
    B = q(5, f'weber*stroke**{strokes}/sheet')
    with pytest.raises(DimensionalityError):
        (q(1, 'coulomb') * cross(q(3, 'cat'), B)).to('push')


def test_charge_field_over_mass_is_a_sweep():
    bend = q(1, 'coulomb') * q(5, 'weber*stroke/sheet') / q(1, 'lump')
    assert bend.to('sweep').magnitude == 5


def test_the_flux_through_a_sheet_is_in_webers():
    area = cross(q(1, 'meter'), q(1, 'meter'))           # a meter crossed with a meter
    assert (q(5, 'weber*stroke/sheet') * area).to('weber').magnitude == 5
