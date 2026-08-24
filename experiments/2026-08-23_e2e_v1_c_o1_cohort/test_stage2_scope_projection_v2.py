"""O1_SCOPE_PROJECTION_V2 계약 (D-E2E-v1-32). 이 파일이 계약 정본이다.

## 왜 새 모듈인가 (V1을 고치지 않는다)

판정이 `supersedes: [O1_SCOPE_PROJECTION_V1]`과 `V1_V2_score_comparable: false`를
명했다. V1 모듈 해시는 V4 manifest의 `contract_hashes`에 핀돼 있고, 사슬에
`V1–V4 = V1 semantics` / `V5 onward = V2 semantics`를 선언해야 한다. 따라서
**V1은 바이트 그대로 보존**하고 V2를 신설한다 — 역사적 측정 의미론을 지우면
그 선언이 검증 불가가 된다.

## 무엇이 달라지는가 (실측한 델타)

현재(V1) 투영에 판정의 qualification 8종을 적용한 결과, **미충족은 둘뿐**이다:
  #1 modifier 유무 불변성 · #5 lexical `and`/`or` 정체 미채점
나머지(empty/nonempty · 중첩 양화 · `Q>not` · carrier 보존 · BODY 정책)는
이미 성립한다. **BODY는 이미 판정 정책을 만족하므로** Q32.5의 "대칭화"는
BODY를 바꾸는 것이 아니라 **제한식을 BODY 수준으로 올리는 것**이다.

## 추상화의 성격 — predicate erasure가 아니다

판정문: "이를 **predicate erasure가 아니라 scope-measurement abstraction**으로
기록하는 것이 맞다." 버리는 것과 지키는 것이 명시돼 있다:

    버림: 어휘 라벨 · 술어 개수 · 비-scope 내부 Boolean 구조
    지킴: 내용 유무(empty/nonempty) · 변수 incidence · primary scope 연산자
          · 필요한 carrier topology

## `variable incidence`는 **순서**다 (선행 정본이 강제한다)

판정문은 `variable_incidence`라고만 적었다. 집합으로 구현하면 `P(x,y)`와
`P(y,x)`가 같아지고 그것은 **D-27이 유지를 명한 binding topology를 파괴**한다.
따라서 incidence는 **술어별 인자 이름 튜플의 순서 있는 목록**이고, 동일 튜플의
중복만 제거한다(판정의 "동일 incidence 다중도는 버린다"). 이것은 새 결정이
아니라 선행 정본의 귀결이다.

## `Q_RSTR_BODY`는 **위치**로 정한다 — 판정 문면의 재해석 (확인 대기)

판정은 `implies_generated_by_forall_desugar`를 `Q_RSTR_BODY`로 보존하라고
했으나, desugar 후 생성분과 원본은 **바이트 동일**이다(실측). 태깅으로 구별하면
`forall(x,dog,bark)`와 `forall(x,True,implies(dog,bark))`가 구별되기 시작해
subject의 **인코딩 선택**이 채점된다 — 판정이 방금 제거한 교란과 같은 부류다.

그래서 **위치**로 정의한다: 제한식이 `True`인 양화의 **직접 body**에 있는
`implies`는 provenance 무관하게 `Q_RSTR_BODY`다. 그 위치의 역할이 RSTR/BODY이므로
누가 썼는지 물을 필요가 없다.

**이것은 재해석이므로 확인 항목이다.** 확인 전까지 이 계약이 그 사실을
명시적으로 들고 있고(`REINTERPRETATION` 상수), 판정이 태깅을 지시하면
이 테스트가 뒤집힌다 — 그때 뒤집는 것이 정당한 변경이다.

## 닫힌 profile — 미지 연산자는 추정하지 않는다

`unknown_operator: qualification_fail`. 새 구성자를 만나면 조용히 통과시키지
않고 거부한다. 방언이 8종이 되는 과정에서 하류 게이트가 못 따라온 전례가
있으므로(신호 게이트가 count/prop를 못 보던 것), 이 실패는 소리를 내야 한다.
"""
from __future__ import annotations

