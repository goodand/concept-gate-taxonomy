"""Unit checks for the Phase C boundary, without calling a model provider."""

from __future__ import annotations

import hashlib
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


def test_static_follow_returns_and_enforces_the_exact_next_read_for_a_linkless_authority():
    cases, _ = load()
    corpus = Corpus(HERE / "public_corpus" / "variant-L")
    state = LiveToolState(corpus, cases["HD01"], initial_candidates=None,
                          guard_enabled=True, strict_static=True)
    assert state.dispatch({"action": "search", "query": cases["HD01"]["query"]})["ok"]
    assert state.dispatch({"action": "expand_candidates"})["ok"]
    assert state.dispatch({"action": "read_candidate", "path": "docs/HANDOFF.md",
                           "start": 1, "end": 40})["ok"]
    follow = state.dispatch({"action": "follow_link", "path": "docs/DECISION_freeze_policy.md"})
    assert follow["ok"]
    assert follow["result_paths"] == []
    assert follow["static_next"] == {
        "action": "read_candidate", "path": "docs/DECISION_freeze_policy.md"}
    assert state.dispatch({"action": "read_candidate", "path": "docs/DECISION_freeze_policy.md",
                           "start": 1, "end": 40})["ok"]


def test_static_follow_rejects_a_different_read_path_before_the_required_read():
    cases, _ = load()
    corpus = Corpus(HERE / "public_corpus" / "variant-L")
    state = LiveToolState(corpus, cases["HD01"], initial_candidates=None,
                          guard_enabled=True, strict_static=True)
    assert state.dispatch({"action": "search", "query": cases["HD01"]["query"]})["ok"]
    assert state.dispatch({"action": "expand_candidates"})["ok"]
    assert state.dispatch({"action": "read_candidate", "path": "docs/HANDOFF.md",
                           "start": 1, "end": 40})["ok"]
    assert state.dispatch({"action": "follow_link", "path": "docs/DECISION_freeze_policy.md"})["ok"]
    rejected = state.dispatch({"action": "read_candidate", "path": "docs/directory-cleanup-plan.md",
                               "start": 1, "end": 40})
    assert not rejected["ok"]
    assert "expected read_candidate" in rejected["error"]
    assert state.trace_fields()["stop_reason"] == "V1"


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


def test_codex_mcp_config_is_a_separate_qualification_surface():
    config = load_config("phase_c_codex_mcp_config.json")
    assert config["provider"] == "codex-mcp-cli"
    assert config["tool_policy"] == "single-stdio-mcp-handoff_action-v1"
    assert config["retry_count"] == 0


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


# --------------------------------------------------------------- round 22 ----
def test_the_artifact_kind_is_a_mapping_not_a_ternary():
    """Round 22, found while planning `--canary` and NOT named by the reviewer.

        "kind": "live-subject-pilot" if phase_name == "pilot" \\
                else "live-subject-primary"

    Any phase that is not "pilot" became `live-subject-primary`. So adding a new
    phase name -- which is exactly what `--canary` is -- would have made a
    1-cell canary DECLARE ITSELF a primary result, and
    `make_safety_audit_blind_input` accepts that kind. That is the same
    contamination path round 21 closed for `run_pipeline --primary`: a run that
    is not primary being filed as one.

    A mapping refuses an unregistered phase instead of guessing."""
    import run_live_phase_c as live
    assert hasattr(live, "PHASE_ARTIFACTS")
    assert set(live.PHASE_ARTIFACTS) == {"pilot", "primary", "canary"}
    assert live.PHASE_ARTIFACTS["canary"]["kind"] == "live-subject-canary"
    assert live.PHASE_ARTIFACTS["primary"]["kind"] == "live-subject-primary"
    assert live.PHASE_ARTIFACTS["pilot"]["kind"] == "live-subject-pilot"
    with pytest.raises(live.LiveRunError, match="unregistered phase"):
        live.phase_artifact_fields("smoke-ish")
    source = (HERE / "run_live_phase_c.py").read_text(encoding="utf-8")
    assert 'else "live-subject-primary"' not in source, (
        "the ternary is still there; an unknown phase still becomes primary")


