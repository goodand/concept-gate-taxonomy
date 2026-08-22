"""SBN adapter (PMB_SBN_5_1 profile)의 TDD 계약 — RED 먼저.

D-E2E-v1-22 Q22.2: paired-negation→forall은 **source-결박 codec**으로만
허용. 설계 실측은 SBN_ADAPTER_DESIGN.md(box 사슬 규칙·∀ codec 실물 확정·
<1 외 인덱스 코너). 모든 SBN 조각은 **발명 synset**(zorble.n.01 등)으로
같은 문법을 재현한 것 — corpus 텍스트 0바이트(ORACLE-12).

계약이 고정하는 설계 결정:
- 술어명은 **raw synset 그대로**(lemma 정규화는 평가 profile의 일 — D-22
  §10; adapter가 하면 expected_ir_sha256이 정규화에 오염된다)
- box 내용 = 행 순서 우선의 exists 우결합 사슬 + and; role/DRS-op = 이항
  pred(name, [src, tgt]); 상수 = entity
- ∀ codec: NEG box(restriction, synset≥1) 안에서 두 번째 NEG(body) —
  forall 변수는 restriction의 **첫** synset 지시체. 나머지 restriction
  지시체는 restriction 안 exists로 남되, **body가 그것을 참조하면
  AdapterUnsupported**(donkey 결박은 v0 밖 — 조용한 오역보다 거부)
- fail-closed: NEGATION 외 box-op, `<1` 외 box 인덱스(실측된 릴리스 파서
  자기모순 코너), 미등재 role/op 토큰, 범위 밖 상대 인덱스(동봉 파서는
  상수로 재해석하며 ill-formed 표시만 하지만 우리는 거부 — 오역 hash화가
  최악), 비정형 synset id, 빈 입력
"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from conceptgate import cg_ir
from conceptgate import cg_sbn_adapter as sa


def fp(ir):
    return cg_ir.formula_fingerprint(ir)


V = lambda n: {"kind": "var", "name": n}
E = lambda n: {"kind": "entity", "name": n}
P = lambda name, *args: {"kind": "pred", "name": name, "args": list(args)}


def EX(v, body):
    return {"kind": "exists", "var": v, "restriction": P("True"), "body": body}


def AND(*args):
    return {"kind": "and", "args": list(args)}


# ------------------------------------------------------------ 구조 매핑 ----

def test_single_synset_line_is_existential_pred():
    ir = sa.adapt_sbn("zorble.n.01")
    assert cg_ir.validate_formula(ir) == []
    assert cg_ir.free_variables(ir) == set()
    assert fp(ir) == fp(EX("x0", P("zorble.n.01", V("x0"))))


def test_predicate_names_stay_raw_synsets():
    """정규화는 평가 profile의 일(D-22 §10) — adapter는 원문 충실."""
    ir = sa.adapt_sbn("zorble.n.01")
    names = set()
    def walk(n):
        if isinstance(n, dict):
            if n.get("kind") == "pred": names.add(n["name"])
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(ir)
    assert "zorble.n.01" in names and "zorble" not in names


def test_roles_become_binary_preds_with_relative_targets():
    sbn = "zorble.n.01\nprax.v.02 Agent -1 Time +1\ntime.n.08 EQU now"
    ir = sa.adapt_sbn(sbn)
    assert cg_ir.validate_formula(ir) == [] and cg_ir.free_variables(ir) == set()
    expected = EX("x0", EX("x1", EX("x2", AND(
        P("zorble.n.01", V("x0")),
        P("prax.v.02", V("x1")),
        P("Agent", V("x1"), V("x0")),
        P("Time", V("x1"), V("x2")),
        P("time.n.08", V("x2")),
        P("EQU", V("x2"), E("now"))))))
    assert fp(ir) == fp(expected)


def test_name_constant_becomes_entity():
    ir = sa.adapt_sbn('krell.n.02 Name "Vex"')
    expected = EX("x0", AND(P("krell.n.02", V("x0")),
                            P("Name", V("x0"), E("Vex"))))
    assert fp(ir) == fp(expected)


# ------------------------------------------------------------- NEG 축 ------

def test_single_negation_box_is_not():
    sbn = "zorble.n.01\n            NEGATION <1\nprax.v.02 Theme -1"
    ir = sa.adapt_sbn(sbn)
    assert cg_ir.validate_formula(ir) == [] and cg_ir.free_variables(ir) == set()
    expected = EX("x0", AND(
        P("zorble.n.01", V("x0")),
        {"kind": "not", "body": EX("x1", AND(
            P("prax.v.02", V("x1")), P("Theme", V("x1"), V("x0"))))}))
    assert fp(ir) == fp(expected)


def test_paired_negation_decodes_to_forall():
    """p66/d2061의 구조를 발명 synset으로 재현 — ∀ codec의 양성."""
    sbn = ("            NEGATION <1\n"
           "zorble.n.01 NEQ +1\n"
           'krell.n.02  Name "Vex"\n'
           "            NEGATION <1\n"
           "prax.v.02   Theme -2 Time +1\n"
           "time.n.08   TPR now")
    ir = sa.adapt_sbn(sbn)
    assert cg_ir.validate_formula(ir) == [] and cg_ir.free_variables(ir) == set()
    assert ir["kind"] == "forall"
    expected = {"kind": "forall", "var": "u",
        "restriction": EX("j", AND(
            P("zorble.n.01", V("u")), P("NEQ", V("u"), V("j")),
            P("krell.n.02", V("j")), P("Name", V("j"), E("Vex")))),
        "body": EX("e", EX("t", AND(
            P("prax.v.02", V("e")), P("Theme", V("e"), V("u")),
            P("Time", V("e"), V("t")),
            P("time.n.08", V("t")), P("TPR", V("t"), E("now")))))}
    assert fp(ir) == fp(expected)


def test_odd_negation_chain_is_negated_forall():
    """p76/d2248 구조 재현 — 양화↔부정 scope가 IR에 보존돼야 채점 대상이 된다."""
    sbn = ("            NEGATION <1\n"
           "            NEGATION <1\n"
           "zorble.n.01\n"
           "            NEGATION <1\n"
           "glim.a.01   Experiencer -1")
    ir = sa.adapt_sbn(sbn)
    assert cg_ir.validate_formula(ir) == [] and cg_ir.free_variables(ir) == set()
    assert ir["kind"] == "not"
    assert ir["body"]["kind"] == "forall"


def test_donkey_reference_from_body_fails_closed():
    """body가 restriction의 둘째 지시체를 참조 — v0 결박 밖, 조용한 오역 금지."""
    sbn = ("            NEGATION <1\n"
           "zorble.n.01 NEQ +1\n"
           "krell.n.02\n"
           "            NEGATION <1\n"
           "prax.v.02   Theme -1")   # -1 = krell (restriction 둘째)
    with pytest.raises(sa.AdapterUnsupported) as ei:
        sa.adapt_sbn(sbn)
    # 귀속 결박: 이 거부는 donkey 가드의 것이어야 한다. 최종 닫힘 검사도
    # 같은 입력을 거부하지만(뮤테이션 실측 — 가드 무력화 시 그쪽이 잡음),
    # 원인을 명명하지 못한다. 메시지를 결박해야 가드가 관측 가능해진다.
    assert "donkey" in str(ei.value)


# ------------------------------------------------------------ fail-closed --

@pytest.mark.parametrize("op", ["CONJUNCTION", "POSSIBILITY", "NECESSITY",
                                "CONTINUATION", "ATTRIBUTION"])
def test_non_negation_box_ops_fail_closed(op):
    with pytest.raises(sa.AdapterUnsupported):
        sa.adapt_sbn(f"zorble.n.01\n            {op} <1\nprax.v.02 Theme -1")


def test_box_index_other_than_one_fails_closed():
    """실측 코너: 릴리스 gold에 <2가 실재하고 동봉 파서도 못 읽는다 — 우리는
    후보 풀에 없음을 확인했고(0/695), 지원 확대 대신 명시 거부한다."""
    with pytest.raises(sa.AdapterUnsupported):
        sa.adapt_sbn("zorble.n.01\n            NEGATION <2\nprax.v.02 Theme -1")


def test_unknown_role_token_fails_closed():
    with pytest.raises(sa.AdapterUnsupported):
        sa.adapt_sbn("zorble.n.01\nprax.v.02 Frobnicates -1")


def test_out_of_range_index_refused_not_reinterpreted():
    """동봉 파서는 범위 밖 인덱스를 상수로 재해석(ill-formed 표시)하지만,
    오역이 hash로 굳는 쪽이 최악이므로 우리는 거부한다."""
    with pytest.raises((sa.AdapterSyntaxError, sa.AdapterUnsupported)):
        sa.adapt_sbn("zorble.n.01\nprax.v.02 Theme -5")


def test_malformed_and_empty_inputs():
    for bad in ("", "   \n  ", "not_a_synset_line_at_all !!", "zorble.q.01"):
        with pytest.raises((sa.AdapterSyntaxError, sa.AdapterUnsupported)):
            sa.adapt_sbn(bad)


def test_comment_lines_and_inline_comments_are_stripped():
    sbn = ("%%% header comment\n"
           "zorble.n.01            % original words [0-6]\n")
    assert fp(sa.adapt_sbn(sbn)) == fp(sa.adapt_sbn("zorble.n.01"))


# ------------------------------------------------------------- 자격 축 -----

def test_deterministic_replay():
    sbn = "zorble.n.01\nprax.v.02 Agent -1"
    assert sa.adapt_sbn(sbn) == sa.adapt_sbn(sbn)


def test_codec_is_not_a_general_rewrite():
    """자격 9의 음성 판별: IR 수준의 not(exists(...not(...)))를 만들 뿐인
    '단순 부정 두 개'(중첩 아닌 형제성 없음 — restriction box가 빈 사슬)는
    forall이 되면 안 된다."""
    sbn = ("            NEGATION <1\n"
           "            NEGATION <1\n"
           "zorble.n.01")
    ir = sa.adapt_sbn(sbn)
    # restriction 없는 이중 NEG: not(not(exists zorble)) — forall 금지
    assert ir["kind"] == "not" and ir["body"]["kind"] == "not"


# --------------------------------------------- 격리·순수성 (AST 집행) -------

def test_sbn_adapter_is_pure_and_leaf():
    src = Path(inspect.getfile(sa)).read_text(encoding="utf-8")
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


def test_sbn_adapter_not_imported_by_refine_or_verify():
    root = Path(inspect.getfile(sa)).parent
    for name in ("server.py", "cg_obligations.py", "cg_normalizer.py",
                 "concept_gate_v7.py", "cg_ir.py", "cg_identity.py",
                 "cg_evaluate.py", "cg_oracle_adapter.py",
                 "cg_fixture_resolver.py"):
        src = (root / name).read_text(encoding="utf-8")
        assert "cg_sbn_adapter" not in src, f"{name} imports the sbn adapter"


def test_multiword_quoted_name_constant():
    """Path A 스모크 실측(2026-08-23): 여러 단어 인용 상수가 토큰 단위로
    쪼개져 SYNTAX 18건 — 스펙의 NAME_CONSTANT_PATTERN 둘째 대안(열린 따옴표)
    이 연속 소비를 규정하는데 계약이 누락했었다. 닫는 따옴표까지 병합."""
    ir = sa.adapt_sbn('krell.n.02 Name "Vex Zorble Prime"')
    expected = EX("x0", AND(P("krell.n.02", V("x0")),
                            P("Name", V("x0"), E("Vex Zorble Prime"))))
    assert fp(ir) == fp(expected)


def test_unterminated_quote_fails_closed():
    with pytest.raises((sa.AdapterSyntaxError, sa.AdapterUnsupported)):
        sa.adapt_sbn('krell.n.02 Name "Vex Zorble')
