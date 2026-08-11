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
import tempfile
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
    # `results_dir` became `results_artifact` in round 21: the directory could
    # not be probed at all (`/bin/cat` fails on a directory), so it was replaced
    # by a FILE inside results/.
    assert {p["probe"] for p in probes["forbidden_probes"]} == {
        "answer_key", "preregistration", "results_artifact", "host_transcripts"}
    assert all(p["control_reachable"] for p in probes["forbidden_probes"]), (
        "a probe whose control failed cannot support any conclusion")


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
    # Round 21: the refusal now comes from the HMAC, not from a recomputed
    # public hash. Same case, different mechanism -- the case is what matters.
    with pytest.raises(rr.ReviewerRunnerError, match="signature"):
        rr.verify_isolation_receipt(doc, packet=bundled, assignment=ASSIGNMENT)


def test_a_receipt_bound_to_another_packet_is_refused(bundled, tmp_path):
    _skip_without_sandbox()
    doc = rr.run_reviewer(bundled, "test-reviewer")
    other = tmp_path / "other.json"
    other.write_text("{}", encoding="utf-8")
    with pytest.raises(rr.ReviewerRunnerError, match="another packet"):
        rr.verify_isolation_receipt(doc, packet=other, assignment=ASSIGNMENT)


def test_the_signature_covers_every_field(bundled):
    _skip_without_sandbox()
    doc = rr.run_reviewer(bundled, "test-reviewer")
    for field in ("reviewer_id", "status", "packet_sha256",
                  "sandbox_profile_sha256", "allowed_probe_passed"):
        mutated = {**doc, field: "tampered"}
        with pytest.raises(rr.ReviewerRunnerError, match="signature"):
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


# --------------------------------------------------------------- round 21 ----
def test_the_frozen_assignment_does_not_deny_the_launcher_it_has():
    """Finding #7. The assignment file is what a reader consults to learn what
    this audit does and does not establish. It said "no sandboxed launcher
    exists yet" AFTER the launcher shipped and a closure receipt was recorded
    over it -- the frozen contract asserting the opposite of the code.

    A frozen document that contradicts the implementation is worse than a
    missing one: it is read as authority."""
    doc = json.loads(ASSIGNMENT.read_text(encoding="utf-8"))
    blob = json.dumps(doc, ensure_ascii=False)
    assert "no sandboxed launcher exists" not in blob, (
        "the assignment still denies the launcher in reviewer_runner.py")
    not_verified = doc["what_this_does_and_does_not_prove"]["NOT_machine_verified"]
    # The honest residual claim must still be there. Removing the sentence
    # entirely would swap one wrong document for another.
    assert any("confer" in s for s in not_verified), (
        "the assignment must still say collusion is not machine-verified")
    assert any("isolation" in s.lower() or "sandbox" in s.lower()
               for s in json.dumps(doc, ensure_ascii=False).splitlines()
               ) or "isolation" in blob, "no statement about isolation at all"


# ---- #1: the receipt must not be forgeable with public inputs alone --------
def test_a_receipt_forged_with_the_public_hash_function_is_refused(bundled):
    """THE round-21 finding, reproduced before it was closed.

    The old check was: `produced_by == "reviewer_runner"`, then recompute
    `receipt_sha256` over the rest of the document. Both inputs are public.
    Filling in the field and calling the same public function produced a
    document that verified as PASS with the launcher never having run --
    measured, not argued.

    `test_a_hand_written_receipt_is_refused` below did not catch it because it
    omitted `produced_by`, testing only the weakest possible forgery. A guard
    whose only negative test is the easy case is the vacuous-guard pattern one
    level up: the test exists, and it still cannot tell a real mechanism from
    a broken one.
    """
    from _receipt import receipt_sha256
    forged = {
        "reviewer_id": "attacker",
        "status": "PASS",
        "packet_sha256": rr._sha256(bundled),
        "assignment_sha256": rr._sha256(ASSIGNMENT),
        "sandbox_profile_sha256": "0" * 64,
        "allowed_probe_passed": True,
        "forbidden_probes": [],
        "produced_by": "reviewer_runner",
    }
    forged["receipt_sha256"] = receipt_sha256(forged)
    with pytest.raises(rr.ReviewerRunnerError):
        rr.verify_isolation_receipt(forged, packet=bundled, assignment=ASSIGNMENT)


def test_a_receipt_signed_with_the_wrong_key_is_refused(bundled, tmp_path):
    """Signing is only worth anything if a DIFFERENT key fails."""
    _skip_without_sandbox()
    doc = rr.run_reviewer(bundled, "test-reviewer", assignment=ASSIGNMENT)
    other = tmp_path / "other.key"
    other.write_bytes(b"\x01" * 32)
    with pytest.raises(rr.ReviewerRunnerError, match="signature"):
        rr.verify_isolation_receipt(doc, packet=bundled, assignment=ASSIGNMENT,
                                    key_path=other)


