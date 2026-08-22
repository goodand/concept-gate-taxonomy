"""W5 수정의 TDD 테스트 — 서명된 obligation certificate.

설계 리뷰(DESIGN_DECISION_refine_verify_v0_review.md)의 required_fix 4항을
테스트로 먼저 고정한다: receipt authenticity / subject fingerprint 결박 /
graph revision 결박 / decider·assurance 유효성. 음성 패턴 2종은 codex 선례
(test_a_hand_written_receipt_is_refused, test_an_edited_receipt_is_refused)의
변용이다.
"""
from __future__ import annotations

import pytest

from conceptgate import cg_identity as ci
from conceptgate.cg_obligations import (
    Assurance, CertificateError, DeciderKind, LEGACY_RELATION_PROFILE,
    ObligationResult, Verdict, certify_relation_claims,
    issue_claim_certificate,
)

CLAIM = {"id": "c1", "claim_kind": "relation_assertion",
         "concept": "엔진", "feature": "실린더",
         "relation": "structural_composition",
         "cited_evidence_ids": ["e1"], "graph_revision": 7}
EVIDENCE = {"e1": "엔진은 실린더를 포함한다."}


def _gate_results():
    """실제 게이트가 발급했을 결과의 형태 (registry에 실존하는 의무만)."""
    return [
        ObligationResult(name, Verdict.PASS, Assurance.RULE_CHECKED,
                         DeciderKind.LOCAL_RULE if name.startswith("source")
                         else DeciderKind.GATE,
                         evidence=f"{name}: 검사 통과", graph_revision=7)
        for name in LEGACY_RELATION_PROFILE.required
        if name != "claim.evidence_anchoring"
    ]


@pytest.fixture
def key_path(tmp_path):
    return tmp_path / "host.key"


def test_issued_certificate_certifies_and_promotes_authority(key_path):
    """정품 경로: 발급 → 검증 → 인증 + authority 승격."""
    cert = issue_claim_certificate(CLAIM, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path)
    out = certify_relation_claims([CLAIM], EVIDENCE,
                                  prior_certificates=[cert],
                                  key_path=key_path)
    assert out["certified_claim_ids"] == ["c1"]
    assert out["authority"] == "certifying"


def test_a_hand_written_certificate_is_refused(key_path):
    """조작 1: 서명 없는 손제작 certificate — codex 선례의 변용."""
    forged = {"issuer": {"tool": "run_pipeline", "verifier_version": "x"},
              "subject_fingerprint": ci.claim_fingerprint(CLAIM),
              "graph_revision": 7,
              "results": [{"obligation": n, "verdict": "pass",
                           "assurance": "RULE_CHECKED", "decider": "gate",
                           "evidence": "가짜"}
                          for n in LEGACY_RELATION_PROFILE.required]}
    with pytest.raises(CertificateError, match="signature"):
        certify_relation_claims([CLAIM], EVIDENCE,
                                prior_certificates=[forged],
                                key_path=key_path)


def test_a_certificate_edited_after_signing_is_refused(key_path):
    """조작 2: 서명 후 결과 변조 — 증거는 지우고 판정만 남기기."""
    results = _gate_results()
    # 하나를 FAIL로 발급받은 뒤, 서명된 문서에서 pass로 바꿔치기
    results[0] = ObligationResult(
        results[0].obligation, Verdict.FAIL, Assurance.RULE_CHECKED,
        results[0].decider, evidence="위반", reason="실측 위반", graph_revision=7)
    cert = issue_claim_certificate(CLAIM, results,
                                   issuer_tool="run_pipeline",
                                   key_path=key_path)
    cert["results"][0]["verdict"] = "pass"
    with pytest.raises(CertificateError, match="signature"):
        certify_relation_claims([CLAIM], EVIDENCE,
                                prior_certificates=[cert],
                                key_path=key_path)


def test_a_certificate_for_a_different_claim_is_refused(key_path):
    """결박 1: subject fingerprint 불일치 — 남의 인증서 재사용 차단."""
    other = dict(CLAIM, id="c2", concept="바퀴")
    cert = issue_claim_certificate(other, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path)
    with pytest.raises(CertificateError, match="subject"):
        certify_relation_claims([CLAIM], EVIDENCE,
                                prior_certificates=[cert],
                                key_path=key_path)


