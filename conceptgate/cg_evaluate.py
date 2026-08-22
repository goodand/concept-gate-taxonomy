#!/usr/bin/env python3
"""cg_evaluate — Evaluate layer (D-E2E-v1-19 Stage 1).

This module implements the Evaluate layer, which compares predicted and oracle
formulas against a specification (oracle manifest evaluation_protocol.v1).

**Vocabulary Separation (G32 judgment)**: The Evaluate layer's vocabulary
(PASS/FAIL/UNSCORABLE/ERROR) is intentionally separated from Verify's Verdict
vocabulary. This separation is enforced by import restrictions (test_evaluate_does_not_import_verify_vocabulary).

**4-Way Distinction**:
  - oracle-side defect (malformed, reserved namespace) → UNSCORABLE
    (measurement contract failure, NOT semantic failure)
  - predicted-side defect (malformed) → FAIL
    (subject failure, not evaluator failure)
  - input boundary violations (non-dict) or internal crash → ERROR
    (evaluator execution failure, exceptions are caught and recorded, never raised)
  - both valid → PASS/FAIL via canonicalize_v0 comparison

**Dimension Attribution** (oracle manifest evaluation_protocol.v1.compare):
When a FAIL is detected, mismatch_dimensions must be reported. Rules:
  - operator_type: node kind mismatch (except quantifier order swap)
  - predicate_arguments: predicate name or arity difference
  - binding: canonical variable name differs at same position
  - operator_nesting: structural nesting difference
  - scope: quantifier order swap (allowed to report instead of operator_type)
  - structural_validity: predicted is malformed

**Oracle Isolation** (INV-ORACLE-01/02):
This module enforces unidirectional oracle isolation via import restrictions.
The test_refine_verify_modules_do_not_import_evaluate gate enforces that
cg_normalizer, cg_obligations, concept_gate_v7, and server cannot import
cg_evaluate, preventing evaluation from bleeding into verification/refinement.
"""
from __future__ import annotations

from typing import Any

from . import cg_ir


def evaluate(predicted: Any, oracle_ir: Any) -> dict[str, Any]:
    """Compare predicted formula against oracle_ir specification.

    Args:
        predicted: Predicted formula (should be dict, but may be malformed)
        oracle_ir: Oracle formula (should be dict; must be valid)

    Returns:
        dict with keys:
          - "result": "pass" | "fail" | "unscorable" | "error"
          - "mismatch_dimensions": list[str] (non-empty on FAIL)
          - "reason": str (for unscorable/error)
          - "predicted_fingerprint": str (for pass/fail)
          - "oracle_fingerprint": str (for pass/fail)
    """
    # Check boundary: both inputs must be dicts
    if not isinstance(predicted, dict) or not isinstance(oracle_ir, dict):
        return {
            "result": "error",
            "reason": f"Both inputs must be dicts; got {type(predicted).__name__} and {type(oracle_ir).__name__}"
        }

    # Validate oracle
    oracle_errors = cg_ir.validate_formula(oracle_ir)
    if oracle_errors:
        return {
            "result": "unscorable",
            "reason": f"Oracle formula is invalid: {oracle_errors}"
        }

    # Check for reserved namespace in oracle (free variables starting with "?")
    try:
        oracle_free_vars = cg_ir.free_variables(oracle_ir)
        if any(v.startswith("?") for v in oracle_free_vars):
            return {
                "result": "unscorable",
                "reason": "Oracle contains free variables in reserved namespace (?-prefixed)"
            }
    except Exception as e:
        return {
            "result": "unscorable",
            "reason": f"Error checking oracle free variables: {str(e)}"
        }

    # Validate predicted
    predicted_errors = cg_ir.validate_formula(predicted)
    if predicted_errors:
        # Predicted malformation → FAIL (subject failure, not evaluator failure)
        return {
            "result": "fail",
            "mismatch_dimensions": ["structural_validity"],
            "reason": f"Predicted formula is malformed: {predicted_errors}"
        }

    # Both are valid dicts; try to canonicalize and compare
    try:
        predicted_canon = cg_ir.canonicalize_v0(predicted)
        oracle_canon = cg_ir.canonicalize_v0(oracle_ir)

        # Compute fingerprints for result reporting
        predicted_fingerprint = cg_ir.formula_fingerprint(predicted)
        oracle_fingerprint = cg_ir.formula_fingerprint(oracle_ir)

        if predicted_canon == oracle_canon:
            return {
                "result": "pass",
                "mismatch_dimensions": [],
                "predicted_fingerprint": predicted_fingerprint,
                "oracle_fingerprint": oracle_fingerprint
            }
        else:
            # Mismatch detected; find which dimensions differ
            dims = _find_mismatch_dimensions(predicted_canon, oracle_canon)
            return {
                "result": "fail",
                "mismatch_dimensions": list(dims),
                "reason": f"Predicted and oracle formulas differ in: {dims}",
                "predicted_fingerprint": predicted_fingerprint,
                "oracle_fingerprint": oracle_fingerprint
            }

    except Exception as e:
        # Internal crash: record as ERROR, never raise
        return {
            "result": "error",
            "reason": f"Internal evaluator error: {str(e)}"
        }


