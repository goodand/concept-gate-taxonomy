"""Oracle Adapter — typed-lambda LF (wikisem format) → cg_ir dict.

(D-E2E-v1-20 b+, ORACLE-10, ORACLE-12)

이 adapter는 wikisem corpus의 LF 형식을 구조 보존하며 cg_ir로 변환한다.
GQ→FOL 변환(정리-동치)은 하지 않는다 — 2-람다 GQ 형(restriction+body)을
그대로 유지한다.

금지사항(AST 검사로 집행):
- File IO (open 호출 없음)
- Fixture/corpus 내장 (fixture/case_id/answer/expected_table/lookup 상수 없음)
- Refine/Verify 역류 (cg_oracle_adapter import 금지)

지원하는 구조:
- (Head arg1 arg2 ...) — Head가 구조 연산자가 아니면 pred
- (Some (\\x Restr) (\\x Body)) — exists with restriction + body
- (All (\\x Restr) (\\x Body)) — forall with restriction + body
- (^ A B ...) — and (n-ary)
- (\\x REST...) — lambda (REST가 여러 토큰이면 인라인 평탄 형태)
- True → {"kind":"pred","name":"True","args":[]}

지원하지 않는 head (fail-closed):
- Some, All → quantifier로 처리
- ^ → conjunction으로 처리
- 콜론을 포함하는 head (e.g., N-aD:zorble) → predicate
- 모든 다른 head → AdapterUnsupported 예외 발생
  (Equal, Intension, None, Gen, NNORD*, InAntecedentSet, InAnaphorSet, Qvar,
  미등록 head 등 모두 실패)

정량화된 람다(Some, All)의 두 람다:
- 이름이 다르면 capture-free 리네이밍으로 통일한다.
- 결박 변수는 하나이며, 제한과 본문 모두에 적용된다.

산출 검증:
- adapt()은 반환 전에 cg_ir.validate_formula()로 IR을 검증한다.
- 검증 실패는 AdapterUnsupported 예외를 발생시킨다.

예외:
- AdapterUnsupported: 미지원 구조 연산자, syntax 오류, 또는 산출 검증 실패
- AdapterSyntaxError: 괄호 불균형, 빈 입력 등
"""
from __future__ import annotations

import re
from typing import Any

import conceptgate.cg_ir as cg_ir


class AdapterUnsupported(Exception):
    """Unsupported LF construct or structural operator."""
    pass


class AdapterSyntaxError(Exception):
    """Syntax error in LF string (unbalanced parens, empty input, etc.)."""
    pass


def adapt(lf: str) -> dict:
    """Parse typed-lambda LF string and return cg_ir dict.

    Args:
        lf: wikisem format LF string

    Returns:
        cg_ir formula dict

    Raises:
        AdapterSyntaxError: if syntax is invalid
        AdapterUnsupported: if construct is not supported or output validation fails
    """
    if not lf or not lf.strip():
        raise AdapterSyntaxError("empty input")

    tokens = _tokenize(lf)
    if not tokens:
        raise AdapterSyntaxError("empty token stream")

    result, pos = _parse_expr(tokens, 0)
    if pos != len(tokens):
        raise AdapterSyntaxError(f"unexpected tokens after expression at position {pos}")

    # Validate output against cg_ir schema
    errors = cg_ir.validate_formula(result)
    if errors:
        raise AdapterUnsupported(f"output validation failed: {errors}")

    return result


def _collect_names(formula: dict) -> set[str]:
    """Collect all names that occur in a formula tree.

    Names include: var node names, entity node names, and quantifier var fields.
    """
    names = set()
    kind = formula.get("kind")

    if kind == "var":
        if "name" in formula:
            names.add(formula["name"])
    elif kind == "entity":
        if "name" in formula:
            names.add(formula["name"])
    elif kind == "pred":
        for arg in formula.get("args", []):
            names.update(_collect_names(arg))
    elif kind in ("forall", "exists"):
        if "var" in formula:
            names.add(formula["var"])
        if "restriction" in formula:
            names.update(_collect_names(formula["restriction"]))
        if "body" in formula:
            names.update(_collect_names(formula["body"]))
    elif kind in ("box", "diamond", "not"):
        if "body" in formula:
            names.update(_collect_names(formula["body"]))
    elif kind == "implies":
        if "left" in formula:
            names.update(_collect_names(formula["left"]))
        if "right" in formula:
            names.update(_collect_names(formula["right"]))
    elif kind in ("and", "or"):
        for arg in formula.get("args", []):
            names.update(_collect_names(arg))

    return names


