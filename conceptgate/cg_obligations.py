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

import hashlib
import json
import unicodedata

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

from . import cg_identity
from . import cg_signing

SCHEMA_VERSION = "0.1.0"
VERIFIER = {"name": "cg_obligations", "version": SCHEMA_VERSION}


class Verdict(Enum):
    PASS = "pass"
    FAIL = "fail"
    UNKNOWN = "unknown"
    # D1 (Refine/Verify 지시 I8, 2026-08-22): 판단 근거 부족(UNKNOWN)과
    # 실행기/도구 실패(ERROR)를 구별한다. 예: ontology inconsistent → FAIL,
    # HermiT timeout/crash → ERROR. 이전에는 on_unavailable이 둘을 UNKNOWN
    # 하나로 흡수해 "검사가 판단하지 못했다"와 "검사가 돌지 못했다"가
    # 구별 불가였다. 루트 게이트 어휘와의 매핑: ERROR ≈ BLOCKED
    # ("시작조차 못 함") — 단 게이트 BLOCKED는 exit code 미기여인 반면
    # 여기 ERROR는 집계에서 PASS를 차단한다(아래 aggregate).
    # oracle 평가 프로토콜 v1의 UNSCORABLE과의 관계는 G32(어휘 불일치,
    # 설계 담당 확인 대기) 해소 전까지 매핑하지 않는다.
    ERROR = "error"


class ExecutionStatus(Enum):
    """W2 (설계 리뷰 2026-08-22, (a)-refined): 실행 축 — semantic verdict와
    직교한다. verdict는 "명제가 어떤가", execution은 "검사기가 돌았는가".

      OK          — 검사기가 정상 실행됨 (verdict가 무엇이든)
      UNAVAILABLE — 배포 프로파일상 optional인 의존성이 없어 못 돎 (예상됨)
      ERROR       — required 의존성 부재 또는 실행 중 crash/timeout (예상 밖)

    product state의 존재 이유: 단일 enum에 합치면 "ontology inconsistent
    (semantic=FAIL, execution=OK)"와 "HermiT crash(semantic=UNKNOWN,
    execution=ERROR)"의 원인 정보가 섞인다 — 판정문 §4·§5.
    """
    OK = "ok"
    UNAVAILABLE = "unavailable"
    ERROR = "error"


# 배포 프로파일이 reasoner를 요구하는가. optional(기본)이면 의존성 부재는
# UNAVAILABLE(예상된 미가용 — 로컬 개발·게이트의 BLOCKED 의미론과 일치),
# required면 같은 부재가 ERROR다(docker 배포는 Dockerfile이 JRE를 보장하므로
# 부재 = unexpectedly missing — 판정문 §4의 V2 지적). Dockerfile이
# CONCEPTGATE_REASONER_REQUIREMENT=required를 선언한다.
def reasoner_requirement() -> str:
    import os
    value = os.environ.get("CONCEPTGATE_REASONER_REQUIREMENT", "optional")
    return value if value in ("optional", "required") else "optional"


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
    # D-v0 (2026-08-22): 결정론적 어휘 결박. decider가 이 모듈 안에 실존한다
    # (results_from_claim_anchoring) — registry YAGNI 원칙 충족.
    "claim.evidence_anchoring": ObligationSpec(
        DeciderKind.LOCAL_RULE, Assurance.RULE_CHECKED,
        "cg_obligations.results_from_claim_anchoring", Verdict.UNKNOWN),
    # 2026-09-01: 끊긴 간선. anchoring 은 caller 가 준 evidence 안에서만
    # 검사하므로 그 evidence 가 문서와 무관해도 PASS 가 났다(실측). 이 의무는
    # 인용 본문이 **문서 snapshot 에서 유도됐는가**를 판정한다.
    "claim.evidence_provenance": ObligationSpec(
        DeciderKind.LOCAL_RULE, Assurance.RULE_CHECKED,
        "cg_normalizer.resolve_cited_evidence", Verdict.UNKNOWN),
    # 2026-09-01: E2.2.1 hidden contract A("같은 feature 이름은 전역 type
    # 일치")의 **판정 절반** — 유도(사전 명시)는 M1 certificate 의 일이지만
    # 판정(사후)은 결정론이다. wrong_direction 55% 를 만든 그 불변조건이
    # LLM decider 없이 검사된다는 것이 채널 분석의 핵심 발견(S4).
    "graph.feature_type_consistency": ObligationSpec(
        DeciderKind.LOCAL_RULE, Assurance.RULE_CHECKED,
        "cg_obligations.results_from_feature_type_consistency", Verdict.UNKNOWN),
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
    # D5 (지시 §4.2/§16): 이 판정이 어느 graph revision에 대한 것인가.
    # None = revision 개념이 없는 호출자(기존 MCP 응답 경로) — 유효하다.
    # 값이 있으면 소비자는 자기 snapshot revision과 대조해 stale을 거부할
    # 수 있다(stale_obligations 참조).
    graph_revision: "str | int | None" = None
    # W2: 실행 축. 기본 OK — 기존 생산자 전부가 "검사기가 돌았다" 경우이므로
    # 가산적이다. 미가용/실패 생산자만 명시 설정한다.
    execution: ExecutionStatus = ExecutionStatus.OK
    # SURVEY §14.2 대안 B (2026-08-31): 이 판정이 어느 불변식을 지목하는가.
    # FQN `<문서군>:<글자><번호>`(docs/IDENTIFIER_REGISTER.md:25) — 맨 번호는
    # 발행자마다 뜻이 달라 무엇을 어겼는지 말하지 못한다(directive:I3 ≠
    # mechspec:I3). None = 지목 없는 기존 생산자 19곳 — graph_revision과 같은
    # 선례로 가산 도입한다. validate_result가 FQN 형태·등록된 문서군인지만
    # 검사하고, 불변식이 실제로 위반됐는지는 검사하지 않는다(다른 층의 일).
    invariant: "str | None" = None


# docs/IDENTIFIER_REGISTER.md §계열 표의 문서군 이름, 글자 `I`(불변식) 행만.
# 손으로 베끼지 않는다 — 손으로 베낀 목록은 등록부가 바뀌면 갈라진다
# (G199·G213, 등록부 서두). test_identifier_register.py의 _rows()는 테스트
# 파일이라 production 코드가 import하지 않고(테스트 파일 import는 배포
# 패키지에 테스트 트리 의존을 만든다), 같은 표 파싱을 여기 독립적으로
# 반복한다(열 개수·구분자 계약은 그 파일과 동일 — 등록부 헤더가 정의).
#
# 등록부는 docs/ 아래에 있고 Dockerfile은 conceptgate/·vendor/만 이미지에
# 복사한다(docs/는 배포물 밖, 실측: Dockerfile:18-19) — 배포 환경에는 이
# 파일이 없다. 그 경우 빈 frozenset으로 내려간다: fail-closed(모든 FQN이
# INVARIANT_UNKNOWN_GROUP)이지 fail-open이 아니다. 가산 필드라 기존 생산자
# 19곳 중 누구도 invariant를 채우지 않으므로 이 저하는 지금 아무 실행 경로에도
# 영향을 주지 않는다.
# 문서군 목록은 등록부에서 **생성된** 상수를 쓴다 — 런타임 파싱을 지웠다.
# production 이 사람이 유지하는 마크다운에 의존했고, `Dockerfile` 이 `docs/`
# 를 COPY 하지 않아 배포에서 무력했다. 생성기는
# `scripts/gen_identifier_groups.py`, 일치는
# `test_identifier_groups_sync.py` 가 강제한다.
from conceptgate._identifier_groups import INVARIANT_GROUPS