import pytest

import _stage2_scope_projection_v2 as v2

V = lambda n: {"kind": "var", "name": n}                      # noqa: E731
P = lambda n, *a: {"kind": "pred", "name": n, "args": list(a)}  # noqa: E731
AND = lambda *a: {"kind": "and", "args": list(a)}             # noqa: E731
OR = lambda *a: {"kind": "or", "args": list(a)}               # noqa: E731
NOT = lambda b: {"kind": "not", "body": b}                    # noqa: E731
IMP = lambda l, r: {"kind": "implies", "left": l, "right": r}  # noqa: E731
FA = lambda v, r, b: {"kind": "forall", "var": v, "restriction": r, "body": b}   # noqa: E731
EX = lambda v, r, b: {"kind": "exists", "var": v, "restriction": r, "body": b}   # noqa: E731
CNT = lambda rel, num, v, r, b: {"kind": "count", "rel": rel, "num": num,        # noqa: E731
                                 "var": v, "restriction": r, "body": b}
PROP = lambda rel, v, r, b: {"kind": "prop", "rel": rel, "var": v,               # noqa: E731
                             "restriction": r, "body": b}
TRUE = {"kind": "pred", "name": "True", "args": []}

same = lambda a, b: v2.signature(a) == v2.signature(b)        # noqa: E731


# ---- profile 정체 -------------------------------------------------------

def test_profile_identity():
    assert v2.PROJECTION_PROFILE_ID == "O1_SCOPE_PROJECTION_V2"
    assert v2.SUPERSEDES == ("O1_SCOPE_PROJECTION_V1",)
    assert v2.V1_SCORE_COMPARABLE is False


def test_primary_scope_operators_are_the_ruled_set():
    assert set(v2.PRIMARY_SCOPE) == {"forall", "exists", "count", "prop", "not"}


def test_reinterpretation_is_declared_not_hidden():
    """위치 기반 Q_RSTR_BODY가 판정 문면의 재해석임을 코드가 들고 있어야 한다."""
    assert "position" in v2.REINTERPRETATION
    assert len(v2.REINTERPRETATION) > 80


def test_logical_equivalence_is_not_claimed():
    """비-scope 내용을 접는 것은 동치 주장이 아니라 측정 함수다."""
    assert v2.LOGICAL_EQUIVALENCE_CLAIM is False


# ---- 판정 §"필요한 V2 qualification tests" 8종 -------------------------

def test_q1_modifier_presence_is_not_scored():
    """1. `previous(x) ∧ exorcism(x)` vs `exorcism(x)` → same"""
    assert same(EX("x", AND(P("previous", V("x")), P("exorcism", V("x"))), P("f", V("x"))),
                EX("x", P("exorcism", V("x")), P("f", V("x"))))


def test_q2_empty_and_nonempty_restriction_stay_distinct():
    """2. `True` restriction vs `dog(x)` → different.

    이것이 없으면 generalized_quantifier 층의 측정이 비어 버린다.
    """
    assert not same(EX("x", TRUE, P("b", V("x"))),
                    EX("x", P("dog", V("x")), P("b", V("x"))))


def test_q3_nested_quantifier_in_restriction_is_scored():
    """3. nested `exists/forall/count/prop` 추가 → different"""
    plain = EX("x", P("d", V("x")), P("b", V("x")))
    nested = EX("x", AND(P("d", V("x")),
                         FA("y", P("c", V("y")), P("r", V("y")))), P("b", V("x")))
    assert not same(plain, nested)


@pytest.mark.parametrize("inner", [
    FA("y", P("c", V("y")), P("r", V("y"))),
    EX("y", P("c", V("y")), P("r", V("y"))),
    CNT("eq", 2, "y", P("c", V("y")), P("r", V("y"))),
    PROP("most", "y", P("c", V("y")), P("r", V("y"))),
], ids=["forall", "exists", "count", "prop"])
def test_q3_holds_for_every_primary_binder(inner):
    """네 결박자 전부에 대해 성립해야 한다 — 하나라도 새면 그 층이 비워진다."""
    plain = EX("x", P("d", V("x")), P("b", V("x")))
    nested = EX("x", AND(P("d", V("x")), inner), P("b", V("x")))
    assert not same(plain, nested)


