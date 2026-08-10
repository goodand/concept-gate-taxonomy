#!/usr/bin/env python3
"""Build the blinded reviewer packet for the manual safety audit.

Amendment 34 (independent review round 12, finding #2). The audit used to be
one sentence of prose -- "blind audit all 32 cells" -- which is not an
executable pre-registration: it left the blinding, the randomisation, the
label criteria, the exclusion rules, and the artifact binding to be decided
after the results were visible. This script fixes the parts a script can fix.
The label criteria live in SAFETY_AUDIT_RUBRIC.md and are frozen with it.

WHAT THE REVIEWER MUST NOT SEE, and what this therefore strips:
  arm, provider, failure_codes, s1_candidate_status, retrieval_hard_gate,
  and every other prior score.
WHAT THE REVIEWER MUST SEE, and what this therefore keeps:
  the recommendation text, the case query, and the case's public authority
  document (NOT gold's term inventory -- see below).

The rule the reviewer judges against comes from the PUBLIC authority
document for the case -- the same text the subject read -- never from
hidden_gold. A reviewer shown gold's term inventory would be matching terms,
which is the automatic procedure this audit exists to replace. Note that
public_cases/cases.json carries no prose safety rule (its `trap` field is a
slug), so the authority document is the only honest source.

Case identity is deliberately NOT blinded: the forbidden action is
case-specific, so a reviewer who cannot tell which case a recommendation
belongs to cannot judge it at all. What is blinded is everything that could
anchor the judgement -- arm, provider, and every automatic score.

Usage:
    python3 make_safety_audit_blind_input.py results/<primary>.json
"""
from __future__ import annotations

import hashlib
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Fixed seed, declared before any result is looked at. Randomisation exists so
# reviewer fatigue and any residual case/arm ordering do not correlate with
# the labels; a fixed seed keeps the shuffle reproducible by a third party.
SHUFFLE_SEED = 20260810


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(result_path: Path) -> dict:
    data = json.loads(result_path.read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in json.loads(
        (HERE / "public_cases" / "cases.json").read_text(encoding="utf-8"))}
    corpus_root = HERE / "public_corpus" / "variant-L"

    def _authority_text(cid: str) -> str:
        case = cases.get(cid) or {}
        rel = case.get("handoff_path")
        if not rel:
            return ""
        doc = corpus_root / rel
        return doc.read_text(encoding="utf-8") if doc.is_file() else ""

    rules = {cid: _authority_text(cid) for cid in cases}

    # A result file keeps SCORES in `results` and the recommendation text in
    # a parallel `traces` list; neither alone is enough. Joined on
    # (case_id, arm, variant) rather than on position, because a positional
    # join would silently mis-pair if either list is ever filtered.
    rows = data.get("results") or []
    traces_by_key = {
        (t.get("case_id"), t.get("arm"), t.get("variant")): t
        for t in (data.get("traces") or [])}

    items, keymap, excluded = [], {}, []
    for i, row in enumerate(rows):
        cid = row.get("case_id")
        key = (cid, row.get("arm"), row.get("variant"))
        trace = traces_by_key.get(key)
        if trace is None:
            excluded.append({"index": i, "case_id": cid,
                             "reason": "no_matching_trace"})
            continue
        # V1 (invalid run) and C5 (host-action noncompliance) cells are
        # excluded from the audit denominator for the same reason
        # _safety_summary excludes them: no safety judgement can be made
        # about a run that did not execute or did not follow the contract.
        # They are LISTED, not silently dropped.
        if row.get("invalid_run") or (
                row.get("host_action_compliance") or {}).get("passed") is False:
            excluded.append({"index": i, "case_id": cid,
                             "reason": "V1" if row.get("invalid_run") else "C5"})
            continue
        actions = trace.get("recommended_actions") or []
        if not actions:
            # An empty recommendation list is not "safe"; it is a cell with
            # nothing to judge. Recorded as not_applicable, not as a pass.
            excluded.append({"index": i, "case_id": cid,
                             "reason": "no_recommendations"})
            continue
        for j, action in enumerate(actions):
            blind_id = f"B{len(items):04d}"
            items.append({
                "blind_id": blind_id,
                "recommendation": action,
                "case_id": cid,
                "case_query": (cases.get(cid) or {}).get("query", ""),
                "authority_document": rules.get(cid, ""),
            })
            keymap[blind_id] = {"index": i, "case_id": cid,
                                "action_index": j}

    rng = random.Random(SHUFFLE_SEED)
    rng.shuffle(items)
    # Re-issue blind ids AFTER shuffling so the id itself does not leak the
    # original ordering (and therefore the case grouping).
    remap = {}
    for n, item in enumerate(items):
        new_id = f"R{n:04d}"
        remap[new_id] = keymap[item["blind_id"]]
        item["blind_id"] = new_id

    return {
        "audit_version": 1,
        "rubric": "SAFETY_AUDIT_RUBRIC.md",
        "source_result_file": result_path.name,
        # Binds this packet to the exact bytes judged. A verdict file whose
        # source hash does not match the result it is applied to is rejected
        # by apply_safety_audit.py.
        "source_result_sha256": _sha256(result_path),
        "shuffle_seed": SHUFFLE_SEED,
        "n_items": len(items),
        "excluded_cells": excluded,
        "reviewer_packet": items,
        "unblinding_key": remap,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    result_path = Path(argv[1])
    if not result_path.is_file():
        print(f"no such result file: {result_path}", file=sys.stderr)
        return 2
    out = build(result_path)

    stem = result_path.stem
    packet = HERE / "results" / f"safety_audit_packet_{stem}.json"
    key = HERE / "results" / f"safety_audit_key_{stem}.json"
    for path in (packet, key):
        if path.exists():
            # results/ is append-only (record-V1-and-do-not-replace).
            print(f"refusing to overwrite existing artifact: {path.name}",
                  file=sys.stderr)
            return 2

    reviewer_view = {k: v for k, v in out.items() if k != "unblinding_key"}
    packet.write_text(json.dumps(reviewer_view, ensure_ascii=False, indent=1),
                      encoding="utf-8")
    key.write_text(json.dumps(
        {"source_result_sha256": out["source_result_sha256"],
         "unblinding_key": out["unblinding_key"]},
        ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{out['n_items']} recommendations -> {packet.name}")
    print(f"excluded cells: {len(out['excluded_cells'])}")
    print(f"KEY (do not give to reviewers): {key.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
