"""cg_ir JSON Schema 생성기 — constructor profile에서 유도.

스키마를 상수로 박지 않는 이유: constructor profile은 사전등록 정본이자
manifest와 함께 동결되는 estimand boundary(ruling D-E2E-v1-21 Q21.3)이다.
스키마가 별도 상수면 profile과 불일치할 구조적 가능성이 생기는데, 단일
출처에서 파생시키면 그 불일치는 구조적으로 불가능해진다.

양화의 제한식(restriction) 필수화 근거: corpus의 주류 형태는 GQ
2-람다 일반화 양화자(generalized quantifier two-lambda form)다. 제한식 없이
통과하면 다른 방언(bare quantifier 형태)을 측정하게 되어 동치 관계가
틀어진다. 제한식을 required로 강제하면 이 방언 편향을 스키마 수준에서 차단한다.

예시(invented predicates):
  forall x. zorble(x) → glims(x)  # 유효: restriction=zorble(x), body=glims(x)
  exists y. tikk(y) ∧ prax(y)     # 유효: restriction=tikk(y), body=prax(y)
  ∀x. glims(x)                     # 무효: restriction 없음
"""
from __future__ import annotations

from typing import Any


V0_O1_CONSTRUCTORS = ("forall", "exists", "and", "pred")


def _assert_known_constructors(constructors: tuple[str, ...]) -> None:
    """Constructor 목록이 지원되는 종류만 포함하는지 검증.

    지원 집합: {"forall", "exists", "and", "pred", "or", "implies", "not",
    "box", "diamond", "count", "prop"}

    `count`·`prop`은 D-E2E-v1-29 Q29.1이 도입한 기수·비례 measurement
    constructor다. 수치는 **operator parameter**이지 term이 아니므로
    term 문법(var|entity)은 불변이다 — 판정 §2·§4가 수치 term 도입을 기각.

    Raises:
        ValueError: 지원되지 않는 constructor가 있을 때, 그것을 지명하는 메시지와 함께.
    """
    supported = {"forall", "exists", "and", "pred", "or", "implies", "not",
                 "box", "diamond", "count", "prop"}
    for ctor in constructors:
        if ctor not in supported:
            raise ValueError(f"unknown constructor: {ctor!r}")


