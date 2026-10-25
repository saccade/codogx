"""Linkage and capture over a turn of the shaft, drawn with Manim. Claude.

The angle counts the ring's way: from face-on, turning about the shaft.
Positive capture catches linked flux turning that way; negative releases it.
"""

import io
from dataclasses import replace
from typing import NamedTuple

import ipywidgets as w
import numpy as np
from manim import Camera, VGroup, VMobject, Line, Dot, DashedLine

from ring import capture, follow_flux, winding, pose
from view import (PAPER, INK, COPPER, FORCE, FLUX, GHOST, label, project,
                  field_arrows, ring_figure)

TURN = 2*np.pi
FACE_ON, EDGE_ON, TRIANGLE = 0.0, TURN/4, np.arccos(4/5)


class Reading(NamedTuple):
    linkage: float        # weber
    capture: float        # catch, weber per radian
    torque: float         # newton meter about the shaft: the capture of the current
    voltage: float        # volt: the opposite of the capture of the sweep
    shaft_power: float    # watt, torque at sweep
    circuit_power: float  # watt, voltage of the current


def reading(case, angle):
    flux = follow_flux(case, angle)
    kappa = capture(case, angle)
    voltage = -kappa * case.values['sweep']
    return Reading(flux.linked, kappa, flux.torque, voltage,
                   flux.torque * case.values['sweep'],
                   voltage * case.values['current'])


def signed(value, figures=2):
    value = 0.0 if abs(value) < 5e-10 else value
    return f'{value:+.{figures}g}'.replace('-', '−') if value else '0'


def size(value):
    return f'{abs(value):.2g}'


def sentences(case, r):
    """The readings, said with their senses (a minus is the opposite of)."""
    if abs(r.capture) < 1e-9:
        caught = '0 catch: a small turn neither catches nor releases'
    elif r.capture > 0:
        caught = f'{size(r.capture)} catch: each radian the ring’s way catches {size(r.capture)} Wb'
    else:
        caught = (f'{signed(r.capture)} catch: each radian the ring’s way '
                  f'releases {size(r.capture)} Wb')
    if abs(r.torque) < 1e-9:
        turning = '0 N·m'
    else:
        more = (r.torque > 0) == (r.capture > 0)
        turning = (f'{size(r.torque)} N·m, turning it toward '
                   f'{"more" if more else "less"} linkage')
    if abs(r.shaft_power) < 1e-9:
        role = 'neither motor nor generator'
    elif r.shaft_power > 0:
        role = 'motor: the circuit gives, the shaft gets'
    else:
        role = 'generator: the shaft gives, the circuit gets'
    return dict(
        linkage=f'linkage λ = {signed(r.linkage)} Wb',
        capture=f'capture κ = {caught}',
        torque=f'torque χ = κ i = {turning}',
        voltage=f'voltage ℰ = −κ ω = {signed(r.voltage)} V at {signed(case.values["sweep"])} rad/s',
        balance=(f'χ ω + ℰ i = {signed(r.shaft_power)} W {"+" if r.circuit_power >= 0 else "−"} '
                 f'{size(r.circuit_power)} W = 0 · {role}'),
    )


class Graph:
    """One turn of shaft angle across, webers and catch up the side."""
    left, right, middle, height = .75, 6.65, .45, 1.8

    def __init__(self, top):
        self.top = top

    def x(self, angle):
        return self.left + (self.right-self.left)*angle/TURN

    def y(self, value):
        return self.middle + self.height*value/self.top

    def point(self, angle, value):
        return [self.x(angle), self.y(value), 0]

    def axes(self):
        objects = VGroup(Line(self.point(0, 0), self.point(TURN, 0), color=GHOST, stroke_width=1.2),
                         Line(self.point(0, -self.top), self.point(0, self.top),
                              color=GHOST, stroke_width=1.2))
        for quarter, words in enumerate(['face-on', '¼ turn', '½ turn', '¾ turn', '1 turn']):
            x = self.x(quarter*TURN/4)
            objects.add(Line([x, self.y(0)-.06, 0], [x, self.y(0)+.06, 0],
                             color=GHOST, stroke_width=1.2))
            objects.add(label(words, [x, self.y(-self.top)-.25, 0], 14))
        for value in (-self.top, self.top):
            objects.add(label(signed(value), [self.left-.32, self.y(value), 0], 13))
        return objects

    def curve(self, angles, values, color):
        shape = VMobject(stroke_color=color, stroke_width=2.5)
        return shape.set_points_smoothly([self.point(a, v) for a, v in zip(angles, values)])


