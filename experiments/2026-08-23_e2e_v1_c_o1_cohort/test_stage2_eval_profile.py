"""O1_PMB_LEMMA_NO_SENSE_V1 평가 profile의 TDD 계약 — RED 먼저.

D-E2E-v1-22 Q22.3(a*): WSD를 estimand 밖으로 — synset 술어명을 lemma·
소문자로 정규화하되 **occurrence 정체·arity·argument topology·scope 위치
보존, 동일 lemma 노드 병합 금지, 커널 전역 정규화 금지**(§9-§10).
end-to-end 리허설이 실측한 실패(표면형 vs 어간 불일치만으로 3/3 FAIL)를
죽이는 조각이다. 위치는 실험 폴더 — 커널이 아니다: 다른 실험에선 WSD가
estimand일 수 있다.
"""
from __future__ import annotations

import ast
import inspect
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

import _stage2_eval_profile as prof  # noqa: E402
from conceptgate import cg_evaluate, cg_ir, cg_sbn_adapter  # noqa: E402

V = lambda n: {"kind": "var", "name": n}
P = lambda name, *args: {"kind": "pred", "name": name, "args": list(args)}
EX = lambda v, body: {"kind": "exists", "var": v,
                      "restriction": P("True"), "body": body}


def test_profile_identity():
    assert prof.PROFILE_ID == "O1_PMB_LEMMA_NO_SENSE_V1"


def test_synset_names_become_lowercase_lemmas():
    ir = EX("x", {"kind": "and", "args": [
        P("Zorble.n.01", V("x")), P("glim.a.02", V("x")),
        P("zorble_krell.n.03", V("x"))]})
    out = prof.normalize_predicate_labels(ir)
    names = [a["name"] for a in out["body"]["args"]]
    assert names == ["zorble", "glim", "zorble_krell"]


def test_non_synset_names_untouched():
    """role·DRS-op·subject의 평문 이름은 synset 패턴이 아니다 — 불변."""
    ir = EX("x", {"kind": "and", "args": [
        P("zorble", V("x")), P("Agent", V("x"), V("x")),
        P("EQU", V("x"), {"kind": "entity", "name": "now"})]})
    out = prof.normalize_predicate_labels(ir)
    assert [a["name"] for a in out["body"]["args"]] == ["zorble", "Agent", "EQU"]


def test_same_lemma_different_sense_stays_two_nodes():
    """§9: sense 구별 무시 ≠ occurrence 정체 붕괴 — 병합 금지."""
    ir = {"kind": "and", "args": [P("zorble.n.01", V("x")),
                                  P("zorble.n.02", V("y"))]}
    out = prof.normalize_predicate_labels(ir)
    assert len(out["args"]) == 2
    assert out["args"][0]["name"] == out["args"][1]["name"] == "zorble"
    assert out["args"][0]["args"] != out["args"][1]["args"]  # 논항은 그대로


def test_structure_arity_topology_untouched():
    ir = {"kind": "forall", "var": "u", "restriction": P("tikk.n.01", V("u")),
          "body": EX("e", {"kind": "and", "args": [
              P("prax.v.02", V("e")), P("Theme", V("e"), V("u"))]})}
    out = prof.normalize_predicate_labels(ir)
    assert out["kind"] == "forall" and out["body"]["kind"] == "exists"
    assert out["body"]["body"]["args"][1]["args"] == [V("e"), V("u")]


def test_input_not_mutated_and_idempotent():
    ir = EX("x", P("zorble.n.01", V("x")))
    import copy; before = copy.deepcopy(ir)
    out = prof.normalize_predicate_labels(ir)
    assert ir == before, "입력 변이는 oracle IR 오염이다"
    assert prof.normalize_predicate_labels(out) == out


def test_kills_the_rehearsal_failure_shape():
    """리허설 실측 재현: oracle(원 synset, SBN adapter 경유) vs subject
    (lemma 평문) — profile 정규화 후 evaluate가 pass여야 한다."""
    oracle = cg_sbn_adapter.adapt_sbn("zorble.n.01\nglim.v.01 Agent -1")
    subject = EX("a", EX("b", {"kind": "and", "args": [
        P("zorble", V("a")), P("glim", V("b")),
        P("Agent", V("b"), V("a"))]}))
    raw = cg_evaluate.evaluate(subject, oracle)
    assert raw["result"] == "fail"          # 정규화 없이는 리허설과 같은 FAIL
    normalized = cg_evaluate.evaluate(
        prof.normalize_predicate_labels(subject),
        prof.normalize_predicate_labels(oracle))
    assert normalized["result"] == "pass", normalized


def test_profile_lives_outside_the_kernel():
    """§10: 커널 전역 정규화 금지 — 커널 모듈이 이 profile을 모르는지 AST로."""
    root = REPO / "conceptgate"
    for name in ("cg_ir.py", "cg_evaluate.py", "cg_identity.py",
                 "cg_sbn_adapter.py", "cg_oracle_adapter.py"):
        src = (root / name).read_text(encoding="utf-8")
        assert "_stage2_eval_profile" not in src
        assert "LEMMA_NO_SENSE" not in src


def test_profile_module_is_pure():
    tree = ast.parse(Path(inspect.getfile(prof)).read_text(encoding="utf-8"))
    imported = {a.name for n in ast.walk(tree) if isinstance(n, ast.Import)
                for a in n.names}
    imported |= {n.module for n in ast.walk(tree)
                 if isinstance(n, ast.ImportFrom) and n.module}
    assert imported <= {"__future__", "typing", "re", "copy"}, imported