def test_q4_negation_scope_order_is_scored():
    """4. `Q > not` vs `not > Q` → different (quantifier_negation_scope 층)"""
    assert not same(FA("x", P("d", V("x")), NOT(P("b", V("x")))),
                    NOT(FA("x", P("d", V("x")), P("b", V("x")))))


def test_q4_negation_inside_restriction_is_also_scored():
    """제한식 안의 `not`도 primary scope다 — 판정이 명시했다."""
    assert not same(EX("x", AND(P("d", V("x")), NOT(P("c", V("x")))), P("b", V("x"))),
                    EX("x", AND(P("d", V("x")), P("c", V("x"))), P("b", V("x"))))


def test_q5_lexical_and_or_identity_is_not_scored():
    """5. lexical-only `and` vs `or` → same.

    명제 동치를 주장하는 것이 아니다 — O1 측정 함수가 그 차원을 **의도적으로
    관측하지 않는다**(판정문).
    """
    assert same(EX("x", OR(P("d", V("x")), P("c", V("x"))), P("b", V("x"))),
                EX("x", AND(P("d", V("x")), P("c", V("x"))), P("b", V("x"))))


def test_q6_carrier_with_scope_descendant_preserves_topology():
    """6. `and/or` 안에 중첩 양화 → topology 보존"""
    with_scope = EX("x", AND(P("d", V("x")),
                             EX("y", P("c", V("y")), P("r", V("y")))), P("b", V("x")))
    lexical = EX("x", AND(P("d", V("x")), P("z", V("x"))), P("b", V("x")))
    assert not same(with_scope, lexical)


def test_q6_carrier_identity_is_not_scored_even_with_scope():
    """carrier가 보존돼도 `and`/`or`라는 **정체**는 채점하지 않는다."""
    inner = EX("y", P("c", V("y")), P("r", V("y")))
    assert same(EX("x", AND(P("d", V("x")), inner), P("b", V("x"))),
                EX("x", OR(P("d", V("x")), inner), P("b", V("x"))))


def test_q7_q_rstr_body_direction_is_preserved():
    """7. generated `implies`의 RSTR/BODY 방향 → preserved.

    주의: 양쪽 피연산자가 같은 opaque atom으로 접히면 좌우 교환은 **원리상
    관측 불가**이고 그것은 결함이 아니라 계약의 귀결이다. 그래서 한쪽에
    중첩 양화를 둬 관측 가능하게 한다.
    """
    inner = EX("y", P("c", V("y")), P("r", V("y")))
    assert not same(FA("x", TRUE, IMP(P("d", V("x")), inner)),
                    FA("x", TRUE, IMP(inner, P("d", V("x")))))


def test_q8_body_lexical_multiplicity_is_not_scored():
    """8a. BODY의 어휘 다중도만 변화 → same"""
    assert same(EX("x", P("d", V("x")), AND(P("b", V("x")), P("c", V("x")))),
                EX("x", P("d", V("x")), P("b", V("x"))))


def test_q8_body_incidence_change_is_scored():
    """8b. 변수 incidence 변화 → different"""
    assert not same(EX("x", P("d", V("x")), EX("y", P("c", V("y")), P("r", V("x"), V("y")))),
                    EX("x", P("d", V("x")), EX("y", P("c", V("y")), P("r", V("y"), V("x")))))


# ---- incidence는 순서다 (D-27이 강제) ---------------------------------

def test_binding_topology_survives_the_collapse():
    """`P(x,y) ≠ P(y,x)` — incidence를 집합으로 구현하면 이 테스트가 죽는다.

    D-27이 유지를 명한 성질이고, 판정문의 `variable_incidence`를 순서로
    읽어야 하는 근거다.
    """
    assert not same(EX("x", P("d", V("x")), EX("y", TRUE, P("r", V("x"), V("y")))),
                    EX("x", P("d", V("x")), EX("y", TRUE, P("r", V("y"), V("x")))))


