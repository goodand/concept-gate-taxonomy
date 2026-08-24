"""V4 재동결 불변식 게이트 (D-25 + D-26).

보증하는 것:
  1. V1·V2 manifest는 바이트 불변 (V1 pin은 test_stage2_freeze_v2가 이미
     보유 — 여기서는 V2를 pin)
  2. PMB in-N 15: V2와 선별·commitment 불변, profile hash 필드만 V4
  3. V4의 모든 fixture(20 + FOLIO control 3 + PMB control 3)가
     MEASUREMENT_SATISFIABILITY_V2를 통과 — 캐시 실물로 재판정
  4. contract_hashes가 라이브 모듈과 일치 — **projection·satisfiability·
     canonical core·eval profile을 고치면 V4 동결이 자동 실효**
     (adapter 자격의 코드 결박과 같은 기제)
  5. profile hash 재계산 가능, 방언 6종(implies 포함), seed·층 상속
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from conceptgate.cg_identity import canonical_sha256  # noqa: E402
from conceptgate.cg_ir_schema import dispatch_envelope_schema  # noqa: E402

V2_MANIFEST_SHA256 = "7eac95dd74fa96ce036f7d66c3c2f251fe83b33eab0f3628036ad146bbde0bfc"

V2_PATH = HERE / "stage2_fixture_manifest_v2.json"
V4_PATH = HERE / "stage2_fixture_manifest_v4.json"
SAT_SCAN_PATH = HERE / "stage2_sat_scan_v4.json"

INVARIANT_FIELDS = ("case_id", "stratum", "source_locator", "subcorpus",
                    "text_sha256", "lf_sha256", "adapter_version",
                    "adapter_code_sha256", "expected_ir_sha256")


def _load():
    return (json.loads(V2_PATH.read_text(encoding="utf-8")),
            json.loads(V4_PATH.read_text(encoding="utf-8")))


def test_v2_manifest_is_byte_immutable():
    assert hashlib.sha256(V2_PATH.read_bytes()).hexdigest() == V2_MANIFEST_SHA256


def test_v4_declares_lineage():
    _, v4 = _load()
    assert v4["manifest_version"] == "e2e-v1-c-fixtures-v4"
    am = v4["amendment"]
    assert am["rulings"] == ["D-E2E-v1-25", "D-E2E-v1-26"]
    assert am["v2_status"] == "SUPERSEDED_PRE_EXECUTION"
    assert "ABORTED_PRE_FREEZE" in am["v3_status"]
    assert "no cohort outcomes observed" in am["defect"]


def test_pmb_15_invariant_from_v2():
    v2, v4 = _load()
    p2 = {e["case_id"]: e for e in v2["entries"] if e["case_id"].startswith("PMB-")}
    p4 = {e["case_id"]: e for e in v4["entries"] if e["case_id"].startswith("PMB-")}
    assert set(p2) == set(p4) and len(p4) == 15
    for cid, e2 in p2.items():
        e4 = p4[cid]
        for f in INVARIANT_FIELDS:
            assert e2.get(f) == e4.get(f), (cid, f)
        assert e4["canonicalization_profile_hash"] == v4["profile_hash"]


def test_profile_v4_recomputable_and_has_implies_dialect():
    _, v4 = _load()
    assert canonical_sha256(v4["profile"]) == v4["profile_hash"]
    assert v4["profile"]["constructors"] == \
        ["forall", "exists", "and", "pred", "not", "implies"]
    assert v4["profile"]["comparison_core"]["scope_projection"] == \
        "O1_SCOPE_PROJECTION_V1"
    labels = v4["profile"]["comparison_core"]["predicate_labels"]
    assert "diagnostic_only" in labels["status"]


# 동결 계보의 현재 상태. V4의 코드 결박은 "V4가 현행 동결일 때만" 유효하다 —
# D-27(curry 정규화·표면 필터) 구현으로 측정 경로 모듈이 바뀌었으므로 V4는
# 실효됐고 V5는 아직 동결되지 않았다. 이 공백은 숨기지 않고 주장한다:
# 이 상태에서 코호트를 실행하면 어떤 동결도 결과를 규정하지 못한다.
FREEZE_STATE = "V4_SUPERSEDED_BY_D27_IMPLEMENTATION__V5_ACTIVE"


def test_v4_code_binding_state_is_asserted_not_hidden():
    """V4 contract_hashes가 라이브와 어긋났다면 그것은 결함이 아니라
    **동결 실효 사실**이다 — 다만 그 사실이 명시돼 있어야 한다.

    V4가 현행이면 라이브와 일치해야 하고, superseded면 어긋나 있어야 한다
    (어긋나지 않았다면 FREEZE_STATE 선언이 거짓이다)."""
    _, v4 = _load()
    ch = v4["contract_hashes"]
    pairs = (("canonicalization_core_sha256", "_stage2_canonical_core.py"),
             ("projection_module_sha256", "_stage2_scope_projection.py"),
             ("satisfiability_module_sha256", "_stage2_satisfiability.py"),
             ("eval_profile_module_sha256", "_stage2_eval_profile.py"))
    drift = [rel for key, rel in pairs
             if ch[key] != hashlib.sha256((HERE / rel).read_bytes()).hexdigest()]
    if FREEZE_STATE.startswith("V4_CURRENT"):
        assert not drift, f"V4가 현행인데 실효: {drift}"
    else:
        assert drift, ("FREEZE_STATE가 superseded를 선언했는데 라이브가 V4와 "
                       "동일하다 — 선언이 거짓이거나 게이트가 공허하다")


def test_no_cohort_may_run_while_freeze_is_superseded():
    """실효 상태에서 코호트 결과 파일이 생겨 있으면 안 된다 —
    어떤 동결도 그 결과를 규정하지 못하므로 해석 불가다."""
    if FREEZE_STATE.startswith("V4_CURRENT"):
        return
    for name in ("stage2_results.json", "stage2_results_v4.json",
                 "stage2_cohort_results.json"):
        assert not (HERE / name).exists(), (
            f"{name}: 동결 실효 상태에서 코호트 결과가 존재한다")


def test_all_v4_fixtures_satisfiable_from_cache():
    import _stage2_satisfiability as sat
    from conceptgate import cg_sbn_adapter as sbn, cg_fol_adapter as fol
    _, v4 = _load()
    cache = REPO / ".oracle_cache"
    everything = (v4["entries"] + v4["folio_simple_controls"]
                  + v4["pmb_projection_controls"])
    assert len(everything) == 26
    for e in everything:
        lf = (cache / e["lf_sha256"]).read_bytes().decode()
        ir = (sbn.adapt_sbn(lf) if e["case_id"].startswith("PMB-")
              else fol.adapt_fol(lf))
        rec = sat.check_oracle_ir(e["case_id"], ir)
        assert rec["verdict"] == "SATISFIABLE", (e["case_id"], rec)


def test_sat_scan_pinned_and_gate_v2():
    _, v4 = _load()
    ss = json.loads(SAT_SCAN_PATH.read_text(encoding="utf-8"))
    assert ss["gate"] == "MEASUREMENT_SATISFIABILITY_V2"
    assert (v4["selection_inputs"]["satisfiability_scan_v4_sha256"]
            == canonical_sha256(ss))


def test_seed_and_strata_inherited():
    v2, v4 = _load()
    assert v4["order_seed"] == v2["order_seed"]
    assert v4["strata_counts"] == v2["strata_counts"]
    assert len(v4["entries"]) == 20
    assert len(v4["folio_simple_controls"]) == 3
    assert len(v4["pmb_projection_controls"]) == 3
    assert all(e["stratum"] == "pmb_projection_control"
               for e in v4["pmb_projection_controls"])


def test_diff_gate_catches_pmb_swap():
    v2, v4 = _load()
    tampered = json.loads(json.dumps(v4))
    victim = next(e for e in tampered["entries"] if e["case_id"].startswith("PMB-"))
    victim["expected_ir_sha256"] = "0" * 64
    p2 = {e["case_id"]: e for e in v2["entries"] if e["case_id"].startswith("PMB-")}
    bad = [cid for cid, e in
           ((x["case_id"], x) for x in tampered["entries"]
            if x["case_id"].startswith("PMB-"))
           if any(e.get(f) != p2[cid].get(f) for f in INVARIANT_FIELDS)]
    assert bad, "바꿔치기가 잡히지 않으면 이 게이트는 공허하다"


def test_v4_template_and_schema_hashes_still_bind():
    """template·dispatch schema는 코드 모듈이 아니라 불변 artifact다 —
    D-27 구현과 무관하게 V4 값이 계속 맞아야 한다(실효 대상 아님)."""
    _, v4 = _load()
    ch = v4["contract_hashes"]
    assert ch["prompt_template_v4_sha256"] == hashlib.sha256(
        (HERE / "stage2_prompt_template_v4.md").read_bytes()).hexdigest()
    assert ch["dispatch_schema_sha256"] == canonical_sha256(
        dispatch_envelope_schema(("forall", "exists", "and", "pred", "not", "implies")))


# ---- D-E2E-v1-31 Q31.3: 재료 신원 ≠ adapter 산출 신원 -------------------
#
# 판정: "`source artifact identity ≠ adapter output identity`를 혼동하지 않는
# 것이 핵심이다. 현재 `lf_sha256`이 **정확히 원본 artifact byte의 hash**라는
# 계약이라면 이름만 명확히 해도 된다."
#
# 실측으로 그 계약이 이미 성립한다: `freeze_stage2_v4.py`가
# `put_cache(f.encode())`(FOLIO의 FOL 텍스트) / `put_cache(sbn_bytes)`(PMB의
# 원본 바이트)로 계산하고, `.oracle_cache`가 그 해시로 **content-addressed**다.
# 아래 두 테스트는 그 계약을 **명시적으로** 결박한다 — 지금까지는 캐시 조회가
# 우연히 성공하는 것으로만 간접 보장됐다.

def test_lf_sha256_is_the_cached_artifact_byte_hash():
    """content-addressed 캐시의 이름이 곧 내용의 해시여야 한다."""
    import hashlib
    _, v4 = _load()
    cache = REPO / ".oracle_cache"
    everything = (v4["entries"] + v4["folio_simple_controls"]
                  + v4["pmb_projection_controls"])
    for e in everything:
        raw = (cache / e["lf_sha256"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == e["lf_sha256"], e["case_id"]


def test_source_identity_and_adapter_identity_are_distinct_fields():
    """둘이 같은 값이면 어느 층의 신원인지 구별할 수 없게 된다."""
    _, v4 = _load()
    everything = (v4["entries"] + v4["folio_simple_controls"]
                  + v4["pmb_projection_controls"])
    for e in everything:
        assert e["lf_sha256"] != e["expected_ir_sha256"], e["case_id"]
        assert e["lf_sha256"] != e["text_sha256"], e["case_id"]


def test_material_identity_fields_are_all_present():
    """판정이 요구한 최소 신원 필드가 항목마다 있어야 한다."""
    _, v4 = _load()
    for e in v4["entries"]:
        for field in ("source_locator", "text_sha256", "lf_sha256"):
            assert e.get(field), (e["case_id"], field)
        for field in ("expected_ir_sha256", "adapter_version",
                      "canonicalization_profile_hash"):
            assert e.get(field), (e["case_id"], field)
