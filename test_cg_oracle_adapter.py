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


# ============================================================== ROUND 2 ====
# 2026-08-23. 실 corpus(C6) 전수 실측이 위 계약의 공백 3개를 드러냈다.
# 위 계약의 LF는 전부 **restriction과 scope가 같은 이름을 결박**했고, 미지원
# 검사도 최상위 경로에서만 시험됐다. 실제 corpus는 두 조건 모두 위반한다.
#
# 실측(2026-08-23, C6 131 레코드):
#   - 파싱 성공 22건 **전부** 자유변수 12~51개 보유 → 닫힌 문장의 번역이
#     열린 식. 즉 22건은 "v0 부분집합 안"이 아니라 **조용한 오역**이었다.
#   - 미지원 연산자(Equal/Intension/None)가 인라인 람다 본문 경로로 통과.
#   - 콜론 태그 술어가 람다를 인자로 받는 형태가 pred 인자 자리에 수식을
#     넣어 cg_ir 스키마 무효 IR을 생산.
# 세 결함 모두 D-E2E-v1-20 ORACLE-11(commitment ≠ correctness)이 지목한 바로
# 그 실패 — 커밋 전에 잡혔다.


def test_quantifier_binds_the_scope_lambda_that_uses_a_different_name():
    """corpus의 GQ는 restriction과 scope가 서로 다른 이름을 결박한다.

    `Some (\\u R[u]) (\\w S[w])`는 두 람다를 **같은 인자에** 적용한 것이므로
    결박 변수는 하나다. 이름이 다르다는 이유로 한쪽을 자유변수로 남기면
    닫힌 문장의 번역이 열린 식이 된다.
    """
    ir = oa.adapt(r"(Some (\x1 N-aD:zorble x1) (\z A-aN:glim z))")
    assert cg_ir.free_variables(ir) == set(), ir
    assert ir["kind"] == "exists"
    var = ir["var"]
    assert ir["restriction"]["args"][0] == {"kind": "var", "name": var}
    assert ir["body"]["args"][0] == {"kind": "var", "name": var}


def test_universal_quantifier_unifies_binders_too():
    ir = oa.adapt(r"(All (\x1 N-aD:zorble x1) (\y1 A-aN:glim y1))")
    assert ir["kind"] == "forall"
    assert cg_ir.free_variables(ir) == set(), ir
    assert ir["restriction"]["args"][0] == ir["body"]["args"][0]


def test_binder_unification_does_not_capture():
    """scope 본문에 restriction 쪽 이름과 같은 내부 결박이 있으면, 소박한
    치환은 그 내부 결박이 외부 변수를 포획한다."""
    ir = oa.adapt(r"(Some (\x1 N-aD:zorble x1) "
                  r"(\z Some (\x1 N-aD:prax x1) (\x1 A-aN:glim z)))")
    assert cg_ir.free_variables(ir) == set(), ir
    outer, inner = ir["var"], ir["body"]["var"]
    assert outer != inner, (outer, inner)
    # z는 외곽 양화의 변수였다 — 내부 결박에 잡히지 않고 그대로 보여야 한다.
    assert ir["body"]["body"]["args"][0] == {"kind": "var", "name": outer}


def test_same_binder_name_still_works():
    """ROUND 1 형태의 회귀 — 이름이 같으면 그대로 하나로 남는다."""
    ir = oa.adapt(r"(Some (\x1 N-aD:zorble x1) (\x1 A-aN:glim x1))")
    assert ir["var"] == "x1"
    assert cg_ir.free_variables(ir) == set()


def test_trivial_scope_idiom_still_works():
    ir = oa.adapt(r"(Some (\x1 N-aD:zorble x1) (\z True))")
    assert ir["body"] == {"kind": "pred", "name": "True", "args": []}
    assert cg_ir.free_variables(ir) == set()


@pytest.mark.parametrize("head", ["Equal", "Intension", "None", "Gen",
                                  "NNORD", "InAntecedentSet"])
def test_unsupported_head_fails_closed_inside_a_lambda_body(head):
    """실패차단이 최상위 경로에만 있어 인라인 람다 본문 경로로 새어나갔다.

    새어나간 결과는 예외가 아니라 `pred(name="Equal", …)` — 미지원 연산자가
    이름만 남긴 평범한 술어로 조용히 번역된다.
    """
    lf = rf"(Some (\a1 {head} a1 (\v1 N-aD:zorble v1)) (\a1 A-aN:glim a1))"
    with pytest.raises(oa.AdapterUnsupported):
        oa.adapt(lf)


