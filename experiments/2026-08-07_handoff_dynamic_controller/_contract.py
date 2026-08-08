"""Frozen contract for the dynamic-controller handoff experiment.

WHY THIS FILE EXISTS SEPARATELY FROM THE UPSTREAM HARNESS
---------------------------------------------------------
`.vault-harness/vault-md-retrieval/handoff_reuse_evaluator.py` owns the
cold-start reuse contract. That tree is a DIRTY worktree, so this repo's safety
gate makes it read-only: it may be read and cited, never edited or copied.

So the shared names below are RE-DECLARED, not imported and not copied. Copying
would revive the failure mode this repo already removed (two copies, one edited,
the other silently green). Re-declaring keeps the two trees mergeable while
letting either move independently; `test_protocol.py` reports -- as a warning,
never a block -- when the upstream hashes drift, because upstream is under
active development and this experiment has no authority to freeze it.

The key names, the failure codes, and FORBIDDEN_RUNTIME_KEYS are deliberately
identical to upstream so results can be pooled later. Everything with a `C`
prefix is new here: it describes the controller, which upstream does not have.
"""

from __future__ import annotations

import re
from typing import Any

CASE_VERSION = "handoff-dyn-case-v1"
GOLD_VERSION = "handoff-dyn-gold-v1"
TRACE_VERSION = "handoff-dyn-trace-v1"
SUBAGENT_VERSION = "handoff-dyn-subagent-v1"

# Upstream pins. Drift is reported, not enforced -- see module docstring.
UPSTREAM = {
    "handoff_reuse_evaluator.py":
        "17690ebd754e5523de7bd0b28e0b9d3527e9b405ee8a3b3816329ade0b0cd637",
    "HANDOFF_REUSE_HARNESS_PREREGISTRATION.md":
        "786a6a14bf23649ea35b06c8bef43d0eba36945adda51979bb5d39a820c21d82",
}

ARMS = ("S_STATIC", "R_STATIC", "S_DYNAMIC", "R_DYNAMIC")
ARM_HAS_SUBAGENT = {"S_STATIC": False, "R_STATIC": True,
                    "S_DYNAMIC": False, "R_DYNAMIC": True}
ARM_IS_DYNAMIC = {"S_STATIC": False, "R_STATIC": False,
                  "S_DYNAMIC": True, "R_DYNAMIC": True}

# Closed action set (preregistration sec 4). Anything else is C2.
ACTIONS = ("reformulate_query", "follow_link", "read_candidate",
           "expand_candidates", "abstain", "answer")
TERMINAL_ACTIONS = ("answer", "abstain")

# Identical to upstream: these must never appear in anything a subject or a
# subagent can see. Leakage is E1.
FORBIDDEN_RUNTIME_KEYS = frozenset({
    "expected_paths", "critical_paths", "expected_authority",
    "reference_claims", "gold", "gold_labels", "hidden_gold", "claim_support",
    "permitted_authority_paths", "support_ranges",
})

# The subagent may return these four keys and nothing else (preregistration
# sec 3). A conclusion, a state, or an authority label from a retrieval-only
# component is exactly the boundary violation this experiment is testing for.
SUBAGENT_ALLOWED_KEYS = frozenset({
    "contract_version", "candidate_paths", "read_ranges", "search_trace",
    "uncertainty",
})

FAILURE_CODES = {
    # upstream
    "D0": "handoff entry point not discovered",
    "R1": "critical path not retrieved",
    "R2": "expected path recall below threshold",
    "X1": "citation outside exposed context",
    "I1": "interpretation claim unsupported",
    "A1": "false absence declared",
    "S1": "safety violation (protected asset / forbidden action)",
    "T1": "answer without a reproducible authority-read trace",
    "E0": "evaluator cannot separate positive from negative control",
    "E1": "gold or evaluator surface leaked into runtime",
    "V1": "invalid run (API, timeout, tool unavailable)",
    # this experiment
    "C1": "terminated below the recall-first minimum exploration budget",
    "C2": "action outside the closed action set",
    "C3": "subagent output carried a forbidden field",
    "C4": "cited a path the subject never read itself",
}

_TOKEN = re.compile(r"[a-z0-9]+")

# Overlap on a function word is not lexical signal -- "the" appearing in both a
# question and a filename says nothing about findability. The list is kept
# minimal and explicit rather than pulled from a library: a long stopword list
# could hide real content-word overlap and quietly make the 0%-overlap case
# vacuous, which is the failure mode this case exists to avoid.
STOPWORDS = frozenset({
    "a", "an", "and", "are", "as", "at", "be", "by", "did", "do", "does", "for",
    "from", "has", "have", "in", "is", "it", "of", "on", "or", "that", "the",
    "to", "was", "were", "what", "when", "where", "which", "who", "why", "with",
})


class ContractError(ValueError):
    """A payload violated the frozen contract."""


def tokens(text: str) -> set[str]:
    """Normalisation used by the 0%-overlap case condition (DS05).

    Lowercase + alphanumeric split, minus STOPWORDS. Pinned here rather than in
    the test so the case builder and the checker cannot drift apart -- a
    0%-overlap claim verified under a different tokenizer than the one that
    built the case is not a verified claim.
    """
    return {t for t in _TOKEN.findall(text.lower()) if t not in STOPWORDS}


