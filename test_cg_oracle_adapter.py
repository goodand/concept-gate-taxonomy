"""Oracle Adapter의 TDD 계약 (D-E2E-v1-20 b+) — RED 먼저.

typed-lambda LF(wikisem 문법) → cg_ir dict. 일반 syntax-directed —
fixture별 lookup 금지(ORACLE-12). **이 테스트의 모든 LF는 corpus 문장이
아니라 같은 문법으로 창작한 것이다**(창작 술어: zorble/glim/prax) —
테스트에 corpus 콘텐츠를 넣는 것 자체가 ORACLE-12 위반이므로.

실측된 wikisem 문법 (C6 파일 직접 분석, 2026-08-22):
  - 레코드: "N LOGIC: (<expr>)"  (이 계약은 <expr> 파싱만 다룸)
  - GQ 2-람다: Some (\\x1 RESTR) (\\x1 SCOPE), All 동형
  - 접속: (^ A B ...) n-ary
  - 원자 적용: (Head arg1 arg2 ...) — Head는 `-`,`{`,`}`,`:` 포함 가능
  - 자명 restriction 관용구: (\\z True)
  - binder: \\x1 \\e1 등 (문자+숫자, 숫자 없는 \\x도 존재)
  - 미지원(v0): Equal, Intension, None, Gen, NNORD* → fail-closed
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from conceptgate import cg_ir
from conceptgate import cg_oracle_adapter as oa


def canon_hash(lf: str) -> str:
    return cg_ir.formula_fingerprint(oa.adapt(lf))


# ------------------------------------------------------------ 구조 매핑 ----

def test_atom_application_maps_to_pred():
    out = oa.adapt("(N-aD:zorble e1 x1)")
    assert out == {"kind": "pred", "name": "N-aD:zorble",
                   "args": [{"kind": "var", "name": "e1"},
                            {"kind": "var", "name": "x1"}]}


def test_category_tags_with_braces_survive_tokenization():
    out = oa.adapt("(B-aN-b{A-aN}:be x1)")
    assert out["kind"] == "pred" and out["name"] == "B-aN-b{A-aN}:be"


def test_generalized_quantifier_two_lambda_form():
    """Some (\\x R) (\\x S) → exists x with restriction+body. GQ→FOL 변환
    (∃x(R∧S))은 정리-동치 재작성이라 하지 않는다 — 구조 보존."""
    out = oa.adapt("(Some (\\x1 (N-aD:zorble e1 x1)) (\\x1 (A-aN:glim x1)))")
    assert out["kind"] == "exists" and out["var"] == "x1"
    assert out["restriction"]["name"] == "N-aD:zorble"
    assert out["body"]["name"] == "A-aN:glim"


def test_trivial_restriction_idiom_is_true_pred():
    out = oa.adapt("(Some (\\z True) (\\z (A-aN:glim z)))")
    assert out["restriction"] == {"kind": "pred", "name": "True", "args": []}


def test_all_maps_to_forall_and_caret_to_and():
    out = oa.adapt(
        "(All (\\x1 (N-aD:zorble e1 x1)) "
        "(\\x1 (^ (A-aN:glim x1) (A-aN:prax x1))))")
    assert out["kind"] == "forall"
    assert out["body"]["kind"] == "and" and len(out["body"]["args"]) == 2


def test_caret_is_nary():
    out = oa.adapt("(^ (A-aN:glim x1) (A-aN:prax x1) (N-aD:zorble e1 x1))")
    assert out["kind"] == "and" and len(out["args"]) == 3


# ---------------------------------------------- 자격 (판정 b+ 5항목 중 4) ----

def test_alpha_rename_invariance():
    """LF 문자열 수준의 변수 개명이 canonical hash를 바꾸지 않는다."""
    a = "(Some (\\x1 (N-aD:zorble e1 x1)) (\\x1 (A-aN:glim x1)))"
    b = "(Some (\\x9 (N-aD:zorble e1 x9)) (\\x9 (A-aN:glim x9)))"
    assert canon_hash(a) == canon_hash(b)


def test_quantifier_reordering_negative():
    """BLOCKER 조건: ∀∃ 중첩과 ∃∀ 중첩이 같은 hash면 안 된다."""
    fe = ("(All (\\x1 (N-aD:zorble e1 x1)) (\\x1 "
          "(Some (\\y1 (N-aD:prax e2 y1)) (\\y1 (A-aN:glim x1 y1)))))")
    ef = ("(Some (\\y1 (N-aD:prax e2 y1)) (\\y1 "
          "(All (\\x1 (N-aD:zorble e1 x1)) (\\x1 (A-aN:glim x1 y1)))))")
    assert canon_hash(fe) != canon_hash(ef)


def test_binding_preservation_across_shadowing():
    """안쪽 binder가 같은 이름을 재바인딩해도 참조가 올바른 binder로 간다."""
    a = ("(Some (\\x1 (N-aD:zorble e1 x1)) (\\x1 "
         "(Some (\\x1 (N-aD:prax e2 x1)) (\\x1 (A-aN:glim x1)))))")
    b = ("(Some (\\u (N-aD:zorble e1 u)) (\\u "
         "(Some (\\w (N-aD:prax e2 w)) (\\w (A-aN:glim w)))))")
    assert canon_hash(a) == canon_hash(b)


def test_lambda_body_inline_application_is_corpus_form():
    r"""corpus 실측 형태: 람다 본문이 괄호 없이 인라인 — (\x1 Head args…).
    중첩형 (\x1 (Head args…))과 같은 canonical로 수렴해야 한다."""
    inline = r"(Some (\x1 N-aD:zorble e1 x1) (\x1 A-aN:glim x1))"
    nested = r"(Some (\x1 (N-aD:zorble e1 x1)) (\x1 (A-aN:glim x1)))"
    assert canon_hash(inline) == canon_hash(nested)


def test_lambda_body_inline_quantifier():
    r"""(\x1 Some (…) (…)) — 람다 본문이 인라인 GQ인 corpus 형태."""
    lf = (r"(Some (\x1 N-aD:zorble e1 x1) "
          r"(\x1 Some (\y1 N-aD:prax e2 y1) (\y1 A-aN:glim x1 y1)))")
    out = oa.adapt(lf)
    assert out["kind"] == "exists" and out["body"]["kind"] == "exists"


def test_deterministic_replay():
    lf = "(Some (\\x1 (N-aD:zorble e1 x1)) (\\x1 (A-aN:glim x1)))"
    assert oa.adapt(lf) == oa.adapt(lf)


# ------------------------------------------------------------ fail-closed --

@pytest.mark.parametrize("lf", [
    "(Equal a1 (\\v1 (N-aD:zorble e1 v1)))",
    "(Intension (\\w (A-aN:glim w)))",
    "(None (\\x1 (N-aD:zorble e1 x1)) (\\x1 (A-aN:glim x1)))",
])
def test_unsupported_constructs_fail_closed(lf):
    """v0 미지원 구성자는 조용한 오역이 아니라 명시 거부 — 오역된 expected
    IR이 hash로 commit되는 것이 최악의 실패(ORACLE-11)."""
    with pytest.raises(oa.AdapterUnsupported):
        oa.adapt(lf)


def test_malformed_input_is_refused():
    for bad in ("(Some (\\x1", "", "not-an-sexpr)", "(All (\\x1 R))"):
        with pytest.raises((oa.AdapterUnsupported, oa.AdapterSyntaxError)):
            oa.adapt(bad)


def test_adapter_output_validates_under_cg_ir():
    out = oa.adapt("(Some (\\x1 (N-aD:zorble e1 x1)) (\\x1 (A-aN:glim x1)))")
    assert cg_ir.validate_formula(out) == []


# --------------------------------------------- ORACLE-10/12 (AST 집행) -----

def test_adapter_is_pure_and_embeds_no_answer_table():
    """ORACLE-12: fixture별 lookup·corpus 내장 금지. 집행: 파일 IO 금지
    (open/json.load 부재 — adapter는 순수 str→dict), fixture/case/answer류
    이름의 모듈 상수 금지."""
    src = Path(inspect.getfile(oa)).read_text(encoding="utf-8")
    tree = ast.parse(src)
    calls = {n.func.id for n in ast.walk(tree)
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "open" not in calls
    names = {t.id.lower() for n in ast.walk(tree) if isinstance(n, ast.Assign)
             for t in n.targets if isinstance(t, ast.Name)}
    assert not any(any(k in nm for k in ("fixture", "case_id", "answer",
                                         "expected_table", "lookup"))
                   for nm in names), names


def test_adapter_is_not_imported_by_refine_or_verify(  ):
    """ORACLE-10: adapter가 Refine/Verify로 역류 금지."""
    root = Path(inspect.getfile(oa)).parent
    for name in ("server.py", "cg_obligations.py", "cg_normalizer.py",
                 "concept_gate_v7.py", "cg_ir.py", "cg_identity.py",
                 "cg_evaluate.py"):
        src = (root / name).read_text(encoding="utf-8")
        assert "cg_oracle_adapter" not in src, f"{name} imports the adapter"


def test_adapter_imports_stay_in_kernel():
    tree = ast.parse(Path(inspect.getfile(oa)).read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                for a in n.names}
    imported |= {n.module for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= {"__future__", "typing", "re",
                        "cg_ir", "conceptgate.cg_ir"}, imported
