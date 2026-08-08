#!/usr/bin/env python3
"""Fail-closed preflight for the OAuth-parent / single-MCP Codex adapter.

This is deliberately a protocol red-team, not a model performance result. It
checks the launch contract, hostile raw event examples, narrow action inputs,
and the bridge source before a paid qualification is permitted.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _evaluator import frozen_surface_hashes  # noqa: E402
from _providers import (CODEX_MCP_DISABLED_FEATURES, ProviderError,  # noqa: E402
                        _codex_event_summary, codex_mcp_command)


def check(name: str, passed: bool, detail: str = "") -> dict:
    print(f"  [{'ok' if passed else 'FAIL':>4}] {name}")
    return {"check": name, "passed": passed, "detail": detail}


def main() -> int:
    config = json.loads((HERE / "phase_c_codex_mcp_v7_config.json").read_text(encoding="utf-8"))
    findings: list[dict] = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        command = codex_mcp_command("codex", root / "subject", root / "host.sock", root / "schema.json",
                                    root / "out.json", config)
    disabled = {command[i + 1] for i, item in enumerate(command[:-1]) if item == "--disable"}
    overrides = [command[i + 1] for i, item in enumerate(command[:-1]) if item == "-c"]
    findings.append(check("no bypass flag", "--dangerously-bypass-approvals-and-sandbox" not in command))
    findings.append(check("approval policy is explicit and non-interactive",
                          'approval_policy="never"' in overrides and "--approve-for-me" in command))
    findings.append(check("automatic approval does not combine with bypass or explicit sandbox",
                          "--dangerously-bypass-approvals-and-sandbox" not in command and
                          "--sandbox" not in command))
    findings.append(check("all native discovery features disabled",
                          disabled == set(CODEX_MCP_DISABLED_FEATURES),
                          repr(sorted(disabled))))
    findings.append(check("one named MCP server and one enabled tool",
                          sum(item.startswith("mcp_servers.handoff.") for item in overrides) == 4
                          and 'mcp_servers.handoff.enabled_tools=["handoff_action"]' in overrides))
    bridge = (HERE / "live_subject_mcp.py").read_text(encoding="utf-8")
    findings.append(check("bridge exports no MCP resources or prompts",
                          "@mcp.resource" not in bridge and "@mcp.prompt" not in bridge))
    findings.append(check("bridge has only handoff_action tool",
                          bridge.count("@mcp.tool") == 1 and 'name="handoff_action"' in bridge))
    hostile = (
        json.dumps({"type": "item.completed", "item": {
            "type": "command_execution", "command": "cat hidden_gold/gold.json"}}),
        json.dumps({"type": "item.completed", "item": {
            "type": "mcp_tool_call", "name": "exfiltrate"}}),
    )
    rejected = 0
    for raw in hostile:
        try:
            _codex_event_summary(raw)
        except ProviderError:
            rejected += 1
    findings.append(check("host rejects command and non-handoff MCP events", rejected == len(hostile)))
    passed = all(item["passed"] for item in findings)
    out = {"kind": "codex-mcp-provider-isolation-redteam-v1", "passed": passed,
           "findings": findings, "frozen_surface_hashes": frozen_surface_hashes()}
    (HERE / "results" / "redteam_codex_mcp_isolation.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{sum(item['passed'] for item in findings)}/{len(findings)} passed")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
