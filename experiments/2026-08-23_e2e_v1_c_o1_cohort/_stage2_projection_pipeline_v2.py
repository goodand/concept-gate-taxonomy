"""V2 채점 파이프라인 — V1 전처리 + V2 signature의 합성 (D-E2E-v1-32 B.8 §1).

## 왜 합성인가

D-32 B.8 §1은 V2의 델타를 **#1(제한식 opaque 붕괴)과 #5(and/or 정체
미채점)뿐**이라 명시했고 "나머지는 현행 유지"다. '나머지'에는 V1의 source별
granularity 다리 — PMB scaffold ∃ 제거(F3: 사건 매개 oracle과 직접 관계
subject의 대칭화), 국소 관용구 정규화(D-27), desugar — 가 포함된다. 그것을
버리면 PMB 채점이 구조적으로 전부 실패한다(oracle에만 사건 층이 있으므로).

따라서 V2 채점 = `V1 전처리(project_scope_for_case) → V2 signature` 합성이고,
이 합성은 runner에 흩어두지 않고 이 hash-pin 가능한 계약 모듈에 둔다(V4가
계약 모듈만 pin하는 규율의 연장 — runner는 회계, 계약은 pin).

V2 모듈(`_stage2_scope_projection_v2`) 자신은 V1을 import하지 않는다(그
파일의 자기 선언). 이 합성을 만드는 것은 이 모듈의 책임이다.

## 채점 결과 어휘 = cg_evaluate.evaluate

`_stage2_score`가 "pass"를 세므로 결과 어휘를 바꾸면 조용히 0점이 된다.
경계 의미론도 evaluate를 그대로 따른다: oracle 불량 = unscorable(평가기
결함), predicted 불량 = fail structural_validity(subject 결함). 투영 중
예외(ProjectionQualificationFail 등)는 fail-closed로 error 처리한다.
"""
from __future__ import annotations

from typing import Any

from conceptgate import cg_ir

from _stage2_scope_projection import project_scope_for_case
from _stage2_scope_projection_v2 import signature as _signature_v2

PRE_PROJECTION_PROFILE_ID = "O1_SCOPE_PROJECTION_V1"
PROJECTION_PROFILE_ID = "O1_SCOPE_PROJECTION_V2"


def scope_signature_v2_for_case(case_id: str, formula: dict) -> tuple:
    """V1 전처리(desugar·관용구 정규화·source별 granularity 다리) 후 V2 signature.

    순수 함수: 입력 무변이.
    """
    return _signature_v2(project_scope_for_case(case_id, formula))


def signature_jsonable(sig: Any) -> Any:
    """중첩 tuple을 중첩 list로 재귀 변환 (canonical_sha256 해시용)."""
    if isinstance(sig, tuple):
        return [signature_jsonable(x) for x in sig]
    if isinstance(sig, list):
        return [signature_jsonable(x) for x in sig]
    return sig


def evaluate_scope_v2(case_id: str, predicted: Any, oracle_ir: Any) -> dict:
    """`cg_evaluate.evaluate`와 동일한 경계 의미론으로 V2 signature를 비교한다."""
    if not isinstance(predicted, dict) or not isinstance(oracle_ir, dict):
        return {
            "result": "error",
            "reason": f"Both inputs must be dicts; got "
                      f"{type(predicted).__name__} and {type(oracle_ir).__name__}",
        }

    oracle_errors = cg_ir.validate_formula(oracle_ir)
    if oracle_errors:
        return {
            "result": "unscorable",
            "reason": f"Oracle formula is invalid: {oracle_errors}",
        }

    predicted_errors = cg_ir.validate_formula(predicted)
    if predicted_errors:
        return {
            "result": "fail",
            "mismatch_dimensions": ["structural_validity"],
            "reason": f"Predicted formula is malformed: {predicted_errors}",
        }

    try:
        predicted_sig = scope_signature_v2_for_case(case_id, predicted)
        oracle_sig = scope_signature_v2_for_case(case_id, oracle_ir)
    except Exception as exc:
        return {"result": "error", "reason": f"{type(exc).__name__}: {exc}"}

    if predicted_sig == oracle_sig:
        return {"result": "pass", "mismatch_dimensions": []}
    return {"result": "fail", "mismatch_dimensions": ["scope_signature_v2"]}
