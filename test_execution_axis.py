"""W2 (a)-refined — semantic verdict × execution status 두 축의 테스트."""
from __future__ import annotations

import pytest

from conceptgate.cg_obligations import (
    Assurance, DeciderKind, ExecutionStatus, ObligationResult, Verdict,
    aggregate, aggregate_execution, certify, reasoner_requirement,
    results_from_classification,
)


def test_execution_defaults_to_ok_everywhere():
    """가산성: 기존 생산자는 전부 '검사기가 돌았다' 경우 — 기본 OK."""
    r = ObligationResult("relation.acyclicity", Verdict.FAIL,
                         Assurance.RULE_CHECKED, DeciderKind.GATE,
                         evidence="cycle", reason="A->B->A")
    assert r.execution is ExecutionStatus.OK


def test_semantic_fail_with_execution_ok_is_the_inconsistency_case():
    """판정문 §4의 예 1: ontology inconsistent → semantic FAIL, execution OK.
    확정 위반은 도구 문제가 아니다."""
    resp = {"ok": True, "unsatisfiable": ["돌체"]}
    [r] = results_from_classification(resp)
    assert r.verdict is Verdict.FAIL
    assert r.execution is ExecutionStatus.OK


def test_optional_dependency_absence_is_unavailable(monkeypatch):
    """판정문 §4의 예 2: optional 배포에서 의존성 부재 → UNKNOWN + UNAVAILABLE.
    로컬 개발(owlready2 의도적 미설치)의 기존 의미론 보존."""
    monkeypatch.delenv("CONCEPTGATE_REASONER_REQUIREMENT", raising=False)
    resp = {"ok": False, "errors": [{"code": "OWLREADY2_UNAVAILABLE"}]}
    [r] = results_from_classification(resp)
    assert r.verdict is Verdict.UNKNOWN
    assert r.execution is ExecutionStatus.UNAVAILABLE


def test_required_dependency_absence_is_error(monkeypatch):
    """docker 배포(JRE 보장)에서 같은 부재는 unexpectedly missing → ERROR.
    판정문 V2가 지적한 Dockerfile 사실과 정합."""
    monkeypatch.setenv("CONCEPTGATE_REASONER_REQUIREMENT", "required")
    resp = {"ok": False,
            "errors": [{"code": "REASONER_DEPENDENCY_UNAVAILABLE"}]}
    [r] = results_from_classification(resp)
    assert r.verdict is Verdict.UNKNOWN
    assert r.execution is ExecutionStatus.ERROR


def test_runtime_failure_is_error_regardless_of_requirement(monkeypatch):
    """판정문 §4의 예 3: crash/timeout은 배포 선언과 무관하게 ERROR."""
    monkeypatch.delenv("CONCEPTGATE_REASONER_REQUIREMENT", raising=False)
    resp = {"ok": False, "errors": [{"code": "REASONER_RUNTIME_FAILURE"}]}
    [r] = results_from_classification(resp)
    assert r.verdict is Verdict.UNKNOWN
    assert r.execution is ExecutionStatus.ERROR


def test_malformed_requirement_env_falls_back_to_optional(monkeypatch):
    """음성: 오타 env가 required로 읽히면 로컬 게이트가 전부 ERROR로 물든다 —
    enum 밖 값은 optional로 강등, 조용한 강등이 안전한 유일한 방향."""
    monkeypatch.setenv("CONCEPTGATE_REASONER_REQUIREMENT", "requird")
    assert reasoner_requirement() == "optional"


def test_certify_reports_both_axes_without_information_loss():
    """판정문 §5: FAIL과 '동시에 reasoner가 죽었다'를 함께 보고 —
    priority enum이 아니라 product state."""
    bad = ObligationResult("relation.acyclicity", Verdict.FAIL,
                           Assurance.RULE_CHECKED, DeciderKind.GATE,
                           evidence="cycle", reason="A->B->A")
    dead = ObligationResult("owl.consistent", Verdict.UNKNOWN,
                            Assurance.PROPOSED, DeciderKind.REASONER,
                            reason="crash", execution=ExecutionStatus.ERROR)
    out = certify([bad, dead])
    assert out["verdict"] == "fail"          # semantic 축
    assert out["execution"] == "error"       # 실행 축 — 정보 미소실
    assert aggregate([bad, dead]) is Verdict.FAIL
    assert aggregate_execution([bad, dead]) is ExecutionStatus.ERROR
