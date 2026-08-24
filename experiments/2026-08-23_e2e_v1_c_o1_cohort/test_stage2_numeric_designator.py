"""E14 결정적 detector 계약 (D-E2E-v1-31 Q31.2). 이 파일이 계약 정본이다.

판정이 명한 것:

    E14:
      semantic_category: numeric_designator
      detector:
        deterministic: required
        fixture_specific_exception_table: forbidden

그리고 **자동 detector가 안전하게 확정할 수 없으면 `INELIGIBLE / NEEDS_AUDIT`
로 보내야지 추측해서 cardinal로 채택해서는 안 된다.**

따라서 이 detector는 2값(기수/지정자)이 아니라 **3값**이다:

    CARDINAL   — 개수를 양화한다. 기수 후보로 진행
    DESIGNATOR — 수사가 명칭의 일부다. 배제
    NEEDS_AUDIT— 결정적으로 가릴 수 없다. **cardinal로 채택 금지**, 사람 감사

`NEEDS_AUDIT`이 이 계약의 존재 이유다. 2값이면 애매한 것을 어느 쪽으로든
추측하게 되고, 판정이 그것을 금지했다.

**fixture별 예외표 금지**: 특정 item_id를 열거해 통과/배제시키는 경로를 두지
않는다. 판별은 구조와 어휘 부류로만 한다 — 그래야 source-general이다.
"""
from __future__ import annotations

import pytest

import _stage2_numeric_designator as nd


def ep(pred, lbl="h8", **args):
    return {"pred": pred, "lbl": lbl, "args": dict(args)}


def mrs(eps, hcons=(), top="h1"):
    return {"top": top, "eps": list(eps), "hcons": [tuple(h) for h in hcons]}


def test_profile_identity():
    assert nd.DETECTOR_ID == "NUMERIC_DESIGNATOR_DETECTOR_V1"
    assert set(nd.VERDICTS) == {"CARDINAL", "DESIGNATOR", "NEEDS_AUDIT"}


def test_no_fixture_specific_exception_table():
    """판정이 금지한 경로가 코드에 없어야 한다."""
    src = nd.__doc__ or ""
    import inspect
    body = inspect.getsource(nd)
    for banned in ("item_id", "20154005", "EXCEPTION_ITEMS", "ALLOWLIST"):
        assert banned not in body, f"fixture별 예외 경로 흔적: {banned}"


# ---- DESIGNATOR: 수사가 명칭의 일부 ------------------------------------

def test_compound_with_proper_name_is_designator():
    """`Intel 286 microprocessors` — `compound`가 수사를 명칭에 묶는다."""
    m = mrs([ep("udef_q", "h4", ARG0="x5", RSTR="h6", BODY="h7"),
             ep("card", "h8", ARG0="e9", ARG1="x5", CARG="286"),
             ep("compound", "h8", ARG0="e10", ARG1="x5", ARG2="x11"),
             ep("proper_q", "h12", ARG0="x11", RSTR="h13", BODY="h14"),
             ep("named", "h15", ARG0="x11", CARG="Intel"),
             ep("_microprocessor_n_1", "h8", ARG0="x5")],
            hcons=[("h6", "QEQ", "h8"), ("h13", "QEQ", "h15")])
    assert nd.classify(m, "x5")["verdict"] == "DESIGNATOR"


def test_designator_reason_is_reported():
    m = mrs([ep("card", "h8", ARG1="x5", CARG="286"),
             ep("compound", "h8", ARG1="x5", ARG2="x11"),
             ep("named", "h15", ARG0="x11", CARG="Intel")],
            hcons=[])
    assert nd.classify(m, "x5")["reason"] == "cardinal_inside_name_compound"


def test_card_on_a_named_entity_is_designator():
    """수사가 `named`와 같은 label을 공유하면 명칭이다."""
    m = mrs([ep("card", "h8", ARG1="x5", CARG="747"),
             ep("named", "h8", ARG0="x5", CARG="Boeing")], hcons=[])
    assert nd.classify(m, "x5")["verdict"] == "DESIGNATOR"


