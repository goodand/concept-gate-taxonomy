"""D-E2E-v1-25 Q25.4: MEASUREMENT_SATISFIABILITY_V1 — RED 먼저.

게이트가 검사하는 것은 "모델이 잘 맞힐 것인가"가 아니라 **"허용된 subject
언어 안에 이 fixture를 PASS시키는 출력이 최소 1개 존재하는가"**다(판정 §20-21).

witness 정리(판정 §22의 결정론 구현): `projection(oracle)` 자체가 subject
schema에 valid하면 그것이 곧 존재 증인이다 — projection이 idempotent이므로
`project(witness) == project(oracle)`이고, evaluate 왕복까지 PASS면 충족.
LLM 불요, 숨김 유지.

경계(판정 §23): witness는 절대 model-facing이 아니다 — 게이트 기록에는
witness의 **sha256만** 남기고 식 내용은 어떤 산출물에도 넣지 않는다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

import _stage2_satisfiability as sat  # noqa: E402

V = lambda n: {"kind": "var", "name": n}
P = lambda name, *args: {"kind": "pred", "name": name, "args": list(args)}
FA = lambda v, r, b: {"kind": "forall", "var": v, "restriction": r, "body": b}
EX = lambda v, r, b: {"kind": "exists", "var": v, "restriction": r, "body": b}
AND = lambda *a: {"kind": "and", "args": list(a)}
NOT = lambda b: {"kind": "not", "body": b}
T = P("True")

DAVIDSONIAN = NOT(FA("x0", P("child.n.01", V("x0")),
                     EX("x2", T, AND(P("apple.n.01", V("x2")),
                        EX("x1", T, AND(P("like.v.03", V("x1")),
                           P("Experiencer", V("x1"), V("x0")),
                           P("Stimulus", V("x1"), V("x2"))))))))


def test_gate_identity():
    assert sat.GATE_ID == "MEASUREMENT_SATISFIABILITY_V1"


def test_pmb_davidsonian_oracle_is_satisfiable_under_v3():
    """V2에서 15/15를 죽였던 바로 그 형태가 V3 projection 아래서는 SATISFIABLE
    — 이 게이트가 F3을 freeze 전에 잡았을 방식의 역방향 확인(판정 §24-25)."""
    rec = sat.check_oracle_ir("PMB-p15-t", DAVIDSONIAN)
    assert rec["verdict"] == "SATISFIABLE"
    checks = rec["checks"]
    for k in ("oracle_projection_success", "subject_schema_valid",
              "hidden_witness_can_score_PASS", "no_unsupported_scored_operator"):
        assert checks[k] is True, k


def test_unsupported_operator_in_projection_is_unsatisfiable():
    """projection 산출에 subject 방언 밖 연산자가 남으면 UNSAT —
    §26 no_unsupported_scored_operator의 음성."""
    bad = {"kind": "or", "args": [P("A", V("x")), P("B", V("x"))]}
    ir = FA("x", T, bad)
    rec = sat.check_oracle_ir("FOLIO-9t", ir)
    assert rec["verdict"] == "MEASUREMENT_UNSATISFIABLE"
    assert rec["checks"]["no_unsupported_scored_operator"] is False \
        or rec["checks"]["subject_schema_valid"] is False


def test_record_never_contains_witness_or_oracle_formula():
    """유출 방지 — 기록에는 해시만, 식 내용(kind/pred/var 구조)은 0바이트."""
    rec = sat.check_oracle_ir("PMB-p15-t", DAVIDSONIAN)
    s = json.dumps(rec, ensure_ascii=False)
    for token in ('"kind"', '"forall"', '"pred"', "child.n.01", "Experiencer", "□"):
        assert token not in s, token
    assert len(rec["witness_sha256"]) == 64


def test_adapter_failure_is_unsatisfiable_not_crash():
    def boom(_):
        raise ValueError("adapter refused")
    rec = sat.check_fixture_entry(
        {"case_id": "FOLIO-8t", "lf_sha256": "0" * 64}, cache_dir=None,
        adapter_fn=boom, lf_bytes=b"junk")
    assert rec["verdict"] == "MEASUREMENT_UNSATISFIABLE"
    assert rec["checks"]["oracle_adapter_success"] is False


def test_unknown_prefix_refuses():
    import pytest
    with pytest.raises(ValueError):
        sat.check_oracle_ir("WIKISEM-1", FA("x", T, P("a", V("x"))))
