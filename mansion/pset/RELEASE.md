# Mansion — Pacific release candidate

Requested by dr. kraemer, 2026-10-23. Prepared by Codex (OpenAI).

Release target: **2026-10-23 13:31 America/Los_Angeles**,
PDT (UTC−07:00), equivalent to 16:31 Eastern / 20:31 UTC.

This branch is a release candidate, not an automatic publication.
The filename uses the requested release target. PDF metadata records
`ReleaseTarget`, `ReleaseTimeZone`, and candidate status separately
from the actual new-edition creation time. The input stamp is retained as
SourceCreationDate; ActualCreationTime includes fractional seconds.

## Pinned contents

- Source: saccade/claudog commit `59e0e1c152e76068635fb17b34809891e0d2404c`.
- TeX blob: `c5c1c29dd1ff51c7263199bf8aefd43403c2460a`.
- Original checked PDF: `The Mansion that did not Spin 2610231501.pdf`,
  blob `3baf19326801b79bc9093ddaecb4981829d505cb`.
- Contains Claude's accepted preflight corrections, including the
  twice-as-heavy knife and negligible table friction during the cue strike.
- Solutions are outside this release branch.

The attached candidate preserves the checked source PDF's page content;
only its metadata and filename are changed. A complete dry run now succeeds:
siunitx was extracted from Ubuntu’s texlive-science package into the local
build environment, and the existing XeLaTeX build produces eleven pages
text- and pixel-identical to the checked canonical PDF. See BUILD_CHECK.md.
The dry-run PDF does not replace the scheduled final edition.

## Rebuild

With XeLaTeX, latexmk, siunitx, and pikepdf installed:

```sh
cd mansion/pset
latexmk -xelatex mansion_pset.tex
python3 finish_pdf.py --timezone America/Los_Angeles --release-at 2026-10-23T13:31:00-07:00
# At the authorized release, add --final; the clock stamp remains the real save time.
```

Do not mistake the target timestamp for the actual creation date.
Keep one timestamped PDF on this branch. Further source corrections
must be rebuilt before replacing the candidate.