# ---- CARDINAL: 가산 명사를 세는 경우 -----------------------------------

def test_plain_count_noun_is_cardinal():
    """`Two ironies intrude.` — card가 보통명사와 label을 공유하고 명칭 없음."""
    m = mrs([ep("udef_q", "h4", ARG0="x5", RSTR="h6", BODY="h7"),
             ep("card", "h8", ARG0="e9", ARG1="x5", CARG="2"),
             ep("_irony_n_1", "h8", ARG0="x5"),
             ep("_intrude_v_1", "h2", ARG0="e3", ARG1="x5")],
            hcons=[("h6", "QEQ", "h8"), ("h1", "QEQ", "h2")])
    assert nd.classify(m, "x5")["verdict"] == "CARDINAL"


def test_bare_generic_entity_is_cardinal():
    """`Five were interested.` — 무어휘 제한식도 기수다(D-30 Q30.6)."""
    m = mrs([ep("udef_q", "h6", ARG0="x5", RSTR="h7", BODY="h8"),
             ep("card", "h4", ARG0="e9", ARG1="x5", CARG="5"),
             ep("generic_entity", "h4", ARG0="x5")],
            hcons=[("h7", "QEQ", "h4")])
    assert nd.classify(m, "x5")["verdict"] == "CARDINAL"


# ---- NEEDS_AUDIT: 결정적으로 가릴 수 없는 경우 --------------------------

def test_no_card_for_that_variable_is_needs_audit_not_cardinal():
    """판별할 대상이 없으면 통과시키지 않는다 — fail-closed 방향."""
    m = mrs([ep("_irony_n_1", "h8", ARG0="x5")], hcons=[])
    assert nd.classify(m, "x5")["verdict"] == "NEEDS_AUDIT"


def test_card_with_no_colabeled_content_is_needs_audit():
    """card가 홀로 있으면 명칭인지 개수인지 구조가 말해주지 않는다."""
    m = mrs([ep("card", "h8", ARG1="x5", CARG="3")], hcons=[])
    assert nd.classify(m, "x5")["verdict"] == "NEEDS_AUDIT"


def test_unknown_word_restriction_is_needs_audit():
    """`_u_unknown`(ERG 어휘 미지)은 보통명사로 단정할 수 없다 — E12 표지."""
    m = mrs([ep("card", "h8", ARG1="x5", CARG="2"),
             ep("_exorcisms/NNS_u_unknown", "h8", ARG0="x5")], hcons=[])
    out = nd.classify(m, "x5")
    assert out["verdict"] == "NEEDS_AUDIT"
    assert out["reason"] == "unknown_word_restriction"


def test_needs_audit_is_never_promoted_to_cardinal():
    """3값 계약의 핵심: 애매한 것을 추측으로 채택하지 않는다."""
    ambiguous = mrs([ep("card", "h8", ARG1="x5", CARG="3")], hcons=[])
    out = nd.classify(ambiguous, "x5")
    assert out["verdict"] != "CARDINAL"
    assert nd.eligible_as_cardinal(out) is False


def test_eligible_helper_admits_only_cardinal():
    assert nd.eligible_as_cardinal({"verdict": "CARDINAL"}) is True
    assert nd.eligible_as_cardinal({"verdict": "DESIGNATOR"}) is False
    assert nd.eligible_as_cardinal({"verdict": "NEEDS_AUDIT"}) is False


def test_verdict_is_deterministic():
    m = mrs([ep("card", "h8", ARG1="x5", CARG="2"),
             ep("_irony_n_1", "h8", ARG0="x5")], hcons=[])
    assert nd.classify(m, "x5") == nd.classify(m, "x5")


def test_unknown_variable_is_refused_not_guessed():
    m = mrs([ep("card", "h8", ARG1="x5", CARG="2")], hcons=[])
    assert nd.classify(m, "x99")["verdict"] == "NEEDS_AUDIT"
