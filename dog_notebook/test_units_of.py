import pytest
from sympy import symbols, Rational, sqrt
from ledger import units as u
from units_of import units_of, kind

eta, omega, chi, theta, K = symbols('eta omega chi theta K')
kind.update({eta: u['wheel'], omega: u['sweep'], chi: u['crank'],
             theta: (0, 0, 0, 1), K: u['thump']})

def test_spin():
    assert units_of(eta * omega) == u['roll']

def test_hook_with_a_half():
    assert units_of(Rational(1, 2) * eta * omega**2) == u['thump']

def test_grunt_adds_to_hook():
    assert units_of(chi * theta + eta * omega**2) == u['thump']

def test_crank_does_not_add_to_hook():
    with pytest.raises(AssertionError):
        units_of(chi + K)

def test_root():
    assert units_of(sqrt(K / eta)) == u['sweep']
