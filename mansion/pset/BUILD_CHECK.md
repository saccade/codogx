# Full build dry run — 2026-10-23

Codex (OpenAI), at dr. kraemer's request: “okay build everything through once to be sure we're alive”.

## Results

- Problem set: current claudog 59e0e1c / source blob c5c1c29.
  Existing XeLaTeX/latexmk chain runs successfully to an 11-page PDF.
- Every fresh PDF page has identical extracted text and rendered pixels to
  Claude's checked 15:01 PDF. No overfull boxes, missing glyphs, or LaTeX
  warnings in the fresh build log.
- Metadata finisher: passes. The test exposed xdvipdfmx's wrong time-zone
  offset being preserved by the earlier Codex adaptation. The corrected
  finisher stamps the actual new-edition save time in the chosen zone,
  retains the input stamp as SourceCreationDate, and records fractional
  seconds as ActualCreationTime. Candidate/final status is explicit.
- Four solution paths: build successfully. Claude's latest Path 1 paragraph
  was reconciled with the pending Codex edits in an isolated build copy;
  all four resulting texts and native formatting match the live workbook.
- Feature tests: 7 passed. Repetition check: no duplicate whole lines.
- Arrow checks: 97/97 passed.
- All four registered Codex physics cases pass; Mansion was additionally
  executed fresh without cache (104 observables and 33 named checks).
- Harness protocol/runner tests: 9 passed.
- Planner, gap data, and gap HTML regenerate successfully.
- Poetry workshop: 17 → 9 → 4 manifests are consistent, and the first
  assembly retains the protected last line.

The level scanner produced 26 advisory lines. These include ordinary
English matches (stretch, striped), electrical ohms, and early pickup
wording. The scanner is advisory; it did not automatically alter prose.

## Environment and scope

Initially siunitx.sty was absent. Ubuntu's texlive-science package was
downloaded and extracted locally, without replacing the renderer or
changing the problem source. In this workspace the fresh build used:

    TEXINPUTS="$PWD/tex-deps/usr/share/texlive/texmf-dist/tex//:" latexmk -xelatex -interaction=nonstopmode -halt-on-error -outdir=pdf ../pacific-release/mansion_pset.tex

The test outputs are scratch artifacts. No live solution tab was written,
no physics assumption changed, and no early final PDF was published.
The release branch changes only the metadata finishing script and its
build notes; the existing candidate remains for the timed final save.
The prose Path 4 and the separate verse workshop remain distinct.
