#!/usr/bin/env python3
"""Fail-closed preflight for the OAuth-parent / single-MCP Codex adapter.

This is deliberately a protocol red-team, not a model performance result. It
checks the launch contract, hostile raw event examples, narrow action inputs,
and the bridge source before a paid qualification is permitted.
"""

from __future__ import annotations

import hashlib
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


BLOCKED_EXIT = 2


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _target_config() -> str:
    """The Codex config primary would actually run, not a hardcoded v7.

    Round 17, finding #6: this read `phase_c_codex_mcp_v7_config.json` while
    the current target was v9, so the red-team certified a config nobody was
    going to use -- and the artifact carried no config identity at all, so
    nothing downstream could tell.
    """
    auth = HERE / "results" / "PRIMARY_AUTHORIZATION.json"
    if auth.is_file():
        name = json.loads(auth.read_text(encoding="utf-8"))["config_file"]
        if "codex" in name and (HERE / name).is_file():
            return name
    candidates = sorted(HERE.glob("phase_c_codex_mcp_v*_config.json"),
                        key=lambda p: int(p.stem.split("_v")[-1].split("_")[0]))
    return candidates[-1].name


def main() -> int:
    config_name = _target_config()
    config = json.loads((HERE / config_name).read_text(encoding="utf-8"))
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
    # Round 16 closed the same fail-open in redteam_provider_isolation.py: an
    # environment that cannot run the probes at all must report BLOCKED, not
    # PASS. Here every check is a direct assertion rather than a
    # reachability probe, so a check that could not run fails outright --
    # `conclusive` is recorded anyway so the readiness gate and doctor read
    # the same field from both red-teams instead of special-casing one.
    conclusive = bool(findings)
    out = {"kind": "codex-mcp-provider-isolation-redteam-v1", "passed": passed,
           "conclusive": conclusive,
           "checked_configs": [{"file": config_name,
                                "sha256": _sha256(HERE / config_name)}],
           "status": "PASS" if conclusive and passed else (
               "BLOCKED" if not conclusive else "FAIL"),
           "findings": findings, "frozen_surface_hashes": frozen_surface_hashes()}
    (HERE / "results" / "redteam_codex_mcp_isolation.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{sum(item['passed'] for item in findings)}/{len(findings)} passed")
    if not passed:
        return 1
    return 0 if conclusive else BLOCKED_EXIT


if __name__ == "__main__":
    raise SystemExit(main())