def validate_result(result: ObligationResult,
                    registry: Dict[str, ObligationSpec] | None = None
                    ) -> List[Dict[str, Any]]:
    """단일 결과의 권한·보증 불변조건 검사. 위반 목록 반환 (빈 목록 = 유효).

    `registry`는 이 저장소 밖의 의무 집합을 위한 seam이다(기본값은 전역
    OBLIGATION_REGISTRY). 여기 있는 불변조건 — 특히 `PASS는 evidence 필수` —
    는 도메인과 무관하게 유효한데, 그것을 쓰려면 의무 이름이 전역 레지스트리에
    있어야 했다. 실험용 의무 10개를 이 도메인 레지스트리에 등록하면 개념 게이트
    레지스트리가 오염되고, 규칙을 실험 쪽에 다시 구현하면 검증된 기제가 두 벌이
    된다. 인자 하나가 둘 다 피한다.
    """
    registry = OBLIGATION_REGISTRY if registry is None else registry
    spec = registry.get(result.obligation)
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
    if result.verdict is Verdict.ERROR and not result.reason:
        # 이유 없는 ERROR는 "왜 못 돌았나"를 잃는다 — 재실행 판단 불가.
        errors.append({"code": "ERROR_WITHOUT_REASON",
                       "detail": "ERROR는 reason 필수 (도구 실패의 원인 기록)"})
    if result.verdict is Verdict.PASS:
        if result.assurance < spec.min_assurance:
            errors.append({"code": "INSUFFICIENT_ASSURANCE",
                           "detail": {"required": spec.min_assurance.name,
                                      "got": result.assurance.name}})
        if not result.evidence:
            errors.append({"code": "MISSING_EVIDENCE",
                           "detail": "PASS는 evidence 필수 (근거 없는 판정 폐기)"})
    if result.invariant is not None:
        # 빈 문자열은 None(지목 안 함)도 FQN(지목함)도 아니다 — "지목했다고
        # 적혀 있는데 아무것도 안 가리키는" 상태를 폐기한다. 콜론 없는 맨
        # 번호(예: `directive:I3`에서 접두를 뗀 표기)도 마찬가지 — 세
        # 발행자(directive/mechspec/h1a-scope)에 걸쳐 무엇을 어겼는지 말하지
        # 못한다(등록부 §계열 표, `I` 행 COLLIDES).
        if not result.invariant or ":" not in result.invariant:
            errors.append({"code": "INVARIANT_NOT_FULLY_QUALIFIED",
                           "detail": result.invariant})
        else:
            group, _, _rest = result.invariant.partition(":")
            if group not in INVARIANT_GROUPS:
                errors.append({"code": "INVARIANT_UNKNOWN_GROUP",
                               "detail": {"invariant": result.invariant,
                                          "known_groups": sorted(INVARIANT_GROUPS)}})
    return errors


def aggregate(results: Iterable[ObligationResult]) -> Verdict:
    """ALL 결합: FAIL > ERROR > (전부 PASS) > UNKNOWN.

    FAIL이 ERROR보다 우선하는 이유: 확정된 위반은 도구 고장보다 강한
    사실이다 — 어떤 검사기가 죽었더라도 다른 검사기가 잡은 위반은
    사라지지 않는다. ERROR가 PASS를 차단하는 이유: 돌지 못한 검사를
    통과로 세탁하지 않는다(I8; 게이트 BLOCKED와 같은 정신).
    """
    verdicts = {r.verdict for r in results}
    if not verdicts:
        return Verdict.UNKNOWN
    if Verdict.FAIL in verdicts:
        return Verdict.FAIL
    if Verdict.ERROR in verdicts:
        return Verdict.ERROR
    if verdicts == {Verdict.PASS}:
        return Verdict.PASS
    return Verdict.UNKNOWN


_EXECUTION_SEVERITY = {ExecutionStatus.OK: 0,
                       ExecutionStatus.UNAVAILABLE: 1,
                       ExecutionStatus.ERROR: 2}


def aggregate_execution(results: Iterable[ObligationResult]) -> ExecutionStatus:
    """실행 축의 worst-of. 판정문 §5: aggregate가 FAIL을 돌려줘도 "동시에
    reasoner 하나가 죽었다"는 정보를 버리지 않는다 — 두 축을 나란히 반환."""
    worst = ExecutionStatus.OK
    for r in results:
        if _EXECUTION_SEVERITY[r.execution] > _EXECUTION_SEVERITY[worst]:
            worst = r.execution
    return worst


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
        # W2 매핑: 의존성 부재(예상 여부는 배포 선언이 정함) vs 실행 실패.
        dep_absent = any(c in ("OWLREADY2_UNAVAILABLE",
                               "REASONER_DEPENDENCY_UNAVAILABLE")
                         for c in codes)
        runtime_failure = any(c == "REASONER_RUNTIME_FAILURE" for c in codes)
        if runtime_failure:
            execution = ExecutionStatus.ERROR
        elif dep_absent:
            execution = (ExecutionStatus.ERROR
                         if reasoner_requirement() == "required"
                         else ExecutionStatus.UNAVAILABLE)
        else:
            execution = ExecutionStatus.OK  # 입력 오류 등 — 검사기 탓 아님
        return [ObligationResult(
            "owl.consistent", spec.on_unavailable, Assurance.PROPOSED,
            DeciderKind.REASONER,
            reason=f"decider 미실행: {codes or 'unknown'}",
            execution=execution)]
    unsat = resp.get("unsatisfiable") or []
    if unsat:
        return [ObligationResult(
            "owl.consistent", Verdict.FAIL, Assurance.REASONER_PROVED,
            DeciderKind.REASONER, evidence="unsatisfiable",
            reason=f"unsatisfiable classes: {unsat[:5]}")]
    return [ObligationResult(
        "owl.consistent", Verdict.PASS, Assurance.REASONER_PROVED,
        DeciderKind.REASONER, evidence="HermiT: unsatisfiable 0건")]


def stale_obligations(results: Iterable[ObligationResult],
                      current_revision: "str | int") -> List[str]:
    """D5의 소비 절반: 현재 revision과 다른 revision에 대한 판정 목록.

    지시 §4.2 — Refine은 stale obligation을 적용하지 않고 STALE_OBLIGATION
    으로 무시하거나 재검증을 요청한다. revision이 None인 판정(revision 개념이
    없는 경로)은 stale로 세지 않는다 — 없는 결박을 위반으로 읽으면 기존
    MCP 응답 경로 전부가 거짓 stale이 된다.
    """
    return [r.obligation for r in results
            if r.graph_revision is not None
            and r.graph_revision != current_revision]


