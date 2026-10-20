# Physics checks, in harness

Prepared by Codex (OpenAI) for dr. kraemer, 2026-10-20.

The shared work is the case definition and the comparison contract.
Implementations remain independently authored. They must not import one
another's model functions. Rendering may be shared or separate.

## Run

Python 3.10 or newer. Create an environment and install requirements.txt,
or use an existing environment with NumPy and SciPy.

    python run.py list
    python run.py check --implementation codex
    python run.py check --case valves --no-cache
    python -m unittest discover -s tests -v

The second command runs all available Codex implementations. The third
also asks for Claude's implementation; until the original is registered,
it reports MISSING and exits 2. A missing checker is never a pass.

Exit codes: 0 = selected implementations passed; 1 = failure or
cross-implementation disagreement; 2 = an expected implementation is
missing. A run with only one available author does not establish an
independent two-author verification, even when it exits 0.

Reports are JSON, with units, tolerances, assumptions, implementation
identity, source hashes and environment versions recoverable from the
case, registry and report. On an unchanged calculation a cached result
is reused. Source, declared helper, fixture, runner or dependency-version
changes invalidate the cache. Use --no-cache for a fresh run.

## The three cases

- valves: the actual checks behind Codex Three Valves 2610201529.
  Original physics expressions and assertions were retained; literals
  now come from the fixture and output no longer uses a scratch path.
- sweater_equal: the existing equal-lag calculation was extracted from
  the document writer. Checking the numbers no longer writes a new
  document, copies upload helpers or changes a timestamp.
- sweater_two_store: Codex's independent numerical check of Claude's
  stated CL-180/181 model, captured from the earlier check in chat.
  This is Codex code, not Claude's original script.

The two sweater cases describe DIFFERENT models. They are not required
to agree point for point. Future implementations of either case must
use that case's stated model and assumptions, or create a new case.

Inputs use SI units unless a fixture explicitly identifies scaled
coordinates or time. Display rounding belongs in documents, never in
regression tolerances. Baselines are regression records, not proofs.
Agreement between implementations also does not prove the model's
physical assumptions; those remain subject to review.

## Add Claude's actual scripts

The registry reserves one Claude entry per case. These are currently
missing. No original Claude check script was materialized in this run:
the Library download helper returned HTTP 403. Older archived scripts
were located, but cannot be credited as executed here. They are not
substitutes for the current sweater and valve checks.

For each actual original script:

1. Retain it unchanged under originals/ with its author, source document,
   version and SHA-256 in originals/provenance.json.
2. Put a small adapter under implementations/claude/. It receives the
   case JSON path as its only argument and emits one JSON object. Keep
   its own derivation and numerical/symbolic methods. An adapter may
   translate names, units or output formatting; record those changes.
3. Match the output schema in CONTRACT.md. Mark that registry entry
   available. List imported local helper paths in the entry's sources.
4. Run that implementation alone, then both authors on the same case.
   A disagreement is a result to investigate, not something to average
   away or silence by widening tolerances.

Do not fill the Claude slots by asking another Codex agent to produce
an implementation and relabeling it Claude.

## Reuse document tools

No PDF engine or document renderer is included or rebuilt here.
Existing installed tools discovered in this environment are:

    /root/.codex/skills/builtins/documents/render_docx.py
    /root/.codex/skills/builtins/documents/scripts/render_and_diff.py
    /root/.codex/skills/builtins/presentations/container_tools/render_slides.py

Use the applicable document skill and these existing tools when a
render is actually needed. Independent rendering chains are fine.
Keep document rendering separate from model checks. A prose edit such
as using govern/governing/governed does not itself require rerunning
physics or rebuilding a rendering stack. Layout changes still need
appropriate visual verification when a rendered document is delivered.

## Editorial rule carried forward

Govern, governing, governed and governor form a strong ordinary word
family. Use the family where it explains the mechanism. A reminder to
verb a word is a local editorial correction; it does not automatically
ask for a new model or a complete rewrite.

The bot carries the heavy algebra. The explanation shows the grounded
quantities, their physical distribution and the finite exchanges that
change them. Rules 36–38 remain in force: proposals are tested, 37 is
excellent, and suspicious requests get challenged before action.
