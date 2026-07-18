#!/usr/bin/env python3
"""cg_obligations — 의미 판정의 권한 경계 (verdict/assurance 분리).

설계 원칙 (expansion_strategy_review_20260717 blocker 1 해소):
  1. verdict(판정 결과)와 assurance(보증 수준)를 분리한다.
     "무엇으로 판정했나"를 잃으면 LLM 판단이 검증 라벨을 달고 통과한다
     (결정론 세탁). cg_normalizer의 confidence ≠ verification_status
     분리와 같은 철학.
  2. decider 종류별 발행 가능한 assurance 상한을 고정한다.
     LLM은 SOURCE_ANCHORED까지 — RULE_CHECKED 이상은 결정론 검사기·
     reasoner·사람만 발행한다.
  3. registry에는 현재 코드베이스에 decider가 실존하는 obligation만
     등록한다 (YAGNI). 신규 semantic obligation은 decider 구현과 함께.

의존성: stdlib only. 실행 결합 없음 — 각 decider(cg_normalizer,
CompositionGate, HermiT)는 기존 위치에서 실행되고, 이 모듈은 결과를
ObligationResult로 검증·집계하는 계약만 제공한다.

보류 계층(warm JVM, invalidation, R2 등)과 도입 트리거:
docs/obligation_layer_roadmap.md — 트리거 충족 전 구현 금지.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, Dict, Iterable, List, Tuple

SCHEMA_VERSION = "0.1.0"
VERIFIER = {"name": "cg_obligations", "version": SCHEMA_VERSION}


class Verdict(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"


class Assurance(IntEnum):
    PROPOSED = 1
    SOURCE_ANCHORED = 2
    RULE_CHECKED = 3
    REASONER_PROVED = 4
    HUMAN_APPROVED = 5


class DeciderKind(Enum):
    LLM = "llm"
    LOCAL_RULE = "local_rule"
    GATE = "gate"
    REASONER = "reasoner"
    HUMAN = "human"


# 결정론 세탁 차단의 핵심: decider가 자기 권한 밖의 보증을 발행할 수 없다.
MAX_ASSURANCE: Dict[DeciderKind, Assurance] = {
    DeciderKind.LLM: Assurance.SOURCE_ANCHORED,
    DeciderKind.LOCAL_RULE: Assurance.RULE_CHECKED,
    DeciderKind.GATE: Assurance.RULE_CHECKED,
    DeciderKind.REASONER: Assurance.REASONER_PROVED,
    DeciderKind.HUMAN: Assurance.HUMAN_APPROVED,
}


@dataclass(frozen=True)
class ObligationSpec:
    decider: DeciderKind
    min_assurance: Assurance   # PASS 인정에 필요한 최소 보증
    handler: str               # 실제 판정 코드 위치 (dotted path, 문서용)
    on_unavailable: Verdict    # decider 실행 불가 시 기록할 verdict


# 현재 코드베이스에 decider가 실존하는 obligation만. handler는 실명 대조 완료.
OBLIGATION_REGISTRY: Dict[str, ObligationSpec] = {
    "source.snapshot_hash": ObligationSpec(
        DeciderKind.LOCAL_RULE, Assurance.RULE_CHECKED,
        "cg_normalizer._snapshot_integrity_errors", Verdict.FAIL),
    "source.span_evidence": ObligationSpec(
        DeciderKind.LOCAL_RULE, Assurance.RULE_CHECKED,
        "cg_normalizer._span_evidence", Verdict.FAIL),
    "relation.antisymmetry": ObligationSpec(
        DeciderKind.GATE, Assurance.RULE_CHECKED,
        "concept_gate_v7.CompositionGate", Verdict.FAIL),
    "relation.acyclicity": ObligationSpec(
        DeciderKind.GATE, Assurance.RULE_CHECKED,
        "concept_gate_v7.CompositionGate", Verdict.FAIL),
    "relation.isa_hasa_exclusivity": ObligationSpec(
        DeciderKind.GATE, Assurance.RULE_CHECKED,
        "concept_gate_v7.CompositionGate", Verdict.FAIL),
    "ufo.no_antipattern": ObligationSpec(
        DeciderKind.GATE, Assurance.RULE_CHECKED,
        "concept_gate_v7.UFOAntiPatternGate", Verdict.UNKNOWN),
    "owl.consistent": ObligationSpec(
        DeciderKind.REASONER, Assurance.REASONER_PROVED,
        "cg_owl.classify", Verdict.UNKNOWN),
}


@dataclass(frozen=True)
class ObligationResult:
    obligation: str
    verdict: Verdict
    assurance: Assurance
    decider: DeciderKind
    evidence: str = ""
    reason: str = ""
    depends_on: Tuple[str, ...] = ()  # provenance만 — invalidation은 로드맵 트리거 대기


def validate_result(result: ObligationResult) -> List[Dict[str, Any]]:
    """단일 결과의 권한·보증 불변조건 검사. 위반 목록 반환 (빈 목록 = 유효)."""
    spec = OBLIGATION_REGISTRY.get(result.obligation)
    if spec is None:
        return [{"code": "UNKNOWN_OBLIGATION", "detail": result.obligation}]
    errors: List[Dict[str, Any]] = []
    if result.decider is not spec.decider:
        errors.append({"code": "DECIDER_MISMATCH",
                       "detail": {"expected": spec.decider.value,
                                  "got": result.decider.value}})
    cap = MAX_ASSURANCE[result.decider]
    if result.assurance > cap:
        errors.append({"code": "ASSURANCE_EXCEEDS_DECIDER_CAP",
                       "detail": {"decider": result.decider.value,
                                  "cap": cap.name,
                                  "claimed": result.assurance.name}})
    if result.verdict is Verdict.PASS:
        if result.assurance < spec.min_assurance:
            errors.append({"code": "INSUFFICIENT_ASSURANCE",
                           "detail": {"required": spec.min_assurance.name,
                                      "got": result.assurance.name}})
        if not result.evidence:
            errors.append({"code": "MISSING_EVIDENCE",
                           "detail": "PASS는 evidence 필수 (근거 없는 판정 폐기)"})
    return errors


def aggregate(results: Iterable[ObligationResult]) -> Verdict:
    """ALL 결합: 하나라도 FAIL → FAIL, 전부 PASS → PASS, 그 외 → UNKNOWN."""
    verdicts = {r.verdict for r in results}
    if not verdicts:
        return Verdict.UNKNOWN
    if Verdict.FAIL in verdicts:
        return Verdict.FAIL
    if verdicts == {Verdict.PASS}:
        return Verdict.PASS
    return Verdict.UNKNOWN


def certify(results: List[ObligationResult]) -> Dict[str, Any]:
    """검증 + 집계 단일 진입점. 불변조건 위반이 하나라도 있으면 FAIL."""
    errors: List[Dict[str, Any]] = []
    for r in results:
        for e in validate_result(r):
            errors.append({"obligation": r.obligation, **e})
    verdict = Verdict.FAIL if errors else aggregate(results)
    return {
        "ok": verdict is Verdict.PASS,
        "verdict": verdict.value,
        "errors": errors,
        "results": [
            {"obligation": r.obligation, "verdict": r.verdict.value,
             "assurance": r.assurance.name, "decider": r.decider.value,
             "evidence": r.evidence, "reason": r.reason,
             "depends_on": list(r.depends_on)}
            for r in results
        ],
        "verifier": VERIFIER,
    }
