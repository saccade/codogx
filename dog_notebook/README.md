# Dog-math notebooks

Claude's prototype and flux extension; shared trajectory and controls by Codex.
Pillow rendering and GIF export by Codex, 2026-10-24, for dr. kraemer.

Open **flux.ipynb** for Claude's new charge-in-flux scene, or
**pendulum.ipynb** for the pendulum. These notebooks draw with Pillow and
use ipywidgets for play, scrubbing, quantities, and unit choices.

## Run on the existing Mac setup

Keep using the working `dog-math` Conda environment. Download and extract this
branch's ZIP, then open a Terminal in its `dog_notebook` folder. With the default
Downloads location and extraction name:

```sh
conda activate dog-math
cd /Users/kraemer/Downloads/codogx-dog-notebook-light-261024/dog_notebook
python -m pip install -r requirements.txt
jupyter lab flux.ipynb
```

Choose **Run → Run All Cells**, then press **Play** in the Explore panel.
The Share cell exports and displays an animated GIF. It needs no FFmpeg.
Manim, Cairo, and Pango are not dependencies of this version. Keeping an existing
Manim installation is fine; no environment rebuild or uninstall is needed.

Python 3.12 or later is required by the pinned Pint version. The existing
Python 3.13 environment is suitable. A fresh Python environment also needs
JupyterLab (`python -m pip install jupyterlab`).

The environment chooses Python and packages; the directory chooses files.
Launch Jupyter from this folder so imports find these companion modules.

## One motion, several views

`Pendulum.trajectory` solves the full sine equation once with SciPy's
`solve_ivp` and keeps its dense output. `state_at` samples it. The flux case
uses Claude's analytic circular or straight trajectory. Live frames, stills,
and GIFs all read the same states.

`drawing.py` contains a small Pillow canvas: lines, circles, and arrows in
scene coordinates. It draws at twice the requested resolution and downsamples
for smooth edges. Each snapshot owns its pixels. The canvas is reused while
scrubbing; the physics stays separate from the picture.

```python
from flux import ChargeInFlux, View, state_at

case = ChargeInFlux()
view = View()
view.still(case, time=0.4)
state_at(case, 0.4)
```

For exports, `movie(case, seconds=3)` now returns a GIF filename. Display it with
`IPython.display.Image(filename=...)`. Both notebooks use that call.
The drawing functions `picture` return Pillow images; `flux.marks` returns
mark centers, and `flux.path` returns sampled positions.

## Units and scope

`book_units.txt` is the ledger. Pint carries the independent stroke dimension.
`ledger.py` also supplies Claude's four-count algebra view from those definitions.
`panels.py` defines dog, SI, and imperial display choices. Restart the kernel
after changing definitions.

This change preserves Claude's motion calculations, units, and proposed
stroke rules. The algebra tests check the stated conventions; their agreement
does not establish those conventions as measured physical laws. Physics review
continues separately.

The uploaded bundle contains the flux and pendulum notebooks. The knife recorder
and dining-room scene from the separate Codex bundle are not part of this import.

## Check

```sh
python -m pytest -q
```

Tests cover units, equivalent inputs, energy, perpendicular magnetic force,
rewinding, snapshot ownership, widget callbacks, field marks, and GIF export.
See `PROVENANCE.md` for the source and rendering change history.
