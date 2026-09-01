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

## 배선 범위의 제약 — Risk More READ 가 확정한 것 (프로토콜 2단, 2026-09-01)

**이 의무를 저장소 전역 게이트로 배선하면 안 된다.** 코퍼스 전수 실측:
JSON 125개 중 **15개가 FAIL** 이고, 그것은 **오탐이 아니라 정탐**이다 —
E2.2 계열 실험 fixture(`e2.2.1/e2.2.2/e2.2.3/bvsc` 의 `fixture.json`·
`trials.json`)가 `'바퀴': essential_feature(돌체) vs functional(돌체린)`
같은 불일치를 **의도적으로 심어 놓았다**. 모델이 발견해 repair 해야 하는
문제 그 자체이기 때문이다.

따라서:

- **claim graph 판정용 obligation** 으로는 옳다 — 그것이 이 파일의 대상이다.
- **전역 게이트로는 부적절하다** — 동결 fixture 는 수정 금지이므로 게이트가
  영구히 빨갛거나 면제 목록이 커진다. CLAUDE.md 가 경고한 "게이트는 사람이
  끄면 끝" 이 정확히 그 상황이다.
- 실행 비용은 무해: 10,000 출현에 1.2ms(전수 실측).

## 배선 미실행과 그 이유 — 적대검증 blocker (2026-09-01)

**production 호출 0건**이고, 이 저장소에는 그 상태로 삭제된 선례가 있다
(`docs/LEGACY_REGISTER.md:31` — P21 "테스트는 도는데 배선 0·import 0").
그러나 지금 배선하지 않는 것은 태만이 아니라 **순서**다:

- `certify([FAIL])` 는 프로파일 미편입이어도 집계 verdict 를 `fail` 로
  뒤집는다(실측). 즉 배선 즉시 `run_pipeline` 인증서 동작이 바뀐다.
- 그래서 **정규화가 배선의 선행조건**이었다(적대검증 지목, 채택·완료).
  정규화 없이 붙이면 표기 차이에서 나온 거짓 FAIL 이 인증서에 실리고, 그
  되돌림이 곧 P21 경로다.
- 배선 지점 후보는 실측으로 지목돼 있다: `server.py:427`
  (`_attach_lint(_serialize_pipeline_output(out, parsed), concepts)` — 인자가
  정확히 `list[dict]` + feature/type 이고 parse 통과 후라 type 이 정규값) ·
  `server.py:958`(assembled concepts). **배포된 도구의 관측 가능한 출력을
  바꾸므로 D-38 ㄷ 이 지목한 backward-compatibility 사안**이고 별도 판단이다.

`Edge case` 쪽 수확은 아래 enum 계약 둘이다 — 코퍼스 지배 형태
(`('evidence','feature','type')` 1,231건)가 dataclass 유래여서, 초판은
실제 그래프에서 조용히 아무것도 검사하지 않았다.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from conceptgate import cg_obligations as ob  # noqa: E402

