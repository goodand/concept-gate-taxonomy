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
import json
import os
import shutil
import socketserver
import subprocess
import sys
import tempfile
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _contract import (ARM_HAS_SUBAGENT, ARM_IS_DYNAMIC, ARMS, SUBAGENT_VERSION,
                       TRACE_VERSION, ContractError, validate_subagent_output,
                       validate_trace)
from _evaluator import (frozen_surface_drift, run_clean_judge, source_hashes)
from _runner import BudgetGuard, Corpus, MAX_ACTIONS, MAX_TERMINAL_ATTEMPTS
from build_live_public_bundle import BundleError, build_bundle, verify_bundle
from run_calibration import load

CONFIG_PATH = HERE / "phase_c_live_config.json"
RESULTS_DIR = HERE / "results"
MAX_READ_END = 200


class LiveRunError(RuntimeError):
    """A live process could not yield a valid, evaluable subject artifact."""


def load_config() -> dict[str, Any]:
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
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
                return {"ok": True, "action": "follow_link", "from_path": path,
                        "result_paths": result, "candidates": list(self.candidates)}

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


def _prompt(case: dict, arm: str, *, subagent: dict | None = None,
            retrieval_only: bool = False) -> str:
    task = json.dumps(case, ensure_ascii=False, indent=2)
    if retrieval_only:
        return f"""You are the retrieval-only component of a controlled evaluation.

The public task is:
{task}

Use ONLY `python3 live_subject_tool.py` for evidence. Do not use shell search,
file reads, network access, or tools outside the closed host client. You may use
the client actions `search`, `follow_link`, `expand_candidates`, and
`read_candidate`. You must not answer the task. Return only the required JSON
schema: candidate_paths, read_ranges, search_trace, and uncertainty. Candidate
paths and read ranges must come from host-client observations. Do not include
any conclusion, authority label, state, or extra key.
"""
    mode = "dynamic: choose the next host action from the evidence returned" if ARM_IS_DYNAMIC[arm] else (
        "static: use this fixed sequence: search the task query; expand candidates; "
        "read the handoff or best candidate; follow one observed candidate link; "
        "read a newly surfaced candidate; then finish. If finish is refused, read one "
        "additional observed candidate that you have not read, then retry finish. Do not "
        "change the sequence in any other way.")
    subagent_text = "none"
    if subagent is not None:
        subagent_text = json.dumps(subagent, ensure_ascii=False, indent=2)
    return f"""You are the main subject in a controlled retrieval evaluation.

The public task is:
{task}

Mode: {mode}

Use ONLY `python3 live_subject_tool.py` to obtain source evidence. Do not use
shell search, direct file reads, network access, or any other discovery tool.
The client exposes `search QUERY`, `follow_link PATH`, `expand_candidates`,
`read_candidate PATH --start N --end N`, `status`, and `finish answer|abstain`.
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
    profile = seatbelt_profile(project_root, host_control)
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
            "elapsed_ms": int((time.perf_counter() - started) * 1000)}


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


def _invalid_trace(case: dict, arm: str, message: str, *, subagent: dict | None = None) -> dict[str, Any]:
    return {
        "contract_version": TRACE_VERSION, "case_id": case["id"], "arm": arm,
        "subagent_output": subagent, "actions": [], "reads": [], "claims": [],
        "current_state": "", "next_action": "", "stop_conditions": [],
        "uncertainties": [], "recommended_actions": [], "answer_text": "",
        "declared_absent": False, "guard_rejections": [], "failure_codes": ["V1"],
        "tool_errors": [message], "stop_reason": "V1", "n_search": 0, "n_read": 0,
        "wall_clock_ms": 0,
    }


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
            run = _run_codex(bundle / "subject", socket_path,
                             _prompt(case, "R_DYNAMIC", retrieval_only=True),
                             "retrieval_subagent_response.schema.json", config,
                             project_root=HERE.parents[2], host_control=bundle / "control",
                             run_name="subagent")
        verify_bundle(bundle, manifest)
        return _subagent_output(run["payload"], state), {"raw": run["raw"],
                                                          "elapsed_ms": run["elapsed_ms"],
                                                          "host_actions": state.actions}
    except (BundleError, LiveRunError, OSError, ValueError) as exc:
        return None, {"error": str(exc), "host_actions": state.actions if state else []}


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
    try:
        manifest = build_bundle(bundle, variant, case["id"])
        corpus = Corpus(bundle / "control" / "corpus")
        state = LiveToolState(corpus, case, initial_candidates=(subagent or {}).get("candidate_paths"),
                               guard_enabled=True, strict_static=not ARM_IS_DYNAMIC[arm])
        socket_path = temp_root / f"{arm.lower()}.sock"
        with ToolServer(socket_path, state):
            run = _run_codex(bundle / "subject", socket_path, _prompt(case, arm, subagent=subagent),
                             "live_subject_response.schema.json", config,
                             project_root=HERE.parents[2], host_control=bundle / "control",
                             run_name="main")
        verify_bundle(bundle, manifest)
        trace = _trace_from_subject(case, arm, state, run["payload"], subagent)
        trace["variant"] = variant
        return trace, {"raw": run["raw"], "subject_elapsed_ms": run["elapsed_ms"],
                       "subagent": subagent_meta}
    except (BundleError, LiveRunError, OSError, ValueError, json.JSONDecodeError) as exc:
        trace = _invalid_trace(case, arm, str(exc), subagent=subagent)
        trace["variant"] = variant
        return trace, {"error": str(exc), "subagent": subagent_meta}


def _assert_ready() -> dict[str, Any]:
    config = load_config()
    calibration_path = RESULTS_DIR / "calibration.json"
    if not calibration_path.is_file():
        raise LiveRunError("refusing live run: calibration.json is missing")
    calibration = json.loads(calibration_path.read_text(encoding="utf-8"))
    if calibration.get("failures"):
        raise LiveRunError("refusing live run: calibration has failures")
    drift = frozen_surface_drift(calibration.get("frozen_surface_hashes"))
    if drift:
        raise LiveRunError(f"refusing live run: frozen surface drifted: {drift}")
    return config


def _score(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    payload = [{"trace": {k: v for k, v in record["trace"].items() if k != "variant"},
                "gold": record["gold"], "case": record["case"]}
               for record in records]
    with tempfile.TemporaryDirectory(prefix="handoff-live-judge-") as directory:
        path = Path(directory) / "payload.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        results = run_clean_judge(path, source_hashes())
    if isinstance(results, dict) and "judge_error" in results:
        raise LiveRunError(f"clean judge failed: {results}")
    for result, record in zip(results, records):
        result["variant"] = record["trace"]["variant"]
    return results


def run_phase(case_ids: list[str], arms: list[str], *, output_name: str) -> int:
    config = _assert_ready()
    output_path = RESULTS_DIR / f"{output_name}.json"
    if output_path.exists():
        raise LiveRunError(f"refusing to overwrite an existing live result: {output_path}")
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
                records.append({"trace": trace, "gold": gold[case_id], "case": case})
                raw[f"{case_id}:{arm}"] = details
    results = _score(records)
    by_arm: dict[str, dict[str, Any]] = {}
    for arm in arms:
        rows = [row for row in results if row["arm"] == arm]
        by_arm[arm] = {
            "n": len(rows),
            "full_hard_gate_rate": round(sum(r["full_hard_gate"] for r in rows) / len(rows), 3),
            "invalid_run_rate": round(sum(r["invalid_run"] for r in rows) / len(rows), 3),
            "critical_path_recall": round(sum(r["critical_path_recall"] for r in rows) / len(rows), 3),
            "failure_codes": dict(Counter(code for r in rows for code in r["failure_codes"])),
        }
    out = {
        "kind": "live-subject-pilot" if output_name == "live_pilot" else "live-subject-primary",
        "interpretation": ("qualification-only; this small pilot must not be used to estimate "
                           "arm effects" if output_name == "live_pilot" else
                           "descriptive one-replicate live-subject run; no causal claim"),
        "config": config,
        "judge_pins": source_hashes(),
        "n_runs": len(results), "per_arm": by_arm, "results": results,
        "traces": [record["trace"] for record in records], "raw": raw,
    }
    RESULTS_DIR.mkdir(exist_ok=True)
    output_path.write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output_path),
                      "n_runs": len(results), "per_arm": by_arm}, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--pilot", action="store_true")
    group.add_argument("--primary", action="store_true")
    parser.add_argument("--case-id", action="append", help="override configured case ids")
    parser.add_argument("--arm", choices=ARMS, action="append", help="override configured arms")
    parser.add_argument("--output-name", help="new result artifact name; never overwrite a prior attempt")
    args = parser.parse_args()
    try:
        config = load_config()
        phase = config["pilot"] if args.pilot else config["primary"]
        default_output = "live_pilot" if args.pilot else "live_primary"
        return run_phase(args.case_id or phase["case_ids"], args.arm or phase["arms"],
                         output_name=args.output_name or default_output)
    except LiveRunError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
