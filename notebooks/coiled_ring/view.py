"""One Manim camera for the winding and its shadow. Codex."""

import numpy as np
from manim import Camera, VGroup, VMobject, Line, Arrow, Text, Dot
from ring import state_at, shaft, torque_about_shaft
from comparison import flux_reading, torque_reading

PAPER = '#f8f7f2'
INK = '#24489c'
COPPER = '#9a6241'
FORCE = '#a85147'
FLUX = '#528b7b'
GHOST = '#bec2bb'


def label(words, point, size=19, color='#626860'):
    return Text(words, font_size=size, color=color).move_to(point)


def project(points):
    matrix = np.array([[1, .10, 0], [.40, .32, 0], [0, .95, 0]])
    return 1.65*np.asarray(points) @ matrix + [-3.65, .45, 0]


def shadow(points):
    return 1.65*np.asarray(points)*[1, 1, 0] + [3.4, .45, 0]


def trace(points, color=COPPER, width=1.5, fill=0):
    shape = VMobject(stroke_color=color, stroke_width=width,
                     fill_color=color, fill_opacity=fill)
    return shape.set_points_as_corners(np.vstack((points, points[0])))


class RingView:
    def __init__(self, pixels=1100):
        self.camera = Camera(pixel_width=pixels, pixel_height=round(pixels*9/16),
                             frame_width=14.2, frame_height=14.2*9/16,
                             background_color=PAPER)
        self.fixed = VGroup(
            label('Forces along the wire', [-3.65, 3.15, 0], 25, INK),
            label('Flux through its shadow', [3.4, 3.15, 0], 25, FORCE),
            label('oblique view · field points up', [-3.65, 2.72, 0], 17),
            label('seen along the field', [3.4, 2.72, 0], 17),
            label('blue: area arrow   red: force per wire length', [-3.65, -2.45, 0], 16),
            label('shadow overlaps count with their signs', [3.4, -2.45, 0], 16),
            label('One circuit around the hole; many windings around the tube.', [0, -3.65, 0], 18),
            Line([0, -2.5, 0], [0, 2.45, 0], color=GHOST, stroke_width=.7),
        )
        for x in [-1.1, 1.1]:
            for y in [-.65, .65]:
                self.fixed.add(Arrow(project((x,y,-.75)), project((x,y,1.1)),
                                     color=GHOST, stroke_width=1, stroke_opacity=.55,
                                     buff=0, max_tip_length_to_length_ratio=.05))

    def still(self, case, time=0, forces=True):
        state = state_at(case, time)
        p = state.forces.positions
        stride = max(1, case.samples_per_winding//32)
        objects = VGroup(self.fixed,
                         trace(project(p[::stride])),
                         trace(shadow(p[::stride]), fill=.07))
        axis = shaft(case)
        objects.add(Line(project(-1.6*axis), project(1.6*axis), color=GHOST, stroke_width=2))
        area = state.flux.area
        normal = area / np.linalg.norm(area)
        objects.add(Arrow(project([0,0,0]), project(.9*normal), color=INK,
                          buff=0, stroke_width=2, max_tip_length_to_length_ratio=.14))
        if forces:
            indices = np.linspace(0, len(p), 61, endpoint=False, dtype=int)
            for index in indices:
                f = state.forces.per_length[index]
                if np.linalg.norm(f) > 1e-8:
                    objects.add(Arrow(project(p[index]), project(p[index]+.10*f),
                                      color=FORCE, stroke_width=1, buff=0,
                                      max_tip_length_to_length_ratio=.22))
        objects.add(Dot(shadow([0,0,0]), color=GHOST, radius=.025))
        objects.add(label(f'{case.windings} windings around the tube', [-3.65,-2.85,0], 19))
        objects.add(label(flux_reading(state.flux.linked, 3), [3.4,-2.85,0], 17, FLUX))
        for torque, center, unit, color in (
            (torque_about_shaft(case, state.forces.moment), -3.65, 'N m', INK),
            (state.flux.torque, 3.4, 'crank', FORCE)):
            words = torque_reading(case, torque, unit, 3)
            objects.add(label(f'torque: {words}', [center,-3.23,0], 16, color))
        self.camera.reset()
        self.camera.capture_mobjects([objects])
        return self.camera.get_image().copy()
