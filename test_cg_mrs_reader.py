"""cg_mrs_reader 계약 — MRS 직렬화 → 파싱 구조. 이 파일이 계약 정본이다.

**판정 층과 분리한다**: 이 모듈은 텍스트를 구조로만 바꾼다. fail-closed
적격 판정은 `MRS_COUNT_PROJECTION_V1`(실험층)의 몫이다. 섞으면 "거부됨"과
"읽지 못함"이 구별되지 않는다.

시험 입력은 **실물**이다 — 발명하지 않았다(P15). 두 출처의 같은 문장:
  * 변종 A: Open SDP 1.2 `sdp/2015/eds/21618050.mrs` (LTOP, `_rel` 접미사,
    인용된 술어명)
  * 변종 B: Redwoods export mirror `DeepBank1.1/21618050` (TOP, 접미사·
    인용 없음)
두 직렬화는 **구조가 동일**해야 한다 — 그것이 이 파서의 핵심 계약이다.
"""
from __future__ import annotations

import pytest

from conceptgate import cg_mrs_reader as rd

# --- 실물 변종 A (Open SDP 1.2, 바이트 그대로) ---------------------------
VARIANT_A = ''' [ LTOP: h1
   INDEX: e3 [ e SF: PROP TENSE: PRES MOOD: INDICATIVE PROG: - PERF: - ]
   RELS: <
          [ udef_q_rel<0:3>
            LBL: h4
            ARG0: x5 [ x PERS: 3 NUM: PL ]
            RSTR: h6
            BODY: h7 ]
          [ card_rel<0:3>
            LBL: h8
            ARG0: e9 [ e SF: PROP TENSE: UNTENSED MOOD: INDICATIVE ]
            ARG1: x5
            CARG: "2" ]
          [ "_irony_n_1_rel"<4:11>
            LBL: h8
            ARG0: x5 ]
          [ "_intrude_v_1_rel"<12:20>
            LBL: h2
            ARG0: e3
            ARG1: x5 ] >
   HCONS: < h6 QEQ h8 h1 QEQ h2 > ]
'''

# --- 실물 변종 B (Redwoods export mirror, 바이트 그대로) ----------------
VARIANT_B = ''' [ TOP: h1
   INDEX: e3 [ e SF: PROP TENSE: PRES MOOD: INDICATIVE PROG: - PERF: - ]
   RELS: <
          [ udef_q<0:3>
            LBL: h4
            ARG0: x5 [ x PERS: 3 NUM: PL ]
            RSTR: h6
            BODY: h7 ]
          [ card<0:3>
            LBL: h8
            ARG0: e9 [ e SF: PROP TENSE: UNTENSED MOOD: INDICATIVE PROG: - PERF: - ]
            ARG1: x5
            CARG: "2" ]
          [ _irony_n_1<4:11>
            LBL: h8
            ARG0: x5 ]
          [ _intrude_v_1<12:20>
            LBL: h2
            ARG0: e3
            ARG1: x5 ] >
   HCONS: < h6 QEQ h8 h1 QEQ h2 > ]
'''


def test_top_is_read_under_both_names():
    """LTOP(구 직렬화)와 TOP(신)을 같은 자리로 읽는다."""
    assert rd.read_mrs(VARIANT_A)["top"] == "h1"
    assert rd.read_mrs(VARIANT_B)["top"] == "h1"


def test_index_is_read():
    assert rd.read_mrs(VARIANT_A)["index"] == "e3"


def test_ep_count_and_order_preserved():
    """EP 순서는 보존한다 — 재배열은 금지된 정규화다(D-25/D-27)."""
    eps = rd.read_mrs(VARIANT_A)["eps"]
    assert len(eps) == 4
    assert [e["pred"] for e in eps][:2] == ["udef_q", "card"]


