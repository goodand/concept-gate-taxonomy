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
    "relation.is_a": ObligationSpec(
        DeciderKind.GATE, Assurance.RULE_CHECKED,
        "concept_gate_v7.ConceptGate.ontoclean_meta_gate", Verdict.UNKNOWN),
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


def results_from_pipeline(serialized: Dict[str, Any]) -> List[ObligationResult]:
    """_serialize_pipeline_output 산출물 → 관계 obligation 결과 4종.

    gates는 이미 실행됐다 — 이 어댑터는 그 판정을 ObligationResult로
    옮길 뿐 재검사하지 않는다. 입력은 직렬화된 dict(실행 결합 없음).

    필드 부재는 '위반 0건'과 다르다: composition_issues/anti_patterns 키가
    아예 없으면 gate가 실행되지 않은 것 → UNKNOWN(on_unavailable). 빈
    배열(키 존재)만 PASS다 — '검사 안 됨'이 '통과'로 세탁되지 않게 한다.
    """
    comp_ran = "composition_issues" in serialized
    by_kind: Dict[str, List[Dict[str, Any]]] = {}
    for i in (serialized.get("composition_issues") or []):
        by_kind.setdefault(i.get("kind", ""), []).append(i)

    def _gate(obligation: str, kind: str, gate_name: str) -> ObligationResult:
        if not comp_ran:
            return ObligationResult(
                obligation, Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.GATE,
                reason=f"{gate_name} 미실행 (composition_issues 필드 부재)")
        hits = by_kind.get(kind, [])
        if hits:
            return ObligationResult(
                obligation, Verdict.FAIL, Assurance.RULE_CHECKED,
                DeciderKind.GATE, evidence=f"composition_issues[kind={kind}]",
                reason="; ".join(h.get("detail", "") for h in hits[:3]))
        return ObligationResult(
            obligation, Verdict.PASS, Assurance.RULE_CHECKED,
            DeciderKind.GATE, evidence=f"{gate_name}: {kind} 위반 0건")

    if "anti_patterns" not in serialized:
        ufo = ObligationResult(
            "ufo.no_antipattern", Verdict.UNKNOWN, Assurance.PROPOSED,
            DeciderKind.GATE,
            reason="UFOAntiPatternGate 미실행 (anti_patterns 필드 부재)")
    elif serialized["anti_patterns"]:
        ufo = ObligationResult(
            "ufo.no_antipattern", Verdict.FAIL, Assurance.RULE_CHECKED,
            DeciderKind.GATE, evidence="anti_patterns",
            reason=f"UFO 안티패턴 {len(serialized['anti_patterns'])}건 감지")
    else:
        ufo = ObligationResult(
            "ufo.no_antipattern", Verdict.PASS, Assurance.RULE_CHECKED,
            DeciderKind.GATE, evidence="UFOAntiPatternGate: 0건")
    return [
        _gate("relation.antisymmetry", "antisymmetry", "CompositionGate"),
        _gate("relation.acyclicity", "cycle", "CompositionGate"),
        _gate("relation.isa_hasa_exclusivity", "isa_hasa_conflict",
              "CompositionGate"),
        ufo,
    ]


def results_from_normalizer(resp: Dict[str, Any]) -> List[ObligationResult]:
    """assemble_concepts 성공 응답 → source.* obligation 2종.

    registry에 등록됐으나 아직 발급되지 않던 source.snapshot_hash·
    source.span_evidence를 실제 MCP 응답에 노출한다. cg_normalizer가 이미
    snapshot integrity(_snapshot_integrity_errors)와 span+quote+hash
    (_span_evidence)를 결정론적으로 검사했다 — 이 어댑터는 그 결과를 옮길 뿐.

    실패 응답은 stage 오류가 이미 원인을 표면화하므로 certificate를 만들지
    않는다(빈 목록). span 미제공(unverified) claim이 하나라도 있으면
    source.span_evidence는 PASS가 아니라 UNKNOWN이다.
    """
    if not resp.get("ok"):
        return []
    results: List[ObligationResult] = []
    source = resp.get("source") or {}
    if source.get("sha256"):
        results.append(ObligationResult(
            "source.snapshot_hash", Verdict.PASS, Assurance.RULE_CHECKED,
            DeciderKind.LOCAL_RULE,
            evidence=f"snapshot sha256 재계산 일치: {source['sha256'][:12]}"))
    else:
        results.append(ObligationResult(
            "source.snapshot_hash", Verdict.UNKNOWN, Assurance.PROPOSED,
            DeciderKind.LOCAL_RULE, reason="snapshot 미제공 — hash 판정 대상 없음"))
    claims = resp.get("claims") or []
    unverified = [c for c in claims
                  if c.get("verification_status") != "source_span_verified"]
    if claims and not unverified:
        results.append(ObligationResult(
            "source.span_evidence", Verdict.PASS, Assurance.RULE_CHECKED,
            DeciderKind.LOCAL_RULE,
            evidence=f"claim {len(claims)}건 span+quote+hash 검증"))
    else:
        results.append(ObligationResult(
            "source.span_evidence", Verdict.UNKNOWN, Assurance.PROPOSED,
            DeciderKind.LOCAL_RULE,
            reason=f"span 미검증 claim {len(unverified)}건 (evidence_span 부재)"))
    return results


