"""Meta-test: every guard that can raise must have a test that makes it raise.

Why this is a mechanism and not a rule
--------------------------------------
A guard promises two things: violating input raises, and valid input passes.
A test that only feeds valid input observes the SAME outcome for a working
guard and for a no-op guard, so it cannot distinguish them. `assert_5` in the
H1a policy module was completely vacuous while its positive test passed; an
independent reviewer found it, not the suite. `docs/H1A_PROBLEM_ANALYSIS.md`
records that pattern (P1) occurring seven times, and the written discipline --
"state both propositions and check them" -- failed all seven times. Discipline
has to be remembered. This does not.

Why AST and not introspection
-----------------------------
Importing is not an option. Experiment folders deliberately hold same-named
modules as frozen copies, and `pytest.ini` explains the consequence: whichever
loads first wins `sys.modules` and another experiment silently runs on it.
Parsing reads those files without importing any of them, so this one
root-level test reaches every experiment despite `norecursedirs = experiments`.

What this does NOT catch
-----------------------
Only guards that EXIST but are unproven. A missing check -- no guard written
at all -- is invisible here, because there is no `assert_*` to find. The four
defects recorded in
`experiments/2026-08-04_owl_entailment_contract_shape/OPERATIONS_LOG.md`
(2026-08-05 judgment) are all of that second kind. This closes P1, not those.

Functions named `assert_*` whose body contains no `raise` and no `assert` are
not guards; requiring negative tests for them would be noise. They are skipped
and reported by name, never silently dropped.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
SKIP_PARTS = {"venv", ".venv", "vendor", "__pycache__", ".git", "node_modules"}
GUARD_PREFIXES = ("assert_", "_assert_")

# Guards whose raise paths cannot be reached without mocking the collaborator
# they inspect. Writing a negative test against a mock would prove the mock,
# not the guard, so the honest state is "unproven, and here is why" rather than
# a fabricated test. Every entry needs a reason and an owner for closing it.
#
# These are NOT exempt from scrutiny -- `test_known_unproven_entries_are_not_stale`
# fails if an entry disappears or stops being able to raise, so the list cannot
# rot into a silent cap.
KNOWN_UNPROVEN: dict[str, str] = {
    # Emptied 2026-08-05: assert_9's entry is CLOSED. D-H1a-12 Q12.4's
    # independent golden contract (h1a_common_policy_block_v2.json) replaced
    # the self-identity comparison, so all three raise paths are now reachable
    # and the ruling's five negative tests exist and pass -- including the
    # load-bearing one where BOTH arms drift identically. The ruling forbade
    # permanent KNOWN_UNPROVEN status for it; this is that condition met, not
    # waived.
}


def _python_files(root: Path):
    for path in sorted(root.rglob("*.py")):
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def _can_raise(fn: ast.AST) -> bool:
    return any(isinstance(n, (ast.Raise, ast.Assert)) for n in ast.walk(fn))


def _called_name(call: ast.Call) -> str | None:
    func = call.func
    if isinstance(func, ast.Attribute):
        return func.attr
    return getattr(func, "id", None)


def scan(root: Path) -> tuple[dict[str, list[Path]], dict[str, set[str]], list[str]]:
    """Return (raising guard -> defining paths, guard -> covering tests, skipped)."""
    raising: dict[str, list[Path]] = {}
    skipped: list[str] = []

    for path in _python_files(root):
        if path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith(GUARD_PREFIXES):
                continue
            if _can_raise(node):
                raising.setdefault(node.name, []).append(path.relative_to(root))
            else:
                skipped.append(node.name)

    covered: dict[str, set[str]] = {}
    for path in _python_files(root):
        if not path.name.startswith("test_"):
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.With):
                continue
            expects_raise = any(
                isinstance(item.context_expr, ast.Call)
                and (_called_name(item.context_expr) or "") == "raises"
                for item in node.items
            )
            if not expects_raise:
                continue
            for inner in ast.walk(node):
                if isinstance(inner, ast.Call):
                    name = _called_name(inner)
                    if name and name.startswith(GUARD_PREFIXES):
                        covered.setdefault(name, set()).add(str(path.relative_to(root)))

    return raising, covered, sorted(set(skipped))


# ==========================================================================
# the gate
# ==========================================================================
def test_every_raising_guard_has_a_negative_test() -> None:
    raising, covered, skipped = scan(ROOT)

    assert raising, "the scan found no guards at all -- it is broken, not the repo"

    missing = sorted(
        name for name in raising if name not in covered and name not in KNOWN_UNPROVEN
    )
    assert not missing, (
        "these guards can raise but no test ever makes them raise, so their "
        "recall is unmeasured and a vacuous rewrite would go undetected:\n"
        + "\n".join(
            f"  {name}  ({', '.join(str(p) for p in raising[name])})"
            for name in missing
        )
        + "\n\nFeed violating input inside `with pytest.raises(...)`. A "
        "positive-only test cannot tell a working guard from a no-op one -- see "
        "this module's docstring.\n"
        f"\nNot required (no raise/assert in body): {skipped or 'none'}"
    )


def test_known_unproven_entries_are_not_stale() -> None:
    """An exception list that outlives its reason is a silent cap.

    Every entry must still name a guard that exists and can still raise. When a
    guard is deleted, renamed, or made non-raising, the entry has to go too --
    otherwise the list quietly exempts nothing while looking like it exempts
    something, and a future guard reusing the name inherits the exemption.
    """
    raising, covered, _ = scan(ROOT)

    vanished = sorted(name for name in KNOWN_UNPROVEN if name not in raising)
    assert not vanished, (
        "KNOWN_UNPROVEN names guards that no longer exist or can no longer "
        f"raise -- delete these entries: {vanished}"
    )

    now_covered = sorted(name for name in KNOWN_UNPROVEN if name in covered)
    assert not now_covered, (
        "these guards now have a negative test, so the exemption is obsolete -- "
        f"delete them from KNOWN_UNPROVEN: {now_covered}"
    )


# ==========================================================================
# the scanner is itself a checker, so it gets both directions
# (skills-catalog pattern 8: checker-recall-and-precision)
# ==========================================================================
def _write(root: Path, name: str, body: str) -> None:
    (root / name).write_text(body, encoding="utf-8")


def test_scanner_flags_a_guard_whose_test_only_feeds_valid_input(tmp_path: Path) -> None:
    """Recall. This is the `assert_5` shape: a positive-only test."""
    _write(tmp_path, "mod.py", "def assert_x(v):\n    if v:\n        raise ValueError\n")
    _write(tmp_path, "test_mod.py", "def test_ok():\n    assert_x(0)\n")

    raising, covered, _ = scan(tmp_path)

    assert "assert_x" in raising
    assert "assert_x" not in covered


def test_scanner_does_not_flag_a_guard_with_a_negative_test(tmp_path: Path) -> None:
    """Precision. A guard exercised inside `pytest.raises` must not be listed."""
    _write(tmp_path, "mod.py", "def assert_x(v):\n    if v:\n        raise ValueError\n")
    _write(
        tmp_path,
        "test_mod.py",
        "import pytest\n"
        "def test_fires():\n"
        "    with pytest.raises(ValueError):\n"
        "        assert_x(1)\n",
    )

    _, covered, _ = scan(tmp_path)

    assert covered["assert_x"] == {"test_mod.py"}


def test_scanner_skips_an_assert_named_function_that_cannot_raise(tmp_path: Path) -> None:
    """Precision. A reporter that returns data is not a guard."""
    _write(tmp_path, "mod.py", "def assert_report():\n    return {'ok': True}\n")

    raising, _, skipped = scan(tmp_path)

    assert "assert_report" not in raising
    assert skipped == ["assert_report"]


def test_scanner_recognizes_a_guard_reached_through_a_module_attribute(
    tmp_path: Path,
) -> None:
    """The experiment suites call guards as `policy.assert_x(...)`, so attribute
    calls must count as coverage -- otherwise every real guard reads as missing."""
    _write(tmp_path, "mod.py", "def assert_x(v):\n    if v:\n        raise ValueError\n")
    _write(
        tmp_path,
        "test_mod.py",
        "import pytest\n"
        "def test_fires(policy):\n"
        "    with pytest.raises(ValueError):\n"
        "        policy.assert_x(1)\n",
    )

    _, covered, _ = scan(tmp_path)

    assert "assert_x" in covered


def test_scan_reaches_experiment_folders_without_importing_them() -> None:
    """The point of parsing: `norecursedirs` hides these from collection and
    importing them would collide on `sys.modules`."""
    raising, _, _ = scan(ROOT)

    in_experiments = [
        name
        for name, paths in raising.items()
        if any(str(p).startswith("experiments/") for p in paths)
    ]
    assert in_experiments, "no experiment guards seen -- the scan is not reaching them"


def test_the_staleness_check_itself_fires_on_a_bogus_entry(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The staleness check is a guard too, and this file's whole point is that a
    guard nobody makes fire has unmeasured recall. So make it fire."""
    monkeypatch.setitem(KNOWN_UNPROVEN, "assert_not_a_real_guard_xyz", "synthetic")

    with pytest.raises(AssertionError, match="no longer exist"):
        test_known_unproven_entries_are_not_stale()


@pytest.mark.parametrize("prefix", GUARD_PREFIXES)
def test_both_guard_prefixes_are_recognized(tmp_path: Path, prefix: str) -> None:
    _write(tmp_path, "mod.py", f"def {prefix}g():\n    raise ValueError\n")

    raising, _, _ = scan(tmp_path)

    assert f"{prefix}g" in raising
