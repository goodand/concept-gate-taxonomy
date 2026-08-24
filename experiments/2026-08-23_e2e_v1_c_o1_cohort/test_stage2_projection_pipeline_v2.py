"""V2 채점 파이프라인 계약 (D-E2E-v1-32 B.8 §1 "나머지는 현행 유지").

## 왜 합성인가 — 이 파일이 그 결정의 정본이다

V2 서명 모듈(`_stage2_scope_projection_v2`)은 순수한 signature 함수다.
그러나 D-32 B.8 §1은 V2의 델타를 **#1(제한식 opaque 붕괴)과 #5(and/or 정체
미채점)뿐**이라 명시했고 "나머지는 현행 유지"다. '나머지'에는 V1의 source별
granularity 다리 — PMB scaffold ∃ 제거(F3: 사건 매개 oracle과 직접 관계
subject의 대칭화), 국소 관용구 정규화(D-27), desugar — 가 포함된다. 그것을
버리면 PMB 채점이 구조적으로 전부 실패한다(oracle에만 사건 층이 있으므로).

따라서 V2 채점 = `V1 전처리(project_scope_for_case) → V2 signature` 합성이고,
이 합성은 runner에 흩어두지 않고 **hash-pin 가능한 계약 모듈**
`_stage2_projection_pipeline_v2.py`에 둔다 (V4가 계약 모듈만 pin하는 규율의
연장 — runner는 회계, 계약은 pin).

주의: V2 모듈 자신은 V1을 import하지 않는다(그 파일의 자기 선언). import는
파이프라인 모듈의 일이다.

## 채점 결과 어휘는 `cg_evaluate.evaluate`와 동일해야 한다

`_stage2_score`가 "pass"를 세므로 결과 어휘를 바꾸면 조용히 0점이 된다.
경계 의미론도 evaluate를 그대로 따른다: oracle 불량 = unscorable(평가기
결함), predicted 불량 = fail structural_validity(subject 결함).
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

import _stage2_projection_pipeline_v2 as pipe  # noqa: E402


# ---- 구성 선언 ----------------------------------------------------------

def test_pipeline_declares_its_composition():
    assert pipe.PRE_PROJECTION_PROFILE_ID == "O1_SCOPE_PROJECTION_V1"
    assert pipe.PROJECTION_PROFILE_ID == "O1_SCOPE_PROJECTION_V2"


def test_runner_scores_with_the_v2_pipeline():
    """0-e 배선 자체를 계약으로 결박한다 — runner가 V1 evaluate로 돌아가면
    이 테스트가 소리를 낸다."""
    import _stage2_run as run
    assert run.evaluate_scope_v2 is pipe.evaluate_scope_v2


# ---- 헬퍼 ---------------------------------------------------------------

def V(n):
    return {"kind": "var", "name": n}


def P(name, *vs):
    return {"kind": "pred", "name": name, "args": [V(x) for x in vs]}


TRUE = {"kind": "pred", "name": "True", "args": []}


def forall(v, r, b):
    return {"kind": "forall", "var": v, "restriction": r, "body": b}


def exists(v, r, b):
    return {"kind": "exists", "var": v, "restriction": r, "body": b}


def implies(l, r):
    return {"kind": "implies", "left": l, "right": r}


def conj(*args):
    return {"kind": "and", "args": list(args)}


def disj(*args):
    return {"kind": "or", "args": list(args)}


# ---- desugar가 서명보다 먼저다 (운영 전제의 결박) -----------------------

def test_desugar_runs_before_signature():
    """설탕형과 탈설탕형은 같은 서명 — 이 불변성은 파이프라인이
    desugar를 먼저 돌리기 때문에 성립한다(V2 모듈 단독 계약과 동일 논거)."""
    sugared = forall("x", P("dog", "x"), P("bark", "x"))
    desugared = forall("x", TRUE, implies(P("dog", "x"), P("bark", "x")))
    assert (pipe.scope_signature_v2_for_case("FOLIO-t1p0", sugared)
            == pipe.scope_signature_v2_for_case("FOLIO-t1p0", desugared))


# ---- source dispatch는 fail-closed --------------------------------------

def test_unknown_case_prefix_is_refused():
    with pytest.raises(ValueError):
        pipe.scope_signature_v2_for_case("MRS-x", P("p", "x"))


# ---- PMB granularity 다리는 유지된다 (D-32 "나머지는 현행 유지") --------

def test_pmb_scaffold_bridge_is_retained():
    """사건 비계(∃e + 동사 synset + ROLE)가 있는 oracle과 참여자만 있는
    subject가 같은 서명이어야 한다 — V1 전처리를 빼면 이것이 깨진다."""
    with_event = exists("x", TRUE, conj(
        P("person.n.01", "x"),
        exists("e", TRUE, conj(P("walk.v.01", "e"), P("Agent", "e", "x")))))
    without_event = exists("x", TRUE, P("person.n.01", "x"))
    assert (pipe.scope_signature_v2_for_case("PMB-t", with_event)
            == pipe.scope_signature_v2_for_case("PMB-t", without_event))


# ---- V2 의미론이 실제로 채점한다 (V1 evaluate로의 회귀를 적발) -----------

def test_lexical_and_or_identity_is_not_scored_v2_semantics():
    """scope 없는 국소에서 and/or 정체는 V2가 버리는 차원이다. V1 전면
    비교(evaluate)로 배선하면 이 둘이 달라져 이 테스트가 실패한다 —
    배선 회귀의 판별자."""
    a = forall("x", TRUE, implies(conj(P("p", "x"), P("q", "x")), P("r", "x")))
    b = forall("x", TRUE, implies(disj(P("p", "x"), P("q", "x")), P("r", "x")))
    assert (pipe.scope_signature_v2_for_case("FOLIO-t1p0", a)
            == pipe.scope_signature_v2_for_case("FOLIO-t1p0", b))


def test_scope_differences_are_still_scored():
    a = forall("x", P("dog", "x"), P("bark", "x"))
    b = exists("x", P("dog", "x"), P("bark", "x"))
    assert (pipe.scope_signature_v2_for_case("FOLIO-t1p0", a)
            != pipe.scope_signature_v2_for_case("FOLIO-t1p0", b))


# ---- 채점 결과 어휘 = cg_evaluate.evaluate -------------------------------

ORACLE = forall("x", P("dog", "x"), P("bark", "x"))


def test_non_dict_predicted_is_error():
    assert pipe.evaluate_scope_v2("FOLIO-t1p0", "no", ORACLE)["result"] == "error"


def test_invalid_oracle_is_unscorable():
    bad = {"kind": "forall", "var": "x"}  # 필수 필드 결손
    out = pipe.evaluate_scope_v2("FOLIO-t1p0", ORACLE, bad)
    assert out["result"] == "unscorable"


def test_invalid_predicted_is_a_subject_failure():
    bad = {"kind": "forall", "var": "x"}
    out = pipe.evaluate_scope_v2("FOLIO-t1p0", bad, ORACLE)
    assert out["result"] == "fail"
    assert "structural_validity" in out["mismatch_dimensions"]


def test_matching_signatures_pass():
    out = pipe.evaluate_scope_v2("FOLIO-t1p0", copy.deepcopy(ORACLE), ORACLE)
    assert out["result"] == "pass"
    assert out["mismatch_dimensions"] == []


def test_mismatching_signatures_fail_with_the_v2_dimension():
    pred = exists("x", P("dog", "x"), P("bark", "x"))
    out = pipe.evaluate_scope_v2("FOLIO-t1p0", pred, ORACLE)
    assert out["result"] == "fail"
    assert out["mismatch_dimensions"] == ["scope_signature_v2"]


# ---- 순수성·해시 가능성 ---------------------------------------------------

def test_pipeline_does_not_mutate_its_input():
    ir = forall("x", P("dog", "x"), conj(P("bark", "x"), P("loud", "x")))
    snapshot = copy.deepcopy(ir)
    pipe.scope_signature_v2_for_case("FOLIO-t1p0", ir)
    pipe.evaluate_scope_v2("FOLIO-t1p0", ir, copy.deepcopy(ir))
    assert ir == snapshot


def test_signature_jsonable_is_deterministic_and_hashable():
    from conceptgate.cg_identity import canonical_sha256
    sig = pipe.scope_signature_v2_for_case("FOLIO-t1p0", ORACLE)
    j = pipe.signature_jsonable(sig)
    assert isinstance(j, list)
    h1 = canonical_sha256(j)
    h2 = canonical_sha256(pipe.signature_jsonable(
        pipe.scope_signature_v2_for_case("FOLIO-t1p0", copy.deepcopy(ORACLE))))
    assert h1 == h2 and len(h1) == 64
