"""control 재선별 V5.1 불변식 게이트 (D-E2E-v1-27 §18 — 판정이 이미 승인한 경로).

V5 control 실행이 2/6(FOLIO adapter 2/3)으로 해석 가능 조건을 미충족했다
(`CONTROLS_RUN_V5_20260824.md`). D-27 §18은 이 상황의 처분을 이미 판정했다:
old controls → 역사 기록(삭제 금지), 새 적격 술어(`O1_CONTROL_ELIGIBILITY_V1`,
2층) → 결정론 재선별 → qualification 재실행. 이 게이트가 보증하는 것:

  1. 층 구성이 판정 문면을 따른다 — D-27 §16(source별 단순 보편 1~2 +
     단순 존재 1) ∧ D-25 §29(PMB 총 2~3): FOLIO U2+E1, PMB U1+E1
  2. 모든 entry가 `control_eligible` 2층 술어를 캐시 실물 재계산으로 통과
  3. in-N 20과 서로소 (control은 N 밖)
  4. commitment 완전성: V5와 같은 필드 + V2 서명 commitment, profile은 V5
  5. old control 6건은 V5 manifest에 바이트 그대로 남아 있다(역사 기록)
  6. 선별 풀 크기가 selection_inputs에 기록돼 재검증 가능하다
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from conceptgate.cg_identity import canonical_sha256  # noqa: E402

V5_1_PATH = HERE / "stage2_controls_manifest_v5_1.json"
V5_PATH = HERE / "stage2_fixture_manifest_v5.json"

EXPECTED_STRATA = {
    "folio_universal_control": 2,
    "folio_existential_control": 1,
    "pmb_universal_control": 1,
    "pmb_existential_control": 1,
}

COMMITMENT_FIELDS = ("case_id", "stratum", "source_locator", "text_sha256",
                     "lf_sha256", "adapter_version", "adapter_code_sha256",
                     "canonicalization_profile_hash", "expected_ir_sha256",
                     "expected_scope_signature_v2_sha256")


def _load():
    return (json.loads(V5_PATH.read_text(encoding="utf-8")),
            json.loads(V5_1_PATH.read_text(encoding="utf-8")))


# ---- 1. 층 구성 = 판정 문면 ------------------------------------------------

def test_strata_follow_d27_s16_and_d25_s29():
    _, m = _load()
    got = {}
    for e in m["entries"]:
        got[e["stratum"]] = got.get(e["stratum"], 0) + 1
    assert got == EXPECTED_STRATA
    assert m["strata_counts"] == EXPECTED_STRATA
    # D-25 §29: PMB 총 2~3
    pmb = sum(v for k, v in got.items() if k.startswith("pmb_"))
    assert 2 <= pmb <= 3


def test_amendment_cites_the_authorizing_ruling_and_the_failed_run():
    _, m = _load()
    am = m["amendment"]
    assert am["procedure"] == "PRE_EXECUTION_FREEZE_AMENDMENT_V1"
    assert "D-E2E-v1-27" in am["rulings"]
    assert am["eligibility_profile"] == "O1_CONTROL_ELIGIBILITY_V1"
    assert "CONTROLS_RUN_V5_20260824" in am["reselection_trigger"]
    assert am["old_controls_status"] == "HISTORICAL_QUALIFICATION_EVIDENCE"


# ---- 2. 2층 술어를 캐시 실물로 재계산 --------------------------------------

def test_every_control_passes_the_two_layer_predicate_from_cache():
    from conceptgate import cg_sbn_adapter as sbn, cg_fol_adapter as fol
    from conceptgate.cg_fixture_resolver import resolve_bytes
    from _stage2_surface_filters import control_eligible
    import _stage2_projection_pipeline_v2 as pipe

    _, m = _load()
    cache = REPO / ".oracle_cache"
    for e in m["entries"]:
        cid = e["case_id"]
        text = resolve_bytes(e["text_sha256"], cache)
        lf = resolve_bytes(e["lf_sha256"], cache)
        assert text["execution"] == "ok" and lf["execution"] == "ok", cid
        if cid.startswith("PMB-"):
            ir = sbn.adapt_sbn(lf["data"].decode("utf-8", "replace"))
        else:
            ir = fol.adapt_fol(lf["data"].decode("utf-8"))
        ok, why = control_eligible(cid, text["data"].decode("utf-8"), ir)
        assert ok, (cid, why)
        assert canonical_sha256(ir) == e["expected_ir_sha256"], cid
        sig = pipe.scope_signature_v2_for_case(cid, ir)
        assert (canonical_sha256(pipe.signature_jsonable(sig))
                == e["expected_scope_signature_v2_sha256"]), cid


def test_stratum_matches_the_single_quantifier_kind():
    """`*_universal_control`은 forall 1개, `*_existential_control`은 exists
    1개 — 층 이름이 거짓말을 못 하게 결박한다."""
    from conceptgate import cg_sbn_adapter as sbn, cg_fol_adapter as fol
    from conceptgate.cg_fixture_resolver import resolve_bytes
    from _stage2_scope_projection import project_scope_for_case

    _, m = _load()
    cache = REPO / ".oracle_cache"
    for e in m["entries"]:
        cid = e["case_id"]
        lf = resolve_bytes(e["lf_sha256"], cache)["data"]
        ir = (sbn.adapt_sbn(lf.decode("utf-8", "replace")) if cid.startswith("PMB-")
              else fol.adapt_fol(lf.decode("utf-8")))
        sig = project_scope_for_case(cid, ir)
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
        expected = "forall" if "universal" in e["stratum"] else "exists"
        assert kinds == [expected], (cid, e["stratum"], kinds)


# ---- 3. N 밖 ---------------------------------------------------------------

def test_controls_are_disjoint_from_the_frozen_20():
    v5, m = _load()
    in_n_ids = {e["case_id"] for e in v5["entries"]}
    in_n_locs = {e["source_locator"]["record_locator"] for e in v5["entries"]}
    for e in m["entries"]:
        assert e["case_id"] not in in_n_ids
        assert e["source_locator"]["record_locator"] not in in_n_locs


# ---- 4. commitment 완전성 + profile 상속 -----------------------------------

def test_commitment_fields_are_complete_and_profile_is_v5():
    v5, m = _load()
    assert m["profile_hash"] == v5["profile_hash"]
    assert m["measurement_contract"] == v5["measurement_contract"]
    for e in m["entries"]:
        for f in COMMITMENT_FIELDS:
            assert e.get(f), (e.get("case_id"), f)
        assert e["canonicalization_profile_hash"] == v5["profile_hash"]


# ---- 5. old controls는 역사 기록으로 보존 ----------------------------------

def test_old_controls_remain_in_v5_manifest_verbatim():
    v5, _ = _load()
    old = ([e["case_id"] for e in v5["folio_simple_controls"]]
           + [e["case_id"] for e in v5["pmb_projection_controls"]])
    assert old == ["FOLIO-175p1", "FOLIO-500p4", "FOLIO-1377p0",
                   "PMB-p12-d2559", "PMB-p11-d2268", "PMB-p24-d2685"]


# ---- 6. 선별 풀의 재검증 가능성 --------------------------------------------

def test_selection_pool_sizes_are_recorded():
    _, m = _load()
    pools = m["selection_inputs"]["control_eligibility_pools"]
    for key in ("folio_forall", "folio_exists", "pmb_forall", "pmb_exists"):
        assert isinstance(pools[key], int) and pools[key] >= 1, key
    # 뽑은 수보다 풀이 작을 수는 없다
    assert pools["folio_forall"] >= 2
    assert pools["pmb_forall"] >= 1
