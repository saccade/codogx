# Working in codogx

- Reuse the physics harness and existing document tools. A wording reminder is a local edit unless it changes a physical claim.
- Keep independently authored implementations independent. Share cases, assumptions, units, tolerances, and result contracts.
- Preserve authorship and original sources. Missing Claude scripts remain explicitly missing; never relabel Codex code as Claude.
- Read a case before changing its implementation. Changed physical assumptions need an explicit case revision.
- Run `python physics_harness/run.py check --implementation codex` and `python -m unittest discover -s physics_harness/tests -v` for relevant harness changes. A combined run exits 2 while expected implementations are missing.
- Preserve source provenance. Treat numerical agreement as a check of the stated model, not proof of its physical assumptions.
