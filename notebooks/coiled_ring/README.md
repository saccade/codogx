# A coiled ring, two accounts

Working notebook and code by Codex, 2026-10-25. Ideas and teaching direction from dr. kraemer.

Open `Codex-Coiled-Ring-2610250944.ipynb` beside these Python files. Use the existing
`dog-math` environment, restart the notebook kernel, and Run All. The saved notebook
includes a still, a short animation, the worked comparison, and saved widget state.
The live controls run when the Python kernel is connected.

Keep this whole folder together: the notebook imports the Python files and reads
the animation in `preview/`. From the repository root:

```sh
conda activate dog-math
cd notebooks/coiled_ring
jupyter lab Codex-Coiled-Ring-2610250944.ipynb
```

The wire goes once around the central hole and 25 or 36 times around the tube.
The rigid, nonmagnetic former carries one closed wire with current held fixed by
an ideal source. A steady uniform external field acts on it. The notebook adds
external magnetic forces and compares their total turning effect with current
times flux gained per stroke. Internal stresses hold the shape.

`ring.py` contains the geometry and the two accounts. `view.py` draws them through
one reusable Manim camera. `panel.py` connects their common controls.
`comparison.py` prints the live readings. `units.txt` is a small explicit Pint
ledger with SI, book, and length aliases; extend its lines to add units.

The force account samples the smooth wire's analytic tangent. The flux account
measures signed triangle areas of a polygonal wire and follows the resulting area
arrow's sweep directly: the shaft axis crossed with the area gives its change per
numerical stroke. Field dotted with that sweep, times current, gives shaft torque.
It calls no force routine. The small difference between the accounts comes from
the polygonal area measurement and shrinks quadratically with refinement.

The notebook starts by reading the wire, field arrows, and shadow, then introduces
linked flux and the work balance. The panel reports torque about the shaft as a
size and sense. It separately reports the total moment about the center and any
across-shaft moment that the bearings must balance. Here the across-shaft moment
is zero. Changing heading changes the world-axis components of the same shaft
torque. Playback follows a prescribed sweep.

## Units and energy

In the book's ledger, the field has units `tesla * stroke`. Dividing by one stroke
gives the usual SI magnetic field. The numerical boundary counts angles in strokes
and evaluates crosses as the usual component operations; their stroke divisors are
accounted for in the named output units. Torque is `crank = thump / stroke`;
the shaft carries it as twist.

For fixed current, mechanical work done by the magnetic forces is `I * dΦ`.
That statement concerns shaft work with the current maintained. The source and
the field-producing apparatus participate in the energy exchange.

The notebook cites Feynman II, chapters 15 and 17, for the conventional force,
induction, and mechanical-work relations. Its toroidal-winding calculation and
the comparison code are derived here.

## Check it

```sh
python -m pytest -q
```

Python 3.12 or later. Requirements match the earlier Manim notebook, with SymPy
added for the optional symbolic calculation. Existing working environments can
usually run it directly.

Codex validation: 20 tests pass, including the direct sweep, current reversal,
across-shaft moment, area convergence, units, and live-control callbacks. All nine
code cells execute in a fresh Python process. Claude's review checked the saved
arithmetic by hand; Claude's independent execution is still pending.

## Provenance · append only

- 2026-10-25 09:44 America/New_York — Codex created this companion to the
  rotating-loop notebook at dr. kraemer's request: two independently evaluated
  accounts, shared controls, a coiled ring, and an explicit numerical comparison.
  The Manim camera pattern follows the earlier Codex notebook. The longhand unit
  ledger follows dr. kraemer's and Claude's design; this small registry starts
  empty and defines each included unit explicitly.
- 2026-10-25 — Codex incorporated Claude's review, relayed by dr. kraemer:
  forward/upward parts; torque about the shaft; total and across-shaft moments;
  magnitude-and-sense readings; complete folder delivery through `saccade/codogx`.
  This also corrects the earlier description of two world components as
  "transverse": both can belong to the same torque about the shaft.
  Following dr. kraemer's teaching reminder, the introduction now builds from
  the visible apparatus and a flux measurement to the balance. The physical
  assumptions and the two independent calculations are unchanged.
- 2026-10-25 10:18 — Following Claude's note and dr. kraemer's instruction to
  "go straight to the sweep," Codex replaced the finite difference of flux with
  the area arrow's exact sweep at the measured area. The convergence table now
  tests area measurement alone. The force account remains independent. The
  force column labels linked flux "not used."
