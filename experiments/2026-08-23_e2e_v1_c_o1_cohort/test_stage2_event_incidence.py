"""D-E2E-v1-28 Q28.1(d): PMB_EVENT_INCIDENCE_PROJECTION_V1 — RED 먼저.

판정 §1: `∃e(Smile(e)∧Agent(e,x)) ≢ Smile(x)`이므로 **논리식 재작성은
금지**다. 대신 §2-3의 측정 전용 투영: 사건 술어의 **어휘 진리값은 버리고**,
role edge가 말하는 "이 양화된 참여자가 body의 어떤 내용 술어에 참여한다"는
**결박 incidence만 무라벨 slot으로 보존**한다. 동치를 주장하지 않는다.

이것이 해결하는 결함(G3): 기존 투영은 동사 synset을 비계로 제거해 oracle
본문을 `True`로 붕괴시켰다("Everyone smiled" → `∀(T;(□→T))`) — 단순보편
4건이 전부 같은 골격이 되어 신호가 사라지고 실패가 예정됐다.

보존(판정 §5): 양화 종류·중첩·부정 위치·함의 위치·제한/본문 영역·참여자
incidence·술어 occurrence 존재.
버림: 사건 변수 정체·시간 변수·role 라벨·동사 synset 라벨·사건 술어 어휘.

**인자 순서 규약(운영 세션 설계 판단, 위험 명기)**: role 라벨은 채점 밖
이므로(§판정 `role_label_scored: false`) 참여자 인자 순서를 role 서열로
정할 수 없다. 대신 **양화 계보 순서(외부→내부)** 로 정렬한다. subject 쪽은
자기가 쓴 인자 순서를 유지하므로, 결과적으로 "subject가 계보 순서대로
인자를 놓았는가"가 측정된다 — D-27이 유지를 명한 binding topology가 이
정의로 살아 있다. 위험: 이 규약은 비대칭이며, 계보 순서가 자연 어순과
어긋나는 source에서는 재검토가 필요하다.

fail-closed(판정 §6): 참여자 incidence 0 / 중첩 사건 결합 모호 /
scope 교차 / 양화 재배열 필요 → 그 fixture는 INELIGIBLE.
"""
from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

import _stage2_event_incidence as ei  # noqa: E402
from conceptgate import cg_evaluate  # noqa: E402

V = lambda n: {"kind": "var", "name": n}
P = lambda name, *a: {"kind": "pred", "name": name, "args": list(a)}
FA = lambda v, r, b: {"kind": "forall", "var": v, "restriction": r, "body": b}
EX = lambda v, r, b: {"kind": "exists", "var": v, "restriction": r, "body": b}
AND = lambda *a: {"kind": "and", "args": list(a)}
NOT = lambda b: {"kind": "not", "body": b}
T = P("True")


def same(a, b) -> bool:
    return cg_evaluate.evaluate(a, b)["result"] == "pass"


def test_profile_identity():
    assert ei.EVENT_INCIDENCE_PROFILE_ID == "PMB_EVENT_INCIDENCE_PROJECTION_V1"
    assert ei.SLOT == "□"


# ---- G3 회귀 계약: "Everyone smiled." ----

ORACLE_SMILED = FA("x", P("person.n.01", V("x")),
                   EX("e", T, AND(P("smile.v.01", V("e")),
                                  P("Agent", V("e"), V("x")))))
SUBJECT_SMILED = FA("x", P("everyone", V("x")), P("smiled", V("x")))


def test_g3_body_signal_survives():
    """oracle 본문이 True로 붕괴하지 않는다 — 신호가 살아남아야 한다."""
    sig = ei.project_event_incidence(ORACLE_SMILED)
    body = sig["body"]
    # desugar 결과는 forall(x, True, implies(restriction, body))
    assert body["kind"] == "implies"
    assert body["right"]["kind"] == "pred"
    assert body["right"]["name"] == ei.SLOT
    assert [a["name"] for a in body["right"]["args"]] == ["x"]


def test_g3_oracle_and_natural_subject_converge():
    assert same(ei.project_event_incidence(ORACLE_SMILED),
                ei.project_event_incidence(SUBJECT_SMILED))


def test_g3_scope_mutation_still_fails():
    """∀→∃ 변이는 여전히 구별돼야 한다(투영이 공허해지지 않았다)."""
    mutated = EX("x", P("everyone", V("x")), P("smiled", V("x")))
    assert not same(ei.project_event_incidence(mutated),
                    ei.project_event_incidence(ORACLE_SMILED))


