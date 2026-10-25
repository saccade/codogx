# Bring me a pendulum

Claude's working prototype, extended by Codex for doc, 2026-10-24.

Open **pendulum.ipynb**. It starts with a one-metre pendulum: 10 hand,
1 lump, released from 0.6 stroke under 1 dog per second. The still is a
direct Python call. The next cell gives play, a time slider, physical knobs,
unit choices, zoom, and heft and hook beside the picture.

This is an ideal pendulum with a fixed pivot, a massless rod, and a point
mass. It keeps swinging. Its equation is the full sine equation, so a larger
release takes longer than the small-angle approximation predicts.

## Try it

Use Python 3.11 or later with Manim's Cairo/Pango prerequisites and FFmpeg
installed. In this directory:

```sh
python -m pip install -r requirements.txt
python -m pytest -q
jupyter lab pendulum.ipynb
```

JupyterLab is the notebook host; install it separately if needed. Restart
the kernel after changing the unit definitions.

The first useful call is deliberately small:

```python
from pendulum import Pendulum, View, state_at

case = Pendulum(length=(10, 'hand'), release=(0.6, 'stroke'))
view = View()
view.still(case, time=0.3)
```

`state_at(case, 0.3)` returns angle, sweep, speed, heft, and hook. Times are
seconds within the case's duration, which defaults to six seconds. Angles
use stroke, sweep uses stroke per second, speed uses cat, and energies use
thump. Heft is zero at the bottom. The teal arrow shows the instantaneous
velocity multiplied by a tenth of a second.

## One motion, several ways to look

`Pendulum.trajectory` solves once with SciPy's `solve_ivp` and keeps its
dense output. `state_at` samples that trajectory. The still, interactive
panel, and native Manim movie all use it. Scrubbing backward reads the same
motion. A `View` keeps one camera, clears it, and copies each finished image.

Changing length, mass, gravity, or release starts a fresh release. Changing
units or zoom keeps the current instant. Drawing scale is scene units per
metre; it changes the picture's size independently of the physics.

## Units and panels

`book_units.txt` is the ledger: one named construction per line, longhand,
as in doc's onir glyphs. Pint reads it. Stroke has its own base dimension,
so a crank times a stroke is a thump, while a crank alone stays a crank.

The solver boundary converts length to metres, gravity to zoom, and angle
to a count of strokes. There, one stroke is interpreted as one radian by
the sine equation. Stroke retains its separate dimension in the ledger.
`ledger.py` also supplies the four counts used by Claude's original algebra
tests; both views come from the same definitions.

`panels.py` offers dog, SI, and imperial choices for the knobs and readouts.
A reader can add another dictionary of units. For example:

```python
from panels import panels
panels['bench'] = dict(panels['imperial'], length='inch')
```

Then create another `explore(case, view)` panel. New unit names go in
`book_units.txt`. The product-table button grid and student ledger with
missing names are the next pieces to add; the present panel supplies the
pendulum's controls.

## What was checked

All 13 tests from Claude's archive passed before the changes and remain
unchanged. The full suite now has 27 passing tests. Added checks cover exact
unit conversions, stroke separation, equivalent physical inputs, energy
conservation, mass and gravity effects, deterministic scrubbing, copied
camera frames, and panel callbacks.

The notebook's five code cells executed in-process, including a direct still,
the widget, and the native Manim movie. The notebook contains their outputs
and saved widget state. This host cannot open a Jupyter kernel socket, so
live browser playback has not been checked here. The embedded movie and
`preview/pendulum.gif` provide portable motion previews.

One metre under 10 zoom at this release begins with about 1.75 thump.
Across six seconds, the measured energy error was below 9e-10 thump.
Warm state lookup averaged 0.012 ms and a 360-pixel still about 7 ms on this
host; notebook transport adds its own time.

The book's “0.1 ponder under 10 zoom” heft row remains a question for doc.
The ledger preserves ponder as lump at a lever.

The source archive includes the two original Claude commits and the Codex
extension, so Claude can inspect the change directly with `git show`.
