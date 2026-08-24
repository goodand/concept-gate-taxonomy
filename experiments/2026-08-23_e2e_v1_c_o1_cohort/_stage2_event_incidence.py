"""PMB_EVENT_INCIDENCE_PROJECTION_V1 + ProjectionSignalGate (D-E2E-v1-28).

판정 §1이 확정한 것: `∃e(Smile(e)∧Agent(e,x)) ≢ Smile(x)` — 따라서 사건
논리식을 참여자 논리식으로 **재작성하는 것은 금지**다(우리 재검증에서도
비동치 확인). 대신 §2-3의 측정 전용 투영을 쓴다:

    사건 술어의 **어휘 진리값은 버리고**, role edge가 말하는
    "이 양화된 참여자가 body의 어떤 내용 술어에 참여한다"는
    **결박 incidence만 무라벨 slot으로 보존**한다.

동치를 주장하지 않는다(`logical_equivalence_claim: false`). 이것이 해소하는
결함 G3: 기존 투영은 동사 synset을 비계로 제거해 oracle 본문을 `True`로
붕괴시켰고("Everyone smiled" → `∀(T;(□→T))`) 단순보편 4건이 전부 같은
골격이 되어 신호가 사라졌다.

계약 전문은 `test_stage2_event_incidence.py`의 docstring이 정본이다.
인자 순서는 **양화 계보 순서(외부→내부)** — role 라벨이 채점 밖이므로
role 서열을 쓸 수 없다. 그 결과 "subject가 계보 순서대로 인자를 놓았는가"가
측정되며, D-27이 명한 binding topology가 이 정의로 유지된다.

`ProjectionSignalGate`(§7-8): 투영 후 각 target 양화의 제한식·본문 중
**적어도 하나에 채점 가능한 내용이 남아 있어야** 한다. 기본 fail-closed —
이 게이트가 없었기에 G3가 네 번의 동결을 통과했다.
"""
from __future__ import annotations

import copy
import re
from typing import Any

from _stage2_canonical_core import desugar
from _stage2_scope_projection import normalize_local_idioms

EVENT_INCIDENCE_PROFILE_ID = "PMB_EVENT_INCIDENCE_PROJECTION_V1"
# target 양화(= 신호가 남아야 하는 결박자). 방언을 넓히면 **여기도 넓혀야**
# 한다 — D-29가 count·prop을 추가했을 때 이 집합을 넓히지 않아 기수·비례
# fixture가 `target_quantifiers=0`으로 집계됐다(fail-closed라 안전 쪽으로
# 틀렸지만 이유가 틀렸다).
TARGET_BINDERS = ("forall", "exists", "count", "prop")
SLOT = "□"
RESERVED = "True"

_SYNSET = re.compile(r".+\.(n|v|a|r|x)\.\d+$")
_VERB_SYNSET = re.compile(r".+\.v\.\d+$")
_TIME_NOUN = re.compile(r"(?:time|month|year|day|hour)\.n\.\d+$")


class EventContractionRefused(Exception):
    """fail-closed(판정 §6): 안전한 contraction이 불가능한 fixture."""


def _is_role(name: str) -> bool:
    """의미역 술어 — 대문자 시작 비-synset(Agent/Experiencer/Time/EQU…)."""
    return bool(name) and name[0].isupper() and not _SYNSET.match(name)


def _is_event_pred(name: str) -> bool:
    return bool(_VERB_SYNSET.match(name))


def _is_time_pred(name: str) -> bool:
    return bool(_TIME_NOUN.match(name))


def _collect(node: Any, acc: list) -> list:
    """(pred_name, [arg var names]) 목록 — 트리 전체."""
    if isinstance(node, dict):
        if node.get("kind") == "pred":
            acc.append((node.get("name"),
                        [a.get("name") for a in node.get("args", [])
                         if isinstance(a, dict) and a.get("kind") == "var"]))
        for v in node.values():
            _collect(v, acc)
    elif isinstance(node, list):
        for v in node:
            _collect(v, acc)
    return acc


def _ancestry(node: Any, seen: list) -> list:
    """양화 변수를 외부→내부 순서로 수집(계보 순서)."""
    if isinstance(node, dict):
        if node.get("kind") in ("forall", "exists"):
            seen.append(node["var"])
        for key in ("restriction", "left", "body", "right"):
            if key in node:
                _ancestry(node[key], seen)
        if node.get("kind") == "and":
            for a in node["args"]:
                _ancestry(a, seen)
    elif isinstance(node, list):
        for v in node:
            _ancestry(v, seen)
    return seen


def _analyze(work: dict) -> tuple:
    """사건 변수 → 참여자 목록, 그리고 시간·역할 변수 집합을 구한다."""
    preds = _collect(work, [])
    uses: dict = {}
    for name, args in preds:
        if name == RESERVED:
            continue
        for v in args:
            uses.setdefault(v, []).append(name)

    event_vars, time_vars = set(), set()
    for v, names in uses.items():
        if any(_is_event_pred(n) for n in names):
            event_vars.add(v)
        elif names and all(_is_time_pred(n) or _is_role(n) for n in names):
            time_vars.add(v)

    # 사건별 참여자: role 술어의 인자 중 사건/시간 변수가 아닌 것
    participants: dict = {e: [] for e in event_vars}
    for name, args in preds:
        if not _is_role(name) or len(args) < 2:
            continue
        head = args[0]
        if head not in event_vars:
            continue
        for other in args[1:]:
            if other in event_vars:
                raise EventContractionRefused(
                    "unresolved nested event attachment: "
                    f"{name}({head},{other}) — 사건이 사건에 붙는다")
            if other not in time_vars and other not in participants[head]:
                participants[head].append(other)

    for e, ps in participants.items():
        if not ps:
            raise EventContractionRefused(
                f"zero retained participants for event var {e!r}")
    return event_vars, time_vars, participants


