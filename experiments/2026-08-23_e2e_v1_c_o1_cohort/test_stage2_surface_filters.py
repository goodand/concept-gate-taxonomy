"""D-E2E-v1-27 Q27.2·Q27.3: 동결 표면 필터 — RED 먼저.

Q27.2(b): PMB 대명사/고유명 fixture는 **표면 규칙으로 제외**한다
(projection folding 불허 — ∃ 참여자와 지정 개체는 논리적으로 비동치,
Male(e) 가정 하에서도 반례 존재). oracle synset만 보고 제거하는 것은
금지되므로 판정은 **문장 표면**을 본다.

**범위 주의(운영 세션 실측 오류의 기록)**: 첫 구현 시도에서 lexicon에
양화 대명사(nobody/everyone/someone…)를 넣었더니 quantifier_negation_scope
층이 1/4로 붕괴해 BLOCKED가 났다. 판정 §9가 지목한 것은
personal·possessive·demonstrative 3종이고, 양화 대명사는 **O1이 측정하려는
양화 어휘 자체**다(그 층의 주력이 "Not everyone …"이다). 3종으로 좁히면
5/4로 충족된다 — 이 계약이 그 경계를 고정한다.

Q27.3: control 재료는 표면 술어와 oracle projection 복잡도 **양층**을
통과해야 한다. 길이 상한은 판정 §14가 "운영이 재선별 전 확정"을 요구한
값으로, 판정이 제시한 engineering bound 15 토큰을 그대로 채택한다
(재료를 보고 조정한 값이 아니다).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

import _stage2_surface_filters as sf  # noqa: E402


def test_profile_identities():
    assert sf.PMB_PARTICIPANT_FILTER_ID == "PMB_O1_V1_PARTICIPANT_FILTER"
    assert sf.CONTROL_PROFILE_ID == "O1_CONTROL_ELIGIBILITY_V1"
    assert sf.CONTROL_MAX_TOKENS == 15


# ---- Q27.2: PMB 참여자 필터 ----

@pytest.mark.parametrize("sent", [
    "He is anything but a fool.",          # personal
    "Nobody encouraged him.",              # personal(him) — nobody는 양화라 무관
    "That is my book.",                    # possessive + demonstrative
    "These are cheaper than those.",       # demonstrative
    "She washed herself.",                 # reflexive
])
def test_pronoun_bearing_sentences_are_excluded(sent):
    assert sf.has_excluded_participant(sent) is True


@pytest.mark.parametrize("sent", [
    "Not everyone likes apples.",          # 양화 대명사 — 제외 대상 아님
    "Nobody laughed.",                     # 양화 대명사만
    "All humans eat.",
    "Not all children like apples.",
    "Someone must know something.",        # 부정대명사류 — 제외 대상 아님
])
def test_quantificational_pronouns_are_not_excluded(sent):
    assert sf.has_excluded_participant(sent) is False


def test_proper_names_mid_sentence_are_excluded():
    assert sf.has_excluded_participant("Not everyone in Boston laughed.") is True
    assert sf.has_excluded_participant("Apples are sweet.") is False   # 문두 대문자


def test_sentence_initial_proper_name_is_a_documented_leak():
    """근사의 알려진 한계: 문두 고유명("Tom laughed.")은 문두 대문자 규칙과
    구별할 수 없어 통과한다. tagger 의존을 피한 대가이며 **과잉 통과**
    방향의 누출이다. 실제 누출 규모는 PMB 재census에서 SBN `Name` role로
    교차 실측하고, 유의하면 상신한다(추측으로 규칙을 늘리지 않는다)."""
    assert sf.has_excluded_participant("Tom laughed.") is False
    assert "문두 고유명" in sf.has_excluded_participant.__doc__


def test_filter_never_inspects_oracle_synsets():
    """판정 §9: synset만 보고 제거하는 것 금지 — 이 함수의 서명이 문장뿐이다."""
    import inspect
    params = list(inspect.signature(sf.has_excluded_participant).parameters)
    assert params == ["sentence"]


# ---- Q27.3: control 표면 술어 ----

def test_control_surface_accepts_a_minimal_universal():
    ok, why = sf.control_surface_ok("All humans eat.")
    assert ok, why


@pytest.mark.parametrize("sent,reason", [
    ("There are few bookstores in this area.", "unsupported_quantifier"),
    ("He is anything but a fool.", "known_idiom"),   # 관용구 검사가 먼저 걸린다
    ("He laughed loudly.", "excluded_participant"),
    ("All right, every zorble glims.", "known_idiom"),
    ("Every zorble glims and some tikk praxes.", "quantifier_count"),
    ("Zorbles glim.", "quantifier_count"),           # 지원 한정사 0개
    (" ".join(["all"] + ["zorble"] * 20), "max_tokens"),
])
def test_control_surface_rejects_with_named_reason(sent, reason):
    ok, why = sf.control_surface_ok(sent)
    assert not ok and why == reason, (ok, why)


# ---- Q27.3: oracle projection 복잡도 층 ----

V = lambda n: {"kind": "var", "name": n}
P = lambda name, *a: {"kind": "pred", "name": name, "args": list(a)}
FA = lambda v, r, b: {"kind": "forall", "var": v, "restriction": r, "body": b}
EX = lambda v, r, b: {"kind": "exists", "var": v, "restriction": r, "body": b}
T = P("True")


def test_projection_complexity_accepts_single_target_quantifier():
    ok, why = sf.control_projection_ok("FOLIO-t", FA("x", P("h", V("x")), P("e", V("x"))))
    assert ok, why


def test_projection_complexity_rejects_nested_quantifier():
    ok, why = sf.control_projection_ok(
        "FOLIO-t", FA("x", T, EX("y", T, P("r", V("x"), V("y")))))
    assert not ok and why == "nested_or_extra_quantifier", why


def test_projection_complexity_rejects_unsupported_operator():
    ok, why = sf.control_projection_ok(
        "FOLIO-t", FA("x", T, {"kind": "or", "args": [P("a", V("x")), P("b", V("x"))]}))
    assert not ok and why in ("unsupported_operator", "not_satisfiable"), why


def test_projection_complexity_requires_satisfiability():
    """Gate A(형식 가능성)를 control 적격에도 요구 — 판정 §15."""
    ok, _ = sf.control_projection_ok("FOLIO-t", FA("x", P("h", V("x")), P("e", V("x"))))
    assert ok


def test_control_profile_is_documented_as_not_representative():
    """판정 §17: control은 모집단 대표 표본이 아님이 명문화돼야 한다."""
    assert "representative" in sf.__doc__.lower()
    assert "sanity" in sf.__doc__.lower()