def certification_cycle(results: Iterable[ObligationResult]) -> List[str]:
    """D3 (지시 I10/§24): certification dependency의 순환 검출.

    semantic graph의 순환은 유효할 수 있다(A related_to B related_to A).
    금지되는 것은 **인증 의존**의 순환 — "C는 D 때문에 인증, D는 C가
    인증됐기 때문에 유도"다. depends_on이 그 의존 edge다.

    stdlib graphlib.TopologicalSorter를 쓴다 (Ponytail 3단: stdlib가 풀면
    stdlib). 반환: 순환에 참여하는 obligation 이름 목록(없으면 빈 목록).
    presented 집합 밖을 가리키는 depends_on은 edge가 되지 않는다 — 외부
    노드의 순환 여부는 이 호출이 판정할 수 있는 범위 밖이다.
    """
    presented = {r.obligation for r in results}
    graph = {r.obligation: {d for d in r.depends_on if d in presented}
             for r in results}
    try:
        # list()가 load-bearing: static_order()는 generator라 소비하지 않으면
        # CycleError가 영영 발생하지 않는다. 이 함수의 첫 판이 정확히 그
        # 공허한 형태였고(P1), 음성 테스트가 잡았다 (2026-08-22 실측).
        list(TopologicalSorter(graph).static_order())
        return []
    except CycleError as exc:
        # exc.args[1]은 순환 경로 (첫/끝 반복 포함)
        return list(dict.fromkeys(exc.args[1]))


# ---------------------------------------------------------------- D7 ------
def _assert_no_required_allowed_na_overlap(profile: "CertificationProfile") -> None:
    """같은 이유로 별도 함수로 뽑는다 — 게이트가 `_assert_` prefix로 스캔한다
    (`conceptgate/cg_identity._assert_known_fingerprint_kind`와 같은 이유)."""
    overlap = set(profile.required) & set(profile.allowed_na)
    if overlap:
        raise ValueError(
            f"profile {profile.profile_id!r}: {sorted(overlap)} 이 required와 "
            f"allowed_na에 동시에 있다 — 같은 검사가 필수이면서 면제일 수 없다")


@dataclass(frozen=True)
class CertificationProfile:
    """claim 종류별 인증 요건 (지시 §15). 새 top-level module이 아니라
    Verify가 읽는 선언이다.

    required: 전부 PASS여야 인증. allowed_na: UNKNOWN이어도 인증을 막지
    않는 검사(그 claim 종류에 적용 불가한 축). required와 allowed_na에 둘 다
    있는 이름은 모순이므로 생성 시 거부한다.
    """
    profile_id: str
    applies_to_claim_kind: str
    required: Tuple[str, ...]
    allowed_na: Tuple[str, ...] = ()

    def __post_init__(self):
        _assert_no_required_allowed_na_overlap(self)


# 최초 legacy relation claim profile (지시 §31-E가 요구한 최소 1개).
# H1a/E2.4가 실제로 검사해 온 축을 그대로 옮겼다 — 새 요건을 발명하지 않는다.
LEGACY_RELATION_PROFILE = CertificationProfile(
    profile_id="legacy_relation_claim_v0",
    applies_to_claim_kind="relation_assertion",
    required=(
        "source.snapshot_hash",      # 출처 무결성 (기존 decider 실재)
        "source.span_evidence",      # span+quote+hash (기존 decider 실재)
        "claim.evidence_anchoring",  # 이번에 추가된 결정론 검사 (아래)
        "relation.antisymmetry",
        "relation.acyclicity",
        "relation.isa_hasa_exclusivity",
    ),
    allowed_na=(
        # 지시 §15의 예와 동일: 단순 관계 주장엔 적용 불가한 축
        "quantifier_scope",
        "modal_scope",
    ),
)


# D-38 ㄱ (2026-09-01): `NEW_PROFILE_IDENTITY_PREFERRED`. Q38 이 물은 변경
# (`claim.evidence_provenance` 를 required 에 넣는 것)을 **새 identity 안에서**
# 한다. `_v0` 는 제자리 재정의하지 않는다 — 판정 원문: "이미 배포된 profile의
# 계약 의미를 보존해야 한다면 `_v0`를 제자리에서 재정의해서는 안 되고, 새
# profile identity가 필요하다."
#
# **기본값은 바꾸지 않는다.** 배포된 도구의 기본 profile 을 이것으로 돌리면
# 기존 호출자의 관측 가능한 출력이 바뀌고(certified_claim_ids 축소), 판정 ㄷ가
# 그것을 "제품 계약 변경에 별도 backward-compatibility 규칙이 필요하다는
# 근거"로 지목했다. 그 판단은 미결이다(D-38 수신 검증 V8).
RELATION_CLAIM_V1_PROFILE = CertificationProfile(
    profile_id="relation_claim_v1",
    applies_to_claim_kind="relation_assertion",
    required=LEGACY_RELATION_PROFILE.required + ("claim.evidence_provenance",),
    allowed_na=LEGACY_RELATION_PROFILE.allowed_na,
)


def profile_commitment(profile: CertificationProfile) -> Dict[str, Any]:
    """이 profile 이 **무엇을 요구했는가**를 재구성 가능한 형태로 굳힌다.

    D-38 ㄴ: `profile_id` 만으로는 그 이름이 무엇을 요구했는지 재구성할 수
    없으므로 판정이 더 강한 형태(`profile_id` + `required_hash`)를 권했다.
    정의는 판정이 주지 않았으므로 여기서 못박는다(설계 적대검증 채택 #3 —
    정의 없이 "구제 경로 있음"으로 두면 나중에 재구성이 불가능해진다):

        required_hash = sha256(canonical_json({profile_id, sorted(required)}))

    **정렬한다.** 나열 순서가 바뀌었다는 이유로 해시가 달라지면 무관한 편집이
    인증서 불일치를 만들고, 그렇게 우는 게이트는 사람이 끈다.
    """
    payload = json.dumps({"profile_id": profile.profile_id,
                          "required": sorted(profile.required)},
                         sort_keys=True, ensure_ascii=False,
                         separators=(",", ":"))
    return {"profile_id": profile.profile_id,
            "required_hash": hashlib.sha256(payload.encode("utf-8")).hexdigest()}


def is_certified(profile: CertificationProfile,
                 check_verdicts: Dict[str, Verdict]) -> bool:
    """claim is certified iff profile.required checks가 전부 PASS (지시 §15).

    없는 검사는 PASS가 아니다 — dict.get의 기본값이 UNKNOWN인 이유.
    '검사 안 됨'이 '통과'로 세탁되지 않는다는 이 모듈의 기존 원칙 그대로.
    """
    return all(check_verdicts.get(name, Verdict.UNKNOWN) is Verdict.PASS
               for name in profile.required)


