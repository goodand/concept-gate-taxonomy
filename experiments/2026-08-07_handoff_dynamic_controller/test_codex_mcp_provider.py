"""Unit tests for the Codex OAuth-parent / MCP-only capability boundary."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _providers import (CODEX_MCP_DISABLED_FEATURES, ProviderError,
                        _codex_event_summary, codex_mcp_command,
                        sanitize_provider_raw)


def _config() -> dict:
    return json.loads((HERE / "phase_c_codex_mcp_v7_config.json").read_text(encoding="utf-8"))


def test_codex_mcp_command_has_exactly_one_server_and_disables_native_tools(tmp_path):
    subject = tmp_path / "subject"
    command = codex_mcp_command("codex", subject, subject / "host.sock", subject / "schema.json",
                                subject / "run" / "out.json", _config())
    assert "--dangerously-bypass-approvals-and-sandbox" not in command
    assert "--approve-for-me" in command
    assert "--sandbox" not in command
    overrides = [command[i + 1] for i, part in enumerate(command[:-1]) if part == "-c"]
    assert 'approval_policy="never"' in overrides
    assert command.count("--disable") == len(CODEX_MCP_DISABLED_FEATURES)
    assert {command[i + 1] for i, part in enumerate(command[:-1]) if part == "--disable"} == set(
        CODEX_MCP_DISABLED_FEATURES)
    overrides = [command[i + 1] for i, part in enumerate(command[:-1]) if part == "-c"]
    assert sum(item.startswith("mcp_servers.handoff.") for item in overrides) == 4
    assert 'mcp_servers.handoff.enabled_tools=["handoff_action"]' in overrides
    assert any(item.startswith("mcp_servers.handoff.env=") for item in overrides)
    assert not any("mcp_servers." in item and "handoff" not in item for item in overrides)


def test_event_checker_allows_only_the_named_mcp_tool():
    raw = "\n".join((
        json.dumps({"type": "thread.started"}),
        json.dumps({"type": "item.completed", "item": {
            "type": "mcp_tool_call", "name": "handoff_action"}}),
    ))
    summary = _codex_event_summary(raw)
    assert summary["mcp_tools"] == ["handoff_action"]
    with pytest.raises(ProviderError, match="forbidden"):
        _codex_event_summary(json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "command": "cat hidden_gold/gold.json"}}))
    with pytest.raises(ProviderError, match="forbidden"):
        _codex_event_summary(json.dumps({"type": "item.completed", "item": {
            "type": "mcp_tool_call", "name": "another_tool"}}))


def test_raw_sanitizer_removes_provider_session_and_thread_identifiers():
    raw = json.dumps({"session_id": "s", "thread_id": "t", "keep": {"session_id": "x"}})
    sanitized = sanitize_provider_raw(raw)
    assert "session_id" not in sanitized
    assert "thread_id" not in sanitized
    assert json.loads(sanitized) == {"keep": {}}
