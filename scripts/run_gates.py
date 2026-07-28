#!/usr/bin/env python3
"""Single entry point for this repo's merge gates.

Why this exists
---------------
CLAUDE.md used to list five separate gate commands, and the first of them
(`pytest -q` at the repo root) had been aborting at collection for some time:
three experiment directories each ship a `test_protocol.py`, which the default
import mode cannot hold simultaneously. Nothing ran. Enabling
`--import-mode=importlib` fixed collection but exposed a second, independent
defect underneath it.

That second defect is the reason this runner uses processes rather than a
cleverer pytest configuration. Experiment directories deliberately carry
byte-identical copies of `_cert_core.py` (6 copies), plus same-named
`evaluate.py` (10) and `_gen_prompts.py` (7). The duplication is not an
accident to be cleaned up -- `_cert_core.py`'s own header states it is
"Copied verbatim ... per the preregistration rule that E2.1 stays frozen",
i.e. the freeze discipline in docs/EXPERIMENT_METHODOLOGY.md requires it, and
every new experiment adds another copy. Two experiment test files import those
siblings by plain name after `sys.path.insert(0, HERE)`, so in a single
interpreter whichever loads first wins `sys.modules` and the other experiment
silently runs against the wrong evaluator. That is not hypothetical: it
produced `KeyError: 'role'` in the 2026-07-23 suite, which had been passing
only because it was always run from its own directory.

Per-folder mitigations (a conftest in each directory, or rewriting each test
to load siblings by file path) all share the same weakness: they must be
remembered for experiment N+1, and forgetting them fails silently with wrong
results rather than loudly with an error. Running each experiment in its own
interpreter makes the collision structurally impossible instead, and costs new
experiments nothing.

Exit code policy
----------------
FAIL (a real failure) exits 1. BLOCKED (a gate could not run at all because an
optional dependency is absent) does not, and is reported separately. Mixing
"this environment lacks owlready2" into the same signal as "a test regressed"
is how a gate stops being believed; the missing module is named so the reader
can decide whether to care.

BLOCKED is deliberately narrow: it means the gate never started. For pytest
gates that is exit code 2 (collection/usage error); for plain scripts it is a
nonzero exit whose output shows the import dying. A suite that ran and had
tests fail is FAIL even when a failure message mentions a missing module,
because otherwise one environment-dependent test would mask real regressions
in every other test in the same suite. A gate producing no recognizable
result is FAIL, not BLOCKED, so silence is never mistaken for success.

Stdlib only, per this repo's convention for tooling that must run anywhere.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = sys.executable

# Dependencies that are genuinely optional in a bare checkout. A gate that dies
# on one of these is BLOCKED, not failed.
OPTIONAL_DEPS = ("fastmcp", "owlready2")

_MISSING_MODULE = re.compile(r"No module named '([^']+)'")


@dataclass
class Result:
    name: str
    status: str  # PASS | FAIL | BLOCKED
    detail: str


def _blocked_on(output: str) -> str | None:
    """Return the missing optional dependency, if that is why a gate died."""
    for match in _MISSING_MODULE.finditer(output):
        if match.group(1).split(".")[0] in OPTIONAL_DEPS:
            return match.group(1)
    return None


def _last_meaningful_line(output: str) -> str:
    for line in reversed(output.strip().splitlines()):
        stripped = line.strip()
        if stripped and not stripped.startswith("-- Docs:"):
            return stripped[:160]
    return "(no output)"


def run_gate(name: str, argv: list[str], cwd: Path, is_pytest: bool) -> Result:
    proc = subprocess.run(
        argv,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    output = proc.stdout + proc.stderr

    if proc.returncode == 0:
        return Result(name, "PASS", _last_meaningful_line(output))

    # Only "never started" counts as BLOCKED. pytest exit 2 is a
    # collection/usage error; exit 1 means tests actually ran and failed, and
    # that must stay FAIL even if some failure text names a missing module --
    # otherwise one env-dependent test would mask regressions in its whole
    # suite.
    never_started = proc.returncode == 2 if is_pytest else True
    missing = _blocked_on(output)
    if never_started and missing:
        return Result(name, "BLOCKED", f"optional dependency missing: {missing}")

    return Result(name, "FAIL", _last_meaningful_line(output))


def gates() -> list[tuple[str, list[str], Path, bool]]:
    specs: list[tuple[str, list[str], Path, bool]] = [
        # Core suite. pytest.ini excludes experiments/, which are run below in
        # their own interpreters.
        ("core pytest", [PY, "-m", "pytest", "-q"], ROOT, True),
    ]

    # One interpreter per experiment: this is the isolation that makes the
    # duplicated frozen module names safe. cwd is the experiment directory so
    # each suite sees the same working directory it was written against.
    for test_file in sorted(ROOT.glob("experiments/*/test_protocol.py")):
        experiment = test_file.parent.name
        specs.append(
            (
                f"experiment: {experiment}",
                [PY, "-m", "pytest", "-q", "test_protocol.py"],
                test_file.parent,
                True,
            )
        )

    specs += [
        ("test_server.py", [PY, "test_server.py"], ROOT, False),
        ("qa_v7.py", [PY, "qa_v7.py"], ROOT, False),
        ("concept_gate_v7 inline", [PY, "-m", "conceptgate.concept_gate_v7"], ROOT, False),
        ("fuzz_normalizer_types.py", [PY, "fuzz_normalizer_types.py"], ROOT, False),
    ]
    return specs


def main() -> int:
    results = [run_gate(*spec) for spec in gates()]

    width = max(len(r.name) for r in results)
    print()
    for r in results:
        mark = {"PASS": "ok  ", "FAIL": "FAIL", "BLOCKED": "-- "}[r.status]
        print(f"  [{mark}] {r.name.ljust(width)}  {r.detail}")

    failed = [r for r in results if r.status == "FAIL"]
    blocked = [r for r in results if r.status == "BLOCKED"]
    print()
    print(
        f"  {len(results) - len(failed) - len(blocked)} passed, "
        f"{len(failed)} failed, {len(blocked)} blocked"
    )
    if blocked:
        print(
            "  blocked gates did not run and were not counted as failures; "
            "install the named dependency to cover them."
        )
    print()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
