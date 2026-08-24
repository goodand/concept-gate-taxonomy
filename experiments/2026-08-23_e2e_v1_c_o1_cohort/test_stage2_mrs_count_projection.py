"""MRS_COUNT_PROJECTION_V1 계약 (D-E2E-v1-29 §9~§11). 이 파일이 계약 정본이다.

판정 §9가 명한 것: quantifier EP와 cardinal EP를 **같은 결박 변수로 연결될
때만** package한다. `card_rel`가 문장 어딘가 있다는 이유로 가장 가까운
quantifier에 붙이면 안 된다(판정 §11 말미).

§11의 require 7종 / reject 5종을 **문자 그대로** 인코딩한다. 완화 후보가
있어도 여기서 적용하지 않는다 — 측정 계약의 완화는 판정 사안이다(P19).

입력은 파싱된 MRS다(파싱 자체는 adapter의 몫, 이 층은 판정만 한다):

    {"top": "h1",
     "eps": [{"pred": str, "lbl": str, "args": {"ARG0": str, ...}}, ...],
     "hcons": [(hi, "QEQ", hj), ...]}

이 분리가 필요한 이유: fail-closed 판정을 파싱 오류와 섞으면 "거부됨"이
"읽지 못함"과 구별되지 않는다(저장소의 PASS/FAIL/BLOCKED 규율과 동형).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import _stage2_mrs_count_projection as mcp  # noqa: E402


def mrs(eps, hcons=(), top="h1"):
    return {"top": top, "eps": list(eps), "hcons": [tuple(h) for h in hcons]}


def q(pred="udef_q", lbl="h4", bv="x5", rstr="h6", body="h7"):
    return {"pred": pred, "lbl": lbl,
            "args": {"ARG0": bv, "RSTR": rstr, "BODY": body}}


def card(lbl="h8", arg1="x5", carg="3"):
    return {"pred": "card", "lbl": lbl,
            "args": {"ARG0": "e9", "ARG1": arg1, "CARG": carg}}


def noun(pred="_irony_n_1", lbl="h8", bv="x5"):
    return {"pred": pred, "lbl": lbl, "args": {"ARG0": bv}}


# ---- profile 정체 -------------------------------------------------------

def test_profile_identity():
    assert mcp.PROJECTION_PROFILE_ID == "MRS_COUNT_PROJECTION_V1"
    # D-29 §11의 5종은 D-31 Q31.2로 개정됐다 — 정본 집합은
    # `test_reject_codes_are_exactly_the_ruled_set`가 결박한다(아래).
    assert "card_and_quantifier_variable_disagree" in mcp.REJECT_CODES
    assert "unresolved_handle_constraint" in mcp.REJECT_CODES


def test_no_logical_equivalence_is_claimed():
    """§9는 측정용 package이고 동치 재작성이 아니다(D-28 §1과 동형)."""
    assert mcp.LOGICAL_EQUIVALENCE_CLAIM is False


# ---- require 7종 --------------------------------------------------------

def test_quantifier_and_cardinal_with_same_variable_packages():
    m = mrs([q(), card(), noun()],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["ok"] is True, out
    assert out["count"]["rel"] == "eq" and out["count"]["num"] == 3
    assert out["count"]["var"] == "x5"


def test_missing_quantifier_EP_is_refused():
    m = mrs([card(), noun()], hcons=[("h6", "QEQ", "h8")])
    assert mcp.package_count(m)["ok"] is False


def test_missing_cardinal_EP_is_refused():
    m = mrs([q(), noun()], hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    assert mcp.package_count(m)["ok"] is False


def test_non_integer_CARG_is_refused():
    m = mrs([q(), card(carg="a few"), noun()],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["ok"] is False and out["reject"] == "unsupported_numeric_relation"


# ---- reject 5종 ---------------------------------------------------------

def test_multiple_card_candidates_on_same_variable_is_refused():
    m = mrs([q(), card(carg="3"), card(lbl="h9", carg="4"), noun()],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["ok"] is False
    # D-31 Q31.2가 사유 코드를 개정했다: "표현 불가"가 아니라 "승인된 사상 없음".
    assert out["reject"] == "unsupported_compound_cardinal_mapping_v1"


def test_variable_disagreement_is_refused():
    """§11 말미: 가장 가까운 quantifier에 붙이지 마라."""
    m = mrs([q(bv="x5"), card(arg1="x99"), noun()],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["ok"] is False
    assert out["reject"] == "card_and_quantifier_variable_disagree"


def test_unresolved_RSTR_is_refused():
    m = mrs([q(), card(), noun()], hcons=[("h7", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["ok"] is False
    assert out["reject"] == "unresolved_handle_constraint"


def test_unresolved_BODY_is_refused():
    """§11 `BODY_resolved: true`를 문자 그대로. **실물 4/4가 여기 걸린다** —
    B.4 참조. 이 테스트는 그 사실을 계약 안에 보존한다."""
    m = mrs([q(), card(), noun()], hcons=[("h6", "QEQ", "h8")])
    out = mcp.package_count(m)
    assert out["ok"] is False
    assert out["reject"] == "unresolved_handle_constraint"


def test_two_quantifiers_sharing_the_cardinal_variable_is_ambiguous():
    """수치가 어느 양화에 붙는지 결정할 수 없으면 거부(§11 attachment)."""
    m = mrs([q(lbl="h4", bv="x5", rstr="h6", body="h7"),
             q(pred="_the_q", lbl="h10", bv="x5", rstr="h11", body="h12"),
             card(), noun()],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2"),
                   ("h11", "QEQ", "h8"), ("h12", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["ok"] is False
    assert out["reject"] == "numeric_scope_attachment_ambiguous"


# ---- 실물 4건 회귀 ------------------------------------------------------

REAL_ITEMS = {
    # B.1의 실물 판독값. BODY handle이 HCONS에 없다(MRS의 정상 형태).
    "21618050": mrs([q(lbl="h4", bv="x5", rstr="h6", body="h7"),
                     card(lbl="h8", arg1="x5", carg="2"),
                     noun("_irony_n_1", "h8", "x5")],
                    hcons=[("h6", "QEQ", "h8"), ("h1", "QEQ", "h2")]),
    "21438006": mrs([q(lbl="h4", bv="x5", rstr="h6", body="h7"),
                     card(lbl="h8", arg1="x5", carg="3"),
                     noun("_company_n_of", "h8", "x5")],
                    hcons=[("h19", "QEQ", "h20"), ("h11", "QEQ", "h12"),
                           ("h6", "QEQ", "h8"), ("h1", "QEQ", "h2")]),
}


@pytest.mark.parametrize("item_id", sorted(REAL_ITEMS))
def test_real_deepbank_items_are_refused_by_the_letter_of_the_ruling(item_id):
    """실물이 계약을 통과하지 못한다는 사실을 **기록**한다.

    이것은 버그가 아니라 판정 §11을 문자 그대로 구현한 결과다. MRS는
    최외곽 양화의 BODY를 scope resolution까지 비워 두므로, `BODY_resolved`를
    "HCONS에 제약됨"으로 읽으면 모든 record가 거부된다. 완화(예: "유일
    해소 가능"으로 읽기)는 **판정 사안**이며 여기서 하지 않는다.

    이 테스트가 GREEN인 동안 MRS source는 승격 불가다. 판정이 오면 이
    테스트를 **뒤집어야** 하고, 그때 뒤집는 것이 정당한 변경이다.
    """
    out = mcp.package_count(REAL_ITEMS[item_id])
    assert out["ok"] is False
    assert out["reject"] == "unresolved_handle_constraint"
    assert out["blocker_ref"] == "D29_S11_BODY_RESOLVED"


def test_the_same_real_item_would_package_if_BODY_were_constrained():
    """완화 후보가 실제로 실물을 통과시키는지 **측정만** 한다(적용 아님).

    BODY에 제약을 하나 넣은 가상 record는 통과한다 — 즉 실물이 막히는
    유일한 이유가 BODY 비제약임을 증명한다. 다른 결함은 없다.
    """
    m = REAL_ITEMS["21618050"]
    patched = mrs(m["eps"], hcons=list(m["hcons"]) + [("h7", "QEQ", "h2")])
    out = mcp.package_count(patched)
    assert out["ok"] is True
    assert out["count"] == {"rel": "eq", "num": 2, "var": "x5",
                            "restriction_label": "h8", "body_label": "h2"}


# ---- D-E2E-v1-31: E15 최상위 hard gate + E13 사유 정정 ------------------
#
# 판정 Q31.2:
#  * E15(`card.ARG1`이 개체 변수 아님) → `TYPE_MISMATCH`, **정본 hard gate**.
#    `count.var`는 개체 변수인데 MRS가 `i`/`e`를 주면 사상에 **타입 강제**가
#    필요하고 그것은 adapter 계약에 없다. 그래서 다른 모든 검사보다 앞이다.
#    운영 세션 실측: 게이트 순서 교환성이 성립하므로(최종 15,084 동일) 이
#    승격은 적격 결과를 바꾸지 않는다 — 계약 명확성의 문제다.
#  * E13(선언/범위 기수) 사유를 `UNSUPPORTED_COMPOUND_CARDINAL_MAPPING_V1`로.
#    "표현 불가"가 아니다 — 방언에는 `or`+복수 `count`를 조합할 능력이 있다.
#    **승인된 semantics-preserving 사상이 없어서** fail-closed reject다.
#    이 구분이 향후 방언 확장 없이 검증된 projection rule로 지원할 여지를 남긴다.

def q_i(pred="udef_q", lbl="h4", bv="i9", rstr="h6", body="h7"):
    return {"pred": pred, "lbl": lbl,
            "args": {"ARG0": bv, "RSTR": rstr, "BODY": body}}


def test_type_mismatch_is_a_reject_code():
    assert "type_mismatch" in mcp.REJECT_CODES


def test_non_entity_bound_variable_is_refused():
    """`card.ARG1 = i` — 측정 구문의 미명세 개체($1.5 billion의 i25)."""
    m = mrs([q(bv="i25"), card(arg1="i25"), noun(bv="i25")],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["ok"] is False
    assert out["reject"] == "type_mismatch"


def test_event_bound_variable_is_refused():
    m = mrs([q(bv="e9"), card(arg1="e9"), noun(bv="e9")],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    assert mcp.package_count(m)["reject"] == "type_mismatch"


def test_type_gate_precedes_every_other_check():
    """판정 §Q31.2: E15가 **최상위**다. 다른 결함이 함께 있어도 타입이 먼저다.

    이 record는 (a) 비개체 변수 (b) CARG 비정수 (c) RSTR 미해소 를 동시에
    갖는다. 셋 다 거부 사유지만 보고되는 것은 타입이어야 한다 — 그래야
    거부 사유 회계가 게이트 순서를 반영한다.
    """
    m = mrs([q(bv="i9"), card(arg1="i9", carg="a few"), noun(bv="i9")],
            hcons=[])
    assert mcp.package_count(m)["reject"] == "type_mismatch"


def test_entity_variable_still_reaches_the_later_checks():
    """게이트를 올리는 것이 뒤 검사를 가리면 안 된다(음성 방향)."""
    m = mrs([q(bv="x5"), card(arg1="x5", carg="a few"), noun(bv="x5")],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    assert mcp.package_count(m)["reject"] == "unsupported_numeric_relation"


def test_e13_reason_code_is_unsupported_mapping_not_inexpressible():
    """같은 변수에 card가 둘 — 판정이 명한 사유 코드로 보고한다."""
    m = mrs([q(), card(carg="2"), card(lbl="h9", carg="3"), noun()],
            hcons=[("h6", "QEQ", "h8"), ("h7", "QEQ", "h2")])
    out = mcp.package_count(m)
    assert out["ok"] is False
    assert out["reject"] == "unsupported_compound_cardinal_mapping_v1"
    # "표현 불가"를 주장하지 않는다는 것이 계약이다.
    assert out.get("intrinsically_unexpressible") is False


def test_compound_reject_code_replaces_the_old_one():
    assert "multiple_card_EP_candidates" not in mcp.REJECT_CODES
    assert "unsupported_compound_cardinal_mapping_v1" in mcp.REJECT_CODES


def test_reject_codes_are_exactly_the_ruled_set():
    """D-29 §11 5종 중 2종이 D-31로 개정됐다. 임의로 늘리지 않는다."""
    assert set(mcp.REJECT_CODES) == {
        "unsupported_compound_cardinal_mapping_v1",   # D-31 (구 multiple_card)
        "card_and_quantifier_variable_disagree",
        "unresolved_handle_constraint",
        "numeric_scope_attachment_ambiguous",
        "unsupported_numeric_relation",
        "type_mismatch",                              # D-31 신설, 최상위
    }
