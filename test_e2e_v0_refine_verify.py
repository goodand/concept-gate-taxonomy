"""E2E-v0 — Refine/Verify 지시 §25의 최소 관통 + 신규 primitive의 음성 검증.

이 파일이 §31-F의 산출물이다: 기존 ConceptGate 자산을 새 authority contract
아래에서 Source → Candidate → Verify → Obligation → Repair → Certified →
기존 projection까지 관통시키고, 각 전이마다 누가 상태를 썼고(authority)
provenance가 무엇인지 단언한다.

Refine 자리는 하드코딩된 stand-in이다 — 프로덕션에서 Refine은 MCP 클라이언트
LLM이고(gap 분석 §1), 이 테스트가 검사하는 것은 그 주위의 계약이지 생성
품질이 아니다.
"""
from __future__ import annotations

import pytest

from conceptgate import cg_identity as ci
from conceptgate.cg_obligations import (
    Assurance, CertificationProfile, DeciderKind, LEGACY_RELATION_PROFILE,
    ObligationResult, Verdict, aggregate, certification_cycle, certify,
    certified_projection, is_certified, results_from_claim_anchoring,
    stale_obligations, validate_result,
)


# ---------------------------------------------------------- D1: ERROR -----

def test_error_verdict_blocks_pass_in_aggregate():
    """돌지 못한 검사를 통과로 세탁하지 않는다 (I8)."""
    ok = ObligationResult("relation.acyclicity", Verdict.PASS,
                          Assurance.RULE_CHECKED, DeciderKind.GATE, evidence="e")
    err = ObligationResult("owl.consistent", Verdict.ERROR,
                           Assurance.PROPOSED, DeciderKind.REASONER,
                           reason="HermiT timeout")
    assert aggregate([ok, err]) is Verdict.ERROR


def test_fail_outranks_error():
    """확정된 위반은 도구 고장보다 강한 사실이다."""
    bad = ObligationResult("relation.acyclicity", Verdict.FAIL,
                           Assurance.RULE_CHECKED, DeciderKind.GATE,
                           evidence="cycle", reason="A->B->A")
    err = ObligationResult("owl.consistent", Verdict.ERROR,
                           Assurance.PROPOSED, DeciderKind.REASONER,
                           reason="crash")
    assert aggregate([bad, err]) is Verdict.FAIL


def test_error_without_reason_is_invalid():
    """음성: 이유 없는 ERROR는 재실행 판단 근거를 잃는다."""
    err = ObligationResult("owl.consistent", Verdict.ERROR,
                           Assurance.PROPOSED, DeciderKind.REASONER)
    codes = [e["code"] for e in validate_result(err)]
    assert "ERROR_WITHOUT_REASON" in codes


# ------------------------------------------------- D3: 인증 의존 순환 -----

def _r(name, depends_on=()):
    return ObligationResult(name, Verdict.PASS, Assurance.RULE_CHECKED,
                            DeciderKind.GATE, evidence="e",
                            depends_on=tuple(depends_on))


def test_certification_cycle_is_detected_and_fails_certify():
    """음성(I10): C는 D 때문, D는 C 때문 — 자기부양 인증은 무효."""
    results = [_r("a", ["b"]), _r("b", ["a"])]
    assert set(certification_cycle(results)) == {"a", "b"}
    cert = certify(results, registry={
        "a": _spec(), "b": _spec()})
    assert cert["verdict"] == "fail"
    assert any(e["code"] == "CERTIFICATION_CYCLE" for e in cert["errors"])


def test_acyclic_dependencies_pass():
    """정밀도: 무조건 우는 검출기는 위 음성 테스트를 공허하게 통과한다."""
    results = [_r("a"), _r("b", ["a"]), _r("c", ["a", "b"])]
    assert certification_cycle(results) == []


def test_dependency_outside_presented_set_is_not_an_edge():
    """제시 집합 밖 참조는 이 호출의 판정 범위 밖 — 순환으로 세지 않는다."""
    assert certification_cycle([_r("a", ["ghost"])]) == []


def _spec():
    from conceptgate.cg_obligations import ObligationSpec
    return ObligationSpec(DeciderKind.GATE, Assurance.RULE_CHECKED,
                          "test", Verdict.UNKNOWN)


# ------------------------------------------------- D5: revision 결박 ------

