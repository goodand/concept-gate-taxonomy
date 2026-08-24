"""MRS_COUNT_PROJECTION_V1 — 기수/비례 MRS의 fail-closed package 판정.

판정 D-E2E-v1-29 §9~§11. 계약 전문은 `test_stage2_mrs_count_projection.py`의
docstring이 정본이다.

이 층은 **판정만** 한다 — MRS 텍스트 파싱은 adapter의 몫이고, 여기 입력은
이미 파싱된 구조다. 그 분리가 필요한 이유: fail-closed 거부를 파싱 실패와
섞으면 "거부됨"이 "읽지 못함"과 구별되지 않는다(저장소의 PASS/FAIL/BLOCKED
규율과 동형 — BLOCKED를 FAIL로 읽으면 게이트 신뢰가 무너진다).

동치를 주장하지 않는다(`LOGICAL_EQUIVALENCE_CLAIM = False`). MRS에서 `card`는
quantifier의 **제한식 내부 술어**이고(실물에서 명사와 LBL을 공유한다) 독립
결박자가 아니다. 우리 IR의 `count`는 자체 결박자이므로, 이 package는 두
표상 사이의 **측정용 사상**이지 동치 변환이 아니다.
"""
from __future__ import annotations

from typing import Any

PROJECTION_PROFILE_ID = "MRS_COUNT_PROJECTION_V1"
LOGICAL_EQUIVALENCE_CLAIM = False

# 판정 §11 reject_if 5종 + D-E2E-v1-31 Q31.2 개정 2건 = 6종. 이 집합이
# 정본이며 임의로 늘리지 않는다.
#   - "multiple_card_EP_candidates" → "unsupported_compound_cardinal_mapping_v1":
#     "표현 불가"가 아니라 "승인된 semantics-preserving 사상이 아직 없어서
#     fail-closed reject"라는 구분을 코드가 주장하지 않게 하려는 개정.
#   - "type_mismatch" 신설: card.ARG1이 개체 변수가 아니면(§below 접두 `x`
#     판정) 사상에 타입 강제가 필요하고 adapter 계약에 없어 최상위 게이트.
REJECT_CODES = (
    "unsupported_compound_cardinal_mapping_v1",
    "card_and_quantifier_variable_disagree",
    "unresolved_handle_constraint",
    "numeric_scope_attachment_ambiguous",
    "unsupported_numeric_relation",
    "type_mismatch",
)

# require 실패(=재료가 애초에 기수 fixture가 아님)는 reject 5종과 구별한다.
ABSENT_CODES = ("quantifier_EP_absent", "cardinal_EP_absent")

CARDINAL_PRED = "card"


def _is_quantifier(ep: dict) -> bool:
    """RSTR·BODY를 둘 다 갖는 EP가 양화 EP다(ERG 관례이자 MRS RFC 형태)."""
    args = ep.get("args", {})
    return "RSTR" in args and "BODY" in args


def _resolves(handle: str, hcons: list) -> str | None:
    """`h QEQ x` 가 있으면 x를 준다. 없으면 None(= 미해소)."""
    for lhs, rel, rhs in hcons:
        if lhs == handle and rel == "QEQ":
            return rhs
    return None


def _refuse(code: str, detail: str = "", **extra) -> dict:
    return {"ok": False, "profile": PROJECTION_PROFILE_ID,
            "reject": code, "detail": detail, **extra}