def certified_projection(claims: List[Dict[str, Any]],
                         verdicts_by_claim: Dict[str, Dict[str, Verdict]],
                         profile: CertificationProfile) -> List[Dict[str, Any]]:
    """Certified Projection (지시 §6/I6) — view이지 DB가 아니다.

    asserted graph를 수정하지 않는다: 입력 claim dict를 변경 없이 통과시키고,
    projection 멤버십만 결정한다. lifecycle 갱신은 호출자(Refine 소유)의
    몫이다 — 여기서 dict를 고치면 Verify쪽 코드가 graph writer가 된다(I3).
    """
    return [c for c in claims
            if is_certified(profile, verdicts_by_claim.get(c["id"], {}))]


def results_from_claim_anchoring(
        claims: List[Dict[str, Any]],
        evidence_texts: Dict[str, str]) -> List[ObligationResult]:
    """claim.evidence_anchoring — 결정론적 어휘 결박 검사.

    **이것은 semantic support 판정이 아니다.** 검사하는 명제: claim이 인용한
    evidence 본문에 claim의 concept과 feature 문자열이 실제로 등장한다.
    등장하지 않으면 UNKNOWN — FAIL이 아닌 이유는, 어휘 부재가 의미적
    비지지를 증명하지 않기 때문이다(동의어·조응). 의미 수준 support는
    LLM decider(assurance 상한 SOURCE_ANCHORED)의 몫이고, 그 decider가
    실제로 구현될 때 registry에 등록된다(YAGNI 원칙 유지).
    """
    out: List[ObligationResult] = []
    for c in claims:
        ids = c.get("cited_evidence_ids", [])
        raw = [(e, evidence_texts.get(e)) for e in ids]
        # 신뢰 경계 타입 검증. `t in body` 는 body 가 str 이 아니어도 **동작한다** —
        # dict 면 키만 보고 list 면 원소 완전일치로 의미가 바뀌므로, 값이 주장을
        # 정면으로 부정하는 dict 가 PASS + RULE_CHECKED + "문자 등장" 을 받고
        # certify 까지 ok:True 로 통과했다(2026-08-31 실측). 죽는 편(bytes·int)이
        # 오히려 안전했다 — 조용한 오판을 막는 것이 이 검사의 목적이다.
        illtyped = [e for e, t in raw if t is not None and not isinstance(t, str)]
        if illtyped:
            out.append(ObligationResult(
                "claim.evidence_anchoring", Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: evidence 본문이 문자열이 아니다 {illtyped} — "
                       f"문자 결박을 주장할 수 없음(타입 오류를 '빈 본문'으로 "
                       f"위장하지 않는다)",
                graph_revision=c.get("graph_revision")))
            continue
        bad_terms = [k for k in ("concept", "feature")
                     if c.get(k) is not None and not isinstance(c.get(k, ""), str)]
        if bad_terms:
            out.append(ObligationResult(
                "claim.evidence_anchoring", Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: claim 어휘가 문자열이 아니다 {bad_terms} — "
                       f"문자 결박을 주장할 수 없음",
                graph_revision=c.get("graph_revision")))
            continue
        cited = [t for _, t in raw if t]
        if not cited:
            # 매달린 인용(키 부재 = 그래프 무결성 결함 후보)과 빈 본문(수리
            # 대기 = 정상 중간 상태)은 다른 사건이다 — 접으면 Refine 이 무엇을
            # 공급해야 하는지 알 수 없다 (동료 검토 MAJOR-3, 2026-08-31).
            dangling = [e for e in ids if e not in evidence_texts]
            hollow = [e for e in ids if e in evidence_texts]
            parts = ([f"매달린 인용 {dangling}"] if dangling else []) + \
                    ([f"빈 본문 {hollow}"] if hollow else []) or ["인용 없음"]
            out.append(ObligationResult(
                "claim.evidence_anchoring", Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: 결박 판정 대상 없음 — " + " · ".join(parts),
                graph_revision=c.get("graph_revision")))
            continue
        terms = [t for t in (c.get("concept", ""), c.get("feature", "")) if t]
        if not terms:
            # 어휘가 없으면 검사가 없다 — 여기서 PASS 를 내면 "아무것도 검사
            # 하지 않은 RULE_CHECKED" 가 된다 (공허한 가드 P1 형태, 동료 검토
            # MAJOR-1). 검사 부재는 통과가 아니라 판정 불가다.
            out.append(ObligationResult(
                "claim.evidence_anchoring", Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: 검사할 어휘 없음 — concept·feature 둘 다 비어 "
                       f"있어 결박을 주장할 수 없음",
                graph_revision=c.get("graph_revision")))
            continue
        missing = [t for t in terms if not any(t in body for body in cited)]
        if missing:
            out.append(ObligationResult(
                "claim.evidence_anchoring", Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: {missing} 가 인용 evidence에 문자적으로 "
                       f"부재 — 어휘 부재는 의미적 비지지의 증명이 아니므로 "
                       f"FAIL이 아니라 UNKNOWN",
                graph_revision=c.get("graph_revision")))
        else:
            out.append(ObligationResult(
                "claim.evidence_anchoring", Verdict.PASS, Assurance.RULE_CHECKED,
                DeciderKind.LOCAL_RULE,
                evidence=f"{c['id']}: concept·feature가 인용 evidence "
                         f"{c.get('cited_evidence_ids')}에 문자 등장",
                graph_revision=c.get("graph_revision")))
    return out


def results_from_cited_evidence(
        resp: Dict[str, Any],
        claims: List[Dict[str, Any]]) -> List[ObligationResult]:
    """claim.evidence_provenance — 인용 본문이 **문서에서 유도됐는가**.

    입력은 `cg_normalizer.resolve_cited_evidence` 의 직렬화 응답이다(실행
    결합 없음 — 이 모듈의 규약). 그 함수가 문서 snapshot 에서 span 을 해소
    하고, 여기서는 그 결과를 판정으로 옮긴다.

    **왜 UNKNOWN 이 아니라 FAIL 인가.** 어휘 부재는 의미적 비지지의 증명이
    아니어서 `claim.evidence_anchoring` 은 UNKNOWN 을 낸다. 그러나 선언된
    span 에서 인용문이 **일치하지 않는다**는 것은 부재가 아니라 **불일치의
    적극적 증거**다 — `_span_evidence` 가 `QUOTE_MISMATCH` 를 오류로 내는
    것과 같은 이유이고, `source.span_evidence` 의 `on_unavailable` 도 FAIL 이다.

    인용을 **선언하지 않은** claim 은 판정 대상이 아니다(UNKNOWN) — 인용이
    없다는 것과 인용이 위조라는 것은 다른 사건이다.
    """
    resolved = set((resp.get("texts") or {}))
    failed_ids = {
        (e.get("detail") or {}).get("citation_id")
        for e in (resp.get("errors") or [])
    } - {None}
    out: List[ObligationResult] = []
    for c in claims:
        cited = list(c.get("cited_evidence_ids", []))
        rev = c.get("graph_revision")
        if not cited:
            out.append(ObligationResult(
                "claim.evidence_provenance", Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: 인용 선언 없음 — 유도 여부를 판정할 대상이 없음",
                graph_revision=rev))
            continue
        bad = [e for e in cited if e in failed_ids]
        missing = [e for e in cited if e not in resolved and e not in failed_ids]
        if bad:
            out.append(ObligationResult(
                "claim.evidence_provenance", Verdict.FAIL, Assurance.RULE_CHECKED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: 인용 {bad} 이 문서 snapshot 에서 해소되지 "
                       f"않음 — 인용 본문이 문서에서 유도되지 않았다",
                graph_revision=rev))
        elif missing:
            out.append(ObligationResult(
                "claim.evidence_provenance", Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: 인용 {missing} 에 대한 해소 시도 기록이 "
                       f"없음 — 판정 보류(부재와 미확인을 가른다)",
                graph_revision=rev))
        else:
            out.append(ObligationResult(
                "claim.evidence_provenance", Verdict.PASS, Assurance.RULE_CHECKED,
                DeciderKind.LOCAL_RULE,
                evidence=f"{c['id']}: 인용 {cited} 이 문서 "
                         f"{resp.get('source_sha256', '')[:16]} 의 선언된 span "
                         f"에서 유도됨",
                graph_revision=rev))
    return out


