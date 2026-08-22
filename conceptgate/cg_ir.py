#!/usr/bin/env python3
"""cg_ir — Shared Semantic Kernel의 최소 IR (DESIGN_DIRECTIVE §11–13).

이 모듈은 quantifier/modal scope를 표현할 수 있는 최소 semantic IR primitives를
제공한다. α-동치 공식들을 정규화하며, 의미 변경(quantifier 재배열·교환법칙
재배열·정리 동치)은 금지한다 (§8).

원칙들:
- Canonicalization은 representation normalization만 한다 (§8).
  Semantic judgment (판정/증명/동치/단순화)은 제공하지 않는다 (§29 negative contract).
- α-renaming은 bound variable을 등장 순서대로 "?0", "?1", ... 로 변환한다.
  자유변수는 절대 변경하지 않는다.
- 자유변수 이름이 "?"로 시작하면 ValueError를 던진다 (capture 회피 via namespace reservation).
- Shadowing은 환경 스택으로 처리: 안쪽 binder가 같은 이름을 재바인딩하면
  안쪽 body에서 안쪽 binder의 canonical 이름이 바깥쪽을 가린다.
- Formula dict 입력을 변경하지 않는다 (새 dict 반환).

§29 negative contract (AST 검사로 집행):
이 모듈에서 절대 금지되는 함수명:
  simplify, equival, entail, prove, infer, rewrite, judge, certif,
  select, score, oracle, verdict
"""
from __future__ import annotations

from typing import Any

import conceptgate.cg_identity as cg_identity


def validate_formula(node: Any) -> list[dict]:
    """Formula dict의 구조 검증. 오류 목록 반환 (빈 리스트 = 유효).

    각 오류는 {"code": "...", "detail": "..."} dict.
    """
    errors = []

    if not isinstance(node, dict):
        errors.append({
            "code": "NOT_DICT",
            "detail": f"node must be a dict, got {type(node).__name__}"
        })
        return errors

    kind = node.get("kind")
    if kind is None:
        errors.append({
            "code": "MISSING_KIND",
            "detail": "node must have a 'kind' field"
        })
        return errors

    if not isinstance(kind, str):
        errors.append({
            "code": "KIND_NOT_STRING",
            "detail": f"'kind' must be string, got {type(kind).__name__}"
        })
        return errors

    # Known kinds and their required/optional fields
    known_kinds = {
        "entity": {"required": ["name"], "optional": []},
        "var": {"required": ["name"], "optional": []},
        "pred": {"required": ["name", "args"], "optional": []},
        "forall": {"required": ["var", "body"], "optional": []},
        "exists": {"required": ["var", "body"], "optional": []},
        "box": {"required": ["body"], "optional": []},
        "diamond": {"required": ["body"], "optional": []},
        "implies": {"required": ["left", "right"], "optional": []},
        "and": {"required": ["args"], "optional": []},
        "or": {"required": ["args"], "optional": []},
        "not": {"required": ["body"], "optional": []},
    }

    if kind not in known_kinds:
        errors.append({
            "code": "UNKNOWN_KIND",
            "detail": f"unknown formula kind: {kind!r}"
        })
        return errors

    spec = known_kinds[kind]
    for required_field in spec["required"]:
        if required_field not in node:
            errors.append({
                "code": f"MISSING_{required_field.upper()}",
                "detail": f"kind {kind!r} requires field {required_field!r}"
            })

    # Type checks for specific fields
    if kind in ("forall", "exists"):
        var_val = node.get("var")
        if var_val is not None and not isinstance(var_val, str):
            errors.append({
                "code": "VAR_NOT_STRING",
                "detail": f"'var' must be string, got {type(var_val).__name__}"
            })
        body = node.get("body")
        if body is not None:
            errors.extend(validate_formula(body))

    elif kind in ("box", "diamond", "not"):
        body = node.get("body")
        if body is not None:
            errors.extend(validate_formula(body))

    elif kind == "implies":
        left = node.get("left")
        right = node.get("right")
        if left is not None:
            errors.extend(validate_formula(left))
        if right is not None:
            errors.extend(validate_formula(right))

    elif kind in ("and", "or"):
        args = node.get("args")
        if args is not None:
            if not isinstance(args, list):
                errors.append({
                    "code": "ARGS_NOT_LIST",
                    "detail": f"'args' must be list, got {type(args).__name__}"
                })
            else:
                for arg in args:
                    errors.extend(validate_formula(arg))

    elif kind == "pred":
        args = node.get("args")
        if args is not None:
            if not isinstance(args, list):
                errors.append({
                    "code": "ARGS_NOT_LIST",
                    "detail": f"'args' must be list, got {type(args).__name__}"
                })
            else:
                for arg in args:
                    errors.extend(validate_formula(arg))

    return errors


def free_variables(formula: dict) -> set[str]:
    """Formula의 자유변수(bound되지 않은 변수) 목록.

    Quantifier (forall/exists)에 의해 bound된 변수는 제외된다.
    """
    return _free_variables_helper(formula, bound_vars=set())


