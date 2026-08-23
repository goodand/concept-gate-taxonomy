"""O1_SCOPE_PROJECTION_V1 — scope signature 추출 (D-E2E-v1-25 Q25.1).

projection은 formula 재작성기가 아니라 **측정 함수**다(판정 §2): oracle과
subject **양측에 같은 함수**를 적용해 scope-bearing 구조만 남긴 signature를
얻고, signature 사이를 기존 커널 `cg_evaluate.evaluate`의 exact structural
match로 비교한다. full formula의 논리적 동치를 주장하지 않는다(판정 §3 —
"Projection ≠ proof of full logical equivalence").

signature는 IR 형태의 트리다 — 커널이 projection의 존재를 모른 채(판정
§29의 경계, Q22.3 §10의 커널 금지 원칙) 기존 canonicalize/evaluate를 호출
지점 조합만으로 재사용하기 위해서다. desugar가 도입하는 implies가 signature
에 남을 수 있고 이는 subject 방언 밖이지만 무방하다 — signature는 비교
전용이고, subject 방언 witness는 `_stage2_satisfiability`의 렌더러가 만든다.

동결 규칙 전문은 계약 `test_stage2_scope_projection.py`의 docstring이 정본.
변수 분류 규칙은 V2 manifest의 PMB 15 fixture, 양화 변수 73개 전수 실측에서
잔여(UNCLASSIFIED) 0으로 확인된 것이다.

첫 위임 구현(2026-08-23)은 json.dumps 전역 monkey-patch와 undesugar 재작성
기를 도입해 거부·재작성됐다 — 원인이던 계약 모순(위 witness 문단)은 계약에서
제거됐고, 전역 부수효과·역변환은 이 모듈에 영구 금지다.
"""
from __future__ import annotations

import copy
import re
from typing import Any

from _stage2_canonical_core import desugar

PROJECTION_PROFILE_ID = "O1_SCOPE_PROJECTION_V1"

SLOT = "□"          # 익명 술어 라벨 (라벨 어휘는 채점 밖 — 판정 §13)
RESERVED = "True"   # desugar의 중립 제한식 토큰 — 절대 익명화하지 않는다

_SYNSET = re.compile(r".+\.(n|v|a|r|x)\.\d+$")
_VERB_SYNSET = re.compile(r".+\.v\.\d+$")
_TIME_NOUN = re.compile(r"(?:time|month)\.n\.\d+$")


def scaffold_use(pred_name: str) -> bool:
    """이 술어에 인자로 나타나는 것이 '사건 의미론 비계' 용법인가.

    (i) 대문자 시작 비-synset(ROLE: Agent, EQU, TPR …) /
    (ii) 동사 synset `*.v.NN` / (iii) 시간 명사 synset.
    subject의 평범한 소문자 술어는 셋 다 아니므로 자연히 참여자 용법이다.
    """
    if pred_name == RESERVED:
        return False  # True는 용법으로 세지 않는다 (호출측에서도 건너뜀)
    if pred_name[0].isupper() and not _SYNSET.match(pred_name):
        return True
    if _VERB_SYNSET.match(pred_name):
        return True
    return bool(_TIME_NOUN.match(pred_name))


def _var_uses(node: Any, acc: dict) -> dict:
    if isinstance(node, dict):
        if node.get("kind") == "pred" and node.get("name") != RESERVED:
            for arg in node.get("args", []):
                if isinstance(arg, dict) and arg.get("kind") == "var":
                    acc.setdefault(arg["name"], []).append(node["name"])
        for v in node.values():
            _var_uses(v, acc)
    elif isinstance(node, list):
        for v in node:
            _var_uses(v, acc)
    return acc


def _scaffold_vars(formula: dict) -> set:
    """용법 전부가 scaffold인 변수 집합 (용법 0개인 변수는 PARTICIPANT 취급)."""
    return {v for v, names in _var_uses(formula, {}).items()
            if names and all(scaffold_use(n) for n in names)}


_TRUE_PRED = {"kind": "pred", "name": RESERVED, "args": []}


