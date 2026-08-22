"""Canonical comparison desugaring of IR quantifier restrictions.

Per D-E2E-v1-23 §5/§9/§12: This module applies definitional desugaring of the
IR's own quantifier constructors at the CANONICAL COMPARISON layer. It is NOT
logical rewriting or theorem equivalence — the transformations are syntactic
lowering of restricted quantifiers to their neutral (True-restricted) form.

Desugaring rules:
  FORALL(x, R, B) where R ≠ True  →  FORALL(x, True, IMPLIES(R, B))
  EXISTS(x, R, B) where R ≠ True  →  EXISTS(x, True, AND(R, B))
  Neutral inputs (True restriction) are fixed points; recurse into body.
  Other kinds: recurse into child formulas.

Why at comparison layer (§10): The desugarer lives between subject output and
canonical comparison, never enlarging the estimand. Subject dialect remains
unchanged; only the comparison inputs are normalized.

Quantifier order is never reordered (§7). This is definitional desugaring of
constructors, not logical rewriting. Input mutation is forbidden — this is a
pure function (deep copy semantics).
"""
from __future__ import annotations

import copy
from typing import Any


def desugar(formula: dict) -> dict:
    """Desugar a formula by lowering restricted quantifiers to neutral form.

    Pure function: input is never modified. Returns a deep copy with
    restricted quantifiers rewritten to equivalent neutral form.

    Args:
        formula: A formula dict in the IR schema.

    Returns:
        A desugared formula dict (logically equivalent, syntactically normalized).
    """
    # Deep copy to ensure no mutation
    working = copy.deepcopy(formula)

    # Helper to check if a restriction is the True predicate
    def is_true_pred(restriction: Any) -> bool:
        return (
            isinstance(restriction, dict)
            and restriction.get("kind") == "pred"
            and restriction.get("name") == "True"
            and restriction.get("args") == []
        )

    # Helper to recursively desugar a formula
    def desugar_inner(f: dict) -> dict:
        if not isinstance(f, dict):
            return f

        kind = f.get("kind")

        # Handle forall with non-True restriction
        if kind == "forall":
            var = f.get("var")
            restriction = f.get("restriction")
            body = f.get("body")

            if restriction is not None and not is_true_pred(restriction):
                # Transform: FORALL(x, R, B) → FORALL(x, True, IMPLIES(R, B))
                true_pred = {"kind": "pred", "name": "True", "args": []}
                implies_body = {
                    "kind": "implies",
                    "left": desugar_inner(restriction),
                    "right": desugar_inner(body)
                }
                return {
                    "kind": "forall",
                    "var": var,
                    "restriction": true_pred,
                    "body": implies_body
                }
            else:
                # True-restricted forall: keep shape, recurse into body
                desugared_body = desugar_inner(body) if body is not None else body
                return {
                    "kind": "forall",
                    "var": var,
                    "restriction": restriction,
                    "body": desugared_body
                }

        # Handle exists with non-True restriction
        elif kind == "exists":
            var = f.get("var")
            restriction = f.get("restriction")
            body = f.get("body")

            if restriction is not None and not is_true_pred(restriction):
                # Transform: EXISTS(x, R, B) → EXISTS(x, True, AND(R, B))
                true_pred = {"kind": "pred", "name": "True", "args": []}
                and_body = {
                    "kind": "and",
                    "args": [desugar_inner(restriction), desugar_inner(body)]
                }
                return {
                    "kind": "exists",
                    "var": var,
                    "restriction": true_pred,
                    "body": and_body
                }
            else:
                # True-restricted exists: keep shape, recurse into body
                desugared_body = desugar_inner(body) if body is not None else body
                return {
                    "kind": "exists",
                    "var": var,
                    "restriction": restriction,
                    "body": desugared_body
                }

        # Handle other formula kinds
        elif kind == "implies":
            return {
                "kind": "implies",
                "left": desugar_inner(f.get("left")),
                "right": desugar_inner(f.get("right"))
            }

        elif kind == "and":
            args = f.get("args", [])
            return {
                "kind": "and",
                "args": [desugar_inner(arg) for arg in args]
            }

        elif kind == "or":
            args = f.get("args", [])
            return {
                "kind": "or",
                "args": [desugar_inner(arg) for arg in args]
            }

        elif kind == "not":
            return {
                "kind": "not",
                "body": desugar_inner(f.get("body"))
            }

        elif kind == "box":
            return {
                "kind": "box",
                "body": desugar_inner(f.get("body"))
            }

        elif kind == "diamond":
            return {
                "kind": "diamond",
                "body": desugar_inner(f.get("body"))
            }

        # Leaf nodes: pred, var, entity, etc. — no desugaring
        else:
            return f

    return desugar_inner(working)
