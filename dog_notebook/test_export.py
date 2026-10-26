"""Portable exports use the live drawing and preserve a visible time sequence."""

import numpy as np
import pytest
from PIL import Image

import flux
import pendulum


@pytest.mark.parametrize('module,case', [
    (pendulum, pendulum.Pendulum()),
    (flux, flux.ChargeInFlux()),
])
def test_movie_is_a_moving_gif(module, case, tmp_path):
    path = module.movie(case, seconds=0.2, folder=tmp_path)
    with Image.open(path) as image:
        assert image.format == 'GIF'
        assert image.size == (480, 480)
        assert image.n_frames == 5
        assert image.info['loop'] == 0
        assert image.info['duration'] == 40
        first = np.array(image.convert('RGB'))
        image.seek(4)
        assert np.any(np.array(image.convert('RGB')) != first)


def test_zero_field_and_zero_speed_draw_with_zero_arrows():
    case = flux.ChargeInFlux(field=(0, 'weber*stroke/sheet'), speed=(0, 'cat'))
    view = flux.View(pixels=160)
    first = view.still(case, 0)
    np.testing.assert_array_equal(view.still(case, 4), first)


def test_field_marks_show_the_field_direction():
    from dataclasses import replace

    case = flux.ChargeInFlux(speed=(0, 'cat'))
    view = flux.View(pixels=160)
    up = np.array(view.still(case))
    down = np.array(view.still(replace(case, field=(-5, 'weber*stroke/sheet'))))
    assert np.any(up != down)
