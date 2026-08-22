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

    지원 집합: {"forall", "exists", "and", "pred", "or", "implies", "not", "box", "diamond"}

    Raises:
        ValueError: 지원되지 않는 constructor가 있을 때, 그것을 지명하는 메시지와 함께.
    """
    supported = {"forall", "exists", "and", "pred", "or", "implies", "not", "box", "diamond"}
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
        "$schema": "https://json-schema.org/draft/2020-12/schema",
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
        "$ref": "#/$defs/formula",
    }

    return schema
