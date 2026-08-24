#!/usr/bin/env python3
"""Stage 2 재동결 V5 — 투영 전용 개정 (D-E2E-v1-32 + D-E2E-v1-32-C).

V5는 V4의 fixture 선별·commitment·방언·template을 **전혀 바꾸지 않는다.**
바뀌는 것은 측정 계약(투영 profile V1→V2)과 그로부터 재생성되는 서명
commitment뿐이다 — B.8 §1 "델타는 #1·#5뿐, 나머지는 현행 유지"의 기계화.

이 스크립트가 하는 일:
  1. V4의 20 entries + control 6의 commitment 필드를 **deepcopy 후 바이트
     동일 assert**로 복사한다(V4가 V2에서 PMB 15를 복사한 규율과 동일).
  2. profile을 V4에서 정확히 두 필드(id, comparison_core.scope_projection)
     만 바꿔 유도한다 — 투영 전용 개정이라는 주장의 기계 검증.
  3. `.oracle_cache`에서 실물을 재해석해 expected_ir_sha256을 재확인하고
     (IR 유도는 안 바뀜), `_stage2_projection_pipeline_v2`로 V2 서명
     commitment를 신규 계산한다(26건 전부).
  4. in-N 20건에 대해 V1 서명과 V2 서명이 실제로 달라지는 건수를 세어
     `reprojection_impact`에 싣는다 — 하드코딩하지 않는다.
"""
from __future__ import annotations

import hashlib
import json
import sys
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from conceptgate import cg_sbn_adapter as sbn, cg_fol_adapter as fol  # noqa: E402
from conceptgate.cg_identity import canonical_sha256  # noqa: E402
from conceptgate.cg_fixture_resolver import resolve_bytes  # noqa: E402

import _stage2_projection_pipeline_v2 as pipe  # noqa: E402
from _stage2_scope_projection import project_scope_for_case  # noqa: E402

V4_PATH = HERE / "stage2_fixture_manifest_v4.json"

INVARIANT_FIELDS = ("case_id", "stratum", "source_locator", "subcorpus",
                    "text_sha256", "lf_sha256", "adapter_version",
                    "adapter_code_sha256", "expected_ir_sha256")
CONTROL_INVARIANT_FIELDS = tuple(f for f in INVARIANT_FIELDS if f != "subcorpus")


def _code_sha(rel: str) -> str:
    return hashlib.sha256((HERE / rel).read_bytes()).hexdigest()


def _adapt(case_id: str, data: bytes) -> dict:
    if case_id.startswith("PMB-"):
        return sbn.adapt_sbn(data.decode("utf-8", "replace"))
    return fol.adapt_fol(data.decode("utf-8"))


def _copy_commitments(v4_block: list[dict], fields: tuple[str, ...]) -> list[dict]:
    """V4 entry를 deepcopy하고 commitment 필드가 바이트 동일한지 확인한다."""
    out = []
    for e in v4_block:
        e2 = deepcopy(e)
        for f in fields:
            assert e2.get(f) == e.get(f), (e["case_id"], f)
        out.append(e2)
    return out


def _profile_v5(v4_profile: dict) -> dict:
    d = deepcopy(v4_profile)
    d["id"] = "O1_V5"
    d["comparison_core"]["scope_projection"] = pipe.PROJECTION_PROFILE_ID
    return d


def _add_signature_commitment(entry: dict, cache: Path) -> None:
    """캐시 실물에서 재해석해 expected_ir_sha256을 대조하고 V2 서명을 얹는다."""
    cid = entry["case_id"]
    got = resolve_bytes(entry["lf_sha256"], cache)
    if got["execution"] != "ok":
        raise SystemExit(f"BLOCKED: cache unavailable for {cid}: {got.get('reason')}")
    ir = _adapt(cid, got["data"])
    assert canonical_sha256(ir) == entry["expected_ir_sha256"], cid
    sig = pipe.scope_signature_v2_for_case(cid, ir)
    entry["expected_scope_signature_v2_sha256"] = canonical_sha256(
        pipe.signature_jsonable(sig))
    return ir