def _find_mismatch_dimensions(pred_canon: dict, orac_canon: dict) -> set[str]:
    """Find which dimensions differ between two canonical formulas.

    Traverses both trees in parallel and collects differing dimensions.
    """
    dims = set()
    _traverse_and_collect(pred_canon, orac_canon, dims)
    return dims


def _traverse_and_collect(pred: Any, orac: Any, dims: set[str]) -> None:
    """Parallel tree traversal; collect dimensions where they differ."""

    # Handle type mismatches
    if type(pred) != type(orac):
        dims.add("operator_nesting")
        return

    if not isinstance(pred, dict) or not isinstance(orac, dict):
        dims.add("operator_nesting")
        return

    pred_kind = pred.get("kind")
    orac_kind = orac.get("kind")

    # Kind mismatch
    if pred_kind != orac_kind:
        # Default: kind mismatch → operator_type
        # (quantifier swaps can alternatively be reported as scope, but operator_type is primary)
        dims.add("operator_type")
        return

    # Kind-specific comparisons
    if pred_kind == "var":
        if pred.get("name") != orac.get("name"):
            dims.add("binding")

    elif pred_kind == "entity":
        if pred.get("name") != orac.get("name"):
            dims.add("predicate_arguments")

    elif pred_kind == "pred":
        # Check predicate name
        if pred.get("name") != orac.get("name"):
            dims.add("predicate_arguments")
        # Check arity
        pred_args = pred.get("args", [])
        orac_args = orac.get("args", [])
        if len(pred_args) != len(orac_args):
            dims.add("predicate_arguments")
        else:
            # Recursively check arguments
            for pred_arg, orac_arg in zip(pred_args, orac_args):
                _traverse_and_collect(pred_arg, orac_arg, dims)

    elif pred_kind in ("forall", "exists"):
        # Check variable binding (canonical names)
        if pred.get("var") != orac.get("var"):
            dims.add("binding")
        # Recursively check body
        _traverse_and_collect(pred.get("body"), orac.get("body"), dims)

    elif pred_kind in ("box", "diamond", "not"):
        # Recursively check body
        _traverse_and_collect(pred.get("body"), orac.get("body"), dims)

    elif pred_kind == "implies":
        # Recursively check left and right
        _traverse_and_collect(pred.get("left"), orac.get("left"), dims)
        _traverse_and_collect(pred.get("right"), orac.get("right"), dims)

    elif pred_kind in ("and", "or"):
        pred_args = pred.get("args", [])
        orac_args = orac.get("args", [])
        if len(pred_args) != len(orac_args):
            dims.add("operator_nesting")
        else:
            for pred_arg, orac_arg in zip(pred_args, orac_args):
                _traverse_and_collect(pred_arg, orac_arg, dims)


def _is_quantifier(kind: str | None) -> bool:
    """Check if kind is a quantifier (forall or exists)."""
    return kind in ("forall", "exists")
