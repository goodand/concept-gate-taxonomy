"""cg_ir 재귀 JSON 스키마 생성기의 TDD 계약 — RED 먼저 (Stage 2 준비물 ②).

trial subject(o1-compiler)의 schema-forced dispatch에 쓸 JSON Schema를
**constructor 목록에서 유도**한다. 상수 스키마를 박지 않는 이유: constructor
profile은 사전등록 정본(D-21 Q21.3)이라 manifest와 함께 동결되는데, 스키마가
별도 상수면 profile과 어긋날 수 있다 — 단일 출처에서 파생시키면 구조적으로
불가능해진다.

프로브 실측(PROBE_o1_compiler_20260823.md)이 이 준비물의 필요를 실증했다:
프롬프트 규율만으로는 fence 위반이 나온다 — 강제는 스키마가 한다.

검증기: 설치된 jsonschema 4.26 (Ponytail 5단 — H1a 시절엔 없어서 수제
검증기를 썼고, 그 주석이 이력을 증언한다). 프로덕션 경로는 스키마 dict를
방출만 하고 검증은 dispatch 하네스가 한다 — 이 모듈은 검증기를 갖지 않는다.
"""
from __future__ import annotations

import ast
import inspect
import json
from pathlib import Path

import jsonschema
import pytest

from conceptgate import cg_ir
from conceptgate import cg_ir_schema as sch


def valid(doc, schema) -> bool:
    try:
        jsonschema.validate(doc, schema)
        return True
    except jsonschema.ValidationError:
        return False


P = lambda n, *args: {"kind": "pred", "name": n,
                      "args": [{"kind": "var", "name": a} for a in args]}


# ------------------------------------------------------------- 생성 계약 ---

def test_default_constructors_are_the_o1_v0_dialect():
    assert sch.V0_O1_CONSTRUCTORS == ("forall", "exists", "and", "pred")


def test_schema_is_deterministic_and_json_serializable():
    a, b = sch.formula_json_schema(), sch.formula_json_schema()
    assert a == b
    json.dumps(a)  # 직렬화 가능해야 dispatch에 실을 수 있다


def test_unknown_constructor_is_refused():
    with pytest.raises(ValueError):
        sch._assert_known_constructors(("forall", "frobnicate"))
    with pytest.raises(ValueError):
        sch.formula_json_schema(("frobnicate",))


# ------------------------------------------------------------- 수용 축 -----

def test_accepts_the_probe_output_shape():
    """프로브 B가 실제로 낸 IR — 이것이 통과 못 하면 스키마가 코호트를 죽인다."""
    ir = {"kind": "forall", "var": "x",
          "restriction": P("zorble", "x"), "body": P("glims", "x")}
    assert valid(ir, sch.formula_json_schema())
    assert cg_ir.validate_formula(ir) == []


def test_accepts_nested_quantifiers_depth_three():
    ir = {"kind": "forall", "var": "x", "restriction": P("zorble", "x"),
          "body": {"kind": "exists", "var": "y", "restriction": P("tikk", "y"),
                   "body": {"kind": "and", "args": [
                       P("glims", "x", "y"),
                       {"kind": "exists", "var": "e",
                        "restriction": P("quux", "e"),
                        "body": P("prax", "e", "x")}]}}}
    assert valid(ir, sch.formula_json_schema())
    assert cg_ir.validate_formula(ir) == []


def test_accepts_entity_terms_in_pred_args():
    ir = P("glims", "x")
    ir["args"].append({"kind": "entity", "name": "socrates"})
    ir = {"kind": "exists", "var": "x", "restriction": P("zorble", "x"),
          "body": ir}
    assert valid(ir, sch.formula_json_schema())


# ------------------------------------------------------------- 거부 축 -----

def test_rejects_formula_in_pred_argument_slot():
    """커널 G57(PRED_ARG_NOT_TERM)과 같은 경계를 스키마도 지켜야 한다 —
    스키마가 통과시키고 커널이 거부하면 그 불일치는 UNSCORABLE 회계를
    오염시킨다."""
    bad = {"kind": "forall", "var": "x", "restriction": P("zorble", "x"),
           "body": {"kind": "pred", "name": "glims",
                    "args": [{"kind": "and", "args": [P("tikk", "x")]}]}}
    assert not valid(bad, sch.formula_json_schema())
    assert any(e["code"] == "PRED_ARG_NOT_TERM"
               for e in cg_ir.validate_formula(bad))


def test_rejects_quantifier_without_restriction():
    """O1 방언에서 양화는 GQ 2-람다 형 — restriction 필수. 없는 채 통과하면
    corpus 형태와 다른 방언을 측정하게 된다."""
    bad = {"kind": "forall", "var": "x", "body": P("glims", "x")}
    assert not valid(bad, sch.formula_json_schema())


