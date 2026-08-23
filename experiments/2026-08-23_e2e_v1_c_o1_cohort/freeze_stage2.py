#!/usr/bin/env python3
"""Stage 2 fixture 동결 — 결정적 선별 + commitment manifest 생성.

D-19 §11(사전등록 목록)·D-20(commitment, 원문 0바이트)·D-21 §15(2경로
합의)·D-22 §16(구성: PMB≤15+FOLIO≥5, stratum)·D-23 §15-§16(FOLIO 조건,
subset 기록)의 집행이다. 모든 선택은 이 파일이 정본인 규칙으로 결정된다 —
seed는 스캔 결과 커밋 이후에 정해졌고(이력이 증거), 손 선택 지점은 없다.

텍스트 규칙(기록): PMB 문장 = en.raw의 공백 정규화(" ".join(split)) —
80열 행접기 제거. LF = en.drs.sbn 바이트 그대로. FOLIO 문장/FOL = 레코드
문자열 그대로(utf-8).

선별 모집단: PMB = Path B 후보 중 **ANA 토큰 무보유**(적대검증 라운드의
기록 — 문장 내 조응 연산자 회피 우선). FOLIO = 2경로 합의 multi_mixed.
층 배정은 우선순위 사슬(proportional → quant_neg → universal → cardinal →
existential)로 결정적 — 한 문서는 한 층에만.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from conceptgate import cg_ir, cg_sbn_adapter as sbn, cg_fol_adapter as fol  # noqa: E402
from conceptgate.cg_identity import canonical_sha256  # noqa: E402

SEED = "E2EV1C-freeze-20260823-v1"
O1_V1_CONSTRUCTORS = ("forall", "exists", "and", "pred", "not")
PROFILE_DESCRIPTOR = {
    "id": "O1_V1",
    "constructors": list(O1_V1_CONSTRUCTORS),
    "canonicalizer": "cg_ir.canonicalize_v0 (capture-avoiding alpha-rename only)",
    "comparison_core": {
        "desugar": "FORALL(x,R,B)->FORALL(x,True,implies(R,B)); "
                   "EXISTS(x,R,B)->EXISTS(x,True,and(R,B)) (D-23 §12)",
        "predicate_labels": "O1_PMB_LEMMA_NO_SENSE_V1",
    },
    "source_encoding_profiles": {
        "PMB_SBN_5_1": "paired NEGATION -> forall (documented codec, D-22 Q22.2)",
        "FOLIO_FOL_V0": "implication-under-forall lowering; neutral exists (D-23 §12)",
    },
}
PROFILE_HASH = canonical_sha256(PROFILE_DESCRIPTOR)

STRATA_COUNTS = {"proportional": 1, "quantifier_negation_scope": 4,
                 "single_universal": 4, "cardinal": 3, "single_existential": 3}
FOLIO_MULTI_N = 5
FOLIO_CONTROL_N = 3

SC = Path("/private/tmp/claude-501/-Users-jaehyuntak/3d0782d1-aa4a-4b52-a775-cf96d309690c/scratchpad")
GOLD = SC / "pmb_gold"
CACHE = REPO / ".oracle_cache"


def order_key(ident: str) -> str:
    return hashlib.sha256(f"{SEED}:{ident}".encode()).hexdigest()


def put_cache(data: bytes) -> str:
    CACHE.mkdir(exist_ok=True)
    h = hashlib.sha256(data).hexdigest()
    (CACHE / h).write_bytes(data)
    return h


def kinds_of(ir) -> set:
    acc = set()
    def walk(n):
        if isinstance(n, dict):
            if "kind" in n:
                acc.add(n["kind"])
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(ir)
    return acc


def pmb_stratum(doc: str, raw: str, sbn_text: str, ks: set) -> str | None:
    if re.search(r"\bmost\b", raw, re.I):
        return "proportional"
    if "forall" in ks and "not" in ks:
        return "quantifier_negation_scope"
    if "forall" in ks:
        return "single_universal"
    has_quantity = bool(re.search(r"(?:^|\s)Quantity(?:\s)", sbn_text, re.M)
                        or re.search(r"quantity\.n\.\d+", sbn_text))
    if has_quantity:
        return "cardinal"
    if "exists" in ks and "forall" not in ks and "not" not in ks:
        return "single_existential"
    return None


def freeze() -> dict:
    pmb_scan = json.loads((HERE / "pmb_eligibility_scan_pathB.json").read_text())
    folio_scan = json.loads((HERE / "folio_eligibility_scan.json").read_text())
    sbn_code = hashlib.sha256((REPO / "conceptgate" / "cg_sbn_adapter.py")
                              .read_text().encode()).hexdigest()
    fol_code = hashlib.sha256((REPO / "conceptgate" / "cg_fol_adapter.py")
                              .read_text().encode()).hexdigest()

    # ---- PMB 15 ----
    strata_pools: dict[str, list] = {k: [] for k in STRATA_COUNTS}
    for c in pmb_scan["candidates"]:
        doc = c["doc"]
        sbn_text = (GOLD / doc / "en.drs.sbn").read_text(errors="replace")
        # ANA 보유 문서 제외 (적대검증 라운드 기록)
        if any("ANA" in l.split("%", 1)[0].split()
               for l in sbn_text.splitlines() if not l.startswith("%%%")):
            continue
        try:
            ir = sbn.adapt_sbn(sbn_text)
        except Exception:
            continue
        if cg_ir.validate_formula(ir) or cg_ir.free_variables(ir):
            continue
        raw = (GOLD / doc / "en.raw").read_text(errors="replace")
        s = pmb_stratum(doc, raw, sbn_text, kinds_of(ir))
        if s in strata_pools:
            strata_pools[s].append(doc)

    entries = []
    assignment = {}
    for stratum, n in STRATA_COUNTS.items():
        pool = sorted(strata_pools[stratum], key=order_key)
        if len(pool) < n:
            raise SystemExit(f"stratum {stratum}: pool {len(pool)} < {n}")
        for doc in pool[:n]:
            raw = (GOLD / doc / "en.raw").read_text(errors="replace")
            text = " ".join(raw.split())
            sbn_bytes = (GOLD / doc / "en.drs.sbn").read_bytes()
            met = (GOLD / doc / "en.met").read_text(errors="replace")
            sub = (re.search(r"subcorpus:\s*(.+)", met) or [None, "?"])[1].strip()
            ir = sbn.adapt_sbn(sbn_bytes.decode("utf-8", "replace"))
            entries.append({
                "case_id": f"PMB-{doc.replace('/', '-')}",
                "stratum": stratum,
                "source_locator": {
                    "corpus_id": "pmb-5.1.0", "corpus_version": "5.1.0",
                    "artifact": f"data/en/gold/{doc}/en.drs.sbn",
                    "record_locator": doc,
                    "retrieval_urls": ["https://pmb.let.rug.nl/releases/pmb-5.1.0.zip"]},
                "subcorpus": sub,
                "text_sha256": put_cache(text.encode()),
                "lf_sha256": put_cache(sbn_bytes),
                "adapter_version": "cg_sbn_adapter/PMB_SBN_5_1",
                "adapter_code_sha256": sbn_code,
                "canonicalization_profile_hash": PROFILE_HASH,
                "expected_ir_sha256": canonical_sha256(ir)})
            assignment[entries[-1]["case_id"]] = stratum

    # ---- FOLIO 5 (multi) + 3 (controls, N 밖) ----
    folio_recs = {}
    for fn in ("folio-train.jsonl", "folio-validation.jsonl"):
        for line in (SC / fn).read_text().splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            folio_recs[(fn, rec.get("example_id"))] = rec

    def folio_entry(x, stratum):
        rec = folio_recs[(x["file"], x["example_id"])]
        i = x["premise_index"]
        text = (rec.get("premises") or [""] * (i + 1))[i]
        f = (rec.get("premises-FOL") or [""] * (i + 1))[i].strip()
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
            "canonicalization_profile_hash": PROFILE_HASH,
            "expected_ir_sha256": canonical_sha256(ir)}

    multi = sorted(folio_scan["multi_mixed"],
                   key=lambda x: order_key(f"{x['example_id']}#{x['premise_index']}"))
    controls = sorted(folio_scan["single_controls"],
                      key=lambda x: order_key(f"{x['example_id']}#{x['premise_index']}"))
    for x in multi[:FOLIO_MULTI_N]:
        e = folio_entry(x, "multi_quantifier")
        entries.append(e)
        assignment[e["case_id"]] = "multi_quantifier"
    control_entries = [folio_entry(x, "adapter_control")
                       for x in controls[:FOLIO_CONTROL_N]]

    manifest = {
        "manifest_version": "e2e-v1-c-fixtures-v1",
        "order_seed": SEED,
        "profile": PROFILE_DESCRIPTOR,
        "profile_hash": PROFILE_HASH,
        "selection_inputs": {
            "pmb_scan_sha256": hashlib.sha256(
                (HERE / "pmb_eligibility_scan_pathB.json").read_bytes()).hexdigest(),
            "folio_scan_sha256": hashlib.sha256(
                (HERE / "folio_eligibility_scan.json").read_bytes()).hexdigest()},
        "strata_counts": {**STRATA_COUNTS, "multi_quantifier": FOLIO_MULTI_N},
        "entries": entries,
        "folio_simple_controls": control_entries,
    }
    assert len(entries) == 20, len(entries)
    return manifest


if __name__ == "__main__":
    m = freeze()
    out = HERE / "stage2_fixture_manifest.json"
    if out.exists():
        raise SystemExit("manifest already exists — freeze is irreversible; refusing overwrite")
    out.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    from collections import Counter
    print("frozen:", len(m["entries"]), "fixtures +", len(m["folio_simple_controls"]), "controls")
    print("strata:", dict(Counter(e["stratum"] for e in m["entries"])))
    print("profile_hash:", m["profile_hash"][:16])
    print("subcorpora:", dict(Counter(e.get("subcorpus", e.get("folio_subset")) for e in m["entries"])))
