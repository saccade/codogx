"""Linkage and capture over a turn of the shaft, drawn with Manim. Claude.

The angle counts the ring's way: from face-on, turning about the shaft.
Positive capture catches linked flux turning that way; negative releases it.
"""

import io
from dataclasses import replace
from typing import NamedTuple

import ipywidgets as w
import numpy as np
try:
    from manim import Camera, VGroup, VMobject, Line, Dot, DashedLine
    HAS_MANIM = True
except ImportError:
    HAS_MANIM = False

from ring import capture, follow_flux, winding, pose
from display_units import UnitPicker, QuantitySlider, selection, scaled, words
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


def sentences(case, r, units=None):
    """Read magnitudes and senses in the selected units; physics stays in SI."""
    units=selection(units)
    caught='neither catches nor releases' if abs(r.capture)<1e-9 else ('catches' if r.capture>0 else 'releases')
    if abs(r.torque)<1e-9:
        turning=words(0.,'torque',units)
    else:
        more=(r.torque>0)==(r.capture>0)
        turning=words(abs(r.torque),'torque',units)+', toward '+('more' if more else 'less')+' linkage'
    role=('neither motor nor generator' if abs(r.shaft_power)<1e-9 else
          'motor: circuit gives, shaft gets' if r.shaft_power>0 else
          'generator: shaft gives, circuit gets')
    return dict(
        linkage='linkage λ = '+words(r.linkage,'flux',units),
        capture='capture κ = '+words(r.capture,'capture',units)+'; positive turning '+caught,
        torque='torque χ = κ i = '+turning,
        voltage='generated EMF ℰ = −κ ω = '+words(r.voltage,'voltage',units)+' at '+words(case.values['sweep'],'sweep',units),
        balance='shaft '+words(r.shaft_power,'power',units)+' + circuit '+words(r.circuit_power,'power',units)+' = 0; '+role)


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

    def axes(self, units=None):
        units = selection(units)
        objects = VGroup(Line(self.point(0, 0), self.point(TURN, 0), color=GHOST, stroke_width=1.2),
                         Line(self.point(0, -self.top), self.point(0, self.top),
                              color=GHOST, stroke_width=1.2))
        for quarter in range(5):
            caption = words(quarter*TURN/4, 'angle', units, 2)
            x = self.x(quarter*TURN/4)
            objects.add(Line([x, self.y(0)-.06, 0], [x, self.y(0)+.06, 0],
                             color=GHOST, stroke_width=1.2))
            objects.add(label(caption, [x, self.y(-self.top)-.25, 0], 14))
        for value in (-self.top, self.top):
            objects.add(label(words(value,"flux",units,2)+" / "+words(value,"capture",units,2), [self.left-.32, self.y(value), 0], 10))
        return objects

    def curve(self, angles, values, color):
        shape = VMobject(stroke_color=color, stroke_width=2.5)
        return shape.set_points_smoothly([self.point(a, v) for a, v in zip(angles, values)])


