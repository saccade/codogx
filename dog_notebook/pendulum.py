"""A pendulum: givens, a trajectory, a state, and a picture.

Claude's drawing and notebook prototype, extended by Codex, 2026-10-24.
"""

from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import NamedTuple

import numpy as np
from scipy.integrate import solve_ivp
from drawing import Canvas, COBALT, TEAL, save_movie
from ledger import number

UP = np.array([0., 1.])
DOWN = -UP
RIGHT = np.array([1., 0.])


@dataclass(frozen=True)
class Pendulum:
    length: tuple = (10, "hand")
    mass: tuple = (1, "lump")
    release: tuple = (0.6, "stroke")
    gravity: tuple = (1, "dog/second")
    duration: tuple = (6, "second")

    @cached_property
    def values(self):
        return dict(
            length=float(number(self.length, "meter")),
            mass=float(number(self.mass, "lump")),
            release=float(number(self.release, "stroke")),
            gravity=float(number(self.gravity, "zoom")),
            duration=float(number(self.duration, "second")),
        )

    @cached_property
    def trajectory(self):
        p = self.values

        def move(time, state):
            angle, sweep = state
            return sweep, -p['gravity'] / p['length'] * np.sin(angle)

        return solve_ivp(move, (0, p['duration']), (p['release'], 0),
                         dense_output=True, rtol=1e-10, atol=1e-12)


class State(NamedTuple):
    angle: float       # stroke
    sweep: float       # sweep
    speed: float       # cat
    heft: float        # thump, relative to the bottom
    hook: float        # thump


def state_at(case, time):
    """Read a time in seconds within the case's solved duration."""
    angle, sweep = case.trajectory.sol(time)
    p = case.values
    speed = p['length'] * sweep
    heft = p['mass'] * p['gravity'] * p['length'] * (1 - np.cos(angle))
    hook = p['mass'] * speed**2 / 2
    return State(angle, sweep, abs(speed), heft, hook)


def bob_at(lever, angle, pivot):
    return pivot + lever * (np.sin(angle) * RIGHT + np.cos(angle) * DOWN)


def picture(case, state, scale=6, pivot=3.5 * UP, canvas=None):
    """Draw one state; scale is scene units per meter."""
    canvas = canvas if canvas is not None else Canvas()
    canvas.clear()
    lever = scale * case.values['length']
    start = abs(case.values['release'])
    bob = bob_at(lever, state.angle, pivot)
    run = lever * state.sweep * (np.cos(state.angle) * RIGHT + np.sin(state.angle) * UP)
    for fraction in np.arange(0, 1, 0.04):
        canvas.line([pivot + fraction * lever * DOWN,
                     pivot + min(1, fraction + 0.02) * lever * DOWN])
    angles = np.linspace(-start, start, 100)
    canvas.line([bob_at(lever, angle, pivot) for angle in angles])
    canvas.line([pivot, bob], 'black', 3)
    canvas.circle(pivot, 0.06, 'black', 'black')
    canvas.circle(bob, 0.28, COBALT, COBALT)
    canvas.arrow(bob, bob + run / 10, TEAL)
    return canvas.snapshot()


class View:
    def __init__(self, pixels=480, scale=6, width=10):
        self.scale = scale
        self.camera = Canvas(pixels=pixels, width=width)

    def draw(self, case, state):
        return picture(case, state, self.scale, canvas=self.camera)

    def still(self, case, time=0):
        return self.draw(case, state_at(case, time))


def movie(case, seconds=3, folder="movies", scale=6):
    return save_movie(case, View(scale=scale), seconds, folder, 'swinging')


# Claude's original entry points use hand and stroke.
gravity = float(number((1, "dog/second"), "hand/second²"))


@lru_cache(maxsize=8)
def _case(lever, start, duration):
    return Pendulum(length=(lever, "hand"), release=(start, "stroke"),
                    duration=(duration, "second"))


@lru_cache(maxsize=8)
def _view(pixels, hands):
    return View(pixels=pixels, scale=10, width=hands)


def swing(lever, start, t):
    state = state_at(_case(lever, start, max(3, t)), t)
    return state.angle, state.sweep


def still(lever=5, start=0.6, t=0.0, pixels=480, hands=10):
    return _view(pixels, hands).still(_case(lever, start, max(3, t)), t)
