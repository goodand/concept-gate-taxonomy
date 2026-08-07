#!/usr/bin/env python3
"""Provider adapters for the Phase C live runner.

The runner owns the corpus, the guard, the action trace, and the judge. A
provider adapter owns exactly one thing: turning a prompt into a validated JSON
payload from a fresh, sandboxed subject process. Nothing here may touch the
corpus, gold, evaluator, action set, BudgetGuard, the four-key retrieval-subagent
contract, the public bundle, or the host-owned trace.

WHY A SECOND PROFILE EXISTS
---------------------------
`run_live_phase_c.seatbelt_profile` (v1) is `(allow default)` plus two denies:
the repository and the bundle's `control/` root. Probed with the real profile
(`redteam_provider_isolation.py`), those two hold -- hidden gold, prior live
results, and `control/corpus` are all unreadable. But `(allow default)` means
everything ELSE on the machine is readable, and three of those "elsewhere" paths
carry the answers:

    ~/.claude/projects/*.jsonl   full transcripts of every session in this
                                 workspace, including ones where corpus text and
                                 gold structures were printed
    ~/.claude.json               account/config and project-path metadata
    ~/.codex/                    the same for the Codex CLI

A subject with shell access can grep those. That is not a Claude-specific hole:
the Codex pilot in commit 8b333bc ran under v1 and had the same reach. It is
reported, not silently patched, because changing v1 would change the conditions
of a pilot that already ran.

v2 adds those denies and is used by the Claude adapter. Cross-provider
comparison therefore requires re-running the Codex qualification under v2 --
recorded as an unresolved risk in PROVIDER_ADAPTERS.md rather than assumed away.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path
from typing import Any, Callable

# Tools a retrieval subject must never have: they would bypass the host client
# and make the action trace incomplete rather than wrong -- which is worse,
# because an incomplete trace still scores.
CLAUDE_DENIED_TOOLS = (
    "Read", "Glob", "Grep", "WebFetch", "WebSearch", "Task", "Agent",
    "Edit", "Write", "NotebookEdit", "TodoWrite",
)


class ProviderError(RuntimeError):
    """A provider failed to produce a usable payload. Becomes V1 upstream."""

    def __init__(self, message: str, *, raw: str = "",
                 provider_meta: dict[str, Any] | None = None):
        super().__init__(message)
        self.raw = raw
        self.provider_meta = provider_meta or {}


# --------------------------------------------------------------------------
# sandbox
# --------------------------------------------------------------------------
def home_leak_denies() -> list[str]:
    """Paths outside the repository that carry prior-session content."""
    home = Path.home()
    return [
        str(home / ".claude" / "projects"),
        str(home / ".claude" / "todos"),
        str(home / ".claude" / "shell-snapshots"),
        str(home / ".claude" / "history.jsonl"),
        str(home / ".codex"),
        str(home / "Library" / "Application Support" / "Claude"),
    ]


def seatbelt_profile_v2(project_root: Path, host_control: Path,
                        *, extra_denies: list[str] | None = None) -> str:
    """v1 plus the home-directory transcript channels.

    `~/.claude.json` is deliberately NOT denied: the CLI reads it to resolve the
    logged-in account, and denying it stops the subject from starting at all.
    Its account/config and project-path metadata therefore remain reachable --
    an accepted, documented residual risk, not an oversight. The red-team probe
    found no prompt-history arrays in this file on this host.
    """
    lines = ["(version 1)", "(allow default)"]
    for path in [str(project_root), str(host_control), *home_leak_denies(),
                 *(extra_denies or [])]:
        lines.append(f'(deny file-read* (subpath "{path}"))')
        lines.append(f'(deny file-write* (subpath "{path}"))')
    return "\n".join(lines)


# --------------------------------------------------------------------------
# minimal JSON-schema check (the CLI has no --output-schema equivalent)
# --------------------------------------------------------------------------
def validate_against_schema(payload: Any, schema: dict, path: str = "$") -> None:
    """Validate every JSON-schema keyword used by the two response schemas."""
    kind = schema.get("type")
    if kind == "object":
        if not isinstance(payload, dict):
            raise ProviderError(f"{path}: expected object, got {type(payload).__name__}")
        for key in schema.get("required", []):
            if key not in payload:
                raise ProviderError(f"{path}: missing required key {key!r}")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            extra = sorted(set(payload) - set(props))
            if extra:
                raise ProviderError(f"{path}: unexpected key(s) {extra}")
        for key, sub in props.items():
            if key in payload:
                validate_against_schema(payload[key], sub, f"{path}.{key}")
    elif kind == "array":
        if not isinstance(payload, list):
            raise ProviderError(f"{path}: expected array")
        if "items" in schema:
            for i, item in enumerate(payload):
                validate_against_schema(item, schema["items"], f"{path}[{i}]")
    elif kind == "string":
        if not isinstance(payload, str):
            raise ProviderError(f"{path}: expected string")
        if len(payload) < schema.get("minLength", 0):
            raise ProviderError(f"{path}: shorter than minLength")
    elif kind == "boolean":
        if not isinstance(payload, bool):
            raise ProviderError(f"{path}: expected boolean")
    elif kind == "integer":
        if not isinstance(payload, int) or isinstance(payload, bool):
            raise ProviderError(f"{path}: expected integer")
        if "minimum" in schema and payload < schema["minimum"]:
            raise ProviderError(f"{path}: below minimum {schema['minimum']}")
    if "const" in schema and payload != schema["const"]:
        raise ProviderError(f"{path}: {payload!r} does not equal const {schema['const']!r}")
    if "enum" in schema and payload not in schema["enum"]:
        raise ProviderError(f"{path}: {payload!r} not in {schema['enum']}")


_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.S)


def _decoded_objects(text: str) -> list[dict[str, Any]]:
    """Decode objects without treating braces inside JSON strings as syntax."""
    decoder = json.JSONDecoder()
    found: list[dict[str, Any]] = []
    cursor = 0
    while cursor < len(text):
        index = text.find("{", cursor)
        if index < 0:
            break
        try:
            value, consumed = decoder.raw_decode(text[index:])
        except json.JSONDecodeError:
            cursor = index + 1
            continue
        if isinstance(value, dict):
            found.append(value)
            cursor = index + consumed
        else:
            cursor = index + 1
    return found


def extract_json_object(text: str) -> dict:
    """Pull the final JSON object out of a model's prose.

    Codex is given `--output-schema` and writes the object to a file. The Claude
    CLI has no such flag, so the object arrives inside `result` as text and the
    adapter must find it. Preferring the LAST fenced block, then the last
    balanced object, matches how a model that reasons then answers actually
    formats a reply.
    """
    blocks = _FENCE.findall(text or "")
    fenced = [obj for block in blocks for obj in _decoded_objects(block)]
    if fenced:
        return fenced[-1]
    objects = _decoded_objects(text or "")
    if objects:
        return objects[-1]
    raise ProviderError("no JSON object found in the subject's final message")


def payload_from_claude_envelope(envelope: dict[str, Any]) -> dict[str, Any]:
    """Prefer the CLI's native structured output; retain prose fallback."""
    structured = envelope.get("structured_output")
    if isinstance(structured, dict):
        return structured
    return extract_json_object(envelope.get("result", ""))


