"""GATE_C_AUDIT_TABLE_V1 계약 (D-E2E-v1-29 §17). 이 파일이 계약 정본이다.

§17이 요구한 것: Gate C에 `surface reading` / `MRS predicate` /
`assigned stratum`을 **같이** 표시한다. 이유가 명시돼 있다 — "Q28의 실패를
반복하지 않으려면". Q28의 실패는 표면형 `most`를 최상급과 구별하지 못해
비례 층이 오분류된 것이었다.

따라서 이 표는 장식이 아니라 **세 독립 신호의 교차 검사**다:
표면(사람이 읽는 것) · MRS 술어(gold가 말하는 것) · 층 배정(우리가 주장하는 것).
셋이 어긋나면 그 fixture는 사람 감사에 올라간다.

`surface_display`는 **기본값이 없다** — WSJ/LDC 재료의 문장 원문을 저장소에
커밋할 수 있는지가 미결 판정 항목(3차 조사 검증 §B.9-2)이기 때문이다.
호출자가 매번 명시해야 하며, 그래서 조용히 선택되는 일이 없다.
"""
from __future__ import annotations

import pytest

import _stage2_gate_c_table as gc


CAND_CARD = {"case_id": "MRS-21618050", "surface": "Two ironies intrude.",
             "mrs_preds": ["udef_q", "card", "_irony_n_1", "_intrude_v_1"],
             "stratum": "cardinal"}
CAND_PROP = {"case_id": "MRS-20214052", "surface": "Most are trim.",
             "mrs_preds": ["_most_q", "generic_entity", "_trim_a_1"],
             "stratum": "proportional"}
# Q28이 실제로 놓친 형태: 표면에 most가 있으나 gold는 최상급 형용사다.
CAND_SUPERLATIVE = {"case_id": "PMB-x", "surface": "The most beautiful flowers.",
                    "mrs_preds": ["_the_q", "superl", "_beautiful_a_1"],
                    "stratum": "proportional"}


def test_profile_identity():
    assert gc.GATE_C_PROFILE_ID == "GATE_C_AUDIT_TABLE_V1"


def test_required_columns_are_the_three_the_ruling_named():
    row = gc.audit_row(CAND_CARD, surface_display="full")
    for col in ("surface_reading", "mrs_predicate", "assigned_stratum"):
        assert col in row, col


def test_surface_display_has_no_default():
    """조용한 선택을 금지한다 — 권리 판정이 미결이다."""
    with pytest.raises(TypeError):
        gc.audit_row(CAND_CARD)


def test_surface_display_full_shows_the_sentence():
    row = gc.audit_row(CAND_CARD, surface_display="full")
    assert row["surface_reading"] == "Two ironies intrude."


def test_surface_display_sha256_withholds_the_sentence():
    """제한된 재료용 경로 — 표면형을 커밋하지 않고도 표가 성립해야 한다."""
    row = gc.audit_row(CAND_CARD, surface_display="sha256")
    assert "ironies" not in row["surface_reading"]
    assert len(row["surface_reading"]) == 64
    assert row["surface_withheld"] is True


def test_unknown_surface_display_is_refused():
    with pytest.raises(ValueError):
        gc.audit_row(CAND_CARD, surface_display="maybe")


def test_mrs_predicate_column_names_the_deciding_predicate():
    """모든 술어를 나열하지 않고 **층을 결정하는** 술어를 지목한다."""
    assert gc.audit_row(CAND_CARD, surface_display="full")["mrs_predicate"] == "card"
    assert gc.audit_row(CAND_PROP, surface_display="full")["mrs_predicate"] == "_most_q"


def test_consistent_candidate_is_marked_consistent():
    assert gc.audit_row(CAND_CARD, surface_display="full")["verdict"] == "CONSISTENT"
    assert gc.audit_row(CAND_PROP, surface_display="full")["verdict"] == "CONSISTENT"


def test_superlative_masquerading_as_proportional_is_flagged():
    """Q28의 실패 사례. 표면에 most가 있고 층은 proportional인데 gold에
    `_most_q`가 없다 → 사람 감사로 올려야 한다."""
    row = gc.audit_row(CAND_SUPERLATIVE, surface_display="full")
    assert row["verdict"] == "STRATUM_MRS_MISMATCH"
    assert row["mrs_predicate"] is None


def test_cardinal_stratum_without_card_predicate_is_flagged():
    bad = dict(CAND_CARD, mrs_preds=["udef_q", "_irony_n_1"])
    assert gc.audit_row(bad, surface_display="full")["verdict"] == "STRATUM_MRS_MISMATCH"


def test_proportional_predicate_under_cardinal_stratum_is_flagged():
    bad = dict(CAND_PROP, stratum="cardinal")
    assert gc.audit_row(bad, surface_display="full")["verdict"] == "STRATUM_MRS_MISMATCH"


def test_unknown_stratum_is_refused_not_passed_through():
    with pytest.raises(ValueError):
        gc.audit_row(dict(CAND_CARD, stratum="mystery"), surface_display="full")


def test_table_renders_all_rows_and_keeps_order():
    rows = gc.audit_table([CAND_CARD, CAND_PROP, CAND_SUPERLATIVE],
                          surface_display="sha256")
    assert [r["case_id"] for r in rows] == ["MRS-21618050", "MRS-20214052", "PMB-x"]


def test_markdown_render_marks_mismatches_visibly():
    md = gc.render_markdown(
        gc.audit_table([CAND_CARD, CAND_SUPERLATIVE], surface_display="full"))
    assert "STRATUM_MRS_MISMATCH" in md
    assert md.count("\n|") >= 3          # 헤더 + 구분선 + 2행


def test_mismatch_count_is_reported_for_gate_decision():
    summary = gc.audit_summary(
        gc.audit_table([CAND_CARD, CAND_PROP, CAND_SUPERLATIVE],
                       surface_display="full"))
    assert summary["total"] == 3
    assert summary["mismatch"] == 1
    assert summary["gate"] == "HUMAN_AUDIT_REQUIRED"


def test_all_consistent_still_requires_human_audit():
    """Gate C는 사람 감사다 — 표가 초록이어도 자동 통과가 아니다(D-27/D-28)."""
    summary = gc.audit_summary(
        gc.audit_table([CAND_CARD, CAND_PROP], surface_display="full"))
    assert summary["mismatch"] == 0
    assert summary["gate"] == "HUMAN_AUDIT_REQUIRED"