def results_from_feature_type_consistency(
        concepts: Any) -> List[ObligationResult]:
    """graph.feature_type_consistency — 같은 feature 이름의 전역 type 일치.

    E2.2.1 이 실증한 hidden contract A 의 판정 절반이다. 원문(roadmap):
    같은 feature 이름이 concept 마다 다른 type 을 달고 있어도 모델은
    "의미론적으로 정당하다"고 합리화했다(wrong_direction 55%). 이 검사는
    그 위반을 산출 그래프 위에서 결정론으로 드러낸다 — 옳은 repair 를
    만들어내지는 못한다(그것은 certificate 의 자연어 불변조건, A_ONLY 20/20).

    판정:
    - 같은 이름에 서로 다른 비어있지 않은 type 공존 → **FAIL**
      (적극적 불일치 — provenance 의 QUOTE_MISMATCH 와 같은 논리)
    - 형태가 깨진 항목 존재 & 위반 미검출 → UNKNOWN (파싱 불가를 통과로
      세탁하지 않는다; 단 **검출된 위반은 깨진 항목보다 우선**한다 —
      파싱 실패가 적극적 증거의 도피구가 되면 안 된다)
    - 비교 가능한(typed) 출현 0 → UNKNOWN (없는 검사는 PASS 가 아니다)
    - 그 외 → PASS
    """
    seen: Dict[str, Dict[str, List[str]]] = {}   # feature -> type -> [concept...]
    unparsed = 0
    typed = 0
    if not isinstance(concepts, list):
        return [ObligationResult(
            "graph.feature_type_consistency", Verdict.UNKNOWN,
            Assurance.PROPOSED, DeciderKind.LOCAL_RULE,
            reason="concepts 가 리스트가 아니다 — 형태를 파싱할 수 없어 판정 불가")]
    for c in concepts:
        if not isinstance(c, dict) or not isinstance(c.get("features"), list):
            unparsed += 1
            continue
        cname = str(c.get("name", "?"))
        for f in c["features"]:
            if not isinstance(f, dict):
                unparsed += 1
                continue
            fname, ftype = f.get("feature"), f.get("type")
            # type 은 **enum 일 수 있다** — 이 저장소의 정본 자료구조
            # `NormalizedFeature.type` 이 `FeatureType` enum 이고, 코퍼스 전수
            # (2026-09-01, JSON 125개)에서 지배 형태가 그 유래다(1,231건).
            # `isinstance(str)` 만 요구하면 실제 그래프에서 **조용히 아무것도
            # 검사하지 않는다** — Edge case More READ 가 잡은 결함이고,
            # 빈 어휘가 PASS 를 받던 MAJOR-1 과 같은 부류다.
            ftype = getattr(ftype, "value", ftype)
            if not (isinstance(fname, str) and fname
                    and isinstance(ftype, str) and ftype):
                continue                     # type 없는 출현은 비교에 안 들어간다
            # **비교 키 정규화 — 새 정책이 아니라 두 층의 정책 불일치 시정.**
            # `cg_normalizer` 는 concept name·label 에 이미 NFC 를 적용한다
            # (7곳, 실측). 이 층이 원문 그대로 비교하면 같은 글자의 다른
            # 코드점(NFC/NFD)·후행 공백·대소문자 차이로 **위반이 우회**되고
            # (실측: 충돌인데 PASS), 반대로 type 표기 변이가 **거짓 FAIL** 을
            # 만든다(실측: structural_composition vs "structural composition").
            # 한 원인이라 한 줄로 닫힌다 — 적대검증이 "배선의 선행조건"으로
            # 지목한 것이고, 정규화 없이 배선하면 거짓 FAIL 이 인증서에 실려
            # 되돌려지고 그 되돌림이 곧 P21 경로다.
            fkey = unicodedata.normalize("NFC", fname).strip().casefold()
            tkey = unicodedata.normalize("NFC", ftype).strip().casefold().replace(" ", "_")
            if not (fkey and tkey):
                continue
            typed += 1
            seen.setdefault(fkey, {}).setdefault(tkey, []).append(cname)
    conflicts = {name: types for name, types in seen.items() if len(types) > 1}
    if conflicts:
        parts = []
        for name in sorted(conflicts):
            per_type = " vs ".join(
                f"{t}({', '.join(sorted(cs))})"
                for t, cs in sorted(conflicts[name].items()))
            parts.append(f"'{name}': {per_type}")
        return [ObligationResult(
            "graph.feature_type_consistency", Verdict.FAIL,
            Assurance.RULE_CHECKED, DeciderKind.LOCAL_RULE,
            reason="같은 feature 이름에 서로 다른 type 이 공존 — "
                   + " · ".join(parts)
                   + (f" (파싱 불가 항목 {unparsed}건 별도)" if unparsed else ""))]
    if unparsed:
        return [ObligationResult(
            "graph.feature_type_consistency", Verdict.UNKNOWN,
            Assurance.PROPOSED, DeciderKind.LOCAL_RULE,
            reason=f"파싱 불가 항목 {unparsed}건 — 전역 일치를 판정할 수 없다"
                   f"(통과로 세탁하지 않는다)")]
    if typed == 0:
        return [ObligationResult(
            "graph.feature_type_consistency", Verdict.UNKNOWN,
            Assurance.PROPOSED, DeciderKind.LOCAL_RULE,
            reason="typed feature 출현 0 — 검사 대상 없음(없는 검사는 PASS 가 아니다)")]
    return [ObligationResult(
        "graph.feature_type_consistency", Verdict.PASS,
        Assurance.RULE_CHECKED, DeciderKind.LOCAL_RULE,
        evidence=f"feature 이름 {len(seen)}종 · typed 출현 {typed}건 전역 일치")]


