"""수사(card)가 개수 양화인지 명칭 일부인지 구조로 가리는 3값 판별기.

MRS의 label 공유와 compound/named 결합이 유일한 판단 근거다. 어느 쪽인지
구조에 근거가 없으면 NEEDS_AUDIT으로 보낸다 — 애매함을 기수 쪽으로
추측해서 채택하지 않는다(fail-closed).
"""
from __future__ import annotations

DETECTOR_ID = "NUMERIC_DESIGNATOR_DETECTOR_V1"
VERDICTS = frozenset({"CARDINAL", "DESIGNATOR", "NEEDS_AUDIT"})


def _args(ep):
    return ep.get("args", {})


def _is_unknown_pred(pred):
    # ERG 런타임이 미지 어휘에 붙이는 표지("..._u_unknown") — 어휘 부류를
    # 보통명사로 단정할 근거가 없으므로 별도로 걸러낸다.
    return isinstance(pred, str) and pred.endswith("_u_unknown")


def _named_arg0(eps, target):
    return any(e.get("pred") == "named" and _args(e).get("ARG0") == target
               for e in eps)


def classify(mrs: dict, var: str) -> dict:
    eps = mrs.get("eps", [])
    cards = [e for e in eps if e.get("pred") == "card" and _args(e).get("ARG1") == var]
    if not cards:
        return {"verdict": "NEEDS_AUDIT", "reason": "no_card_predicate"}

    for card in cards:
        lbl = card.get("lbl")
        colabeled = [e for e in eps if e is not card and e.get("lbl") == lbl]

        # (1) compound가 수사를 다른 변수(명칭 후보)에 묶는가.
        for e in colabeled:
            if e.get("pred") == "compound" and _args(e).get("ARG1") == var:
                mod = _args(e).get("ARG2")
                if mod is not None and _named_arg0(eps, mod):
                    return {"verdict": "DESIGNATOR",
                            "reason": "cardinal_inside_name_compound"}

        # (2) 변수 자신이 같은 label에서 이미 명칭으로 서술되는가.
        if any(e.get("pred") == "named" and _args(e).get("ARG0") == var
               for e in colabeled):
            return {"verdict": "DESIGNATOR", "reason": "card_colabeled_with_named"}

        # (3) 같은 label의 제한식이 어휘 부류 미지(unknown word)인가 —
        #     보통명사인지 단정할 수 없으므로 사람 감사로 넘긴다.
        if any(_is_unknown_pred(e.get("pred")) and _args(e).get("ARG0") == var
               for e in colabeled):
            return {"verdict": "NEEDS_AUDIT", "reason": "unknown_word_restriction"}

        # (4) 같은 label에 var를 ARG0로 갖는 제한식이 있으면 가산 명사를
        #     세는 것으로 본다.
        if any(_args(e).get("ARG0") == var for e in colabeled):
            return {"verdict": "CARDINAL", "reason": "card_colabeled_with_count_noun"}

    # card는 있으나 같은 label 안에서 명칭도 가산 명사도 확인되지 않음 —
    # 구조가 말해주지 않는 경우이므로 채택하지 않는다.
    return {"verdict": "NEEDS_AUDIT", "reason": "no_colabeled_content"}


def eligible_as_cardinal(result: dict) -> bool:
    return result.get("verdict") == "CARDINAL"
