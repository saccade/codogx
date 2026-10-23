# Mansion — current release source

Prepared by Codex (OpenAI) for dr. kraemer, 2026-10-23.
Branch: `release/mansion-261023-1331-pacific` in `saccade/codogx`.

This is the current thirteen-page problem-set source, including doc's
opening edits, appendix punctuation, joined twin introduction/speech,
real compilation-date display, and linked asterisk note at the very end.
The two explanatory lines about the spring/trigger and independent phases
are retained. Solutions and poetry are separate work.

## Shared local backup

The original Codex local PDF is now available as an additional backup:
[download The_Mansion_that_did_not_Spin_2026102313311331.pdf](The_Mansion_that_did_not_Spin_2026102313311331.pdf).
See [CODEX_LOCAL_BACKUP.md](CODEX_LOCAL_BACKUP.md) for real compile/save
times and the checksum. Claude's edition remains the primary publication.

## Build from this head

Install XeLaTeX/latexmk, siunitx (Ubuntu: texlive-science), standard fonts,
and Python pikepdf (tested here with 10.17.0). Then:

```sh
cd mansion/pset
python3 build_pdf.py
```

Use the wrapper, rather than compiling a previously generated date:
it writes build_stamp.tex from the real clock before invoking the existing
XeLaTeX chain. It produces one new PDF named with its actual
YYYYMMDDHHMMSScc creation time and build_record.json. The first-page date
is the actual compilation start. Metadata separately records compilation
start/end and actual new-edition creation time, with Pacific offset.

build_stamp.tex and build_record.json committed here are evidence for
the included review PDF; they are regenerated on every build.

## Appointed creation target

Aim: 2026-10-23 13:31:13.31 America/Los_Angeles, PDT (UTC−07:00),
or 16:31:13.31 Eastern.

Historical timed-build invocation (the target has passed):

```sh
python3 build_pdf.py --final --aim 2026-10-23T13:31:13.31-07:00
```

The wrapper compiles, waits once if early (maximum sixty seconds), and
captures the real save instant. If late, it saves immediately and records
the actual offset. It does not set a fictional creation date or change
filesystem timestamps. The target is only separate metadata. Claude owns the primary release. The Codex local copy was created at
the target and subsequently authorized for sharing as a backup; see above.

## Checked content and provenance

Base physics/source: claudog 59e0e1c. This branch adds doc's subsequent
approved prose and layout changes, not new physical assumptions.
Current build remains thirteen pages, no split problem statements.
Date asterisk reaches the note on page thirteen.
Current review PDF's exact timestamps are in build_record.json.

The earlier fixed-1331 candidate and standalone metadata finisher have
been removed to prevent accidentally publishing the stale layout or date.
For all prior independent physics, paths, and arrow checks see BUILD_CHECK.md.
