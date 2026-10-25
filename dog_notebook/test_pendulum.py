import numpy as np
from pendulum import swing, gravity, still

def test_hangs_still():
    assert swing(5, 0.0, 1.0) == (0.0, 0.0)

def test_small_swing_rings_at_the_tone():
    lever = 5
    ring = np.sqrt(gravity / lever)               # stroke a second
    cycle = 2 * np.pi / ring                      # one turn of phase per cycle
    angle, _ = swing(lever, 0.01, cycle)
    assert abs(angle - 0.01) < 0.0002

def test_heft_turns_into_hook():                  # per lump, per lever squared
    lever, start = 5, 0.6
    angle, sweep = swing(lever, start, 0.4)
    drop = lever * (np.cos(angle) - np.cos(start))
    assert abs(gravity * drop - (lever * sweep) ** 2 / 2) < 0.01 * gravity * lever

def test_still_is_a_picture():
    assert still(t=0.3).size == (480, 480)