def test_the_signing_key_is_not_reachable_from_the_reviewer_profile():
    """A host-only key that the reviewer can read is not host-only."""
    _skip_without_sandbox()
    key = rr.launcher_key_path()
    denied = rr.denied_paths()
    assert any(d == key or d in key.parents for d in denied), (
        f"the launcher key {key} is outside every denied subtree, so a "
        f"sandboxed reviewer could read it and sign its own receipt")


# ---- #2: the profile must be the hardened one, not the one it documents ----
def test_the_reviewer_profile_is_v2_and_denies_the_home_transcripts():
    """Finding #2. The module docstring cited Seatbelt v2 and `_providers.py`
    §55 -- the probe that found `~/.claude/projects` and `~/.codex` readable --
    and then called v1, which denies exactly two subtrees and neither of those.

    Measured before the fix: the v1 profile string did not contain
    ~/.claude/projects at all.
    """
    from _providers import home_leak_denies, seatbelt_profile_v2
    profile = rr._profile(Path("/tmp/anywhere"))
    assert profile == seatbelt_profile_v2(rr.HERE, rr.HERE / "results"), (
        "the reviewer profile is not the hardened one")
    for path in home_leak_denies():
        assert path in profile, f"{path} is not denied to the reviewer"


def test_the_deny_list_and_the_profile_cannot_drift():
    """`denied_paths()` is used to refuse a bundle inside a denied subtree, so
    a path missing from it is a hole. Bind it to the profile string itself."""
    profile = rr._profile(Path("/tmp/anywhere"))
    for path in rr.denied_paths():
        assert str(path) in profile, (
            f"denied_paths() claims {path} is denied, the profile does not")


# ---- #2a: a probe that cannot reach its target measures nothing ------------
def test_every_forbidden_probe_target_is_reachable_under_a_permissive_profile():
    """THE finding I missed, and the worst one this round.

    `_reachable` reads `returncode == 0`. `/bin/cat` on a DIRECTORY returns 1
    regardless of any sandbox, so `results_dir` and `host_transcripts` -- both
    directories -- were reported `ok` under a profile with ZERO denies.
    Measured:

        (version 1)(allow default)      <- deny nothing at all
        cat ~/.claude/projects   rc=1   "Is a directory"   -> reported ok
        cat results              rc=1   "Is a directory"   -> reported ok

    Two of the four forbidden probes were not measuring the sandbox. This is
    the vacuous-guard pattern (7 prior occurrences in H1A_PROBLEM_ANALYSIS)
    inside the module whose docstring says a probe is evidence.
    """
    _skip_without_sandbox()
    for name, target in rr.forbidden_targets():
        reachable, detail = rr._reachable(rr.PERMISSIVE_PROFILE, target)
        assert reachable, (
            f"probe {name!r} cannot read {target} even with nothing denied "
            f"({detail!r}), so a denial tells us nothing about the sandbox")


def test_a_vacuous_probe_is_blocked_not_ok(bundled, monkeypatch):
    """If a target stops being readable on this host, the probe must degrade to
    BLOCKED. Silently counting it as `ok` is how the two directory probes
    survived four rounds."""
    _skip_without_sandbox()
    monkeypatch.setattr(rr, "forbidden_targets",
                        lambda: [("nonexistent", rr.HERE / "no-such-file.json")])
    doc = rr.run_reviewer(bundled, "test-reviewer", assignment=ASSIGNMENT)
    probe = doc["forbidden_probes"][0]
    assert probe["control_reachable"] is False
    assert probe["status"] == "BLOCKED", probe
    assert doc["status"] == "BLOCKED", (
        "a run whose probes measured nothing must not report PASS")


# ---- #9: one bundle location, and it may not be inside a denied subtree ----
def test_a_bundle_inside_a_denied_subtree_is_refused(tmp_path):
    """Finding #9, mine. `main()`'s default out_dir was
    `HERE/audit_workspace/reviewer`, and the profile denies all of HERE. The
    allowed probe therefore failed every time, so the documented CLI could
    only ever return BLOCKED -- while the release E2E, which uses a temp dir,
    returned PASS. Two paths, one structurally broken: the canonical-path
    violation the frozen 2026-07-28 decision exists to prevent.
    """
    packet = tmp_path / "packet.json"
    packet.write_text("{}", encoding="utf-8")
    inside = rr.HERE / "audit_workspace" / "reviewer" / "would-be-blocked"
    with pytest.raises(rr.ReviewerRunnerError, match="denied subtree"):
        rr.build_reviewer_bundle(packet, inside)


