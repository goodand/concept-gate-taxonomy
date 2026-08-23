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


# ---------------------------------------------------------------------------
# D-E2E-v1-24 Q24.1: FOLIO_LABEL_LOWERCASE_V1 — RED 먼저.
#
# smoke가 적발한 B1: FOLIO oracle 술어는 대문자/CamelCase로 남는데 template은
# subject에게 소문자를 강제 → 라벨 불일치만으로 fail. 판정은 FOLIO 한정
# 소문자화 codec만 허용(분절·동의어·lemma·병합 금지), PMB codec과 별도 유지,
# source(case_id 접두어)별 dispatch를 비교층에 요구했다.
# ---------------------------------------------------------------------------


def test_folio_profile_identity():
    assert prof.FOLIO_PROFILE_ID == "FOLIO_LABEL_LOWERCASE_V1"


def test_folio_casefold_positive():
    ir = EX("x", {"kind": "and", "args": [
        P("Zorble", V("x")), P("CanCatch", V("x"), V("x"))]})
    out = prof.normalize_folio_labels(ir)
    names = [a["name"] for a in out["body"]["args"]]
    assert names == ["zorble", "cancatch"]


def test_folio_no_lexical_substitution():
    """판정 §12 negative: Zorble ≠ Creature — codec은 어휘를 절대 바꾸지 않는다."""
    ir = EX("x", {"kind": "and", "args": [
        P("Zorble", V("x")), P("Creature", V("x"))]})
    out = prof.normalize_folio_labels(ir)
    names = [a["name"] for a in out["body"]["args"]]
    assert names == ["zorble", "creature"]
    assert names[0] != names[1]


def test_folio_no_camelcase_segmentation():
    """판정 §2: CamelCase 분절 금지 — 'CanCatch'는 'cancatch'이지 'can_catch'가 아니다."""
    out = prof.normalize_folio_labels(P("CanCatch", V("x"), V("x")))
    assert out["name"] == "cancatch"
    assert "_" not in out["name"] and " " not in out["name"]


def test_folio_preserves_reserved_true_token():
    """desugar는 중립 제한식을 name == "True" 문자열로 식별한다
    (_stage2_canonical_core.py). codec이 True를 소문자화하면 desugar가 중립형을
    재포장해 비교가 깨진다 — 예약 토큰은 codec을 통과해도 불변이어야 한다."""
    ir = EX("x", P("Glims", V("x")))          # EX의 restriction = P("True")
    out = prof.normalize_folio_labels(ir)
    assert out["restriction"]["name"] == "True"
    assert out["body"]["name"] == "glims"


def test_folio_structure_arity_topology_untouched():
    ir = EX("x", {"kind": "and", "args": [
        P("OnRoof", V("x")), {"kind": "not", "body": P("WentWrong", V("x"))}]})
    out = prof.normalize_folio_labels(ir)
    assert out["kind"] == "exists" and out["body"]["kind"] == "and"
    assert out["body"]["args"][1]["kind"] == "not"
    assert len(out["body"]["args"][0]["args"]) == 1


def test_folio_input_not_mutated_and_idempotent():
    import copy
    ir = EX("x", P("Zorble", V("x")))
    snapshot = copy.deepcopy(ir)
    once = prof.normalize_folio_labels(ir)
    assert ir == snapshot
    assert prof.normalize_folio_labels(once) == once


def test_folio_same_lowercased_names_stay_separate_nodes():
    """소문자화로 라벨이 충돌해도 노드 병합 금지 (판정 preserve: predicate_occurrence)."""
    ir = EX("x", {"kind": "and", "args": [
        P("Glims", V("x")), P("GLIMS", V("x"))]})
    out = prof.normalize_folio_labels(ir)
    assert len(out["body"]["args"]) == 2
    assert [a["name"] for a in out["body"]["args"]] == ["glims", "glims"]


# --- source별 dispatch (비교층 배선의 단일 진입점) ---


def test_dispatch_pmb_routes_to_synset_codec():
    out = prof.normalize_labels_for_case(
        "PMB-p09-d2243", P("Zorble.n.01", V("x")))
    assert out["name"] == "zorble"          # synset → lemma


def test_dispatch_folio_routes_to_casefold_codec():
    out = prof.normalize_labels_for_case(
        "FOLIO-175p1", P("Zorble.n.01", V("x")))
    assert out["name"] == "zorble.n.01"     # FOLIO codec은 lemma 추출이 아니라 소문자화만


def test_dispatch_unknown_prefix_refuses():
    """미지 source는 조용한 무정규화가 아니라 거부 — fail-closed.

    SMOKE-도 거부다: 코호트 비교층의 codec은 판정상 정확히 두 source
    (PMB·FOLIO)에 결박된다. smoke 하네스가 codec이 필요하면
    normalize_folio_labels를 직접 부른다 — dispatch를 넓히지 않는다
    (첫 위임 구현이 SMOKE- 분지를 임의 추가했다가 검수에서 제거된 이력)."""
    with pytest.raises(ValueError):
        prof.normalize_labels_for_case("WIKISEM-01", P("Zorble", V("x")))
    with pytest.raises(ValueError):
        prof.normalize_labels_for_case("SMOKE-01", P("Zorble", V("x")))
