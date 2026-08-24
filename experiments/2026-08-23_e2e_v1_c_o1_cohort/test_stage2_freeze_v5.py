"""V5 재동결 불변식 게이트 (D-E2E-v1-32 + D-E2E-v1-32-C).

V5는 **투영 전용 개정**이다: fixture 선별·commitment·방언·template은 V4
그대로이고, 바뀌는 것은 측정 계약(투영 profile V1→V2)과 그로부터 재생성되는
서명 commitment뿐이다. 이 게이트가 보증하는 것:

  1. V4 manifest는 바이트 불변 (pin)
  2. V5 entries 20 + control 6: V4와 commitment 필드 바이트 동일 —
     **expected_ir_sha256 포함**(oracle IR 유도는 안 바뀌었다; 판정문
     "expected_ir_sha256 재생성"은 재계산 후 동일값 확인을 뜻하고,
     20/20이 바뀌는 것은 IR가 아니라 **scope 서명**이다 — 회고 §16 G121)
  3. 각 entry에 `expected_scope_signature_v2_sha256`가 있고, 캐시 실물에서
     파이프라인으로 재계산한 값과 일치한다 (drift 게이트)
  4. measurement_contract·supersedes·score_comparability·측정 의미론 선언이
     판정 B.7의 문면 그대로 존재한다
  5. contract_hashes가 라이브 계약 모듈과 일치 — V2 투영·파이프라인을
     고치면 V5 동결이 자동 실효된다 (V4와 같은 기제)
  6. profile은 V4에서 정확히 두 필드(id, scope_projection)만 다르다 —
     투영 전용 개정이라는 주장의 기계 검증
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from conceptgate.cg_identity import canonical_sha256  # noqa: E402

V4_MANIFEST_SHA256 = "723ed98c2ce1c2d9edb7892c6aeb2760dc18e03ad93b94081d9e0d5dbc8b4ec8"

V4_PATH = HERE / "stage2_fixture_manifest_v4.json"
V5_PATH = HERE / "stage2_fixture_manifest_v5.json"

INVARIANT_FIELDS = ("case_id", "stratum", "source_locator", "subcorpus",
                    "text_sha256", "lf_sha256", "adapter_version",
                    "adapter_code_sha256", "expected_ir_sha256")

CONTROL_INVARIANT_FIELDS = tuple(f for f in INVARIANT_FIELDS if f != "subcorpus")


def _load():
    return (json.loads(V4_PATH.read_text(encoding="utf-8")),
            json.loads(V5_PATH.read_text(encoding="utf-8")))


def _code_sha(rel: str) -> str:
    return hashlib.sha256((HERE / rel).read_bytes()).hexdigest()


# ---- 1. V4 바이트 불변 ----------------------------------------------------

def test_v4_manifest_bytes_are_unchanged():
    assert hashlib.sha256(V4_PATH.read_bytes()).hexdigest() == V4_MANIFEST_SHA256


# ---- 2. 선별·commitment 불변 ---------------------------------------------

def test_v5_exists_and_is_versioned():
    _, v5 = _load()
    assert v5["manifest_version"] == "e2e-v1-c-fixtures-v5"


def test_entries_keep_v4_commitments_verbatim():
    v4, v5 = _load()
    assert len(v5["entries"]) == 20
    by_id_v4 = {e["case_id"]: e for e in v4["entries"]}
    for e in v5["entries"]:
        ref = by_id_v4[e["case_id"]]
        for f in INVARIANT_FIELDS:
            assert e.get(f) == ref.get(f), (e["case_id"], f)
        assert e["canonicalization_profile_hash"] == v5["profile_hash"]


@pytest.mark.parametrize("block,n", [("folio_simple_controls", 3),
                                     ("pmb_projection_controls", 3)])
def test_controls_keep_v4_commitments_verbatim(block, n):
    v4, v5 = _load()
    assert len(v5[block]) == n
    by_id_v4 = {e["case_id"]: e for e in v4[block]}
    for e in v5[block]:
        ref = by_id_v4[e["case_id"]]
        for f in CONTROL_INVARIANT_FIELDS:
            assert e.get(f) == ref.get(f), (e["case_id"], f)


def test_selection_and_strata_are_inherited_from_v4():
    v4, v5 = _load()
    assert v5["selection_inputs"] == v4["selection_inputs"]
    assert v5["strata_counts"] == v4["strata_counts"]
    assert v5["order_seed"] == v4["order_seed"]


# ---- 3. 서명 commitment — 존재 + 캐시 실물 재계산 일치 --------------------

def test_every_fixture_carries_a_v2_signature_commitment():
    _, v5 = _load()
    for block in ("entries", "folio_simple_controls", "pmb_projection_controls"):
        for e in v5[block]:
            h = e.get("expected_scope_signature_v2_sha256")
            assert isinstance(h, str) and len(h) == 64, e["case_id"]


def test_signature_commitments_recompute_from_cache():
    """drift 게이트 — 기록된 값을 믿지 않고 캐시 실물에서 재계산으로 대조한다
    (`cg_normalizer.verify_snapshot`의 "hash는 증거가 아니다"와 같은 철학)."""
    from conceptgate import cg_sbn_adapter as sbn, cg_fol_adapter as fol
    from conceptgate.cg_fixture_resolver import resolve_bytes
    import _stage2_projection_pipeline_v2 as pipe

    _, v5 = _load()
    cache = REPO / ".oracle_cache"
    checked = 0
    for block in ("entries", "folio_simple_controls", "pmb_projection_controls"):
        for e in v5[block]:
            got = resolve_bytes(e["lf_sha256"], cache)
            assert got["execution"] == "ok", e["case_id"]
            cid = e["case_id"]
            if cid.startswith("PMB-"):
                ir = sbn.adapt_sbn(got["data"].decode("utf-8", "replace"))
            else:
                ir = fol.adapt_fol(got["data"].decode("utf-8"))
            assert canonical_sha256(ir) == e["expected_ir_sha256"], cid
            sig = pipe.scope_signature_v2_for_case(cid, ir)
            h = canonical_sha256(pipe.signature_jsonable(sig))
            assert h == e["expected_scope_signature_v2_sha256"], cid
            checked += 1
    assert checked == 26


# ---- 4. 판정 B.7 문면 -----------------------------------------------------

def test_measurement_contract_is_declared():
    _, v5 = _load()
    mc = v5["measurement_contract"]
    assert mc["projection_profile"] == "O1_SCOPE_PROJECTION_V2"
    assert mc["projection_profile_hash"] == v5["profile_hash"]
    assert mc["projection_module_sha256"] == _code_sha("_stage2_scope_projection_v2.py")
    assert mc["pre_projection_module_sha256"] == _code_sha("_stage2_scope_projection.py")
    assert mc["pipeline_module_sha256"] == _code_sha("_stage2_projection_pipeline_v2.py")


def test_supersedes_and_comparability_are_declared():
    _, v5 = _load()
    assert v5["supersedes"] == ["O1_SCOPE_PROJECTION_V1"]
    cmp_ = v5["score_comparability"]["V1_to_V2"]
    assert cmp_["direct_numeric_comparison"] is False
    assert cmp_["reason"] == "non_scope_restriction_and_body_content_projection_changed"


def test_measurement_semantics_chain_is_declared():
    _, v5 = _load()
    sem = v5["measurement_semantics"]
    assert sem["V1-V4"] == "O1_SCOPE_PROJECTION_V1"
    assert sem["V5_onward"] == "O1_SCOPE_PROJECTION_V2"


def test_amendment_records_procedure_rulings_and_zero_dispatch():
    _, v5 = _load()
    am = v5["amendment"]
    assert am["procedure"] == "PRE_EXECUTION_FREEZE_AMENDMENT_V1"
    assert am["rulings"] == ["D-E2E-v1-32", "D-E2E-v1-32-C"]
    assert am["v4_status"] == "SUPERSEDED_PRE_EXECUTION"
    assert am["cohort_dispatch_count_at_amendment"] == 0
    imp = am["reprojection_impact"]
    assert imp["in_n_signature_changed_vs_v1"] == 20
    assert imp["in_n_total"] == 20


# ---- 5. contract_hashes = 라이브 (수정 시 자동 실효) ----------------------

def test_contract_hashes_bind_the_live_modules():
    v4, v5 = _load()
    ch = v5["contract_hashes"]
    # 투영 전용 개정: template·schema는 V4 그대로
    assert ch["prompt_template_v4_sha256"] == v4["contract_hashes"]["prompt_template_v4_sha256"]
    assert ch["dispatch_schema_sha256"] == v4["contract_hashes"]["dispatch_schema_sha256"]
    for key, rel in (
            ("canonicalization_core_sha256", "_stage2_canonical_core.py"),
            ("projection_module_sha256", "_stage2_scope_projection.py"),
            ("projection_module_v2_sha256", "_stage2_scope_projection_v2.py"),
            ("projection_pipeline_module_sha256", "_stage2_projection_pipeline_v2.py"),
            ("satisfiability_module_sha256", "_stage2_satisfiability.py"),
            ("eval_profile_module_sha256", "_stage2_eval_profile.py")):
        assert ch[key] == _code_sha(rel), key


# ---- 6. 투영 전용 개정의 기계 검증 ----------------------------------------

def test_profile_differs_from_v4_in_exactly_the_projection_fields():
    from copy import deepcopy
    v4, v5 = _load()
    patched = deepcopy(v4["profile"])
    patched["id"] = "O1_V5"
    patched["comparison_core"]["scope_projection"] = "O1_SCOPE_PROJECTION_V2"
    assert v5["profile"] == patched
    assert v5["profile_hash"] == canonical_sha256(v5["profile"])