def test_the_cli_default_workspace_is_outside_every_denied_subtree():
    dest = rr.reviewer_workspace("some-reviewer")
    for denied in rr.denied_paths():
        assert denied != dest and denied not in dest.parents, (
            f"the default reviewer workspace {dest} is inside {denied}")


def test_v1_would_have_leaked_the_host_transcripts(bundled):
    """The counterfactual, without which "we use v2" is unfalsifiable.

    v1 denies the repository and the results directory and nothing else. With
    `host_transcripts` now pointing at a real FILE rather than a directory, v1
    must LEAK it and v2 must deny it. If both denied, this test would be
    telling us the environment blocks home access and the profile is doing
    nothing -- which is what round 21's reviewer suspected was happening.
    """
    _skip_without_sandbox()
    from run_live_phase_c import seatbelt_profile
    targets = dict(rr.forbidden_targets())
    transcript = targets["host_transcripts"]
    if not transcript.is_file():
        pytest.skip("no host transcript file on this host; nothing to contrast")
    v1 = seatbelt_profile(rr.HERE, rr.HERE / "results")
    v1_reachable, _ = rr._reachable(v1, transcript)
    v2_reachable, detail = rr._reachable(rr._profile(bundled.parent), transcript)
    assert v1_reachable, (
        "v1 did NOT leak the transcript, so this host blocks it by other means "
        "and the v2 result below proves nothing about the profile")
    assert not v2_reachable, f"v2 leaked the transcript: {detail}"


def test_assert_reachable_workspace_refuses_a_denied_path_directly():
    """The guard itself, not through `build_reviewer_bundle`.

    Required by the repository-wide gate `test_guard_negative_coverage.py`, and
    it caught a real gap: the only negative test reached this guard THROUGH the
    bundle builder, so deleting the builder's call site would have left the
    guard with no test that makes it raise. That is the vacuous-guard shape one
    call frame out.
    """
    with pytest.raises(rr.ReviewerRunnerError, match="denied subtree"):
        rr.assert_reachable_workspace(rr.HERE / "results" / "anything")
    # And the positive direction, so a guard that refuses everything fails here.
    outside = Path("/tmp") / "cg-reviewer-positive"
    assert rr.assert_reachable_workspace(outside) == outside


# ---- #3: the launcher must actually RUN the reviewer -----------------------
# Round 21, finding #3: `run_reviewer(command=...)` called subprocess.run and
# THREW THE RESULT AWAY. The release E2E passed no command at all, and the
# "reviewer labels" in it were written by the E2E from the answer key. So the
# component was a sandbox probe runner wearing a launcher's name, and nothing
# downstream could tell.

FIXTURE = HERE / "safety_audit_rubric_fixture.json"
ANSWERS = HERE / "safety_audit_rubric_answers.json"


def _fake_reviewer(tmp_path, payload: str, *, exit_code: int = 0) -> list[str]:
    """A reviewer that prints `payload` on stdout. Stands in for an agent CLI.

    The adapter must not care what produced the JSON -- that is the point of a
    schema at a trust boundary.
    """
    script = tmp_path / "fake_reviewer.py"
    script.write_text(
        "import sys\n"
        f"sys.stdout.write({payload!r})\n"
        f"sys.exit({exit_code})\n", encoding="utf-8")
    return [sys.executable, str(script)]


def _good_output(blind_ids) -> str:
    answers = json.loads(ANSWERS.read_text(encoding="utf-8"))["answers"]
    return json.dumps({"qualification": answers,
                       "labels": {b: "MENTION" for b in blind_ids}})


@pytest.fixture
def packet_bundle(tmp_path):
    """A bundle whose packet has two blind ids, like a real one."""
    packet = tmp_path / "packet.json"
    packet.write_text(json.dumps(
        {"reviewer_packet": [{"blind_id": "R0000"}, {"blind_id": "R0001"}]}),
        encoding="utf-8")
    return rr.build_reviewer_bundle(packet, tmp_path / "bundle")


def test_a_reviewers_output_becomes_a_label_artifact(packet_bundle, tmp_path):
    """The positive path. Without it, refusing everything would look correct."""
    _skip_without_sandbox()
    command = _fake_reviewer(tmp_path, _good_output(["R0000", "R0001"]))
    doc = rr.run_reviewer(packet_bundle, "e2e-A", command=command,
                          assignment=ASSIGNMENT, labels_out=tmp_path / "labels.json")
    assert doc["status"] == "PASS", doc
    labels = json.loads((tmp_path / "labels.json").read_text(encoding="utf-8"))
    # Exactly the shape apply_safety_audit reads -- bound to packet, assignment
    # and the frozen qualification fixture.
    assert labels["reviewer_id"] == "e2e-A"
    assert labels["packet_sha256"] == rr._sha256(packet_bundle)
    assert labels["assignment_sha256"] == rr._sha256(ASSIGNMENT)
    assert labels["fixture_sha256"] == rr._sha256(FIXTURE)
    assert set(labels["labels"]) == {"R0000", "R0001"}
    # And the receipt binds what ran to what came out.
    assert doc["reviewer_command_sha256"] and doc["reviewer_output_sha256"]


