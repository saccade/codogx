# Mansion routes and the current Dog Math snapshot

Written by Codex (OpenAI), 2026-10-23, for dr. kraemer and Claude.
Model working/inspiration words, not dr. kraemer's manuscript.

The adjacent `mansion-routes.patch` targets claudog
`a450df6ff449dc4822138ec56399e77cd783cea9`, including Claude's newly
preserved Dog Math history. PR #3's planner is already in the base.

## What changes

- Each path notices different details from the existing Clowns table,
  chosen for its mood. Common clues, the frozen clown, and the final choruses
  remain. No per-room quota was imposed.
- All four worked energy accounts follow additions of motion, spin, charge,
  or flux at their velocity, sweep, voltage, or current. Ghost energy is
  **kept**: added velocity keeps zip; added sweep keeps zing. Body energy is
  stored. Half-square energy shortcuts are removed from explanations and
  worked checks. The AP statements are unchanged; geometric halves and
  phase half-sums remain separate mathematical facts.
- Earlier approved edits remain: the single 5 mm rise, the downward fraction,
  the grip's fifths, the equivalent ring, and the torque count in twenty-fifths.
- The current live Dog Math is preserved as the next text snapshot in
  `docs/dog-math/doc-snapshots/`. Twelve scoped energy edits were made in the
  live original. Its prior hand edits remain, and terminal newlines alone are
  normalized in the snapshot. The older snapshots are untouched.
- Craft and Next record the energy rule and pending canonical integration.

Claude clarified the manual's history: no dedicated assembly program existed.
It was hand-edited through 47 text versions and then edited in Google Docs,
using the shared `typeset/` tools for wrapping and checks. The Google Doc stays
the source of truth. Do not regenerate it from a snapshot. Its newest previous
snapshot matches the pre-edit live text after blank-line and Markdown-export
normalization; the snapshot diff is not a reason to undo hand edits.

## Apply in claudog

Merging this PR stores a handoff in codogx. It does not apply the patch to
claudog. From a current claudog checkout, save the adjacent patch and run:

```sh
git apply --check --whitespace=error /path/to/mansion-routes.patch
git apply --whitespace=error /path/to/mansion-routes.patch
cd mansion/sets
python3 -m unittest test_path_features.py
python3 build_sets.py
python3 repeats.py
python3 paths_plan.py four_paths.html
python3 gaps.py gaps.json
python3 gaps_page.py gaps.json forgetting_gaps.html
```

Review and commit the eight changed sources plus regenerated outputs in
claudog. If the check fails on newer work, reconcile; do not force the patch.
The reader tabs and live manual already have the text changes. Follow the
existing `mansion/BUILDING.md` verification chain before any later tab write,
preserving intervening reader edits.

## Validation

- `git apply --check --whitespace=error` passes; applying the patch reproduces
  all eight local source files byte for byte.
- Seven existing feature tests pass; all four paths build without repeated
  whole lines. A contextual audit finds no half-square energy shortcuts in
  the solution text. The protected final choruses compare unchanged.
- The live manual matches the new snapshot, apart from terminal newlines.
  Native path text and formatting are verified using the existing tools.
- Physics models are unchanged; no new renderer or blind derivation was made.

Source scope: four `mansion/sets/` files (`build_sets.py`, `p4_reel.py`,
`path_features.json`, new `clown_noticing.py`); Craft and Next Markdown sources;
the Dog Math lineage README; and one new live-manual text snapshot. No private
workbook snapshots or coordination logs are in this handoff.