def _rename_free_occurrences(formula: dict, old_name: str, new_name: str,
                             bound_vars: set[str] | None = None) -> dict:
    """Rename free occurrences of old_name to new_name in formula.

    A variable occurrence is free if it is not bound by a quantifier
    at that point in the tree.

    bound_vars: set of variable names currently bound by enclosing quantifiers.
    Returns a new dict with renames applied; does not modify the input.
    """
    if bound_vars is None:
        bound_vars = set()

    kind = formula.get("kind")

    if kind == "var":
        name = formula.get("name")
        if name == old_name and name not in bound_vars:
            return {"kind": "var", "name": new_name}
        return formula

    elif kind == "entity":
        return formula

    elif kind == "pred":
        new_args = []
        for arg in formula.get("args", []):
            new_args.append(_rename_free_occurrences(arg, old_name, new_name, bound_vars))
        return {"kind": "pred", "name": formula.get("name"), "args": new_args}

    elif kind in ("forall", "exists"):
        # When descending into a quantifier, add its var to bound_vars
        var = formula.get("var")
        new_bound = bound_vars | {var}
        new_restriction = None
        if "restriction" in formula:
            new_restriction = _rename_free_occurrences(
                formula["restriction"], old_name, new_name, new_bound)
        new_body = None
        if "body" in formula:
            new_body = _rename_free_occurrences(
                formula["body"], old_name, new_name, new_bound)
        result = {"kind": kind, "var": var}
        if new_restriction is not None:
            result["restriction"] = new_restriction
        if new_body is not None:
            result["body"] = new_body
        return result

    elif kind in ("box", "diamond", "not"):
        new_body = _rename_free_occurrences(formula.get("body"), old_name, new_name, bound_vars)
        return {"kind": kind, "body": new_body}

    elif kind == "implies":
        new_left = _rename_free_occurrences(formula.get("left"), old_name, new_name, bound_vars)
        new_right = _rename_free_occurrences(formula.get("right"), old_name, new_name, bound_vars)
        return {"kind": "implies", "left": new_left, "right": new_right}

    elif kind in ("and", "or"):
        new_args = []
        for arg in formula.get("args", []):
            new_args.append(_rename_free_occurrences(arg, old_name, new_name, bound_vars))
        return {"kind": kind, "args": new_args}

    return formula


def _unify_quantifier_binders(restr_var: str, restriction: dict,
                              body_var: str, body: dict) -> tuple[str, dict, dict]:
    """Unify two quantifier binders capture-free.

    Args:
        restr_var: variable name from restriction lambda
        restriction: parsed restriction formula
        body_var: variable name from body lambda
        body: parsed body formula

    Returns:
        (unified_var, renamed_restriction, renamed_body) where:
        - unified_var: the single variable that binds both restriction and body
        - renamed_restriction: restriction with free occurrences of restr_var renamed if needed
        - renamed_body: body with free occurrences of body_var renamed if needed
    """
    if restr_var == body_var:
        # Same name: nothing to rename
        return restr_var, restriction, body

    # Collect names in restriction and body
    names_restriction = _collect_names(restriction)
    names_body = _collect_names(body)

    # Rule 3: Check if restr_var appears in body
    if restr_var not in names_body:
        # restr_var does not occur in scope; use it and rename body_var to restr_var
        new_body = _rename_free_occurrences(body, body_var, restr_var)
        return restr_var, restriction, new_body

    # Rule 4: Pick a fresh name that occurs in neither restriction nor body
    target = restr_var
    counter = 2
    all_names = names_restriction | names_body
    while target in all_names:
        target = f"{restr_var}_{counter}"
        counter += 1

    # Rename free occurrences of restr_var to target in restriction
    new_restriction = _rename_free_occurrences(restriction, restr_var, target)
    # Rename free occurrences of body_var to target in body
    new_body = _rename_free_occurrences(body, body_var, target)

    return target, new_restriction, new_body