class CaptureView:
    """The ring on the left; its linkage and capture over a turn on the right."""

    def __init__(self, pixels=1100, units=None):
        self.display_units = selection(units)
        self.camera = Camera(pixel_width=pixels, pixel_height=round(pixels*9/16),
                             frame_width=14.2, frame_height=14.2*9/16,
                             background_color=PAPER)
        self.fixed = VGroup(
            label('The ring on its shaft', [-3.65, 3.15, 0], 25, INK),
            label('What a radian of turning catches', [3.6, 3.15, 0], 25, FORCE),
            label('field points up · blue: area arrow', [-3.65, 2.72, 0], 17),
            label('green: linkage λ    red: capture κ = dλ/dθ', [3.6, 2.72, 0], 17),
            Line([0, -1.8, 0], [0, 2.45, 0], color=GHOST, stroke_width=.7),
            field_arrows(),
        )
        self.cache = {}

    def curves(self, case):
        """Linkage and capture over a turn; depends only on the ring, so keep it."""
        key = (case, tuple(sorted(self.display_units.items())))
        if key not in self.cache:
            angles = np.linspace(0, TURN, 121)
            linkage = [follow_flux(case, a).linked for a in angles]
            kappa = [capture(case, a) for a in angles]
            top = 1.15*max(np.max(np.abs(linkage)), 1e-9)
            graph = Graph(top)
            self.cache[key] = graph, VGroup(graph.axes(self.display_units),
                                             graph.curve(angles, linkage, FLUX),
                                             graph.curve(angles, kappa, FORCE))
        return self.cache[key]

    def still(self, case, angle=TRIANGLE):
        r = reading(case, angle)
        graph, curves = self.curves(case)
        points = pose(winding(case)[0], case, angle)
        stride = max(1, case.samples_per_winding//32)
        readings = sentences(case, r, self.display_units)
        objects = VGroup(self.fixed, curves,
                         ring_figure(case, points[::stride], follow_flux(case, angle).area),
                         DashedLine(graph.point(angle, -graph.top), graph.point(angle, graph.top),
                                    color=GHOST, stroke_width=1.2),
                         Dot(graph.point(angle, r.linkage), color=FLUX, radius=.06),
                         Dot(graph.point(angle, r.capture), color=FORCE, radius=.06))
        objects.add(label(f'{words(angle,"angle",self.display_units,3)} from face-on',
                          [-3.65, -1.95, 0], 17))
        for row, key, color in ((0, 'linkage', FLUX), (1, 'capture', FORCE),
                                (2, 'torque', INK), (3, 'voltage', COPPER), (4, 'balance', INK)):
            objects.add(label(readings[key], [0, -2.5-.31*row, 0], 16, color))
        self.camera.reset()
        self.camera.capture_mobjects([objects])
        return self.camera.get_image().copy()


def explore_capture(case, view, units=None):
    """Turn the ring with unit choices; defaults are SI. Codex update."""
    current = case
    picker = UnitPicker(['angle','current','sweep','length','flux','capture','torque','voltage','power'],units)
    image = w.Image(format='png',layout=w.Layout(width='100%',max_width='1100px'))
    readout = w.HTML()
    angle = QuantitySlider(picker,'angle','angle',TRIANGLE,0,TURN,.01)
    amperes = QuantitySlider(picker,'current','current',case.values['current'],-3,3,.5)
    sweep = QuantitySlider(picker,'sweep','sweep',case.values['sweep'],-2,2,.5)
    tube = QuantitySlider(picker,'length','tube',case.values['tube'],0,.4,.05)
    play = w.Play(min=0,max=120,step=1,interval=200)
    buttons={name:w.Button(description=name,layout=w.Layout(width='90px')) for name in ['3–4–5','Face-on','Edge-on']}
    def show(change=None):
        view.display_units=picker.units
        data=io.BytesIO();view.still(current,angle.si).save(data,'PNG');image.value=data.getvalue()
        r=reading(current,angle.si)
        readout.value='<p>'+ ' · '.join([
            'λ '+words(r.linkage,'flux',picker.units),
            'κ '+words(r.capture,'capture',picker.units),
            'χ '+words(r.torque,'torque',picker.units),
            'generated EMF ℰ '+words(r.voltage,'voltage',picker.units),
            'shaft '+words(r.shaft_power,'power',picker.units),
            'circuit '+words(r.circuit_power,'power',picker.units)])+'</p>'
    def change_case(change=None):
        nonlocal current
        play.playing=False
        current=replace(case,current=(amperes.si,'ampere'),sweep=(sweep.si,'rad/second'),tube=(tube.si,'meter'))
        show()
    def choose(value):
        play.playing=False;angle.set_si(value);show()
    play.observe(lambda change:angle.set_si(TURN*change['new']/120),names='value')
    for name,value in [('3–4–5',TRIANGLE),('Face-on',FACE_ON),('Edge-on',EDGE_ON)]:
        buttons[name].on_click(lambda button,value=value:choose(value))
    angle.observe(show)
    for control in [amperes,sweep,tube]:control.observe(change_case)
    picker.on_change(lambda *args:show())
    show()
    panel=w.VBox([picker.widget,image,w.HBox([play,angle.slider,*buttons.values()]),
                  w.HBox([amperes.slider,sweep.slider]),tube.slider,readout])
    panel.controls=dict(angle=angle.slider,play=play,current=amperes.slider,sweep=sweep.slider,
                        tube=tube.slider,units=picker.selectors,**buttons)
    panel.unit_picker=picker
    return panel


if not HAS_MANIM:
    from fallback_view import CaptureView
