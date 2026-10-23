# Review: path features, not a growing pile of formatter exceptions

Written by Codex (OpenAI), 2026-10-23, for Claude and dr. kraemer.

## What changed

Claude's four-path matrix and forgetting-gap page now display a shared
[path_features.json](path_features.json) plan. It represents notation, explanatory
register, poetic form, directional English, stanza glosses, rhythmic interleaving,
narrative recurrence, the book interlude, and the protected finale.

Every feature records a stable ID, kind, priority, implementation type, state per
path, where it begins or changes, payoff locations, source/evidence, and whether
it is applied, available, in progress, planned, or protected. The existing
terminology tables and use/gloss counts remain; this extends those tools.

The numeric formatter reads this same plan. The user's current choice is:
path 1 mostly decimals with revealing ratios retained; path 2 begins in decimals
and switches at 6-a, after the rolling ball makes the fifths visible; paths 3 and 4 can use established exact fractions from the start, improper
above one. This does not require a fraction for every value. Rounded results
stay decimals or exact roots. A small, explicit catalog selects meaningful
exact balances, with a denominator bound. Inertia/spin use grams with useful prefixes.

The planning page provides a feature-kind filter, per-path modes and onset
controls, a reset, and JSON export. A changed control is a preview and marks the
feature planned; it does not edit Docs. The displayed observed counts always
refer to the current build, not the unbuilt preview. Replace the manifest with
an exported plan, rebuild, review the diff, then sync the path tabs.

The gaps page adds a collapsible feature summary per path. Editorial choices
have no automatic poetry score. A regex can count forms; it cannot prove that a
verse carries its equation well.

## Review focus

- Is the data model broad enough for the other notation transitions, without
  pretending that an editorial judgment is an executable rule?
- Does the path 2 transition land where the fifths reveal the mechanism? It is now one
  manifest edit, not a Python special case.
- No rounded fractions are generated. Read the selected exact fractions for
  whether they actually expose the relationship. Counts are observations, not
  a conversion target. No mechanical “about” insertion.
- R-130 remains unchanged; the added number-choice policy is R-131.
- The a-4/a-5 highlights assert their full expected source before replacing it.
- The existing planner's length targets are old model estimates, not user quotas.
  The new panel labels them as historical. Do not turn them into requirements.
- Keep the existing four-path meanings, source equations, independent checks,
  and final chorus protected.

## Run

    cd mansion/sets
    python3 -m unittest test_path_features.py
    python3 build_sets.py
    python3 repeats.py
    python3 check_levels.py
    python3 paths_plan.py four_paths.html
    python3 gaps.py gaps.json
    python3 gaps_page.py gaps.json forgetting_gaps.html

Then use the existing set_doc patch/style/verify chain in ../BUILDING.md.
