"""Where flux comes from: two wires, with every cross taking a stroke away."""

import numpy as np
import pytest

from ledger import registry

q = registry.Quantity
stroke = q(1, 'stroke')
turn = q(2 * np.pi, 'stroke')          # the book's turn; pint's own 'turn' has no stroke


def cross(a, b):
    return a * b / stroke


# The force between two bits of current: two crosses, so the constant carries two strokes.
k = q(1e-7, 'newton*stroke**2/ampere**2')


def field_of_a_long_wire(current, distance):
    # Biot-Savart: k I (dl crossed with r) / r**2, summed along the wire, comes to 2 k I / d
    return cross(2 * k * current, 1 / distance)


def test_a_wire_makes_flux_per_sheet_with_one_stroke():
    B = field_of_a_long_wire(q(1, 'ampere'), q(1, 'meter'))
    assert B.to('weber*stroke/sheet').magnitude == pytest.approx(2e-7)


def test_two_wires_push_the_measured_amount():
    B = field_of_a_long_wire(q(1, 'ampere'), q(1, 'meter'))
    force = cross(q(1, 'ampere') * q(1, 'meter'), B)
    assert force.to('newton').magnitude == pytest.approx(2e-7)


def test_ampere_around_the_wire_gives_mu_zero_as_two_turns_of_k():
    d, current = q(1, 'meter'), q(1, 'ampere')
    circumference = cross(turn, d)                   # the turn crossed with the radius
    mu0 = field_of_a_long_wire(current, d) * circumference / current
    assert (mu0 / cross(2 * turn, k / stroke)).to('').magnitude == pytest.approx(1)
    assert mu0.to('newton*stroke/ampere**2').magnitude == pytest.approx(4 * np.pi * 1e-7)


# The electric side: Coulomb's law has a 4 pi and no cross.

two_turns = 2 * turn
light = q(299792458, 'meter/second')


def mu0():
    return two_turns * k / stroke**2                  # as Ampere's loop gives it


def eps0():
    return 1 / (mu0() * light**2)                     # mu0 times eps0 is one on light's speed squared


def coulomb_push(four_pi):
    return q(1, 'coulomb') ** 2 / (four_pi * eps0() * q(1, 'meter') ** 2)


def test_eps0_carries_minus_a_stroke():
    assert eps0().dimensionality['[swing]'] == -1


def test_coulomb_pushes_when_4_pi_is_two_turns():
    assert coulomb_push(two_turns).to('newton').magnitude == pytest.approx(8.9875517873681764e9)


def test_coulomb_is_not_a_push_when_4_pi_is_a_plain_number():
    from pint import DimensionalityError
    with pytest.raises(DimensionalityError):
        coulomb_push(4 * np.pi).to('newton')
