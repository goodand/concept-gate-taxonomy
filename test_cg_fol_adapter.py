"""FOL adapter (FOLIO_FOL_V0)의 TDD 계약 — RED 먼저.

D-E2E-v1-23 §12가 정본: 지원 {∀,∃,∧,¬,→,술어적용,True} / 금지 {∨,=,⊕,↔,
미지연산자}. 핵심 비대칭(§최종): **∀ 직하의 →만 restricted forall로
definitional lowering; ∃는 neutral(restriction=True) — 분할을 발명하지
않는다.** prefix 양화 순서는 강한 불변식(반례 2/16 재계산 일치), 양화를
가로지르는 → 이동은 금지(의존 antecedent 반례 56/256 재계산 일치).
판정 §14의 뮤테이션 A·B·C가 이 계약의 음성 테스트로 직접 들어간다.
모든 식은 발명 술어(Zorble/Glim/Prax/Tikk) — corpus 0바이트.
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from conceptgate import cg_ir
from conceptgate import cg_fol_adapter as fa


def fp(ir):
    return cg_ir.formula_fingerprint(ir)


V = lambda n: {"kind": "var", "name": n}
E = lambda n: {"kind": "entity", "name": n}
P = lambda name, *args: {"kind": "pred", "name": name, "args": list(args)}
T = P("True")


def FA(v, r, b): return {"kind": "forall", "var": v, "restriction": r, "body": b}
def EX(v, b):    return {"kind": "exists", "var": v, "restriction": T, "body": b}
def AND(*a):     return {"kind": "and", "args": list(a)}
def IMP(l, r):   return {"kind": "implies", "left": l, "right": r}
def NOT(b):      return {"kind": "not", "body": b}


# ------------------------------------------------- definitional lowering ---

def test_forall_immediate_implication_lowers_to_restriction():
    ir = fa.adapt_fol("∀x (Zorble(x) → Glim(x))")
    assert fp(ir) == fp(FA("x", P("Zorble", V("x")), P("Glim", V("x"))))


def test_forall_without_implication_is_neutral():
    ir = fa.adapt_fol("∀x Zorble(x)")
    assert fp(ir) == fp(FA("x", T, P("Zorble", V("x"))))


def test_existential_is_always_neutral_never_split():
    """판정 §14 Mutation B: ∃y(A∧B∧C)를 임의 분할하면 FAIL —
    restriction=True, body=전체 conjunction이어야 한다."""
    ir = fa.adapt_fol("∃y (Zorble(y) ∧ Glim(y) ∧ Prax(y))")
    assert fp(ir) == fp(EX("y", AND(P("Zorble", V("y")), P("Glim", V("y")),
                                    P("Prax", V("y")))))
    assert ir["restriction"] == T


def test_prefix_chain_preserved_in_order():
    """판정 §14 Mutation A: ∀x∃y ≠ ∃y∀x — canonical hash가 달라야 한다."""
    fe = fa.adapt_fol("∀x ∃y Prax(x, y)")
    ef = fa.adapt_fol("∃y ∀x Prax(x, y)")
    assert fp(fe) != fp(ef)
    assert fe["kind"] == "forall" and fe["body"]["kind"] == "exists"
    assert ef["kind"] == "exists" and ef["body"]["kind"] == "forall"


def test_no_unsafe_implication_crossing():
    """판정 §8-§9·§14 Mutation C: ∀x∃y(P(x)→Q(x,y))는 그대로 보존 —
    exists 안의 implies로 남고, forall의 restriction으로 이동 금지."""
    ir = fa.adapt_fol("∀x ∃y (Zorble(x) → Prax(x, y))")
    expected = FA("x", T, EX("y", IMP(P("Zorble", V("x")),
                                      P("Prax", V("x"), V("y")))))
    assert fp(ir) == fp(expected)
    assert ir["restriction"] == T, "P(x)가 restriction으로 이동했다면 금지 위반"


def test_ruling_example_shape_universal_language():
    """판정 실물 형태의 발명판: ∀x ∀y (∃z (K(x,z) ∧ K(y,z)) → C(x,y))."""
    ir = fa.adapt_fol("∀x ∀y (∃z (Tikk(x, z) ∧ Tikk(y, z)) → Prax(x, y))")
    inner = IMP(EX("z", AND(P("Tikk", V("x"), V("z")),
                            P("Tikk", V("y"), V("z")))),
                P("Prax", V("x"), V("y")))
    # ∀y 직하가 →이므로 lowering: restriction=∃z(...), body=Prax
    lowered = FA("x", T, FA("y", EX("z", AND(P("Tikk", V("x"), V("z")),
                                             P("Tikk", V("y"), V("z")))),
                            P("Prax", V("x"), V("y"))))
    assert fp(ir) == fp(lowered)


# ------------------------------------------------------------- 항 규칙 -----

def test_bound_identifiers_are_vars_unbound_are_entities():
    ir = fa.adapt_fol("∀x Prax(x, berlinzorb)")
    assert fp(ir) == fp(FA("x", T, P("Prax", V("x"), E("berlinzorb"))))
    assert cg_ir.free_variables(ir) == set()


def test_negation_and_nary_conjunction():
    ir = fa.adapt_fol("∀x (Zorble(x) → ¬(Glim(x) ∧ Prax(x)))")
    assert fp(ir) == fp(FA("x", P("Zorble", V("x")),
                           NOT(AND(P("Glim", V("x")), P("Prax", V("x"))))))


def test_predicate_names_preserved_raw():
    ir = fa.adapt_fol("∃y ZorbleKrell(y)")
    assert ir["body"]["name"] == "ZorbleKrell"


# ------------------------------------------------------------ fail-closed --

@pytest.mark.parametrize("bad", [
    "∀x (Zorble(x) ∨ Glim(x))",
    "∃y (Zorble(y) ∧ y = berlinzorb)",
    "∀x (Zorble(x) ⊕ Glim(x))",
    "∀x (Zorble(x) ↔ Glim(x))",
])
def test_unsupported_operators_fail_closed(bad):
    with pytest.raises(fa.AdapterUnsupported):
        fa.adapt_fol(bad)


def test_malformed_inputs_refused():
    for bad in ("", "∀x (Zorble(x)", "Zorble x", "∀ (Zorble(x))"):
        with pytest.raises((fa.AdapterSyntaxError, fa.AdapterUnsupported)):
            fa.adapt_fol(bad)


# ------------------------------------------------------------- 자격 축 -----

def test_deterministic_replay_and_validity():
    s = "∀x ∃y (Zorble(x) → Prax(x, y))"
    a, b = fa.adapt_fol(s), fa.adapt_fol(s)
    assert a == b
    assert cg_ir.validate_formula(a) == []
    assert cg_ir.free_variables(a) == set()


def test_alpha_invariance_across_variable_letters():
    a = fa.adapt_fol("∀x (Zorble(x) → Glim(x))")
    b = fa.adapt_fol("∀u (Zorble(u) → Glim(u))")
    assert fp(a) == fp(b)


# --------------------------------------------- 격리·순수성 (AST 집행) -------

def test_fol_adapter_is_pure_and_leaf():
    src = Path(inspect.getfile(fa)).read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls = {n.func.id for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "open" not in calls
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                for a in n.names}
    imported |= {n.module for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= {"__future__", "typing", "re",
                        "cg_ir", "conceptgate.cg_ir"}, imported


def test_fol_adapter_not_imported_by_refine_or_verify():
    root = Path(inspect.getfile(fa)).parent
    for name in ("server.py", "cg_obligations.py", "cg_normalizer.py",
                 "concept_gate_v7.py", "cg_ir.py", "cg_identity.py",
                 "cg_evaluate.py", "cg_oracle_adapter.py",
                 "cg_sbn_adapter.py", "cg_fixture_resolver.py"):
        src = (root / name).read_text(encoding="utf-8")
        assert "cg_fol_adapter" not in src, f"{name} imports the fol adapter"