def project_scope_for_case(case_id: str, formula: dict) -> dict:
    """source(case_id 접두어)별 정책으로 scope signature를 반환한다.

    순수 함수: 입력 무변이(desugar가 이미 새 트리를 반환), idempotent.
    미지 접두어는 거부한다 — codec dispatch와 같은 fail-closed 규율.
    """
    work = desugar(formula)  # idempotent; 입력을 변이하지 않는다
    if case_id.startswith("PMB-"):
        return _project_pmb(work)
    if case_id.startswith("FOLIO-"):
        return _project_folio(work)
    raise ValueError(f"unknown case_id prefix for projection: {case_id!r}")


# ---------------------------------------------------------------- FOLIO ----

def _project_folio(work: dict) -> dict:
    """FOLIO: 구조 전부 유지, 라벨만 익명화 (인자·arity·결박 순서 보존)."""
    out = copy.deepcopy(work)
    _anonymize_in_place(out)
    return out


def _anonymize_in_place(node: Any) -> None:
    if isinstance(node, dict):
        if node.get("kind") == "pred" and node.get("name") != RESERVED:
            node["name"] = SLOT
        for v in node.values():
            _anonymize_in_place(v)
    elif isinstance(node, list):
        for v in node:
            _anonymize_in_place(v)


# ------------------------------------------------------------------ PMB ----

def _project_pmb(work: dict) -> dict:
    """PMB: scaffold ∃ 제거(본문 승격) + 술어 필터 + 익명화.

    술어 제거 규칙(계약 정본): scaffold 이름이거나, SCAFFOLD 변수를 만지거나,
    arity ≥ 2 — 사건 매개 관계(oracle)와 직접 관계(subject)의 granularity를
    양측 대칭으로 다리 놓는 유일한 결정론 규칙이다. 남는 술어(PARTICIPANT
    변수 위 1항)는 익명 slot이 된다.
    """
    scaffold = _scaffold_vars(work)
    projected = _walk_pmb(work, scaffold)
    return projected if projected is not None else copy.deepcopy(_TRUE_PRED)


def _walk_pmb(node: Any, scaffold: set):
    """None 반환 = 이 부분트리는 signature에서 사라진다."""
    if not isinstance(node, dict):
        return None
    kind = node.get("kind")

    if kind in ("forall", "exists"):
        var = node["var"]
        if kind == "exists" and var in scaffold:
            # scaffold ∃ 제거: 본문 승격 (desugar 후 제한은 True다)
            return _walk_pmb(node["body"], scaffold)
        restriction = _walk_pmb(node["restriction"], scaffold)
        body = _walk_pmb(node["body"], scaffold)
        return {"kind": kind, "var": var,
                "restriction": restriction if restriction is not None
                else copy.deepcopy(_TRUE_PRED),
                "body": body if body is not None
                else copy.deepcopy(_TRUE_PRED)}

    if kind == "not":
        inner = _walk_pmb(node["body"], scaffold)
        return {"kind": "not",
                "body": inner if inner is not None else copy.deepcopy(_TRUE_PRED)}

    if kind == "implies":
        left = _walk_pmb(node["left"], scaffold)
        right = _walk_pmb(node["right"], scaffold)
        return {"kind": "implies",
                "left": left if left is not None else copy.deepcopy(_TRUE_PRED),
                "right": right if right is not None else copy.deepcopy(_TRUE_PRED)}

    if kind == "and":
        kept = [p for p in (_walk_pmb(a, scaffold) for a in node.get("args", []))
                if p is not None]
        if not kept:
            return None            # 빈 AND는 소거 (상위가 True로 대체)
        if len(kept) == 1:
            return kept[0]         # 단일 인자 AND 붕괴
        return {"kind": "and", "args": kept}

    if kind == "pred":
        name = node.get("name")
        if name == RESERVED:
            return copy.deepcopy(node)
        args = node.get("args", [])
        if scaffold_use(name):
            return None
        if any(isinstance(a, dict) and a.get("kind") == "var"
               and a.get("name") in scaffold for a in args):
            return None
        if len(args) >= 2:
            return None
        return {"kind": "pred", "name": SLOT, "args": copy.deepcopy(args)}

    # 미지 kind(예: or)는 구조 그대로 보존 — satisfiability gate의
    # no_unsupported_scored_operator 검사가 하류에서 잡도록 숨기지 않는다
    return copy.deepcopy(node)