def test_negation_position_preserved():
    a = NOT(ORACLE_SMILED)
    b = FA("x", P("person.n.01", V("x")),
           NOT(EX("e", T, AND(P("smile.v.01", V("e")),
                              P("Agent", V("e"), V("x"))))))
    assert not same(ei.project_event_incidence(a),
                    ei.project_event_incidence(b))


# ---- 2참여자: "Not all children like apples." ----

ORACLE_LIKE = NOT(FA("x0", P("child.n.01", V("x0")),
                     EX("x2", P("apple.n.01", V("x2")),
                        EX("e", T, AND(P("like.v.03", V("e")),
                                       P("Experiencer", V("e"), V("x0")),
                                       P("Stimulus", V("e"), V("x2")))))))
SUBJECT_LIKE = NOT(FA("x", P("child", V("x")),
                      EX("y", P("apple", V("y")), P("like", V("x"), V("y")))))


def test_two_participant_incidence_converges():
    assert same(ei.project_event_incidence(ORACLE_LIKE),
                ei.project_event_incidence(SUBJECT_LIKE))


def test_argument_order_follows_quantifier_ancestry():
    """참여자 인자는 양화 계보(외부→내부) 순서로 정렬된다."""
    sig = ei.project_event_incidence(ORACLE_LIKE)
    names = []
    def walk(n):
        if isinstance(n, dict):
            if n.get("kind") == "pred" and len(n.get("args", [])) == 2:
                names.append([a["name"] for a in n["args"]])
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(sig)
    assert names and names[0] == ["x0", "x2"]      # ∀x0 이 ∃x2 보다 외부


def test_reversed_subject_arguments_still_fail():
    """D-27 유지: P(x,y) ≠ P(y,x) — 계보 역순 출력은 불일치."""
    reversed_subj = NOT(FA("x", P("child", V("x")),
                           EX("y", P("apple", V("y")), P("like", V("y"), V("x")))))
    assert not same(ei.project_event_incidence(reversed_subj),
                    ei.project_event_incidence(ORACLE_LIKE))


# ---- fail-closed (판정 §6) ----

def test_zero_participant_incidence_is_ineligible():
    """사건에 참여자가 없으면 무라벨 slot을 붙일 대상이 없다 → 거부."""
    weather = EX("e", T, P("rain.v.01", V("e")))       # 참여자 0
    with pytest.raises(ei.EventContractionRefused) as ei_:
        ei.project_event_incidence(FA("x", P("day.n.01", V("x")), weather))
    assert "participant" in str(ei_.value)


def test_nested_event_attachment_is_ineligible():
    """사건이 사건에 붙는 중첩(want→win)은 자동 salvage하지 않는다."""
    nested = EX("e1", T, AND(P("want.v.01", V("e1")),
                             P("Agent", V("e1"), V("x")),
                             P("Theme", V("e1"), V("e2"))))
    f = FA("x", P("person.n.01", V("x")),
           EX("e2", T, AND(P("win.v.01", V("e2")), nested)))
    with pytest.raises(ei.EventContractionRefused):
        ei.project_event_incidence(f)


def test_time_and_role_labels_are_dropped():
    with_time = FA("x", P("person.n.01", V("x")),
                   EX("e", T, AND(P("smile.v.01", V("e")),
                                  P("Agent", V("e"), V("x")),
                                  EX("t", T, AND(P("time.n.08", V("t")),
                                                 P("Time", V("e"), V("t")))))))
    assert same(ei.project_event_incidence(with_time),
                ei.project_event_incidence(ORACLE_SMILED))


def test_pure_and_idempotent():
    snap = copy.deepcopy(ORACLE_LIKE)
    once = ei.project_event_incidence(ORACLE_LIKE)
    assert ORACLE_LIKE == snap
    assert ei.project_event_incidence(once) == once


# ---- ProjectionSignalGate (판정 §7-8) ----

def test_signal_gate_accepts_retained_signal():
    rec = ei.projection_signal_check("PMB-t", ORACLE_SMILED)
    assert rec["verdict"] == "SIGNAL_RETAINED", rec


def test_signal_gate_rejects_collapsed_body():
    """기존 투영이 만들던 형태(본문 True)를 게이트가 거부해야 한다 —
    이 게이트가 없었기에 G3가 4번의 동결을 통과했다."""
    collapsed = FA("x", T, {"kind": "implies", "left": P("□", V("x")),
                            "right": dict(T)})
    rec = ei.projection_signal_check("PMB-t", collapsed, already_projected=True)
    assert rec["verdict"] == "SIGNAL_COLLAPSED"
    assert rec["collapsed_quantifiers"] == 1


