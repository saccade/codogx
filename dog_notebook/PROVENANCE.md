# Notebook provenance

Working notes by Codex (OpenAI), 2026-10-24, for dr. kraemer and Claude.

## Source received

- Archive: `dog-notebook-claude-strokes-2610242156.zip`
- SHA-256: `1c4e5caacd9a3500ee31d0b66ac3f6147408c462882961a4f41b2cdc3c8df47a`
- Source head: `64902dce645f6da7d2a8b7e509900ab624f675f4`
- Source branch: `cross-takes-a-stroke`

The first GitHub import commit preserves the supplied text source. Notebook
outputs and saved widget state were cleared. The archive's Git database and
binary previews were omitted. The original uploaded archive remains the source
for its full embedded history and previews.

## Rendering change

At dr. kraemer's request, Codex replaced Manim drawing with a small Pillow
canvas. Both models retain their existing states and equations. Pillow also
exports the same drawing as GIF, replacing the Manim/FFmpeg movie call.
The notebooks, dependency list, and run instructions follow that change.
The zoom test now checks physical rod geometry directly, rather than calling
a method on a Manim line. Added export tests cover moving GIF frames, timing,
field direction marks, and zero arrows. A neutral particle is drawn with a
small ring instead of a plus sign.

Authorship remains distinct: Claude supplied the flux model and proposed
stroke algebra; Codex supplied the earlier shared-trajectory interface and
this rendering revision. This is implementation and regression checking of
the supplied model, with no new physical assumptions.

## Source commit record

```text
64902dc The electric side needs the 4 pi to be two turns
52394cf Where flux comes from: the strokes balance
4bf3f9e Posit: every cross takes a stroke away; flux per sheet carries one
9f04453 A charge's velocity, bent by flux, on Codex's interface
a6436ee Share a dense pendulum trajectory across Manim views and swappable units
f8a1709 Pendulum in book units: manim draws, swing() moves
e3c87a3 Dog math notebook prototype: unit ledger, units_of, tests
```

## Validation

57 tests pass with Manim absent, on Python 3.12 with the pinned requirements
and Pillow 12.3.0. All five code cells in each notebook executed in-process.
Both 3-second GIFs decode as 75 frames at 480 by 480 pixels. Stills from both
views were visually inspected. Live Jupyter browser playback and the Mac
remain local checks.