def refreeze() -> dict:
    v4 = json.loads(V4_PATH.read_text(encoding="utf-8"))
    cache = REPO / ".oracle_cache"

    profile_hash_v5 = None
    profile_v5 = _profile_v5(v4["profile"])
    profile_hash_v5 = canonical_sha256(profile_v5)

    entries = _copy_commitments(v4["entries"], INVARIANT_FIELDS)
    folio_controls = _copy_commitments(v4["folio_simple_controls"],
                                       CONTROL_INVARIANT_FIELDS)
    pmb_controls = _copy_commitments(v4["pmb_projection_controls"],
                                     CONTROL_INVARIANT_FIELDS)
    assert len(entries) == 20
    assert len(folio_controls) == 3
    assert len(pmb_controls) == 3

    for e in entries:
        e["canonicalization_profile_hash"] = profile_hash_v5

    # ---- 재투영: 26건 전부, expected_scope_signature_v2_sha256 신설 ----
    v1_sig_hashes = {}
    for e in entries:
        ir = _add_signature_commitment(e, cache)
        v1_sig = project_scope_for_case(e["case_id"], ir)
        v1_sig_hashes[e["case_id"]] = canonical_sha256(v1_sig)
    for e in folio_controls + pmb_controls:
        _add_signature_commitment(e, cache)

    # ---- reprojection_impact 실측 (in-N 20, 하드코딩 금지) ----
    changed = 0
    for e in entries:
        v2_hash = e["expected_scope_signature_v2_sha256"]
        if v1_sig_hashes[e["case_id"]] != v2_hash:
            changed += 1
    reprojection_impact = {"in_n_signature_changed_vs_v1": changed, "in_n_total": 20}

    manifest = {
        "manifest_version": "e2e-v1-c-fixtures-v5",
        "amendment": {
            "procedure": "PRE_EXECUTION_FREEZE_AMENDMENT_V1",
            "rulings": ["D-E2E-v1-32", "D-E2E-v1-32-C"],
            "supersedes": "stage2_fixture_manifest_v4.json (V4)",
            "v4_status": "SUPERSEDED_PRE_EXECUTION",
            "cohort_dispatch_count_at_amendment": 0,
            "reprojection_impact": reprojection_impact,
            "defect": "투영 전용 개정 — 제한식 내용이 V1에서 미채점이던 것을 "
                      "opaque incidence로 채점(D-32); fixture 선별·방언· "
                      "template 불변",
        },
        "order_seed": v4["order_seed"],
        "profile": profile_v5,
        "profile_hash": profile_hash_v5,
        "contract_hashes": {
            "prompt_template_v4_sha256": v4["contract_hashes"]["prompt_template_v4_sha256"],
            "dispatch_schema_sha256": v4["contract_hashes"]["dispatch_schema_sha256"],
            "canonicalization_core_sha256": _code_sha("_stage2_canonical_core.py"),
            "projection_module_sha256": _code_sha("_stage2_scope_projection.py"),
            "projection_module_v2_sha256": _code_sha("_stage2_scope_projection_v2.py"),
            "projection_pipeline_module_sha256": _code_sha("_stage2_projection_pipeline_v2.py"),
            "satisfiability_module_sha256": _code_sha("_stage2_satisfiability.py"),
            "eval_profile_module_sha256": _code_sha("_stage2_eval_profile.py"),
        },
        "selection_inputs": v4["selection_inputs"],
        "strata_counts": v4["strata_counts"],
        "measurement_contract": {
            "projection_profile": pipe.PROJECTION_PROFILE_ID,
            "projection_profile_hash": profile_hash_v5,
            "projection_module_sha256": _code_sha("_stage2_scope_projection_v2.py"),
            "pre_projection_module_sha256": _code_sha("_stage2_scope_projection.py"),
            "pipeline_module_sha256": _code_sha("_stage2_projection_pipeline_v2.py"),
        },
        "supersedes": ["O1_SCOPE_PROJECTION_V1"],
        "score_comparability": {
            "V1_to_V2": {
                "direct_numeric_comparison": False,
                "reason": "non_scope_restriction_and_body_content_projection_changed",
            }
        },
        "measurement_semantics": {
            "V1-V4": "O1_SCOPE_PROJECTION_V1",
            "V5_onward": "O1_SCOPE_PROJECTION_V2",
        },
        "entries": entries,
        "folio_simple_controls": folio_controls,
        "pmb_projection_controls": pmb_controls,
    }
    return manifest


if __name__ == "__main__":
    m = refreeze()
    out = HERE / "stage2_fixture_manifest_v5.json"
    if out.exists():
        raise SystemExit("V5 artifact already exists — refusing overwrite")
    out.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    imp = m["amendment"]["reprojection_impact"]
    print("refrozen V5:", len(m["entries"]), "fixtures +",
          len(m["folio_simple_controls"]), "FOLIO controls +",
          len(m["pmb_projection_controls"]), "PMB controls")
    print("reprojection_impact:", imp)
    print("profile_hash V5:", m["profile_hash"][:16])
