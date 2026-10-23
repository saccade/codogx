# Mansion routes: clown attention and storage-first zing

Written by Codex (OpenAI), 2026-10-23, for dr. kraemer and Claude.
These are model working/inspiration words, not dr. kraemer's manuscript.

This is a seven-file source handoff for `saccade/claudog`, based on
`b81531c7f95fdcc433f37684a14a29ab8486da06`. The earlier planner handoff
in codogx PR #3 is already integrated in that base; do not reapply it.

## What this lands

- Different observations from the existing Clowns table suit the four paths:
  curious materials and small discoveries; determined tracing and inspection;
  a manic succession of wrong details; cycles, returns, and patterns in Path 4.
  No per-room quota. The common clues and the first quiet second person remain.
- Ghost energy is kept: added velocity keeps zip, added sweep keeps zing.
  Body energy is stored: the velocity of added motion stores punch; the sweep
  of added spin stores hook. All four worked paths follow the additions,
  including their checks; half-square energy shortcuts are removed.
  Geometric halves and phase half-sums remain separate mathematical facts.
- Earlier approved running edits: Path 3's single 5 mm rise, downward fraction
  before the statement's required cosine, and the grip's fifths; Path 1's
  equivalent ring; Path 2's torque count in twenty-fifths; the causal-number
  principle in the feature plan.

The AP statements and final choruses are unchanged. Dog Math’s live wording
was preserved before its scoped energy edits; that current text is versioned
in `docs/dog_math.txt` with one terminal newline. The dated older copy remains
intact. Craft and Next record the rule and pending source integration. The reader tabs already
contain these edits and verified against the local build. This PR stores the
patch; merging it in codogx does not apply it to claudog.

## Apply in claudog

From a current claudog checkout, save the adjacent `mansion-routes.patch` and run:

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

Review and commit the seven changed sources and regenerated outputs in claudog.
If the checkout has moved and the check fails, reconcile the source changes;
do not force the patch or rebuild the live tabs from an older source.
Use the existing `mansion/BUILDING.md` sync/verify chain if the reader tabs have
changed since this handoff. Keep any newer reader edits.

## Validation

- Patch passes `git apply --check --whitespace=error` against the captured base.
  Applying it reproduces all seven checked local source files byte for byte.
- Seven existing feature tests pass; all four paths build; no repeated whole lines.
- All four native path tabs verify for text and formatting against that build.
- Protected final choruses compare unchanged against the pre-pass reader text.
- No physics model changed; the independent physics harness was not rerun for
  this editorial pass.

Seven source files: `mansion/sets/build_sets.py`, `p4_reel.py`,
`path_features.json`, and new `clown_noticing.py` in that directory;
`mansion/workbook/tabs/craft.md` and `next.md`; and new `docs/dog_math.txt`.

The repo README identified the Google Doc as canonical. This current manual
text is now versioned without overwriting the older dated copy or losing
hand edits. The original Dog Math assembly program was not located: the
related builders inspected produce the Straight Dope or old house sets. Ask
Claude for the original builder and its inputs; no replacement renderer was
created. Reconcile that builder against this live-derived text before any
regeneration. Fixed-width typesetting tools already live in `typeset/`.
Generated pages are rebuilt in the canonical repository rather than duplicated
here. No private workbook snapshots or coordination logs are included.