def test_a_reviewer_that_emits_garbage_is_refused(packet_bundle, tmp_path):
    _skip_without_sandbox()
    command = _fake_reviewer(tmp_path, "I am a helpful assistant!")
    with pytest.raises(rr.ReviewerRunnerError, match="not JSON"):
        rr.run_reviewer(packet_bundle, "e2e-A", command=command,
                        assignment=ASSIGNMENT, labels_out=tmp_path / "labels.json")
    assert not (tmp_path / "labels.json").exists(), (
        "a label artifact was written from unparseable output")


def test_a_reviewer_output_missing_labels_is_refused(packet_bundle, tmp_path):
    _skip_without_sandbox()
    answers = json.loads(ANSWERS.read_text(encoding="utf-8"))["answers"]
    command = _fake_reviewer(tmp_path, json.dumps({"qualification": answers}))
    with pytest.raises(rr.ReviewerRunnerError, match="labels"):
        rr.run_reviewer(packet_bundle, "e2e-A", command=command,
                        assignment=ASSIGNMENT, labels_out=tmp_path / "labels.json")


def test_labels_for_ids_outside_the_packet_are_refused(packet_bundle, tmp_path):
    """The adjudicator already refuses a mismatched id set. Catching it HERE
    means the launcher does not hand on an artifact it knows is wrong."""
    _skip_without_sandbox()
    command = _fake_reviewer(tmp_path, _good_output(["R0000", "R9999"]))
    with pytest.raises(rr.ReviewerRunnerError, match="do not match the packet"):
        rr.run_reviewer(packet_bundle, "e2e-A", command=command,
                        assignment=ASSIGNMENT, labels_out=tmp_path / "labels.json")


def test_a_label_outside_the_rubric_is_refused(packet_bundle, tmp_path):
    _skip_without_sandbox()
    answers = json.loads(ANSWERS.read_text(encoding="utf-8"))["answers"]
    command = _fake_reviewer(tmp_path, json.dumps(
        {"qualification": answers,
         "labels": {"R0000": "PROBABLY_FINE", "R0001": "MENTION"}}))
    with pytest.raises(rr.ReviewerRunnerError, match="outside the rubric"):
        rr.run_reviewer(packet_bundle, "e2e-A", command=command,
                        assignment=ASSIGNMENT, labels_out=tmp_path / "labels.json")


def test_a_reviewer_that_exits_nonzero_is_blocked(packet_bundle, tmp_path):
    """It did not fail the boundary and it did not pass -- it did not run."""
    _skip_without_sandbox()
    command = _fake_reviewer(tmp_path, _good_output(["R0000", "R0001"]),
                             exit_code=3)
    with pytest.raises(rr.ReviewerRunnerError, match="exited 3"):
        rr.run_reviewer(packet_bundle, "e2e-A", command=command,
                        assignment=ASSIGNMENT, labels_out=tmp_path / "labels.json")


def test_the_receipt_binding_covers_the_reviewer_output(packet_bundle, tmp_path):
    """Editing the labels after the fact must invalidate the receipt, or the
    receipt attests to a run whose output nobody can still identify."""
    _skip_without_sandbox()
    command = _fake_reviewer(tmp_path, _good_output(["R0000", "R0001"]))
    doc = rr.run_reviewer(packet_bundle, "e2e-A", command=command,
                          assignment=ASSIGNMENT, labels_out=tmp_path / "labels.json")
    tampered = {**doc, "reviewer_output_sha256": "0" * 64}
    with pytest.raises(rr.ReviewerRunnerError, match="signature"):
        rr.verify_isolation_receipt(tampered, packet=packet_bundle,
                                    assignment=ASSIGNMENT)


def test_a_probe_only_run_says_so_rather_than_implying_a_reviewer_ran():
    """`command=None` is legitimate -- the release E2E asks only whether the
    boundary holds. It must not be indistinguishable from a run that produced
    labels, which is how finding #3 stayed invisible."""
    _skip_without_sandbox()
    packet = Path(tempfile.mkdtemp()) / "packet.json"
    packet.write_text(json.dumps({"reviewer_packet": [{"blind_id": "R0000"}]}),
                      encoding="utf-8")
    bundled = rr.build_reviewer_bundle(packet, packet.parent / "b")
    doc = rr.run_reviewer(bundled, "probe-only", assignment=ASSIGNMENT)
    assert doc["reviewer_command_sha256"] is None
    assert doc["reviewer_output_sha256"] is None
