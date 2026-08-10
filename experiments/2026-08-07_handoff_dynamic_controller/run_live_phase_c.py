#!/usr/bin/env python3
"""Run Phase C live subjects without exposing hidden labels to the subject.

This runner deliberately separates four things that are easy to accidentally
mix in an agent experiment:

* the model-visible task and socket client (``subject/``),
* the corpus and action log held by this host process (``control/``),
* the evaluator-only labels in this experiment directory, and
* the disposable Codex process that is denied both host-only roots by macOS
  Seatbelt.

The tool server, rather than the model, is the authority for reads, candidate
sets, guard refusals, and the final action trace. That makes C4 and C1
observable even when a model's final JSON is otherwise well formed.
"""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
import uuid
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _contract import (ARM_HAS_SUBAGENT, ARM_IS_DYNAMIC, ARMS, SUBAGENT_VERSION,
                       TRACE_VERSION, ContractError, validate_subagent_output,
                       validate_trace)
from _evaluator import (frozen_surface_drift, frozen_surface_hashes,
                        run_clean_judge, source_hashes)
from _runner import BudgetGuard, Corpus, MAX_ACTIONS, MAX_TERMINAL_ATTEMPTS
from run_smoke import _safety_summary
from _providers import ProviderError, resolve_provider, seatbelt_profile_v2
from build_live_public_bundle import BundleError, build_bundle, verify_bundle
from run_calibration import load

CONFIG_PATH = HERE / "phase_c_live_config.json"
ALLOWED_CONFIG_NAMES = (
    "phase_c_live_config.json",
    "phase_c_codex_v2_config.json",
    "phase_c_codex_mcp_config.json",
    "phase_c_codex_mcp_v2_config.json",
    "phase_c_codex_mcp_v3_config.json",
    "phase_c_codex_mcp_v4_config.json",
    "phase_c_codex_mcp_v5_config.json",
    "phase_c_codex_mcp_v6_config.json",
    "phase_c_codex_mcp_v7_config.json",
    # v8 / surface-v3: re-qualification configs frozen 2026-08-10 after
    # Amendments 22-31 changed the frozen surface. Older configs are kept
    # as historical evidence but their qualification artifacts are stale
    # (frozen_surface_drift reports 6 files) and can no longer serve as a
    # primary precondition -- same precedent as Amendment 21's v6->v7.
    "phase_c_codex_mcp_v8_config.json",
    "phase_c_codex_mcp_v9_config.json",
    "phase_c_claude_config.json",
    "phase_c_claude_mcp_surface_config.json",
    "phase_c_claude_mcp_surface_v2_config.json",
    "phase_c_claude_mcp_surface_v3_config.json",
)
RESULTS_DIR = HERE / "results"
QUALIFICATION_LEDGER_NAME = "qualification_ledger.jsonl"
PRIMARY_AUTHORIZATION_NAME = "PRIMARY_AUTHORIZATION.json"
PRIMARY_ATTEMPT_LEDGER_NAME = "primary_attempt_ledger.jsonl"
MAX_READ_END = 200


class LiveRunError(RuntimeError):
    """A live process could not yield a valid, evaluable subject artifact."""


def _sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LiveRunError(
                f"invalid JSONL record in {path.name}:{line_number}: {exc}"
            ) from exc
        if not isinstance(record, dict):
            raise LiveRunError(f"non-object JSONL record in {path.name}:{line_number}")
        records.append(record)
    return records


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def load_config(path: str | Path = CONFIG_PATH) -> dict[str, Any]:
    selected = Path(path)
    if not selected.is_absolute():
        selected = HERE / selected
    selected = selected.resolve()
    allowed = {(HERE / name).resolve() for name in ALLOWED_CONFIG_NAMES}
    if selected not in allowed:
        raise LiveRunError(
            f"config is not part of the frozen provider set: {selected}")
    config = json.loads(selected.read_text(encoding="utf-8"))
    if config.get("contract_version") != "handoff-dyn-phase-c-config-v1":
        raise LiveRunError("unsupported Phase C config")
    if tuple(config.get("pilot", {}).get("arms", [])) != ARMS:
        raise LiveRunError("pilot arms differ from frozen arm contract")
    if config.get("max_actions") != MAX_ACTIONS:
        raise LiveRunError("config max_actions differs from BudgetGuard contract")
    if config.get("max_terminal_attempts") != MAX_TERMINAL_ATTEMPTS:
        raise LiveRunError("config terminal attempts differs from BudgetGuard contract")
    return config


def _safe_rel(value: object) -> str | None:
    if not isinstance(value, str) or not value or value.startswith("/"):
        return None
    path = Path(value)
    if ".." in path.parts:
        return None
    return path.as_posix()


