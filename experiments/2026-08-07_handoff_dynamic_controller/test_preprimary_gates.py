"""Regression tests for the independent pre-primary red-team findings."""

from __future__ import annotations

import json
import multiprocessing
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_live_phase_c as live  # noqa: E402
from _evaluator import frozen_surface_hashes  # noqa: E402

CLAUDE_V2 = json.loads(
    (HERE / "phase_c_claude_mcp_surface_v2_config.json").read_text(encoding="utf-8"))


def _qualification_artifact(spec: dict) -> dict:
    qualification_config = json.loads(
        (HERE / spec["config_file"]).read_text(encoding="utf-8"))
    return {
        "kind": "live-subject-pilot",
        "qualification": {"passed": True},
        "config": qualification_config,
        "config_file": spec["config_file"],
        "config_sha256": live._sha256_path(HERE / spec["config_file"]),
        "n_runs": len(spec["case_ids"]) * len(spec["arms"]),
        "per_arm": {arm: {"n": len(spec["case_ids"])} for arm in spec["arms"]},
        "frozen_surface_hashes": frozen_surface_hashes(),
        "arm_effect_estimable": False,
        "n_per_cell": 1,
    }


def _write_qualifications(result_dir: Path, config: dict = CLAUDE_V2) -> None:
    ledger = result_dir / live.QUALIFICATION_LEDGER_NAME
    for spec in config["primary"]["required_qualification_artifacts"]:
        artifact = _qualification_artifact(spec)
        path = result_dir / spec["file"]
        path.write_text(json.dumps(artifact), encoding="utf-8")
        live._append_jsonl(ledger, {
            "file": path.name,
            "sha256": live._sha256_path(path),
            "config_sha256": artifact["config_sha256"],
            "arms": spec["arms"],
            "case_ids": spec["case_ids"],
        })


def _authorization(qualification_hashes: dict[str, str]) -> dict:
    return {
        "authorized_by": "user-test-fixture",
        "authorized_at": "2026-08-07T22:00:00+09:00",
        "config_file": "phase_c_claude_mcp_surface_v2_config.json",
        "config_sha256": live._sha256_path(
            HERE / "phase_c_claude_mcp_surface_v2_config.json"),
        "qualification_sha256": qualification_hashes,
        "matrix": {
            "case_ids": CLAUDE_V2["primary"]["case_ids"],
            "arms": CLAUDE_V2["primary"]["arms"],
        },
        "max_attempts": 1,
    }


