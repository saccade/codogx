# Independent implementation interface

Each command is:

    python implementation.py /absolute/path/to/case.json

It runs in a fresh temporary working directory. stdout must contain
exactly one JSON object. Diagnostic output belongs on stderr. Local
paths in the case are not part of the protocol; find declared helper
files relative to the implementation's own __file__.

    {
      "schema_version": 1,
      "case_id": "the fixture's exact case_id",
      "implementation": "claude",
      "observations": {"observable_name": 1.23},
      "checks": {"named_physical_invariant": true}
    }

Every observable in the fixture is required. Values must be finite
numbers in the fixture's stated units; booleans are not numbers here.
Extra observations are allowed. At least one meaningful named physical
check must be present and every check must be boolean true.

Implementations receive the same inputs and boundary conditions. They
independently derive and calculate outputs. They must not copy the
fixture's expected values into observations or import another author's
physics code. Fixture expectations are checked only by the runner.

Use case-level tolerances for numerical differences. Record a changed
physical assumption as a new or revised case, not an implementation
that silently answers a different question. All local helper code must
be listed in the registry entry's sources so cache invalidation sees it.

The runner compares authors only within the same case. It reports
missing originals, nonzero exits, timeouts, malformed output, failed
invariants and disagreements explicitly. Reports include Python and
package versions, source and fixture hashes, and whether an execution
was reused from cache.