def test_signal_gate_counts_every_target_quantifier():
    two_ok = ei.projection_signal_check("PMB-t", ORACLE_LIKE)
    assert two_ok["verdict"] == "SIGNAL_RETAINED"
    assert two_ok["target_quantifiers"] == 2


def test_role_order_does_not_determine_argument_order():
    """계보 정렬이 load-bearing임을 결박한다.

    같은 의미의 oracle을 role 술어 **등장 순서만 뒤집어** 쓴 것이다
    (SBN은 role 줄 순서를 보장하지 않는다). 등장 순서를 그대로 쓰면
    인자가 [x2, x0]이 되어 subject와 불일치하지만, 계보 순서(∀x0 외부 →
    ∃x2 내부)로 정렬하면 일치한다. 첫 뮤테이션 시도가 이 계약 없이는
    빗나갔다(P16) — 등장 순서와 계보 순서가 우연히 같았기 때문이다."""
    reordered = NOT(FA("x0", P("child.n.01", V("x0")),
                       EX("x2", P("apple.n.01", V("x2")),
                          EX("e", T, AND(P("like.v.03", V("e")),
                                         P("Stimulus", V("e"), V("x2")),
                                         P("Experiencer", V("e"), V("x0")))))))
    sig = ei.project_event_incidence(reordered)
    found = []
    def walk(n):
        if isinstance(n, dict):
            if n.get("kind") == "pred" and len(n.get("args", [])) == 2:
                found.append([a["name"] for a in n["args"]])
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)
    walk(sig)
    assert found and found[0] == ["x0", "x2"], found      # 계보 순서로 정규화
    assert same(sig, ei.project_event_incidence(SUBJECT_LIKE))


# ---- D-E2E-v1-29: count·prop도 target 양화다 ---------------------------
#
# 실물 대조(Redwoods 20214052 "Most are trim." / 21438006 "Three companies…")로
# 드러난 결함: 게이트가 target 양화를 `forall|exists`로만 세므로 기수·비례
# fixture는 `target_quantifiers=0`이 되어 SIGNAL_COLLAPSED로 떨어진다.
# fail-closed라 안전 쪽으로 틀리지만 **이유가 틀리다** — 신호가 붕괴한 것이
# 아니라 게이트가 그 양화를 보지 못한 것이다. 방언을 넓히면서 하류 게이트를
# 넓히지 않은 것이 원인(P9 계열의 역방향).

def test_count_is_counted_as_a_target_quantifier():
    f = {"kind": "count", "rel": "eq", "num": 3, "var": "x",
         "restriction": {"kind": "pred", "name": "company",
                         "args": [{"kind": "var", "name": "x"}]},
         "body": {"kind": "pred", "name": "trade",
                  "args": [{"kind": "var", "name": "x"}]}}
    out = ei.projection_signal_check("MRS-21438006", f, already_projected=True)
    assert out["target_quantifiers"] == 1, out
    assert out["verdict"] == "SIGNAL_RETAINED", out


def test_prop_is_counted_as_a_target_quantifier():
    f = {"kind": "prop", "rel": "most", "var": "x",
         "restriction": {"kind": "pred", "name": "generic_entity",
                         "args": [{"kind": "var", "name": "x"}]},
         "body": {"kind": "pred", "name": "trim",
                  "args": [{"kind": "var", "name": "x"}]}}
    out = ei.projection_signal_check("MRS-20214052", f, already_projected=True)
    assert out["target_quantifiers"] == 1, out
    assert out["verdict"] == "SIGNAL_RETAINED", out


def test_count_with_empty_body_still_collapses():
    """게이트를 넓히는 것이 게이트를 무르게 하는 것이어서는 안 된다(음성)."""
    f = {"kind": "count", "rel": "eq", "num": 3, "var": "x",
         "restriction": {"kind": "pred", "name": "company",
                         "args": [{"kind": "var", "name": "x"}]},
         "body": {"kind": "pred", "name": "True", "args": []}}
    out = ei.projection_signal_check("MRS-x", f, already_projected=True)
    assert out["target_quantifiers"] == 1 and out["collapsed_quantifiers"] == 1
    assert out["verdict"] == "SIGNAL_COLLAPSED"