def test_same_incidence_tuple_repeated_is_collapsed():
    """동일 튜플의 중복만 접는다 — 판정의 '동일 incidence 다중도는 버린다'."""
    assert same(EX("x", AND(P("a", V("x")), P("b", V("x")), P("c", V("x"))), P("z", V("x"))),
                EX("x", P("a", V("x")), P("z", V("x"))))


def test_arity_change_is_an_incidence_change():
    """`P(x)`와 `P(x,x)`는 incidence 튜플이 다르다."""
    assert not same(EX("x", P("d", V("x")), P("b", V("x"))),
                    EX("x", P("d", V("x")), P("b", V("x"), V("x"))))


# ---- count/prop의 채점 차원은 V1에서 이어받는다 -----------------------

def test_cardinal_value_and_relation_remain_scored():
    a = CNT("eq", 3, "x", P("d", V("x")), P("b", V("x")))
    assert not same(a, CNT("eq", 4, "x", P("d", V("x")), P("b", V("x"))))
    assert not same(a, CNT("ge", 3, "x", P("d", V("x")), P("b", V("x"))))


def test_prop_and_count_stay_distinct():
    assert not same(PROP("most", "x", P("d", V("x")), P("b", V("x"))),
                    CNT("ge", 2, "x", P("d", V("x")), P("b", V("x"))))


def test_alpha_renaming_is_still_invisible():
    assert same(EX("x", P("d", V("x")), P("b", V("x"))),
                EX("z", P("d", V("z")), P("b", V("z"))))


# ---- 닫힌 profile: 미지 연산자는 거부 ---------------------------------

def test_unknown_operator_is_refused():
    with pytest.raises(v2.ProjectionQualificationFail):
        v2.signature({"kind": "modal_box_new", "body": P("d", V("x"))})


def test_unknown_operator_nested_is_also_refused():
    bad = EX("x", AND(P("d", V("x")), {"kind": "brand_new", "body": TRUE}), P("b", V("x")))
    with pytest.raises(v2.ProjectionQualificationFail):
        v2.signature(bad)


def test_refusal_names_the_operator():
    try:
        v2.signature({"kind": "weird_op"})
    except v2.ProjectionQualificationFail as exc:
        assert "weird_op" in str(exc)
    else:
        pytest.fail("거부되지 않았다")


# ---- 순수 함수·idempotent ---------------------------------------------

def test_signature_is_deterministic_and_does_not_mutate_input():
    import copy
    f = EX("x", AND(P("d", V("x")), P("e", V("x"))), P("b", V("x")))
    before = copy.deepcopy(f)
    a, b = v2.signature(f), v2.signature(f)
    assert a == b
    assert f == before, "입력을 변경했다"


# ---- D-32-C: 위치 규칙은 **`forall` 한정**이다 -------------------------
#
# 판정 D-E2E-v1-32-C가 운영 세션의 재해석을 **승인하되 좁혔다**. 요청서에 쓴
# "제한식이 `True`인 **양화**의 직접 body"를 모든 결박자에 적용하면 안 된다.
#
# 근거(판정문 + 우리 2원소 전수 재계산으로 이중화):
#   restricted universal   `P→Q`  ≡  `True→(P→Q)`   — 4/4 조합 동치
#   restricted existential `P∧Q`  ≢  `True∧(P→Q)`   — 반례 (F,F)·(F,T)
# 즉 `forall`에서만 두 인코딩이 같은 의미이고, `exists`·`count`·`prop`에서는
# 위치 규칙을 적용하면 **의미가 다른 것을 같게 만든다**.
#
# 적대 검증(2026-08-24)이 구현에서 이 과일반화를 실측했다 — 4종 전부에 표지가
# 붙고 있었다. 계약이 `forall`만 시험 입력으로 썼기 때문에 잡히지 않았다.
# 판정의 `non_matches` 4항을 여기서 결박한다.

