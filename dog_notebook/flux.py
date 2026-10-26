"""A charge's velocity, bent by flux.

Same shape as pendulum.py: givens, a state at a time, a picture.
Flux per sheet is a weber through each square meter of the page;
a positive number comes up out of the page.  Each mark on the
picture is one weber.
"""

from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

import numpy as np
from drawing import Canvas, COBALT, TEAL, RED, GRAY, save_movie

from ledger import number


@dataclass(frozen=True)
class ChargeInFlux:
    charge: tuple = (1, "coulomb")
    mass: tuple = (1, "lump")
    speed: tuple = (3, "cat")
    field: tuple = (5, "weber*stroke/sheet")
    duration: tuple = (6, "second")

    @cached_property
    def values(self):
        return dict(
            charge=float(number(self.charge, "coulomb")),
            mass=float(number(self.mass, "lump")),
            speed=float(number(self.speed, "cat")),
            field=float(number(self.field, "weber*stroke/sheet")),
            duration=float(number(self.duration, "second")),
        )

    @cached_property
    def bend(self):
        """How fast the velocity swings, in strokes a second.
        Positive is forward around; a positive charge in flux
        coming up out of the page swings back around."""
        p = self.values
        return -p['charge'] * p['field'] / p['mass']

    @cached_property
    def start(self):
        """Where the charge sets out, heading forward, so that its
        circle is centered on the picture."""
        if self.bend == 0:
            return np.array([0.0, 0.0])
        radius = self.values['speed'] / self.bend
        return np.array([0.0, -radius])


class State(NamedTuple):
    time: float            # second
    place: np.ndarray      # meter, from the picture's center
    velocity: np.ndarray   # cat
    push: np.ndarray       # push: the charge's velocity across the flux
    speed: float           # cat
    punch: float           # thump
    bend: float            # stroke a second, forward around


def state_at(case, time):
    p = case.values
    bend = case.bend
    heading = bend * time
    velocity = p['speed'] * np.array([np.cos(heading), np.sin(heading)])
    if bend == 0:
        place = case.start + velocity * time
    else:
        place = case.start + p['speed'] / bend * np.array(
            [np.sin(heading), 1 - np.cos(heading)])
    push = p['charge'] * p['field'] * np.array([velocity[1], -velocity[0]])
    punch = p['mass'] * p['speed'] ** 2 / 2
    return State(time, place, velocity, push, p['speed'], punch, bend)


MARK = "#a0a0a0"


def mark(canvas, center, coming_up):
    center = np.asarray(center)
    canvas.circle(center, 0.1, MARK)
    if coming_up:
        canvas.circle(center, 0.03, MARK, MARK)
    else:
        for direction in (np.array([1., 1.]), np.array([1., -1.])):
            canvas.line([center - 0.065 * direction, center + 0.065 * direction], MARK)


def marks(field, scale, width):
    """One mark per weber; return centers in scene coordinates."""
    if field == 0:
        return np.empty((0, 2))
    spacing = 1 / np.sqrt(abs(field))
    count = int(np.ceil(width / scale / 2 / spacing))
    rows = spacing * (np.arange(-count, count) + 0.5)
    return np.array([(x, y) for x in rows for y in rows]) * scale


def path(case, time, scale, points=120):
    begin = max(0.0, time - turn_time(case))
    times = np.linspace(begin, time, points)
    return np.array([state_at(case, t).place for t in times]) * scale


def turn_time(case):
    """Time for the velocity to swing all the way round."""
    return np.inf if case.bend == 0 else 2 * np.pi / abs(case.bend)


def picture(case, state, scale=6, width=10, canvas=None):
    """Draw one state, with scale in scene units per meter."""
    canvas = canvas if canvas is not None else Canvas(width=width)
    canvas.clear()
    for center in marks(case.values['field'], scale, width):
        mark(canvas, center, case.values['field'] > 0)
    if state.speed > 0:
        canvas.line(path(case, state.time, scale), GRAY)
    here = state.place * scale
    run = state.velocity * scale / 10
    added = state.push / case.values['mass'] * scale / 100
    canvas.circle(here, 0.22, COBALT, COBALT)
    canvas.line([here - (0.12, 0), here + (0.12, 0)], 'white', 3)
    if case.values['charge'] > 0:
        canvas.line([here - (0, 0.12), here + (0, 0.12)], 'white', 3)
    if case.values['charge'] == 0:
        canvas.circle(here, 0.08, 'white')
    canvas.arrow(here, here + run, TEAL)
    canvas.arrow(here, here + added, RED)
    return canvas.snapshot()


