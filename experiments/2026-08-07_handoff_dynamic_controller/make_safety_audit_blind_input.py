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

FAIL-CLOSED, against a frozen spec. Every invariant the input must satisfy
lives in `safety_audit_spec.json` and is checked by `validate_audit_input` --
kind, the exact case x arm matrix, allowed variants, cell count, duplicate
keys, and a result<->trace bijection in BOTH directions. Plus a present,
non-empty authority document per case.

Round 13, finding #5: malformed cells used to be added to `excluded_cells`
and the run continued, and the apply step -- which never received
`excluded_cells` -- then treated the unlabelled rows as `not_applicable`.
Round 15: the matrix check existed but was an OPTIONAL keyword the CLI never
passed, so a 1-cell, non-primary artifact produced a valid packet; and the
trace check looked in one direction only, so an extra trace was ignored.
Both were reproduced. The lesson taken is not "add two more conditionals" --
it is that scattered conditionals are how the next invariant goes missing.
There is no longer any way for a caller to skip validation.

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
SPEC = HERE / "safety_audit_spec.json"


from _provenance import (SYNTHETIC, VERIFIED, ProvenanceError,  # noqa: E402
                         VerifiedRunReceipt, verify_run)


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


def _cell_key(row: dict) -> tuple:
    return (row.get("case_id"), row.get("arm"), row.get("variant"))


def validate_audit_input(data: dict, spec: dict, *, source: str) -> dict:
    """Check EVERY audit-input invariant against the frozen spec, in one place.

    Round 15: these used to be scattered conditionals, and the one that
    mattered most -- the matrix size -- was an optional keyword the CLI never
    passed. A 1-cell, non-primary artifact built a valid packet. Fixing them
    one `if` at a time is how the next invariant goes missing, so they are all
    here and the caller cannot opt out of any of them.

    The spec is the authority, NOT the artifact's own self-reported fields:
    an artifact claiming to be a primary run is not evidence that it is one.

    Returns the trace-by-cell-key map, since building it is most of the work.
    """
    kind = data.get("kind")
    if kind not in spec["allowed_kinds"]:
        raise AuditInputError(
            f"{source}: kind is {kind!r}, not one of {spec['allowed_kinds']} "
            "-- a pilot or smoke artifact is not a primary result")

    rows = data.get("results") or []
    if not rows:
        raise AuditInputError(f"{source} carries no `results` rows")
    if len(rows) != spec["expected_cells"]:
        raise AuditInputError(
            f"{source}: expected {spec['expected_cells']} cells, carries "
            f"{len(rows)}")

    expected_keys = {(c, a) for c in spec["case_ids"] for a in spec["arms"]}
    row_keys = [_cell_key(r) for r in rows]
    if len(set(row_keys)) != len(row_keys):
        dupes = sorted({str(k) for k in row_keys if row_keys.count(k) > 1})
        raise AuditInputError(f"{source}: duplicate result cell keys: {dupes}")

    bad_variant = sorted({str(k[2]) for k in row_keys
                          if k[2] not in spec["allowed_variants"]})
    if bad_variant:
        raise AuditInputError(f"{source}: variants outside the spec: {bad_variant}")

    got = {(k[0], k[1]) for k in row_keys}
    if got != expected_keys:
        missing = sorted(str(k) for k in expected_keys - got)
        extra = sorted(str(k) for k in got - expected_keys)
        raise AuditInputError(
            f"{source}: case x arm matrix does not match the spec "
            f"(missing={missing[:6]}, extra={extra[:6]})")

    traces = data.get("traces") or []
    trace_keys = [_cell_key(t) for t in traces]
    if len(set(trace_keys)) != len(trace_keys):
        dupes = sorted({str(k) for k in trace_keys if trace_keys.count(k) > 1})
        raise AuditInputError(f"{source}: duplicate trace cell keys: {dupes}")

    if spec["require_result_trace_bijection"] and set(row_keys) != set(trace_keys):
        # BOTH directions. The previous check looked only for result rows
        # without a trace; an EXTRA trace was silently ignored, so an
        # artifact carrying a cell that no result row accounts for still
        # produced a packet (round 15, reproduced).
        orphan_rows = sorted(str(k) for k in set(row_keys) - set(trace_keys))
        orphan_traces = sorted(str(k) for k in set(trace_keys) - set(row_keys))
        raise AuditInputError(
            f"{source}: result and trace cells are not a bijection "
            f"(rows without trace={orphan_rows[:6]}, "
            f"traces without row={orphan_traces[:6]}) -- the artifact is "
            "malformed; an unjudgeable cell must not become a passing one")

    return dict(zip(trace_keys, traces))