@pytest.mark.parametrize("bad", [
    {"kind": "box", "body": {"kind": "pred", "name": "p", "args": []}},
    {"kind": "implies", "left": {"kind": "pred", "name": "p", "args": []},
     "right": {"kind": "pred", "name": "q", "args": []}},
    {"kind": "frobnicate"},
], ids=["box-outside-profile", "implies-outside-profile", "unknown-kind"])
def test_rejects_kinds_outside_the_constructor_list(bad):
    assert not valid(bad, sch.formula_json_schema())


def test_rejects_extra_properties():
    ir = {"kind": "forall", "var": "x", "restriction": P("zorble", "x"),
          "body": P("glims", "x"), "hint": "the answer is 42"}
    assert not valid(ir, sch.formula_json_schema()), (
        "여분 필드를 허용하면 subject가 스키마 밖 채널로 무엇이든 실어 보낼 수 있다")


def test_rejects_non_object_output():
    for bad in ("```json\n{}\n```", [], "forall x. glims(x)", 42, None):
        assert not valid(bad, sch.formula_json_schema())


# ---------------------------------------------------- profile 파라미터화 ---

def test_wider_constructor_list_admits_modal_kinds():
    """profile이 (판정을 받아) 넓어지면 스키마도 같은 호출로 넓어진다 —
    O3 준비가 이 함수의 재사용으로 끝나는지의 선행 검사."""
    wide = sch.formula_json_schema(("forall", "exists", "and", "pred",
                                    "box", "diamond", "not"))
    ir = {"kind": "box", "body": {"kind": "not", "body": P("glims", "x")}}
    assert valid(ir, wide)
    assert cg_ir.validate_formula(ir) == []


def test_every_default_constructor_is_a_kernel_kind():
    """스키마 어휘 ⊆ 커널 어휘 — 스키마가 커널이 모르는 kind를 수용하면
    subject 출력이 evaluate 전에 죽는다."""
    probes = {
        "forall": {"kind": "forall", "var": "x", "body": P("p", "x"),
                   "restriction": P("q", "x")},
        "exists": {"kind": "exists", "var": "x", "body": P("p", "x"),
                   "restriction": P("q", "x")},
        "and": {"kind": "and", "args": [P("p", "x")]},
        "pred": P("p", "x"),
    }
    for kind in sch.V0_O1_CONSTRUCTORS:
        assert cg_ir.validate_formula(probes[kind]) == [], kind


# ------------------------------------------------------------- 순수성 ------