class View:
    def __init__(self, pixels=480, scale=6, width=10):
        self.scale = scale
        self.width = width
        self.camera = Canvas(pixels=pixels, width=width)

    def draw(self, case, state):
        return picture(case, state, self.scale, self.width, self.camera)

    def still(self, case, time=0):
        return self.draw(case, state_at(case, time))


def explore(case, view):
    """A picture, its quantities, and knobs, like the pendulum's."""
    import io
    from dataclasses import replace
    import ipywidgets as w
    from panels import panels

    current = case
    image = w.Image(format='png', width=440)
    readout = w.HTML()
    system = w.Dropdown(options=list(panels), value='dog', description='units')
    time = w.IntSlider(min=0, max=round(number(case.duration, 'second') * 100),
                       description='1/100 second')
    clock = w.Play(min=0, max=time.max, step=4, interval=40, description='Play')
    link = w.jslink((clock, 'value'), (time, 'value'))
    controls = dict(system=system, time=time, clock=clock)
    knobs = w.HBox()

    def show(change=None):
        state = state_at(current, time.value / 100)
        data = io.BytesIO()
        view.draw(current, state).save(data, 'PNG')
        image.value = data.getvalue()
        chosen = panels[system.value]

        def say(value, source, target):
            return f'{float(number((value, source), target)):.3g} {target}'

        sense = ('back around' if state.bend < 0 else
                 'forward around' if state.bend > 0 else 'straight on')
        radius = (say(state.speed / abs(state.bend), 'meter', chosen['length'])
                  if state.bend else 'none')
        readout.value = (
            f'<b>{state.time:.2f} second</b><br><br>'
            f"speed: {say(state.speed, 'cat', chosen['speed'])}<br>"
            f"punch: {say(state.punch, 'thump', chosen['energy'])}<br>"
            f"push: {say(np.hypot(*state.push), 'push', chosen['force'])}<br><br>"
            f'velocity sweeps at {abs(state.bend):.3g} strokes a second, {sense}<br>'
            f'circle radius: {radius}'
        )

    def set_out_again(change):
        nonlocal current
        clock.playing = False
        chosen = panels[system.value]
        current = replace(case, **{field: (controls[field].value, chosen[field])
                                   for field in ('charge', 'mass', 'speed', 'field')})
        time.value = 0
        show()

    def choose_units(change=None):
        chosen = panels[system.value]
        limits = dict(charge=(-5, 5, 1, 'coulomb'),
                      mass=(1, 8, 1, 'lump'),
                      speed=(1, 8, 1, 'cat'),
                      field=(-13, 13, 1, 'weber*stroke/sheet'))
        for field, (low, high, step, source) in limits.items():
            unit = chosen[field]
            knob = w.FloatSlider(
                value=float(number(getattr(current, field), unit)),
                min=float(number((low, source), unit)),
                max=float(number((high, source), unit)),
                step=float(number((step, source), unit)),
                description=f'{field} · {unit}',
                style=dict(description_width='150px'),
                continuous_update=False)
            knob.observe(set_out_again, names='value')
            controls[field] = knob
        knobs.children = (
            w.VBox([controls['charge'], controls['field']]),
            w.VBox([controls['speed'], controls['mass']]),
        )
        show()

    time.observe(show, names='value')
    system.observe(choose_units, names='value')
    choose_units()
    panel = w.VBox([
        w.HBox([image, readout]), w.HBox([clock, time]), system, knobs,
        w.HTML('Each mark is a weber. A knob sets the charge off again; units keep the instant.'),
    ])
    panel.controls = controls
    panel.readout = readout
    panel.time_link = link
    return panel


def movie(case, seconds=3, folder="movies", scale=6):
    return save_movie(case, View(scale=scale), seconds, folder, 'bending')