def claude_cli_schema(schema_path: Path) -> dict[str, Any]:
    """Remove only the draft URI unsupported by Claude CLI's schema parser."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema.pop("$schema", None)
    return schema


# --------------------------------------------------------------------------
# claude-cli adapter
# --------------------------------------------------------------------------
def claude_command(claude: str, sandbox: str, profile: str, subject: Path,
                   schema_path: Path, config: dict[str, Any],
                   session_id: str) -> list[str]:
    """Built separately from execution so tests can assert on it without paying
    for a model call."""
    return [
        sandbox, "-p", profile, claude, "--print",
        "--output-format", "json",
        "--json-schema", json.dumps(
            claude_cli_schema(schema_path), separators=(",", ":")),
        "--model", config["model"],
        "--max-turns", str(config.get("max_turns", 40)),
        # Q4: a fresh subject per cell. No session is written, so none can be
        # resumed; the id is unique so nothing is joined to a prior run.
        "--no-session-persistence",
        "--session-id", session_id,
        # No user/project/local settings and no CLAUDE.md: the workspace's own
        # instructions would otherwise become part of the subject's prompt.
        "--setting-sources", "",
        "--safe-mode", "--disable-slash-commands", "--no-chrome",
        "--strict-mcp-config", "--mcp-config", '{"mcpServers":{}}',
        # The host client is the only evidence channel. Bash is required to run
        # it; every other retrieval tool is blocked so a read cannot happen off
        # the trace.
        "--tools", "Bash", "--allowedTools", "Bash",
        "--disallowedTools", *CLAUDE_DENIED_TOOLS,
        # The surrounding Seatbelt profile is the OS boundary, exactly as with
        # Codex. This flag only removes the interactive approval prompt.
        "--dangerously-skip-permissions",
        "--add-dir", str(subject),
    ]


def run_claude_cli(subject: Path, socket_path: Path, prompt: str, schema_name: str,
                   config: dict[str, Any], *, project_root: Path, host_control: Path,
                   run_name: str) -> dict[str, Any]:
    """Same signature and return shape as the runner's `_run_codex`."""
    claude = shutil.which("claude")
    sandbox = Path("/usr/bin/sandbox-exec")
    if not claude or not sandbox.is_file():
        raise ProviderError("Claude CLI or macOS sandbox-exec is unavailable")
    run_dir = subject / "run"
    run_dir.mkdir(exist_ok=True)
    raw_path = run_dir / f"{run_name}.jsonl"
    output_path = run_dir / f"{run_name}.json"
    schema_path = subject / schema_name
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    session_id = str(uuid.uuid4())
    profile = seatbelt_profile_v2(project_root, host_control)
    command = claude_command(claude, str(sandbox), profile, subject, schema_path,
                             config, session_id)

    env = dict(os.environ)
    env["HANDOFF_LIVE_TOOL_SOCKET"] = str(socket_path)
    # The CLI cannot see the workspace anyway (Seatbelt), but an inherited
    # CLAUDE_CODE_* var could still change behaviour between cells.
    for key in [k for k in env if k.startswith("CLAUDE_CODE_")]:
        env.pop(key)

    started = time.perf_counter()
    try:
        proc = subprocess.run(command, input=prompt, text=True, capture_output=True,
                              env=env, cwd=subject,
                              timeout=config["timeout_seconds"], check=False)
    except subprocess.TimeoutExpired as exc:
        raw_path.write_text((exc.stdout or "") + "\n" + (exc.stderr or ""),
                            encoding="utf-8")
        raise ProviderError(
            f"Claude CLI timed out after {config['timeout_seconds']} seconds") from exc

    raw = proc.stdout + "\n-- STDERR --\n" + proc.stderr
    raw_path.write_text(raw, encoding="utf-8")
    if proc.returncode != 0:
        tail = ("stdout=" + proc.stdout[-1200:] + " stderr=" + proc.stderr[-1200:]).strip()
        raise ProviderError(f"Claude CLI exited {proc.returncode}: {tail}", raw=raw)
    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise ProviderError(f"Claude CLI envelope is not JSON: {exc}", raw=raw) from exc
    if envelope.get("is_error"):
        raise ProviderError(f"Claude CLI reported an error: "
                            f"{str(envelope.get('result'))[:300]}", raw=raw)

    provider_meta = {"provider": "claude-cli", "session_id": session_id,
                     "cost_usd": envelope.get("total_cost_usd"),
                     "num_turns": envelope.get("num_turns"),
                     "sandbox_profile": "v2",
                     "structured_output": isinstance(
                         envelope.get("structured_output"), dict)}
    try:
        payload = payload_from_claude_envelope(envelope)
        # Native schema enforcement is primary. Revalidation protects against
        # CLI regressions and keeps provider artifacts comparable over time.
        validate_against_schema(payload, schema)
    except ProviderError as exc:
        raise ProviderError(str(exc), raw=raw, provider_meta=provider_meta) from exc
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                           encoding="utf-8")
    return {"payload": payload, "raw": raw_path.read_text(encoding="utf-8"),
            "elapsed_ms": int((time.perf_counter() - started) * 1000),
            "provider_meta": provider_meta}


# --------------------------------------------------------------------------
# registry
# --------------------------------------------------------------------------
def resolve_provider(config: dict[str, Any],
                     codex_impl: Callable[..., dict[str, Any]]) -> Callable[..., dict[str, Any]]:
    """Pick the adapter named by the frozen config.

    `codex_impl` is passed in rather than imported so this module never imports
    the runner -- the runner imports this one, and the existing Codex path is
    untouched byte-for-byte.
    """
    name = config.get("provider")
    if name == "codex-cli":
        return codex_impl
    if name == "claude-cli":
        return run_claude_cli
    raise ProviderError(f"unknown provider: {name!r}")