def results_from_isa(dag: Dict[str, List[str]],
                     ontoclean_names: Iterable[str]) -> List[ObligationResult]:
    """DAG의 is-a 간선 → relation.is_a obligation (M1: 첫 semantic obligation).

    is-a 반례 4종(instance-of/role/phase/part-of 아닌가) 중 role·phase·rigidity·
    dependence는 OntoCleanMetaGate가 결정론적으로 검사하고 위반 시 간선을 차단한다
    (part-of masquerade는 Relation Discrimination Gate가 상류에서 차단). 따라서
    *형성된* 간선은 두 경우뿐이다:

    - 양 끝이 OntoClean 메타데이터를 지님 → 게이트가 반례를 검사·통과시킴
      → RULE_CHECKED PASS.
    - 메타데이터 부재 → 게이트가 판정 불가(on_unavailable) → UNKNOWN. 간선은
      feature-label 집합 포함으로만 형성됐고 instance/role/phase masquerade가
      결정론적으로 배제되지 않았다 — 이 is-a는 LLM 제안일 뿐이다.

    이것이 최초의 certificate-only 신호다: status PASS·lint 0·anti_patterns 0인데
    relation.is_a는 UNKNOWN. UNKNOWN은 집계에서 PASS를 막으므로 '판정 안 된 is-a'가
    '통과'로 세탁되지 않는다.
    """
    names = set(ontoclean_names)
    edges = [(p, c) for p, children in dag.items() for c in children]
    if not edges:
        return []  # is-a 주장 없음 — 판정 대상 없음 (공허)
    grounded = {(p, c) for (p, c) in edges if p in names and c in names}
    ungrounded = [e for e in edges if e not in grounded]
    if ungrounded:
        detail = ", ".join(f"{p}→{c}" for p, c in sorted(ungrounded)[:5])
        return [ObligationResult(
            "relation.is_a", Verdict.UNKNOWN, Assurance.PROPOSED,
            DeciderKind.GATE,
            reason=f"OntoClean 메타데이터 부재로 반례(instance/role/phase) 미배제 "
                   f"— LLM 제안 is-a: {detail}")]
    detail = ", ".join(f"{p}→{c}" for p, c in sorted(grounded)[:5])
    return [ObligationResult(
        "relation.is_a", Verdict.PASS, Assurance.RULE_CHECKED,
        DeciderKind.GATE,
        evidence=f"OntoCleanMetaGate 검증 간선: {detail}")]


def results_from_classification(resp: Dict[str, Any]) -> List[ObligationResult]:
    """classify_owl 응답 → owl.consistent 결과 1종.

    ok=False(reasoner 미가용 등)면 decider가 실행되지 않은 것 —
    spec.on_unavailable(UNKNOWN)을 기록한다. UNKNOWN은 집계에서
    PASS를 차단하므로 '판정 안 됨'이 '통과'로 세탁되지 않는다.
    """
    spec = OBLIGATION_REGISTRY["owl.consistent"]
    if not resp.get("ok"):
        codes = [e.get("code") for e in resp.get("errors", [])]
        return [ObligationResult(
            "owl.consistent", spec.on_unavailable, Assurance.PROPOSED,
            DeciderKind.REASONER,
            reason=f"decider 미실행: {codes or 'unknown'}")]
    unsat = resp.get("unsatisfiable") or []
    if unsat:
        return [ObligationResult(
            "owl.consistent", Verdict.FAIL, Assurance.REASONER_PROVED,
            DeciderKind.REASONER, evidence="unsatisfiable",
            reason=f"unsatisfiable classes: {unsat[:5]}")]
    return [ObligationResult(
        "owl.consistent", Verdict.PASS, Assurance.REASONER_PROVED,
        DeciderKind.REASONER, evidence="HermiT: unsatisfiable 0건")]


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
