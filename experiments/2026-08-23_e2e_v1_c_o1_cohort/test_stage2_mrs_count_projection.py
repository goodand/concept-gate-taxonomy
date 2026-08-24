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
    assert set(mcp.REJECT_CODES) == {
        "multiple_card_EP_candidates",
        "card_and_quantifier_variable_disagree",
        "unresolved_handle_constraint",
        "numeric_scope_attachment_ambiguous",
        "unsupported_numeric_relation",
    }


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
    assert out["reject"] == "multiple_card_EP_candidates"


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