def package_count(mrs: dict) -> dict:
    """quantifier EP + card EP를 **같은 결박 변수일 때만** package한다.

    판정 §11 말미: `card_rel`가 문장 어딘가 있다는 이유로 가장 가까운
    quantifier에 붙이면 안 된다. 그래서 변수 일치가 유일한 연결 근거다.
    """
    eps: list = list(mrs.get("eps", []))
    hcons: list = list(mrs.get("hcons", []))

    quantifiers = [e for e in eps if _is_quantifier(e)]
    cards = [e for e in eps if e.get("pred") == CARDINAL_PRED]

    if not quantifiers:
        return _refuse("quantifier_EP_absent", "RSTR/BODY를 갖는 EP가 없다")
    if not cards:
        return _refuse("cardinal_EP_absent", f"{CARDINAL_PRED} EP가 없다")

    # D-E2E-v1-31 Q31.2: E15 타입 게이트를 최상위로. 우리 IR의 count.var는
    # 개체 변수인데 card.ARG1이 미명세 개체(i)나 사건(e)이면 사상에 타입
    # 강제가 필요하고 adapter 계약에 없다. 다른 결함(CARG 비정수·RSTR 미해소
    # 등)이 동시에 있어도 이것부터 판정해야 거부 사유 회계가 게이트 순서를
    # 반영한다. 개체 변수는 접두 `x`로 식별한다(운영 실측: 게이트 순서를
    # 바꿔도 최종 적격 집합은 불변 — 이 승격은 계약 명확성 문제다).
    for c in cards:
        v = c.get("args", {}).get("ARG1")
        if not (isinstance(v, str) and v.startswith("x")):
            return _refuse("type_mismatch",
                           f"card ARG1={v!r}가 개체 변수(접두 x)가 아니다")

    # 여러 card가 **같은 변수**를 겨냥하면 어느 수치인지 결정 불가.
    by_var: dict = {}
    for c in cards:
        by_var.setdefault(c.get("args", {}).get("ARG1"), []).append(c)
    contested = [v for v, cs in by_var.items() if len(cs) > 1]
    # D-31 Q31.2: 사유는 "표현 불가"가 아니다 — 방언에는 `or`+복수 `count`를
    # 조합할 능력이 있다. "승인된 semantics-preserving 사상이 아직 없어서
    # fail-closed reject"이므로 intrinsically_unexpressible을 명시적으로
    # False로 싣는다(향후 검증된 projection rule로 지원할 여지를 남긴다).
    if contested:
        return _refuse("unsupported_compound_cardinal_mapping_v1",
                       f"변수 {contested!r}에 card EP가 여럿",
                       intrinsically_unexpressible=False)
    if len(cards) > 1:
        return _refuse("unsupported_compound_cardinal_mapping_v1",
                       "card EP가 여럿 — v1은 단일 기수 문장만 다룬다",
                       intrinsically_unexpressible=False)

    card = cards[0]
    target = card.get("args", {}).get("ARG1")

    matched = [q for q in quantifiers if q.get("args", {}).get("ARG0") == target]
    if not matched:
        return _refuse("card_and_quantifier_variable_disagree",
                       f"card ARG1={target!r}를 결박하는 양화 EP가 없다")
    if len(matched) > 1:
        return _refuse("numeric_scope_attachment_ambiguous",
                       f"변수 {target!r}를 결박하는 양화 EP가 {len(matched)}개")

    quant = matched[0]

    carg = card.get("args", {}).get("CARG")
    # 수치 상수만 지원한다. `a few`·`several` 같은 어휘 CARG는 관계를 알 수 없다.
    if not (isinstance(carg, str) and carg.lstrip("-").isdigit()):
        return _refuse("unsupported_numeric_relation",
                       f"CARG={carg!r}가 정수가 아니다")

    args = quant.get("args", {})
    rstr_target = _resolves(args.get("RSTR"), hcons)
    body_target = _resolves(args.get("BODY"), hcons)

    # 판정 §11 `RSTR_resolved`/`BODY_resolved`를 **문자 그대로** 적용한다.
    # 실물 DeepBank record는 최외곽 양화의 BODY를 HCONS에 넣지 않으므로
    # 여기서 전부 거부된다 — 그것이 관측이고, 완화는 판정 사안이다(P19).
    # 완화 논의가 필요한 지점을 코드가 이름으로 지목한다.
    if rstr_target is None:
        return _refuse("unresolved_handle_constraint",
                       f"RSTR handle {args.get('RSTR')!r}가 HCONS에 없다",
                       blocker_ref="D29_S11_RSTR_RESOLVED")
    if body_target is None:
        return _refuse("unresolved_handle_constraint",
                       f"BODY handle {args.get('BODY')!r}가 HCONS에 없다",
                       blocker_ref="D29_S11_BODY_RESOLVED")

    return {"ok": True, "profile": PROJECTION_PROFILE_ID,
            "count": {"rel": "eq", "num": int(carg), "var": target,
                      "restriction_label": rstr_target,
                      "body_label": body_target},
            "quantifier_pred": quant.get("pred")}


def refusal_census(records: dict) -> dict:
    """여러 record의 거부 사유 분포. 재료 심사 기록용(계약 아님)."""
    out: dict[str, Any] = {}
    for rid, m in records.items():
        r = package_count(m)
        out[rid] = "ok" if r["ok"] else r["reject"]
    return out
