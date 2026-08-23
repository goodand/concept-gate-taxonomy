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

# D-28 Q28.2 G1: 비례 판별. bare `\bmost\b`는 폐기 — 최상급을 잡는다.
# 인정 형태: `most of …` / `most + 복수명사`. 최상급(`the most ADJ …`,
# `most ADJ`)은 배제한다. V1 동결 파일 freeze_stage2.pmb_stratum은 불변
# 보존하며, 이 정정 술어가 후속 동결의 정본이다.
_MOST_OF = re.compile(r"\bmost\s+of\b", re.I)
_MOST_NOMINAL = re.compile(r"\bmost\s+[a-z]+\b", re.I)
# 최상급의 표지는 한정사 `the`다(`the most beautiful …`). 복수형 `-s` 판별로
# 구분하려던 첫 시도는 people/children 같은 불규칙 복수를 놓쳤다(실측).
# 최상급 표지: 한정사 `the` 또는 소유격(`Copland's most`, `her most`).
_SUPERLATIVE_MOST = re.compile(r"(?:\bthe\s+most\b|'s\s+most\b|\b(?:his|her|its|their|my|your|our)\s+most\b)", re.I)
# `at most`는 상한 기수 표현이지 비례가 아니다(실물 대조에서 오탐 확인).
_AT_MOST = re.compile(r"\bat\s+most\b", re.I)
UNSUPPORTED_QUANTIFIER_LEXICON = ("few", "fewer", "several", "many", "most",
                                  "both", "either", "neither")
KNOWN_IDIOMS = ("anything but", "all right", "at all", "all of a sudden",
                "no doubt", "no longer", "some day")


def _tokens(sentence: str) -> list:
    """아포스트로피를 **경계로** 분리한다 — `She's`가 한 토큰이 되면 lexicon
    검사가 `she`를 놓친다(D-28 Gate C 실측 누출). 소유격 `John's`도 같은
    이유로 `John`이 드러나야 고유명 검사에 걸린다."""
    return re.findall(r"[A-Za-z]+", sentence)


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


def is_proportional(sentence: str) -> bool:
    """비례 양화 문장인가 (D-28 Q28.2 G1 정정 술어).

    `at most N`(상한 기수)은 먼저 배제한다. `most of …`는 인정. 최상급
    표지(`the most …`, `X's most …`, `her most …`)는 배제. 그 외
    `most + 명사`는 비례로 인정한다. **알려진 근사의 한계**: 한정사 없는
    최상급(`most talented students`)은 통과한다 — 드물고, Gate C(사람의
    재료 감사)가 최종 방어선이다. 첫 시도는 복수형 `-s`로 구분하려 했으나
    people/children 같은 불규칙 복수를 놓쳤다(실측).
    """
    if _AT_MOST.search(sentence):
        return False          # 상한 기수 (`at most N`)
    if _MOST_OF.search(sentence):
        return True
    if _SUPERLATIVE_MOST.search(sentence):
        return False          # 최상급 (`the most …`, `X's most …`)
    return bool(_MOST_NOMINAL.search(sentence))