def formula_json_schema(constructors: tuple[str, ...] = V0_O1_CONSTRUCTORS) -> dict[str, Any]:
    """Constructor 목록에서 JSON Schema (draft 2020-12)를 유도해 반환.

    같은 입력에 대해 호출마다 같은 dict를 반환한다(결정성).
    JSON 직렬화 가능하다.

    Args:
        constructors: 스키마가 수용할 constructor 이름 튜플.
            기본값: V0_O1_CONSTRUCTORS (O1 방언).

    Returns:
        JSON Schema dict. 최상위는 formula를 $ref로 가리킨다.

    Raises:
        ValueError: constructors에 지원되지 않는 이름이 있을 때.
    """
    _assert_known_constructors(constructors)

    # 각 constructor에 대한 schema branch
    schema_branches = {}

    # forall과 exists: var (string) + restriction (formula) + body (formula) 필수
    if "forall" in constructors:
        schema_branches["forall"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "forall"},
                "var": {"type": "string"},
                "restriction": {"$ref": "#/$defs/formula"},
                "body": {"$ref": "#/$defs/formula"},
            },
            "required": ["kind", "var", "restriction", "body"],
            "additionalProperties": False,
        }

    if "exists" in constructors:
        schema_branches["exists"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "exists"},
                "var": {"type": "string"},
                "restriction": {"$ref": "#/$defs/formula"},
                "body": {"$ref": "#/$defs/formula"},
            },
            "required": ["kind", "var", "restriction", "body"],
            "additionalProperties": False,
        }

    # and와 or: args (array of formula), minItems 1
    if "and" in constructors:
        schema_branches["and"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "and"},
                "args": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/formula"},
                    "minItems": 1,
                },
            },
            "required": ["kind", "args"],
            "additionalProperties": False,
        }

    if "or" in constructors:
        schema_branches["or"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "or"},
                "args": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/formula"},
                    "minItems": 1,
                },
            },
            "required": ["kind", "args"],
            "additionalProperties": False,
        }

    # pred: name (string) + args (array of term)
    if "pred" in constructors:
        schema_branches["pred"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "pred"},
                "name": {"type": "string"},
                "args": {
                    "type": "array",
                    "items": {"$ref": "#/$defs/term"},
                },
            },
            "required": ["kind", "name", "args"],
            "additionalProperties": False,
        }

    # not, box, diamond: body (formula)
    if "not" in constructors:
        schema_branches["not"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "not"},
                "body": {"$ref": "#/$defs/formula"},
            },
            "required": ["kind", "body"],
            "additionalProperties": False,
        }

    if "box" in constructors:
        schema_branches["box"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "box"},
                "body": {"$ref": "#/$defs/formula"},
            },
            "required": ["kind", "body"],
            "additionalProperties": False,
        }

    if "diamond" in constructors:
        schema_branches["diamond"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "diamond"},
                "body": {"$ref": "#/$defs/formula"},
            },
            "required": ["kind", "body"],
            "additionalProperties": False,
        }

    # count: 기수 양화 binder (D-29 Q29.1). rel·num은 parameter, 결박은
    # forall/exists와 동형. 의미는 |{x: R(x)∧B(x)}| rel num (판정 §3).
    if "count" in constructors:
        schema_branches["count"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "count"},
                "rel": {"enum": ["eq", "ge", "le", "gt", "lt"]},
                "num": {"type": "integer"},
                "var": {"type": "string"},
                "restriction": {"$ref": "#/$defs/formula"},
                "body": {"$ref": "#/$defs/formula"},
            },
            "required": ["kind", "rel", "num", "var", "restriction", "body"],
            "additionalProperties": False,
        }

    # prop: 비례 양화 binder. count와 **분리**한다 — most는 어떤 고정 기수
    # threshold로도 표현할 수 없다(restrictor 크기 의존, 판정 §5 및 우리
    # 재검증: 크기 1~8에서 해집합 공집합). v1은 rel=most만(§6).
    if "prop" in constructors:
        schema_branches["prop"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "prop"},
                "rel": {"enum": ["most"]},
                "var": {"type": "string"},
                "restriction": {"$ref": "#/$defs/formula"},
                "body": {"$ref": "#/$defs/formula"},
            },
            "required": ["kind", "rel", "var", "restriction", "body"],
            "additionalProperties": False,
        }

    # implies: left + right (both formula)
    if "implies" in constructors:
        schema_branches["implies"] = {
            "type": "object",
            "properties": {
                "kind": {"const": "implies"},
                "left": {"$ref": "#/$defs/formula"},
                "right": {"$ref": "#/$defs/formula"},
            },
            "required": ["kind", "left", "right"],
            "additionalProperties": False,
        }

    # 조건부로 branch를 추가하는 대신, 모든 가능성을 포함하고 oneOf로 선택하게 함
    # (다만 constructor 목록에 없는 것들은 제외)
    formula_one_of = list(schema_branches.values())

    schema = {
        "$defs": {
            "term": {
                "oneOf": [
                    {
                        "type": "object",
                        "properties": {
                            "kind": {"const": "var"},
                            "name": {"type": "string"},
                        },
                        "required": ["kind", "name"],
                        "additionalProperties": False,
                    },
                    {
                        "type": "object",
                        "properties": {
                            "kind": {"const": "entity"},
                            "name": {"type": "string"},
                        },
                        "required": ["kind", "name"],
                        "additionalProperties": False,
                    },
                ]
            },
            "formula": {
                "oneOf": formula_one_of,
            },
        },
        # 실측된 dispatch 계약 2건(2026-08-23 리허설): ① $schema 메타 참조는
        # 하네스 검증기가 해석 못 함 — 방출하지 않는다. ② API가 tool
        # input_schema의 root "type"을 요구 — bare $ref root는 400. formula의
        # 모든 구성자가 object이므로 type:object + allOf($ref)는 의미 불변.
        "type": "object",
        "allOf": [{"$ref": "#/$defs/formula"}],
    }

    return schema


def dispatch_envelope_schema(
        constructors: "tuple[str, ...]" = V0_O1_CONSTRUCTORS) -> dict:
    """schema-forced dispatch용 봉투: {"formula": <formula>}.

    실측된 API 계약(2026-08-23 리허설 3건째): tool input_schema의 root에
    oneOf/allOf/anyOf가 올 수 없다. formula는 본질적으로 oneOf이므로 root에
    직접 둘 수 없고, 단일 property 봉투로 감싼다. 실행기는 "formula" 키를
    벗겨 순수 IR을 얻는다. formula_json_schema는 그대로 순수 IR 검증
    (자격 항목 6, 커널 대조)에 쓰인다 — 두 함수가 같은 constructor 목록에서
    유도되므로 어긋날 수 없다.
    """
    inner = formula_json_schema(constructors)
    return {
        "type": "object",
        "properties": {"formula": {"$ref": "#/$defs/formula"}},
        "required": ["formula"],
        "additionalProperties": False,
        "$defs": inner["$defs"],
    }
