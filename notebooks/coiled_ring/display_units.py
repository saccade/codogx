"""Selectable display units. Numerical models always receive SI magnitudes. Codex."""

import math
import ipywidgets as w

# Values are SI magnitudes of one displayed unit. Book units are opt-in.
UNITS = {
    'length': {'m': 1., 'cm': .01, 'hand': .1, 'ft': .3048},
    'angle': {'rad': 1., 'deg': math.pi/180, 'turn': math.tau, 'stroke': 1.},
    'sweep': {'rad/s': 1., 'rpm': math.tau/60, 'sweep': 1.},
    'pickup': {'rad/s²': 1., 'pickup': 1.},
    'current': {'A': 1., 'mA': .001},
    'charge': {'C': 1., 'mC': .001},
    'time': {'s': 1., 'ms': .001},
    'inertia': {'kg·m²': 1., 'g·m²': .001, 'wheel': 1., 'mw': .001},
    'spin': {'N·m·s': 1., 'mN·m·s': .001, 'roll': 1.},
    'torque': {'N·m': 1., 'mN·m': .001, 'crank': 1.},
    'flux': {'Wb': 1., 'mWb': .001},
    'capture': {'Wb/rad': 1., 'mWb/rad': .001, 'catch': 1.},
    'voltage': {'V': 1., 'mV': .001},
    'climb': {'V/s': 1., 'mV/s': .001},
    'force': {'N': 1., 'mN': .001, 'push': 1.},
    'energy': {'J': 1., 'mJ': .001, 'thump': 1.},
    'power': {'W': 1., 'mW': .001, 'pow': 1.},
}
SI_UNITS = {kind: next(iter(options)) for kind, options in UNITS.items()}


def selection(overrides=None):
    chosen = dict(SI_UNITS)
    chosen.update(overrides or {})
    for kind, unit in chosen.items():
        if kind not in UNITS or unit not in UNITS[kind]:
            raise ValueError(f'Unknown {kind} unit: {unit}')
    return chosen


def scaled(value, kind, units=None):
    chosen = selection(units)
    return value / UNITS[kind][chosen[kind]]


def words(value, kind, units=None, figures=4):
    chosen = selection(units)
    number = scaled(value, kind, chosen)
    number = 0. if abs(number) < 1e-10 else number
    return f'{number:.{figures}g} {chosen[kind]}'


class UnitPicker:
    def __init__(self, kinds, defaults=None):
        self.units = selection(defaults)
        self.callbacks = []
        self.selectors = {}
        for kind in dict.fromkeys(kinds):
            control = w.Dropdown(options=list(UNITS[kind]), value=self.units[kind],
                                 description=kind, style={'description_width': '80px'},
                                 layout=w.Layout(width='235px'))
            control.observe(lambda change, kind=kind: self._changed(kind, change), names='value')
            self.selectors[kind] = control
        self.widget = w.Accordion(children=[w.GridBox(
            list(self.selectors.values()), layout=w.Layout(
                grid_template_columns='repeat(3, 235px)', grid_gap='4px'))])
        self.widget.set_title(0, 'Units — SI by default; change without changing the apparatus')
        self.widget.selected_index = None

    def _changed(self, kind, change):
        previous = self.units[kind]
        self.units[kind] = change['new']
        for callback in tuple(self.callbacks):
            callback(kind, previous, change['new'])

    def on_change(self, callback):
        self.callbacks.append(callback)

    def value(self, value, kind):
        return scaled(value, kind, self.units)

    def label(self, name, kind):
        return f'{name} ({self.units[kind]})'


class QuantitySlider:
    """A slider whose displayed value changes units while its SI value stays put."""
    def __init__(self, picker, kind, name, value, minimum, maximum, step):
        self.picker, self.kind, self.name = picker, kind, name
        self.bounds = minimum, maximum, step
        self.changing_units = False
        factor = UNITS[kind][picker.units[kind]]
        self.slider = w.FloatSlider(value=value/factor, min=minimum/factor,
                                    max=maximum/factor, step=step/factor,
                                    description=picker.label(name, kind),
                                    continuous_update=False, readout_format='.4g',
                                    style={'description_width': '150px'},
                                    layout=w.Layout(width='430px'))
        picker.on_change(self._units_changed)

    @property
    def si(self):
        return self.slider.value * UNITS[self.kind][self.picker.units[self.kind]]

    def set_si(self, value):
        self.slider.value = value / UNITS[self.kind][self.picker.units[self.kind]]

    def observe(self, callback):
        self.slider.observe(lambda change: None if self.changing_units else callback(change),
                            names='value')

    def _units_changed(self, kind, old, new):
        if kind != self.kind:
            return
        value = self.slider.value * UNITS[kind][old]
        factor = UNITS[kind][new]
        lo, hi, step = (x/factor for x in self.bounds)
        self.changing_units = True
        try:
            self.slider.min = min(self.slider.min, lo)
            self.slider.max = max(self.slider.max, hi)
            self.slider.value = value/factor
            self.slider.min, self.slider.max, self.slider.step = lo, hi, step
            self.slider.description = self.picker.label(self.name, kind)
        finally:
            self.changing_units = False
