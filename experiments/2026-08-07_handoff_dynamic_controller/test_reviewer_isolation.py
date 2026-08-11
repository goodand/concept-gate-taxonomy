#!/usr/bin/env python3
"""Tests for the sandboxed reviewer launcher — AUDIT SURFACE.

Round 20, finding #3: the rubric said an agent reviewer that can read the
repository is not blinded, and nothing implemented it. `doctor` read booleans
out of a file the reviewer submitted, so a hand-written PASS was
indistinguishable from a probe result -- a vacuous guard by another name.

Every test here feeds a VIOLATING input. The positive path is asserted too,
because a launcher that denies everything (including the packet) would
otherwise look perfect.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reviewer_runner as rr  # noqa: E402

ASSIGNMENT = HERE / "safety_audit_reviewer_assignment.json"


@pytest.fixture
def bundled(tmp_path):
    packet = tmp_path / "packet.json"
    packet.write_text(json.dumps({"reviewer_packet": [{"blind_id": "R0000"}]}),
                      encoding="utf-8")
    return rr.build_reviewer_bundle(packet, tmp_path / "bundle")


def _skip_without_sandbox():
    if not rr.SANDBOX.is_file():
        pytest.skip("sandbox-exec unavailable; isolation is BLOCKED here, "
                    "which is the honest state, not a pass")


def test_the_bundle_holds_the_packet_and_nothing_else(bundled):
    assert [p.name for p in bundled.parent.iterdir()] == ["packet.json"]


def test_a_symlinked_packet_is_refused(tmp_path):
    """The public-bundle precedent refuses links rather than following them,
    because otherwise the exclusion is walked around by pointing a link at
    results/."""
    real = tmp_path / "real.json"
    real.write_text("{}", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(real)
    with pytest.raises(rr.ReviewerRunnerError, match="symlink"):
        rr.build_reviewer_bundle(link, tmp_path / "b")


def test_the_probes_run_both_directions(bundled):
    """A launcher that denies everything would score perfectly on the forbidden
    probes. The allowed probe is what distinguishes isolation from a broken
    sandbox."""
    _skip_without_sandbox()
    probes = rr.probe_isolation(bundled)
    assert probes["allowed_probe_passed"] is True, probes["allowed_detail"]
    assert {p["probe"] for p in probes["forbidden_probes"]} == {
        "answer_key", "preregistration", "results_dir", "host_transcripts"}


def test_the_answer_key_and_repository_are_not_reachable(bundled):
    _skip_without_sandbox()
    doc = rr.run_reviewer(bundled, "test-reviewer")
    leaked = [p["probe"] for p in doc["forbidden_probes"] if p["reachable"]]
    assert not leaked, f"reviewer could reach {leaked}"
    assert doc["status"] == "PASS"


def test_a_blocked_sandbox_is_not_a_pass(bundled, monkeypatch):
    """Round 17's fail-open, in the new component: if the allowed probe fails
    the boundary was never exercised, and that is BLOCKED."""
    monkeypatch.setattr(rr, "_reachable", lambda profile, path: (False, "denied"))
    doc = rr.run_reviewer(bundled, "test-reviewer")
    assert doc["status"] == "BLOCKED"


def test_a_leak_is_a_failure(bundled, monkeypatch):
    monkeypatch.setattr(rr, "_reachable", lambda profile, path: (True, ""))
    doc = rr.run_reviewer(bundled, "test-reviewer")
    assert doc["status"] == "FAIL"


def test_a_hand_written_receipt_is_refused(bundled):
    """THE test for this finding. A reviewer's own claim is not evidence."""
    forged = {"reviewer_id": "x", "status": "PASS", "packet_sha256": "0" * 64,
              "assignment_sha256": "0" * 64, "sandbox_profile_sha256": "0" * 64,
              "allowed_probe_passed": True, "forbidden_probes": []}
    with pytest.raises(rr.ReviewerRunnerError, match="not produced by the launcher"):
        rr.verify_isolation_receipt(forged, packet=bundled, assignment=ASSIGNMENT)


def test_an_edited_receipt_is_refused(bundled):
    _skip_without_sandbox()
    doc = rr.run_reviewer(bundled, "test-reviewer")
    doc["status"] = "PASS"
    doc["forbidden_probes"] = []          # erase the evidence, keep the verdict
    with pytest.raises(rr.ReviewerRunnerError, match="has been edited"):
        rr.verify_isolation_receipt(doc, packet=bundled, assignment=ASSIGNMENT)


def test_a_receipt_bound_to_another_packet_is_refused(bundled, tmp_path):
    _skip_without_sandbox()
    doc = rr.run_reviewer(bundled, "test-reviewer")
    other = tmp_path / "other.json"
    other.write_text("{}", encoding="utf-8")
    with pytest.raises(rr.ReviewerRunnerError, match="another packet"):
        rr.verify_isolation_receipt(doc, packet=other, assignment=ASSIGNMENT)


def test_the_receipt_hash_covers_every_field(bundled):
    _skip_without_sandbox()
    doc = rr.run_reviewer(bundled, "test-reviewer")
    for field in ("reviewer_id", "status", "packet_sha256",
                  "sandbox_profile_sha256", "allowed_probe_passed"):
        mutated = {**doc, field: "tampered"}
        with pytest.raises(rr.ReviewerRunnerError, match="has been edited"):
            rr.verify_isolation_receipt(mutated, packet=bundled,
                                        assignment=ASSIGNMENT)


def test_the_launcher_cli_refuses_a_symlinked_packet(tmp_path, capsys):
    """Driven through main(), because test_cli_wiring_coverage requires it --
    and because round 15's lesson was that a helper-only test inherits the
    helper's blind spots."""
    real = tmp_path / "real.json"
    real.write_text("{}", encoding="utf-8")
    link = tmp_path / "link.json"
    link.symlink_to(real)
    rc = rr.main(["reviewer_runner.py", str(link), "cli-test", str(tmp_path / "out")])
    assert rc == 2
    assert "symlink" in capsys.readouterr().err


def test_the_launcher_cli_prints_usage_when_underfed(capsys):
    assert rr.main(["reviewer_runner.py"]) == 2
    assert "usage" in capsys.readouterr().err
