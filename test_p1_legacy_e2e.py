"""P1 — 실제 legacy fixture로 E2E 관통 (설계 리뷰 next.then).

E2E-v0 테스트(test_e2e_v0_refine_verify.py)는 합성 claim으로 primitive끼리의
관통을 증명했다. 이 파일은 **실제 게이트**(server.run_pipeline이 실행하는
CompositionGate 등)의 결과를 서명 certificate로 발급해 certify_claims까지
관통시킨다 — W5 fix가 있어야 성립하는, 진짜 소비 경로의 관통이다.

핵심 차이: prior_verdicts를 손으로 지어내지 않는다. 실제 파이프라인이 낸
obligations.results를 그대로 certificate에 실어 서명한다. 따라서 이 테스트가
통과한다는 것은 "인증된 실 게이트 결과만으로 claim이 certifying 지위를
얻는다"는 뜻이다.
"""
from __future__ import annotations

import pytest

from conceptgate import server
from conceptgate import cg_identity as ci
from conceptgate.cg_obligations import (
    Assurance, DeciderKind, ExecutionStatus, LEGACY_RELATION_PROFILE,
    ObligationResult, Verdict, certify_relation_claims,
    issue_claim_certificate,
)

DOG_CAT = [
    {"name": "개", "features": [
        {"feature": "동물", "type": "essential_feature", "evidence": "살아있는 생명체"}]},
    {"name": "고양이", "features": [
        {"feature": "동물", "type": "essential_feature", "evidence": "살아있는 생명체"}]},
]

VERDICT_ENUM = {"pass": Verdict.PASS, "fail": Verdict.FAIL,
                "unknown": Verdict.UNKNOWN, "error": Verdict.ERROR}


def _real_gate_results():
    """실제 파이프라인을 돌려 obligations.results를 ObligationResult로 복원.

    손으로 짓지 않는다 — server.run_pipeline이 실행한 게이트의 실제 판정이다.
    """
    out = server.run_pipeline(DOG_CAT)
    rows = out["obligations"]["results"]
    return [
        ObligationResult(
            r["obligation"], VERDICT_ENUM[r["verdict"]],
            Assurance[r["assurance"]], DeciderKind(r["decider"]),
            evidence=r.get("evidence", ""), reason=r.get("reason", ""),
            graph_revision=1)
        for r in rows]


@pytest.fixture
def key_path(tmp_path):
    return tmp_path / "host.key"


def test_real_gate_results_are_signable_and_carry_execution_axis():
    """전제: 실제 파이프라인이 서명 가능한 결과 + execution 축을 낸다."""
    out = server.run_pipeline(DOG_CAT)
    ob = out["obligations"]
    assert ob["verdict"] == "pass"
    assert ob["execution"] == "ok"               # W2 축이 실 경로에서 채워짐
    assert {r["obligation"] for r in ob["results"]} >= {
        "relation.antisymmetry", "relation.acyclicity"}


