"""D-E2E-v1-24 Q24.2: predicate_label_reachability — RED 먼저.

판정 §4: FOLIO fixture의 모든 oracle 술어는 codec 통과 후 **동결된 기계
규칙**으로 문장에서 파생 가능해야 적격이다. 규칙은 LLM 의미 판단이 아니라
결정론 함수이고, Path A(실 adapter의 IR 술어)와 Path B(FOL 문자열 독립
추출)가 **같은 라벨 집합**을 내야 한다(불일치 = 판정 불가, 부적격 처리).

동결 파생 규칙 (이 계약이 규칙의 정본이다 — 구현은 이것을 만족해야 한다):
  후보 집합 = 문장의 소문자 영숫자 토큰들에서
    (i)  연속 토큰 1~4개를 구분자 없이 이어붙인 문자열 전부
    (ii) 각 토큰의 복수형 접미 제거형: w가 "es"로 끝나면 w[:-2], "s"로
         끝나면 w[:-1] (기계적 문자열 절단 — lemma 사전·형태소 분석 아님)
  도달 가능 ⇔ codec(라벨) ∈ 후보 집합.
왜 (ii)가 codec의 lemma 금지와 모순이 아닌가: codec은 **채점 비교층**에서
라벨을 바꾸는 장치라 어휘 변형이 금지되지만(D-24 §2), 이 규칙은 **적격성
판정**에서 후보 집합을 넓히는 장치다 — oracle 라벨은 절대 변형되지 않는다.

재료는 전부 발명(P15 대응 — corpus 원문은 repo에 0바이트).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import scan_folio_eligibility_v2 as v2  # noqa: E402


# --- 파생 규칙 (동결 함수) ---


def test_candidates_include_words_and_contiguous_joins():
    c = v2.derive_candidates("Every zorble that can catch florps is happy.")
    assert "zorble" in c
    assert "cancatch" in c            # 연속 2토큰 이어붙임
    assert "catchflorps" in c         # 이어붙임은 인접만 — 임의 조합 아님
    assert "zorblecatch" not in c     # 비인접 조합 금지


def test_candidates_include_mechanical_plural_strips():
    c = v2.derive_candidates("Tikks and boxes.")
    assert "tikk" in c                # "tikks"[:-1]
    assert "box" in c                 # "boxes"[:-2]
    assert "tikks" in c and "boxes" in c


def test_reachable_is_case_insensitive_via_codec():
    assert v2.label_reachable("CanCatch", "People who can catch balls.")
    assert v2.label_reachable("Ball", "People who can catch balls.")


def test_unreachable_authored_vocabulary():
    assert not v2.label_reachable("SpectatorsBetOn",
                                  "The zorbles pursue the florp while people bet.")
    assert not v2.label_reachable("Racing", "A zorble is fast if it is in a race.")


def test_reserved_true_is_always_reachable():
    """중립 제한식의 True는 oracle 어휘가 아니라 IR 구조 토큰 — 도달성 판정 제외."""
    assert v2.label_reachable("True", "Any sentence at all.")


# --- Path A / Path B 라벨 추출과 합의 ---


def test_path_labels_agree_on_wellformed_fol():
    fol = "∀x (Zorble(x) → CanCatch(x, x))"
    a = v2.path_a_labels(fol)
    b = v2.path_b_labels(fol)
    assert a == b == {"Zorble", "CanCatch"}


def test_path_b_ignores_variables_and_arguments():
    fol = "∀x ∃y (Know(x, y) ∧ Good(x, widereciever))"
    assert v2.path_b_labels(fol) == {"Know", "Good"}


def test_fixture_reachability_requires_path_agreement():
    """두 경로의 라벨 집합이 다르면 도달성 판정 자체를 내리지 않는다(부적격)."""
    verdict = v2.fixture_reachability(
        "∀x (Zorble(x) → Glims(x))", "Every zorble glims.")
    assert verdict == {"reachable": True, "paths_agree": True,
                       "unreachable_labels": []}
    bad = v2.fixture_reachability(
        "∀x (Zorble(x) → SpectatorsBetOn(x))", "Every zorble glims.")
    assert bad["paths_agree"] is True
    assert bad["reachable"] is False
    assert bad["unreachable_labels"] == ["SpectatorsBetOn"]


# --- 가드 음성 (저장소 게이트 요구) ---


def test_empty_sentence_refused():
    with pytest.raises(ValueError):
        v2.derive_candidates("   ")