def _tokenize(lf: str) -> list[str]:
    """Tokenize LF string.

    Delimiters are ( ) and whitespace.
    Tokens can contain -, {, }, :
    Binders: \\x, \\x1, \\e1, etc.
    """
    tokens = []
    i = 0
    while i < len(lf):
        # Skip whitespace
        if lf[i].isspace():
            i += 1
            continue
        # Parentheses are individual tokens
        if lf[i] in "()":
            tokens.append(lf[i])
            i += 1
            continue
        # Otherwise, read a token until we hit delimiter or whitespace
        j = i
        while j < len(lf) and lf[j] not in "() \t\n\r":
            j += 1
        if i < j:
            tokens.append(lf[i:j])
        i = j
    return tokens


def _parse_expr(tokens: list[str], pos: int) -> tuple[dict, int]:
    """Parse an expression starting at pos.

    Returns (formula_dict, next_pos)
    """
    if pos >= len(tokens):
        raise AdapterSyntaxError("unexpected end of input")

    token = tokens[pos]

    # Atom: True
    if token == "True":
        return {"kind": "pred", "name": "True", "args": []}, pos + 1

    # Lambda: \\binder REST...
    if token.startswith("\\"):
        return _parse_lambda(tokens, pos)

    # List: (Head arg1 arg2 ...)
    if token == "(":
        return _parse_list(tokens, pos)

    # Atom: variable or entity
    if _is_variable(token):
        return {"kind": "var", "name": token}, pos + 1
    else:
        return {"kind": "entity", "name": token}, pos + 1


def _assert_head_is_in_v0_scope(head: str) -> None:
    """Guard: raise AdapterUnsupported if head is not in v0 scope.

    Allowed heads: Some, All, ^, True, and any head containing ':'.
    Raises:
        AdapterUnsupported: if head is not on the whitelist
    """
    if head not in ("Some", "All", "^", "True") and ":" not in head:
        raise AdapterUnsupported(f"unsupported head: {head}")


def _classify_head(head: str) -> str:
    """Classify head by whitelist rule. Return head kind or raise AdapterUnsupported.

    Returns:
        One of: "quantifier_some", "quantifier_all", "conjunction",
                "predicate" (includes True and category-tagged lexical predicates)

    Raises:
        AdapterUnsupported: if head is not on the whitelist
    """
    _assert_head_is_in_v0_scope(head)

    if head == "Some":
        return "quantifier_some"
    elif head == "All":
        return "quantifier_all"
    elif head == "^":
        return "conjunction"
    elif head == "True":
        return "predicate"
    else:
        # head contains ':' (category-tagged predicate)
        # e.g., N-aD:zorble, B-aN-b{A-aN}:be
        return "predicate"