def certify(results: List[ObligationResult],
            registry: Dict[str, ObligationSpec] | None = None) -> Dict[str, Any]:
    """검증 + 집계 단일 진입점. 불변조건 위반이 하나라도 있으면 FAIL.

    `registry`는 validate_result와 같은 seam이다 — 전달하지 않으면 전역
    레지스트리를 쓴다.
    """
    errors: List[Dict[str, Any]] = []
    for r in results:
        for e in validate_result(r, registry):
            errors.append({"obligation": r.obligation, **e})
    cycle = certification_cycle(results)
    if cycle:
        # I10: 인증 의존 순환은 반드시 무효 — "C는 D 때문, D는 C 때문"이
        # 통과하면 두 주장이 서로를 인증하는 자기부양이 된다.
        errors.append({"obligation": cycle[0],
                       "code": "CERTIFICATION_CYCLE",
                       "detail": {"cycle": cycle}})
    verdict = Verdict.FAIL if errors else aggregate(results)
    return {
        "ok": verdict is Verdict.PASS,
        "verdict": verdict.value,
        # W2: 실행 축을 나란히 — verdict가 원인 정보를 삼키지 않게.
        "execution": aggregate_execution(results).value,
        "errors": errors,
        "results": [
            {"obligation": r.obligation, "verdict": r.verdict.value,
             "assurance": r.assurance.name, "decider": r.decider.value,
             "evidence": r.evidence, "reason": r.reason,
             "depends_on": list(r.depends_on),
             "graph_revision": r.graph_revision,
             "execution": r.execution.value}
            for r in results
        ],
        "verifier": VERIFIER,
    }


# ================================================== v0 MCP 배선 (2026-08-22) --
# W1(배선 감사)의 해소: 아래 함수가 v0 primitive 사슬(anchoring → certify →
# projection + fingerprint + stale)을 하나의 호출로 묶고, server.py의 신규
# MCP tool `certify_claims`가 이것에 얇게 위임한다. 로직이 여기(순수 함수)에
# 있는 이유: fastmcp 없는 로컬 환경에서도 테스트 가능해야 한다
# (test_cg_obligations.py의 OPTIONAL_DEPS 패턴과 같은 제약).

_VERDICT_BY_VALUE = {v.value: v for v in Verdict}

# ------------------------------------------- W5: 서명된 obligation certificate
# 설계 리뷰(2026-08-22) required_fix의 구현. 부품은 전부 재사용:
# canonical/HMAC/키는 cg_identity(← codex _receipt.py verbatim), 결박 어휘는
# 이 모듈의 fingerprint·graph_revision, 유효성은 validate_result.

CERTIFICATE_DOMAIN = "obligation-certificate"
# v0 → v1 (2026-08-31): 서명 본체에 invariant FQN이 추가되며 몸체 형태가
# 바뀌었다. 검증부는 지금 이 문자열을 대조하지 않지만(:665-690 부근에
# schema 검사 없음), 올리지 않으면 나중에 v0/v1 문서를 구별할 근거 자체가
# 없어진다 — 이름 자체를 못박는다(느슨한 endswith 단언은 이것을 보증 못함).
# v1 → v2 (2026-09-01, D-38 ㄴ): 서명 본체에 profile commitment 가 추가되며
# 몸체 형태가 또 바뀌었다. 판정 원문 — "현재 obligation_certificate_v1의 서명
# payload 정의 자체가 바뀐다면, 기존 v1과 새로운 payload를 동일 schema라고
# 부르는 것은 위험하다." 수신 검증 V5 가 08-31 v0→v1 과 같은 종류의 변경임을
# 실측했다.
# v2 → v3 (2026-09-03): 서명을 HMAC→Ed25519, issuer 에 scheme·key_id 추가 —
# D-38 "서명 payload shape 이 바뀌면 bump" 이행, W5 권고 봉투(`{scheme,
# key_id, signature}`) 채택. 배포면(Render)이 발급한 인증서를 로컬 cg_store
# 가 검증 키 불일치로 거부한 사고(D16: 대칭 키 영수증은 자기동일성과 검증
# 불가 사이만 오간다)를 비대칭 서명 + 공개키 리소스 노출로 닫는다.
CERTIFICATE_SCHEMA = "obligation_certificate_v3"


class CertificateError(Exception):
    """certificate의 authenticity/결박/유효성 위반 — fail-closed 거부."""


def issue_claim_certificate(claim: Dict[str, Any],
                            results: List[ObligationResult],
                            *, issuer_tool: str,
                            key_path=None,
                            profile: CertificationProfile | None = None
                            ) -> Dict[str, Any]:
    """claim 하나에 대한 게이트 결과를 서명된 certificate로 발급.

    발급 주체는 **게이트를 실제로 실행한 서버측 코드**다 — MCP client가
    자기 결과를 발급하는 경로는 없다(키가 host-only라 접근 불가).
    subject_fingerprint와 graph_revision이 몸체에 들어가 서명되므로,
    다른 claim·다른 revision으로의 재사용이 서명 검증 없이도 아니라
    **서명 검증으로** 막힌다.
    """
    seed = cg_identity.load_or_create_key(
        key_path or cg_identity.default_key_path())
    pub = cg_signing.public_key_bytes(seed)
    body = {
        "schema": CERTIFICATE_SCHEMA,
        # W5 수정(2026-09-03): scheme·key_id 추가 -- 검증자가 "이 인증서가
        # 주장하는 키"와 "내가 검증에 쓴 키"를 독립적으로 대조할 수 있어야
        # key_id 가 주석이 아니라 결박의 일부가 된다(아래
        # _assert_certificate_grants_verdicts 의 key_id 대조 참조).
        "issuer": {"tool": issuer_tool, "verifier": VERIFIER,
                   "scheme": "ed25519", "key_id": cg_signing.key_id(pub)},
        # D-38 ㄴ: 어떤 인증 계약이 적용됐는지가 **서명 아래**에 있어야 한다.
        # 없으면 동일 results[] 를 가진 두 문서를 verifier 가 구별하지 못한다 —
        # 수신 검증 V3 이 그것을 실측했다(두 profile 의 payload 가 바이트 동일).
        # 형태는 조건부로 갈리지 않는다: 주장 안 한 호출도 같은 키를 내고 None 이다.
        "profile": profile_commitment(profile) if profile is not None else None,
        "subject_fingerprint": cg_identity.claim_fingerprint(claim),
        "graph_revision": claim.get("graph_revision"),
        "results": [
            {"obligation": r.obligation, "verdict": r.verdict.value,
             "assurance": r.assurance.name, "decider": r.decider.value,
             "evidence": r.evidence, "reason": r.reason,
             "graph_revision": r.graph_revision,
             "invariant": r.invariant}
            for r in results],
    }
    return {**body, "signature": cg_signing.sign(
        body, seed, domain=CERTIFICATE_DOMAIN)}


def _key_source_name(key_path) -> str:
    """진단용 키 **파일명**. 전체 경로가 아닌 이유는 위 분기 주석에 있다."""
    return Path(key_path or cg_identity.default_key_path()).name


