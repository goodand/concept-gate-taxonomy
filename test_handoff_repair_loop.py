"""Negative tests for the repair-loop guards, written FROM the red team's
successful attacks.

An adversarial review reached PASS by three routes and found that the module's
docstring claimed five guards while implementing three -- the same defect class
(a stated proposition the code does not make true) that this repo has recorded
ten times. Positive tests could not have caught it: a guard that never runs and
a guard that runs and finds nothing look identical from the passing side.

So every test here feeds a guard the input that BEAT it, and asserts the guard
now says so. `test_the_docstring_does_not_claim_more_than_it_implements` is the
meta-test: it re-checks the specific claim/implementation gap that occurred.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
import handoff_repair_loop as loop  # noqa: E402


# --------------------------------------------------------------------------
# G4 -- clearing a finding by narrowing the audit input, not by repairing
# --------------------------------------------------------------------------
def _baseline(**over) -> dict:
    base = {"tracked_file_count": 100, "ref": "HEAD", "audit_inputs": ["a.md", "b.md"]}
    base.update(over)
    return base


def test_G4_fires_when_tracked_files_are_deleted(monkeypatch):
    """Red team route A, half 1: delete the orphan instead of linking it."""
    monkeypatch.setattr(loop, "tracked_file_count", lambda: 99)
    monkeypatch.setattr(loop, "audit_input_set", lambda ref: {"a.md", "b.md"})
    monkeypatch.setattr(loop, "skip_worktree_paths", lambda: [])
    out = loop.assert_input_not_narrowed(_baseline())
    assert any("tracked files dropped" in v for v in out)


def test_G4_fires_when_a_file_is_gitignored_out_of_the_audit(monkeypatch):
    """Red team route A, half 2: `.gitignore` the only orphan. The metric went
    9 -> 0 while measured reachability stayed 135 -> 135."""
    monkeypatch.setattr(loop, "tracked_file_count", lambda: 100)
    monkeypatch.setattr(loop, "audit_input_set", lambda ref: {"a.md"})
    monkeypatch.setattr(loop, "skip_worktree_paths", lambda: [])
    out = loop.assert_input_not_narrowed(_baseline())
    assert any("left the audit input set" in v and "b.md" in v for v in out)


def test_G4_fires_when_edits_are_hidden_with_skip_worktree(monkeypatch):
    """Red team: one reversible `git update-index --skip-worktree` blinded the
    edit guards while the auditor still read the file from disk."""
    monkeypatch.setattr(loop, "tracked_file_count", lambda: 100)
    monkeypatch.setattr(loop, "audit_input_set", lambda ref: {"a.md", "b.md"})
    monkeypatch.setattr(loop, "skip_worktree_paths", lambda: ["docs/HANDOFF.md"])
    out = loop.assert_input_not_narrowed(_baseline())
    assert any("skip-worktree" in v for v in out)


def test_G4_is_silent_when_nothing_was_narrowed(monkeypatch):
    """PRECISION. A guard that fires on a clean repair gets disabled wholesale
    -- the tripwire lesson this repo already paid for."""
    monkeypatch.setattr(loop, "tracked_file_count", lambda: 101)
    monkeypatch.setattr(loop, "audit_input_set", lambda ref: {"a.md", "b.md", "c.md"})
    monkeypatch.setattr(loop, "skip_worktree_paths", lambda: [])
    assert loop.assert_input_not_narrowed(_baseline()) == []


# --------------------------------------------------------------------------
# G1 -- editing the thing that grades you
# --------------------------------------------------------------------------
def test_G1_fires_when_the_grader_changes_mid_loop():
    """Editing the auditor is the most direct gaming path, so the pin is
    re-checked every iteration -- a mid-loop edit followed by a revert would
    otherwise be laundered."""
    before = dict(loop.pin())
    before["scripts/handoff_reachability.py"] = "0" * 64
    with pytest.raises(loop.GameDetected, match="the grader changed"):
        loop.assert_pins_intact(before)


def test_G1_fires_when_a_pinned_file_is_deleted():
    """ABSENT must not compare equal to a hash: deleting the tests that pin the
    auditor is as effective as editing them."""
    with pytest.raises(loop.GameDetected):
        loop.assert_pins_intact({"scripts/does_not_exist.py": "deadbeef"})


def test_G1_is_silent_on_an_untouched_grader():
    """PRECISION -- a pin that fires on a clean tree gets removed by the next
    person who hits it."""
    assert loop.assert_pins_intact(loop.pin()) is None


# --------------------------------------------------------------------------
# G2 -- counting links, not lines carrying links
# --------------------------------------------------------------------------
def test_G2_counts_links_not_lines(tmp_path, monkeypatch):
    """Red team attack 4: 12 links on ONE prose line read as 1 under the old
    per-line count and slipped under --max-links-per-file."""
    dump = " ".join(f"[d{i}](docs/d{i}.md)" for i in range(12))
    monkeypatch.setattr(loop, "changed_markdown", lambda ref: [tmp_path / "H.md"])
    (tmp_path / "H.md").write_text(dump, encoding="utf-8")
    monkeypatch.setattr(loop, "ROOT", tmp_path)
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=f"+{dump}\n", stderr=""),
    )
    out = loop.inspect_edits("HEAD", max_links=3, dump_ratio=0.5, min_context=20)
    assert any("G2" in v and "12 links" in v for v in out)


# --------------------------------------------------------------------------
# G5 -- a run that did not reduce findings is a stall, not a pass
# --------------------------------------------------------------------------
def test_G5_flag_exists_and_is_read_by_main():
    """The claim that failed review was that G5 existed at all. Pin the wiring,
    not just the flag: a parser argument nobody reads is what G4 already was."""
    src = (Path(__file__).parent / "scripts" / "handoff_repair_loop.py").read_text()
    assert "--require-progress" in src
    assert "args.require_progress is not None" in src, "flag defined but never read"


# --------------------------------------------------------------------------
# the meta-test: does the docstring still promise what the code does not do?
# --------------------------------------------------------------------------
@pytest.mark.parametrize("guard,func", [
    ("G4", "assert_input_not_narrowed"),
    ("G4", "tracked_file_count"),
])
def test_a_guard_documented_as_implemented_is_actually_CALLED(guard, func):
    """The original defect: `tracked_file_count()` was defined, cited in the
    docstring as G4, and never called.

    The first version of this very test searched for the function NAME in the
    source and passed on mutated code with the call site deleted -- the `def`
    line alone satisfied it. That is the identical shallow-check defect, made
    inside the test written to catch it. So: parse the AST and require a real
    ast.Call node. Verified by deleting the call site and watching this fail.
    """
    src = (Path(__file__).parent / "scripts" / "handoff_repair_loop.py").read_text()
    doc = src.split('"""')[1]
    if f"{guard} " not in doc or "IMPLEMENTED" not in doc:
        pytest.skip(f"{guard} is not documented as implemented")
    called = {
        node.func.id
        for node in ast.walk(ast.parse(src))
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert func in called, (
        f"{guard} is documented as IMPLEMENTED but {func}() is never called. "
        f"A definition is not an implementation."
    )


def test_the_unclosed_bypass_stays_disclosed():
    """G1 hashes source; CPython executes bytecode. That hole is NOT fixed, and
    the one thing that must not happen is it quietly dropping out of the
    docstring during a later edit -- an undisclosed limit reads as absent."""
    doc = (Path(__file__).parent / "scripts" / "handoff_repair_loop.py").read_text()
    assert "KNOWN UNCLOSED BYPASS" in doc
    assert "bytecode" in doc.lower()