def test_stale_obligations_are_named_and_none_revision_is_not_stale():
    cur = ObligationResult("a", Verdict.UNKNOWN, Assurance.PROPOSED,
                           DeciderKind.GATE, reason="r", graph_revision=17)
    old = ObligationResult("b", Verdict.UNKNOWN, Assurance.PROPOSED,
                           DeciderKind.GATE, reason="r", graph_revision=16)
    legacy = ObligationResult("c", Verdict.UNKNOWN, Assurance.PROPOSED,
                              DeciderKind.GATE, reason="r")  # revision 없음
    assert stale_obligations([cur, old, legacy], current_revision=17) == ["b"]


# ------------------------------------------------- D7: profile ------------

def test_profile_rejects_required_and_na_overlap():
    """음성: 같은 검사가 필수이면서 면제일 수 없다."""
    with pytest.raises(ValueError, match="동시에"):
        CertificationProfile("bad", "relation_assertion",
                             required=("x",), allowed_na=("x",))


def test_the_overlap_guard_fires_when_called_directly():
    """뮤테이션 게이트가 요구하는 직접 호출."""
    from conceptgate.cg_obligations import _assert_no_required_allowed_na_overlap
    bad = CertificationProfile("ok", "relation_assertion", required=("x",))
    object.__setattr__(bad, "allowed_na", ("x",))  # frozen dataclass 우회
    with pytest.raises(ValueError, match="동시에"):
        _assert_no_required_allowed_na_overlap(bad)


def test_missing_check_is_not_pass():
    """없는 검사 ≠ 통과 — is_certified의 기본값이 UNKNOWN인 이유."""
    prof = CertificationProfile("p", "relation_assertion", required=("a", "b"))
    assert not is_certified(prof, {"a": Verdict.PASS})
    assert is_certified(prof, {"a": Verdict.PASS, "b": Verdict.PASS})
    assert not is_certified(prof, {"a": Verdict.PASS, "b": Verdict.ERROR})


# =================================================== E2E-v0 (§25) ==========

FIXTURE = {
    # 기존 H1a 계열 fixture 형태 그대로: concept · feature · evidence 2건
    "concept": "칼", "feature": "철",
    "evidence": {
        "ev1": "문서: 철은 칼의 재료이며 본질적 특성이다 (essential_feature).",
        "ev3": "코드: 칼-철 관계는 structural_composition으로 등록된다.",
    },
}


def test_e2e_v0_source_to_certified_projection():
    # [1] Source snapshot — 기존 canonical 기능 재사용. 쓴 주체: 없음(읽기).
    snapshot_sha = ci.canonical_sha256(FIXTURE)
    assert snapshot_sha

    # [2] Refine(stand-in)이 candidate claim을 쓴다.
    #     authority: Refine만 asserted graph를 쓴다(I2).
    #     provenance: origin=asserted, lifecycle=candidate (§23).
    claim = {
        "id": "c1", "claim_kind": "relation_assertion",
        "concept": "칼", "feature": "철",
        "relation": "structural_composition",
        "cited_evidence_ids": ["ev1"],          # 일부러 하나만 — 수리 대상
        "origin": "asserted", "lifecycle": "candidate",
        "graph_revision": 1,
    }
    graph_r1 = {"revision": 1, "claims": [claim]}
    fp_r1 = ci.graph_fingerprint(graph_r1)

    # [3] Verify — graph를 쓰지 않는다(I3). 판정만 낸다.
    verdicts = {r.obligation: r for r in results_from_claim_anchoring(
        [claim], FIXTURE["evidence"])}
    anchoring = verdicts["claim.evidence_anchoring"]
    # ev1엔 '철'과 '칼'이 등장하므로 anchoring 자체는 PASS지만,
    # 나머지 required 검사가 없으므로 인증은 불가여야 한다.
    assert anchoring.verdict is Verdict.PASS

    # [4] Obligation — atomic, revision 결박(§16). patch 없음(I11).
    obligation = ObligationResult(
        "source.span_evidence", Verdict.UNKNOWN, Assurance.PROPOSED,
        DeciderKind.LOCAL_RULE,
        reason="ev3 미인용: 충돌 출처가 인용되지 않아 span 검증 불완전",
        graph_revision=1)
    assert stale_obligations([obligation], current_revision=1) == []

    # [5] Repair 1회 — Refine이 **새 revision**을 만든다. r1은 불변(I1/§6).
    repaired = dict(claim, cited_evidence_ids=["ev1", "ev3"], graph_revision=2)
    graph_r2 = {"revision": 2, "parent_revision": 1, "claims": [repaired]}
    assert ci.graph_fingerprint(graph_r2) != fp_r1          # 진짜 새 상태
    assert ci.graph_fingerprint(graph_r1) == fp_r1          # r1 무변경 증명
    # stale 거부(§4.2): r1의 obligation은 r2에 적용하지 않는다.
    assert stale_obligations([obligation], current_revision=2) == \
        ["source.span_evidence"]

    # [6] Certified Projection — profile.required 전부 PASS인 claim만.
    all_pass = {name: Verdict.PASS for name in LEGACY_RELATION_PROFILE.required}
    incomplete = dict(all_pass, **{"relation.acyclicity": Verdict.UNKNOWN})
    assert certified_projection([repaired], {"c1": incomplete},
                                LEGACY_RELATION_PROFILE) == []
    certified = certified_projection([repaired], {"c1": all_pass},
                                     LEGACY_RELATION_PROFILE)
    assert certified == [repaired]
    # projection은 view다 — 입력 dict를 변경하지 않는다(I3).
    assert repaired["lifecycle"] == "candidate"

    # [7]-[9] 기존 subsystem·유도·provenance: certified만 하류로.
    #     derived claim은 origin으로 구별(§23) — lifecycle 재사용 아님.
    derived = {"id": "d1", "origin": "derived",
               "derived": {"reasoner": "HermiT", "derived_from": ["c1"]}}
    assert derived["origin"] != repaired["origin"]
    assert {c["id"] for c in certified} == {"c1"}


