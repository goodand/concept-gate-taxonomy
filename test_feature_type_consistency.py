"""graph.feature_type_consistency — E2.2.1 hidden contract A 의 **판정 절반**.

## 무엇을 푸는가

E2.2.1 근본 원인 분석(roadmap): "같은 feature 이름은 모든 concept 에서
type 이 전역적으로 일치해야 한다"는 불변조건이 **어디에도 명시되지 않아서**,
모델이 concept-local 해석을 정당화했다 — wrong_direction_repair **55%**.
trial 3 원문: "a structural component in 돌체 and a functional role in
돌체린" 을 해소로 착각.

그 불변조건은 두 반쪽으로 갈린다(합리화 공백 채널 분석, KNOWHOW §C-0):
- **유도(사전)**: 자연어 명시 — A_ONLY 20/20, certificate 가 운반(M1 재설계).
- **판정(사후)**: 산출 그래프 위의 결정론 검사 — **이 파일이 그것이다.**
  LLM decider 가 필요 없다(probe 로 증명: 그 사례가 5줄 검사로 검출됨).

## 무엇을 재지 않는가

- 옳은 방향의 repair 를 **만들어내지** 못한다 — 위반을 드러낼 뿐이다.
  유도는 M1 certificate 의 일이다.
- type 이 **의미적으로 옳은지** 재지 않는다 — 전역 일치만 본다. 전부
  틀린 type 으로 일치해도 PASS 다(그 판정은 semantic decider 의 몫).
- 프로파일 `required` 에 넣지 않는다 — 편입은 D-38 절차(새 identity)다.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from conceptgate import cg_obligations as ob  # noqa: E402

# E2.2.1 trial 3 의 그 사례 — 실측 원문에서 온 픽스처다.
INCONSISTENT = [
    {"name": "돌체", "features": [
        {"feature": "액체금속", "type": "structural_composition"}]},
    {"name": "돌체린", "features": [
        {"feature": "액체금속", "type": "functional_role"}]},
]
CONSISTENT = [
    {"name": "돌체", "features": [
        {"feature": "액체금속", "type": "structural_composition"}]},
    {"name": "돌체린", "features": [
        {"feature": "액체금속", "type": "structural_composition"},
        {"feature": "가열", "type": "functional_role"}]},
]


def _verdict(concepts):
    (r,) = ob.results_from_feature_type_consistency(concepts)
    return r


def test_the_e221_case_is_detected_as_fail():
    """55% 를 만든 그 입력이 FAIL 로 검출된다 — UNKNOWN 이 아니다. 서로 다른
    type 의 **적극적 공존**은 부재가 아니라 불일치의 증거다(provenance 의
    QUOTE_MISMATCH → FAIL 과 같은 논리)."""
    r = _verdict(INCONSISTENT)
    assert r.verdict is ob.Verdict.FAIL
    assert r.obligation == "graph.feature_type_consistency"
    assert "액체금속" in r.reason
    assert "돌체" in r.reason and "돌체린" in r.reason


def test_a_consistent_graph_passes():
    """음성 증명의 짝 — 없으면 "항상 FAIL" 구현이 위를 통과한다."""
    r = _verdict(CONSISTENT)
    assert r.verdict is ob.Verdict.PASS
    assert r.assurance is ob.Assurance.RULE_CHECKED


def test_same_name_same_type_across_many_concepts_passes():
    many = [{"name": f"c{i}", "features": [
        {"feature": "공유부품", "type": "structural_composition"}]}
        for i in range(5)]
    assert _verdict(many).verdict is ob.Verdict.PASS


def test_no_typed_features_is_unknown_not_pass():
    """검사할 대상이 없으면 통과가 아니라 판정 불가다 — "없는 검사는 PASS 가
    아니다"(is_certified 규약)와 같은 결."""
    r = _verdict([{"name": "돌체", "features": []}])
    assert r.verdict is ob.Verdict.UNKNOWN
    assert "대상" in r.reason


def test_untyped_occurrences_do_not_join_the_comparison():
    """type 없는 출현은 비교에 안 들어간다 — 빈 값을 비교에 넣으면 부재가
    불일치로 오판된다(MAJOR-1 계열의 역방향)."""
    mixed = [
        {"name": "돌체", "features": [{"feature": "액체금속",
                                        "type": "structural_composition"}]},
        {"name": "돌체린", "features": [{"feature": "액체금속", "type": ""}]},
    ]
    assert _verdict(mixed).verdict is ob.Verdict.PASS


def test_malformed_entries_yield_unknown_not_crash_and_not_silent_pass():
    """신뢰 경계 — 형태가 깨진 입력은 죽지도, 조용히 통과하지도 않는다
    (비-str evidence 본문의 조용한 오판과 같은 부류를 사전에 막는다)."""
    r = _verdict([{"name": "돌체", "features": "문자열이다"}])
    assert r.verdict is ob.Verdict.UNKNOWN
    assert "파싱" in r.reason or "형태" in r.reason
    r2 = _verdict("리스트가 아니다")
    assert r2.verdict is ob.Verdict.UNKNOWN


def test_a_conflict_wins_over_malformed_entries():
    """깨진 항목이 섞여 있어도 **검출된 위반은 위반이다** — 파싱 실패가
    적극적 증거를 가리면 깨진 입력이 도피구가 된다."""
    both = INCONSISTENT + [{"name": "x", "features": 42}]
    assert _verdict(both).verdict is ob.Verdict.FAIL


def test_the_reason_is_deterministic_across_input_order():
    """결정론 — 입력 순서가 바뀌어도 reason 이 같아야 재현·대조가 성립한다."""
    a = _verdict(INCONSISTENT).reason
    b = _verdict(list(reversed(INCONSISTENT))).reason
    assert a == b


def test_it_is_registered_with_a_real_decider_and_not_in_any_profile():
    """레지스트리 YAGNI(실존 decider 만) 충족 + 프로파일 미편입(편입은 D-38
    절차 — required 변경은 새 identity 사안)."""
    assert "graph.feature_type_consistency" in ob.OBLIGATION_REGISTRY
    spec = ob.OBLIGATION_REGISTRY["graph.feature_type_consistency"]
    assert spec.decider is ob.DeciderKind.LOCAL_RULE
    for prof in (ob.LEGACY_RELATION_PROFILE, ob.RELATION_CLAIM_V1_PROFILE):
        assert "graph.feature_type_consistency" not in prof.required


def test_invariant_stays_none_here_too():
    """지목 값 채움은 M1 설계 판단이다 — 이 producer 가 선점하지 않는다.
    (D-38 이 자리·서명·대조를 준비했고, 어느 FQN 을 다는가가 남은 판단.)"""
    assert _verdict(INCONSISTENT).invariant is None