def project_event_incidence(formula: dict) -> dict:
    """oracle·subject 양측에 적용하는 측정 함수. 순수·idempotent.

    Raises:
        EventContractionRefused: 판정 §6의 fail-closed 조건.
    """
    work = normalize_local_idioms(desugar(formula))
    event_vars, time_vars, participants = _analyze(work)
    order = _ancestry(work, [])
    rank = {v: i for i, v in enumerate(order)}
    drop = event_vars | time_vars

    def by_ancestry(names):
        return sorted(names, key=lambda v: rank.get(v, len(rank)))

    def walk(node: Any):
        if not isinstance(node, dict):
            return None
        kind = node.get("kind")
        if kind in ("forall", "exists"):
            if node["var"] in drop:
                # 사건·시간 ∃를 접는다. 그 자리에는 참여자 incidence slot이
                # 온다(사건 술어의 어휘는 버리고 결박만 남긴다).
                inner = walk(node["body"])
                slot = None
                ps = participants.get(node["var"])
                if ps:
                    slot = {"kind": "pred", "name": SLOT,
                            "args": [{"kind": "var", "name": v}
                                     for v in by_ancestry(ps)]}
                if inner is None:
                    return slot
                if slot is None:
                    return inner
                return {"kind": "and", "args": [inner, slot]} \
                    if inner != slot else slot
            r = walk(node["restriction"])
            b = walk(node["body"])
            return {"kind": kind, "var": node["var"],
                    "restriction": r if r is not None else _true(),
                    "body": b if b is not None else _true()}
        if kind == "not":
            inner = walk(node["body"])
            return {"kind": "not", "body": inner if inner is not None else _true()}
        if kind == "implies":
            left, right = walk(node["left"]), walk(node["right"])
            return {"kind": "implies",
                    "left": left if left is not None else _true(),
                    "right": right if right is not None else _true()}
        if kind == "and":
            kept = [p for p in (walk(a) for a in node["args"]) if p is not None]
            # 같은 slot이 중복되면 하나로 (사건 술어 + role 술어가 같은
            # incidence를 두 번 만들지 않게)
            uniq = []
            for p in kept:
                if p not in uniq:
                    uniq.append(p)
            if not uniq:
                return None
            return uniq[0] if len(uniq) == 1 else {"kind": "and", "args": uniq}
        if kind == "pred":
            name = node.get("name")
            if name == RESERVED:
                return copy.deepcopy(node)
            args = [a for a in node.get("args", [])
                    if isinstance(a, dict)]
            if _is_role(name) or _is_event_pred(name) or _is_time_pred(name):
                return None            # 라벨·어휘는 버린다
            if any(a.get("name") in drop for a in args):
                return None
            # 인자 순서는 **그대로 유지**한다. 계보 정렬은 사건 contraction이
            # 만드는 slot에만 쓴다 — subject가 쓴 순서를 재정렬하면 D-27이
            # 유지를 명한 binding topology(P(x,y) ≠ P(y,x))가 소실된다.
            return {"kind": "pred", "name": SLOT,
                    "args": [dict(a) for a in args]}
        return copy.deepcopy(node)

    out = walk(work)
    return out if out is not None else _true()


def _true() -> dict:
    return {"kind": "pred", "name": RESERVED, "args": []}


# ---------------------------------------------- ProjectionSignalGate ----

def _has_content(node: Any) -> bool:
    if not isinstance(node, dict):
        return False
    if node.get("kind") == "pred":
        return node.get("name") != RESERVED
    for key in ("restriction", "body", "left", "right"):
        if key in node and _has_content(node[key]):
            return True
    if node.get("kind") == "and":
        return any(_has_content(a) for a in node["args"])
    return False


def projection_signal_check(case_id: str, formula: dict,
                            already_projected: bool = False) -> dict:
    """PROJECTION_SIGNAL_V1 (판정 §7-8) — 기본 fail-closed.

    각 target 양화의 **본문**에 채점 가능한 내용이 남아 있어야 한다
    (desugar 형태에서는 `implies`의 right). 판정 §7의 구체 예시가
    "restriction: PRED_SLOT / body: TRUE → signal failure"이므로 §8의
    "at least one"보다 이 쪽이 정본이다. 진짜 vacuous한 원문의 예외는
    profile에 명시적으로 넣어야 하며 기본은 fail-closed다.
    """
    try:
        sig = formula if already_projected else project_event_incidence(formula)
    except EventContractionRefused as exc:
        return {"gate": "PROJECTION_SIGNAL_V1", "case_id": case_id,
                "verdict": "CONTRACTION_REFUSED", "detail": str(exc)[:160],
                "target_quantifiers": 0, "collapsed_quantifiers": 0}

    total, collapsed = 0, 0

    def walk(node: Any) -> None:
        nonlocal total, collapsed
        if isinstance(node, dict):
            if node.get("kind") in TARGET_BINDERS:
                total += 1
                body = node["body"]
                # desugar 후 형태: forall(x, True, implies(R, B)) —
                # 제한식 내용은 implies.left, 본문 내용은 implies.right다.
                if isinstance(body, dict) and body.get("kind") == "implies":
                    body_content = _has_content(body["right"])
                else:
                    body_content = _has_content(body)
                # 판정 §7: restriction만 남고 body가 True면 signal failure.
                if not body_content:
                    collapsed += 1
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(sig)
    verdict = ("SIGNAL_COLLAPSED" if collapsed or total == 0
               else "SIGNAL_RETAINED")
    return {"gate": "PROJECTION_SIGNAL_V1", "case_id": case_id,
            "verdict": verdict, "target_quantifiers": total,
            "collapsed_quantifiers": collapsed}
