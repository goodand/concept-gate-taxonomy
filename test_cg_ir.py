"""cg_ir의 TDD 계약 — 지시 §11~13의 최소 semantic IR (RED 먼저 작성).

이 테스트가 계약의 정본이다. 구현이 어디서 오든(subtree든 신규든) 이
계약을 통과해야 하고, 특히 **금지 재작성**(quantifier 재배열·교환법칙
재배열·정리 동치)이 정규화에 스며들면 즉시 실패해야 한다 — oracle 비교의
전제(manifest canonicalization_profile)가 그것이기 때문.

표기: formula는 JSON 직렬화 가능한 dict.
  {"kind":"entity","name":..} {"kind":"var","name":..}
  {"kind":"pred","name":..,"args":[Term..]}
  {"kind":"forall"|"exists","var":..,"body":F}
  {"kind":"box"|"diamond","body":F}
  {"kind":"and"|"or","args":[F..]} {"kind":"implies","left":F,"right":F}
  {"kind":"not","body":F}
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from conceptgate import cg_ir


def V(n): return {"kind": "var", "name": n}
def E(n): return {"kind": "entity", "name": n}
def P(name, *args): return {"kind": "pred", "name": name, "args": list(args)}
def FORALL(v, body): return {"kind": "forall", "var": v, "body": body}
def EXISTS(v, body): return {"kind": "exists", "var": v, "body": body}
def BOX(body): return {"kind": "box", "body": body}
def IMPLIES(l, r): return {"kind": "implies", "left": l, "right": r}
def AND(*args): return {"kind": "and", "args": list(args)}


# ---------------------------------------------------------- α-동치 --------

def test_alpha_equivalent_formulas_share_canonical_form():
    """∀x∃y R(x,y) ≡α ∀a∃b R(a,b) — 이것이 정규화가 존재하는 이유."""
    f1 = FORALL("x", EXISTS("y", P("R", V("x"), V("y"))))
    f2 = FORALL("a", EXISTS("b", P("R", V("a"), V("b"))))
    assert cg_ir.canonicalize_v0(f1) == cg_ir.canonicalize_v0(f2)
    assert cg_ir.formula_fingerprint(f1) == cg_ir.formula_fingerprint(f2)


def test_shadowing_is_renamed_correctly():
    """∀x(P(x) ∧ ∀x Q(x)) — 안쪽 x는 다른 binder다. 순진한 일괄 치환은
    두 x를 같은 이름으로 뭉갠다."""
    f = FORALL("x", AND(P("P", V("x")), FORALL("x", P("Q", V("x")))))
    g = FORALL("a", AND(P("P", V("a")), FORALL("b", P("Q", V("b")))))
    assert cg_ir.canonicalize_v0(f) == cg_ir.canonicalize_v0(g)


def test_inner_binding_does_not_leak_to_later_siblings():
    """scope 격리: 안쪽 binder의 바인딩이 그 뒤 형제 가지로 새면 안 된다.

    ∀x( (∀x Q(x)) ∧ P(x) ) — 뒤쪽 P(x)의 x는 **바깥** binder다. 환경을
    사본 없이 전달하면 안쪽 재바인딩이 남아 뒤쪽 x가 안쪽 이름을 받는다.
    이 테스트는 뮤테이션(rename_map.copy() 제거)이 기존 스위트를 전부
    통과한 실측 공백에서 추가됐다 — 기존 shadowing 테스트는 바깥 참조가
    안쪽 binder보다 앞에만 있었다."""
    f = FORALL("x", AND(FORALL("x", P("Q", V("x"))), P("P", V("x"))))
    g = FORALL("a", AND(FORALL("b", P("Q", V("b"))), P("P", V("a"))))
    assert cg_ir.canonicalize_v0(f) == cg_ir.canonicalize_v0(g)


def test_free_variables_are_not_captured():
    """capture 회피: 자유변수가 canonical bound 이름과 충돌해도 포획되지
    않아야 한다. 예약 네임스페이스 침범은 거부가 정답."""
    # 자유변수 이름이 canonical 예약 형태('?0')인 경우 — 거부
    f = EXISTS("y", P("P", V("y"), V("?0")))
    with pytest.raises(ValueError, match="reserved"):
        cg_ir.canonicalize_v0(f)


def test_canonicalization_is_idempotent():
    f = FORALL("x", EXISTS("y", P("R", V("x"), V("y"))))
    once = cg_ir.canonicalize_v0(f)
    assert cg_ir.canonicalize_v0(once) == once


# ------------------------------------------- 구별해야 하는 것 (topology) ----

def test_quantifier_order_is_not_equivalent():
    """∀x∃y R(x,y) ≠ ∃y∀x R(x,y) — 재배열은 정규화가 아니라 의미 변경(§8)."""
    f1 = FORALL("x", EXISTS("y", P("R", V("x"), V("y"))))
    f2 = EXISTS("y", FORALL("x", P("R", V("x"), V("y"))))
    assert cg_ir.canonicalize_v0(f1) != cg_ir.canonicalize_v0(f2)


def test_modal_scope_is_distinguished():
    """□(P→Q) ≠ P→□Q — LogicalOperator가 존재하는 이유(§12)."""
    p, q = P("P"), P("Q")
    f1 = BOX(IMPLIES(p, q))
    f2 = IMPLIES(p, BOX(q))
    assert cg_ir.formula_fingerprint(f1) != cg_ir.formula_fingerprint(f2)


def test_de_re_de_dicto_derive_from_topology_not_labels():
    """∃x□P(x) ≠ □∃xP(x) — label 없이 nesting만으로 구별(§13)."""
    f_de_re = EXISTS("x", BOX(P("P", V("x"))))
    f_de_dicto = BOX(EXISTS("x", P("P", V("x"))))
    assert cg_ir.canonicalize_v0(f_de_re) != cg_ir.canonicalize_v0(f_de_dicto)


def test_commutativity_is_not_rewritten():
    """and(P,Q) ≠canon and(Q,P) — 교환법칙 재배열은 v0 금지 목록(§8).
    인자 순서는 의미 보존 대상이지 정규화 대상이 아니다."""
    f1 = AND(P("P"), P("Q"))
    f2 = AND(P("Q"), P("P"))
    assert cg_ir.canonicalize_v0(f1) != cg_ir.canonicalize_v0(f2)


# ------------------------------------------------------------ 검증 --------

def test_unknown_kind_is_refused():
    errs = cg_ir.validate_formula({"kind": "iff", "args": []})
    assert errs and any("kind" in e["code"].lower() or "KIND" in e["code"]
                        for e in errs)


def test_malformed_nodes_are_refused():
    assert cg_ir.validate_formula({"kind": "forall", "var": 3, "body": P("P")})
    assert cg_ir.validate_formula({"kind": "pred", "name": "R"})  # args 없음
    assert cg_ir.validate_formula({"kind": "implies", "left": P("P")})  # right 없음


def test_valid_formula_has_no_errors_and_free_vars_are_listed():
    f = FORALL("x", P("R", V("x"), V("z")))
    assert cg_ir.validate_formula(f) == []
    assert cg_ir.free_variables(f) == {"z"}


def test_fingerprint_kind_is_formula_and_domain_separated():
    """'formula' kind가 의도적으로 등록되고, 같은 dict라도 claim
    fingerprint와 다르다(도메인 분리 유지)."""
    from conceptgate import cg_identity as ci
    f = P("P")
    fp = cg_ir.formula_fingerprint(f)
    assert fp.startswith("formula:")
    assert fp != ci.claim_fingerprint(f)


# -------------------------------------------------- §29 negative ----------

FORBIDDEN = ("simplify", "equival", "entail", "prove", "infer", "rewrite",
             "judge", "certif", "select", "score", "oracle", "verdict")


def test_ir_module_defines_no_inference_machinery():
    """커널 부정 계약: IR 모듈에 simplification/동치/증명 기능이 존재하는 것
    자체가 금지다 — 안 쓰는 것으로 충분하지 않다(오용·드리프트 표면)."""
    tree = ast.parse(Path(inspect.getfile(cg_ir)).read_text(encoding="utf-8"))
    offenders = [n.name for n in ast.walk(tree)
                 if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                 and any(p in n.name.lower() for p in FORBIDDEN)]
    assert not offenders, offenders


def test_ir_module_imports_stay_in_kernel():
    tree = ast.parse(Path(inspect.getfile(cg_ir)).read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                for a in n.names}
    imported |= {n.module for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= {"__future__", "cg_identity", "conceptgate.cg_identity",
                        "typing"}, imported
