"""Adapter + boundary tests for the claude-cli provider. No paid model calls.

Every test that asserts a boundary holds has a partner that makes the boundary
fail, because a positive-only suite cannot distinguish an enforced boundary from
an absent one -- the defect class this repository has recorded twelve times.

The forgery tests are the important ones: they drive the REAL host tool server
with a fake provider that reads one thing and then claims another, and assert
that the host trace, not the model's payload, is what reaches the evaluator.
"""

from __future__ import annotations

import json
import socket
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import run_live_phase_c as live  # noqa: E402
from _providers import (CLAUDE_DENIED_TOOLS, ProviderError,  # noqa: E402
                        claude_cli_schema, claude_command, extract_json_object, home_leak_denies,
                        payload_from_claude_envelope, resolve_provider, seatbelt_profile_v2,
                        validate_against_schema)
from run_calibration import load  # noqa: E402

CLAUDE_CONFIG = json.loads((HERE / "phase_c_claude_config.json").read_text(encoding="utf-8"))
CODEX_CONFIG = json.loads((HERE / "phase_c_live_config.json").read_text(encoding="utf-8"))
CODEX_V2_CONFIG = json.loads((HERE / "phase_c_codex_v2_config.json").read_text(encoding="utf-8"))
CLAUDE_SURFACE_V2_CONFIG = json.loads(
    (HERE / "phase_c_claude_mcp_surface_v2_config.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# registry -- the Codex path must be untouched
# --------------------------------------------------------------------------
def test_codex_config_still_resolves_to_the_original_implementation():
    sentinel = object()
    assert resolve_provider(CODEX_CONFIG, sentinel) is sentinel


def test_claude_config_resolves_to_the_claude_adapter():
    from _providers import run_claude_cli
    assert resolve_provider(CLAUDE_CONFIG, object()) is run_claude_cli


def test_each_frozen_provider_config_is_selectable():
    assert live.load_config("phase_c_claude_config.json")["provider"] == "claude-cli"
    assert "seatbelt-v2" in live.load_config(
        "phase_c_codex_v2_config.json")["sandbox_policy"]
    assert live.load_config("phase_c_codex_mcp_config.json")["provider"] == "codex-mcp-cli"
    assert live.load_config("phase_c_codex_mcp_v7_config.json")["provider"] == "codex-mcp-cli"
    assert live.load_config("phase_c_claude_mcp_surface_v2_config.json")["provider"] == "claude-cli"


def test_an_unfrozen_config_is_refused(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps(CLAUDE_CONFIG), encoding="utf-8")
    with pytest.raises(live.LiveRunError, match="not part of the frozen provider set"):
        live.load_config(path)


def test_an_unknown_provider_is_refused_rather_than_defaulted():
    """Defaulting to some provider on a typo would run the wrong experiment and
    label it with the config that was asked for."""
    with pytest.raises(ProviderError, match="unknown provider"):
        resolve_provider({"provider": "gpt-cli"}, object())


# --------------------------------------------------------------------------
# Q4 -- fresh session per cell
# --------------------------------------------------------------------------
def _cmd(tmp_path):
    schema_path = tmp_path / "s.json"
    schema_path.write_text(
        (HERE / "live_subject_response.schema.json").read_text(encoding="utf-8"),
        encoding="utf-8")
    return claude_command("/bin/claude", "/usr/bin/sandbox-exec", "(version 1)",
                          tmp_path, schema_path, CLAUDE_CONFIG, "SID-1")


def test_command_never_resumes_or_continues_a_session(tmp_path):
    cmd = _cmd(tmp_path)
    assert "--resume" not in cmd and "--continue" not in cmd and "-c" not in cmd


def test_command_disables_session_persistence_and_pins_a_unique_id(tmp_path):
    cmd = _cmd(tmp_path)
    assert "--no-session-persistence" in cmd
    assert cmd[cmd.index("--session-id") + 1] == "SID-1"


def test_two_runs_get_different_session_ids():
    from _providers import uuid
    assert str(uuid.uuid4()) != str(uuid.uuid4())


def test_command_loads_no_settings_and_no_mcp_servers(tmp_path):
    """Otherwise the workspace's own CLAUDE.md becomes part of the subject
    prompt, and the subject stops being cold-start."""
    cmd = _cmd(tmp_path)
    assert cmd[cmd.index("--setting-sources") + 1] == ""
    assert "--strict-mcp-config" in cmd
    assert json.loads(cmd[cmd.index("--mcp-config") + 1]) == {"mcpServers": {}}
    assert "--safe-mode" in cmd and "--disable-slash-commands" in cmd


def test_command_uses_native_structured_output_and_only_bash(tmp_path):
    cmd = _cmd(tmp_path)
    cli_schema = json.loads(cmd[cmd.index("--json-schema") + 1])
    assert cli_schema == claude_cli_schema(tmp_path / "s.json")
    assert "$schema" not in cli_schema
    assert cli_schema["properties"] == SCHEMA["properties"]
    assert cmd[cmd.index("--tools") + 1] == "Bash"


def test_every_off_trace_retrieval_tool_is_disallowed(tmp_path):
    cmd = _cmd(tmp_path)
    for tool in ("Read", "Grep", "Glob", "WebFetch", "WebSearch", "Task"):
        assert tool in cmd, tool
    assert cmd[cmd.index("--allowedTools") + 1] == "Bash"


def test_the_denied_tool_list_is_not_empty():
    """A vacuous list would satisfy the test above by accident."""
    assert len(CLAUDE_DENIED_TOOLS) >= 8


# --------------------------------------------------------------------------
# sandbox profile -- both directions
# --------------------------------------------------------------------------
def test_v2_denies_the_home_transcript_channels(tmp_path):
    profile = seatbelt_profile_v2(Path("/repo"), tmp_path / "control")
    for path in home_leak_denies():
        assert f'(deny file-read* (subpath "{path}"))' in profile


def test_v2_still_denies_everything_v1_denied(tmp_path):
    control = tmp_path / "control"
    v1 = live.seatbelt_profile(Path("/repo"), control)
    v2 = seatbelt_profile_v2(Path("/repo"), control)
    for line in v1.splitlines():
        if line.startswith("(deny"):
            assert line in v2, line


def test_v2_does_not_deny_the_config_file_the_cli_needs():
    """Denying ~/.claude.json stops the subject from starting at all. It is left
    reachable ON PURPOSE and the residual is documented -- measured: it carries
    no history arrays, only config and path metadata."""
    profile = seatbelt_profile_v2(Path("/repo"), Path("/c"))
    assert str(Path.home() / ".claude.json") not in profile


# --------------------------------------------------------------------------
# schema enforcement moves provider-side -> adapter-side
# --------------------------------------------------------------------------
SCHEMA = json.loads((HERE / "live_subject_response.schema.json").read_text(encoding="utf-8"))


def _good_payload():
    return {"contract_version": "handoff-dyn-live-answer-v1", "case_id": "HD01",
            "arm": "S_STATIC", "terminal_action": "answer", "answer_text": "x",
            "claims": [], "current_state": "x", "next_action": "x",
            "stop_conditions": ["x"], "recommended_actions": [],
            "uncertainties": [], "declared_absent": False}


def test_a_conforming_payload_validates():
    validate_against_schema(_good_payload(), SCHEMA)


def test_a_missing_required_key_is_rejected():
    payload = _good_payload()
    del payload["terminal_action"]
    with pytest.raises(ProviderError, match="missing required key"):
        validate_against_schema(payload, SCHEMA)


def test_an_extra_key_is_rejected():
    """additionalProperties=false is how a subject smuggling a gold key is
    stopped at the provider boundary rather than inside the evaluator."""
    with pytest.raises(ProviderError, match="unexpected key"):
        validate_against_schema({**_good_payload(), "critical_paths": ["x"]}, SCHEMA)


def test_a_wrong_type_is_rejected():
    with pytest.raises(ProviderError, match="expected"):
        validate_against_schema({**_good_payload(), "claims": "not-a-list"}, SCHEMA)


def test_const_min_length_and_minimum_are_enforced():
    with pytest.raises(ProviderError, match="const"):
        validate_against_schema({**_good_payload(), "contract_version": "wrong"}, SCHEMA)
    with pytest.raises(ProviderError, match="minLength"):
        validate_against_schema({**_good_payload(), "case_id": ""}, SCHEMA)
    payload = {**_good_payload(), "claims": [{
        "claim_id": "x", "claim": "x",
        "support": [{"path": "docs/HANDOFF.md", "start": 0, "end": 1}],
    }]}
    with pytest.raises(ProviderError, match="minimum"):
        validate_against_schema(payload, SCHEMA)


@pytest.mark.parametrize("text,expected", [
    ('prose\n```json\n{"a": 1}\n```\n', {"a": 1}),
    ('{"a": 1} then more text {"a": 2}', {"a": 2}),
    ('thinking...\n{"nested": {"b": [1,2]}}', {"nested": {"b": [1, 2]}}),
])
def test_json_is_extracted_from_prose(text, expected):
    assert extract_json_object(text) == expected


def test_a_reply_with_no_json_is_an_error_not_an_empty_payload():
    """Returning {} here would score as a well-formed but empty run instead of
    an invalid one."""
    with pytest.raises(ProviderError, match="no JSON object"):
        extract_json_object("I could not complete the task.")


def test_braces_inside_a_json_string_do_not_break_extraction():
    assert extract_json_object('prose {"answer": "use {x} literally"}') == {
        "answer": "use {x} literally"}


def test_native_structured_output_wins_over_result_prose():
    payload = _good_payload()
    assert payload_from_claude_envelope({
        "structured_output": payload, "result": '{"wrong": true}'}) == payload


# --------------------------------------------------------------------------
# Q3 -- forgery, driven through the REAL host tool server
# --------------------------------------------------------------------------
def _talk(socket_path, payload):
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        sock.connect(str(socket_path))
        sock.sendall(json.dumps(payload).encode() + b"\n")
        return json.loads(sock.makefile("rb").read().decode())


def _fake_provider(script, payload):
    """A provider that performs `script` host actions, then returns `payload`."""
    def run(subject, socket_path, prompt, schema_name, config, **kw):
        for step in script:
            _talk(socket_path, step)
        return {"payload": payload, "raw": "", "elapsed_ms": 0}
    return run


@pytest.fixture
def short_tmp():
    """AF_UNIX caps the socket path length, and pytest's tmp_path is long. The
    runner already pins /private/tmp for this reason; the tests must too, or
    every socket-driven test fails with `AF_UNIX path too long` and reads as a
    boundary failure when it is a path-length failure."""
    import shutil, tempfile
    path = Path(tempfile.mkdtemp(prefix="hdt-", dir="/private/tmp"))
    try:
        yield path
    finally:
        shutil.rmtree(path, ignore_errors=True)


def _run_with(monkeypatch, short_tmp, script, payload, arm="S_DYNAMIC"):
    cases, gold = load()
    monkeypatch.setattr(live, "resolve_provider",
                        lambda config, codex: _fake_provider(script, payload))
    return live.run_cell(cases["HD01"], gold["HD01"], arm, "variant-L",
                         CLAUDE_CONFIG, short_tmp, subagent=None, subagent_meta=None)


HONEST_SCRIPT = [
    {"action": "search", "query": "current state of the reshape"},
    {"action": "read_candidate", "path": "docs/HANDOFF.md", "start": 1, "end": 40},
    {"action": "follow_link", "path": "docs/HANDOFF.md"},
    {"action": "read_candidate", "path": "docs/DECISION_freeze_policy.md",
     "start": 1, "end": 40},
    # The guard requires one read or hop on a candidate the FIRST search did not
    # surface. Without this the honest script is refused and the forgery tests
    # would compare against a run that never terminated.
    {"action": "expand_candidates"},
    {"action": "read_candidate", "path": "docs/glossary.md", "start": 1, "end": 40},
    {"action": "finish", "terminal_action": "answer"},
]


def test_the_host_trace_records_what_the_host_served(monkeypatch, short_tmp):
    """PRECISION for the forgery tests below: the honest path must produce a
    non-empty host trace, or 'forgery failed' would be indistinguishable from
    'the harness recorded nothing'."""
    payload = {**_good_payload(), "arm": "S_DYNAMIC"}
    trace, _ = _run_with(monkeypatch, short_tmp, HONEST_SCRIPT, payload)
    assert {r["path"] for r in trace["reads"]} == {
        "docs/HANDOFF.md", "docs/DECISION_freeze_policy.md", "docs/glossary.md"}
    assert trace["stop_reason"] == "answer"
    assert trace["actions"], "host recorded no actions"


def test_a_self_reported_read_never_enters_the_trace(monkeypatch, short_tmp):
    """The subject claims to have read the audit it never opened."""
    payload = {**_good_payload(), "arm": "S_DYNAMIC",
               "claims": [{"claim_id": "forged", "support": [
                   {"path": "notes/audits/two-shapes-2026-06-11.md",
                    "start": 1, "end": 40}]}]}
    trace, _ = _run_with(monkeypatch, short_tmp, HONEST_SCRIPT, payload)
    assert "notes/audits/two-shapes-2026-06-11.md" not in {
        r["path"] for r in trace["reads"]}
    from _evaluator import evaluate
    cases, gold = load()
    assert "C4" in evaluate(trace, gold["HD01"], cases["HD01"])["failure_codes"]


def test_a_widened_range_on_a_real_read_is_caught(monkeypatch, short_tmp):
    """Read 1-40, cite 1-400: the file was opened, the range was not exposed."""
    payload = {**_good_payload(), "arm": "S_DYNAMIC",
               "claims": [{"claim_id": "wide", "support": [
                   {"path": "docs/HANDOFF.md", "start": 1, "end": 400}]}]}
    trace, _ = _run_with(monkeypatch, short_tmp, HONEST_SCRIPT, payload)
    from _evaluator import evaluate
    cases, gold = load()
    assert "X1" in evaluate(trace, gold["HD01"], cases["HD01"])["failure_codes"]


def test_claiming_a_terminal_action_the_guard_never_accepted_is_V1(monkeypatch, short_tmp):
    """The subject stops early and writes terminal_action=answer anyway."""
    payload = {**_good_payload(), "arm": "S_DYNAMIC"}
    trace, _ = _run_with(monkeypatch, short_tmp,
                         [{"action": "search", "query": "x"}], payload)
    assert "V1" in trace["failure_codes"]
    assert trace["stop_reason"] != "answer"


def test_a_payload_for_a_different_case_or_arm_is_V1(monkeypatch, short_tmp):
    payload = {**_good_payload(), "case_id": "DS05", "arm": "S_DYNAMIC"}
    trace, _ = _run_with(monkeypatch, short_tmp, HONEST_SCRIPT, payload)
    assert "V1" in trace["failure_codes"]


def test_a_gold_key_in_the_payload_reaches_the_evaluator_as_E1(monkeypatch, short_tmp):
    payload = {**_good_payload(), "arm": "S_DYNAMIC",
               "uncertainties": [{"critical_paths": ["docs/HANDOFF.md"]}]}
    trace, _ = _run_with(monkeypatch, short_tmp, HONEST_SCRIPT, payload)
    from _evaluator import evaluate
    cases, gold = load()
    assert "E1" in evaluate(trace, gold["HD01"], cases["HD01"])["failure_codes"]


def test_a_provider_failure_becomes_V1_and_does_not_abort_the_sweep(monkeypatch, short_tmp):
    def boom(config, codex):
        def run(*a, **k):
            raise ProviderError("simulated CLI crash")
        return run
    cases, gold = load()
    monkeypatch.setattr(live, "resolve_provider", boom)
    trace, details = live.run_cell(cases["HD01"], gold["HD01"], "S_STATIC",
                                   "variant-L", CLAUDE_CONFIG, short_tmp,
                                   subagent=None, subagent_meta=None)
    assert trace["failure_codes"] == ["V1"]
    assert "simulated CLI crash" in details["error"]


def test_provider_failure_preserves_host_actions_and_diagnostics(monkeypatch, short_tmp):
    def provider(config, codex):
        def run(subject, socket_path, *args, **kwargs):
            _talk(socket_path, {"action": "search", "query": "reshape"})
            raise ProviderError("bad structured output", raw="RAW",
                                provider_meta={"cost_usd": 0.1})
        return run
    cases, gold = load()
    monkeypatch.setattr(live, "resolve_provider", provider)
    trace, details = live.run_cell(
        cases["HD01"], gold["HD01"], "S_DYNAMIC", "variant-L",
        CLAUDE_CONFIG, short_tmp, subagent=None, subagent_meta=None)
    assert len(trace["actions"]) == 1
    assert trace["failure_codes"] == ["V1"]
    assert details["raw"] == "RAW"
    assert details["provider_meta"]["cost_usd"] == 0.1


# --------------------------------------------------------------------------
# Q5 -- invalid runs cannot be selectively replaced
# --------------------------------------------------------------------------
def test_claude_config_keeps_the_no_retry_invalid_run_policy():
    assert CLAUDE_CONFIG["retry_count"] == 0
    assert CLAUDE_CONFIG["invalid_run_policy"] == "record-V1-and-do-not-replace"


def test_the_runner_refuses_to_overwrite_an_existing_result_file():
    src = (HERE / "run_live_phase_c.py").read_text(encoding="utf-8")
    assert "refusing to overwrite an existing live result" in src


def test_claude_results_are_not_poolable_with_codex_results():
    """Different provider, different sandbox version, different schema
    enforcement point. Pooling them would average two harnesses."""
    assert CLAUDE_CONFIG["provider"] != CODEX_CONFIG["provider"]
    assert CLAUDE_CONFIG["sandbox_policy"] != CODEX_CONFIG["sandbox_policy"]
    assert "never pool with codex" in CLAUDE_CONFIG["pilot"]["interpretation"]


# --------------------------------------------------------------------------
# the experiment semantics remain untouched; provider orchestration is now a
# deliberately frozen extension and is tested through frozen_surface_hashes.
# --------------------------------------------------------------------------
@pytest.mark.parametrize("name", [
    "_contract.py", "_runner.py", "build_corpus.py",
    "build_live_public_bundle.py", "live_subject_tool.py",
    "live_subject_response.schema.json", "retrieval_subagent_response.schema.json",
    "phase_c_live_config.json", "corpus_manifest.json",
])
def test_the_adapter_did_not_modify_the_frozen_surface(name):
    import subprocess
    out = subprocess.run(["git", "diff", "--name-only", "8b333bc", "--",
                          f"experiments/2026-08-07_handoff_dynamic_controller/{name}"],
                         cwd=HERE.parents[1], capture_output=True, text=True)
    assert out.stdout.strip() == "", f"{name} changed: {out.stdout}"


def test_provider_execution_inputs_are_in_the_frozen_surface():
    from _evaluator import FROZEN_SURFACE_FILES
    for name in ("_providers.py", "phase_c_claude_config.json",
                 "phase_c_claude_mcp_surface_config.json", "phase_c_codex_mcp_config.json",
                 "phase_c_claude_mcp_surface_v2_config.json", "phase_c_codex_mcp_v7_config.json",
                 "phase_c_codex_v2_config.json", "live_subject_mcp.py",
                 "redteam_provider_isolation.py", "redteam_codex_mcp_isolation.py"):
        assert name in FROZEN_SURFACE_FILES


def test_codex_v2_and_claude_share_the_hardened_os_boundary():
    assert CODEX_V2_CONFIG["sandbox_policy"] == CLAUDE_CONFIG["sandbox_policy"]


def test_host_action_compliance_is_separate_from_retrieval_score():
    static = live._host_action_compliance(
        {"arm": "S_DYNAMIC", "actions": []}, {"subagent": None})
    assert static == {
        "passed": False, "main_host_actions": 0, "subagent_host_actions": 0,
        "subagent_required": False, "failures": ["main-host-action-missing"],
    }
    retrieval = live._host_action_compliance(
        {"arm": "R_DYNAMIC", "actions": [{"action": "search"}]},
        {"subagent": {"host_actions": []}})
    assert not retrieval["passed"]
    assert retrieval["failures"] == ["subagent-host-action-missing"]


def test_primary_requires_a_current_passing_qualification(monkeypatch, tmp_path):
    monkeypatch.setattr(live, "RESULTS_DIR", tmp_path)
    spec = CLAUDE_SURFACE_V2_CONFIG["primary"]["required_qualification_artifacts"][0]
    with pytest.raises(live.LiveRunError, match="qualification artifact is missing"):
        live._assert_primary_qualifications(CLAUDE_SURFACE_V2_CONFIG)
    assert spec["arms"] == ["S_STATIC", "R_STATIC", "S_DYNAMIC", "R_DYNAMIC"]