def _assert_certificate_grants_verdicts(
        cert: Dict[str, Any], claim: Dict[str, Any], public_key: bytes,
        registry: Dict[str, ObligationSpec] | None = None,
        expected_profile: "CertificationProfile | None" = None,
        key_source: str | None = None
) -> Dict[str, Verdict]:
    """authenticity → issuer key_id → schema → 결박 → 계약(profile) →
    유효성 순서로 검사하고, 통과 시에만 certificate가 나르는
    {obligation: Verdict}를 돌려준다. `public_key`는 검증에 쓸 Ed25519
    공개키 raw 32바이트다(cg_signing.public_key_bytes의 출력) — 개인키/seed
    가 아니다. 비대칭 서명(2026-09-03)으로, 발급자와 검증자가 서로 다른
    호스트여도(다른 키 파일) 공개키 바이트만 가지고 이 함수에 도달한다.

    순서가 계약이다: 서명이 깨진 문서의 '결박 오류'를 먼저 보고하면
    공격자에게 조작 진행도를 알려주는 oracle이 된다 — authenticity 먼저.

    **key_id 를 서명 다음, schema 보다 먼저 읽는다 (2026-09-03, 적대검증
    #4 채택).** `issuer.key_id`는 지금까지 아무도 읽지 않았다(판독 0곳) —
    같은 seed 로 key_id 만 바꿔 재서명하면 서명은 유효하므로, 변조와
    구별하려면 검증부가 key_id 를 **독립적으로** 대조해야 한다.

    **schema·profile 을 여기서 읽는다 (2026-09-01, D-38 구현 적대검증 채택).**
    v0→v1 때도 v1→v2 때도 "검증부는 지금 이 문자열을 대조하지 않는다"는
    주석을 남겼다 — 같은 주석을 세 번째로 쓰는 대신 대조를 넣는다. profile
    commitment 는 서명 아래 있었지만 아무도 읽지 않아서, `_v0` 에만 commit
    한 인증서와 `profile: None` 인증서가 `_v1` 검증에서 인증됐다(실측).
    서명 아래에 넣는 이유는 verifier 가 **읽기** 때문이다 — 읽지 않으면
    필드는 주석과 같은 지위다.
    """
    if not cg_signing.verify(cert, public_key, domain=CERTIFICATE_DOMAIN):
        # **원인을 두 가설로 병렬 제시한다** (2026-09-01). 이 분기가 나는
        # 원인은 넷이고 전부 같은 문구를 냈다(실측): 서명 부재 · 서명 변조 ·
        # 본문 변조 · **키 불일치(문서는 정당)**. 넷째만 성격이 다른데
        # 초판은 "손으로 쓴 문서"를 단정해서 E2E 조립 시 원인을 못 찾게
        # 했다 — 선례 `2c8df63`("오류 메시지가 자기 키를 말하게")의 형태로
        # 검증부가 **읽은 것**(키 파일)을 말하게 한다.
        #
        # oracle 규율(아래 docstring)은 위반하지 않는다: 발원 커밋이 oracle 을
        # "how far a forgery got" 으로 좁게 정의하고, 키 출처는 **문서의
        # 함수가 아니라 호스트 설정의 함수**여서 어떤 위조 문서에도 같은
        # 값이다 — 조작 진행도를 전달하지 않는다. `path.name` 만 쓴다:
        # `str(exc)` 가 MCP client 로 나가므로(`server.py`) 절대경로를
        # 흘리지 않기 위해서다(`cg_identity` 가 이미 그 선례).
        where = f" (verified with key file {key_source!r})" if key_source else ""
        raise CertificateError(
            "certificate signature is absent or does not verify -- either a "
            "hand-written or edited-after-signing document is refused, or the "
            "issuer signed with a different key than this verifier holds"
            f"{where}; if the document is legitimate, pass the issuer's "
            "key_path (host-only key; the caller cannot manufacture this)")
    presented_key_id = (cert.get("issuer") or {}).get("key_id")
    verifying_key_id = cg_signing.key_id(public_key)
    if presented_key_id != verifying_key_id:
        raise CertificateError(
            f"certificate issuer key_id {presented_key_id!r} != verifying "
            f"key_id {verifying_key_id!r} -- the signature is valid but "
            f"claims a different key than it was actually signed with; "
            f"issuer.key_id is checked independently of the signature "
            f"(a resign with the same key cannot launder a tampered key_id)")
    if cert.get("schema") != CERTIFICATE_SCHEMA:
        raise CertificateError(
            f"certificate schema {cert.get('schema')!r} != "
            f"{CERTIFICATE_SCHEMA!r} -- a document from an older signing "
            f"contract is not silently re-interpreted under the new one "
            f"(fail-closed; reissue under the current schema)")
    if cert.get("subject_fingerprint") != cg_identity.claim_fingerprint(claim):
        raise CertificateError(
            f"certificate subject {cert.get('subject_fingerprint')!r} does "
            f"not match this claim's fingerprint -- a certificate issued for "
            f"another claim cannot be replayed here (subject binding)")
    if cert.get("graph_revision") != claim.get("graph_revision"):
        raise CertificateError(
            f"certificate revision {cert.get('graph_revision')!r} != claim "
            f"revision {claim.get('graph_revision')!r} -- stale certificate "
            f"(revision binding)")
    if expected_profile is not None:
        committed = cert.get("profile")
        expected = profile_commitment(expected_profile)
        if committed != expected:
            raise CertificateError(
                f"certificate profile commitment {committed!r} != expected "
                f"{expected!r} -- a certificate committed to another "
                f"certification contract (or to none) cannot grant verdicts "
                f"under this one. None is not a wildcard: an uncommitted "
                f"certificate passing every profile is exactly the bypass "
                f"this field exists to close")
    granted: Dict[str, Verdict] = {}
    for row in cert.get("results", []):
        try:
            rebuilt = ObligationResult(
                row["obligation"], _VERDICT_BY_VALUE[row["verdict"]],
                Assurance[row["assurance"]], DeciderKind(row["decider"]),
                evidence=row.get("evidence", ""),
                reason=row.get("reason", ""),
                graph_revision=row.get("graph_revision"),
                invariant=row.get("invariant"))
        except (KeyError, ValueError) as exc:
            raise CertificateError(
                f"certificate result row is not well-formed: {exc!r}") from exc
        violations = validate_result(rebuilt, registry)
        if violations:
            raise CertificateError(
                f"signed result violates obligation invariants "
                f"{[v['code'] for v in violations]} -- a signature proves "
                f"origin, not authority: "
                f"{rebuilt.obligation} by {rebuilt.decider.value}")
        granted[rebuilt.obligation] = rebuilt.verdict
    return granted



