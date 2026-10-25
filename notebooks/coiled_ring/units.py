"""One boundary between named quantities and the numerical geometry."""

from pathlib import Path
from pint import UnitRegistry

registry = UnitRegistry(None)
registry.load_definitions(Path(__file__).with_name('units.txt'))
q = registry.Quantity


def number(amount, unit):
    value, source = amount
    return q(value, source).to(unit).magnitude



def field_number(amount):
    """Accept SI tesla or the explicit-angle book field."""
    from pint.errors import DimensionalityError
    value, source = amount
    field = q(value, source)
    try:
        return field.to('tesla').magnitude
    except DimensionalityError:
        return field.to('tesla * stroke').magnitude
