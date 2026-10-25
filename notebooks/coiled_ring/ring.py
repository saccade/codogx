"""A rigid closed winding, and two accounts of its turning effect. Codex."""

from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import NamedTuple

import numpy as np
from units import number, field_number


@dataclass(frozen=True)
class Ring:
    radius: tuple = (1, 'meter')
    tube: tuple = (.2, 'meter')
    current: tuple = (2, 'ampere')
    field: tuple = (1, 'tesla')
    sweep: tuple = (1, 'rad/second')
    heading: tuple = (0, 'rad')
    windings: int = 25
    samples_per_winding: int = 512

    @cached_property
    def values(self):
        return dict(radius=number(self.radius, 'meter'),
                    tube=number(self.tube, 'meter'),
                    current=number(self.current, 'ampere'),
                    field=field_number(self.field),
                    sweep=number(self.sweep, 'sweep'),
                    heading=number(self.heading, 'stroke'))


def rotate(points, axis, angle):
    """A positive turn about a world x, y, or z axis; angle counts strokes."""
    points = np.asarray(points, dtype=float)
    turned = points.copy()
    i, j = (axis + 1) % 3, (axis + 2) % 3
    c, s = np.cos(angle), np.sin(angle)
    turned[..., i] = c * points[..., i] - s * points[..., j]
    turned[..., j] = s * points[..., i] + c * points[..., j]
    return turned


@lru_cache(maxsize=32)
def winding(case):
    """Once around the hole, N times around the tube; return r, dr/du, du."""
    v = case.values
    n = case.windings
    count = n * case.samples_per_winding
    u = 2 * np.pi * np.arange(count) / count
    c, s = np.cos(u), np.sin(u)
    cn, sn = np.cos(n*u), np.sin(n*u)
    radius = v['radius'] + v['tube'] * cn
    slope = -v['tube'] * n * sn
    points = np.column_stack((radius*c, radius*s, v['tube']*sn))
    tangent = np.column_stack((slope*c-radius*s, slope*s+radius*c,
                               v['tube']*n*cn))
    return points, tangent, 2*np.pi/count


def pose(points, case, angle):
    return rotate(rotate(points, 1, angle), 2, case.values['heading'])


class Forces(NamedTuple):
    net: np.ndarray             # push, conventional newton
    moment: np.ndarray           # crank, conventional newton meter
    positions: np.ndarray      # meter
    per_length: np.ndarray     # push per meter


def add_forces(case, angle):
    """Usual account: I dr cross B, then r cross dF, along the whole wire."""
    points, tangent, du = winding(case)
    points, tangent = pose(points, case, angle), pose(tangent, case, angle)
    field = np.array([0., 0., case.values['field']])
    force_density = case.values['current'] * np.cross(tangent, field)
    pieces = force_density * du
    moment = np.sum(np.cross(points, pieces), axis=0)
    per_length = force_density / np.linalg.norm(tangent, axis=1)[:, None]
    return Forces(pieces.sum(axis=0), moment, points, per_length)


def shadow_areas(points):
    """Signed triangle areas in the yz, zx, and xy shadows; square meters."""
    following = np.roll(points, -1, axis=0)
    return np.array([
        np.sum(points[:, i]*following[:, j] - points[:, j]*following[:, i])/2
        for i, j in ((1, 2), (2, 0), (0, 1))
    ])


@lru_cache(maxsize=32)
def area_arrow(case):
    """Measure the three shadows once, while the ring is at home."""
    return shadow_areas(winding(case)[0])


class Flux(NamedTuple):
    linked: float              # weber
    moment: np.ndarray          # crank
    area: np.ndarray           # sheet
    torque: float              # crank about the shaft


def capture(case, angle):
    """Linked flux caught per stroke of turning about the shaft; catch = weber per stroke.
    The area arrow sweeps: dA = (shaft x A) dθ, so dλ = B · (shaft x A) dθ. Claude."""
    area = pose(area_arrow(case), case, angle)
    field = np.array([0., 0., case.values['field']])
    return float(np.dot(field, np.cross(shaft(case), area)))


def follow_flux(case, angle):
    """The area arrow sweeps about the shaft; follow its flux directly."""
    area = pose(area_arrow(case), case, angle)
    field = np.array([0., 0., case.values['field']])
    current = case.values['current']
    torque = current * capture(case, angle)          # the capture of the current
    moment = current * np.cross(area, field)
    return Flux(float(np.dot(field, area)), moment, area, float(torque))


class State(NamedTuple):
    time: float
    angle: float
    forces: Forces
    flux: Flux


def state_at(case, time):
    angle = case.values['sweep'] * time
    return State(time, angle, add_forces(case, angle), follow_flux(case, angle))


def shaft(case):
    return rotate(np.array([0., 1., 0.]), 2, case.values['heading'])


def torque_about_shaft(case, moment):
    return float(np.dot(shaft(case), moment))


def across_shaft(case, moment):
    return moment - torque_about_shaft(case, moment)*shaft(case)