def test_a_certificate_for_a_stale_revision_is_refused(key_path):
    """결박 2: revision 불일치 — 옛 graph의 인증서로 새 graph를 인증 금지."""
    old_claim = dict(CLAIM, graph_revision=6)
    cert = issue_claim_certificate(old_claim, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path)
    # 같은 내용이 revision 7로 재조립됐다고 하자 — fingerprint가 달라지므로
    # subject에서 먼저 걸리지만, subject가 우연히 같아도 revision 검사가 있다.
    with pytest.raises(CertificateError):
        certify_relation_claims([CLAIM], EVIDENCE,
                                prior_certificates=[cert],
                                key_path=key_path)


def test_an_embedded_result_violating_assurance_caps_is_refused(key_path):
    """유효성: LLM decider가 RULE_CHECKED를 주장하는 결과가 서명돼 있어도
    거부 — 서명은 출처만 증명하지 내용의 권한 초과를 정당화하지 않는다."""
    bad = [ObligationResult("relation.is_a", Verdict.PASS,
                            Assurance.RULE_CHECKED, DeciderKind.LLM,
                            evidence="LLM이 그렇게 말함", graph_revision=7)]
    cert = issue_claim_certificate(CLAIM, bad, issuer_tool="run_pipeline",
                                   key_path=key_path)
    with pytest.raises(CertificateError, match="ASSURANCE_EXCEEDS_DECIDER_CAP"):
        certify_relation_claims([CLAIM], EVIDENCE,
                                prior_certificates=[cert],
                                key_path=key_path)


def test_raw_prior_verdict_strings_remain_diagnostic_only(key_path):
    """하위호환 경로: 문자열 prior는 여전히 받되 authority는 diagnostic_only —
    출처 미인증 입력이 권위를 얻는 경로는 존재하지 않는다."""
    prior = {"c1": {n: "pass" for n in LEGACY_RELATION_PROFILE.required
                    if n != "claim.evidence_anchoring"}}
    out = certify_relation_claims([CLAIM], EVIDENCE, prior_verdicts=prior)
    assert out["authority"] == "diagnostic_only"


def test_mixing_certificates_and_raw_strings_does_not_promote(key_path):
    """정품 인증서가 있어도 raw 문자열이 섞이면 승격하지 않는다 —
    가장 약한 입력이 전체의 지위를 정한다(fail-closed)."""
    cert = issue_claim_certificate(CLAIM, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path)
    out = certify_relation_claims([CLAIM], EVIDENCE,
                                  prior_certificates=[cert],
                                  prior_verdicts={"c1": {"relation.is_a": "pass"}},
                                  key_path=key_path)
    assert out["authority"] == "diagnostic_only"


def test_the_certificate_guard_fires_when_called_directly(key_path):
    """뮤테이션 게이트가 요구하는 직접 호출 — 공개 경로를 거친 검증만 있으면
    certify_relation_claims가 미래에 이 가드 호출을 빼먹어도 스위트가 초록일
    수 있다. 세 거부 사유(서명·subject·revision)를 가드에 직접 겨눈다."""
    from conceptgate.cg_obligations import _assert_certificate_grants_verdicts
    key = ci.load_or_create_key(key_path)

    with pytest.raises(CertificateError, match="signature"):
        _assert_certificate_grants_verdicts({"results": []}, CLAIM, key)

    good = issue_claim_certificate(CLAIM, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path)
    other = dict(CLAIM, id="c9", concept="바퀴")
    with pytest.raises(CertificateError, match="subject"):
        _assert_certificate_grants_verdicts(good, other, key)

    aged = dict(CLAIM)
    cert_aged = issue_claim_certificate(aged, _gate_results(),
                                        issuer_tool="run_pipeline",
                                        key_path=key_path)
    cert_aged_body = {k: v for k, v in cert_aged.items() if k != "signature"}
    cert_aged_body["graph_revision"] = 6
    resigned = {**cert_aged_body, "signature": ci.sign(
        cert_aged_body, key, domain="obligation-certificate")}
    # 서명은 유효(키 보유자가 재서명)하지만 revision이 claim과 어긋남 —
    # revision 결박이 서명과 독립으로 검사됨을 증명
    with pytest.raises(CertificateError, match="revision"):
        _assert_certificate_grants_verdicts(resigned, CLAIM, key)