def _free_variables_helper(formula: dict, bound_vars: set[str]) -> set[str]:
    """Helper: bound_vars는 현재 scope에서 bound된 변수들."""
    kind = formula.get("kind")
    free = set()

    if kind == "var":
        name = formula.get("name")
        if name and name not in bound_vars:
            free.add(name)

    elif kind == "entity":
        pass  # No variables

    elif kind == "pred":
        args = formula.get("args", [])
        for arg in args:
            free.update(_free_variables_helper(arg, bound_vars))

    elif kind in ("forall", "exists"):
        var = formula.get("var")
        body = formula.get("body")
        new_bound = bound_vars | {var}
        if body:
            free.update(_free_variables_helper(body, new_bound))

    elif kind in ("box", "diamond", "not"):
        body = formula.get("body")
        if body:
            free.update(_free_variables_helper(body, bound_vars))

    elif kind == "implies":
        left = formula.get("left")
        right = formula.get("right")
        if left:
            free.update(_free_variables_helper(left, bound_vars))
        if right:
            free.update(_free_variables_helper(right, bound_vars))

    elif kind in ("and", "or"):
        args = formula.get("args", [])
        for arg in args:
            free.update(_free_variables_helper(arg, bound_vars))

    return free


def canonicalize_v0(formula: dict) -> dict:
    """Formula의 α-정규화: bound variable을 "?0", "?1", ... 로 순서대로 rename.

    자유변수는 절대 변경하지 않는다. 자유변수 이름이 "?"로 시작하면
    ValueError("... reserved ...") 를 던진다.

    입력 dict를 변경하지 않고 새 dict를 반환한다.

    Args:
        formula: dict

    Returns:
        Canonicalized formula dict

    Raises:
        ValueError: if a free variable name starts with "?"
    """
    # First, check that no free variable starts with "?"
    free_vars = free_variables(formula)
    for fv in free_vars:
        if fv.startswith("?"):
            raise ValueError(f"free variable {fv!r} starts with '?' (reserved for bound variables)")

    # Perform canonical renaming
    result, _counter = _canonicalize_helper(formula, rename_map={}, counter=0)
    return result


def _canonicalize_helper(formula: dict, rename_map: dict[str, str], counter: int) -> tuple[dict, int]:
    """Helper for canonicalize_v0.

    rename_map: current scope's mapping from original var name to canonical name
    counter: current counter for next canonical var name
    """
    kind = formula.get("kind")

    if kind == "var":
        name = formula.get("name")
        # If it's in rename_map, it's a bound variable; otherwise, it's free
        if name in rename_map:
            return {"kind": "var", "name": rename_map[name]}, counter
        else:
            # Free variable: keep as is
            return {"kind": "var", "name": name}, counter

    elif kind == "entity":
        return {"kind": "entity", "name": formula.get("name")}, counter

    elif kind == "pred":
        name = formula.get("name")
        args = formula.get("args", [])
        new_args = []
        for arg in args:
            new_arg, counter = _canonicalize_helper(arg, rename_map, counter)
            new_args.append(new_arg)
        return {"kind": "pred", "name": name, "args": new_args}, counter

    elif kind in ("forall", "exists"):
        var = formula.get("var")
        body = formula.get("body")

        # Create new canonical name for this variable
        canonical_var = f"?{counter}"
        new_counter = counter + 1

        # Create new rename_map with this binding
        new_rename_map = rename_map.copy()
        new_rename_map[var] = canonical_var

        # Process body with new rename_map
        new_body, final_counter = _canonicalize_helper(body, new_rename_map, new_counter)

        return {"kind": kind, "var": canonical_var, "body": new_body}, final_counter

    elif kind in ("box", "diamond", "not"):
        body = formula.get("body")
        new_body, final_counter = _canonicalize_helper(body, rename_map, counter)
        return {"kind": kind, "body": new_body}, final_counter

    elif kind == "implies":
        left = formula.get("left")
        right = formula.get("right")
        new_left, counter = _canonicalize_helper(left, rename_map, counter)
        new_right, final_counter = _canonicalize_helper(right, rename_map, counter)
        return {"kind": "implies", "left": new_left, "right": new_right}, final_counter

    elif kind in ("and", "or"):
        args = formula.get("args", [])
        new_args = []
        for arg in args:
            new_arg, counter = _canonicalize_helper(arg, rename_map, counter)
            new_args.append(new_arg)
        return {"kind": kind, "args": new_args}, counter

    else:
        # Unknown kind: return as is (shouldn't happen if validate_formula was called)
        return formula, counter


def formula_fingerprint(formula: dict) -> str:
    """Formula의 정규화 표현 identity.

    Canonicalize한 후 cg_identity.fingerprint("formula", ...)로 해싱.
    Same normalized representation = same fingerprint.
    Same fingerprint ≠ semantic truth (§I9).
    """
    canonical = canonicalize_v0(formula)
    return cg_identity.fingerprint("formula", canonical)