def _assert_prior_verdicts_are_well_formed(
        prior_verdicts: Dict[str, Dict[str, str]] | None) -> None:
    """신뢰 경계 검증 (hard safety): 호출자가 준 사전 verdict 문자열이
    Verdict enum 밖이면 거부한다. 모르는 문자열을 UNKNOWN으로 눙치면
    'pss' 같은 오타가 조용히 인증 탈락 사유가 되어 디버깅 불가가 되고,
    반대로 관대하게 PASS로 읽으면 세탁이 된다 — 거부가 유일하게 안전하다."""
    if prior_verdicts is None:
        return
    for claim_id, checks in prior_verdicts.items():
        for check, value in checks.items():
            if value not in _VERDICT_BY_VALUE:
                raise ValueError(
                    f"claim {claim_id!r} check {check!r}: verdict 문자열 "
                    f"{value!r}은 {sorted(_VERDICT_BY_VALUE)} 밖이다 — "
                    f"이전 도구 응답의 verdict 값을 그대로 전달하라")


def certify_relation_claims(
        claims: List[Dict[str, Any]],
        evidence_texts: Dict[str, str],
        prior_verdicts: Dict[str, Dict[str, str]] | None = None,
        prior_certificates: List[Dict[str, Any]] | None = None,
        profile: CertificationProfile = LEGACY_RELATION_PROFILE,
        current_revision: "str | int | None" = None,
        key_path=None,
        issuer_public_key: bytes | None = None) -> Dict[str, Any]:
    """v0 인증 사슬의 단일 진입점 (지시 §25 step 3~6의 배선형).

    이 함수가 **하지 않는 것**을 먼저: 게이트를 재실행하지 않는다.
    `relation.*`·`source.*` verdict는 이전 도구 응답(run_pipeline /
    assemble_concepts의 obligations certificate)에서 **호출자가 가져와**
    `prior_verdicts`로 전달한다 — 같은 검사를 두 번 구현하면 검증된 기제가
    두 벌이 된다(registry seam의 docstring과 같은 근거). 이 함수가 직접
    계산하는 것은 `claim.evidence_anchoring` 하나다.

    따라서 `prior_verdicts` 없이 호출하면 (anchoring 외 required가 전부
    UNKNOWN이므로) **아무 claim도 인증되지 않는 것이 정상**이다 — '검사
    안 됨'은 '통과'가 아니라는 이 모듈의 원칙 그대로.

    반환 dict는 자기서술적이다: 어떤 profile로 판정했고(claim별 verdict
    표 포함), 무엇이 stale이고, fingerprint가 무엇인지 — 호출자가 이
    응답만으로 §7식 재구성을 할 수 있게.

    W5 수정 (2026-08-22): 두 입력 경로의 지위가 다르다.
    `prior_certificates`(서명 문서)는 authenticity → subject/revision 결박 →
    decider/assurance 유효성 검증을 전부 통과해야 하며, 그 경로만으로 구성된
    호출이 `authority: certifying`이다. raw `prior_verdicts` 문자열은
    하위호환으로 받되 결과는 영구히 `diagnostic_only` — 미인증 입력이 섞인
    호출도 마찬가지다(가장 약한 입력이 전체 지위를 정한다).

    **비대칭 서명 (2026-09-03).** `issuer_public_key`가 있으면 그 공개키
    바이트만으로 검증한다 — 이 호스트의 개인키 파일을 **열지도 만들지도
    않는다**(발급자와 검증자가 다른 호스트인 배포 경계를 닫는 지점). 없으면
    기존처럼 `key_path`(또는 기본 경로)의 seed 를 로드해 공개키를 유도한다
    — 같은 호스트가 발급·검증을 겸하던 하위 호출 형태 그대로 동작한다.
    """
    _assert_prior_verdicts_are_well_formed(prior_verdicts)
    prior_verdicts = prior_verdicts or {}

    # W5 수정: 인증된 경로. certificate는 authenticity → 결박 → 유효성을
    # 전부 통과해야 하고, 하나라도 위반이면 호출 전체가 CertificateError로
    # 거부된다(fail-closed — 위조 인증서를 조용히 건너뛰면 공격자가 유효한
    # 것만 남을 때까지 재시도한다).
    authenticated: Dict[str, Dict[str, Verdict]] = {}
    if prior_certificates:
        if issuer_public_key is not None:
            public_key = issuer_public_key
            # 공개키가 주어지면 키 절은 "issuer public key <key_id 앞 12자>" —
            # 파일명이 아니라 키 자체를 진단에 남긴다(호스트에 파일이 없다).
            key_source = f"issuer public key {cg_signing.key_id(issuer_public_key)[:12]}"
        else:
            seed = cg_identity.load_or_create_key(
                key_path or cg_identity.default_key_path())
            public_key = cg_signing.public_key_bytes(seed)
            key_source = _key_source_name(key_path)
        fp_to_claim = {cg_identity.claim_fingerprint(c): c for c in claims}
        for cert in prior_certificates:
            subject = fp_to_claim.get(cert.get("subject_fingerprint"))
            if subject is None:
                raise CertificateError(
                    f"certificate subject {cert.get('subject_fingerprint')!r} "
                    f"matches none of the presented claims (subject binding)")
            granted = _assert_certificate_grants_verdicts(
                cert, subject, public_key, expected_profile=profile,
                key_source=key_source)
            authenticated.setdefault(subject["id"], {}).update(granted)

    anchoring = results_from_claim_anchoring(claims, evidence_texts)
    anchoring_by_claim = dict(zip((c["id"] for c in claims), anchoring))

    verdicts_by_claim: Dict[str, Dict[str, Verdict]] = {}
    for c in claims:
        merged = dict(authenticated.get(c["id"], {}))
        merged.update({check: _VERDICT_BY_VALUE[value]
                       for check, value in prior_verdicts.get(c["id"], {}).items()})
        merged["claim.evidence_anchoring"] = anchoring_by_claim[c["id"]].verdict
        verdicts_by_claim[c["id"]] = merged

    # authority: 가장 약한 입력이 전체 지위를 정한다. raw 문자열이 하나라도
    # 섞이면 diagnostic_only — 미인증 입력이 인증에 기여한 결과를 "certifying"
    # 이라 부르는 순간 W5가 한 칸 옆에서 재현된다.
    authority = ("certifying"
                 if authenticated and not prior_verdicts
                 else "diagnostic_only")

    certified = certified_projection(claims, verdicts_by_claim, profile)
    certificate = certify(anchoring)

    stale = ([] if current_revision is None
             else stale_obligations(anchoring, current_revision))

    return {
        "ok": True,
        # W5 수정 착륙(2026-08-22): 인증된 certificate만으로 구성된 호출은
        # "certifying", raw 문자열이 하나라도 섞이면 "diagnostic_only".
        "authority": authority,
        "profile": profile.profile_id,
        "profile_required": list(profile.required),
        "anchoring_certificate": certificate,
        "verdicts_by_claim": {
            cid: {check: v.value for check, v in checks.items()}
            for cid, checks in verdicts_by_claim.items()},
        "certified_claim_ids": [c["id"] for c in certified],
        "stale_anchoring_obligations": stale,
        "claim_fingerprints": {
            c["id"]: cg_identity.claim_fingerprint(c) for c in claims},
        "verifier": VERIFIER,
    }