def _parse_list(tokens: list[str], pos: int) -> tuple[dict, int]:
    """Parse (Head arg1 arg2 ...) or (\\binder REST...).

    pos should point to "("
    """
    if pos >= len(tokens) or tokens[pos] != "(":
        raise AdapterSyntaxError(f"expected '(' at position {pos}")

    pos += 1  # skip "("

    if pos >= len(tokens):
        raise AdapterSyntaxError("unexpected end of input after '('")

    if tokens[pos] == ")":
        raise AdapterSyntaxError("empty list not allowed")

    # Check if this is a lambda form
    if tokens[pos].startswith("\\"):
        # Lambda form: (\\binder REST...)
        # Delegate to lambda parsing
        binder = tokens[pos]
        var_name = binder[1:]
        pos += 1

        # Parse REST until we see ")"
        if pos >= len(tokens):
            raise AdapterSyntaxError("unexpected end of input in lambda body")

        if tokens[pos] == ")":
            raise AdapterSyntaxError("lambda body is empty")

        # Parse body (could be nested or inline)
        body = _parse_lambda_body_content(tokens, pos)
        # body is (expr_dict, next_pos), advance pos
        body, pos = body

        # Expect closing ")"
        if pos >= len(tokens) or tokens[pos] != ")":
            raise AdapterSyntaxError(f"expected ')' to close lambda at position {pos}")
        pos += 1

        return body, pos

    head = tokens[pos]
    pos += 1

    # Classify head with whitelist
    head_kind = _classify_head(head)

    # Handle quantifiers: Some, All
    if head_kind == "quantifier_some":
        return _parse_quantifier(tokens, pos, "exists")
    elif head_kind == "quantifier_all":
        return _parse_quantifier(tokens, pos, "forall")
    elif head_kind == "conjunction":
        return _parse_conjunction(tokens, pos)
    else:
        # Regular predicate application
        return _parse_pred_application(head, tokens, pos)


def _parse_quantifier(tokens: list[str], pos: int, quantifier_type: str) -> tuple[dict, int]:
    """Parse (Some/All (\\x Restr) (\\x Body)).

    pos should point after Some/All.
    Unifies the two lambda binders capture-free if they differ.
    """
    # Parse (\\x Restr)
    if pos >= len(tokens) or tokens[pos] != "(":
        raise AdapterSyntaxError(f"expected '(' for quantifier restriction at position {pos}")

    restr_var, restriction, pos = _parse_lambda_form(tokens, pos)

    # Parse (\\x Body)
    if pos >= len(tokens) or tokens[pos] != "(":
        raise AdapterSyntaxError(f"expected '(' for quantifier body at position {pos}")

    body_var, body, pos = _parse_lambda_form(tokens, pos)

    # Unify the two binders
    var, restriction, body = _unify_quantifier_binders(
        restr_var, restriction, body_var, body)

    # Expect closing ")"
    if pos >= len(tokens) or tokens[pos] != ")":
        raise AdapterSyntaxError(f"expected ')' to close quantifier at position {pos}")
    pos += 1

    result = {
        "kind": quantifier_type,
        "var": var,
        "restriction": restriction,
        "body": body
    }
    return result, pos


def _parse_lambda_body_content(tokens: list[str], pos: int) -> tuple[dict, int]:
    """Parse lambda body content — could be single expr or inline form.

    Called after consuming "(" and binder token.
    pos points to first token of body content.
    Returns (body_expr, next_pos) where next_pos points to ")" that closes the lambda.
    """
    if pos >= len(tokens):
        raise AdapterSyntaxError("unexpected end of input in lambda body")

    if tokens[pos] == ")":
        raise AdapterSyntaxError("lambda body is empty")

    # Check if next token is "(" (nested expr) or not (inline form)
    if tokens[pos] == "(":
        # Nested form: (\\x (expr))
        body, pos = _parse_expr(tokens, pos)
        return body, pos
    else:
        # Inline form: (\\x Head arg1 arg2 ...)
        head = tokens[pos]
        pos += 1

        # Classify head with whitelist
        head_kind = _classify_head(head)

        # Handle inline quantifiers specially
        if head_kind == "quantifier_some":
            # Some in lambda body: Some (\\y Restr) (\\y Body)
            # Parse two lambda forms
            if pos >= len(tokens) or tokens[pos] != "(":
                raise AdapterSyntaxError(f"expected lambda restriction in Some at position {pos}")
            restr_var, restriction, pos = _parse_lambda_form(tokens, pos)

            if pos >= len(tokens) or tokens[pos] != "(":
                raise AdapterSyntaxError(f"expected lambda body in Some at position {pos}")
            body_var, body_expr, pos = _parse_lambda_form(tokens, pos)

            # Unify the two binders
            var, restriction, body_expr = _unify_quantifier_binders(
                restr_var, restriction, body_var, body_expr)

            body = {
                "kind": "exists",
                "var": var,
                "restriction": restriction,
                "body": body_expr
            }
            return body, pos
        elif head_kind == "quantifier_all":
            # All in lambda body: All (\\y Restr) (\\y Body)
            if pos >= len(tokens) or tokens[pos] != "(":
                raise AdapterSyntaxError(f"expected lambda restriction in All at position {pos}")
            restr_var, restriction, pos = _parse_lambda_form(tokens, pos)

            if pos >= len(tokens) or tokens[pos] != "(":
                raise AdapterSyntaxError(f"expected lambda body in All at position {pos}")
            body_var, body_expr, pos = _parse_lambda_form(tokens, pos)

            # Unify the two binders
            var, restriction, body_expr = _unify_quantifier_binders(
                restr_var, restriction, body_var, body_expr)

            body = {
                "kind": "forall",
                "var": var,
                "restriction": restriction,
                "body": body_expr
            }
            return body, pos
        elif head_kind == "conjunction":
            # Conjunction: ^ arg1 arg2 ...
            args = []
            while pos < len(tokens) and tokens[pos] != ")":
                arg, pos = _parse_expr(tokens, pos)
                args.append(arg)
            body = {"kind": "and", "args": args}
            return body, pos
        else:
            # Regular inline predicate
            args = []
            while pos < len(tokens) and tokens[pos] != ")":
                arg, pos = _parse_expr(tokens, pos)
                args.append(arg)
            body = {"kind": "pred", "name": head, "args": args}
            return body, pos


