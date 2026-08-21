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

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from graphlib import CycleError, TopologicalSorter
from typing import Any, Dict, Iterable, List, Tuple

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
        overlap = set(self.required) & set(self.allowed_na)
        if overlap:
            raise ValueError(
                f"profile {self.profile_id!r}: {sorted(overlap)} 이 required와 "
                f"allowed_na에 동시에 있다 — 같은 검사가 필수이면서 면제일 수 없다")


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
        cited = [evidence_texts.get(e) for e in c.get("cited_evidence_ids", [])]
        cited = [t for t in cited if t]
        if not cited:
            out.append(ObligationResult(
                "claim.evidence_anchoring", Verdict.UNKNOWN, Assurance.PROPOSED,
                DeciderKind.LOCAL_RULE,
                reason=f"{c['id']}: 인용 evidence 본문 없음 — 결박 판정 대상 없음",
                graph_revision=c.get("graph_revision")))
            continue
        terms = [c.get("concept", ""), c.get("feature", "")]
        missing = [t for t in terms if t and not any(t in body for body in cited)]
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
        "errors": errors,
        "results": [
            {"obligation": r.obligation, "verdict": r.verdict.value,
             "assurance": r.assurance.name, "decider": r.decider.value,
             "evidence": r.evidence, "reason": r.reason,
             "depends_on": list(r.depends_on),
             "graph_revision": r.graph_revision}
            for r in results
        ],
        "verifier": VERIFIER,
    }
