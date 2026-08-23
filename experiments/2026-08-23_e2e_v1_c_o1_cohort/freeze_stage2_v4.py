#!/usr/bin/env python3
"""Stage 2 재동결 V4 — D-E2E-v1-25 + D-E2E-v1-26 amendment.

계보: V1(f57ae12) → V2(D-24 amendment) → V3(**ABORTED_PRE_FREEZE** —
satisfiability gate가 multi 풀 2/17을 적발, artifact 미생성) → **V4**.
V1·V2는 바이트 불변 보존(감사 표면, 게이트가 감시). 코호트 결과는 여전히
0건 관측 — pre-execution amendment 전제 유지.

V4에서 바뀌는 것 (전부 판정 명령):
- 방언 6종(D-26 Q26.1: + implies — measurement-language repair, estimand
  불변), template V4(1행 추가), schema·profile hash 갱신
- 채점 = O1ScopeMatch: O1_SCOPE_PROJECTION_V1 signature 사이 exact match
  (D-25 Q25.1); 라벨 정체성은 진단 전용(D-25 Q25.2)
- 적격성 = MEASUREMENT_SATISFIABILITY_V2 (D-25 Q25.4, D-26 §14) — 라벨
  도달성은 적격 조건에서 제외·진단 필드로(D-26 Q26.3, 운영 권고 기각 수용)
- FOLIO 두 stratum: 전체 적격 풀에서 동결 selector 재실행(D-26 §16 —
  기존 5건 재사용 금지). `example_id` 부재 record는 식별자 없는 commitment
  불성립(D-20 완전성)으로 선별 전 기계 제외
- PMB in-N 15: 선별·commitment 3필드 불변(V2와 동일 규율), profile hash만 V4
- **PMB live projection control 3건 신설**(D-25 §29, N 밖): in-N 15 제외
  풀에서 SAT-V2 통과분을 order_key 상위 3 — F3형 사각(발명 FOL 재료만
  live로 돌던 것)을 직접 막는다
- contract_hashes 6종을 manifest에 pin(D-26 §18; manifest 자신과 prereg의
  해시는 순환이라 prereg가 manifest hash를 기록하는 쪽으로 분담)
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

from conceptgate import cg_ir, cg_sbn_adapter as sbn, cg_fol_adapter as fol  # noqa: E402
from conceptgate.cg_identity import canonical_sha256  # noqa: E402
from conceptgate.cg_ir_schema import dispatch_envelope_schema  # noqa: E402

from freeze_stage2 import (  # noqa: E402 — V1이 정본, 재타이핑 금지
    SEED, STRATA_COUNTS, FOLIO_MULTI_N, FOLIO_CONTROL_N,
    order_key, put_cache, SC, GOLD,
)
from _stage2_scope_projection import (  # noqa: E402
    PROJECTION_PROFILE_ID, DIALECT_V4_CONSTRUCTORS,
)
import _stage2_satisfiability as sat  # noqa: E402
import scan_folio_eligibility_v2 as reach  # noqa: E402

PMB_CONTROL_N = 3   # D-25 §29: "PMB live projection controls: 2~3" — 상한 채택

V2_DESCRIPTOR_PATH = HERE / "stage2_fixture_manifest_v2.json"

PROFILE_DESCRIPTOR_V4 = None  # refreeze()에서 V2 기반으로 유도 (단일 출처)


def _profile_v4(v2_profile: dict) -> dict:
    d = deepcopy(v2_profile)
    d["id"] = "O1_V4"
    d["constructors"] = list(DIALECT_V4_CONSTRUCTORS)
    d["comparison_core"]["scope_projection"] = PROJECTION_PROFILE_ID
    d["comparison_core"]["primary_metric"] = "O1ScopeMatch (D-25 §8)"
    d["comparison_core"]["predicate_labels"] = {
        "status": "diagnostic_only (D-25 Q25.2, D-26 Q26.3)",
        "PMB": "O1_PMB_LEMMA_NO_SENSE_V1",
        "FOLIO": "FOLIO_LABEL_LOWERCASE_V1",
    }
    d["eligibility_gate"] = sat.GATE_ID
    return d


def _code_sha(rel: str) -> str:
    return hashlib.sha256((HERE / rel).read_bytes()).hexdigest()


def refreeze() -> tuple[dict, dict]:
    v2 = json.loads(V2_DESCRIPTOR_PATH.read_text())
    profile_v4 = _profile_v4(v2["profile"])
    profile_hash_v4 = canonical_sha256(profile_v4)
    folio_scan = json.loads((HERE / "folio_eligibility_scan.json").read_text())
    pmb_scan = json.loads((HERE / "pmb_eligibility_scan_pathB.json").read_text())
    fol_code = hashlib.sha256(
        (REPO / "conceptgate" / "cg_fol_adapter.py").read_bytes()).hexdigest()
    sbn_code = hashlib.sha256(
        (REPO / "conceptgate" / "cg_sbn_adapter.py").read_bytes()).hexdigest()

    # ---- corpus 색인 ----
    folio_recs = {}
    for fn in ("folio-train.jsonl", "folio-validation.jsonl"):
        for line in (SC / fn).read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            folio_recs[(fn, rec.get("example_id"))] = rec

    def premise_of(x):
        rec = folio_recs[(x["file"], x["example_id"])]
        i = x["premise_index"]
        prems = rec.get("premises") or []
        fols = rec.get("premises-FOL") or []
        text = prems[i] if i < len(prems) else ""
        f = (fols[i] if i < len(fols) else "").strip()
        return rec, i, text, f

    # ---- FOLIO 적격성: SAT-V2 + 식별자 완전성 (도달성은 진단으로만 기록) ----
    sat_records = []

    def folio_eligible(pool):
        kept = []
        for x in pool:
            if x.get("example_id") is None:
                sat_records.append({"case": f"{x['file']}#p{x['premise_index']}",
                                    "verdict": "EXCLUDED_NO_IDENTIFIER"})
                continue
            _, i, text, f = premise_of(x)
            if not text.strip() or not f:
                sat_records.append({"case": f"{x['example_id']}p{i}",
                                    "verdict": "EXCLUDED_MISSING_TEXT_OR_FOL"})
                continue
            cid = f"FOLIO-{x['example_id']}p{i}"
            try:
                ir = fol.adapt_fol(f)
            except Exception as exc:
                sat_records.append({"case": cid, "verdict": "ADAPTER_REFUSED",
                                    "detail": type(exc).__name__})
                continue
            rec = sat.check_oracle_ir(cid, ir)
            # D-26 §13: 도달성은 진단 필드
            r = reach.fixture_reachability(f, text)
            rec["diagnostic"]["predicate_label_reachability"] = {
                "reachable": r["reachable"], "paths_agree": r["paths_agree"],
                "unreachable_count": len(r["unreachable_labels"])}
            sat_records.append(rec)
            if rec["verdict"] == "SATISFIABLE":
                kept.append(x)
        return kept

    multi_ok = folio_eligible(folio_scan["multi_mixed"])
    ctrl_ok = folio_eligible(folio_scan["single_controls"])
    if len(multi_ok) < FOLIO_MULTI_N or len(ctrl_ok) < FOLIO_CONTROL_N:
        raise SystemExit(f"BLOCKED: multi {len(multi_ok)}/{FOLIO_MULTI_N}, "
                         f"control {len(ctrl_ok)}/{FOLIO_CONTROL_N}")

    def folio_entry(x, stratum):
        rec, i, text, f = premise_of(x)
        ir = fol.adapt_fol(f)
        assert not cg_ir.validate_formula(ir) and not cg_ir.free_variables(ir)
        subset = {"wiki": "WikiLogic", "hyb": "HybLogic"}.get(rec.get("source"), "?")
        return {
            "case_id": f"FOLIO-{x['example_id']}p{i}",
            "stratum": stratum,
            "source_locator": {
                "corpus_id": "folio", "corpus_version": "v0.0",
                "artifact": f"data/v0.0/{x['file']}",
                "record_locator": f"example_id={x['example_id']};premise={i}",
                "retrieval_urls": ["https://github.com/Yale-LILY/FOLIO"]},
            "folio_subset": subset,
            "text_sha256": put_cache(text.encode()),
            "lf_sha256": put_cache(f.encode()),
            "adapter_version": "cg_fol_adapter/FOLIO_FOL_V0",
            "adapter_code_sha256": fol_code,
            "canonicalization_profile_hash": profile_hash_v4,
            "expected_ir_sha256": canonical_sha256(ir)}

    key = lambda x: order_key(f"{x['example_id']}#{x['premise_index']}")
    folio_entries = [folio_entry(x, "multi_quantifier")
                     for x in sorted(multi_ok, key=key)[:FOLIO_MULTI_N]]
    folio_controls = [folio_entry(x, "adapter_control")
                      for x in sorted(ctrl_ok, key=key)[:FOLIO_CONTROL_N]]

    # ---- PMB in-N 15: V2에서 기계 복사, profile hash만 갱신 ----
    pmb_entries = []
    in_n_docs = set()
    for e in v2["entries"]:
        if not e["case_id"].startswith("PMB-"):
            continue
        e2 = deepcopy(e)
        e2["canonicalization_profile_hash"] = profile_hash_v4
        for fld in ("case_id", "stratum", "source_locator", "subcorpus",
                    "text_sha256", "lf_sha256", "adapter_version",
                    "adapter_code_sha256", "expected_ir_sha256"):
            assert e2.get(fld) == e.get(fld), fld
        pmb_entries.append(e2)
        in_n_docs.add(e["source_locator"]["record_locator"])
    assert len(pmb_entries) == 15

    # ---- PMB live projection controls 3 (D-25 §29, N 밖) ----
    pmb_ctrl_pool = []
    for c in pmb_scan["candidates"]:
        doc = c["doc"]
        if doc in in_n_docs:
            continue
        sbn_path = GOLD / doc / "en.drs.sbn"
        raw_path = GOLD / doc / "en.raw"
        if not sbn_path.exists() or not raw_path.exists():
            continue
        sbn_text = sbn_path.read_text(errors="replace")
        if any("ANA" in l.split("%", 1)[0].split()
               for l in sbn_text.splitlines() if not l.startswith("%%%")):
            continue
        try:
            ir = sbn.adapt_sbn(sbn_text)
        except Exception:
            continue
        if cg_ir.validate_formula(ir) or cg_ir.free_variables(ir):
            continue
        cid = f"PMB-{doc.replace('/', '-')}"
        if sat.check_oracle_ir(cid, ir)["verdict"] != "SATISFIABLE":
            continue
        pmb_ctrl_pool.append(doc)
    if len(pmb_ctrl_pool) < PMB_CONTROL_N:
        raise SystemExit(f"BLOCKED: PMB control pool {len(pmb_ctrl_pool)} < {PMB_CONTROL_N}")

    pmb_controls = []
    for doc in sorted(pmb_ctrl_pool, key=order_key)[:PMB_CONTROL_N]:
        raw = (GOLD / doc / "en.raw").read_text(errors="replace")
        text = " ".join(raw.split())
        sbn_bytes = (GOLD / doc / "en.drs.sbn").read_bytes()
        ir = sbn.adapt_sbn(sbn_bytes.decode("utf-8", "replace"))
        pmb_controls.append({
            "case_id": f"PMB-{doc.replace('/', '-')}",
            "stratum": "pmb_projection_control",
            "source_locator": {
                "corpus_id": "pmb-5.1.0", "corpus_version": "5.1.0",
                "artifact": f"data/en/gold/{doc}/en.drs.sbn",
                "record_locator": doc,
                "retrieval_urls": ["https://pmb.let.rug.nl/releases/pmb-5.1.0.zip"]},
            "text_sha256": put_cache(text.encode()),
            "lf_sha256": put_cache(sbn_bytes),
            "adapter_version": "cg_sbn_adapter/PMB_SBN_5_1",
            "adapter_code_sha256": sbn_code,
            "canonicalization_profile_hash": profile_hash_v4,
            "expected_ir_sha256": canonical_sha256(ir)})

    sat_scan = {"gate": sat.GATE_ID,
                "gate_module_sha256": _code_sha("_stage2_satisfiability.py"),
                "projection_module_sha256": _code_sha("_stage2_scope_projection.py"),
                "records": sat_records,
                "counts": {"multi_eligible": len(multi_ok),
                           "folio_control_eligible": len(ctrl_ok),
                           "pmb_control_pool": len(pmb_ctrl_pool)}}

    manifest = {
        "manifest_version": "e2e-v1-c-fixtures-v4",
        "amendment": {
            "rulings": ["D-E2E-v1-25", "D-E2E-v1-26"],
            "supersedes": "stage2_fixture_manifest_v2.json (V2)",
            "v2_status": "SUPERSEDED_PRE_EXECUTION",
            "v3_status": "ABORTED_PRE_FREEZE (artifact 미생성 — satisfiability "
                         "gate가 multi 2/17을 적발, Q26으로 상신)",
            "defect": "F-dialect — subject language could not express "
                      "FOLIO exists-scoped implication (no cohort outcomes observed)",
        },
        "order_seed": SEED,
        "profile": profile_v4,
        "profile_hash": profile_hash_v4,
        "contract_hashes": {
            "prompt_template_v4_sha256": hashlib.sha256(
                (HERE / "stage2_prompt_template_v4.md").read_bytes()).hexdigest(),
            "dispatch_schema_sha256": canonical_sha256(
                dispatch_envelope_schema(tuple(DIALECT_V4_CONSTRUCTORS))),
            "canonicalization_core_sha256": _code_sha("_stage2_canonical_core.py"),
            "projection_module_sha256": _code_sha("_stage2_scope_projection.py"),
            "satisfiability_module_sha256": _code_sha("_stage2_satisfiability.py"),
            "eval_profile_module_sha256": _code_sha("_stage2_eval_profile.py"),
        },
        "selection_inputs": {
            **v2["selection_inputs"],
            "satisfiability_scan_v4_sha256": canonical_sha256(sat_scan)},
        "strata_counts": {**STRATA_COUNTS, "multi_quantifier": FOLIO_MULTI_N},
        "entries": pmb_entries + folio_entries,
        "folio_simple_controls": folio_controls,
        "pmb_projection_controls": pmb_controls,
    }
    assert len(manifest["entries"]) == 20
    return manifest, sat_scan


if __name__ == "__main__":
    m, ss = refreeze()
    out = HERE / "stage2_fixture_manifest_v4.json"
    sout = HERE / "stage2_sat_scan_v4.json"
    if out.exists() or sout.exists():
        raise SystemExit("V4 artifacts already exist — refusing overwrite")
    sout.write_text(json.dumps(ss, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    out.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    from collections import Counter
    print("refrozen V4:", len(m["entries"]), "fixtures +",
          len(m["folio_simple_controls"]), "FOLIO controls +",
          len(m["pmb_projection_controls"]), "PMB controls")
    print("strata:", dict(Counter(e["stratum"] for e in m["entries"])))
    print("profile_hash V4:", m["profile_hash"][:16])
    print("FOLIO in-N:", [e["case_id"] for e in m["entries"]
                          if e["case_id"].startswith("FOLIO-")])
    print("FOLIO controls:", [e["case_id"] for e in m["folio_simple_controls"]])
    print("PMB controls:", [e["case_id"] for e in m["pmb_projection_controls"]])
    print("SAT counts:", ss["counts"])