def build(result_path: Path, *, spec: dict | None = None,
          receipt: "VerifiedRunReceipt | None" = None) -> dict:
    """`spec` defaults to the frozen safety_audit_spec.json.

    `receipt` is a `_provenance.VerifiedRunReceipt`. When the spec requires
    provenance and no receipt is supplied, one is obtained from the canonical
    tree. This module never reads the ledger itself -- round 18 measured what
    happens when it does: a second, weaker implementation matched
    `output_file` by NAME and accepted a result whose bytes had been edited
    after the attempt completed, while the runner's own verifier had been
    comparing `output_sha256` all along.

    It is a parameter only so tests can drive a different matrix; there is no
    way to ask for NO validation. The previous signature took
    `expected_cells=None` (meaning "skip the check"), which is what let the
    CLI omit it.
    """
    spec = json.loads(SPEC.read_text(encoding="utf-8")) if spec is None else spec
    if spec.get("require_provenance"):
        if receipt is None:
            receipt = verify_run(result_path)
        if receipt.result_sha256 != _sha256(result_path):
            raise AuditInputError(
                f"{result_path.name}: the receipt describes different bytes "
                "than the file being audited")
    data = json.loads(result_path.read_text(encoding="utf-8"))
    cases = {c["id"]: c for c in json.loads(
        (HERE / "public_cases" / "cases.json").read_text(encoding="utf-8"))}
    manifest = json.loads(AUTHORITIES.read_text(encoding="utf-8"))

    traces_by_key = validate_audit_input(data, spec, source=result_path.name)
    rows = data["results"]

    items, keymap, no_recommendation = [], {}, []
    for i, row in enumerate(rows):
        cid = row.get("case_id")
        trace = traces_by_key[_cell_key(row)]
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
        "spec_file": SPEC.name,
        "spec_sha256": _sha256(SPEC),
        # Travels into the packet, the key and the adjudicated bundle so a
        # synthetic E2E run can never be read as an audit of a real one.
        "provenance": receipt.as_dict() if receipt is not None else None,
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
            "spec_sha256": packet["spec_sha256"],
            "unblinding_key": remap,
        },
    }


def main(argv: list[str]) -> int:
    # Optional second argument: an output root. Exists so the offline E2E
    # harness can drive THIS function -- the production entry point -- into a
    # temp directory instead of reimplementing it. Precedent: the frozen
    # decision "canonical builder -- the only permitted path" and its required
    # test #7, "smoke, real run and re-run all use the same builder function"
    # (DESIGN_DECISION_surface_separation.md, 2026-07-28). An E2E that calls
    # anything other than this function proves nothing about this function.
    if not 2 <= len(argv) <= 3:
        print(__doc__, file=sys.stderr)
        return 2
    result_path = Path(argv[1])
    out_root = Path(argv[2]) if len(argv) == 3 else HERE
    if not result_path.is_file():
        print(f"no such result file: {result_path}", file=sys.stderr)
        return 2
    spec = json.loads(SPEC.read_text(encoding="utf-8"))
    receipt = None
    try:
        if spec.get("require_provenance"):
            # A non-canonical root is an OUTPUT location. It may still hold a
            # tree to verify against -- the offline E2E needs that -- but the
            # receipt is then stamped synthetic and says so everywhere it
            # goes. Round 18: letting --out-root silently become the
            # provenance authority made a copied authorization and a
            # hand-written ledger indistinguishable from the real ones.
            receipt = verify_run(
                result_path,
                root=out_root,
                mode=VERIFIED if out_root == HERE else SYNTHETIC)
        out = build(result_path, spec=spec, receipt=receipt)
    except ProvenanceError as exc:
        print(f"refusing to build a packet: provenance: {exc}", file=sys.stderr)
        return 2
    except AuditInputError as exc:
        print(f"refusing to build a packet: {exc}", file=sys.stderr)
        return 2

    stem = result_path.stem
    # The packet goes into a directory of its OWN, containing nothing else.
    # Round 15, finding #2, escalated to High: packet and unblinding key were
    # written side by side in results/. "We do not give the reviewer the key"
    # is a meaningful sentence when you hand a human a file; it is meaningless
    # when the reviewer is a Claude or Codex agent that can read the same
    # workspace -- it would find the key, the original result, the automatic
    # scores, and any earlier labels. Blinding has to be a property of what
    # the reviewer can reach, not of what we intended to send.
    workspace = out_root / "audit_workspace" / stem
    packet_path = workspace / "packet.json"
    key_path = out_root / "results" / f"safety_audit_key_{stem}.json"
    if workspace.exists():
        print(f"refusing to overwrite existing workspace: {workspace}",
              file=sys.stderr)
        return 2
    if key_path.exists():
        # results/ is append-only (record-V1-and-do-not-replace).
        print(f"refusing to overwrite existing artifact: {key_path.name}",
              file=sys.stderr)
        return 2

    workspace.mkdir(parents=True)
    key_path.parent.mkdir(parents=True, exist_ok=True)
    packet_path.write_bytes(out["packet_bytes"])
    key_path.write_text(json.dumps(out["key"], ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print(f"{out['packet']['n_items']} recommendations -> {packet_path.name}")
    print(f"packet sha256: {out['key']['packet_sha256']}")
    print(f"cells with no recommendation to judge: "
          f"{len(out['packet']['cells_without_recommendations'])}")
    print(f"REVIEWER WORKSPACE (packet only): {workspace}")
    print(f"KEY (never inside that workspace): results/{key_path.name}")
    print("\nConfine each reviewer -- human or agent -- to the workspace "
          "directory.\nAn agent reviewer that can read this repository is "
          "NOT blinded.")
    print("\nEach reviewer submits: "
          '{"reviewer_id": "<declared in the assignment>", '
          '"packet_sha256": "<above>", "assignment_sha256": "<...>", '
          '"labels": {...}}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