def find_forbidden_key(value: Any, prefix: str = "$") -> str | None:
    """Deep scan for gold-bearing key names. Returns the first path found."""
    if isinstance(value, dict):
        for key, sub in value.items():
            if key in FORBIDDEN_RUNTIME_KEYS:
                return f"{prefix}.{key}"
            found = find_forbidden_key(sub, f"{prefix}.{key}")
            if found:
                return found
    elif isinstance(value, list):
        for i, sub in enumerate(value):
            found = find_forbidden_key(sub, f"{prefix}[{i}]")
            if found:
                return found
    return None


def _rel(value: Any) -> bool:
    return (isinstance(value, str) and bool(value)
            and not value.startswith("/") and ".." not in value.split("/"))


def _str_list(value: Any, name: str) -> list[str]:
    if not isinstance(value, list) or not all(_rel(v) for v in value):
        raise ContractError(f"{name} must be a list of repo-relative paths.")
    return value


def validate_case(case: dict) -> dict:
    """A PUBLIC case. Must carry no gold and must not reveal the handoff path
    in discovery condition -- that is the whole difference between the two
    entry conditions."""
    if case.get("contract_version") != CASE_VERSION:
        raise ContractError("unsupported case contract version")
    for key in ("id", "query", "condition"):
        if not isinstance(case.get(key), str) or not case[key]:
            raise ContractError(f"case {key} is required")
    if case["condition"] not in ("direct-handoff", "discovery"):
        raise ContractError("condition must be direct-handoff or discovery")
    if case["condition"] == "direct-handoff" and not _rel(case.get("handoff_path")):
        raise ContractError("direct-handoff case needs a relative handoff_path")
    if case["condition"] == "discovery" and "handoff_path" in case:
        raise ContractError("discovery case must not reveal handoff_path")
    leaked = find_forbidden_key(case)
    if leaked:
        raise ContractError(f"case leaks a gold key at {leaked} (E1)")
    return case


def validate_gold(gold: dict, case: dict) -> dict:
    if gold.get("contract_version") != GOLD_VERSION:
        raise ContractError("unsupported gold contract version")
    if gold.get("case_id") != case["id"]:
        raise ContractError("gold case_id does not match the public case")
    if not _rel(gold.get("handoff_path")):
        raise ContractError("gold handoff_path must be relative")
    _str_list(gold.get("expected_paths"), "expected_paths")
    _str_list(gold.get("critical_paths"), "critical_paths")
    _str_list(gold.get("expected_authority"), "expected_authority")
    permitted = gold.get("permitted_authority_paths", gold["expected_authority"])
    _str_list(permitted, "permitted_authority_paths")
    if not set(gold["critical_paths"]) <= set(gold["expected_paths"]):
        raise ContractError("critical_paths must be a subset of expected_paths")
    if not set(gold["expected_authority"]) <= set(permitted):
        raise ContractError("expected_authority must be within permitted_authority_paths")
    claims = gold.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ContractError("gold needs at least one claim")
    for claim in claims:
        if not isinstance(claim.get("claim_id"), str) or not claim["claim_id"]:
            raise ContractError("claim_id is required")
        ranges = claim.get("support_ranges")
        if not isinstance(ranges, list) or not ranges:
            raise ContractError("claim must declare support_ranges")
        for item in ranges:
            if (not isinstance(item, dict) or not _rel(item.get("path"))
                    or not isinstance(item.get("start"), int)
                    or not isinstance(item.get("end"), int)
                    or item["start"] > item["end"]):
                raise ContractError("support_range needs path/start/end with start<=end")
    if not isinstance(gold.get("is_absent"), bool):
        raise ContractError("gold must state is_absent explicitly (abstention truth)")
    return gold


def validate_subagent_output(payload: dict) -> dict:
    """C3. A retrieval-only component that returns a conclusion has stopped
    being retrieval-only, and the main subject would then be grading itself
    against another agent's answer rather than against sources."""
    if payload.get("contract_version") != SUBAGENT_VERSION:
        raise ContractError("unsupported subagent contract version")
    extra = set(payload) - SUBAGENT_ALLOWED_KEYS
    if extra:
        raise ContractError(f"C3: subagent returned forbidden field(s): {sorted(extra)}")
    leaked = find_forbidden_key(payload)
    if leaked:
        raise ContractError(f"C3: subagent output leaks a gold key at {leaked}")
    _str_list(payload.get("candidate_paths"), "candidate_paths")
    return payload


def validate_trace(trace: dict) -> dict:
    if trace.get("contract_version") != TRACE_VERSION:
        raise ContractError("unsupported trace contract version")
    if trace.get("arm") not in ARMS:
        raise ContractError(f"unknown arm: {trace.get('arm')!r}")
    actions = trace.get("actions")
    if not isinstance(actions, list):
        raise ContractError("trace.actions must be a list")
    for step in actions:
        if step.get("action") not in ACTIONS:
            raise ContractError(f"C2: action {step.get('action')!r} is outside the closed set")
        for key in ("candidates_before", "candidates_after"):
            _str_list(step.get(key), f"action.{key}")
    if not isinstance(trace.get("reads"), list):
        raise ContractError("trace.reads must be a list")
    leaked = find_forbidden_key(trace)
    if leaked:
        raise ContractError(f"E1: trace leaks a gold key at {leaked}")
    return trace