def test_rel_suffix_and_quotes_are_normalised():
    """`"_irony_n_1_rel"` → `_irony_n_1`. 두 변종이 같은 술어명이 되어야 한다."""
    a = [e["pred"] for e in rd.read_mrs(VARIANT_A)["eps"]]
    b = [e["pred"] for e in rd.read_mrs(VARIANT_B)["eps"]]
    assert a == b == ["udef_q", "card", "_irony_n_1", "_intrude_v_1"]


def test_two_real_serialisations_are_structurally_identical():
    """계약의 핵심: 같은 item의 두 출처가 같은 구조를 준다."""
    assert rd.read_mrs(VARIANT_A) == rd.read_mrs(VARIANT_B)


def test_spans_are_read_as_integer_pairs():
    eps = rd.read_mrs(VARIANT_A)["eps"]
    assert eps[0]["span"] == (0, 3)
    assert eps[3]["span"] == (12, 20)


def test_labels_and_arguments():
    eps = {e["pred"]: e for e in rd.read_mrs(VARIANT_A)["eps"]}
    assert eps["udef_q"]["lbl"] == "h4"
    assert eps["udef_q"]["args"] == {"ARG0": "x5", "RSTR": "h6", "BODY": "h7"}
    assert eps["card"]["args"] == {"ARG0": "e9", "ARG1": "x5", "CARG": "2"}


def test_variable_feature_structures_are_skipped_not_merged():
    """`ARG0: x5 [ x PERS: 3 NUM: PL ]`에서 feature가 인자로 새면 안 된다."""
    eps = {e["pred"]: e for e in rd.read_mrs(VARIANT_A)["eps"]}
    assert "PERS" not in eps["udef_q"]["args"]
    assert "TENSE" not in eps["card"]["args"]


def test_label_sharing_is_recoverable():
    """card와 명사가 LBL을 공유한다 — attachment 판정에 필요한 사실."""
    eps = {e["pred"]: e for e in rd.read_mrs(VARIANT_A)["eps"]}
    assert eps["card"]["lbl"] == eps["_irony_n_1"]["lbl"] == "h8"


def test_hcons_pairs():
    assert rd.read_mrs(VARIANT_A)["hcons"] == [("h6", "QEQ", "h8"),
                                               ("h1", "QEQ", "h2")]


def test_carg_stays_a_string():
    """수치 해석은 판정층의 몫 — 파서가 int로 바꾸면 `"a few"`를 잃는다."""
    eps = {e["pred"]: e for e in rd.read_mrs(VARIANT_A)["eps"]}
    assert eps["card"]["args"]["CARG"] == "2"
    assert isinstance(eps["card"]["args"]["CARG"], str)


def test_output_feeds_the_projection_contract_unchanged():
    """파서 산출이 MRS_COUNT_PROJECTION_V1의 입력 계약을 그대로 만족한다."""
    m = rd.read_mrs(VARIANT_A)
    assert set(m) >= {"top", "eps", "hcons"}
    assert all(set(e) >= {"pred", "lbl", "args"} for e in m["eps"])


# ---- fail-closed: 읽지 못하는 것을 읽은 척하지 않는다 -------------------

def test_empty_input_is_refused():
    with pytest.raises(rd.MrsSyntaxError):
        rd.read_mrs("   ")


def test_missing_rels_is_refused():
    with pytest.raises(rd.MrsSyntaxError):
        rd.read_mrs(" [ LTOP: h1 INDEX: e3 HCONS: < > ]")


def test_unbalanced_brackets_are_refused():
    with pytest.raises(rd.MrsSyntaxError):
        rd.read_mrs(" [ LTOP: h1 RELS: < [ udef_q<0:3> LBL: h4 ARG0: x5 ")


def test_malformed_hcons_is_refused():
    bad = VARIANT_A.replace("h6 QEQ h8", "h6 QQQ h8")
    with pytest.raises(rd.MrsUnsupported):
        rd.read_mrs(bad)


def test_reader_is_idempotent_on_its_own_serialisation_free_output():
    once = rd.read_mrs(VARIANT_A)
    assert rd.read_mrs(VARIANT_A) == once
