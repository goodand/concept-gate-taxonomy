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


# ---------------------------- GQ restriction 확장 (D-E2E-v1-20 후속) -------
# wikisem 실측: 양화가 2-람다 GQ 형(restriction+scope)이라 Quantifier 노드에
# 선택적 restriction 필드가 필요하다. GQ→FOL 변환은 정리-동치 재작성이라
# 금지 — 구조를 보존한다.

def test_quantifier_restriction_is_alpha_renamed_too():
    f = {"kind": "exists", "var": "x",
         "restriction": P("R", V("x")), "body": P("S", V("x"))}
    g = {"kind": "exists", "var": "y",
         "restriction": P("R", V("y")), "body": P("S", V("y"))}
    assert cg_ir.canonicalize_v0(f) == cg_ir.canonicalize_v0(g)


def test_restriction_and_body_positions_are_distinct():
    """restriction에 있는 것과 body에 있는 것은 다른 공식이다 — 위치가
    의미다. 둘을 스왑한 공식과 canonical이 같으면 안 된다."""
    f = {"kind": "exists", "var": "x",
         "restriction": P("R", V("x")), "body": P("S", V("x"))}
    g = {"kind": "exists", "var": "x",
         "restriction": P("S", V("x")), "body": P("R", V("x"))}
    assert cg_ir.canonicalize_v0(f) != cg_ir.canonicalize_v0(g)


def test_quantifier_without_restriction_stays_valid_and_distinct():
    """restriction 없는 기존 형태는 계속 유효하고, restriction 있는 것과
    구별된다 (기존 테스트 전부와의 하위호환이 이 테스트의 절반)."""
    bare = EXISTS("x", P("S", V("x")))
    assert cg_ir.validate_formula(bare) == []
    withr = {"kind": "exists", "var": "x",
             "restriction": P("R", V("x")), "body": P("S", V("x"))}
    assert cg_ir.validate_formula(withr) == []
    assert cg_ir.canonicalize_v0(bare) != cg_ir.canonicalize_v0(withr)


def test_malformed_restriction_is_refused():
    bad = {"kind": "exists", "var": "x",
           "restriction": {"kind": "pred", "name": "R"},  # args 없음
           "body": P("S", V("x"))}
    assert cg_ir.validate_formula(bad)


def test_free_variables_include_restriction():
    f = {"kind": "exists", "var": "x",
         "restriction": P("R", V("x"), V("free1")), "body": P("S", V("free2"))}
    assert cg_ir.free_variables(f) == {"free1", "free2"}


# ---------------------------------------------------------------- 2026-08-23
# 커널 검증기의 공백. `pred`의 인자는 **항**(var/entity)이어야 하는데
# validate_formula가 인자를 formula로 재귀 검증해서, 인자 자리에 수식이 들어온
# IR을 유효로 판정했다. 실측 경로: Oracle Adapter가 corpus의 "콜론 태그 술어가
# 람다를 인자로 받는" 형태를 번역할 때 pred 인자 자리에 수식을 넣었고,
# 검증기가 통과시켰다. free_variables도 그 노드에서 조용히 공집합을 돌려주므로
# 닫힘 검사로도 잡히지 않는다 — 즉 무효 IR이 cg_evaluate의
# `predicate_arguments` 차원 비교까지 유효한 것처럼 흘러간다.

BAD_PRED_ARGS = (
    {"kind": "and", "args": []},
    {"kind": "or", "args": []},
    {"kind": "not", "body": {"kind": "pred", "name": "q", "args": []}},
    {"kind": "pred", "name": "q", "args": []},
    {"kind": "exists", "var": "x",
     "body": {"kind": "pred", "name": "q", "args": []}},
    {"kind": "forall", "var": "x",
     "body": {"kind": "pred", "name": "q", "args": []}},
    {"kind": "box", "body": {"kind": "pred", "name": "q", "args": []}},
    {"kind": "diamond", "body": {"kind": "pred", "name": "q", "args": []}},
    {"kind": "implies",
     "left": {"kind": "pred", "name": "q", "args": []},
     "right": {"kind": "pred", "name": "r", "args": []}},
)


@pytest.mark.parametrize("bad", BAD_PRED_ARGS, ids=lambda b: b["kind"])
def test_pred_argument_must_be_a_term(bad):
    node = {"kind": "pred", "name": "p", "args": [bad]}
    errors = cg_ir.validate_formula(node)
    assert errors, f"{bad['kind']} accepted in an argument slot"
    assert any(e["code"] == "PRED_ARG_NOT_TERM" for e in errors), errors


def test_pred_accepts_terms_as_arguments():
    node = {"kind": "pred", "name": "p", "args": [
        {"kind": "var", "name": "x"},
        {"kind": "entity", "name": "socrates"},
    ]}
    assert cg_ir.validate_formula(node) == []


