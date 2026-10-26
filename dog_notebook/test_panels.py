from dataclasses import replace

import numpy as np
import pytest
from pint import DimensionalityError

from explore import explore
from ledger import number, registry
from panels import panels
from pendulum import Pendulum, View, state_at


def test_strokes_keep_crank_and_thump_distinct():
    q = registry.Quantity
    assert (q(1, 'crank') * q(1, 'stroke')).to('thump').magnitude == 1
    assert (q(2, 'lump') * q(5, 'hand') / q(1, 'stroke')).to('ponder').magnitude == 1
    with pytest.raises(DimensionalityError):
        q(1, 'crank').to('thump')


def test_imperial_inputs_give_the_same_physical_state():
    metric = Pendulum()
    imperial = replace(metric,
        length=(number(metric.length, 'foot'), 'foot'),
        mass=(number(metric.mass, 'pound'), 'pound'),
        gravity=(number(metric.gravity, 'foot/second**2'), 'foot/second**2'))
    np.testing.assert_allclose(state_at(metric, 0.7), state_at(imperial, 0.7))


def test_physical_knobs_release_again_and_zoom_keeps_time():
    panel = explore(Pendulum(), View(pixels=160))
    knobs = panel.controls
    knobs['time'].value = 50
    knobs['zoom'].value = 5
    assert knobs['time'].value == 50
    knobs['mass'].value = 2
    assert knobs['time'].value == 0
    assert '3.493 thump' in panel.readout.value


def test_unit_panel_changes_keep_the_instant_and_energy():
    panel = explore(Pendulum(), View(pixels=160))
    knobs = panel.controls
    knobs['time'].value = 50
    knobs['system'].value = 'SI'
    assert knobs['time'].value == 50
    assert knobs['length'].value == 1
    assert '1.747 joule' in panel.readout.value
    knobs['system'].value = 'imperial'
    assert knobs['time'].value == 50
    assert knobs['length'].value == pytest.approx(1 / 0.3048)
    assert '1.288 foot*pound_force' in panel.readout.value


def test_a_reader_can_add_a_panel():
    panels['bench'] = dict(panels['imperial'], length='inch')
    panel = explore(Pendulum(), View(pixels=160))
    panel.controls['system'].value = 'bench'
    assert panel.controls['length'].value == pytest.approx(1 / 0.0254)
    del panels['bench']
