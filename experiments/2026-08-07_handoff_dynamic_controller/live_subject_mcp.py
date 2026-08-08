#!/usr/bin/env python3
"""Trusted stdio MCP bridge exposing only the host-owned retrieval actions.

This process is launched by the Codex parent, not by the evaluated model. It
has no resources or prompts and cannot read a corpus: every request is sent to
the existing host socket, where action validation and trace recording occur.
"""

from __future__ import annotations

from typing import Literal

from fastmcp import FastMCP

# Reuse the established socket protocol. The evaluated model cannot execute
# this import itself because native shell/file tools are disabled.
from live_subject_tool import request


Action = Literal["search", "follow_link", "expand_candidates", "read_candidate", "status", "finish"]
TerminalAction = Literal["answer", "abstain"]

mcp = FastMCP("Handoff Action Bridge")


def _payload(action: Action, query: str | None, path: str | None,
             start: int | None, end: int | None,
             terminal_action: TerminalAction | None) -> dict:
    values = {
        "search": {"query": query},
        "follow_link": {"path": path},
        "expand_candidates": {},
        "read_candidate": {"path": path, "start": start, "end": end},
        "status": {},
        "finish": {"terminal_action": terminal_action},
    }
    payload = {"action": action}
    for key, value in values[action].items():
        if value is not None:
            payload[key] = value
    return payload


@mcp.tool(name="handoff_action")
def handoff_action(
    action: Action,
    query: str | None = None,
    path: str | None = None,
    start: int | None = None,
    end: int | None = None,
    terminal_action: TerminalAction | None = None,
) -> dict:
    """Perform exactly one logged retrieval action through the host controller."""
    return request(_payload(action, query, path, start, end, terminal_action))


if __name__ == "__main__":
    mcp.run(transport="stdio")
