"""FIXTURE_DEDUP_V1 계약 (D-E2E-v1-31 Q31.3). 이 파일이 계약 정본이다.

판정이 두 경우를 **분리**하라고 명했다. 분리가 이 계약의 전부다.

    Case A  동일 표면 + 동일 gold artifact
            → 실제로 같은 trial이다. `COLLAPSE`, 대표자는 **결정적 규칙**
              (의미론적으로 고르지 않는다)

    Case B  동일 표면 + **상이한** gold artifact
            → 중복이 아니라 **oracle 신원 충돌**이다. subject가 보는 입력은
              같은데 채점 기준이 둘이므로, 같은 답이 한쪽에서 정답이고 다른
              쪽에서 오답이 된다. `ORACLE_COLLISION`, cohort 부적격,
              **자동 대표자 선택 금지**

왜 자동 선택이 금지인가: 한 gold를 고르면 **fixture 선별 단계가 oracle의
모호성을 해결해 버린다.** 그 판단은 선별의 권한이 아니다.

실측(2026-08-24, Open SDP 1.2 37,060 record): Case A 83그룹/초과 205건,
**Case B 69그룹/395건** — Case B가 더 크다. 표면 기준으로 묶지 않으면 그
아래의 더 큰 문제가 보이지 않는다.
"""
from __future__ import annotations

import pytest

import _stage2_dedup as dd


def item(iid, text, gold):
    return {"item_id": iid, "text_sha256": text, "gold_sha256": gold}


def test_profile_identity():
    assert dd.DEDUP_PROFILE_ID == "FIXTURE_DEDUP_V1"


def test_unique_items_pass_through_untouched():
    items = [item("b", "T1", "M1"), item("a", "T2", "M2")]
    out = dd.partition(items)
    assert [i["item_id"] for i in out["eligible"]] == ["b", "a"]   # 순서 보존
    assert out["collapsed"] == [] and out["collisions"] == []


# ---- Case A: 동일 표면 + 동일 gold ------------------------------------

def test_exact_duplicate_collapses_to_one():
    items = [item("b2", "T", "M"), item("a1", "T", "M"), item("c3", "T", "M")]
    out = dd.partition(items)
    assert len(out["eligible"]) == 1
    assert len(out["collapsed"]) == 2


def test_representative_is_deterministic_minimum_item_id():
    """판정: 의미론적으로 고르지 말고 결정적 규칙으로. 최소 item_id를 쓴다."""
    out = dd.partition([item("b2", "T", "M"), item("a1", "T", "M")])
    assert out["eligible"][0]["item_id"] == "a1"


def test_representative_does_not_depend_on_input_order():
    a = dd.partition([item("b2", "T", "M"), item("a1", "T", "M")])
    b = dd.partition([item("a1", "T", "M"), item("b2", "T", "M")])
    assert a["eligible"][0]["item_id"] == b["eligible"][0]["item_id"] == "a1"


def test_collapsed_records_name_their_representative():
    out = dd.partition([item("a1", "T", "M"), item("b2", "T", "M")])
    assert out["collapsed"][0]["represented_by"] == "a1"
    assert out["collapsed"][0]["reason"] == "exact_duplicate"


# ---- Case B: 동일 표면 + 상이 gold ------------------------------------

def test_same_text_different_gold_is_a_collision_not_a_duplicate():
    items = [item("a1", "T", "M1"), item("b2", "T", "M2")]
    out = dd.partition(items)
    assert out["eligible"] == []
    assert out["collapsed"] == []
    assert len(out["collisions"]) == 2
    assert all(c["reason"] == "oracle_collision" for c in out["collisions"])


def test_collision_selects_no_representative():
    """자동 대표자 선택 금지 — 판정의 명시 금지 사항."""
    out = dd.partition([item("a1", "T", "M1"), item("b2", "T", "M2")])
    assert all("represented_by" not in c for c in out["collisions"])


def test_collision_blocks_every_member_not_just_the_extras():
    """충돌 그룹은 **전원** 부적격이다. 하나를 남기면 임의 선택이 된다."""
    out = dd.partition([item("a", "T", "M1"), item("b", "T", "M1"),
                        item("c", "T", "M2")])
    assert out["eligible"] == []
    assert {c["item_id"] for c in out["collisions"]} == {"a", "b", "c"}


def test_collision_takes_precedence_over_collapse_within_a_group():
    """같은 표면 안에 exact 쌍과 상이 gold가 섞이면 그룹 전체가 충돌이다."""
    out = dd.partition([item("a", "T", "M1"), item("b", "T", "M1"),
                        item("c", "T", "M2")])
    assert out["collapsed"] == []


# ---- 회계: 아무 item도 사라지지 않는다 ---------------------------------

def test_every_input_item_is_accounted_for():
    items = [item("a", "T1", "M1"), item("b", "T1", "M1"),
             item("c", "T2", "M2"), item("d", "T2", "M3"),
             item("e", "T3", "M4")]
    out = dd.partition(items)
    seen = ([i["item_id"] for i in out["eligible"]]
            + [i["item_id"] for i in out["collapsed"]]
            + [i["item_id"] for i in out["collisions"]])
    assert sorted(seen) == ["a", "b", "c", "d", "e"]
    assert len(seen) == len(set(seen)), "한 item이 두 범주에 들어갔다"


def test_summary_counts_match_the_partition():
    items = [item("a", "T1", "M1"), item("b", "T1", "M1"),
             item("c", "T2", "M2"), item("d", "T2", "M3")]
    s = dd.summary(dd.partition(items))
    assert s == {"profile": "FIXTURE_DEDUP_V1", "input": 4,
                 "eligible": 1, "collapsed": 1, "collisions": 2}


# ---- 입력 계약 위반은 조용히 통과시키지 않는다 -------------------------

def test_missing_gold_hash_is_refused():
    with pytest.raises(ValueError):
        dd.partition([{"item_id": "a", "text_sha256": "T"}])


def test_missing_item_id_is_refused():
    with pytest.raises(ValueError):
        dd.partition([{"text_sha256": "T", "gold_sha256": "M"}])


def test_duplicate_item_id_is_refused():
    """같은 item_id가 둘이면 신원이 깨진 것이다 — 대표자 선택이 무의미해진다."""
    with pytest.raises(ValueError):
        dd.partition([item("a", "T1", "M1"), item("a", "T2", "M2")])
