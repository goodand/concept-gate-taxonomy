"""canonical comparison desugar의 TDD 계약 — RED 먼저 (D-23 §5·§9·§12).

비교 전 양측을 neutral core로 낮춘다(정의적 desugar — 정리 동치 아님):
  FORALL(x,R,B), R≠True → FORALL(x,True,IMPLIES(R,B))
  EXISTS(x,R,B), R≠True → EXISTS(x,True,AND(R,B))
subject의 restricted 출력과 oracle의 neutral 출력이 같은 core로 수렴한다
(§5의 BEFORE/AFTER). **양화 순서는 절대 건드리지 않는다**(§7 — 반례 2/16
재계산 일치). estimand 불변(§10): subject 방언은 그대로다.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

import _stage2_canonical_core as core  # noqa: E402
from conceptgate import cg_ir  # noqa: E402

V = lambda n: {"kind": "var", "name": n}
P = lambda name, *args: {"kind": "pred", "name": name, "args": list(args)}
T = P("True")
fp = cg_ir.formula_fingerprint


def test_restricted_forall_lowers_to_implies():
    ir = {"kind": "forall", "var": "x", "restriction": P("Zorble", V("x")),
          "body": P("Glim", V("x"))}
    out = core.desugar(ir)
    assert out == {"kind": "forall", "var": "x", "restriction": T,
                   "body": {"kind": "implies", "left": P("Zorble", V("x")),
                            "right": P("Glim", V("x"))}}


def test_restricted_exists_lowers_to_and():
    ir = {"kind": "exists", "var": "y", "restriction": P("Zorble", V("y")),
          "body": P("Prax", V("y"))}
    out = core.desugar(ir)
    assert out["restriction"] == T
    assert out["body"] == {"kind": "and",
                           "args": [P("Zorble", V("y")), P("Prax", V("y"))]}


def test_ruling_before_after_example_converges():
    """§5: subject의 restricted ∃ vs oracle의 neutral ∃ — desugar 후 동일."""
    subject = {"kind": "exists", "var": "y",
               "restriction": P("Zorble", V("y")),
               "body": P("Prax", V("x"), V("y"))}
    oracle = {"kind": "exists", "var": "y", "restriction": T,
              "body": {"kind": "and", "args": [
                  P("Zorble", V("y")), P("Prax", V("x"), V("y"))]}}
    assert fp(core.desugar(subject)) == fp(core.desugar(oracle))


def test_neutral_inputs_are_fixed_points():
    ir = {"kind": "exists", "var": "y", "restriction": T,
          "body": P("Zorble", V("y"))}
    assert core.desugar(ir) == ir
    assert core.desugar(core.desugar(ir)) == core.desugar(ir)  # 멱등


def test_recursive_and_order_preserving():
    """중첩 내부까지 내려가되 양화 순서는 절대 불변(§7)."""
    ir = {"kind": "forall", "var": "x", "restriction": P("Zorble", V("x")),
          "body": {"kind": "exists", "var": "y",
                   "restriction": P("Tikk", V("y")),
                   "body": P("Prax", V("x"), V("y"))}}
    out = core.desugar(ir)
    assert out["kind"] == "forall" and out["body"]["kind"] == "implies"
    inner = out["body"]["right"]
    assert inner["kind"] == "exists" and inner["body"]["kind"] == "and"
    # 순서 뒤집힘 없음: forall이 여전히 바깥
    swapped = {"kind": "exists", "var": "y", "restriction": P("Tikk", V("y")),
               "body": {"kind": "forall", "var": "x",
                        "restriction": P("Zorble", V("x")),
                        "body": P("Prax", V("x"), V("y"))}}
    assert fp(core.desugar(ir)) != fp(core.desugar(swapped))


def test_input_not_mutated():
    import copy
    ir = {"kind": "forall", "var": "x", "restriction": P("Zorble", V("x")),
          "body": P("Glim", V("x"))}
    before = copy.deepcopy(ir)
    core.desugar(ir)
    assert ir == before


def test_pure_module():
    import ast, inspect
    tree = ast.parse(Path(inspect.getfile(core)).read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                for a in n.names}
    imported |= {n.module for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= {"__future__", "typing", "copy"}, imported


def test_non_dict_input_refused():
    """적대검증: desugar가 비-dict를 조용히 반환하던 타입 구멍 — 거부로."""
    for bad in ("```json", 42, None, ["x"]):
        with pytest.raises(TypeError):
            core.desugar(bad)
