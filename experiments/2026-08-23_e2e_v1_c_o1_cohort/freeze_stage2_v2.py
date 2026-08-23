#!/usr/bin/env python3
"""Stage 2 fixture 재동결 V2 — D-E2E-v1-24 pre-execution amendment.

V1(f57ae12, `stage2_fixture_manifest.json`)은 **불변 보존**된다
(SUPERSEDED_PRE_EXECUTION — 판정 §7-8: 감사 가능한 이전 상태, mutation 금지).
이 스크립트는 V1을 읽기만 하고 절대 쓰지 않는다.

무엇이 왜 바뀌는가 (전부 판정 D-E2E-v1-24가 명령):
  - 결함 B1: FOLIO oracle 술어가 대문자/CamelCase로 남아 subject(소문자 강제)
    가 구조 정합과 무관하게 fail — smoke test가 코호트 실행 전에 적발.
  - Q24.1(a): FOLIO 한정 소문자화 codec `FOLIO_LABEL_LOWERCASE_V1` →
    profile descriptor의 comparison_core.predicate_labels가 source별 map이
    되고 profile hash가 바뀐다.
  - Q24.2(a): 신규 적격성 불변식 `predicate_label_reachability`(동결 기계
    규칙 — `scan_folio_eligibility_v2.py`가 정본) 위반 fixture는 부적격.
    FOLIO **두 stratum 전체**를 동일 SEED로 재선별(§10 엄격안 — 수동 교체
    금지). 실측: multi 17 중 도달 가능 5 = 필요치와 정확히 일치(선별 자유도
    0), control 963 중 422.
  - PMB 15: 선별·text/lf/expected_ir commitment **불변** — V1에서 기계
    복사하고 `canonicalization_profile_hash` 필드만 V2 값으로 갱신한다
    (검증된 L2 설계: "verbatim 복사"는 profile hash 변경과 양립 불가라
    필드 단위로 정밀화. 불변성은 이 스크립트의 assert + V1↔V2 diff 게이트
    `test_stage2_freeze_v2.py`가 이중으로 보증).

선별이 V1과 같은 이유로 조작 불가능한 것: SEED·층 술어·N·임계값은 V1
모듈에서 **import**(재타이핑 금지)하고, 순서는 order_key(SEED 결박 해시),
적격성은 결정론 함수 — 관측된 결과에 조건화된 것이 없다(코호트 미실행,
판정 §6).
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

from conceptgate import cg_ir, cg_fol_adapter as fol  # noqa: E402
from conceptgate.cg_identity import canonical_sha256  # noqa: E402

from freeze_stage2 import (  # noqa: E402 — V1이 정본, 재타이핑 금지
    SEED, PROFILE_DESCRIPTOR, STRATA_COUNTS,
    FOLIO_MULTI_N, FOLIO_CONTROL_N, order_key, put_cache, SC,
)
import scan_folio_eligibility_v2 as reach  # noqa: E402

# ---- V2 profile descriptor: 판정 Q24.1이 명한 유일 변경 ----
PROFILE_DESCRIPTOR_V2 = deepcopy(PROFILE_DESCRIPTOR)
PROFILE_DESCRIPTOR_V2["comparison_core"]["predicate_labels"] = {
    "PMB": "O1_PMB_LEMMA_NO_SENSE_V1",
    "FOLIO": "FOLIO_LABEL_LOWERCASE_V1",
}
PROFILE_HASH_V2 = canonical_sha256(PROFILE_DESCRIPTOR_V2)

COMMITMENT_INVARIANT_FIELDS = ("case_id", "stratum", "source_locator",
                               "subcorpus", "text_sha256", "lf_sha256",
                               "adapter_version", "adapter_code_sha256",
                               "expected_ir_sha256")


def refreeze() -> tuple[dict, dict]:
    """V2 manifest와 도달성 스캔 기록을 반환한다. 쓰기는 __main__만 한다."""
    v1 = json.loads((HERE / "stage2_fixture_manifest.json").read_text())
    folio_scan = json.loads((HERE / "folio_eligibility_scan.json").read_text())
    fol_code = hashlib.sha256(
        (REPO / "conceptgate" / "cg_fol_adapter.py").read_bytes()).hexdigest()

    # ---- corpus 색인 (로컬 캐시 — sha는 V1 취득 기록과 대조) ----
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
        # corpus 불규칙: premises가 premises-FOL보다 짧은 record 실재 —
        # 문장 없는 premise는 도달성 판정이 불가능하므로 부적격으로 흘린다
        text = prems[i] if i < len(prems) else ""
        f = (fols[i] if i < len(fols) else "").strip()
        return rec, i, text, f

    # ---- 도달성 필터 (신규 적격성 불변식) ----
    def reachable_pool(pool):
        kept, dropped = [], []
        for x in pool:
            _, _, text, f = premise_of(x)
            if not text.strip() or not f:
                dropped.append({**x, "unreachable_labels": [],
                                "paths_agree": False, "reason": "missing_text_or_fol"})
                continue
            r = reach.fixture_reachability(f, text)
            (kept if r["reachable"] else dropped).append(
                {**x, **({} if r["reachable"] else
                          {"unreachable_labels": r["unreachable_labels"],
                           "paths_agree": r["paths_agree"]})})
        return kept, dropped

    multi_ok, multi_bad = reachable_pool(folio_scan["multi_mixed"])
    ctrl_ok, ctrl_bad = reachable_pool(folio_scan["single_controls"])
    if len(multi_ok) < FOLIO_MULTI_N or len(ctrl_ok) < FOLIO_CONTROL_N:
        raise SystemExit(
            f"BLOCKED: eligible pool insufficient (multi {len(multi_ok)}/"
            f"{FOLIO_MULTI_N}, control {len(ctrl_ok)}/{FOLIO_CONTROL_N}) — "
            "D-24 Q24.2: re-adjudication required")

    reach_record = {
        "rule_module": "scan_folio_eligibility_v2.py",
        "rule_module_sha256": hashlib.sha256(
            (HERE / "scan_folio_eligibility_v2.py").read_bytes()).hexdigest(),
        "multi_mixed": {"total": len(folio_scan["multi_mixed"]),
                        "reachable": len(multi_ok)},
        "single_controls": {"total": len(folio_scan["single_controls"]),
                            "reachable": len(ctrl_ok)},
        "reachable_multi": multi_ok,
        "reachable_controls_sha_only": [
            {k: x[k] for k in ("file", "example_id", "premise_index",
                               "text_sha256", "fol_sha256")} for x in ctrl_ok],
    }

    # ---- FOLIO 재선별 (V1과 동일한 순서 규칙, 필터만 신설) ----
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
            "canonicalization_profile_hash": PROFILE_HASH_V2,
            "expected_ir_sha256": canonical_sha256(ir)}

    multi_sorted = sorted(multi_ok, key=lambda x: order_key(
        f"{x['example_id']}#{x['premise_index']}"))
    ctrl_sorted = sorted(ctrl_ok, key=lambda x: order_key(
        f"{x['example_id']}#{x['premise_index']}"))
    folio_entries = [folio_entry(x, "multi_quantifier")
                     for x in multi_sorted[:FOLIO_MULTI_N]]
    control_entries = [folio_entry(x, "adapter_control")
                       for x in ctrl_sorted[:FOLIO_CONTROL_N]]

    # ---- PMB 15: V1에서 기계 복사, profile hash 필드만 갱신 ----
    pmb_entries = []
    for e in v1["entries"]:
        if not e["case_id"].startswith("PMB-"):
            continue
        e2 = deepcopy(e)
        e2["canonicalization_profile_hash"] = PROFILE_HASH_V2
        for fld in COMMITMENT_INVARIANT_FIELDS:
            assert e2.get(fld) == e.get(fld), fld
        pmb_entries.append(e2)
    assert len(pmb_entries) == 15, len(pmb_entries)

    manifest = {
        "manifest_version": "e2e-v1-c-fixtures-v2",
        "amendment": {
            "ruling": "D-E2E-v1-24",
            "supersedes": "stage2_fixture_manifest.json (V1, freeze commit f57ae12)",
            "v1_status": "SUPERSEDED_PRE_EXECUTION",
            "defect": "B1 — FOLIO predicate label convention gap "
                      "(smoke test, pre-execution; no cohort outcomes observed)",
        },
        "order_seed": SEED,
        "profile": PROFILE_DESCRIPTOR_V2,
        "profile_hash": PROFILE_HASH_V2,
        "selection_inputs": {
            **v1["selection_inputs"],
            "folio_reachability_scan_v2_sha256": canonical_sha256(reach_record)},
        "strata_counts": {**STRATA_COUNTS, "multi_quantifier": FOLIO_MULTI_N},
        "entries": pmb_entries + folio_entries,
        "folio_simple_controls": control_entries,
    }
    assert len(manifest["entries"]) == 20, len(manifest["entries"])
    return manifest, reach_record


if __name__ == "__main__":
    m, rr = refreeze()
    out = HERE / "stage2_fixture_manifest_v2.json"
    rout = HERE / "folio_reachability_scan_v2.json"
    if out.exists() or rout.exists():
        raise SystemExit("V2 artifacts already exist — refreeze is irreversible; "
                         "refusing overwrite")
    rout.write_text(json.dumps(rr, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    out.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    from collections import Counter
    print("refrozen:", len(m["entries"]), "fixtures +",
          len(m["folio_simple_controls"]), "controls")
    print("strata:", dict(Counter(e["stratum"] for e in m["entries"])))
    print("profile_hash V2:", m["profile_hash"][:16])
    print("FOLIO in-N:", [e["case_id"] for e in m["entries"]
                          if e["case_id"].startswith("FOLIO-")])
    print("controls:", [e["case_id"] for e in m["folio_simple_controls"]])
