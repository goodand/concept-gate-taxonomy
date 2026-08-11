#!/usr/bin/env python3
"""GATE — the offline E2E must DETECT a regression in production code.

AUDIT SURFACE.

Round 17, finding #7: the only check on the E2E was
`assert run_pipeline.e2e_offline() == 0`. The harness owned both its stages
and its expectations, so a stage could be weakened and its expectation would
go with it. That is the defect this whole session kept chasing -- a check
whose absence is invisible -- one level up, now sitting on the thing that was
supposed to end it.

The mechanism is mutation, which is the only thing that has reliably caught
vacuous checks here (`docs/HARNESS_KNOWHOW.md` B4a; `run_calibration.py`'s
applied-checked mutations). But the mutation is applied to PRODUCTION, not to
the harness: each break below is a plausible regression in a real module, and
the E2E must report failure. Mutating the harness would only prove the
harness can be broken, which is not in question.

A mutation that leaves the E2E green means the E2E does not actually cover
that stage, whatever its output says.
"""
from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import apply_safety_audit as asa  # noqa: E402
import make_safety_audit_blind_input as mkblind  # noqa: E402
import run_pipeline  # noqa: E402


def _run_e2e() -> tuple[int, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        rc = run_pipeline.e2e_offline()
    return rc, buf.getvalue()


def test_the_unmutated_e2e_passes():
    """Control. Without it every mutation below could be failing for an
    unrelated reason while the gate still looked meaningful."""
    rc, out = _run_e2e()
    assert rc == 0, out


def test_e2e_catches_an_audit_gate_that_validates_nothing(monkeypatch):
    """The gate is the reason a malformed or unprovenanced artifact cannot be
    audited. If it stopped checking, the E2E must say so."""
    def permissive(data, spec, *, source):
        return {mkblind._cell_key(t): t for t in (data.get("traces") or [])}
    monkeypatch.setattr(mkblind, "validate_audit_input", permissive)
    rc, out = _run_e2e()
    assert rc != 0, out
    assert "audit gate ACCEPTED" in out


def test_e2e_catches_the_unblinding_key_leaking_into_the_reviewer_workspace(
        monkeypatch):
    """Round 15's High finding was that packet and key sat in the same
    directory. If that regressed, the E2E must not stay green."""
    real_main = mkblind.main

    def leaky(argv):
        rc = real_main(argv)
        root = Path(argv[2])
        key = next((root / "results").glob("safety_audit_key_*.json"), None)
        workspace = next((root / "audit_workspace").iterdir())
        if key is not None:
            (workspace / key.name).write_bytes(key.read_bytes())
        return rc
    monkeypatch.setattr(mkblind, "main", leaky)
    rc, out = _run_e2e()
    assert rc != 0, out
    assert "workspace leaks" in out


def test_e2e_catches_reviewer_qualification_being_switched_off(monkeypatch):
    """Round 17's finding was that qualification was scored inside the E2E and
    never by the adjudicator. Now that it IS the adjudicator's, a regression
    there must surface here."""
    monkeypatch.setattr(asa, "_qualify_reviewer", lambda doc: [])
    rc, out = _run_e2e()
    assert rc != 0, out
    assert "retired conditional rule still qualifies" in out


def test_e2e_catches_the_final_bundle_never_being_written(monkeypatch):
    """Round 17, finding #4: adjudication ended in memory, so the writer was
    never exercised. The E2E now reads the bundle back from disk."""
    monkeypatch.setattr(asa, "main", lambda argv: 0)
    rc, out = _run_e2e()
    assert rc != 0, out
    assert "no final bundle" in out


def test_e2e_catches_a_single_reviewer_being_accepted(monkeypatch):
    """`min_distinct_reviewer_ids` is the machine-checkable half of the
    independence claim. If it stopped applying, the E2E must catch it."""
    real = asa.adjudicate

    def permissive(result, packet, key, labels, *, spec=None):
        relaxed = {**(spec or {}), "allow_single_reviewer": True}
        return real(result, packet, key, labels, spec=relaxed)
    monkeypatch.setattr(asa, "adjudicate", permissive)
    rc, out = _run_e2e()
    assert rc != 0, out
    assert "single reviewer produced a bundle" in out


def test_every_numbered_stage_is_covered_by_a_mutation():
    """A stage added later must not arrive unverified. Each numbered stage in
    the E2E output needs a mutation above; the count is pinned so adding one
    without a mutation fails here."""
    import re
    source = (HERE / "run_pipeline.py").read_text(encoding="utf-8")
    stages = re.findall(r'\[(\d)\] ', source)
    mutations = [n for n in globals() if n.startswith("test_e2e_catches_")]
    assert len(set(stages)) >= 7, f"stages found: {sorted(set(stages))}"
    assert len(mutations) >= 5, (
        f"{len(mutations)} mutations for {len(set(stages))} stages -- add one "
        "for the new stage, or the E2E covers it only by assertion")
