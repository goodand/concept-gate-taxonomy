"""MEASUREMENT_SATISFIABILITY_V2 — 측정 가능성 게이트 (D-25 Q25.4, D-26 §14 개정).

검사 대상은 모델 능력이 아니라 측정 계약이다: **허용된 subject 언어 안에
이 fixture를 PASS시키는 출력이 최소 1개 존재하는가**(판정 §20-21). 없으면
그 fixture는 모델 성능과 무관하게 실패가 예정된 것이므로 코호트에 들어가면
안 된다(pre-freeze: INELIGIBLE).

witness는 결정론이다(판정 §22, LLM 불요): oracle IR → projection →
signature를 subject 방언으로 재렌더한 것. D-26이 implies를 방언에 넣은 뒤
렌더는 사실상 항등이다 — implies는 위치 그대로 통과하고(경계 이동 금지),
or 등 방언 밖 연산자만 렌더 불가(= subject_dialect_expressible 실패)로
정직하게 보고한다. 도달성은 D-26 §13-14에 따라 적격 조건이 아니라 진단이다. 이것은 oracle
재작성이 아니다 — witness는 측정 자격 장비이며 어떤 model-facing 산출물에도
들어가지 않는다(판정 §23; 기록에는 witness의 sha256만 남는다).
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

import jsonschema

from _stage2_scope_projection import project_scope_for_case
from conceptgate.cg_evaluate import evaluate
from conceptgate.cg_identity import canonical_sha256
from conceptgate.cg_ir_schema import formula_json_schema

GATE_ID = "MEASUREMENT_SATISFIABILITY_V2"   # D-26 §14: 도달성은 diagnostic

# 동결 subject 방언 = V4 6종 (D-26 Q26.1; projection 모듈이 유도 정본)
from _stage2_scope_projection import DIALECT_V4_CONSTRUCTORS  # noqa: E402

_SCHEMA = formula_json_schema(tuple(DIALECT_V4_CONSTRUCTORS))
_TRUE = {"kind": "pred", "name": "True", "args": []}


class Unrenderable(Exception):
    """signature에 subject 방언으로 표현 불가능한 구조가 남았다."""


def _is_true(node: Any) -> bool:
    return (isinstance(node, dict) and node.get("kind") == "pred"
            and node.get("name") == "True")


def render_witness(signature: dict) -> dict:
    """signature → subject 방언 formula (결정론).

    Raises:
        Unrenderable: implies가 forall 직하가 아닌 위치에 있거나,
            방언 밖 kind(or 등)가 남아 있을 때.
    """
    def walk(node: Any) -> Any:
        if not isinstance(node, dict):
            raise Unrenderable(f"non-dict node: {node!r}")
        kind = node.get("kind")
        if kind in ("forall", "exists"):
            body = node["body"]
            return {"kind": kind, "var": node["var"],
                    "restriction": walk(node["restriction"]),
                    "body": walk(body)}
        if kind == "not":
            return {"kind": "not", "body": walk(node["body"])}
        if kind == "implies":
            # D-26: implies는 방언 안 — 위치 그대로 통과 (경계 이동 금지)
            return {"kind": "implies", "left": walk(node["left"]),
                    "right": walk(node["right"])}
        if kind == "and":
            return {"kind": "and", "args": [walk(a) for a in node["args"]]}
        if kind == "pred":
            return {"kind": "pred", "name": node["name"],
                    "args": [dict(a) for a in node.get("args", [])]}
        raise Unrenderable(f"kind {kind!r} has no subject-dialect rendering")

    return walk(signature)


def check_oracle_ir(case_id: str, oracle_ir: dict) -> dict:
    """oracle IR 하나의 측정 가능성 판정. 기록에 식 내용은 넣지 않는다."""
    checks = {
        "oracle_adapter_success": True,   # IR이 이미 손에 있음
        "oracle_projection_success": False,
        "subject_dialect_expressible": False,
        "subject_schema_valid": False,
        "hidden_witness_can_score_PASS": False,
        "no_unsupported_scored_operator": False,
    }
    detail = None
    witness_sha = "0" * 64
    try:
        sig = project_scope_for_case(case_id, oracle_ir)
        checks["oracle_projection_success"] = True
        try:
            witness = render_witness(sig)
            checks["subject_dialect_expressible"] = True
            try:
                jsonschema.validate(witness, _SCHEMA)
                checks["subject_schema_valid"] = True
                checks["no_unsupported_scored_operator"] = True
            except jsonschema.ValidationError as exc:
                detail = f"schema: {exc.message[:120]}"
            if checks["subject_schema_valid"]:
                round_trip = project_scope_for_case(case_id, witness)
                if evaluate(round_trip, sig)["result"] == "pass":
                    checks["hidden_witness_can_score_PASS"] = True
                    witness_sha = canonical_sha256(witness)
                else:
                    detail = "witness round-trip did not score PASS"
        except Unrenderable as exc:
            detail = f"unrenderable: {exc}"
            checks["no_unsupported_scored_operator"] = False
    except ValueError:
        raise            # 미지 접두어는 게이트의 소관이 아니다 — 그대로 전파
    except Exception as exc:  # projection 자체 실패
        detail = f"projection: {type(exc).__name__}: {str(exc)[:120]}"

    verdict = ("SATISFIABLE" if all(checks.values())
               else "MEASUREMENT_UNSATISFIABLE")
    record = {"gate": GATE_ID, "case_id": case_id, "verdict": verdict,
              "checks": checks, "witness_sha256": witness_sha,
              # D-26 §13-14: 라벨 도달성은 적격 조건이 아니라 진단 —
              # 문장이 있는 호출자(check_fixture_entry)가 채운다
              "diagnostic": {}}
    if detail:
        record["detail"] = detail
    return record


def check_fixture_entry(entry: dict, cache_dir, adapter_fn: Callable,
                        lf_bytes: bytes | None = None) -> dict:
    """manifest entry 하나를 캐시 LF → adapter → 게이트로 관통시킨다."""
    case_id = entry["case_id"]
    if lf_bytes is None:
        from pathlib import Path
        lf_bytes = (Path(cache_dir) / entry["lf_sha256"]).read_bytes()
    try:
        oracle_ir = adapter_fn(lf_bytes)
    except Exception as exc:
        return {"gate": GATE_ID, "case_id": case_id,
                "verdict": "MEASUREMENT_UNSATISFIABLE",
                "checks": {"oracle_adapter_success": False},
                "witness_sha256": "0" * 64,
                "detail": f"adapter: {type(exc).__name__}: {str(exc)[:120]}"}
    return check_oracle_ir(case_id, oracle_ir)
