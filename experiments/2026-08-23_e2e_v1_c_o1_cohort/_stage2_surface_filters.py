"""동결 표면 필터 — PMB 참여자 제외 + control 적격성 (D-E2E-v1-27).

Q27.2(b): PMB의 대명사/고유명 fixture를 **문장 표면 규칙으로** 제외한다.
projection folding은 불허됐다 — ∃ 참여자와 지정 개체는 논리적으로 비동치
이며(2원소·지정개체 고정 16 해석 중 반례 5, Male(e) 가정 하에서도 8 중 1),
추측하면 oracle adapter가 semantic judge가 된다(판정 §7-8). 판정 §9는
oracle synset만 보고 제거하는 것을 금지하므로 이 필터는 **문장만** 본다.

lexicon 범위는 판정 §9의 3종 + 재귀형이다: personal·possessive·
demonstrative(+reflexive). 양화·부정·의문 대명사(nobody/everyone/someone/
who…)는 **제외하지 않는다** — O1이 측정하려는 양화 어휘 자체이고,
quantifier_negation_scope 층의 주력 재료가 "Not everyone …"이다. 운영
세션의 첫 시도가 이것들을 넣어 그 층을 1/4로 붕괴시켜 BLOCKED를 냈고,
3종으로 좁혀 5/4 충족을 실측했다.

Q27.3: control 적격성 `O1_CONTROL_ELIGIBILITY_V1` — 표면층과 oracle
projection 복잡도층을 **모두** 통과해야 한다. control은 모집단을 대표하는
representative 표본이 **아니라** measurement-chain의 sanity check이므로
본 코호트보다 엄격한 단순성 조건을 쓴다(판정 §17). 길이 상한은 판정 §14가
재선별 **전** 확정을 요구한 값으로, 판정이 제시한 engineering bound 15를
그대로 채택한다(재료를 보고 조정한 값이 아니다).
"""
from __future__ import annotations

import re
from typing import Any

PMB_PARTICIPANT_FILTER_ID = "PMB_O1_V1_PARTICIPANT_FILTER"
CONTROL_PROFILE_ID = "O1_CONTROL_ELIGIBILITY_V1"
CONTROL_MAX_TOKENS = 15

PERSONAL = {"i", "me", "you", "he", "him", "she", "her", "it",
            "we", "us", "they", "them"}
POSSESSIVE = {"my", "mine", "your", "yours", "his", "hers", "its",
              "our", "ours", "their", "theirs"}
REFLEXIVE = {"myself", "yourself", "yourselves", "himself", "herself",
             "itself", "ourselves", "themselves"}
DEMONSTRATIVE = {"this", "that", "these", "those"}
EXCLUDED_PARTICIPANT_LEXICON = PERSONAL | POSSESSIVE | REFLEXIVE | DEMONSTRATIVE

# 판정 §9 목록 밖 — 제외하지 않는다(측정 대상 어휘). 문서화 목적의 상수.
QUANTIFICATIONAL_PRONOUNS = {
    "nobody", "somebody", "someone", "anybody", "anyone", "everybody",
    "everyone", "something", "anything", "everything", "nothing",
    "one", "who", "whom", "whose", "none"}

SUPPORTED_QUANTIFIER_LEXICON = ("all", "every", "each", "some", "no")
UNSUPPORTED_QUANTIFIER_LEXICON = ("few", "fewer", "several", "many", "most",
                                  "both", "either", "neither")
KNOWN_IDIOMS = ("anything but", "all right", "at all", "all of a sudden",
                "no doubt", "no longer", "some day")


def _tokens(sentence: str) -> list:
    return re.findall(r"[A-Za-z']+", sentence)


def has_excluded_participant(sentence: str) -> bool:
    """대명사(3종+재귀) 또는 고유명이 문장에 있는가 (D-27 Q27.2 표면 규칙).

    고유명 판정은 문두를 제외한 대문자 시작 토큰 — 결정론 근사이며 tagger
    의존을 피한다(감사 가능성 우선). **알려진 누출: 문두 고유명**("Tom
    laughed.")은 일반 문두 대문자와 구별할 수 없어 통과한다. 누출 규모는
    PMB 재census에서 SBN `Name` role로 교차 실측하며, 유의하면 상신한다.
    """
    toks = _tokens(sentence)
    if any(t.lower() in EXCLUDED_PARTICIPANT_LEXICON for t in toks):
        return True
    return any(t[0].isupper() for t in toks[1:])


def control_surface_ok(sentence: str) -> tuple:
    """control 표면 술어. 반환: (ok, reason) — reason은 실패 사유 이름."""
    low = sentence.lower()
    toks = _tokens(sentence)
    if len(toks) > CONTROL_MAX_TOKENS:
        return False, "max_tokens"
    if any(idiom in low for idiom in KNOWN_IDIOMS):
        return False, "known_idiom"
    if any(w in UNSUPPORTED_QUANTIFIER_LEXICON for w in (t.lower() for t in toks)):
        return False, "unsupported_quantifier"
    if has_excluded_participant(sentence):
        return False, "excluded_participant"
    n = sum(1 for t in toks if t.lower() in SUPPORTED_QUANTIFIER_LEXICON)
    if n != 1:
        return False, "quantifier_count"
    return True, "ok"


def control_projection_ok(case_id: str, oracle_ir: dict) -> tuple:
    """control oracle projection 복잡도 술어 (판정 §15).

    target 양화 정확히 1개 · 중첩/추가 양화 0 · 미지원 연산자 0 ·
    Gate A(measurement satisfiability) 통과.
    """
    from _stage2_scope_projection import project_scope_for_case
    import _stage2_satisfiability as sat
    try:
        sig = project_scope_for_case(case_id, oracle_ir)
    except Exception as exc:
        return False, f"projection_failed:{type(exc).__name__}"
    quants, unsupported = [], []

    def walk(n: Any) -> None:
        if isinstance(n, dict):
            k = n.get("kind")
            if k in ("forall", "exists"):
                quants.append(k)
            elif k not in ("and", "not", "implies", "pred", "var", "entity", None):
                unsupported.append(k)
            for v in n.values():
                walk(v)
        elif isinstance(n, list):
            for v in n:
                walk(v)

    walk(sig)
    if unsupported:
        return False, "unsupported_operator"
    if len(quants) != 1:
        return False, "nested_or_extra_quantifier"
    if sat.check_oracle_ir(case_id, oracle_ir)["verdict"] != "SATISFIABLE":
        return False, "not_satisfiable"
    return True, "ok"


def control_eligible(case_id: str, sentence: str, oracle_ir: dict) -> tuple:
    """양층 통과 여부 — 이것이 control 선별의 유일한 진입점."""
    ok, why = control_surface_ok(sentence)
    if not ok:
        return False, f"surface:{why}"
    ok, why = control_projection_ok(case_id, oracle_ir)
    if not ok:
        return False, f"projection:{why}"
    return True, "ok"
