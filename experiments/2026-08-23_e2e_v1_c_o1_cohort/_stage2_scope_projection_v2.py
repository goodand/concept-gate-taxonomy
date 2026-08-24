"""O1_SCOPE_PROJECTION_V2 — quantifier-scope 채점용 투영 함수.

계약 정본은 `test_stage2_scope_projection_v2.py`의 docstring이다. V1은
바이트 그대로 동결된 표면이므로 이 파일은 V1을 참조도, 수정도 하지 않는다.

## 설계 한 줄 요약

primary scope 연산자(forall/exists/count/prop/not)가 없는 부분트리는
"opaque atom"으로 접는다. atom의 값은 그 아래 모든 술어의 (변수 인자
튜플)을 순서대로 모으고 **동일 튜플의 중복만** 제거한 리스트다 — 술어
이름은 버리므로(판정문: 어휘 라벨은 버림, incidence는 지킴) 이름이 다른
두 술어라도 인자 튜플이 같으면 같은 항목으로 합쳐진다. 이는 predicate
erasure가 아니라 "그 자리에 내용이 있었다"는 흔적만 남기는 것이다.
"""
from __future__ import annotations

PROJECTION_PROFILE_ID = "O1_SCOPE_PROJECTION_V2"
SUPERSEDES = ("O1_SCOPE_PROJECTION_V1",)
V1_SCORE_COMPARABLE = False
LOGICAL_EQUIVALENCE_CLAIM = False
PRIMARY_SCOPE = frozenset({"forall", "exists", "count", "prop", "not"})

REINTERPRETATION = (
    "Q_RSTR_BODY is defined by position, not provenance tagging: an implies "
    "in the direct body of a quantifier whose restriction is True is kept "
    "as the RSTR/BODY structural marker solely because of that position. "
    "This is a reinterpretation of the ruling text, pending confirmation."
)


class ProjectionQualificationFail(Exception):
    """닫힌 profile 밖의 kind를 만났을 때 — 조용히 통과시키지 않는다."""


class _Canon:
    """결박 변수명을 등장 순서의 정수 id로 바꾼다 — α-rename 불가시성.

    dict가 아니라 스택을 쓰는 이유: 같은 이름이 중첩 결박돼도(섀도잉) 안쪽
    결박이 바깥 결박을 가리지 않고 정확히 복원돼야 하기 때문이다.
    """

    def __init__(self) -> None:
        self._stacks: dict[str, list[int]] = {}
        self._n = 0

    def bind(self, name: str) -> None:
        self._n += 1
        self._stacks.setdefault(name, []).append(self._n)

    def unbind(self, name: str) -> None:
        self._stacks[name].pop()

    def get(self, name: str) -> object:
        stack = self._stacks.get(name)
        return stack[-1] if stack else name  # 자유변수는 이름 그대로(테스트 밖 방어)


def _has_scope(node: dict) -> bool:
    """부분트리 어딘가에 primary scope 연산자가 있는가 (carrier 여부 판정용)."""
    kind = node.get("kind")
    if kind in PRIMARY_SCOPE:
        return True
    if kind == "pred":
        return False
    if kind in ("and", "or"):
        return any(_has_scope(a) for a in node["args"])
    if kind == "implies":
        return _has_scope(node["left"]) or _has_scope(node["right"])
    raise ProjectionQualificationFail(f"unknown operator: {kind}")


def _collapse(node: dict, canon: _Canon) -> tuple:
    """scope 없는 부분트리를 incidence 튜플 목록으로 접는다.

    술어 이름·and/or 정체·개수는 버리고(판정문), 인자 변수 튜플의 순서만
    지킨다. 동일 튜플이 반복되면 첫 등장만 남긴다("동일 incidence 다중도는
    버린다"). `True`/무인자 술어는 desugar의 중립 제한식 토큰이라 내용으로
    치지 않는다(empty vs nonempty 구별의 근거).
    """
    tuples: list[tuple] = []

    def walk(n: dict) -> None:
        kind = n.get("kind")
        if kind == "pred":
            if n["name"] == "True" and not n["args"]:
                return
            t = tuple(canon.get(a["name"]) for a in n["args"])
            if t not in tuples:
                tuples.append(t)
        elif kind in ("and", "or"):
            for a in n["args"]:
                walk(a)
        elif kind == "implies":
            walk(n["left"])
            walk(n["right"])
        else:
            raise ProjectionQualificationFail(f"unknown operator: {kind}")

    walk(node)
    return tuple(tuples)


def _sig(node: object, canon: _Canon) -> tuple:
    if not isinstance(node, dict) or "kind" not in node:
        raise ProjectionQualificationFail(f"unknown operator: {node!r}")
    kind = node["kind"]

    if kind in ("forall", "exists", "count", "prop"):
        return _sig_quantifier(node, kind, canon)
    if kind == "not":
        return ("not", _sig(node["body"], canon))
    if kind in ("and", "or"):
        if _has_scope(node):
            # and/or 정체는 채점하지 않는다 — 둘 다 같은 "carrier" 태그.
            return ("carrier", tuple(_sig(a, canon) for a in node["args"]))
        return ("atom", _collapse(node, canon))
    if kind == "implies":
        if _has_scope(node):
            # implies는 방향을 지킨다(carrier와 달리 좌우가 채점 대상).
            return ("implies", _sig(node["left"], canon), _sig(node["right"], canon))
        return ("atom", _collapse(node, canon))
    if kind == "pred":
        return ("atom", _collapse(node, canon))
    raise ProjectionQualificationFail(f"unknown operator: {kind}")


def _is_empty_atom(sig: tuple) -> bool:
    return sig == ("atom", ())


def _sig_quantifier(node: dict, kind: str, canon: _Canon) -> tuple:
    varname = node["var"]
    canon.bind(varname)
    try:
        rsig = _sig(node["restriction"], canon)
        body = node["body"]
        bsig = _sig(body, canon)
        # 위치 규칙(REINTERPRETATION): 제한식이 empty이고 body가 implies면
        # 그 implies는 desugar 산출물의 RSTR/BODY 표지로 태깅한다.
        if _is_empty_atom(rsig) and isinstance(body, dict) and body.get("kind") == "implies":
            bsig = ("QRB", bsig)
        if kind == "count":
            return (kind, node["rel"], node["num"], rsig, bsig)
        if kind == "prop":
            return (kind, node["rel"], rsig, bsig)
        return (kind, rsig, bsig)
    finally:
        canon.unbind(varname)


def signature(formula: dict) -> tuple:
    """채점용 signature. 순수 함수 — 입력을 읽기만 하고 바꾸지 않는다."""
    return _sig(formula, _Canon())
