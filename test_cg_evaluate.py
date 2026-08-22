"""cg_evaluate의 TDD 계약 (D-E2E-v1-19 Stage 1) — RED 먼저.

Evaluate layer의 어휘는 PASS/FAIL/UNSCORABLE/ERROR이고 Verify의 Verdict와
**통일 금지**(G32 판정). 4치 경계:
  - oracle측 결함(비표현·예약침범) → UNSCORABLE  (측정 계약의 실패)
  - predicted측 결함(비정형)        → FAIL        (주체의 실패)
  - 경계 위반(비dict)·내부 crash    → ERROR       (평가기 실행 실패, raise 금지)
차원: operator_type / operator_nesting / scope / binding / predicate_arguments
(oracle manifest evaluation_protocol.v1.compare).
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from conceptgate import cg_evaluate as ev


def V(n): return {"kind": "var", "name": n}
def P(name, *args): return {"kind": "pred", "name": name, "args": list(args)}
def FORALL(v, b): return {"kind": "forall", "var": v, "body": b}
def EXISTS(v, b): return {"kind": "exists", "var": v, "body": b}
def BOX(b): return {"kind": "box", "body": b}
def IMPLIES(l, r): return {"kind": "implies", "left": l, "right": r}


# ------------------------------------------------------------- PASS -------

def test_alpha_variants_pass():
    pred = FORALL("x", EXISTS("y", P("R", V("x"), V("y"))))
    orac = FORALL("a", EXISTS("b", P("R", V("a"), V("b"))))
    out = ev.evaluate(pred, orac)
    assert out["result"] == "pass"
    assert out["mismatch_dimensions"] == []


def test_evaluation_is_deterministic():
    pred = FORALL("x", P("P", V("x")))
    assert ev.evaluate(pred, pred) == ev.evaluate(pred, pred)


# ------------------------------------------------- FAIL + 차원 귀속 -------

DIMS = {"operator_type", "operator_nesting", "scope", "binding",
        "predicate_arguments", "structural_validity"}


def _fail_dims(pred, orac):
    out = ev.evaluate(pred, orac)
    assert out["result"] == "fail", out
    assert out["mismatch_dimensions"], "FAIL은 차원 귀속을 보고해야 한다"
    assert set(out["mismatch_dimensions"]) <= DIMS
    return set(out["mismatch_dimensions"])


def test_quantifier_order_swap_is_scope():
    pred = FORALL("x", EXISTS("y", P("R", V("x"), V("y"))))
    orac = EXISTS("y", FORALL("x", P("R", V("x"), V("y"))))
    assert "scope" in _fail_dims(pred, orac) or \
        "operator_type" in _fail_dims(pred, orac)


def test_modal_scope_difference_is_reported():
    pred = BOX(IMPLIES(P("P"), P("Q")))
    orac = IMPLIES(P("P"), BOX(P("Q")))
    dims = _fail_dims(pred, orac)
    assert dims & {"scope", "operator_nesting", "operator_type"}


def test_predicate_name_difference_is_predicate_arguments():
    pred = FORALL("x", P("R", V("x")))
    orac = FORALL("x", P("S", V("x")))
    assert "predicate_arguments" in _fail_dims(pred, orac)


def test_operator_kind_difference_is_operator_type():
    pred = FORALL("x", P("P", V("x")))
    orac = EXISTS("x", P("P", V("x")))
    assert "operator_type" in _fail_dims(pred, orac)


def test_argument_binding_swap_is_binding():
    pred = FORALL("x", EXISTS("y", P("R", V("x"), V("y"))))
    orac = FORALL("x", EXISTS("y", P("R", V("y"), V("x"))))
    dims = _fail_dims(pred, orac)
    assert dims & {"binding", "predicate_arguments"}


def test_malformed_predicted_is_subject_fail_not_error():
    """비정형 predicted = 주체의 실패(FAIL). 평가기 실패(ERROR)가 아니다 —
    schema 강제를 뚫고 나온 비정형 출력도 기록 가능한 관측이어야 한다."""
    out = ev.evaluate({"kind": "pred", "name": "R"}, FORALL("x", P("P", V("x"))))
    assert out["result"] == "fail"
    assert "structural_validity" in out["mismatch_dimensions"]


# --------------------------------------------------------- UNSCORABLE -----

def test_invalid_oracle_is_unscorable_not_fail():
    """oracle측 결함은 주체 실패의 증거가 아니다 — 측정 계약의 실패(판정
    §5: UNSCORABLE ≠ semantic failure)."""
    out = ev.evaluate(FORALL("x", P("P", V("x"))), {"kind": "pred", "name": "R"})
    assert out["result"] == "unscorable"
    assert out["reason"]


def test_reserved_namespace_oracle_is_unscorable():
    out = ev.evaluate(FORALL("x", P("P", V("x"))),
                      P("P", V("?0")))
    assert out["result"] == "unscorable"


# -------------------------------------------------------------- ERROR -----

def test_non_dict_inputs_are_error_not_exception():
    for pred, orac in ((None, P("P")), (P("P"), "oracle"), (3, None)):
        out = ev.evaluate(pred, orac)
        assert out["result"] == "error"
        assert out["reason"]


def test_internal_crash_is_captured_as_error(monkeypatch):
    """평가기 내부 crash는 raise가 아니라 ERROR 기록 — 실행 중 스위트가
    죽으면 나머지 fixture의 관측까지 잃는다."""
    def boom(_):
        raise RuntimeError("synthetic comparator crash")
    monkeypatch.setattr(ev.cg_ir, "canonicalize_v0", boom)
    out = ev.evaluate(FORALL("x", P("P", V("x"))), FORALL("x", P("P", V("x"))))
    assert out["result"] == "error"
    assert "synthetic comparator crash" in out["reason"]


# ------------------------------------------------------------ 격리 --------

def test_evaluate_does_not_import_verify_vocabulary():
    """G32: Evaluate 어휘는 Verify의 Verdict와 통일 금지 — import 자체를
    막아 실수로도 섞이지 않게 한다."""
    tree = ast.parse(Path(inspect.getfile(ev)).read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                for a in n.names}
    imported |= {n.module for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    assert not any("cg_obligations" in (m or "") for m in imported), imported
    assert imported <= {"__future__", "typing", "cg_ir", "cg_identity",
                        "conceptgate.cg_ir", "conceptgate.cg_identity"}, imported


def test_refine_verify_modules_do_not_import_evaluate():
    """INV-ORACLE-01/02의 코드 집행: oracle 인접 계층(Evaluate)이 생성·검증
    경로로 역류하는 import가 없어야 한다."""
    root = Path(inspect.getfile(ev)).parent
    for name in ("server.py", "cg_obligations.py", "cg_normalizer.py",
                 "concept_gate_v7.py", "cg_ir.py", "cg_identity.py"):
        src = (root / name).read_text(encoding="utf-8")
        tree = ast.parse(src)
        imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                    for a in n.names}
        imported |= {n.module for n in ast.walk(tree)
                     if isinstance(n, ast.ImportFrom) and n.module}
        assert not any("cg_evaluate" in (m or "") for m in imported), (
            f"{name} imports cg_evaluate -- evaluation-boundary leak")
