"""Book units, and the four-count view used by Claude's mechanical tests."""

from fractions import Fraction as F
from pathlib import Path

from pint import UnitRegistry

registry = UnitRegistry(non_int_type=F, on_redefinition='ignore')
registry.load_definitions(Path(__file__).with_name("book_units.txt"))


def step(lump=0, meter=0, second=0, stroke=0):
    return lump, meter, second, stroke


def at(a, b): return tuple(x + y for x, y in zip(a, b))
def on(a, b): return tuple(x - y for x, y in zip(a, b))
def crossed(a, b): return on(at(a, b), stroke)     # a cross takes a stroke away


def counts(unit):
    powers = registry.Unit(unit).dimensionality
    return tuple(powers.get(f'[{base}]', 0)
                 for base in ('mass', 'length', 'time', 'swing'))


catalog = """lump meter second stroke lever hand sheet card cat dog zoom
oompf push thump pow sweep pickup ponder wheel roll crank grunt zip zing
zump swirl twirl shift transit""".split()

units = {name: counts(name) for name in catalog}
one = step()
lump, meter, second, stroke, lever = (
    units[name] for name in ('lump', 'meter', 'second', 'stroke', 'lever')
)
per_second = on(one, second)


def number(amount, unit):
    value, source = amount
    return registry.Quantity(value, source).to(unit).magnitude


def name(v):
    return [key for key, unit in units.items() if unit == v] or ['?']
