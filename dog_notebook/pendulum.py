"""A pendulum: givens, a trajectory, a state, and a picture.

Claude's drawing and notebook prototype, extended by Codex, 2026-10-24.
"""

from dataclasses import dataclass
from functools import cached_property, lru_cache
from typing import NamedTuple

import numpy as np
from scipy.integrate import solve_ivp
from manim import Camera, VGroup, Line, Circle, Dot, DashedLine, Arc, Arrow
from manim import WHITE, BLACK, TEAL_D, GRAY, UP, DOWN, RIGHT

from ledger import number

COBALT = "#24489c"


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


def picture(case, state, scale=6, pivot=3.5 * UP):
    """Draw one physical state, with scale in scene units per meter."""
    lever = scale * case.values['length']
    start = case.values['release']
    angle, sweep = state.angle, state.sweep
    bob = bob_at(lever, angle, pivot)
    run = lever * sweep * (np.cos(angle) * RIGHT + np.sin(angle) * UP)
    return VGroup(
        DashedLine(pivot, pivot + lever * DOWN, color=GRAY),
        Arc(radius=lever, arc_center=pivot,
            start_angle=-np.pi/2 - start, angle=2 * start, color=GRAY),
        Line(pivot, bob, color=BLACK, stroke_width=3),
        Dot(pivot, color=BLACK),
        Circle(radius=0.28, color=COBALT, fill_opacity=1).move_to(bob),
        Arrow(bob, bob + run / 10, buff=0, color=TEAL_D),
    )


class View:
    def __init__(self, pixels=480, scale=6, width=10):
        self.scale = scale
        self.camera = Camera(pixel_width=pixels, pixel_height=pixels,
                             frame_width=width, frame_height=width,
                             background_color=WHITE)

    def draw(self, case, state):
        self.camera.reset()
        self.camera.capture_mobjects([picture(case, state, self.scale)])
        return self.camera.get_image().copy()

    def still(self, case, time=0):
        return self.draw(case, state_at(case, time))


def movie(case, seconds=3, folder="movies", scale=6):
    from manim import Scene, ValueTracker, always_redraw, linear, tempconfig

    class Swinging(Scene):
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
                    output_file="swinging")
    with tempconfig(settings):
        scene = Swinging()
        scene.render()
        return str(scene.renderer.file_writer.movie_file_path)


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