def test_a_canary_artifact_is_not_estimable_and_says_so():
    import run_live_phase_c as live
    fields = live.phase_artifact_fields("canary")
    assert fields["arm_effect_estimable"] is False
    assert "canary" in fields["interpretation"]
    assert "primary" not in fields["interpretation"]


def _ledger_hashes():
    """SHA-256 of both ledgers. Round 22: the reviewer asked for exactly this --
    compare the FILES before and after, not whether a function was called or a
    string appears in the source."""
    import run_live_phase_c as live
    out = {}
    for name in (live.QUALIFICATION_LEDGER_NAME, "primary_attempt_ledger.jsonl"):
        path = live.RESULTS_DIR / name
        out[name] = (hashlib.sha256(path.read_bytes()).hexdigest()
                     if path.is_file() else None)
    return out


@pytest.mark.parametrize("cases,arms,why", [
    (["HD01", "HD02"], ["S_STATIC"], "two cases"),
    (["HD01"], ["S_STATIC", "R_STATIC"], "two arms"),
    ([], ["S_STATIC"], "no case"),
    (["HD01"], [], "no arm"),
])
def test_a_canary_that_is_not_exactly_one_cell_is_refused(cases, arms, why):
    """A canary is ONE cell. Two cells is a small pilot, and a small pilot that
    calls itself a canary is how a measurement gets made by accident."""
    import run_live_phase_c as live
    before = _ledger_hashes()
    with pytest.raises(live.LiveRunError, match="exactly one"):
        live.run_phase(cases, arms, output_name="never_written",
                       phase_name="canary",
                       config_path="phase_c_claude_mcp_surface_v3_config.json")
    # The refusal path must not touch either ledger either.
    assert _ledger_hashes() == before, f"{why}: a refused canary changed a ledger"


def test_a_canary_refuses_to_overwrite_an_existing_result():
    import run_live_phase_c as live
    existing = sorted(live.RESULTS_DIR.glob("live_pilot_*.json"))
    if not existing:
        pytest.skip("no prior live result to collide with")
    before = _ledger_hashes()
    with pytest.raises(live.LiveRunError, match="refusing to overwrite"):
        live.run_phase(["HD01"], ["S_STATIC"],
                       output_name=existing[0].stem, phase_name="canary",
                       config_path="phase_c_claude_mcp_surface_v3_config.json")
    assert _ledger_hashes() == before


def test_the_canary_phase_calls_no_privileged_function():
    """`run_phase` gates every privileged action on `phase_name == "primary"`
    and `_record_qualification` on `== "pilot"`, so a new phase inherits nothing.
    This pins that structure: if someone rewrites those conditions, a canary
    could start claiming attempts."""
    import ast
    src = (HERE / "run_live_phase_c.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "run_phase")
    privileged = {"_assert_primary_qualifications", "_assert_primary_authorization",
                  "_claim_primary_attempt", "_record_primary_attempt_outcome"}
    for node in ast.walk(fn):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id in privileged):
            # find the enclosing If and require it to test phase_name == "primary"
            guarded = any(
                isinstance(anc, ast.If) and "primary" in ast.unparse(anc.test)
                and "phase_name" in ast.unparse(anc.test)
                for anc in ast.walk(fn)
                if isinstance(anc, ast.If) and node in list(ast.walk(anc)))
            assert guarded, (
                f"{node.func.id} is reachable without a phase_name == 'primary' "
                "guard; a canary could claim an attempt")


def test_the_qualification_ledger_records_what_actually_ran():
    """Round 22, the reviewer's finding C. `_record_qualification` read
    `out["config"]["pilot"]["arms"]` -- the CONFIG -- not the arms `run_phase`
    was given. A 1-cell `--pilot` run therefore wrote a ledger entry declaring
    the config's FULL matrix.

    The primary gate still refuses such an artifact (`n_runs`, `per_arm`), so it
    is not an authorization bypass -- it is a permanent false declaration in an
    append-only ledger, which nobody can remove."""
    import ast
    src = (HERE / "run_live_phase_c.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.FunctionDef) and n.name == "_record_qualification")
    body = ast.unparse(fn)
    assert 'pilot["arms"]' not in body and "pilot['arms']" not in body, (
        "the ledger still records the config's matrix instead of the run's")
    assert "case_ids" in [a.arg for a in fn.args.args] or "case_ids" in body, (
        "_record_qualification cannot record what ran unless it is told")