class CaptureView:
    """The ring on the left; its linkage and capture over a turn on the right."""

    def __init__(self, pixels=1100):
        self.camera = Camera(pixel_width=pixels, pixel_height=round(pixels*9/16),
                             frame_width=14.2, frame_height=14.2*9/16,
                             background_color=PAPER)
        self.fixed = VGroup(
            label('The ring on its shaft', [-3.65, 3.15, 0], 25, INK),
            label('What a radian of turning catches', [3.6, 3.15, 0], 25, FORCE),
            label('field points up · blue: area arrow', [-3.65, 2.72, 0], 17),
            label('green: linkage λ, Wb    red: capture κ = dλ/dθ, catch', [3.6, 2.72, 0], 17),
            Line([0, -1.8, 0], [0, 2.45, 0], color=GHOST, stroke_width=.7),
            field_arrows(),
        )
        self.cache = {}

    def curves(self, case):
        """Linkage and capture over a turn; depends only on the ring, so keep it."""
        if case not in self.cache:
            angles = np.linspace(0, TURN, 121)
            linkage = [follow_flux(case, a).linked for a in angles]
            kappa = [capture(case, a) for a in angles]
            top = 1.15*max(np.max(np.abs(linkage)), 1e-9)
            graph = Graph(top)
            self.cache[case] = graph, VGroup(graph.axes(),
                                             graph.curve(angles, linkage, FLUX),
                                             graph.curve(angles, kappa, FORCE))
        return self.cache[case]

    def still(self, case, angle=TRIANGLE):
        r = reading(case, angle)
        graph, curves = self.curves(case)
        points = pose(winding(case)[0], case, angle)
        stride = max(1, case.samples_per_winding//32)
        words = sentences(case, r)
        objects = VGroup(self.fixed, curves,
                         ring_figure(case, points[::stride], follow_flux(case, angle).area),
                         DashedLine(graph.point(angle, -graph.top), graph.point(angle, graph.top),
                                    color=GHOST, stroke_width=1.2),
                         Dot(graph.point(angle, r.linkage), color=FLUX, radius=.06),
                         Dot(graph.point(angle, r.capture), color=FORCE, radius=.06))
        objects.add(label(f'{angle:.3f} rad = {angle/TURN:.3f} turn from face-on',
                          [-3.65, -1.95, 0], 17))
        for row, key, color in ((0, 'linkage', FLUX), (1, 'capture', FORCE),
                                (2, 'torque', INK), (3, 'voltage', COPPER), (4, 'balance', INK)):
            objects.add(label(words[key], [0, -2.5-.31*row, 0], 16, color))
        self.camera.reset()
        self.camera.capture_mobjects([objects])
        return self.camera.get_image().copy()


def explore_capture(case, view):
    """Turn the ring by hand or let it play; the readings follow."""
    current = case
    image = w.Image(format='png', layout=w.Layout(width='100%', max_width='1100px'))
    readout = w.HTML()
    steps = 120
    angle = w.FloatSlider(min=0, max=TURN, step=.01, value=TRIANGLE,
                          description='angle · rad', readout_format='.3f',
                          continuous_update=False, layout=w.Layout(width='440px'),
                          style=dict(description_width='90px'))
    play = w.Play(min=0, max=steps, step=1, interval=200)
    w.link((play, 'value'), (angle, 'value'),
           transform=(lambda k: TURN*k/steps, lambda a: round(steps*a/TURN)))
    current_slider = w.FloatSlider(min=-3, max=3, step=.5, value=case.values['current'],
                                   description='current · A', continuous_update=False,
                                   style=dict(description_width='90px'))
    sweep = w.FloatSlider(min=-2, max=2, step=.5, value=case.values['sweep'],
                          description='ω · rad/s', continuous_update=False,
                          style=dict(description_width='90px'))
    tube = w.FloatSlider(min=0, max=.4, step=.05, value=case.values['tube'],
                         description='tube · m', continuous_update=False,
                         style=dict(description_width='90px'))
    buttons = {name: w.Button(description=name, layout=w.Layout(width='90px'))
               for name in ('3–4–5', 'Face-on', 'Edge-on')}

    def show(change=None):
        data = io.BytesIO()
        view.still(current, angle.value).save(data, 'PNG')
        image.value = data.getvalue()
        r = reading(current, angle.value)
        readout.value = ('<p style="font-family:monospace">'
                         f'λ {r.linkage:+.3f} Wb · κ {r.capture:+.3f} catch · '
                         f'χ {r.torque:+.3f} N·m · ℰ {r.voltage:+.3f} V · '
                         f'χω {r.shaft_power:+.3f} W · ℰi {r.circuit_power:+.3f} W</p>')

    def change_case(change):
        nonlocal current
        play.playing = False
        current = replace(case, current=(current_slider.value, 'ampere'),
                          sweep=(sweep.value, 'sweep'), tube=(tube.value, 'meter'))
        show()

    def choose(value):
        play.playing = False
        angle.value = value

    for name, value in (('3–4–5', TRIANGLE), ('Face-on', FACE_ON), ('Edge-on', EDGE_ON)):
        buttons[name].on_click(lambda button, value=value: choose(value))
    angle.observe(show, names='value')
    for control in (current_slider, sweep, tube):
        control.observe(change_case, names='value')
    show()
    panel = w.VBox([image, w.HBox([play, angle, *buttons.values()]),
                    w.HBox([current_slider, sweep, tube]), readout])
    panel.controls = dict(angle=angle, play=play, current=current_slider,
                          sweep=sweep, tube=tube, **buttons)
    return panel
