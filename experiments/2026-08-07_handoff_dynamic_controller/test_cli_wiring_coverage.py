#!/usr/bin/env python3
"""GATE — a module that refuses input must be tested through its OWN entry
point, not only through the helper that does the refusing.

WHY THIS IS A GATE AND NOT A RULE IN A DOCUMENT
-----------------------------------------------
This repository has measured what happens to review rules that live in prose:
`docs/HARNESS_KNOWHOW.md` B4a records a discipline prescribed 7 times and
failed 7 times, which is why guard/negative-test coverage became
`test_guard_negative_coverage.py` instead of a paragraph. The same reasoning
applies here.

WHAT IT CATCHES, measured
-------------------------
Round 15 (2026-08-11): `make_safety_audit_blind_input.build()` grew an
`expected_cells` check and a test asserted it -- by calling `build()` directly
and passing the argument itself. `main()` never passed it. So the production
CLI accepted a 1-cell, non-primary artifact while the suite was green, and it
took a human running the CLI to find it. That is not a one-off: the same
shape had already appeared in the S1 cross-item test, which stayed green while
the call site was reverted to `" ".join()`.

A test written against a helper inherits the helper's blind spots, because it
was written while looking at the helper. A test that drives `main()` cannot.

THE RULE
--------
If a module in this directory
  (a) defines `main(argv)`, and
  (b) contains at least one fail-closed refusal (raises AuditInputError, or
      builds a SystemExit whose message begins "refusing"),
then some test in this directory must CALL that module's `main(`.

Not "must test the refusal through main" -- that is not statically decidable.
This is a floor: it makes the entry point reachable from the suite at all.
Passing it does not mean the wiring is right; failing it means the wiring was
never executed.

If a module genuinely cannot be driven this way, add it to KNOWN_UNPROVEN with
a reason and an owner. Do NOT satisfy this gate by mocking `main` -- a mocked
entry point proves nothing, the same way a mocked negative test proves nothing
(HARNESS_KNOWHOW B4a).
"""
from __future__ import annotations

import ast
from pathlib import Path

HERE = Path(__file__).resolve().parent

# module -> reason it cannot be exercised through main() from the suite.
# Every entry needs a reason and an owner; an empty dict is the goal.
KNOWN_UNPROVEN: dict[str, str] = {
    # run_live_phase_c.py's main() makes live provider calls and consumes a
    # primary attempt, so the suite must never call it. Its refusals are
    # covered by test_preprimary_gates.py, which drives the individual
    # _assert_* gates. Owner: experiment operator. This is the one case where
    # driving the entry point would be worse than not driving it.
    "run_live_phase_c.py": (
        "main() performs live provider calls and consumes a primary attempt; "
        "gates covered individually in test_preprimary_gates.py"),
    # Both red-teams shell out to sandbox-exec and write results/ artifacts.
    # Their conclusive/BLOCKED logic is asserted directly instead.
    "redteam_provider_isolation.py": (
        "main() spawns sandbox-exec and writes a results/ artifact"),
    "redteam_codex_mcp_isolation.py": (
        "main() spawns sandbox-exec and writes a results/ artifact"),
    "run_calibration.py": "main() writes results/calibration.json",
    "run_smoke.py": "main() writes results/smoke.json",
    "build_corpus.py": "main() regenerates corpus, cases and gold in place",
    "build_live_public_bundle.py": "main() writes a bundle to /private/tmp",
    "live_subject_tool.py": "entry point is a subprocess bridge, not a CLI",
}

_REFUSAL_PREFIX = "refusing"


def _module_facts(path: Path) -> tuple[bool, bool]:
    """(defines main(argv), contains a fail-closed refusal)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    has_main = any(isinstance(n, ast.FunctionDef) and n.name == "main"
                   for n in ast.walk(tree))
    refuses = False
    for node in ast.walk(tree):
        # raise AuditInputError(...) / raise _fail(...) / raise SystemExit(...)
        if isinstance(node, ast.Raise) and isinstance(node.exc, ast.Call):
            fn = node.exc.func
            name = getattr(fn, "id", None) or getattr(fn, "attr", None)
            if name in {"AuditInputError", "_fail"}:
                refuses = True
        # SystemExit("refusing: ...") built anywhere
        if isinstance(node, ast.Call):
            fn = node.func
            name = getattr(fn, "id", None) or getattr(fn, "attr", None)
            if name == "SystemExit":
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str) \
                            and arg.value.startswith(_REFUSAL_PREFIX):
                        refuses = True
        # f"refusing ..." returned from main() as an error path
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and node.value.startswith(_REFUSAL_PREFIX):
            refuses = True
    return has_main, refuses


def _main_calls_in_tests() -> set[str]:
    """Module aliases whose `main(` is called from any test file here."""
    called: set[str] = set()
    for test in HERE.glob("test_*.py"):
        tree = ast.parse(test.read_text(encoding="utf-8"))
        aliases: dict[str, str] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for a in node.names:
                    aliases[a.asname or a.name] = a.name
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) \
                    and node.func.attr == "main":
                base = getattr(node.func.value, "id", None)
                if base in aliases:
                    called.add(aliases[base])
    return called


def test_every_refusing_cli_is_driven_through_its_own_entry_point():
    called = _main_calls_in_tests()
    missing = []
    for path in sorted(HERE.glob("*.py")):
        if path.name.startswith("test_") or path.name.startswith("_"):
            continue
        if path.name in KNOWN_UNPROVEN:
            continue
        has_main, refuses = _module_facts(path)
        if has_main and refuses and path.stem not in called:
            missing.append(path.name)
    assert not missing, (
        "these modules refuse input but no test calls their main(): "
        f"{missing}. A test that only drives the helper inherits the helper's "
        "blind spots -- measured round 15, where build() had the matrix check "
        "and main() never passed it, so the CLI accepted a 1-cell artifact "
        "with a green suite. Add a test that calls main(), or record the "
        "module in KNOWN_UNPROVEN with a reason and an owner."
    )


def test_known_unproven_entries_are_real_and_explained():
    """The escape hatch must not become a place to hide new modules."""
    for name, reason in KNOWN_UNPROVEN.items():
        assert (HERE / name).is_file(), f"KNOWN_UNPROVEN names a missing file: {name}"
        assert len(reason) > 25, f"{name}: reason is too thin to review"
    stale = [n for n in KNOWN_UNPROVEN if not _module_facts(HERE / n)[0]]
    assert not stale, (
        f"these no longer define main() and should leave KNOWN_UNPROVEN: {stale}")