class LiveToolState:
    """Host-owned retrieval state for exactly one model call."""

    def __init__(self, corpus: Corpus, case: dict, *, initial_candidates: list[str] | None,
                 guard_enabled: bool, strict_static: bool = False):
        self.corpus = corpus
        self.case = case
        self.guard = BudgetGuard()
        self.guard_enabled = guard_enabled
        self.strict_static = strict_static
        self.static_steps = ["search", "expand_candidates", "read_candidate",
                             "follow_link", "read_candidate", "finish"]
        self.static_required_read_path: str | None = None
        self.started = time.perf_counter()
        self.candidates: list[str] = []
        self.actions: list[dict[str, Any]] = []
        self.reads: list[dict[str, Any]] = []
        self.guard_rejections: list[dict[str, Any]] = []
        self.failure_codes: list[str] = []
        self.tool_errors: list[str] = []
        self.stop_reason: str | None = None
        self._lock = threading.Lock()
        for path in initial_candidates or []:
            self._add_candidate(path)
        if case["condition"] == "direct-handoff":
            handoff = case["handoff_path"]
            self.candidates = [handoff] + [p for p in self.candidates if p != handoff]

    def _add_candidate(self, path: str) -> bool:
        if path in self.corpus.docs and path not in self.candidates:
            self.candidates.append(path)
            return True
        return False

    def _record(self, action: str, before: list[str], *, query: str | None = None,
                read_range: dict[str, Any] | None = None, accepted: bool = True,
                reject_reason: str | None = None) -> None:
        self.actions.append({
            "i": len(self.actions), "action": action, "query": query,
            "candidates_before": before, "candidates_after": list(self.candidates),
            "read_range": read_range, "accepted": accepted,
            "reject_reason": reject_reason,
            "elapsed_ms": int((time.perf_counter() - self.started) * 1000),
        })

    def _reject(self, message: str) -> dict[str, Any]:
        self.tool_errors.append(message)
        return {"ok": False, "error": message, "candidates": list(self.candidates)}

    def _budget_exhausted(self) -> bool:
        if len(self.actions) < MAX_ACTIONS:
            return False
        if "C1" not in self.failure_codes:
            self.failure_codes.append("C1")
        self.stop_reason = self.stop_reason or "C1"
        return True

    def dispatch(self, request: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            name = request.get("action")
            if name == "status":
                return {"ok": True, "candidates": list(self.candidates),
                        "actions_used": len(self.actions), "actions_limit": MAX_ACTIONS,
                        "terminal_rejections": self.guard.terminal_attempts,
                        "stop_reason": self.stop_reason}
            if name not in ("search", "follow_link", "expand_candidates",
                            "read_candidate", "finish"):
                return self._reject(f"unknown host tool action: {name!r}")
            if self.strict_static:
                initial = self.static_steps[:-1]
                if len(self.actions) < len(initial):
                    allowed = {initial[len(self.actions)]}
                elif len(self.actions) == len(initial):
                    allowed = {"finish"}
                elif (self.actions[-1]["action"] in ("answer", "abstain")
                      and not self.actions[-1]["accepted"]):
                    # A static arm cannot choose a new policy, but a rejected
                    # terminal action must have one fixed recovery operation.
                    # The prompt requires an unread observed candidate here.
                    allowed = {"read_candidate"}
                else:
                    allowed = {"finish"}
                if name not in allowed:
                    self.failure_codes.append("V1")
                    self.stop_reason = "V1"
                    return self._reject(
                        f"static arm protocol violation: expected {sorted(allowed)}, got {name}")
                if name == "read_candidate" and self.static_required_read_path:
                    requested_path = _safe_rel(request.get("path"))
                    if requested_path != self.static_required_read_path:
                        self.failure_codes.append("V1")
                        self.stop_reason = "V1"
                        return self._reject(
                            "static arm protocol violation: expected read_candidate "
                            f"for {self.static_required_read_path!r}, got {requested_path!r}")
            if self.stop_reason:
                return self._reject(f"run has already stopped: {self.stop_reason}")
            if self._budget_exhausted():
                return self._reject("exploration budget exhausted (C1)")

            before = list(self.candidates)
            if name == "search":
                query = request.get("query")
                if not isinstance(query, str) or not query.strip():
                    return self._reject("search query must be a non-empty string")
                result = self.corpus.search(query.strip())
                if self.guard.first_search_paths is None:
                    self.guard.first_search_paths = set(result)
                for path in result:
                    self._add_candidate(path)
                self.guard.observe("reformulate_query", query, result[0] if result else None)
                self._record("reformulate_query", before, query=query)
                return {"ok": True, "action": "search", "result_paths": result,
                        "candidates": list(self.candidates)}

            if name == "follow_link":
                path = _safe_rel(request.get("path"))
                if not path or path not in self.candidates:
                    return self._reject("follow_link path must be an observed candidate")
                result = self.corpus.links(path)
                for target in result:
                    self._add_candidate(target)
                self.guard.observe("follow_link", None, path)
                self._record("follow_link", before)
                response = {"ok": True, "action": "follow_link", "from_path": path,
                            "result_paths": result, "candidates": list(self.candidates)}
                if self.strict_static:
                    read_paths = {item["path"] for item in self.reads}
                    # A link target is preferred. A linkless authority still has
                    # to be read before another graph hop is permitted.
                    choices = [*result, path, *self.candidates]
                    self.static_required_read_path = next(
                        (candidate for candidate in choices if candidate not in read_paths),
                        None)
                    if not self.static_required_read_path:
                        self.failure_codes.append("V1")
                        self.stop_reason = "V1"
                        return self._reject("static arm has no unread candidate after follow_link")
                    response["static_next"] = {
                        "action": "read_candidate",
                        "path": self.static_required_read_path,
                    }
                return response

            if name == "expand_candidates":
                result: list[str] = []
                for path in list(self.candidates):
                    for target in self.corpus.links(path):
                        if self._add_candidate(target):
                            result.append(target)
                self.guard.observe("expand_candidates", None, None)
                self._record("expand_candidates", before)
                return {"ok": True, "action": "expand_candidates", "result_paths": result,
                        "candidates": list(self.candidates)}

            if name == "read_candidate":
                path = _safe_rel(request.get("path"))
                start, end = request.get("start", 1), request.get("end", 40)
                if not path or path not in self.candidates:
                    return self._reject("read_candidate path must be an observed candidate")
                if (not isinstance(start, int) or not isinstance(end, int)
                        or start < 1 or end < start or end > MAX_READ_END):
                    return self._reject(f"read range must satisfy 1 <= start <= end <= {MAX_READ_END}")
                read_range = {"path": path, "start": start, "end": end}
                text = self.corpus.read(path, start, end)
                numbered = "\n".join(
                    f"{line_no}: {line}" for line_no, line in
                    enumerate(text.splitlines(), start=start))
                self.reads.append(read_range)
                self.guard.observe("read_candidate", None, path)
                self._record("read_candidate", before, read_range=read_range)
                if self.strict_static and path == self.static_required_read_path:
                    self.static_required_read_path = None
                return {"ok": True, "action": "read_candidate", "path": path,
                        "start": start, "end": end, "content": numbered,
                        "candidates": list(self.candidates)}

            terminal = request.get("terminal_action")
            if terminal not in ("answer", "abstain"):
                return self._reject("finish needs terminal_action answer or abstain")
            reason = self.guard.check(terminal) if self.guard_enabled else None
            if reason:
                self.guard.terminal_attempts += 1
                self.guard.rejections.append(reason)
                rejection = {"i": len(self.actions), "action": terminal, "reason": reason}
                self.guard_rejections.append(rejection)
                self._record(terminal, before, accepted=False, reject_reason=reason)
                if self.guard.terminal_attempts >= MAX_TERMINAL_ATTEMPTS:
                    self.failure_codes.append("C1")
                    self.stop_reason = "C1"
                    return {"ok": False, "error": "terminal action refused; C1", "reason": reason,
                            "terminal_rejections": self.guard.terminal_attempts,
                            "candidates": list(self.candidates)}
                return {"ok": False, "error": "terminal action refused", "reason": reason,
                        "terminal_rejections": self.guard.terminal_attempts,
                        "candidates": list(self.candidates)}
            self.stop_reason = terminal
            self._record(terminal, before)
            return {"ok": True, "action": "finish", "terminal_action": terminal,
                    "candidates": list(self.candidates)}

    def trace_fields(self) -> dict[str, Any]:
        return {
            "actions": self.actions,
            "reads": self.reads,
            "guard_rejections": self.guard_rejections,
            "failure_codes": self.failure_codes,
            "tool_errors": self.tool_errors,
            "stop_reason": self.stop_reason,
            "n_search": sum(1 for step in self.actions
                            if step["action"] == "reformulate_query" and step["accepted"]),
            "n_read": len(self.reads),
            "wall_clock_ms": int((time.perf_counter() - self.started) * 1000),
        }


class _ToolHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        try:
            line = self.rfile.readline(1024 * 1024)
            request = json.loads(line.decode("utf-8"))
            response = self.server.state.dispatch(request)  # type: ignore[attr-defined]
        except (UnicodeDecodeError, json.JSONDecodeError, OSError, ValueError) as exc:
            response = {"ok": False, "error": f"invalid host tool request: {exc}"}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode("utf-8"))


class ToolServer:
    def __init__(self, socket_path: Path, state: LiveToolState):
        if socket_path.exists():
            raise LiveRunError(f"socket path already exists: {socket_path}")
        self.server = socketserver.ThreadingUnixStreamServer(str(socket_path), _ToolHandler)
        self.server.state = state  # type: ignore[attr-defined]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.socket_path = socket_path

    def __enter__(self) -> "ToolServer":
        self.thread.start()
        return self

    def __exit__(self, *_: object) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        if self.socket_path.exists():
            self.socket_path.unlink()


