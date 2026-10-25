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
from manim import Camera, VGroup, Line, Circle, Dot, Arrow, VMobject
from manim import WHITE, GRAY, TEAL_D, RED_D, LIGHT_GRAY, UP, RIGHT

from ledger import number
from pendulum import COBALT


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


def flat(point):
    return point[0] * RIGHT + point[1] * UP


MARK = "#a0a0a0"


def mark(center, coming_up):
    ring = Circle(radius=0.1, color=MARK, stroke_width=2).move_to(center)
    if coming_up:                                   # up out of the page: a dot
        return VGroup(ring, Dot(center, radius=0.03, color=MARK))
    d = 0.065                                       # down into the page: a cross
    return VGroup(ring,
                  Line(center + d * (UP + RIGHT), center - d * (UP + RIGHT), color=MARK, stroke_width=2),
                  Line(center + d * (UP - RIGHT), center - d * (UP - RIGHT), color=MARK, stroke_width=2))


def marks(field, scale, width):
    """One mark per weber.  Flux per sheet is an axis arrow and carries a stroke;
    the sheet it goes through is a meter crossed with a meter, which takes the
    stroke away again, so 5 weber*stroke/sheet puts 5 marks on each sheet."""
    if field == 0:                                  # no flux, nothing to mark
        return VGroup()
    spacing = 1 / np.sqrt(abs(field))               # meter between marks
    count = int(np.ceil(width / scale / 2 / spacing))
    rows = spacing * (np.arange(-count, count) + 0.5)
    return VGroup(*[mark(flat((x, y)) * scale, field > 0) for x in rows for y in rows])


def path(case, time, scale, points=120):
    begin = max(0.0, time - turn_time(case))
    times = np.linspace(begin, time, points)
    line = VMobject(color=GRAY, stroke_width=2)
    line.set_points_as_corners([flat(state_at(case, t).place) * scale for t in times])
    return line


def turn_time(case):
    """Time for the velocity to swing all the way round."""
    return np.inf if case.bend == 0 else 2 * np.pi / abs(case.bend)


def sign(center, positive):
    d = 0.12
    bars = [Line(center - d * RIGHT, center + d * RIGHT, color=WHITE, stroke_width=3)]
    if positive:
        bars.append(Line(center - d * UP, center + d * UP, color=WHITE, stroke_width=3))
    return bars


def picture(case, state, scale=6, width=10):
    """Draw one state, with scale in scene units per meter."""
    here = flat(state.place) * scale
    run = flat(state.velocity) * scale / 10                        # a tenth of a second's run
    added = flat(state.push) / case.values['mass'] * scale / 100   # run added in a tenth of a second
    shown = [marks(case.values['field'], scale, width)]
    if state.speed > 0:
        shown.append(path(case, state.time, scale))
    shown += [
        Circle(radius=0.22, color=COBALT, fill_opacity=1).move_to(here),
        *sign(here, case.values['charge'] >= 0),
        Arrow(here, here + run, buff=0, color=TEAL_D),
        Arrow(here, here + added, buff=0, color=RED_D),
    ]
    return VGroup(*shown)


class View:
    def __init__(self, pixels=480, scale=6, width=10):
        self.scale = scale
        self.width = width
        self.camera = Camera(pixel_width=pixels, pixel_height=pixels,
                             frame_width=width, frame_height=width,
                             background_color=WHITE)

    def draw(self, case, state):
        self.camera.reset()
        self.camera.capture_mobjects([picture(case, state, self.scale, self.width)])
        return self.camera.get_image().copy()

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
    from manim import Scene, ValueTracker, always_redraw, linear, tempconfig

    class Bending(Scene):
        def construct(self):
            clock = ValueTracker(0)
            self.add(always_redraw(lambda: picture(
                case, state_at(case, clock.get_value()), scale)))
            self.play(clock.animate.set_value(seconds),
                      run_time=seconds, rate_func=linear)

    settings = dict(pixel_width=480, pixel_height=480, frame_rate=25,
                    frame_width=10, frame_height=10, format="mp4",
                    background_color=WHITE, media_dir=folder,
                    verbosity="WARNING", progress_bar="none",
                    output_file="bending")
    with tempconfig(settings):
        scene = Bending()
        scene.render()
        return str(scene.renderer.file_writer.movie_file_path)
