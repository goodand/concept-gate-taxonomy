#!/usr/bin/env python3
"""cg_obligations CI 불변조건 — 결정론 세탁이 구조적으로 불가능함을 계약."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from conceptgate.cg_obligations import (
    MAX_ASSURANCE, OBLIGATION_REGISTRY, Assurance, DeciderKind,
    ObligationResult, Verdict, aggregate, certify,
    results_from_classification, results_from_pipeline, validate_result,
)


def _r(obligation="source.span_evidence", verdict=Verdict.PASS,
       assurance=Assurance.RULE_CHECKED, decider=DeciderKind.LOCAL_RULE,
       evidence="cg_normalizer.py:170", **kw):
    return ObligationResult(obligation, verdict, assurance, decider,
                            evidence=evidence, **kw)


# ── CI 불변조건 (결정론 세탁 차단 계약) ──────────────────────

def test_every_obligation_has_complete_spec():
    assert OBLIGATION_REGISTRY, "registry가 비어 있으면 안 됨"
    for name, spec in OBLIGATION_REGISTRY.items():
        assert spec.handler, f"{name}: handler 미지정"
        assert spec.min_assurance <= MAX_ASSURANCE[spec.decider], \
            f"{name}: decider가 도달 불가능한 min_assurance"


def test_llm_cannot_issue_verified_assurance():
    assert MAX_ASSURANCE[DeciderKind.LLM] == Assurance.SOURCE_ANCHORED


def test_every_decider_kind_has_cap():
    assert set(MAX_ASSURANCE) == set(DeciderKind)


def test_pass_requires_minimum_assurance():
    low = _r(assurance=Assurance.PROPOSED)
    codes = {e["code"] for e in validate_result(low)}
    assert "INSUFFICIENT_ASSURANCE" in codes


def test_assurance_cannot_exceed_decider_cap():
    laundered = _r(assurance=Assurance.REASONER_PROVED)  # local_rule이 reasoner 보증 참칭
    codes = {e["code"] for e in validate_result(laundered)}
    assert "ASSURANCE_EXCEEDS_DECIDER_CAP" in codes


def test_llm_pass_on_rule_checked_obligation_is_rejected():
    # LLM이 RULE_CHECKED 의무를 PASS 시도 → decider 불일치 + 보증 부족 동시 검출
    r = ObligationResult("source.span_evidence", Verdict.PASS,
                         Assurance.SOURCE_ANCHORED, DeciderKind.LLM,
                         evidence="span:42")
    codes = {e["code"] for e in validate_result(r)}
    assert "DECIDER_MISMATCH" in codes and "INSUFFICIENT_ASSURANCE" in codes


def test_unknown_obligation_rejected():
    r = _r(obligation="ghost.obligation")
    assert validate_result(r)[0]["code"] == "UNKNOWN_OBLIGATION"


def test_pass_without_evidence_rejected():
    r = _r(evidence="")
    codes = {e["code"] for e in validate_result(r)}
    assert "MISSING_EVIDENCE" in codes


def test_valid_result_has_no_errors():
    assert validate_result(_r()) == []


# ── 집계 의미론 ──────────────────────────────────────────

def test_aggregate_all_semantics():
    p, f, u = (_r(), _r(verdict=Verdict.FAIL, evidence=""),
               _r(verdict=Verdict.UNKNOWN, evidence=""))
    assert aggregate([p, p]) is Verdict.PASS
    assert aggregate([p, f, u]) is Verdict.FAIL     # FAIL 지배
    assert aggregate([p, u]) is Verdict.UNKNOWN     # UNKNOWN은 PASS 차단
    assert aggregate([]) is Verdict.UNKNOWN         # 공집합은 통과 아님


def test_certify_blocks_on_any_violation():
    ok = certify([_r()])
    assert ok["ok"] and ok["verdict"] == "pass" and ok["errors"] == []
    bad = certify([_r(), _r(assurance=Assurance.PROPOSED)])
    assert not bad["ok"] and bad["verdict"] == "fail"
    assert bad["errors"][0]["obligation"] == "source.span_evidence"


def test_depends_on_recorded_as_provenance():
    r = _r(depends_on=("claim:42", "obl:81"))
    out = certify([r])
    assert out["results"][0]["depends_on"] == ["claim:42", "obl:81"]


# ── 파이프라인 어댑터 (배선) ──────────────────────────────

def test_pipeline_adapter_clean_output_all_pass():
    results = results_from_pipeline(
        {"composition_issues": [], "anti_patterns": []})
    assert {r.obligation for r in results} == {
        "relation.antisymmetry", "relation.acyclicity",
        "relation.isa_hasa_exclusivity", "ufo.no_antipattern"}
    cert = certify(results)
    assert cert["ok"] and cert["verdict"] == "pass" and cert["errors"] == []


def test_pipeline_adapter_maps_issue_kinds_to_obligations():
    results = results_from_pipeline({
        "composition_issues": [
            {"kind": "antisymmetry", "detail": "A⊃B 와 B⊃A 동시"},
            {"kind": "cycle", "detail": "A 순환"},
        ],
        "anti_patterns": [{"kind": "MixRig"}],
    })
    by = {r.obligation: r for r in results}
    assert by["relation.antisymmetry"].verdict is Verdict.FAIL
    assert by["relation.acyclicity"].verdict is Verdict.FAIL
    assert by["relation.isa_hasa_exclusivity"].verdict is Verdict.PASS
    assert by["ufo.no_antipattern"].verdict is Verdict.FAIL
    assert certify(results)["verdict"] == "fail"
    # 모든 결과가 registry 불변조건을 통과해야 함 (어댑터 자체의 세탁 방지)
    for r in results:
        assert validate_result(r) == []


# ── 분류 어댑터 (배선) ───────────────────────────────────

def test_classification_adapter_pass_and_fail():
    [ok] = results_from_classification({"ok": True, "unsatisfiable": []})
    assert (ok.verdict, ok.assurance) == (
        Verdict.PASS, Assurance.REASONER_PROVED)
    assert validate_result(ok) == []
    [bad] = results_from_classification(
        {"ok": True, "unsatisfiable": ["Ghost"]})
    assert bad.verdict is Verdict.FAIL and "Ghost" in bad.reason


def test_classification_adapter_unavailable_is_unknown_not_pass():
    # Java 없는 기본 Render 경로 — '판정 안 됨'이 '통과'로 세탁되면 안 됨
    [r] = results_from_classification(
        {"ok": False, "errors": [{"code": "REASONER_UNAVAILABLE"}]})
    assert r.verdict is Verdict.UNKNOWN
    assert r.assurance is Assurance.PROPOSED  # 증명 보증 참칭 금지
    cert = certify([r])
    assert not cert["ok"] and cert["verdict"] == "unknown"