_INNER = EX("y", P("c", V("y")), P("r", V("y")))   # 방향·표지 관측용


def test_scope_of_the_position_rule_is_declared_forall_only():
    """판정의 지시: **이름에 `forall` 한정임이 드러나야** 한다."""
    assert v2.Q_RSTR_BODY_SCOPE == ("forall",)
    assert "forall" in v2.Q_RSTR_BODY_MARKER.lower()


def test_reinterpretation_text_states_the_forall_restriction():
    assert "forall" in v2.REINTERPRETATION.lower()


def test_forall_with_empty_restriction_and_implies_body_matches():
    out = repr(v2.signature(FA("x", TRUE, IMP(P("d", V("x")), _INNER))))
    assert v2.Q_RSTR_BODY_MARKER in out


@pytest.mark.parametrize("binder", [
    lambda b: EX("x", TRUE, b),
    lambda b: CNT("eq", 2, "x", TRUE, b),
    lambda b: PROP("most", "x", TRUE, b),
], ids=["exists", "count", "prop"])
def test_non_forall_binders_do_not_match(binder):
    """판정 `non_matches`: exists/count/prop는 제외다.

    적용하면 `P∧Q`와 `True∧(P→Q)`를 같게 만들어 **의미가 다른 것을 같게** 한다.
    """
    out = repr(v2.signature(binder(IMP(P("d", V("x")), _INNER))))
    assert v2.Q_RSTR_BODY_MARKER not in out


def test_implies_not_directly_under_forall_body_does_not_match():
    """판정 `non_matches` 4항 — 직접 body가 아니면 적용 안 된다."""
    nested = FA("x", TRUE, AND(IMP(P("d", V("x")), _INNER), P("z", V("x"))))
    assert v2.Q_RSTR_BODY_MARKER not in repr(v2.signature(nested))


def test_forall_with_nonempty_restriction_does_not_match():
    """제한식이 비어 있지 않으면 그 body의 implies는 일반 implies다."""
    out = repr(v2.signature(FA("x", P("d", V("x")), IMP(P("e", V("x")), _INNER))))
    assert v2.Q_RSTR_BODY_MARKER not in out


def test_encoding_invariance_holds_through_desugar():
    """판정 `encoding_invariance: required: true`.

    **운영 전제를 함께 결박한다**: 불변성은 desugar가 먼저 정규화하기 때문에
    성립하고, 위치 규칙 자체가 만드는 성질이 아니다. 비정규화 입력에 이 투영을
    쓰면 두 인코딩의 signature가 갈린다(적대 검증이 실측했다). 따라서
    파이프라인은 반드시 desugar → signature 순서여야 한다.
    """
    from _stage2_canonical_core import desugar
    a = FA("x", TRUE, IMP(P("d", V("x")), P("b", V("x"))))
    b = FA("x", P("d", V("x")), P("b", V("x")))
    assert v2.signature(desugar(a)) == v2.signature(desugar(b))


def test_left_right_direction_survives_the_marker():
    """표지를 붙여도 R→B와 B→R은 구별돼야 한다(판정 `preserve`)."""
    assert not same(FA("x", TRUE, IMP(P("d", V("x")), _INNER)),
                    FA("x", TRUE, IMP(_INNER, P("d", V("x")))))


def test_no_provenance_in_the_signature():
    """판정 `forbidden: desugar_origin_tag_in_scoring_signature`.

    부재 증명: signature는 중첩 tuple뿐이고 문자열 원소는 정해진 어휘에서만
    나온다. `desugar`·`origin`·`generated` 류 표지가 등장하면 실패한다.
    """
    from _stage2_canonical_core import desugar
    out = repr(v2.signature(desugar(FA("x", P("d", V("x")), P("b", V("x"))))))
    for banned in ("desugar", "origin", "generated", "provenance"):
        assert banned not in out.lower()