def test_anchoring_absence_is_unknown_not_fail():
    """음성 + I9: 어휘 부재는 의미적 비지지의 증명이 아니다 — UNKNOWN."""
    claim = {"id": "c2", "concept": "칼", "feature": "청동",
             "cited_evidence_ids": ["ev1"]}
    [r] = results_from_claim_anchoring([claim], FIXTURE["evidence"])
    assert r.verdict is Verdict.UNKNOWN
    assert "청동" in r.reason


def test_anchoring_with_no_cited_evidence_is_unknown():
    claim = {"id": "c3", "concept": "칼", "feature": "철",
             "cited_evidence_ids": []}
    [r] = results_from_claim_anchoring([claim], FIXTURE["evidence"])
    assert r.verdict is Verdict.UNKNOWN


# ====================================== 배선(W1 해소): certify_relation_claims

from conceptgate.cg_obligations import (  # noqa: E402
    _assert_prior_verdicts_are_well_formed, certify_relation_claims,
)

CLAIMS = [{
    "id": "c1", "claim_kind": "relation_assertion",
    "concept": "칼", "feature": "철",
    "relation": "structural_composition",
    "cited_evidence_ids": ["ev1"], "graph_revision": 2,
}]
EVIDENCE = {"ev1": "문서: 철은 칼의 재료다."}


def test_orchestrator_without_prior_verdicts_certifies_nothing():
    """'검사 안 됨'은 '통과'가 아니다 — prior 없이 anchoring만으로는
    required의 나머지가 전부 UNKNOWN이므로 인증 0건이 정상이다."""
    out = certify_relation_claims(CLAIMS, EVIDENCE)
    assert out["certified_claim_ids"] == []
    assert out["verdicts_by_claim"]["c1"]["claim.evidence_anchoring"] == "pass"


def test_orchestrator_with_full_prior_verdicts_certifies():
    from conceptgate.cg_obligations import LEGACY_RELATION_PROFILE
    prior = {"c1": {name: "pass" for name in LEGACY_RELATION_PROFILE.required
                    if name != "claim.evidence_anchoring"}}
    out = certify_relation_claims(CLAIMS, EVIDENCE, prior_verdicts=prior)
    assert out["certified_claim_ids"] == ["c1"]
    assert out["claim_fingerprints"]["c1"].startswith("claim:")


def test_orchestrator_rejects_malformed_prior_verdict_strings():
    """음성(신뢰 경계): enum 밖 문자열은 UNKNOWN으로 눙치지도, PASS로
    관대하게 읽지도 않고 거부한다 — 전자는 디버깅 불가, 후자는 세탁."""
    with pytest.raises(ValueError, match="verdict 문자열"):
        certify_relation_claims(
            CLAIMS, EVIDENCE, prior_verdicts={"c1": {"relation.acyclicity": "pss"}})


def test_the_prior_verdict_guard_fires_when_called_directly():
    """뮤테이션 게이트가 요구하는 직접 호출."""
    with pytest.raises(ValueError, match="verdict 문자열"):
        _assert_prior_verdicts_are_well_formed({"c1": {"x": "maybe"}})


def test_orchestrator_reports_stale_anchoring_against_current_revision():
    out = certify_relation_claims(CLAIMS, EVIDENCE, current_revision=3)
    assert out["stale_anchoring_obligations"] == ["claim.evidence_anchoring"]
    out2 = certify_relation_claims(CLAIMS, EVIDENCE, current_revision=2)
    assert out2["stale_anchoring_obligations"] == []
