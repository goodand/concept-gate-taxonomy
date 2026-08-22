#!/usr/bin/env python3
"""FOL adapter (FOLIO_FOL_V0 profile) — parse FOLIO-style first-order logic into cg_ir.

Implements D-E2E-v1-23 §12 with the asymmetric mapping for universal quantifiers:
- ∀v (A → B) where → is the TOP-LEVEL node: emit forall with A as restriction, B as body
  ("definitional representation lowering")
- ∀v φ otherwise: neutral forall with True restriction
- ∃v φ: always neutral (restriction = True), NEVER split φ's conjunction

Prefix quantifier chains (∀x ∃y φ) are parsed in order (hard invariant).
Implications must NEVER cross quantifier boundaries (side-conditioned theorem).

Forbidden operators: ∨ = ⊕ ↔ — refuse with AdapterUnsupported wherever they appear.
Precedence: ¬ (tightest) > ∧ (n-ary, flatten) > → (binary, right-associative).
Term rule: identifier is var if bound by ENCLOSING quantifier, else entity.
By construction, all outputs are closed (free_variables == set()).
"""
from __future__ import annotations

from typing import Any

import conceptgate.cg_ir


class AdapterUnsupported(Exception):
    """Raised when an unsupported operator or syntax is encountered."""
    pass


class AdapterSyntaxError(Exception):
    """Raised when the input violates the grammar."""
    pass


def tokenize(s: str) -> list[tuple[str, str]]:
    """Tokenize FOL string into (type, value) pairs.

    Token types: "quantifier", "neg", "and", "implies", "lparen", "rparen",
                 "comma", "pred", "var_or_entity"
    """
    tokens = []
    i = 0
    while i < len(s):
        c = s[i]

        # Skip whitespace
        if c.isspace():
            i += 1
            continue

        # Quantifier: ∀ or ∃, possibly followed by whitespace and a variable
        if c in "∀∃":
            quant = c
            j = i + 1
            # Skip whitespace after quantifier
            while j < len(s) and s[j].isspace():
                j += 1
            # Check if next is a valid variable name
            if j < len(s) and (s[j].isalpha() or s[j] == "_"):
                # Read variable name
                var_start = j
                while j < len(s) and (s[j].isalnum() or s[j] == "_"):
                    j += 1
                var = s[var_start:j]
                tokens.append(("quantifier", quant + var))
                i = j
            else:
                raise AdapterSyntaxError(f"quantifier {quant} not followed by variable")

        # Negation: ¬
        elif c == "¬":
            tokens.append(("neg", "¬"))
            i += 1

        # Conjunction: ∧
        elif c == "∧":
            tokens.append(("and", "∧"))
            i += 1

        # Implication: →
        elif c == "→":
            tokens.append(("implies", "→"))
            i += 1

        # Parentheses
        elif c == "(":
            tokens.append(("lparen", "("))
            i += 1
        elif c == ")":
            tokens.append(("rparen", ")"))
            i += 1

        # Comma
        elif c == ",":
            tokens.append(("comma", ","))
            i += 1

        # Predicate or variable/entity: starts with letter or underscore
        elif c.isalpha() or c == "_":
            start = i
            while i < len(s) and (s[i].isalnum() or s[i] == "_"):
                i += 1
            name = s[start:i]

            # Check if followed by '(' → it's a predicate
            j = i
            while j < len(s) and s[j].isspace():
                j += 1
            if j < len(s) and s[j] == "(":
                tokens.append(("pred", name))
                i = j
            else:
                # It's a variable or entity identifier
                tokens.append(("var_or_entity", name))
                i = j

        else:
            raise AdapterSyntaxError(f"unexpected character: {c!r}")

    return tokens