def test_complete_externally_anchored_qualifications_pass(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    assert set(verified) == {
        "live_pilot_claude_mcp_surface_v2.json", "live_pilot_codex_mcp_v7.json"}


def test_self_declared_one_cell_matrix_is_refused(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    path = tmp_path / "live_pilot_claude_mcp_surface_v2.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    artifact["config"]["pilot"] = {"arms": ["S_DYNAMIC"], "case_ids": ["HD01"]}
    artifact["n_runs"] = 1
    artifact["per_arm"] = {"S_DYNAMIC": {"n": 1}}
    path.write_text(json.dumps(artifact), encoding="utf-8")
    with pytest.raises(live.LiveRunError, match="matrix declaration differs"):
        live._assert_primary_qualifications(CLAUDE_V2)


def test_edited_qualification_fails_external_ledger_hash(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    path = tmp_path / "live_pilot_claude_mcp_surface_v2.json"
    artifact = json.loads(path.read_text(encoding="utf-8"))
    artifact["interpretation"] = "edited after qualification"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    with pytest.raises(live.LiveRunError, match="ledger mismatch"):
        live._assert_primary_qualifications(CLAUDE_V2)


def test_missing_qualification_spec_and_v1_primary_fail_closed():
    config = {"primary": {}, "provider": "x", "sandbox_policy": "y"}
    with pytest.raises(live.LiveRunError, match="must be explicit"):
        live._assert_primary_qualifications(config)
    v1 = json.loads((HERE / "phase_c_live_config.json").read_text(encoding="utf-8"))
    with pytest.raises(live.LiveRunError, match="must be explicit"):
        live._assert_primary_qualifications(v1)


def test_cli_has_no_historical_default_config():
    proc = subprocess.run(
        [sys.executable, str(HERE / "run_live_phase_c.py"), "--primary"],
        cwd=HERE, capture_output=True, text=True)
    assert proc.returncode == 2
    assert "--config" in proc.stderr and "required" in proc.stderr


def test_primary_requires_matching_authorization_and_consumes_attempt(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    with pytest.raises(live.LiveRunError, match="authorization file is missing"):
        live._assert_primary_authorization(
            CLAUDE_V2, "phase_c_claude_mcp_surface_v2_config.json", verified,
            CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"])
    authorization_path = tmp_path / live.PRIMARY_AUTHORIZATION_NAME
    authorization_path.write_text(json.dumps(_authorization(verified)), encoding="utf-8")
    authorization_sha, max_attempts = live._assert_primary_authorization(
        CLAUDE_V2, "phase_c_claude_mcp_surface_v2_config.json", verified,
        CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"])
    live._claim_primary_attempt(
        authorization_sha, max_attempts, {"status": "started"})
    _, max_attempts = live._assert_primary_authorization(
        CLAUDE_V2, "phase_c_claude_mcp_surface_v2_config.json", verified,
        CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"])
    with pytest.raises(live.LiveRunError, match="attempt limit exhausted"):
        live._claim_primary_attempt(
            authorization_sha, max_attempts, {"status": "started"})


def test_authorization_rejects_a_different_matrix(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    authorization = _authorization(verified)
    authorization["matrix"]["arms"] = ["S_DYNAMIC"]
    (tmp_path / live.PRIMARY_AUTHORIZATION_NAME).write_text(
        json.dumps(authorization), encoding="utf-8")
    with pytest.raises(live.LiveRunError, match="wrong matrix"):
        live._assert_primary_authorization(
            CLAUDE_V2, "phase_c_claude_mcp_surface_v2_config.json", verified,
            CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"])


def test_judged_payload_hash_is_deterministic_and_sensitive():
    left = live._canonical_json_bytes({"b": 2, "a": 1})
    right = live._canonical_json_bytes({"a": 1, "b": 2})
    changed = live._canonical_json_bytes({"a": 1, "b": 3})
    assert left == right
    assert left != changed


def test_current_pilot_contract_marks_arm_effect_as_not_estimable():
    for name in ("phase_c_codex_mcp_v7_config.json",
                 "phase_c_claude_mcp_surface_v2_config.json"):
        config = json.loads((HERE / name).read_text(encoding="utf-8"))
        assert "no arm effect is estimable" in config["pilot"]["interpretation"]


def test_all_test_modules_are_frozen():
    from _evaluator import FROZEN_SURFACE_FILES
    expected = {path.name for path in HERE.glob("test_*.py")}
    assert expected <= set(FROZEN_SURFACE_FILES)


# --- regressions for the primary_attempt_ledger completeness gap
# (independent review, 2026-08-10, finding #2): before this, the ledger
# recorded ONLY "started" -- no way to distinguish a completed run from a
# rate-limit abort, a crash, or any other failure. "N attempts consumed" was
# really "N attempts started".

def _read_ledger(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_run_phase_records_a_completed_outcome_on_success(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    (tmp_path / live.PRIMARY_AUTHORIZATION_NAME).write_text(
        json.dumps(_authorization(verified)), encoding="utf-8")

    monkeypatch.setattr(live, "_assert_ready", lambda config_path: CLAUDE_V2)
    fake_out = {"n_runs": 4, "qualification": {"failed_cells": []}}

    def fake_body(case_ids, arms, output_path, config, config_path, phase_name):
        # The real _run_phase_body always writes output_path before
        # returning on success; _record_primary_attempt_outcome's
        # "completed" path now hashes that file (finding #4), so the fake
        # must write one too.
        output_path.write_text("{}", encoding="utf-8")
        return fake_out
    monkeypatch.setattr(live, "_run_phase_body", fake_body)

    exit_code = live.run_phase(
        CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"],
        output_name="primary_test_output", phase_name="primary",
        config_path="phase_c_claude_mcp_surface_v2_config.json")
    assert exit_code == 0

    rows = _read_ledger(tmp_path / live.PRIMARY_ATTEMPT_LEDGER_NAME)
    statuses = [row["status"] for row in rows]
    assert statuses == ["started", "completed"], statuses
    assert rows[1]["n_runs"] == 4
    assert rows[1]["output_file"] == rows[0]["output_file"] == "primary_test_output.json"
    # Independent review round 4, finding #2 (2026-08-10): attempt_id and
    # output_sha256 were added but no test checked they actually connect
    # the started/terminal rows to each other or to the real file.
    assert rows[0]["attempt_id"] is not None
    assert rows[0]["attempt_id"] == rows[1]["attempt_id"], (
        "started and completed rows for the same attempt must share attempt_id")
    real_hash = live._sha256_path(tmp_path / "primary_test_output.json")
    assert rows[1]["output_sha256"] == real_hash


def test_output_sha256_changes_if_the_artifact_is_tampered_after_recording(monkeypatch, tmp_path):
    """The recorded output_sha256 is a hash of the file AT COMPLETION TIME.
    If the artifact is edited afterward, re-hashing it must diverge from
    the ledger's recorded value -- otherwise the hash is decorative, not a
    real tamper-evidence mechanism."""
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    (tmp_path / live.PRIMARY_AUTHORIZATION_NAME).write_text(
        json.dumps(_authorization(verified)), encoding="utf-8")
    monkeypatch.setattr(live, "_assert_ready", lambda config_path: CLAUDE_V2)

    def fake_body(case_ids, arms, output_path, config, config_path, phase_name):
        output_path.write_text('{"n_runs": 4}', encoding="utf-8")
        return {"n_runs": 4, "qualification": {"failed_cells": []}}
    monkeypatch.setattr(live, "_run_phase_body", fake_body)

    live.run_phase(
        CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"],
        output_name="primary_tamper_test", phase_name="primary",
        config_path="phase_c_claude_mcp_surface_v2_config.json")
    recorded_hash = _read_ledger(tmp_path / live.PRIMARY_ATTEMPT_LEDGER_NAME)[1]["output_sha256"]

    (tmp_path / "primary_tamper_test.json").write_text('{"n_runs": 999}', encoding="utf-8")
    assert live._sha256_path(tmp_path / "primary_tamper_test.json") != recorded_hash


def test_attempt_id_is_unique_across_separate_attempts(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    authorization = _authorization(verified)
    authorization["max_attempts"] = 2
    (tmp_path / live.PRIMARY_AUTHORIZATION_NAME).write_text(
        json.dumps(authorization), encoding="utf-8")
    monkeypatch.setattr(live, "_assert_ready", lambda config_path: CLAUDE_V2)

    def fake_body(case_ids, arms, output_path, config, config_path, phase_name):
        output_path.write_text("{}", encoding="utf-8")
        return {"n_runs": 1, "qualification": {"failed_cells": []}}
    monkeypatch.setattr(live, "_run_phase_body", fake_body)

    for i in range(2):
        live.run_phase(
            CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"],
            output_name=f"primary_unique_id_test_{i}", phase_name="primary",
            config_path="phase_c_claude_mcp_surface_v2_config.json")

    rows = _read_ledger(tmp_path / live.PRIMARY_ATTEMPT_LEDGER_NAME)
    started_ids = [r["attempt_id"] for r in rows if r["status"] == "started"]
    assert len(started_ids) == 2
    assert len(set(started_ids)) == 2, "attempt_id must be unique per attempt"


def test_failed_attempt_records_output_sha256_when_file_exists(monkeypatch, tmp_path):
    """A failure AFTER the output file was written (e.g. a post-write step
    crashes) must still record a real hash of what was actually written,
    not just output_file_exists=True with no way to verify its content."""
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    (tmp_path / live.PRIMARY_AUTHORIZATION_NAME).write_text(
        json.dumps(_authorization(verified)), encoding="utf-8")
    monkeypatch.setattr(live, "_assert_ready", lambda config_path: CLAUDE_V2)

    def fake_body(case_ids, arms, output_path, config, config_path, phase_name):
        output_path.write_text('{"partial": true}', encoding="utf-8")
        raise RuntimeError("crash after writing output")
    monkeypatch.setattr(live, "_run_phase_body", fake_body)

    with pytest.raises(RuntimeError):
        live.run_phase(
            CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"],
            output_name="primary_partial_write_test", phase_name="primary",
            config_path="phase_c_claude_mcp_surface_v2_config.json")

    failed_row = _read_ledger(tmp_path / live.PRIMARY_ATTEMPT_LEDGER_NAME)[1]
    assert failed_row["output_file_exists"] is True
    assert failed_row["output_sha256"] == live._sha256_path(
        tmp_path / "primary_partial_write_test.json")


def test_run_phase_records_a_failed_outcome_on_exception(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    (tmp_path / live.PRIMARY_AUTHORIZATION_NAME).write_text(
        json.dumps(_authorization(verified)), encoding="utf-8")

    monkeypatch.setattr(live, "_assert_ready", lambda config_path: CLAUDE_V2)
    def boom(*a, **k):
        raise RuntimeError("simulated provider rate limit")
    monkeypatch.setattr(live, "_run_phase_body", boom)

    with pytest.raises(RuntimeError, match="simulated provider rate limit"):
        live.run_phase(
            CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"],
            output_name="primary_test_output_2", phase_name="primary",
            config_path="phase_c_claude_mcp_surface_v2_config.json")

    rows = _read_ledger(tmp_path / live.PRIMARY_ATTEMPT_LEDGER_NAME)
    statuses = [row["status"] for row in rows]
    assert statuses == ["started", "failed"], statuses
    assert "simulated provider rate limit" in rows[1]["error"]
    assert rows[1]["output_file_exists"] is False


def test_max_attempts_three_allows_exactly_three_real_attempts(monkeypatch, tmp_path):
    """Regression for independent review round 3, finding #1: each attempt
    now writes TWO ledger rows ("started" + a terminal status, Amendment 23
    finding #2). Counting every row toward max_attempts halved the real
    limit -- reproduced 2026-08-10: with max_attempts=3, a 3rd claim was
    refused after only 2 completed attempts (4 rows already present).
    max_attempts must mean 3 real attempts, not 3 ledger rows."""
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    _write_qualifications(tmp_path)
    verified = live._assert_primary_qualifications(CLAUDE_V2)
    authorization = _authorization(verified)
    authorization["max_attempts"] = 3
    (tmp_path / live.PRIMARY_AUTHORIZATION_NAME).write_text(
        json.dumps(authorization), encoding="utf-8")

    monkeypatch.setattr(live, "_assert_ready", lambda config_path: CLAUDE_V2)

    def fake_body(case_ids, arms, output_path, config, config_path, phase_name):
        output_path.write_text("{}", encoding="utf-8")
        return {"n_runs": 4, "qualification": {"failed_cells": []}}
    monkeypatch.setattr(live, "_run_phase_body", fake_body)

    for i in range(3):
        exit_code = live.run_phase(
            CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"],
            output_name=f"primary_test_output_attempt{i}", phase_name="primary",
            config_path="phase_c_claude_mcp_surface_v2_config.json")
        assert exit_code == 0, f"attempt {i + 1}/3 was refused"

    rows = _read_ledger(tmp_path / live.PRIMARY_ATTEMPT_LEDGER_NAME)
    assert len(rows) == 6, f"expected 3 started + 3 completed rows, got {len(rows)}"
    assert [r["status"] for r in rows] == ["started", "completed"] * 3

    with pytest.raises(live.LiveRunError, match="attempt limit exhausted"):
        live.run_phase(
            CLAUDE_V2["primary"]["case_ids"], CLAUDE_V2["primary"]["arms"],
            output_name="primary_test_output_attempt3", phase_name="primary",
            config_path="phase_c_claude_mcp_surface_v2_config.json")


# --- concurrency (independent review round 4, finding #3, 2026-08-10) -----
# No prior test exercised real OS-level file locking under concurrent
# access. Uses multiprocessing (not threads) so flock is exercised across
# genuinely separate processes/file descriptors, matching how two real
# `run_live_phase_c.py --primary` invocations would actually race.

def _concurrent_claim_worker(results_dir_str: str, authorization_sha: str,
                             max_attempts: int, worker_id: int) -> str:
    """Module-level (picklable under spawn) worker: re-imports the module
    fresh in the child process rather than relying on any inherited state."""
    import sys as _sys
    from pathlib import Path as _Path
    here = _Path(__file__).resolve().parent
    if str(here) not in _sys.path:
        _sys.path.insert(0, str(here))
    import run_live_phase_c as _live
    _live.RESULTS_DIR = _Path(results_dir_str)
    try:
        _live._claim_primary_attempt(authorization_sha, max_attempts,
                                     {"status": "started", "worker_id": worker_id})
        return "ok"
    except _live.LiveRunError:
        return "blocked"


def test_concurrent_claims_enforce_the_attempt_limit_exactly(tmp_path):
    """max_attempts=3 raced by 10 concurrent processes must let EXACTLY 3
    through, not more (a race in the read-count-then-write critical
    section would let extras slip past) and not fewer (the lock must not
    corrupt or lose a row)."""
    sha = "concurrency-test-sha"
    max_attempts = 3
    n_workers = 10
    ctx = multiprocessing.get_context("fork")
    with ctx.Pool(processes=n_workers) as pool:
        outcomes = pool.starmap(
            _concurrent_claim_worker,
            [(str(tmp_path), sha, max_attempts, i) for i in range(n_workers)])
    assert outcomes.count("ok") == max_attempts, outcomes
    assert outcomes.count("blocked") == n_workers - max_attempts

    ledger_path = tmp_path / live.PRIMARY_ATTEMPT_LEDGER_NAME
    rows = _read_ledger(ledger_path)
    assert len(rows) == max_attempts, (
        f"expected exactly {max_attempts} rows (no corruption/loss), got {len(rows)}")
    assert all(r["status"] == "started" for r in rows)


def _concurrent_terminal_worker(results_dir_str: str, authorization_sha: str, idx: int) -> str:
    """Module-level (picklable under spawn) companion to
    _concurrent_claim_worker, for racing a claim against terminal appends."""
    import sys as _sys
    from pathlib import Path as _Path
    here = _Path(__file__).resolve().parent
    if str(here) not in _sys.path:
        _sys.path.insert(0, str(here))
    import run_live_phase_c as _live
    _live.RESULTS_DIR = _Path(results_dir_str)
    _live._record_primary_attempt_outcome(
        authorization_sha, f"out{idx}.json", "completed",
        attempt_id=f"id{idx}", extra={"n_runs": idx})
    return "done"


def test_concurrent_claim_and_terminal_append_do_not_corrupt_the_ledger(tmp_path):
    """A claim (read-count-then-write) racing against several terminal
    appends (pure locked appends) against the SAME file must never produce
    a line that fails to parse as JSON, regardless of write order."""
    sha = "concurrency-test-sha-2"
    ledger_path = tmp_path / live.PRIMARY_ATTEMPT_LEDGER_NAME

    ctx = multiprocessing.get_context("fork")
    jobs = (
        [(_concurrent_claim_worker, (str(tmp_path), sha, 20, i)) for i in range(5)]
        + [(_concurrent_terminal_worker, (str(tmp_path), sha, i)) for i in range(5)])
    with ctx.Pool(processes=10) as pool:
        results = [pool.apply_async(fn, args) for fn, args in jobs]
        [r.get() for r in results]

    rows = _read_ledger(ledger_path)  # raises if any line fails to parse
    assert len(rows) == 10
