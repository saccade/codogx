"""Unit choices must change presentation, never the physical state."""
import numpy as np
from numpy.testing import assert_allclose
from ring import Ring
from panel import explore
from view import RingView
from capture_view import CaptureView,explore_capture


def test_both_existing_panels_start_si_and_survive_unit_round_trips():
    for panel in [explore(Ring(),RingView(pixels=400)),
                  explore_capture(Ring(),CaptureView(pixels=400))]:
        c=panel.controls;u=c['units']
        assert u['length'].value=='m'
        assert u['torque'].value=='N·m'
        assert u['angle'].value=='rad'
        assert u['current'].value=='A'
        original_angle=c['angle'].value
        u['length'].value='hand'
        assert_allclose(c['tube'].value,2.)
        u['current'].value='mA'
        assert_allclose(c['current'].value,2000.)
        u['angle'].value='turn'
        assert_allclose(c['angle'].value,original_angle/(2*np.pi))
        u['angle'].value='rad';u['length'].value='m';u['current'].value='A'
        assert_allclose(c['angle'].value,original_angle)
        assert_allclose(c['tube'].value,.2)
        assert_allclose(c['current'].value,2.)


def test_book_inputs_are_explicit_and_equivalent_to_si():
    si=Ring()
    book=Ring(radius=(10,'hand'),tube=(2,'hand'),field=(1,'tesla * stroke'),
              sweep=(1,'sweep'),heading=(0,'stroke'))
    assert si.radius==(1,'meter')
    assert si.field==(1,'tesla')
    assert si.values==book.values