def test_pred_argument_check_reaches_nested_predicates():
    """양화 본문 깊숙이 있는 위반도 보고돼야 한다 — 최상위만 보면 실제 번역물이
    통과한다(실측된 형태가 정확히 중첩이었다)."""
    node = {"kind": "exists", "var": "x", "body": {
        "kind": "and", "args": [
            {"kind": "pred", "name": "p", "args": [{"kind": "var", "name": "x"}]},
            {"kind": "pred", "name": "q",
             "args": [{"kind": "and", "args": []}]},
        ]}}
    errors = cg_ir.validate_formula(node)
    assert any(e["code"] == "PRED_ARG_NOT_TERM" for e in errors), errors


def test_bad_pred_arg_selection_is_not_empty():
    assert len(BAD_PRED_ARGS) == 9


# ---- D-E2E-v1-29: count·prop은 커널이 아는 결박자다 --------------------
#
# 왜 커널인가: 이것은 **방언 문법**이고 실험 정책이 아니다. Q22.3 §10이
# 커널 반입을 금지한 것은 라벨 정규화(실험별 평가 정책)였다. 판정 D-29 §1이
# 방언을 8종으로 확정했고 `cg_ir_schema`(같은 커널)가 이미 두 종을 발행하는데
# `validate_formula`/`canonicalize_v0`가 모르면, **subject에게 허용한 것을
# 커널이 채점하지 못한다**(실측: evaluate → UNKNOWN_KIND → unscorable).

_CNT = {"kind": "count", "rel": "ge", "num": 3, "var": "x",
        "restriction": {"kind": "pred", "name": "dog",
                        "args": [{"kind": "var", "name": "x"}]},
        "body": {"kind": "pred", "name": "bark",
                 "args": [{"kind": "var", "name": "x"}]}}
_PROP = {"kind": "prop", "rel": "most", "var": "x",
         "restriction": {"kind": "pred", "name": "cat",
                         "args": [{"kind": "var", "name": "x"}]},
         "body": {"kind": "pred", "name": "sleep",
                  "args": [{"kind": "var", "name": "x"}]}}


def test_count_and_prop_are_known_kinds():
    assert cg_ir.validate_formula(_CNT) == []
    assert cg_ir.validate_formula(_PROP) == []


def test_count_binds_its_variable():
    """결박자다 — restriction·body 양쪽에서 var를 결박한다(forall/exists와 동형)."""
    assert cg_ir.free_variables(_CNT) == set()
    assert cg_ir.free_variables(_PROP) == set()


def test_count_free_variable_outside_the_binder_is_reported():
    f = dict(_CNT, body={"kind": "pred", "name": "chew",
                         "args": [{"kind": "var", "name": "x"},
                                  {"kind": "var", "name": "y"}]})
    assert cg_ir.free_variables(f) == {"y"}


def test_count_variable_is_alpha_renamed():
    a = _CNT
    b = dict(_CNT, var="z",
             restriction={"kind": "pred", "name": "dog",
                          "args": [{"kind": "var", "name": "z"}]},
             body={"kind": "pred", "name": "bark",
                   "args": [{"kind": "var", "name": "z"}]})
    assert cg_ir.canonicalize_v0(a) == cg_ir.canonicalize_v0(b)
    assert cg_ir.formula_fingerprint(a) == cg_ir.formula_fingerprint(b)


def test_canonicalize_preserves_rel_and_num():
    """정규화가 기수 값을 지우거나 뭉개면 3≠4 신호가 사라진다."""
    out = cg_ir.canonicalize_v0(_CNT)
    assert out["rel"] == "ge" and out["num"] == 3
    assert cg_ir.canonicalize_v0(_PROP)["rel"] == "most"


def test_cardinal_value_is_not_canonicalized_away():
    assert (cg_ir.formula_fingerprint(_CNT)
            != cg_ir.formula_fingerprint(dict(_CNT, num=4)))
    assert (cg_ir.formula_fingerprint(_CNT)
            != cg_ir.formula_fingerprint(dict(_CNT, rel="gt")))


def test_count_and_prop_are_not_interchangeable():
    assert (cg_ir.formula_fingerprint(_CNT)
            != cg_ir.formula_fingerprint(dict(_PROP, restriction=_CNT["restriction"],
                                              body=_CNT["body"])))


def test_count_requires_its_own_fields():
    for missing in ("rel", "num", "var", "restriction", "body"):
        bad = {k: v for k, v in _CNT.items() if k != missing}
        assert cg_ir.validate_formula(bad), f"{missing} 누락이 통과됐다"


def test_count_rejects_non_integer_num():
    assert cg_ir.validate_formula(dict(_CNT, num="3"))


def test_count_rejects_unknown_relation():
    assert cg_ir.validate_formula(dict(_CNT, rel="approx"))


def test_prop_v1_admits_only_most():
    """비례는 어떤 고정 기수 임계값도 아니다(D-29 §5 — 우리 실측으로 재확인)."""
    assert cg_ir.validate_formula(dict(_PROP, rel="half"))
    assert "num" not in _PROP


def test_count_malformed_subformula_is_refused():
    assert cg_ir.validate_formula(dict(_CNT, restriction={"kind": "nope"}))