# E2.2.1 trial 3 의 그 사례 — 실측 원문에서 온 픽스처다.
# 이름을 서로의 **부분문자열이 아닌** 값으로 둔다 — 초판은 '돌체'/'돌체린'
# 이었고 `"돌체" in reason` 이 `"돌체린" in reason` 에 논리적으로 포섭되어
# 한쪽만 보고하는 구현이 통과했다(적대검증 major, 채택). type 도 이 저장소의
# 실유효값(`FeatureType`)만 쓴다 — `functional_role` 은 없는 값이었다.
INCONSISTENT = [
    {"name": "하론", "features": [
        {"feature": "액체금속", "type": "structural_composition"}]},
    {"name": "카론", "features": [
        {"feature": "액체금속", "type": "essential_feature"}]},
]
CONSISTENT = [
    {"name": "하론", "features": [
        {"feature": "액체금속", "type": "structural_composition"}]},
    {"name": "카론", "features": [
        {"feature": "액체금속", "type": "structural_composition"},
        {"feature": "가열", "type": "functional"}]},
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
    # 양쪽 concept 이 **각각** 보고되어야 한다. 이름이 서로 부분문자열이
    # 아니므로 이 두 단언은 서로를 포섭하지 않는다.
    assert "하론" in r.reason and "카론" in r.reason


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
    r = _verdict([{"name": "하론", "features": []}])
    assert r.verdict is ob.Verdict.UNKNOWN
    assert "대상" in r.reason


def test_untyped_occurrences_do_not_join_the_comparison():
    """type 없는 출현은 비교에 안 들어간다 — 빈 값을 비교에 넣으면 부재가
    불일치로 오판된다(MAJOR-1 계열의 역방향)."""
    mixed = [
        {"name": "하론", "features": [{"feature": "액체금속",
                                        "type": "structural_composition"}]},
        {"name": "카론", "features": [{"feature": "액체금속", "type": ""}]},
    ]
    assert _verdict(mixed).verdict is ob.Verdict.PASS


def test_enum_typed_features_are_compared_not_skipped():
    """**Edge case More READ 가 잡은 결함**(2026-09-01, 프로토콜 2단).

    이 저장소의 정본 자료구조 `NormalizedFeature.type` 은 `FeatureType`
    **enum** 이고, 코퍼스 전수(JSON 125개)에서 지배 형태가 그 유래다
    (`('evidence','feature','type')` 1,231건). 초판은 `isinstance(str)` 만
    요구해서 그 형태를 통째로 건너뛰었다 — 위반이 실재하는데 "검사 대상
    없음(UNKNOWN)" 을 냈다. 빈 어휘가 PASS 를 받던 MAJOR-1 과 같은 부류:
    **조용히 아무것도 검사하지 않는 상태.**"""
    from conceptgate.concept_gate_v7 import FeatureType
    a, b = list(FeatureType)[0], list(FeatureType)[1]
    conflict = [
        {"name": "하론", "features": [{"feature": "액체금속", "type": a}]},
        {"name": "카론", "features": [{"feature": "액체금속", "type": b}]},
    ]
    r = _verdict(conflict)
    assert r.verdict is ob.Verdict.FAIL
    assert a.value in r.reason and b.value in r.reason   # enum 이 아니라 값으로


def test_enum_and_str_of_the_same_type_are_not_a_conflict():
    """위 수리의 짝 — enum 과 그 `.value` 문자열은 **같은 type** 이다.
    이것이 없으면 정규화가 과잉이어서 멀쩡한 그래프를 빨갛게 만든다."""
    from conceptgate.concept_gate_v7 import FeatureType
    a = list(FeatureType)[0]
    mixed = [
        {"name": "하론", "features": [{"feature": "액체금속", "type": a}]},
        {"name": "카론", "features": [{"feature": "액체금속", "type": a.value}]},
    ]
    assert _verdict(mixed).verdict is ob.Verdict.PASS


def test_unicode_normalization_closes_the_bypass():
    """**적대검증이 잡은 우회**(major, 채택). 같은 글자의 다른 코드점
    (NFC/NFD)으로 이름을 쓰면 충돌이 `PASS` 로 빠져나갔다 — 실측 확인.
    `cg_normalizer` 는 name·label 에 이미 NFC 를 적용한다(7곳)이므로 이
    수리는 새 정책이 아니라 **두 층의 정책 불일치 시정**이다."""
    import unicodedata
    nfc = unicodedata.normalize("NFC", "액체금속")
    nfd = unicodedata.normalize("NFD", "액체금속")
    assert nfc != nfd                      # 전제: 코드점이 실제로 다르다
    r = _verdict([
        {"name": "하론", "features": [{"feature": nfc,
                                       "type": "structural_composition"}]},
        {"name": "카론", "features": [{"feature": nfd,
                                       "type": "essential_feature"}]}])
    assert r.verdict is ob.Verdict.FAIL


def test_whitespace_and_case_do_not_bypass():
    """같은 원인의 다른 표면 — 후행 공백·대소문자로도 우회됐다."""
    for a, b in (("금속", "금속 "), ("Metal", "metal")):
        r = _verdict([
            {"name": "하론", "features": [{"feature": a,
                                           "type": "structural_composition"}]},
            {"name": "카론", "features": [{"feature": b,
                                           "type": "essential_feature"}]}])
        assert r.verdict is ob.Verdict.FAIL, (a, b)


def test_type_spelling_variants_are_not_a_false_conflict():
    """정규화의 **반대 방향** — 같은 원인이 거짓 FAIL 도 만들었다(실측:
    `structural_composition` vs `structural composition` → FAIL). 이 계약이
    없으면 정규화를 한쪽만 적용해 과잉 발화가 남는다."""
    for variant in ("structural composition", "STRUCTURAL_COMPOSITION",
                    "structural_composition "):
        r = _verdict([
            {"name": "하론", "features": [{"feature": "금속",
                                           "type": "structural_composition"}]},
            {"name": "카론", "features": [{"feature": "금속",
                                           "type": variant}]}])
        assert r.verdict is ob.Verdict.PASS, variant


def test_malformed_entries_yield_unknown_not_crash_and_not_silent_pass():
    """신뢰 경계 — 형태가 깨진 입력은 죽지도, 조용히 통과하지도 않는다
    (비-str evidence 본문의 조용한 오판과 같은 부류를 사전에 막는다)."""
    r = _verdict([{"name": "하론", "features": "문자열이다"}])
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