def seatbelt_profile(project_root: Path, host_control: Path) -> str:
    """Default allow, then deny the repository and host-only control surface."""
    return "\n".join((
        "(version 1)",
        "(allow default)",
        f'(deny file-read* (subpath "{project_root}"))',
        f'(deny file-write* (subpath "{project_root}"))',
        f'(deny file-read* (subpath "{host_control}"))',
        f'(deny file-write* (subpath "{host_control}"))',
    ))


def _client_instructions(transport: str) -> str:
    if transport == "mcp":
        return ("Use ONLY the `handoff_action` MCP tool to obtain source evidence. "
                "Call it with action `search`, `follow_link`, `expand_candidates`, "
                "`read_candidate`, `status`, or `finish`; supply the matching named "
                "arguments (`query`, `path`, `start`/`end`, or `terminal_action`).")
    return ("Use ONLY `python3 live_subject_tool.py` to obtain source evidence. "
            "The client exposes `search QUERY`, `follow_link PATH`, "
            "`expand_candidates`, `read_candidate PATH --start N --end N`, `status`, "
            "and `finish answer|abstain`.")


def _prompt(case: dict, arm: str, *, subagent: dict | None = None,
            retrieval_only: bool = False, transport: str = "cli") -> str:
    task = json.dumps(case, ensure_ascii=False, indent=2)
    client = _client_instructions(transport)
    if retrieval_only:
        return f"""You are the retrieval-only component of a controlled evaluation.

The public task is:
{task}

{client} Do not use shell search, file reads, network access, or tools outside
the closed host client. You may use the client actions `search`, `follow_link`,
`expand_candidates`, and `read_candidate`. You must not answer the task. Return only the required JSON
schema: candidate_paths, read_ranges, search_trace, and uncertainty. Candidate
paths and read ranges must come from host-client observations. Do not include
any conclusion, authority label, state, or extra key.
"""
    mode = "dynamic: choose the next host action from the evidence returned" if ARM_IS_DYNAMIC[arm] else (
        "static: use this fixed sequence: search the task query; expand candidates; "
        "read the handoff or best candidate; follow one observed candidate link; "
        "then use the host response's `static_next.path` for the required read; then finish. "
        "Do not issue another follow or finish before that exact read. If finish is refused, read one "
        "additional observed candidate that you have not read, then retry finish. Do not "
        "change the sequence in any other way.")
    subagent_text = "none"
    if subagent is not None:
        subagent_text = json.dumps(subagent, ensure_ascii=False, indent=2)
    return f"""You are the main subject in a controlled retrieval evaluation.

The public task is:
{task}

Mode: {mode}

{client} Do not use shell search, direct file reads, network access, or any
other discovery tool.
Every source used in the final answer must first be read via `read_candidate`.
Call `finish` before emitting final JSON. If it returns a refusal, keep
exploring according to the returned reason. A search miss is not proof of
absence. Cite only path and line ranges you personally read.

Retrieval-only component output, if present, is a candidate hint only. Re-read
all evidence yourself before relying on it:
{subagent_text}

Return only the required JSON schema. Set contract_version to
`handoff-dyn-live-answer-v1`, case_id to `{case['id']}`, arm to `{arm}`, and
terminal_action to the accepted finish action.
"""