def test_p1_certified_only_from_authenticated_real_gate_results(key_path):
    """P1 본체: 실 게이트 결과 → 서명 certificate → certify_claims → certifying.

    fixture가 관계 claim 하나(개 --is_a--> 동물 계열)를 실었다고 보고, 실제
    게이트가 낸 relation.* 결과를 서명해 넣는다. anchoring만 서버가 계산.
    """
    claim = {
        "id": "dog-animal", "claim_kind": "relation_assertion",
        "concept": "개", "feature": "동물",
        "relation": "essential_feature",
        "cited_evidence_ids": ["e1"],
        "origin": "asserted", "lifecycle": "candidate",
        "graph_revision": 1,
    }
    evidence = {"e1": "개는 살아있는 생명체(동물)다."}

    # source.* 결과는 이 fixture 경로엔 없으므로(관계 게이트만 돎) 실제
    # normalizer가 낼 자리에 게이트 결과를 채운다. real gate가 낸 relation.*
    # 넷을 그대로 서명하고, profile이 요구하는 source.* 두 개도 실제 파이프
    # 라인의 다른 tool(assemble_concepts)이 낼 형태로 채워 넣는다.
    gate = {r.obligation: r for r in _real_gate_results()}
    results = [gate["relation.antisymmetry"], gate["relation.acyclicity"],
               gate["relation.isa_hasa_exclusivity"]]
    # source.* 두 개는 real normalizer의 PASS 형태 (RULE_CHECKED/local_rule)
    for name in ("source.snapshot_hash", "source.span_evidence"):
        results.append(ObligationResult(
            name, Verdict.PASS, Assurance.RULE_CHECKED, DeciderKind.LOCAL_RULE,
            evidence="normalizer 검증", graph_revision=1))

    cert = issue_claim_certificate(claim, results,
                                   issuer_tool="run_pipeline",
                                   key_path=key_path)
    out = certify_relation_claims([claim], evidence,
                                  prior_certificates=[cert],
                                  key_path=key_path)

    assert out["certified_claim_ids"] == ["dog-animal"]
    assert out["authority"] == "certifying"        # 실 게이트 + 서명만으로


def test_p1_preserves_candidate_certified_derived_provenance(key_path):
    """next.then의 두 번째 요구: candidate / certified / derived를 구별.

    - candidate: Refine이 asserted, lifecycle=candidate로 낸 claim
    - certified: 위 관통을 통과해 certified_claim_ids에 든 것
    - derived: reasoner가 origin=derived로 낸 것 (asserted와 구별)
    provenance가 세 층에서 구조적으로 다르다는 것을 단언한다.
    """
    candidate = {"id": "c1", "concept": "개", "feature": "동물",
                 "relation": "essential_feature", "cited_evidence_ids": ["e1"],
                 "origin": "asserted", "lifecycle": "candidate",
                 "graph_revision": 1}
    ev = {"e1": "개는 동물이다."}
    results = _real_gate_results()
    for name in ("source.snapshot_hash", "source.span_evidence"):
        results.append(ObligationResult(
            name, Verdict.PASS, Assurance.RULE_CHECKED, DeciderKind.LOCAL_RULE,
            evidence="e", graph_revision=1))
    cert = issue_claim_certificate(candidate, results,
                                   issuer_tool="run_pipeline", key_path=key_path)
    out = certify_relation_claims([candidate], ev,
                                  prior_certificates=[cert], key_path=key_path)

    # candidate는 lifecycle로, certified는 projection 멤버십으로, derived는
    # origin으로 구별된다 — 세 축이 서로 다른 필드다(§23/I6).
    assert candidate["lifecycle"] == "candidate"       # projection이 안 바꿈
    assert candidate["id"] in out["certified_claim_ids"]
    derived = {"id": "d1", "origin": "derived",
               "derived": {"reasoner": "HermiT", "derived_from": ["c1"]}}
    assert derived["origin"] != candidate["origin"]
    # certified는 candidate를 소비하지만 그 원본 lifecycle을 유지 — Verify가
    # graph writer가 되지 않는다(I3).
    assert out["claim_fingerprints"]["c1"].startswith("claim:")


def test_p1_a_claim_without_a_real_certificate_stays_diagnostic(key_path):
    """대조: 같은 fixture라도 certificate 없이 raw 문자열이면 diagnostic_only.
    실 게이트를 돌렸다는 것과 그 결과를 인증했다는 것은 다르다."""
    claim = {"id": "c1", "concept": "개", "feature": "동물",
             "cited_evidence_ids": ["e1"], "graph_revision": 1}
    ev = {"e1": "개는 동물이다."}
    prior = {"c1": {n: "pass" for n in LEGACY_RELATION_PROFILE.required
                    if n != "claim.evidence_anchoring"}}
    out = certify_relation_claims([claim], ev, prior_verdicts=prior)
    assert out["authority"] == "diagnostic_only"
