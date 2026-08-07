"""Unit checks for the Phase C boundary, without calling a model provider."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from build_live_public_bundle import BundleError, build_bundle, verify_bundle
from _runner import Corpus
from run_calibration import load
from run_live_phase_c import (LiveRunError, LiveToolState, _subagent_output,
                              load_config, seatbelt_profile)


def test_public_bundle_has_only_task_and_client_on_subject_surface(tmp_path):
    bundle = tmp_path / "bundle"
    manifest = build_bundle(bundle, "variant-L", "HD01")
    subject_files = {path.relative_to(bundle / "subject").as_posix()
                     for path in (bundle / "subject").rglob("*") if path.is_file()}
    assert subject_files == {
        "task.json", "live_subject_tool.py", "live_subject_response.schema.json",
        "retrieval_subagent_response.schema.json",
    }
    task = json.loads((bundle / "subject" / "task.json").read_text(encoding="utf-8"))
    assert task["id"] == "HD01"
    assert not any("gold" in key or "expected" in key for key in task)
    assert (bundle / "control" / "corpus" / "docs" / "HANDOFF.md").is_file()
    verify_bundle(bundle, manifest)


def test_bundle_postcheck_rejects_an_unexpected_or_modified_input(tmp_path):
    bundle = tmp_path / "bundle"
    manifest = build_bundle(bundle, "variant-L", "HD01")
    (bundle / "subject" / "task.json").write_text("{}", encoding="utf-8")
    with pytest.raises(BundleError, match="drift"):
        verify_bundle(bundle, manifest)


def test_bundle_postcheck_allows_only_the_declared_subject_run_directory(tmp_path):
    bundle = tmp_path / "bundle"
    manifest = build_bundle(bundle, "variant-L", "HD01")
    run = bundle / "subject" / "run"
    run.mkdir()
    (run / "final.json").write_text("{}", encoding="utf-8")
    verify_bundle(bundle, manifest)
    (bundle / "subject" / "surprise.txt").write_text("not an output", encoding="utf-8")
    with pytest.raises(BundleError, match="drift"):
        verify_bundle(bundle, manifest)


def test_guard_rejects_early_finish_then_accepts_real_graph_walk():
    cases, _, = load()
    corpus = Corpus(HERE / "public_corpus" / "variant-L")
    state = LiveToolState(corpus, cases["HD01"], initial_candidates=None,
                          guard_enabled=True)
    early = state.dispatch({"action": "finish", "terminal_action": "answer"})
    assert not early["ok"]
    assert "need" in early["reason"]

    search = state.dispatch({"action": "search", "query": cases["HD01"]["query"]})
    assert search["ok"]
    handoff = "docs/HANDOFF.md"
    follow = state.dispatch({"action": "follow_link", "path": handoff})
    assert follow["ok"]
    target = next(path for path in follow["result_paths"]
                  if path not in state.guard.first_search_paths)
    read = state.dispatch({"action": "read_candidate", "path": target,
                           "start": 1, "end": 40})
    assert read["ok"]
    finished = state.dispatch({"action": "finish", "terminal_action": "answer"})
    assert finished["ok"]
    assert state.trace_fields()["stop_reason"] == "answer"


def test_static_host_rejects_an_out_of_sequence_action():
    cases, _, = load()
    corpus = Corpus(HERE / "public_corpus" / "variant-L")
    state = LiveToolState(corpus, cases["HD01"], initial_candidates=None,
                          guard_enabled=True, strict_static=True)
    response = state.dispatch({"action": "follow_link", "path": "docs/HANDOFF.md"})
    assert not response["ok"]
    assert state.trace_fields()["stop_reason"] == "V1"
    assert "V1" in state.trace_fields()["failure_codes"]


def test_static_host_allows_the_fixed_finish_recovery_suffix():
    cases, _, = load()
    corpus = Corpus(HERE / "public_corpus" / "variant-L")
    state = LiveToolState(corpus, cases["HD01"], initial_candidates=None,
                          guard_enabled=True, strict_static=True)
    assert state.dispatch({"action": "search", "query": cases["HD01"]["query"]})["ok"]
    assert state.dispatch({"action": "expand_candidates"})["ok"]
    assert state.dispatch({"action": "read_candidate", "path": "docs/HANDOFF.md",
                           "start": 1, "end": 40})["ok"]
    assert state.dispatch({"action": "follow_link", "path": "docs/HANDOFF.md"})["ok"]
    assert state.dispatch({"action": "read_candidate",
                           "path": "docs/DECISION_freeze_policy.md",
                           "start": 1, "end": 40})["ok"]
    refused = state.dispatch({"action": "finish", "terminal_action": "answer"})
    assert not refused["ok"]
    # This path is exposed by expansion but was not in the first search pool.
    assert state.dispatch({"action": "read_candidate",
                           "path": "docs/directory-cleanup-plan.md",
                           "start": 1, "end": 40})["ok"]
    assert state.dispatch({"action": "finish", "terminal_action": "answer"})["ok"]


def test_subagent_may_report_a_narrower_range_inside_its_host_read():
    cases, _, = load()
    corpus = Corpus(HERE / "public_corpus" / "variant-L")
    state = LiveToolState(corpus, cases["HD01"], initial_candidates=None,
                          guard_enabled=False)
    assert state.dispatch({"action": "search", "query": "reshape next action"})["ok"]
    assert state.dispatch({"action": "read_candidate", "path": "docs/HANDOFF.md",
                           "start": 1, "end": 40})["ok"]
    payload = {
        "contract_version": "handoff-dyn-subagent-v1",
        "candidate_paths": ["docs/HANDOFF.md"],
        "read_ranges": [{"path": "docs/HANDOFF.md", "start": 5, "end": 9}],
        "search_trace": [], "uncertainty": "candidate only",
    }
    assert _subagent_output(payload, state)["candidate_paths"] == ["docs/HANDOFF.md"]
    payload["read_ranges"][0]["end"] = 41
    with pytest.raises(LiveRunError, match="unobserved"):
        _subagent_output(payload, state)


def test_live_config_matches_contract_limits():
    config = load_config()
    assert config["provider"] == "codex-cli"
    assert config["retry_count"] == 0
    assert config["invalid_run_policy"] == "record-V1-and-do-not-replace"
    assert config["sandbox_policy"].endswith("codex-bypass-in-external-sandbox")


def test_codex_output_schema_declares_types_for_const_and_enum_properties():
    for name in ("live_subject_response.schema.json",
                 "retrieval_subagent_response.schema.json"):
        schema = json.loads((HERE / name).read_text(encoding="utf-8"))
        stack = [schema]
        while stack:
            node = stack.pop()
            if not isinstance(node, dict):
                continue
            if "const" in node or "enum" in node:
                assert "type" in node, f"{name} has an untyped const/enum node: {node}"
            stack.extend(node.get("properties", {}).values())
            items = node.get("items")
            if isinstance(items, dict):
                stack.append(items)


def test_codex_output_schema_avoids_provider_rejected_unique_items():
    for name in ("live_subject_response.schema.json",
                 "retrieval_subagent_response.schema.json"):
        assert "uniqueItems" not in (HERE / name).read_text(encoding="utf-8")


def test_seatbelt_profile_denies_repo_and_host_control():
    profile = seatbelt_profile(Path("/repo/Project_in_progress"), Path("/tmp/control"))
    assert '(deny file-read* (subpath "/repo/Project_in_progress"))' in profile
    assert '(deny file-write* (subpath "/tmp/control"))' in profile
    assert "(allow default)" in profile