def _parse_lambda_form(tokens: list[str], pos: int) -> tuple[str, dict, int]:
    """Parse (\\x REST...) and return (binder_var, body_expr, next_pos).

    pos should point to "(".
    """
    if pos >= len(tokens) or tokens[pos] != "(":
        raise AdapterSyntaxError(f"expected '(' at position {pos}")

    pos += 1  # skip "("

    if pos >= len(tokens):
        raise AdapterSyntaxError("unexpected end of input after '('")

    # Expect binder
    binder = tokens[pos]
    if not binder.startswith("\\"):
        raise AdapterSyntaxError(f"expected lambda binder, got {binder!r} at position {pos}")

    var_name = binder[1:]  # Strip the backslash
    pos += 1

    # Parse body content
    body, pos = _parse_lambda_body_content(tokens, pos)

    # Expect closing ")"
    if pos >= len(tokens) or tokens[pos] != ")":
        raise AdapterSyntaxError(f"expected ')' to close lambda at position {pos}")
    pos += 1

    return var_name, body, pos


def _parse_conjunction(tokens: list[str], pos: int) -> tuple[dict, int]:
    """Parse (^ A B ...) — n-ary conjunction.

    pos should point after "^".
    """
    args = []
    while pos < len(tokens) and tokens[pos] != ")":
        arg, pos = _parse_expr(tokens, pos)
        args.append(arg)

    if pos >= len(tokens):
        raise AdapterSyntaxError("unmatched '(' in conjunction")

    # Expect closing ")"
    if tokens[pos] != ")":
        raise AdapterSyntaxError(f"expected ')', got {tokens[pos]!r} at position {pos}")
    pos += 1

    return {"kind": "and", "args": args}, pos


def _parse_pred_application(head: str, tokens: list[str], pos: int) -> tuple[dict, int]:
    """Parse (Head arg1 arg2 ...) as a predicate application.

    pos should point after head token, and we're inside a list.
    """
    args = []
    while pos < len(tokens) and tokens[pos] != ")":
        arg, pos = _parse_expr(tokens, pos)
        args.append(arg)

    if pos >= len(tokens):
        raise AdapterSyntaxError("unmatched '(' in predicate application")

    # Expect closing ")"
    if tokens[pos] != ")":
        raise AdapterSyntaxError(f"expected ')', got {tokens[pos]!r} at position {pos}")
    pos += 1

    return {"kind": "pred", "name": head, "args": args}, pos


def _is_variable(token: str) -> bool:
    """Check if token is a variable (lowercase start + optional digits)."""
    if not token or token.startswith("\\"):
        return False
    # Variables start with lowercase letter
    return token[0].islower()
