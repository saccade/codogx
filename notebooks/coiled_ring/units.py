"""One boundary between named quantities and the numerical geometry."""

from pathlib import Path
from pint import UnitRegistry

registry = UnitRegistry(None)
registry.load_definitions(Path(__file__).with_name('units.txt'))
q = registry.Quantity


def number(amount, unit):
    value, source = amount
    return q(value, source).to(unit).magnitude