def test_schema_module_imports_stay_pure():
    tree = ast.parse(Path(inspect.getfile(sch)).read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                for a in n.names}
    imported |= {n.module for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= {"__future__", "typing"}, imported


def test_schema_carries_no_meta_schema_reference():
    """실측(2026-08-23 리허설): dispatch 하네스의 스키마 검증기가
    `$schema: draft/2020-12` 메타 참조를 해석하지 못해 3 trial 전부
    dispatch 전에 죽었다. 메타 키는 jsonschema 검증에 불필요하고, dispatch용
    사본에서만 벗기면 등록 아티팩트와 갈라진다(드리프트) — 방출하지 않는 것이
    단일 아티팩트를 지킨다."""
    assert "$schema" not in sch.formula_json_schema()


def test_schema_root_declares_type_object():
    """실측 2건째(2026-08-23 리허설): dispatch가 스키마를 tool input_schema로
    싸는데 API가 root의 "type" 필드를 요구한다(400: input_schema.type Field
    required). bare $ref root는 전송 자체가 안 된다. formula는 모든 구성자가
    object이므로 root를 type:object + allOf($ref)로 두면 의미 불변이다."""
    s = sch.formula_json_schema()
    assert s.get("type") == "object"
    assert s.get("allOf") == [{"$ref": "#/$defs/formula"}]


def test_dispatch_envelope_wraps_formula_for_the_tool_api():
    """실측 3건째(2026-08-23 리허설): API가 tool input_schema의 **root에
    oneOf/allOf/anyOf를 불허**한다(400). formula는 본질적으로 oneOf라 root에
    올 수 없다 — dispatch는 {"formula": <formula>} 봉투로 강제하고 실행기가
    벗긴다. 봉투는 dispatch 전용이고, formula 스키마 자체(자격 항목 6·커널
    대조용)는 별도로 남는다 — 하나로 합치면 순수 IR 검증이 깨진다."""
    env = sch.dispatch_envelope_schema()
    assert env["type"] == "object"
    assert set(env) & {"oneOf", "allOf", "anyOf"} == set()
    assert env["required"] == ["formula"]
    assert env["additionalProperties"] is False
    ir = {"kind": "forall", "var": "x",
          "restriction": P("zorble", "x"), "body": P("glims", "x")}
    assert valid({"formula": ir}, env)
    assert not valid(ir, env)                       # 봉투 없이 통과 금지
    assert not valid({"formula": ir, "note": 1}, env)  # 곁채널 금지
    # 봉투 내부는 formula 스키마와 같은 경계를 지킨다
    bad = {"formula": {"kind": "forall", "var": "x", "body": P("g", "x")}}
    assert not valid(bad, env)


# ---- D-E2E-v1-29 Q29.1: count·prop constructor (기수·비례 measurement) ----

def test_count_branch_shape():
    """`count`는 자체 binder다 — var·restriction·body를 갖고 rel·num이
    **operator parameter**다. 숫자를 term으로 넣지 않으므로 항 문법
    (var|entity)은 불변이다(판정 §2·§4)."""
    s = sch.formula_json_schema(("forall", "exists", "and", "pred", "count"))
    branch = next(b for b in s["$defs"]["formula"]["oneOf"]
                  if b["properties"]["kind"]["const"] == "count")
    assert set(branch["required"]) == {"kind", "rel", "num", "var", "restriction", "body"}
    assert branch["properties"]["rel"]["enum"] == ["eq", "ge", "le", "gt", "lt"]
    assert branch["properties"]["num"]["type"] == "integer"
    assert branch["properties"]["var"]["type"] == "string"
    assert branch["properties"]["restriction"] == {"$ref": "#/$defs/formula"}
    assert branch["properties"]["body"] == {"$ref": "#/$defs/formula"}
    assert branch["additionalProperties"] is False


def test_prop_branch_shape_v1_most_only():
    """v1은 `most` 하나만 — half·ratio·percentage는 source가 없어 미설계
    (판정 §6). 확장은 profile revision 사안이다."""
    s = sch.formula_json_schema(("forall", "exists", "and", "pred", "prop"))
    branch = next(b for b in s["$defs"]["formula"]["oneOf"]
                  if b["properties"]["kind"]["const"] == "prop")
    assert set(branch["required"]) == {"kind", "rel", "var", "restriction", "body"}
    assert branch["properties"]["rel"]["enum"] == ["most"]
    assert "num" not in branch["properties"]          # 비례는 수치를 갖지 않는다


def test_count_and_prop_are_separate_constructors():
    """판정 §5: most는 어떤 고정 기수 threshold로도 표현할 수 없으므로
    두 semantic family를 한 operator에 섞지 않는다."""
    s = sch.formula_json_schema(("pred", "count", "prop"))
    kinds = [b["properties"]["kind"]["const"] for b in s["$defs"]["formula"]["oneOf"]]
    assert "count" in kinds and "prop" in kinds
    cb = next(b for b in s["$defs"]["formula"]["oneOf"]
              if b["properties"]["kind"]["const"] == "count")
    assert "most" not in cb["properties"]["rel"]["enum"]


def test_numeric_terms_are_not_introduced():
    """판정 §4: 수치 term 도입은 기각됐다 — term은 var|entity뿐이다."""
    s = sch.formula_json_schema(("pred", "count"))
    term_kinds = [b["properties"]["kind"]["const"] for b in s["$defs"]["term"]["oneOf"]]
    assert term_kinds == ["var", "entity"]


def test_dispatch_envelope_carries_count_and_prop():
    e = sch.dispatch_envelope_schema(("forall", "exists", "and", "pred", "not",
                                  "implies", "count", "prop"))
    kinds = [b["properties"]["kind"]["const"] for b in e["$defs"]["formula"]["oneOf"]]
    assert {"count", "prop"} <= set(kinds)
    assert list(e["properties"]) == ["formula"]      # 봉투 패턴 불변


def test_schema_rejects_malformed_count():
    import jsonschema
    s = sch.formula_json_schema(("pred", "count"))
    P = lambda n: {"kind": "pred", "name": n, "args": []}
    good = {"kind": "count", "rel": "ge", "num": 3, "var": "x",
            "restriction": P("dog"), "body": P("bark")}
    jsonschema.validate(good, s)
    for bad, why in (
        ({**good, "rel": "most"}, "rel에 most 금지"),
        ({**good, "num": "3"}, "num은 정수"),
        ({k: v for k, v in good.items() if k != "num"}, "num 누락"),
        ({**good, "num": 3, "extra": 1}, "additionalProperties"),
    ):
        try:
            jsonschema.validate(bad, s)
            raise AssertionError(f"거부되지 않았다: {why}")
        except jsonschema.ValidationError:
            pass