def _run_codex(subject: Path, socket_path: Path, prompt: str, schema_name: str,
               config: dict[str, Any], *, project_root: Path, host_control: Path,
               run_name: str) -> dict[str, Any]:
    codex = shutil.which("codex")
    seatbelt = Path("/usr/bin/sandbox-exec")
    if not codex or not seatbelt.is_file():
        raise LiveRunError("Codex CLI or macOS sandbox-exec is unavailable")
    run_dir = subject / "run"
    run_dir.mkdir(exist_ok=True)
    output_path = run_dir / f"{run_name}.json"
    raw_path = run_dir / f"{run_name}.jsonl"
    profile = (seatbelt_profile_v2(project_root, host_control)
               if "seatbelt-v2" in config.get("sandbox_policy", "")
               else seatbelt_profile(project_root, host_control))
    command = [
        str(seatbelt), "-p", profile, codex, "exec", "--ephemeral",
        "--skip-git-repo-check", "--ignore-user-config", "--ignore-rules",
        # The surrounding Seatbelt profile is the OS boundary. Asking Codex to
        # create a second macOS sandbox inside it fails before the public socket
        # client can start (sandbox_apply: Operation not permitted).
        "--dangerously-bypass-approvals-and-sandbox", "-C", str(subject),
        "-m", config["model"], "-c",
        f'model_reasoning_effort="{config["reasoning_effort"]}"',
        "--output-schema", str(subject / schema_name),
        "--output-last-message", str(output_path), "--json", "-",
    ]
    env = dict(os.environ)
    env["HANDOFF_LIVE_TOOL_SOCKET"] = str(socket_path)
    started = time.perf_counter()
    try:
        proc = subprocess.run(
            command, input=prompt, text=True, capture_output=True, env=env,
            cwd=subject, timeout=config["timeout_seconds"], check=False)
    except subprocess.TimeoutExpired as exc:
        raw_path.write_text((exc.stdout or "") + "\n" + (exc.stderr or ""),
                            encoding="utf-8")
        raise LiveRunError(f"Codex timed out after {config['timeout_seconds']} seconds") from exc
    raw_path.write_text(proc.stdout + "\n-- STDERR --\n" + proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        diagnostic = ("stdout=" + proc.stdout[-1200:] + " stderr=" + proc.stderr[-1200:]).strip()
        raise LiveRunError(f"Codex exited {proc.returncode}: {diagnostic}")
    if not output_path.is_file():
        raise LiveRunError("Codex did not produce a final JSON response")
    try:
        payload = json.loads(output_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LiveRunError(f"Codex final response is not JSON: {exc}") from exc
    return {"payload": payload, "raw": raw_path.read_text(encoding="utf-8"),
            "elapsed_ms": int((time.perf_counter() - started) * 1000),
            "provider_meta": {
                "provider": "codex-cli",
                "sandbox_profile": "v2" if "seatbelt-v2" in config.get(
                    "sandbox_policy", "") else "v1",
            }}


def _subagent_output(payload: dict[str, Any], state: LiveToolState) -> dict[str, Any]:
    try:
        result = validate_subagent_output(payload)
    except ContractError as exc:
        raise LiveRunError(f"C3: invalid retrieval-only output: {exc}") from exc
    if len(result["candidate_paths"]) != len(set(result["candidate_paths"])):
        raise LiveRunError("C3: retrieval-only output repeated a candidate path")
    observed = {path for step in state.actions for path in step["candidates_after"]}
    if not set(result["candidate_paths"]) <= observed:
        raise LiveRunError("C3: subagent returned candidate path it did not observe")
    for item in result.get("read_ranges", []):
        path, start, end = item.get("path"), item.get("start"), item.get("end")
        if (not _safe_rel(path) or not isinstance(start, int) or not isinstance(end, int)
                or start < 1 or end < start):
            raise LiveRunError("C3: retrieval-only output has a malformed read range")
        # A subject that exposed lines 1-40 may truthfully report a narrower
        # 8-20 range. Exact tuple equality made that honest report invalid.
        if not any(r["path"] == path and r["start"] <= start and r["end"] >= end
                   for r in state.reads):
            raise LiveRunError("C3: subagent declared an unobserved read range")
    return result


def _trace_from_subject(case: dict, arm: str, state: LiveToolState,
                        response: dict[str, Any], subagent: dict | None) -> dict[str, Any]:
    fields = state.trace_fields()
    trace = {
        "contract_version": TRACE_VERSION, "case_id": case["id"], "arm": arm,
        "subagent_output": subagent, "claims": response.get("claims", []),
        "current_state": response.get("current_state", ""),
        "next_action": response.get("next_action", ""),
        "stop_conditions": response.get("stop_conditions", []),
        "uncertainties": response.get("uncertainties", []),
        "recommended_actions": response.get("recommended_actions", []),
        "answer_text": response.get("answer_text", ""),
        "declared_absent": response.get("declared_absent", False),
        **fields,
    }
    if response.get("case_id") != case["id"] or response.get("arm") != arm:
        trace["failure_codes"].append("V1")
        trace["tool_errors"].append("final response case_id or arm did not match host run")
    if response.get("terminal_action") != trace["stop_reason"]:
        trace["failure_codes"].append("V1")
        trace["tool_errors"].append("final terminal_action was not accepted by host guard")
    if trace["stop_reason"] not in ("answer", "abstain"):
        trace["failure_codes"].append("V1")
        trace["tool_errors"].append("subject ended without an accepted terminal action")
    try:
        validate_trace(trace)
    except ContractError as exc:
        trace["failure_codes"].append("E1" if "E1" in str(exc) else "C2")
        trace["tool_errors"].append(str(exc))
    trace["failure_codes"] = sorted(set(trace["failure_codes"]))
    return trace


def _invalid_trace(case: dict, arm: str, message: str, *, subagent: dict | None = None,
                   state: LiveToolState | None = None) -> dict[str, Any]:
    fields = state.trace_fields() if state is not None else {
        "actions": [], "reads": [], "guard_rejections": [],
        "failure_codes": [], "tool_errors": [], "stop_reason": None,
        "n_search": 0, "n_read": 0, "wall_clock_ms": 0,
    }
    fields["failure_codes"] = sorted(set(fields["failure_codes"] + ["V1"]))
    fields["tool_errors"] = fields["tool_errors"] + [message]
    fields["stop_reason"] = "V1"
    return {
        "contract_version": TRACE_VERSION, "case_id": case["id"], "arm": arm,
        "subagent_output": subagent, "claims": [],
        "current_state": "", "next_action": "", "stop_conditions": [],
        "uncertainties": [], "recommended_actions": [], "answer_text": "",
        "declared_absent": False, **fields,
    }


def _provider_error_details(exc: Exception) -> dict[str, Any]:
    details: dict[str, Any] = {"error": str(exc)}
    if isinstance(exc, ProviderError):
        if exc.raw:
            details["raw"] = exc.raw
        if exc.provider_meta:
            details["provider_meta"] = exc.provider_meta
    return details


def _run_retrieval_subagent(case: dict, variant: str, config: dict[str, Any],
                            temp_root: Path) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    state: LiveToolState | None = None
    try:
        bundle = temp_root / "retrieval-subagent"
        manifest = build_bundle(bundle, variant, case["id"])
        corpus = Corpus(bundle / "control" / "corpus")
        state = LiveToolState(corpus, case, initial_candidates=None, guard_enabled=False)
        socket_path = temp_root / "retrieval-subagent.sock"
        with ToolServer(socket_path, state):
            run = resolve_provider(config, _run_codex)(
                             bundle / "subject", socket_path,
                             _prompt(case, "R_DYNAMIC", retrieval_only=True,
                                     transport="mcp" if config["provider"] == "codex-mcp-cli" else "cli"),
                             "retrieval_subagent_response.schema.json", config,
                             project_root=HERE.parents[2], host_control=bundle / "control",
                             run_name="subagent")
        verify_bundle(bundle, manifest)
        return _subagent_output(run["payload"], state), {
            "raw": run["raw"], "elapsed_ms": run["elapsed_ms"],
            "host_actions": state.actions,
            "provider_meta": run.get("provider_meta", {}),
        }
    except (BundleError, LiveRunError, ProviderError, OSError, ValueError) as exc:
        return None, {**_provider_error_details(exc),
                      "host_actions": state.actions if state else []}


def run_cell(case: dict, gold: dict, arm: str, variant: str, config: dict[str, Any],
             temp_root: Path, *, subagent: dict | None, subagent_meta: dict | None) -> tuple[dict, dict]:
    """Run one main subject. It never receives ``gold``; that argument exists
    only so the host can return a clean-judge payload after the process exits."""
    if ARM_HAS_SUBAGENT[arm] and subagent is None:
        trace = _invalid_trace(case, arm, "retrieval-only component did not return a valid output")
        trace["failure_codes"].append("C3")
        trace["failure_codes"] = sorted(set(trace["failure_codes"]))
        trace["variant"] = variant
        return trace, {"error": "R arm not run because retrieval-only component was invalid",
                       "subagent": subagent_meta}
    bundle = temp_root / f"main-{arm.lower()}"
    state: LiveToolState | None = None
    try:
        manifest = build_bundle(bundle, variant, case["id"])
        corpus = Corpus(bundle / "control" / "corpus")
        state = LiveToolState(corpus, case, initial_candidates=(subagent or {}).get("candidate_paths"),
                               guard_enabled=True, strict_static=not ARM_IS_DYNAMIC[arm])
        socket_path = temp_root / f"{arm.lower()}.sock"
        with ToolServer(socket_path, state):
            run = resolve_provider(config, _run_codex)(
                             bundle / "subject", socket_path, _prompt(
                                 case, arm, subagent=subagent,
                                 transport="mcp" if config["provider"] == "codex-mcp-cli" else "cli"),
                             "live_subject_response.schema.json", config,
                             project_root=HERE.parents[2], host_control=bundle / "control",
                             run_name="main")
        verify_bundle(bundle, manifest)
        trace = _trace_from_subject(case, arm, state, run["payload"], subagent)
        trace["variant"] = variant
        return trace, {
            "raw": run["raw"], "subject_elapsed_ms": run["elapsed_ms"],
            "provider_meta": run.get("provider_meta", {}),
            "subagent": subagent_meta,
        }
    except (BundleError, LiveRunError, ProviderError, OSError, ValueError,
            json.JSONDecodeError) as exc:
        trace = _invalid_trace(case, arm, str(exc), subagent=subagent, state=state)
        trace["variant"] = variant
        return trace, {**_provider_error_details(exc), "subagent": subagent_meta}


def _assert_provider_preflight(config: dict[str, Any]) -> None:
    if config.get("provider") == "codex-mcp-cli":
        path = RESULTS_DIR / "redteam_codex_mcp_isolation.json"
        if not path.is_file():
            raise LiveRunError("refusing Codex MCP run: MCP-isolation red-team is missing")
        report = json.loads(path.read_text(encoding="utf-8"))
        if report.get("passed") is not True:
            raise LiveRunError("refusing Codex MCP run: MCP-isolation red-team failed")
        drift = frozen_surface_drift(report.get("frozen_surface_hashes"))
        if drift:
            raise LiveRunError(
                f"refusing Codex MCP run: MCP-isolation red-team is stale: {drift}")
        return
    if "seatbelt-v2" not in config.get("sandbox_policy", ""):
        return
    path = RESULTS_DIR / "redteam_provider_isolation.json"
    if not path.is_file():
        raise LiveRunError("refusing v2 run: provider-isolation red-team is missing")
    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("hardened_profile_passed") is not True:
        raise LiveRunError("refusing v2 run: hardened provider-isolation red-team failed")
    drift = frozen_surface_drift(report.get("frozen_surface_hashes"))
    if drift:
        raise LiveRunError(
            f"refusing v2 run: provider-isolation red-team is stale: {drift}")


def _assert_ready(config_path: str | Path = CONFIG_PATH) -> dict[str, Any]:
    config = load_config(config_path)
    calibration_path = RESULTS_DIR / "calibration.json"
    if not calibration_path.is_file():
        raise LiveRunError("refusing live run: calibration.json is missing")
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    if calibration.get("failures"):
        raise LiveRunError("refusing live run: calibration has failures")
    drift = frozen_surface_drift(calibration.get("frozen_surface_hashes"))
    if drift:
        raise LiveRunError(f"refusing live run: frozen surface drifted: {drift}")
    _assert_provider_preflight(config)
    return config


def _host_action_compliance(trace: dict[str, Any], details: dict[str, Any]) -> dict[str, Any]:
    main_count = len(trace.get("actions", []))
    subagent_required = ARM_HAS_SUBAGENT[trace["arm"]]
    subagent_meta = details.get("subagent") or {}
    subagent_count = len(subagent_meta.get("host_actions", []))
    failures = []
    if main_count < 1:
        failures.append("main-host-action-missing")
    if subagent_required and subagent_count < 1:
        failures.append("subagent-host-action-missing")
    return {
        "passed": not failures,
        "main_host_actions": main_count,
        "subagent_host_actions": subagent_count,
        "subagent_required": subagent_required,
        "failures": failures,
    }


def _assert_primary_qualifications(config: dict[str, Any]) -> dict[str, str]:
    primary = config.get("primary", {})
    if primary.get("blocked_reason"):
        raise LiveRunError(f"refusing primary: {primary['blocked_reason']}")
    specs = primary.get("required_qualification_artifacts")
    if not isinstance(specs, list) or not specs:
        raise LiveRunError(
            "refusing primary: required_qualification_artifacts must be explicit")
    ledger_path = RESULTS_DIR / QUALIFICATION_LEDGER_NAME
    ledger = _read_jsonl(ledger_path)
    verified: dict[str, str] = {}
    for spec in specs:
        required = {"file", "config_file", "provider", "sandbox_policy", "arms", "case_ids"}
        if not isinstance(spec, dict) or not required.issubset(spec):
            raise LiveRunError(
                "refusing primary: qualification spec lacks an external matrix/config anchor")
        path = RESULTS_DIR / spec["file"]
        if not path.is_file():
            raise LiveRunError(f"refusing primary: qualification artifact is missing: {path}")
        artifact = json.loads(path.read_text(encoding="utf-8"))
        if artifact.get("kind") != "live-subject-pilot":
            raise LiveRunError(f"refusing primary: not a pilot artifact: {path}")
        if artifact.get("qualification", {}).get("passed") is not True:
            raise LiveRunError(f"refusing primary: qualification did not pass: {path}")
        artifact_config = artifact.get("config", {})
        for key in ("provider", "sandbox_policy"):
            if artifact_config.get(key) != spec[key]:
                raise LiveRunError(
                    f"refusing primary: {path.name} has wrong {key}")
        config_file = HERE / spec["config_file"]
        if (artifact.get("config_file") != spec["config_file"] or
                not config_file.is_file() or
                artifact.get("config_sha256") != _sha256_path(config_file)):
            raise LiveRunError(
                f"refusing primary: {path.name} has wrong qualification config identity")
        pilot = artifact_config.get("pilot", {})
        expected_arms = spec["arms"]
        expected_cases = spec["case_ids"]
        if (pilot.get("arms") != expected_arms or pilot.get("case_ids") != expected_cases):
            raise LiveRunError(
                f"refusing primary: {path.name} qualification matrix declaration differs from spec")
        if artifact.get("n_runs") != len(expected_arms) * len(expected_cases):
            raise LiveRunError(
                f"refusing primary: incomplete qualification matrix: {path.name}")
        per_arm = artifact.get("per_arm", {})
        if set(per_arm) != set(expected_arms) or any(
                per_arm[arm].get("n") != len(expected_cases) for arm in expected_arms):
            raise LiveRunError(
                f"refusing primary: qualification arm coverage is incomplete: {path.name}")
        drift = frozen_surface_drift(artifact.get("frozen_surface_hashes"))
        if drift:
            raise LiveRunError(
                f"refusing primary: qualification artifact is stale: {path.name}: {drift}")
        artifact_sha256 = _sha256_path(path)
        matches = [entry for entry in ledger if (
            entry.get("file") == path.name
            and entry.get("sha256") == artifact_sha256
            and entry.get("config_sha256") == artifact.get("config_sha256")
            and entry.get("arms") == expected_arms
            and entry.get("case_ids") == expected_cases
        )]
        if len(matches) != 1:
            raise LiveRunError(
                f"refusing primary: qualification ledger mismatch: {path.name}")
        verified[path.name] = artifact_sha256
    return verified


def _assert_primary_authorization(
        config: dict[str, Any], config_path: str | Path,
        qualification_hashes: dict[str, str], case_ids: list[str], arms: list[str]
        ) -> tuple[str, int]:
    authorization_path = RESULTS_DIR / PRIMARY_AUTHORIZATION_NAME
    if not authorization_path.is_file():
        raise LiveRunError("refusing primary: explicit authorization file is missing")
    authorization = json.loads(authorization_path.read_text(encoding="utf-8"))
    selected_config = Path(config_path)
    if not selected_config.is_absolute():
        selected_config = HERE / selected_config
    expected = {
        "config_file": selected_config.name,
        "config_sha256": _sha256_path(selected_config),
        "qualification_sha256": qualification_hashes,
        "matrix": {"case_ids": case_ids, "arms": arms},
    }
    for key, value in expected.items():
        if authorization.get(key) != value:
            raise LiveRunError(f"refusing primary: authorization has wrong {key}")
    if not isinstance(authorization.get("authorized_by"), str) or not authorization["authorized_by"].strip():
        raise LiveRunError("refusing primary: authorization lacks authorized_by")
    if not isinstance(authorization.get("authorized_at"), str) or not authorization["authorized_at"].strip():
        raise LiveRunError("refusing primary: authorization lacks authorized_at")
    max_attempts = authorization.get("max_attempts")
    if not isinstance(max_attempts, int) or isinstance(max_attempts, bool) or max_attempts < 1:
        raise LiveRunError("refusing primary: authorization max_attempts must be positive")
    authorization_sha256 = _sha256_path(authorization_path)
    return authorization_sha256, max_attempts


_LEDGER_CHAIN_GENESIS = "handoff-dyn-primary-attempt-ledger-chain-genesis-v1"

# External anchor for the two real "started" rows recorded for the actual
# Claude-subject primary attempts (2026-08-09), BEFORE the hash-chain
# mechanism (Amendment 27) existed. Pinned here, in git-committed source,
# because the chain itself cannot protect a prefix that predates it --
# see verify_ledger_chain's docstring (independent review round 8,
# 2026-08-10) for why. Computed once from the real ledger file's raw line
# bytes; this constant must never be updated to match a changed ledger --
# if it stops matching, the ledger changed, which is exactly the point.
# An ORDERED tuple, not a set -- reproduced 2026-08-10 (independent review
# round 9): a frozenset comparison cannot distinguish the real prefix from
# the same rows reordered, or from one row duplicated and another dropped.
# Both returned "matches" before this. The review judged that an audit-
# precision issue rather than an E2E blocker, but the fix is a one-line
# type change, so there is no reason to leave the anchor weaker than it
# claims to be.
_KNOWN_LEGACY_LEDGER_PREFIX_LINE_HASHES = (
    "f7b6c7c65c6179b4ea65a7f45557ca4d22ca738cfe2b23255f410202a1dfaed5",
    "1e19a8dfec9ad25a7dc1077b364e3e61e42245d3a45af26cc41d4aa9ef2f3799",
)


def _parse_ledger_lines(handle, path: Path) -> list[dict[str, Any]]:
    """Shared by every ledger reader (claim and terminal append) so a
    malformed line is caught the same way everywhere."""
    handle.seek(0)
    entries = []
    for line_number, line in enumerate(handle, 1):
        if not line.strip():
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError as exc:
            raise LiveRunError(
                f"invalid JSONL record in {path.name}:{line_number}: {exc}") from exc
        if not isinstance(entry, dict):
            raise LiveRunError(f"non-object JSONL record in {path.name}:{line_number}")
        entries.append(entry)
    return entries


def _legacy_ledger_prefix_matches_known_hashes(handle, path: Path) -> bool:
    """Only meaningful for the ONE real production ledger (identified by
    its fixed path under `HERE`, not the mutable `RESULTS_DIR` tests
    monkeypatch) -- a test's synthetic ledger has no relationship to the
    pinned hashes and must not be checked against them. Returns True
    (vacuously) for any other path.

    Reproduced 2026-08-10 (independent review round 8, finding #1):
    `verify_ledger_chain` treats any row without `chain_hash` as an
    unverifiable-but-accepted legacy prefix -- deleting or editing one of
    the two real legacy rows still returned `verify_ledger_chain() ==
    True`, so the documented claim that this prefix was "a fixed,
    backward-compatible prefix" was aspirational, not enforced. This
    checks the ACTUAL bytes of each legacy (non-chained) line against a
    git-committed pin -- an attacker would also need to alter the git
    history of this source file to launder a change past both checks.
    """
    if path != (HERE / "results" / PRIMARY_ATTEMPT_LEDGER_NAME):
        return True
    handle.seek(0)
    observed = []
    for line in handle:
        stripped = line.rstrip("\n")
        if not stripped.strip():
            continue
        try:
            entry = json.loads(stripped)
        except json.JSONDecodeError:
            continue
        if "chain_hash" in entry:
            continue
        observed.append(hashlib.sha256(stripped.encode("utf-8")).hexdigest())
    return tuple(observed) == _KNOWN_LEGACY_LEDGER_PREFIX_LINE_HASHES


def _ledger_chain_hash(prev_chain_hash: str, record: dict[str, Any]) -> str:
    body = {k: v for k, v in record.items() if k != "chain_hash"}
    return hashlib.sha256(
        prev_chain_hash.encode("utf-8") + _canonical_json_bytes(body)).hexdigest()


def verify_ledger_chain(rows: list[dict[str, Any]]) -> bool:
    """Detects ACCIDENTAL or NAIVE corruption of the ledger -- a row deleted
    or edited without also recomputing the hashes after it. It does NOT
    resist a write-capable adversary: independent review round 8 (2026-08-10)
    correctly demonstrated that editing a row and then recomputing that
    row's chain_hash from its new content still verifies (`True`), because
    the hash and the thing it authenticates live in the same writable file
    -- a self-hash chain has no anchor outside itself. Real resistance to a
    write-capable attacker needs an anchor OUTSIDE this file (e.g. a signed
    authorization, a separate read-only manifest, or -- what this module
    uses for the one prefix that predates the chain --
    `_KNOWN_LEGACY_LEDGER_PREFIX_LINE_HASHES`, pinned in git-committed
    source). Treat this function as "did something change without anyone
    updating the hashes to match", not "was this ledger tampered with by
    someone who controls it".

    Each row written after this mechanism exists carries `chain_hash =
    sha256(previous row's chain_hash + this row's own content)`. Deleting a
    row breaks the link between its former neighbors (the next row's
    chain_hash was computed against a prev_chain_hash that no longer
    appears anywhere) UNLESS the attacker also recomputes everything after
    the deletion point, which they can do with only ledger-file write
    access. Rows written BEFORE this mechanism existed have no `chain_hash`
    field; this function alone treats them as an unverified prefix (see
    `_legacy_ledger_prefix_matches_known_hashes` for the actual anchor on
    that prefix) -- once a chained row appears, every row after it must
    also be chained.
    """
    prev = _LEDGER_CHAIN_GENESIS
    chain_started = False
    for row in rows:
        if "chain_hash" not in row:
            if chain_started:
                return False
            continue
        chain_started = True
        if row["chain_hash"] != _ledger_chain_hash(prev, row):
            return False
        prev = row["chain_hash"]
    return True


def verify_primary_attempt_artifacts(attempts: list[dict[str, Any]],
                                     authorization_sha256: str) -> list[dict[str, str]]:
    """Tamper-DETECTION, not just tamper-evidence: returns one entry per
    "completed" attempt (under this authorization) whose recorded artifact
    can no longer be verified -- either its hash no longer matches
    (`reason: "hash_mismatch"`) or the file is gone
    (`reason: "artifact_missing"`). Called from `_claim_primary_attempt` as
    an actual gate -- any entry refuses the NEW claim, it does not just get
    logged somewhere nobody reads.

    Added 2026-08-10 (independent review round 5, finding #2): output_sha256
    (Amendment 24) was written but nothing ever read it back and compared --
    the field proved tampering was DETECTABLE in principle, not that the
    system actually detected it.

    A missing artifact used to be silently skipped ("deleting a result is a
    different, and differently serious, problem from silently editing
    one"). Independent review round 6, finding #2 correctly rejected that:
    for reproducibility/audit purposes a "completed" row whose artifact is
    simply gone is exactly as unverifiable as a tampered one, and silently
    allowing a new claim on top of it erases the evidence trail the same
    way. Reproduced: deleting a completed attempt's output file left
    `verify_primary_attempt_artifacts() == []`, so the next claim proceeded
    as if nothing had happened. Both failure modes now fail closed.
    """
    problems = []
    for entry in attempts:
        if (entry.get("authorization_sha256") != authorization_sha256
                or entry.get("status") != "completed"):
            continue
        recorded_hash = entry.get("output_sha256")
        output_file = entry.get("output_file")
        if not recorded_hash or not output_file:
            continue
        path = RESULTS_DIR / output_file
        if not path.is_file():
            problems.append({"output_file": output_file, "reason": "artifact_missing"})
            continue
        if _sha256_path(path) != recorded_hash:
            problems.append({"output_file": output_file, "reason": "hash_mismatch"})
    return problems


def _claim_primary_attempt(authorization_sha256: str, max_attempts: int,
                           record: dict[str, Any]) -> None:
    """Atomically consume one authorized attempt before any provider call."""
    path = RESULTS_DIR / PRIMARY_ATTEMPT_LEDGER_NAME
    path.parent.mkdir(exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        attempts = _parse_ledger_lines(handle, path)
        if not verify_ledger_chain(attempts):
            raise LiveRunError(
                "refusing primary: attempt ledger hash chain does not verify -- "
                "a row was deleted or edited after being written. This detects "
                "accidental corruption or a change made without recomputing the "
                "chain; it does NOT resist a write-capable actor who edits a row "
                "and recomputes chain_hash to match (self-hash chains cannot "
                "prove that on their own).")
        if not _legacy_ledger_prefix_matches_known_hashes(handle, path):
            raise LiveRunError(
                "refusing primary: the pre-chain legacy rows in this ledger no "
                "longer match their git-committed pin -- one of the two real "
                "recorded primary attempts was deleted or edited.")
        # Count only "started" rows. Since Amendment 23 also appends a
        # terminal "completed"/"failed" row per attempt (finding #2 in that
        # amendment), counting every row halved the effective max_attempts:
        # reproduced 2026-08-10 (independent review round 3) -- with
        # max_attempts=3, started+completed x2 already sums to 4 rows, so
        # the 3rd claim was refused after only 2 real attempts. A "started"
        # row is written exactly once per attempt (by this function, before
        # any provider call), so it is the correct, single-counted signal
        # for "how many attempts has this authorization consumed".
        used = sum(
            entry.get("authorization_sha256") == authorization_sha256
            and entry.get("status") == "started"
            for entry in attempts)
        if used >= max_attempts:
            raise LiveRunError("refusing primary: authorization attempt limit exhausted")
        unverifiable = verify_primary_attempt_artifacts(attempts, authorization_sha256)
        if unverifiable:
            raise LiveRunError(
                f"refusing primary: prior completed result artifact(s) could not "
                f"be verified -- {unverifiable}. Whether changed since they were "
                f"recorded or deleted outright, both fail closed: do not claim a "
                f"new attempt on top of an unverifiable result history.")
        prev_chain = attempts[-1]["chain_hash"] if attempts and "chain_hash" in attempts[-1] \
            else _LEDGER_CHAIN_GENESIS
        entry = {**record, "authorization_sha256": authorization_sha256}
        entry["chain_hash"] = _ledger_chain_hash(prev_chain, entry)
        handle.seek(0, os.SEEK_END)
        handle.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _record_qualification(output_path: Path, out: dict[str, Any]) -> None:
    pilot = out["config"]["pilot"]
    _append_jsonl(RESULTS_DIR / QUALIFICATION_LEDGER_NAME, {
        "file": output_path.name,
        "sha256": _sha256_path(output_path),
        "config_file": out["config_file"],
        "config_sha256": out["config_sha256"],
        "arms": pilot["arms"],
        "case_ids": pilot["case_ids"],
        "qualification_passed": out["qualification"]["passed"],
        "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    })


def _score(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    payload = [{"trace": {k: v for k, v in record["trace"].items() if k != "variant"},
                "gold": record["gold"], "case": record["case"]}
               for record in records]
    payload_hashes = {
        record["key"]: hashlib.sha256(_canonical_json_bytes(item)).hexdigest()
        for record, item in zip(records, payload)
    }
    with tempfile.TemporaryDirectory(prefix="handoff-live-judge-") as directory:
        path = Path(directory) / "payload.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        results = run_clean_judge(path, source_hashes())
    if isinstance(results, dict) and "judge_error" in results:
        raise LiveRunError(f"clean judge failed: {results}")
    for result, record in zip(results, records):
        result["variant"] = record["trace"]["variant"]
    return results, payload_hashes


def _locked_append_jsonl(path: Path, record: dict[str, Any]) -> None:
    """Append one JSONL row under the same exclusive lock `_claim_primary_
    attempt` uses for its own append, so a concurrent claim and a terminal-
    status append can never interleave their writes.

    Added 2026-08-10 (independent review round 3, finding #3): the terminal
    write used to go through plain `_append_jsonl` (no lock), while the
    "started" write went through `_claim_primary_attempt`'s
    read-under-lock-then-append. Two processes racing a claim and a
    terminal append against the same file could interleave partial writes.

    Extended 2026-08-10 (independent review round 6, finding #2) to also
    read-then-chain like `_claim_primary_attempt` does, so a terminal row
    links into the same hash chain regardless of which of the two writers
    appended most recently.

    Extended again 2026-08-10 (independent review round 8, finding #3):
    this function read `existing` but never actually called
    `verify_ledger_chain` on it -- the module docstring's claim that "both
    claim and terminal append verify the chain" was true for one of the two
    writers. Reproduced: corrupt the chain, call this function, and it
    appended a new row without complaint, leaving the ledger permanently
    corrupted. Now raises the same way `_claim_primary_attempt` does.
    """
    path.parent.mkdir(exist_ok=True)
    with path.open("a+", encoding="utf-8") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        existing = _parse_ledger_lines(handle, path)
        if not verify_ledger_chain(existing):
            raise LiveRunError(
                "refusing to append: attempt ledger hash chain does not verify -- "
                "a row was deleted or edited after being written.")
        if not _legacy_ledger_prefix_matches_known_hashes(handle, path):
            raise LiveRunError(
                "refusing to append: the pre-chain legacy rows in this ledger no "
                "longer match their git-committed pin.")
        prev_chain = (existing[-1]["chain_hash"] if existing and "chain_hash" in existing[-1]
                     else _LEDGER_CHAIN_GENESIS)
        record = dict(record)
        record["chain_hash"] = _ledger_chain_hash(prev_chain, record)
        handle.seek(0, os.SEEK_END)
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _record_primary_attempt_outcome(authorization_sha256: str | None, output_file: str,
                                    status: str, *, attempt_id: str | None = None,
                                    extra: dict[str, Any] | None = None) -> None:
    """Append a terminal-status row to the same attempt ledger `_claim_
    primary_attempt` writes "started" rows to. Correlated by `attempt_id`
    (shared with the "started" row for the same attempt, independent of
    filenames) and `authorization_sha256`.

    Added 2026-08-10 (independent review, finding #2): before this, the
    ledger recorded ONLY "started" -- there was no way to distinguish a
    completed 32-cell run from a rate-limit abort, a process crash, or a
    failure after the output artifact was already written. "2 attempts
    consumed, 1 remaining" was, precisely, "2 attempts STARTED" -- an
    incomplete audit trail for something whose entire purpose is auditing
    attempt consumption.
    """
    record = {"authorization_sha256": authorization_sha256, "attempt_id": attempt_id,
              "output_file": output_file, "status": status,
              "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if extra:
        record.update(extra)
    _locked_append_jsonl(RESULTS_DIR / PRIMARY_ATTEMPT_LEDGER_NAME, record)


def run_phase(case_ids: list[str], arms: list[str], *, output_name: str,
              phase_name: str = "pilot", config_path: str | Path = CONFIG_PATH) -> int:
    config = _assert_ready(config_path)
    authorization_sha256: str | None = None
    attempt_id: str | None = None
    if phase_name == "primary":
        qualification_hashes = _assert_primary_qualifications(config)
        authorization_sha256, max_attempts = _assert_primary_authorization(
            config, config_path, qualification_hashes, case_ids, arms)
        attempt_id = uuid.uuid4().hex
    output_path = RESULTS_DIR / f"{output_name}.json"
    if output_path.exists():
        raise LiveRunError(f"refusing to overwrite an existing live result: {output_path}")
    if phase_name == "primary":
        _claim_primary_attempt(authorization_sha256, max_attempts, {
            "attempt_id": attempt_id,
            "config_file": Path(config_path).name,
            "output_file": output_path.name,
            "case_ids": case_ids,
            "arms": arms,
            "status": "started",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        })
    try:
        out = _run_phase_body(case_ids, arms, output_path, config, config_path, phase_name)
    except BaseException as exc:
        if phase_name == "primary":
            _record_primary_attempt_outcome(
                authorization_sha256, output_path.name, "failed", attempt_id=attempt_id,
                extra={"error": f"{type(exc).__name__}: {exc}",
                      "output_file_exists": output_path.exists(),
                      "output_sha256": _sha256_path(output_path) if output_path.exists() else None})
        raise
    if phase_name == "primary":
        _record_primary_attempt_outcome(
            authorization_sha256, output_path.name, "completed", attempt_id=attempt_id,
            extra={"n_runs": out["n_runs"],
                  "qualification_failed_cells": out["qualification"]["failed_cells"],
                  "output_sha256": _sha256_path(output_path)})
    return 0


def _run_phase_body(case_ids: list[str], arms: list[str], output_path: Path,
                    config: dict[str, Any], config_path: str | Path,
                    phase_name: str) -> dict[str, Any]:
    cases, gold = load()
    unknown = set(case_ids) - set(cases)
    if unknown:
        raise LiveRunError(f"unknown cases: {sorted(unknown)}")
    records: list[dict[str, Any]] = []
    raw: dict[str, Any] = {}
    # AF_UNIX has a short platform path limit. The ambient macOS TMPDIR often
    # contains a long per-user path, so sockets must live under /private/tmp.
    with tempfile.TemporaryDirectory(prefix="hdyn-", dir="/private/tmp") as directory:
        temp_root = Path(directory)
        for case_id in case_ids:
            case = cases[case_id]
            variant = "variant-L"
            reusable_subagent, subagent_meta = _run_retrieval_subagent(
                case, variant, config, temp_root / f"{case_id}-retrieval") if any(
                    ARM_HAS_SUBAGENT[arm] for arm in arms) else (None, None)
            for arm in arms:
                subagent = reusable_subagent if ARM_HAS_SUBAGENT[arm] else None
                meta = subagent_meta if ARM_HAS_SUBAGENT[arm] else None
                trace, details = run_cell(case, gold[case_id], arm, variant, config,
                                          temp_root / f"{case_id}-{arm}",
                                          subagent=subagent, subagent_meta=meta)
                key = f"{case_id}:{arm}"
                records.append({"trace": trace, "gold": gold[case_id], "case": case,
                                "details": details, "key": key})
                raw[key] = details
    results, judged_payload_hashes = _score(records)
    for result, record in zip(results, records):
        compliance = _host_action_compliance(
            record["trace"], record["details"])
        result["host_action_compliance"] = compliance
        result["execution_failure_codes"] = [] if compliance["passed"] else ["C5"]
        result["judged_payload_sha256"] = judged_payload_hashes[record["key"]]
    by_arm: dict[str, dict[str, Any]] = {}
    for arm in arms:
        rows = [row for row in results if row["arm"] == arm]
        by_arm[arm] = {
            "n": len(rows),
            "full_hard_gate_rate": round(sum(r["full_hard_gate"] for r in rows) / len(rows), 3),
            "invalid_run_rate": round(sum(r["invalid_run"] for r in rows) / len(rows), 3),
            "host_action_compliance_rate": round(sum(
                r["host_action_compliance"]["passed"] for r in rows) / len(rows), 3),
            "execution_noncompliance_count": sum(
                not r["host_action_compliance"]["passed"] for r in rows),
            "critical_path_recall": round(sum(r["critical_path_recall"] for r in rows) / len(rows), 3),
            "failure_codes": dict(Counter(code for r in rows for code in r["failure_codes"])),
            # Requested (independent review round 7, 2026-08-10) so primary/
            # pilot reporting carries the same safety breakdown run_smoke.py
            # has (Amendments 25-27): total/valid/V1/U1/auto-decided counts
            # and a confirmed-violation rate that excludes V1, U1, AND C5
            # (host-action noncompliance) from its denominator -- unlike
            # run_smoke.py's own rows, THESE rows carry host_action_
            # compliance, so _safety_summary's C5 exclusion actually applies
            # here.
            **_safety_summary(rows),
        }
    qualification_failures = [
        f"{row['case_id']}:{row['arm']}"
        for row in results
        if row["invalid_run"] or not row["host_action_compliance"]["passed"]
    ]
    qualification = {
        "passed": phase_name == "pilot" and not qualification_failures,
        "criteria": ["invalid_run == false", "main host actions >= 1",
                     "retrieval-subagent host actions >= 1 for R arms"],
        "failed_cells": qualification_failures,
    }
    selected_config_path = Path(config_path)
    if not selected_config_path.is_absolute():
        selected_config_path = HERE / selected_config_path
    out = {
        "kind": "live-subject-pilot" if phase_name == "pilot" else "live-subject-primary",
        "interpretation": ("qualification-only; this small pilot must not be used to estimate "
                           "arm effects" if phase_name == "pilot" else
                           "descriptive one-replicate live-subject run; no causal claim"),
        "config": config,
        "config_file": selected_config_path.name,
        "config_sha256": hashlib.sha256(selected_config_path.read_bytes()).hexdigest(),
        "judge_pins": source_hashes(),
        "frozen_surface_hashes": frozen_surface_hashes(),
        "qualification": qualification,
        "n_runs": len(results), "per_arm": by_arm, "results": results,
        "traces": [record["trace"] for record in records], "raw": raw,
    }
    if phase_name == "pilot":
        out["arm_effect_estimable"] = False
        out["n_per_cell"] = 1
    RESULTS_DIR.mkdir(exist_ok=True)
    output_path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if phase_name == "pilot":
        _record_qualification(output_path, out)
    print(json.dumps({"output": str(output_path),
                      "n_runs": len(results), "qualification": qualification,
                      "per_arm": by_arm}, ensure_ascii=False, indent=2))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pilot", action="store_true")
    group.add_argument("--primary", action="store_true")
    parser.add_argument("--case-id", action="append", help="override configured case ids")
    parser.add_argument("--arm", choices=ARMS, action="append", help="override configured arms")
    parser.add_argument("--output-name", help="new result artifact name; never overwrite a prior attempt")
    parser.add_argument("--config", required=True, choices=ALLOWED_CONFIG_NAMES,
                        help="explicit frozen provider config; no historical default")
    args = parser.parse_args()
    try:
        config = load_config(args.config)
        phase = config["pilot"] if args.pilot else config["primary"]
        phase_name = "pilot" if args.pilot else "primary"
        default_output = config.get("result_names", {}).get(
            phase_name, "live_pilot" if args.pilot else "live_primary")
        return run_phase(args.case_id or phase["case_ids"], args.arm or phase["arms"],
                         output_name=args.output_name or default_output,
                         phase_name=phase_name, config_path=args.config)
    except LiveRunError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
