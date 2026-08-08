"""Regression tests for the independent pre-primary red-team findings."""

from __future__ import annotations

import json
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