class ParserWithScope:
    """Parser that tracks bound variable scope during parsing.

    Grammar (quantifiers do NOT consume implications):
    - formula = implication
    - implication = quantifier_chain (→ implication)?
    - quantifier_chain = quantifier+ quantifier_chain | conjunction
    - conjunction = negation (∧ negation)*
    - negation = ¬ negation | atom
    - atom = pred(args) | (formula)
    """

    def __init__(self, tokens: list[tuple[str, str]]):
        self.tokens = tokens
        self.pos = 0
        self.bound_vars: set[str] = set()

    def at_end(self) -> bool:
        return self.pos >= len(self.tokens)

    def peek(self) -> tuple[str, str] | None:
        if self.at_end():
            return None
        return self.tokens[self.pos]

    def consume(self, expected_type: str | None = None) -> tuple[str, str]:
        if self.at_end():
            raise AdapterSyntaxError("unexpected end of input")
        tok_type, tok_val = self.tokens[self.pos]
        if expected_type and tok_type != expected_type:
            raise AdapterSyntaxError(f"expected {expected_type}, got {tok_type}")
        self.pos += 1
        return tok_type, tok_val

    def parse_formula(self) -> dict:
        """Parse a formula (top-level)."""
        return self.parse_implication()

    def parse_implication(self) -> dict:
        """Parse implications (right-associative)."""
        left = self.parse_quantifier_chain()

        if self.peek() and self.peek()[0] == "implies":
            self.consume("implies")
            right = self.parse_implication()
            return {"kind": "implies", "left": left, "right": right}

        return left

    def parse_quantifier_chain(self) -> dict:
        """Parse quantifier prefix chain (∀x ∃y φ)."""
        if not self.peek() or self.peek()[0] != "quantifier":
            return self.parse_conjunction()

        _, quant_var = self.consume("quantifier")
        if quant_var[0] == "∀":
            quant = "∀"
            var = quant_var[1:]
        else:  # ∃
            quant = "∃"
            var = quant_var[1:]

        old_bound = self.bound_vars.copy()
        self.bound_vars.add(var)

        body = self.parse_quantifier_chain()

        self.bound_vars = old_bound

        if quant == "∀":
            if body.get("kind") == "implies":
                restriction = body["left"]
                new_body = body["right"]
                return {
                    "kind": "forall",
                    "var": var,
                    "restriction": restriction,
                    "body": new_body
                }
            else:
                return {
                    "kind": "forall",
                    "var": var,
                    "restriction": {"kind": "pred", "name": "True", "args": []},
                    "body": body
                }
        else:  # ∃
            return {
                "kind": "exists",
                "var": var,
                "restriction": {"kind": "pred", "name": "True", "args": []},
                "body": body
            }

    def parse_conjunction(self) -> dict:
        """Parse conjunctions (n-ary, flatten consecutive)."""
        args = [self.parse_negation()]

        while self.peek() and self.peek()[0] == "and":
            self.consume("and")
            args.append(self.parse_negation())

        if len(args) == 1:
            return args[0]
        return {"kind": "and", "args": args}

    def parse_negation(self) -> dict:
        """Parse negations."""
        if self.peek() and self.peek()[0] == "neg":
            self.consume("neg")
            body = self.parse_negation()
            return {"kind": "not", "body": body}

        return self.parse_atom()

    def parse_atom(self) -> dict:
        """Parse atoms: predicates or parenthesized formulas."""
        tok = self.peek()
        if not tok:
            raise AdapterSyntaxError("expected atom, got end of input")

        tok_type, tok_val = tok

        if tok_type == "lparen":
            self.consume("lparen")
            formula = self.parse_formula()
            self.consume("rparen")
            return formula

        if tok_type == "pred":
            self.consume("pred")
            self.consume("lparen")

            args = []
            if self.peek() and self.peek()[0] != "rparen":
                args.append(self.parse_term())
                while self.peek() and self.peek()[0] == "comma":
                    self.consume("comma")
                    args.append(self.parse_term())

            self.consume("rparen")
            return {"kind": "pred", "name": tok_val, "args": args}

        raise AdapterSyntaxError(f"expected atom, got {tok_type}: {tok_val}")

    def parse_term(self) -> dict:
        """Parse a term (variable or entity)."""
        tok = self.peek()
        if not tok or tok[0] != "var_or_entity":
            raise AdapterSyntaxError(f"expected identifier, got {tok}")

        _, name = self.consume("var_or_entity")

        if name in self.bound_vars:
            return {"kind": "var", "name": name}
        else:
            return {"kind": "entity", "name": name}


def adapt_fol(fol: str) -> dict:
    """Parse a FOLIO-style first-order logic string into a cg_ir formula dict.

    Implements the FOLIO_FOL_V0 profile (D-E2E-v1-23 §12).

    Args:
        fol: A string in FOLIO_FOL_V0 profile.

    Returns:
        A formula dict conforming to cg_ir schema.

    Raises:
        AdapterUnsupported: if forbidden operators (∨ = ⊕ ↔) appear or validation fails.
        AdapterSyntaxError: if the input violates the grammar.
    """
    if not fol or not fol.strip():
        raise AdapterSyntaxError("empty input")

    for op in ["∨", "=", "⊕", "↔"]:
        if op in fol:
            raise AdapterUnsupported(f"forbidden operator: {op}")

    try:
        tokens = tokenize(fol)
    except Exception as e:
        raise AdapterSyntaxError(str(e)) from e

    if not tokens:
        raise AdapterSyntaxError("no tokens")

    parser = ParserWithScope(tokens)
    try:
        formula = parser.parse_formula()
    except AdapterSyntaxError:
        raise
    except AdapterUnsupported:
        raise
    except Exception as e:
        raise AdapterSyntaxError(f"parse error: {e}") from e

    if not parser.at_end():
        raise AdapterSyntaxError("unexpected trailing tokens")

    errors = conceptgate.cg_ir.validate_formula(formula)
    if errors:
        raise AdapterUnsupported(f"formula validation failed: {errors}")

    free = conceptgate.cg_ir.free_variables(formula)
    if free:
        raise AdapterUnsupported(f"formula has free variables: {free}")

    return formula
