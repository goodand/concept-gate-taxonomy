#!/usr/bin/env python3
"""Stage 2 control 재선별 V5.1 — D-E2E-v1-27 §18이 승인한 경로.

V5 control 실행이 2/6(FOLIO adapter 2/3)으로 해석 가능 조건을 미충족했다
(`CONTROLS_RUN_V5_20260824.md`). D-27 §18의 처분: old controls는 역사
기록으로 V5 manifest에 바이트 그대로 남기고(`stage2_fixture_manifest_v5.json`
의 `folio_simple_controls`/`pmb_projection_controls`), 새 2층 적격 술어
(`_stage2_surface_filters.control_eligible`, `O1_CONTROL_ELIGIBILITY_V1`)로
결정론 재선별한다.

층 구성 = D-27 §16(source별 단순 보편 1~2 + 단순 존재 1, 상한 채택 — V4가
상한을 채택한 선례) ∧ D-25 §29(PMB 총 2~3): FOLIO universal 2 + existential 1,
PMB universal 1 + existential 1.

풀:
  - FOLIO: `folio_eligibility_scan.json`의 `single_controls`
    (example_id None 제외, V5 manifest in-N FOLIO case_id와 서로소)
  - PMB: `pmb_eligibility_scan_pathB.json`의 `candidates`
    (V5 manifest in-N record_locator 제외, ANA 라인 있는 SBN 제외,
    adapt/validate/free_variables 실패 제외)

적격 = `control_eligible(case_id, sentence, oracle_ir)` (유일한 진입점).
층 분류 = `project_scope_for_case`의 signature 안 양화 kind가 정확히 1개일
때 그 kind(forall→universal, exists→existential; 그 외는 풀에서 제외) —
control_eligible이 이미 "정확히 1개"를 강제하므로 이 분류는 그 결과를
읽을 뿐이다.

순서: `freeze_stage2.order_key` — FOLIO는
`order_key(f"{example_id}#{premise_index}")`, PMB는 `order_key(doc)`.
각 층에서 정렬 상위 N건을 취한다. 풀 부족 시 `SystemExit`.

이 스크립트는 새 재료를 `.oracle_cache`에 채운다(`put_cache`) — V5 이후
control 문장/LF가 처음 캐시에 들어가는 지점이다.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(HERE))

from conceptgate import cg_ir, cg_sbn_adapter as sbn, cg_fol_adapter as fol  # noqa: E402
from conceptgate.cg_identity import canonical_sha256  # noqa: E402

from freeze_stage2 import order_key, put_cache, SC, GOLD  # noqa: E402 — V1이 정본
from _stage2_surface_filters import control_eligible  # noqa: E402
from _stage2_scope_projection import project_scope_for_case  # noqa: E402
import _stage2_projection_pipeline_v2 as pipe  # noqa: E402

V5_PATH = HERE / "stage2_fixture_manifest_v5.json"

STRATA_N = {
    "folio_universal_control": 2,
    "folio_existential_control": 1,
    "pmb_universal_control": 1,
    "pmb_existential_control": 1,
}


def _quant_kind(case_id: str, ir: dict) -> str | None:
    """signature 안 양화 kind가 정확히 1개일 때 그 kind, 아니면 None."""
    sig = project_scope_for_case(case_id, ir)
    kinds = []

    def walk(n):
        if isinstance(n, dict):
            if n.get("kind") in ("forall", "exists"):
                kinds.append(n["kind"])
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    walk(sig)
    return kinds[0] if len(kinds) == 1 else None


def _code_sha(rel: str) -> str:
    return hashlib.sha256((REPO / "conceptgate" / rel).read_bytes()).hexdigest()


def _commit(case_id: str, ir: dict, profile_hash: str) -> dict:
    return {
        "expected_ir_sha256": canonical_sha256(ir),
        "canonicalization_profile_hash": profile_hash,
        "expected_scope_signature_v2_sha256": canonical_sha256(
            pipe.signature_jsonable(pipe.scope_signature_v2_for_case(case_id, ir))),
    }


def _folio_pools(in_n_folio_ids: set) -> tuple[list, list]:
    folio_scan = json.loads((HERE / "folio_eligibility_scan.json").read_text())
    folio_recs = {}
    for fn in ("folio-train.jsonl", "folio-validation.jsonl"):
        for line in (SC / fn).read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            folio_recs[(fn, rec.get("example_id"))] = rec

    forall_pool, exists_pool = [], []
    for x in folio_scan["single_controls"]:
        if x.get("example_id") is None:
            continue
        cid = f"FOLIO-{x['example_id']}p{x['premise_index']}"
        if cid in in_n_folio_ids:
            continue
        rec = folio_recs.get((x["file"], x["example_id"]))
        if rec is None:
            continue
        i = x["premise_index"]
        prems = rec.get("premises") or []
        fols = rec.get("premises-FOL") or []
        text = prems[i] if i < len(prems) else ""
        f = (fols[i] if i < len(fols) else "").strip()
        if not text.strip() or not f:
            continue
        try:
            ir = fol.adapt_fol(f)
        except Exception:
            continue
        if cg_ir.validate_formula(ir) or cg_ir.free_variables(ir):
            continue
        ok, _why = control_eligible(cid, text, ir)
        if not ok:
            continue
        kind = _quant_kind(cid, ir)
        if kind == "forall":
            forall_pool.append(x)
        elif kind == "exists":
            exists_pool.append(x)
    return forall_pool, exists_pool


def _folio_entry(x: dict, stratum: str, profile_hash: str, fol_code: str) -> dict:
    folio_recs = {}
    for fn in ("folio-train.jsonl", "folio-validation.jsonl"):
        for line in (SC / fn).read_text().splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            folio_recs[(fn, r.get("example_id"))] = r
    rec = folio_recs[(x["file"], x["example_id"])]
    i = x["premise_index"]
    text = rec["premises"][i]
    f = rec["premises-FOL"][i].strip()
    ir = fol.adapt_fol(f)
    subset = {"wiki": "WikiLogic", "hyb": "HybLogic"}.get(rec.get("source"), "?")
    entry = {
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
    }
    entry.update(_commit(entry["case_id"], ir, profile_hash))
    return entry


def _pmb_pools(in_n_pmb_locs: set) -> tuple[list, list]:
    pmb_scan = json.loads((HERE / "pmb_eligibility_scan_pathB.json").read_text())
    forall_pool, exists_pool = [], []
    for c in pmb_scan["candidates"]:
        doc = c["doc"]
        if doc in in_n_pmb_locs:
            continue
        sbn_path = GOLD / doc / "en.drs.sbn"
        raw_path = GOLD / doc / "en.raw"
        if not sbn_path.exists() or not raw_path.exists():
            continue
        sbn_text = sbn_path.read_text(errors="replace")
        if any("ANA" in l.split("%", 1)[0].split()
               for l in sbn_text.splitlines() if not l.startswith("%%%")):
            continue
        cid = f"PMB-{doc.replace('/', '-')}"
        try:
            ir = sbn.adapt_sbn(sbn_text)
        except Exception:
            continue
        if cg_ir.validate_formula(ir) or cg_ir.free_variables(ir):
            continue
        raw = raw_path.read_text(errors="replace")
        text = " ".join(raw.split())
        ok, _why = control_eligible(cid, text, ir)
        if not ok:
            continue
        kind = _quant_kind(cid, ir)
        if kind == "forall":
            forall_pool.append(doc)
        elif kind == "exists":
            exists_pool.append(doc)
    return forall_pool, exists_pool


def _pmb_entry(doc: str, stratum: str, profile_hash: str, sbn_code: str) -> dict:
    raw = (GOLD / doc / "en.raw").read_text(errors="replace")
    text = " ".join(raw.split())
    sbn_bytes = (GOLD / doc / "en.drs.sbn").read_bytes()
    ir = sbn.adapt_sbn(sbn_bytes.decode("utf-8", "replace"))
    cid = f"PMB-{doc.replace('/', '-')}"
    entry = {
        "case_id": cid,
        "stratum": stratum,
        "source_locator": {
            "corpus_id": "pmb-5.1.0", "corpus_version": "5.1.0",
            "artifact": f"data/en/gold/{doc}/en.drs.sbn",
            "record_locator": doc,
            "retrieval_urls": ["https://pmb.let.rug.nl/releases/pmb-5.1.0.zip"]},
        "text_sha256": put_cache(text.encode()),
        "lf_sha256": put_cache(sbn_bytes),
        "adapter_version": "cg_sbn_adapter/PMB_SBN_5_1",
        "adapter_code_sha256": sbn_code,
    }
    entry.update(_commit(cid, ir, profile_hash))
    return entry


def refreeze() -> dict:
    v5 = json.loads(V5_PATH.read_text(encoding="utf-8"))
    profile_hash = v5["profile_hash"]
    fol_code = _code_sha("cg_fol_adapter.py")
    sbn_code = _code_sha("cg_sbn_adapter.py")

    in_n_folio_ids = {e["case_id"] for e in v5["entries"] if e["case_id"].startswith("FOLIO-")}
    in_n_pmb_locs = {e["source_locator"]["record_locator"] for e in v5["entries"]
                      if e["case_id"].startswith("PMB-")}

    folio_forall_pool, folio_exists_pool = _folio_pools(in_n_folio_ids)
    pmb_forall_pool, pmb_exists_pool = _pmb_pools(in_n_pmb_locs)

    pools = {
        "folio_forall": len(folio_forall_pool),
        "folio_exists": len(folio_exists_pool),
        "pmb_forall": len(pmb_forall_pool),
        "pmb_exists": len(pmb_exists_pool),
    }
    need = {
        "folio_forall": STRATA_N["folio_universal_control"],
        "folio_exists": STRATA_N["folio_existential_control"],
        "pmb_forall": STRATA_N["pmb_universal_control"],
        "pmb_exists": STRATA_N["pmb_existential_control"],
    }
    for k, n in need.items():
        if pools[k] < n:
            raise SystemExit(f"BLOCKED: pool {k} = {pools[k]} < {n}")

    folio_key = lambda x: order_key(f"{x['example_id']}#{x['premise_index']}")
    folio_forall_top = sorted(folio_forall_pool, key=folio_key)[:STRATA_N["folio_universal_control"]]
    folio_exists_top = sorted(folio_exists_pool, key=folio_key)[:STRATA_N["folio_existential_control"]]
    pmb_forall_top = sorted(pmb_forall_pool, key=order_key)[:STRATA_N["pmb_universal_control"]]
    pmb_exists_top = sorted(pmb_exists_pool, key=order_key)[:STRATA_N["pmb_existential_control"]]

    entries = (
        [_folio_entry(x, "folio_universal_control", profile_hash, fol_code) for x in folio_forall_top]
        + [_folio_entry(x, "folio_existential_control", profile_hash, fol_code) for x in folio_exists_top]
        + [_pmb_entry(doc, "pmb_universal_control", profile_hash, sbn_code) for doc in pmb_forall_top]
        + [_pmb_entry(doc, "pmb_existential_control", profile_hash, sbn_code) for doc in pmb_exists_top]
    )

    strata_counts = {}
    for e in entries:
        strata_counts[e["stratum"]] = strata_counts.get(e["stratum"], 0) + 1

    manifest = {
        "manifest_version": "e2e-v1-c-controls-v5.1",
        "amendment": {
            "procedure": "PRE_EXECUTION_FREEZE_AMENDMENT_V1",
            "rulings": ["D-E2E-v1-27"],
            "eligibility_profile": "O1_CONTROL_ELIGIBILITY_V1",
            "reselection_trigger": "CONTROLS_RUN_V5_20260824 — FOLIO adapter 2/3, "
                                    "해석 가능 조건 미충족",
            "old_controls_status": "HISTORICAL_QUALIFICATION_EVIDENCE",
            "cohort_dispatch_count_at_amendment": 0,
            "defect": "V5 control 실행이 결정론 재선별 이전의 손 선택 control 6건에 "
                      "의존해 2/6만 해석 가능했다 — 새 2층 적격 술어로 재선별한다.",
        },
        "order_seed": v5["order_seed"],
        "profile": v5["profile"],
        "profile_hash": v5["profile_hash"],
        "contract_hashes": v5["contract_hashes"],
        "measurement_contract": v5["measurement_contract"],
        "supersedes": v5["supersedes"],
        "score_comparability": v5["score_comparability"],
        "measurement_semantics": v5["measurement_semantics"],
        "selection_inputs": {
            **v5["selection_inputs"],
            "control_eligibility_pools": pools,
        },
        "strata_counts": strata_counts,
        "entries": entries,
    }
    return manifest


if __name__ == "__main__":
    out = HERE / "stage2_controls_manifest_v5_1.json"
    if out.exists():
        raise SystemExit("V5.1 control manifest already exists — refusing overwrite")
    m = refreeze()
    out.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    from collections import Counter
    print("refrozen V5.1 controls:", len(m["entries"]), "entries")
    print("strata:", dict(Counter(e["stratum"] for e in m["entries"])))
    print("pools:", m["selection_inputs"]["control_eligibility_pools"])
    for e in m["entries"]:
        print(" -", e["stratum"], e["case_id"])
