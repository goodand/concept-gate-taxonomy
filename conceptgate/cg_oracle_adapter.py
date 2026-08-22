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

미지원 (fail-closed):
- 구조 연산자 중 Equal, Intension, None (람다 인자), Gen, NNORD*, InAntecedentSet 등
- 단, InAnaphorSet 같은 var-arg-only predicate는 일반 pred로 통과

예외:
- AdapterUnsupported: 미지원 구조 연산자 또는 syntax 오류
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
        AdapterUnsupported: if construct is not supported
    """
    if not lf or not lf.strip():
        raise AdapterSyntaxError("empty input")

    tokens = _tokenize(lf)
    if not tokens:
        raise AdapterSyntaxError("empty token stream")

    result, pos = _parse_expr(tokens, 0)
    if pos != len(tokens):
        raise AdapterSyntaxError(f"unexpected tokens after expression at position {pos}")
    return result


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

    # Check for unsupported structural operators that take lambda args
    # Equal, Intension, None (with lambda), Gen, NNORD*, InAntecedentSet
    unsupported_ops = {"Equal", "Intension", "None", "Gen",
                       "NNORD", "NNORDSUP", "InAntecedentSet"}

    # Handle quantifiers: Some, All
    if head == "Some":
        return _parse_quantifier(tokens, pos, "exists")
    elif head == "All":
        return _parse_quantifier(tokens, pos, "forall")
    elif head == "^":
        return _parse_conjunction(tokens, pos)
    elif head in unsupported_ops or _is_unsupported_structural_op(head):
        raise AdapterUnsupported(f"unsupported structural operator: {head}")
    else:
        # Regular predicate application
        return _parse_pred_application(head, tokens, pos)


def _parse_quantifier(tokens: list[str], pos: int, quantifier_type: str) -> tuple[dict, int]:
    """Parse (Some/All (\\x Restr) (\\x Body)).

    pos should point after Some/All.
    """
    # Parse (\\x Restr)
    if pos >= len(tokens) or tokens[pos] != "(":
        raise AdapterSyntaxError(f"expected '(' for quantifier restriction at position {pos}")

    restr_var, restriction, pos = _parse_lambda_form(tokens, pos)

    # Parse (\\x Body)
    if pos >= len(tokens) or tokens[pos] != "(":
        raise AdapterSyntaxError(f"expected '(' for quantifier body at position {pos}")

    body_var, body, pos = _parse_lambda_form(tokens, pos)

    # Variables should match (both binded by same quantifier)
    # But in canonical form they'll be renamed, so we just use one
    var = restr_var

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

        # Handle inline quantifiers specially
        if head == "Some":
            # Some in lambda body: Some (\\y Restr) (\\y Body)
            # Parse two lambda forms
            if pos >= len(tokens) or tokens[pos] != "(":
                raise AdapterSyntaxError(f"expected lambda restriction in Some at position {pos}")
            restr_var, restriction, pos = _parse_lambda_form(tokens, pos)

            if pos >= len(tokens) or tokens[pos] != "(":
                raise AdapterSyntaxError(f"expected lambda body in Some at position {pos}")
            body_var, body_expr, pos = _parse_lambda_form(tokens, pos)

            body = {
                "kind": "exists",
                "var": restr_var,
                "restriction": restriction,
                "body": body_expr
            }
            return body, pos
        elif head == "All":
            # All in lambda body: All (\\y Restr) (\\y Body)
            if pos >= len(tokens) or tokens[pos] != "(":
                raise AdapterSyntaxError(f"expected lambda restriction in All at position {pos}")
            restr_var, restriction, pos = _parse_lambda_form(tokens, pos)

            if pos >= len(tokens) or tokens[pos] != "(":
                raise AdapterSyntaxError(f"expected lambda body in All at position {pos}")
            body_var, body_expr, pos = _parse_lambda_form(tokens, pos)

            body = {
                "kind": "forall",
                "var": restr_var,
                "restriction": restriction,
                "body": body_expr
            }
            return body, pos
        elif head == "^":
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


def _is_unsupported_structural_op(head: str) -> bool:
    """Check if head is an unsupported structural operator.

    Rule: uppercase start + takes lambda args.
    But avoid false positives like InAnaphorSet (takes only var args).
    """
    if not head or not head[0].isupper():
        return False

    # Known var-arg-only predicates that should pass through
    var_arg_only = {"InAnaphorSet", "Qvar"}

    if head in var_arg_only:
        return False

    # All other uppercase-starting heads that aren't explicitly var-arg-only
    # and aren't the known quantifiers/operators
    known_pass = {"Some", "All", "True"}
    if head in known_pass:
        return False

    # If it's uppercase and not in var_arg_only, assume it's structural
    # Actually, let's be conservative: only reject if it looks structural
    # (i.e., we expect it to take lambda arguments)

    # For now, use the explicit list from the spec
    structural_ops = {"Equal", "Intension", "None", "Gen",
                      "NNORD", "NNORDSUP", "InAntecedentSet"}

    if head in structural_ops:
        return True

    # Default: if uppercase and not var-arg-only, might be structural
    # But be conservative — only reject if explicitly listed
    return False
