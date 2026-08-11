#!/usr/bin/env python3
"""Build the blinded reviewer packet for the manual safety audit.

Amendment 34 (round 12) introduced this step; Amendment 35 (round 13) made it
fail-closed. The audit is now the ONLY route by which a safety judgement
reaches a result, so a defect here is a defect in the headline -- round 13
found three: reviewers got an empty rule document for every discovery case,
a missing trace was quietly demoted to an exclusion, and nothing bound the
packet to the rubric it was judged under.

WHAT THE REVIEWER MUST NOT SEE, and what this therefore strips:
  arm, provider, failure_codes, s1_candidate_status, retrieval_hard_gate,
  and every other prior score.
WHAT THE REVIEWER MUST SEE, and what this therefore keeps:
  the recommendation text, the case query, the case's `safety_question`, and
  the full text of its PUBLIC authority documents.

The rule the reviewer judges against comes from safety_audit_authorities.json
-- a frozen manifest of public corpus paths -- never from hidden_gold and
never from `cases.json`'s `handoff_path`. That field is the case's ENTRY
POINT, not its authority: for HD02 it points at docs/HANDOFF.md while the
rule lives in docs/DECISION_freeze_policy.md, and for DS05/DS06/DS07 it is
null. Reviewers were being asked to judge safety against an empty string.

Case identity is deliberately NOT blinded: the forbidden action is
case-specific, so a reviewer who cannot tell which case a recommendation
belongs to cannot judge it at all. What is blinded is everything that could
anchor the judgement -- arm, provider, and every automatic score.

FAIL-CLOSED. This refuses to produce a packet when the audit input is not
trustworthy: a missing or empty authority document, a case absent from the
manifest, a result row with no matching trace, or duplicate cell keys. Round
13, finding #5: these used to be added to `excluded_cells` and the run
continued, and the apply step -- which never received `excluded_cells` --
then treated the unlabelled rows as `not_applicable`. A malformed artifact
must not become a passing cell.

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

RUBRIC = HERE / "SAFETY_AUDIT_RUBRIC.md"
AUTHORITIES = HERE / "safety_audit_authorities.json"


class AuditInputError(Exception):
    """The audit input is not trustworthy. No packet is produced."""


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _authority_texts(cid: str, manifest: dict, variant: str) -> list[dict]:
    entry = manifest["cases"].get(cid)
    if entry is None:
        raise AuditInputError(
            f"{cid} is not in safety_audit_authorities.json -- a reviewer "
            "cannot judge a case whose rule is undeclared")
    root = HERE / "public_corpus" / (variant or "variant-L")
    docs = []
    for rel in entry["authority_paths"]:
        doc = root / rel
        if not doc.is_file():
            raise AuditInputError(f"{cid}: authority document missing: {rel}")
        text = doc.read_text(encoding="utf-8")
        if not text.strip():
            raise AuditInputError(f"{cid}: authority document is empty: {rel}")
        docs.append({"path": rel, "text": text})
    return docs


def build(result_path: Path, *, expected_cells: int | None = None) -> dict:
    data = json.loads(result_path.read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in json.loads(
        (HERE / "public_cases" / "cases.json").read_text(encoding="utf-8"))}
    manifest = json.loads(AUTHORITIES.read_text(encoding="utf-8"))

    rows = data.get("results") or []
    if not rows:
        raise AuditInputError(f"{result_path.name} carries no `results` rows")
    if expected_cells is not None and len(rows) != expected_cells:
        raise AuditInputError(
            f"expected {expected_cells} cells, result carries {len(rows)}")

    # Cell keys must be unique on BOTH sides and pair 1:1. A duplicate key
    # would make the join ambiguous, and a positional join would silently
    # mis-pair -- neither may be resolved by guessing.
    def _key(row):
        return (row.get("case_id"), row.get("arm"), row.get("variant"))

    row_keys = [_key(r) for r in rows]
    if len(set(row_keys)) != len(row_keys):
        dupes = sorted({str(k) for k in row_keys if row_keys.count(k) > 1})
        raise AuditInputError(f"duplicate result cell keys: {dupes}")
    traces = data.get("traces") or []
    trace_keys = [_key(t) for t in traces]
    if len(set(trace_keys)) != len(trace_keys):
        dupes = sorted({str(k) for k in trace_keys if trace_keys.count(k) > 1})
        raise AuditInputError(f"duplicate trace cell keys: {dupes}")
    traces_by_key = dict(zip(trace_keys, traces))
    orphans = sorted(str(k) for k in set(row_keys) - set(trace_keys))
    if orphans:
        raise AuditInputError(
            f"result rows with no matching trace: {orphans} -- the artifact "
            "is malformed; an unjudgeable cell must not become a passing one")

    items, keymap, no_recommendation = [], {}, []
    for i, row in enumerate(rows):
        cid = row.get("case_id")
        trace = traces_by_key[_key(row)]
        docs = _authority_texts(cid, manifest, row.get("variant"))
        # V1 (invalid run) and C5 (host-action noncompliance) are NOT skipped
        # here. They carry no safety judgement either, but the apply step
        # decides that from the row itself; dropping them here would mean the
        # two steps disagree about the denominator (round 13, finding #5).
        actions = trace.get("recommended_actions") or []
        if not actions:
            no_recommendation.append({"index": i, "case_id": cid})
            continue
        for j, action in enumerate(actions):
            blind_id = f"B{len(items):04d}"
            items.append({
                "blind_id": blind_id,
                "recommendation": action,
                "case_id": cid,
                "case_query": (cases.get(cid) or {}).get("query", ""),
                "safety_question": manifest["cases"][cid]["safety_question"],
                "authority_documents": docs,
            })
            keymap[blind_id] = {
                "index": i, "case_id": cid, "arm": row.get("arm"),
                "variant": row.get("variant"), "action_index": j,
                # Pins WHICH text was judged. The apply step re-derives this
                # from the result file and rejects a key whose locations were
                # edited (round 13, finding #4).
                "recommendation_sha256": _sha256_bytes(action.encode("utf-8")),
            }

    rng = random.Random(SHUFFLE_SEED)
    rng.shuffle(items)
    # Re-issue blind ids AFTER shuffling so the id itself does not leak the
    # original ordering (and therefore the case grouping).
    remap = {}
    for n, item in enumerate(items):
        new_id = f"R{n:04d}"
        remap[new_id] = keymap[item["blind_id"]]
        item["blind_id"] = new_id

    packet = {
        "audit_version": 2,
        "rubric_file": RUBRIC.name,
        "rubric_sha256": _sha256(RUBRIC),
        "authorities_file": AUTHORITIES.name,
        "authorities_sha256": _sha256(AUTHORITIES),
        "source_result_file": result_path.name,
        "source_result_sha256": _sha256(result_path),
        "shuffle_seed": SHUFFLE_SEED,
        "n_items": len(items),
        "n_cells": len(rows),
        "cells_without_recommendations": no_recommendation,
        "reviewer_packet": items,
    }
    # The key is bound to the packet BYTES the reviewers saw, so a packet
    # rebuilt under different rules cannot be adjudicated with an old key.
    packet_bytes = json.dumps(packet, ensure_ascii=False, indent=1,
                              sort_keys=True).encode("utf-8")
    return {
        "packet": packet,
        "packet_bytes": packet_bytes,
        "key": {
            "audit_version": 2,
            "packet_sha256": _sha256_bytes(packet_bytes),
            "source_result_sha256": packet["source_result_sha256"],
            "rubric_sha256": packet["rubric_sha256"],
            "authorities_sha256": packet["authorities_sha256"],
            "unblinding_key": remap,
        },
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    result_path = Path(argv[1])
    if not result_path.is_file():
        print(f"no such result file: {result_path}", file=sys.stderr)
        return 2
    try:
        out = build(result_path)
    except AuditInputError as exc:
        print(f"refusing to build a packet: {exc}", file=sys.stderr)
        return 2

    stem = result_path.stem
    packet_path = HERE / "results" / f"safety_audit_packet_{stem}.json"
    key_path = HERE / "results" / f"safety_audit_key_{stem}.json"
    for path in (packet_path, key_path):
        if path.exists():
            # results/ is append-only (record-V1-and-do-not-replace).
            print(f"refusing to overwrite existing artifact: {path.name}",
                  file=sys.stderr)
            return 2

    packet_path.write_bytes(out["packet_bytes"])
    key_path.write_text(json.dumps(out["key"], ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(f"{out['packet']['n_items']} recommendations -> {packet_path.name}")
    print(f"packet sha256: {out['key']['packet_sha256']}")
    print(f"cells with no recommendation to judge: "
          f"{len(out['packet']['cells_without_recommendations'])}")
    print(f"KEY (do not give to reviewers): {key_path.name}")
    print("\nEach reviewer submits: "
          '{"reviewer_id": "<unique name>", "packet_sha256": "<above>", '
          '"labels": {...}}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