def test_unknown_head_fails_closed_rather_than_becoming_a_predicate():
    """blacklist는 아직 보지 못한 구성자를 통과시킨다 — 이 corpus에서 우리가
    본 것은 7 tranche 중 1개의 일부다. 술어는 corpus의 category-tagged
    형태(콜론 포함)만 허용하고 나머지 head는 전부 닫는다."""
    with pytest.raises(oa.AdapterUnsupported):
        oa.adapt(r"(Frobnicate x1)")
    with pytest.raises(oa.AdapterUnsupported):
        oa.adapt(r"(Some (\a1 Frobnicate a1) (\a1 A-aN:glim a1))")


def test_discourse_anaphora_marker_is_out_of_v0_scope():
    """문장 간 공지시 장치를 불투명 술어로 통과시키면 binding 차원 평가가
    무의미해진다. v0 부분집합에서 명시적으로 제외한다(선언된 범위 축소)."""
    with pytest.raises(oa.AdapterUnsupported):
        oa.adapt(r"(InAnaphorSet 1 x101)")
    with pytest.raises(oa.AdapterUnsupported):
        oa.adapt(r"(Some (\x1 ^ (N-aD:zorble x1) (InAnaphorSet 1 x1)) "
                 r"(\x1 A-aN:glim x1))")


def test_predicate_taking_a_lambda_argument_fails_closed():
    """콜론 태그 술어가 람다를 인자로 받는 corpus 형태는 pred의 인자 자리에
    수식을 넣는다 — cg_ir 스키마상 무효다. adapter가 자기 출력을 검증하지
    않으면 무효 IR이 그대로 expected_ir로 커밋된다."""
    with pytest.raises(oa.AdapterUnsupported):
        oa.adapt(r"(N-b{N-aD}:the (\x112 N-aD:zorble x112))")


SUPPORTED_SHAPES = (
    r"(N-aD:zorble x1)",
    r"(Some (\x1 N-aD:zorble x1) (\z True))",
    r"(Some (\x1 N-aD:zorble x1) (\z A-aN:glim z))",
    r"(All (\x1 N-aD:zorble x1) (\y1 A-aN:glim y1))",
    r"(^ (N-aD:zorble x1) (A-aN:glim x1) (A-aN:prax x1))",
    r"(Some (\x1 ^ (N-aD:zorble x1) (A-aN:glim x1)) "
    r"(\z Some (\e1 B-aN-b{A-aN}:be e1 z) (\z True)))",
)


@pytest.mark.parametrize("lf", SUPPORTED_SHAPES)
def test_successful_adapt_always_returns_a_valid_cg_ir_formula(lf):
    """자격 항목 6 — 산출 검증. 성공 반환은 cg_ir 스키마를 만족해야 한다."""
    ir = oa.adapt(lf)
    assert cg_ir.validate_formula(ir) == [], (lf, cg_ir.validate_formula(ir))


# 위 목록 중 **닫힌** 것만. `(N-aD:zorble x1)`나 `(^ … x1 …)`는 x1이 자유인
# 열린 식이므로 닫힘 보존의 대상이 아니다 — RED 실행이 이 구별을 강제했다.
CLOSED_SHAPES = tuple(lf for lf in SUPPORTED_SHAPES if lf.lstrip("(").startswith(("Some", "All")))


@pytest.mark.parametrize("lf", CLOSED_SHAPES)
def test_closed_lf_adapts_to_a_closed_formula(lf):
    """자격 항목 7 — 닫힘 보존. 이 항목이 있었다면 위 결함은 첫 실측에서
    잡혔다(실 레코드 22/22가 자유변수를 가졌으므로)."""
    assert cg_ir.free_variables(oa.adapt(lf)) == set(), lf


def test_closed_shapes_selection_is_not_empty():
    """CLOSED_SHAPES가 조용히 비면 위 검사는 0건을 통과시킨다(공허 통과)."""
    assert len(CLOSED_SHAPES) == 4, CLOSED_SHAPES


def test_assert_head_is_in_v0_scope_refuses_a_head_outside_the_whitelist():
    """가드 직접 호출 음성 테스트. `adapt()` 경유 테스트만 있으면 이 가드는
    뮤테이션 게이트의 스캔 표면 안에 있어도 결박이 간접적이다 — 저장소 규약이
    직접 호출을 요구하는 이유다(docs/HARNESS_KNOWHOW.md §B4a)."""
    with pytest.raises(oa.AdapterUnsupported):
        oa._assert_head_is_in_v0_scope("Frobnicate")
    with pytest.raises(oa.AdapterUnsupported):
        oa._assert_head_is_in_v0_scope("InAnaphorSet")
    # 허용 head는 통과해야 한다 — 무조건 거부하는 가드는 파서를 죽인다.
    for ok in ("Some", "All", "^", "N-aD:zorble"):
        oa._assert_head_is_in_v0_scope(ok)
