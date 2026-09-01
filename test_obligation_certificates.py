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
    issue_claim_certificate, _assert_certificate_grants_verdicts,
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
                                   key_path=key_path,
        profile=LEGACY_RELATION_PROFILE)
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
                                   key_path=key_path,
        profile=LEGACY_RELATION_PROFILE)
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
                                   key_path=key_path,
        profile=LEGACY_RELATION_PROFILE)
    with pytest.raises(CertificateError, match="subject"):
        certify_relation_claims([CLAIM], EVIDENCE,
                                prior_certificates=[cert],
                                key_path=key_path)


def test_a_certificate_for_a_stale_revision_is_refused(key_path):
    """결박 2: revision 불일치 — 옛 graph의 인증서로 새 graph를 인증 금지."""
    old_claim = dict(CLAIM, graph_revision=6)
    cert = issue_claim_certificate(old_claim, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path,
        profile=LEGACY_RELATION_PROFILE)
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
                                   key_path=key_path,
        profile=LEGACY_RELATION_PROFILE)
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
                                   key_path=key_path,
        profile=LEGACY_RELATION_PROFILE)
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
                                   key_path=key_path,
        profile=LEGACY_RELATION_PROFILE)
    other = dict(CLAIM, id="c9", concept="바퀴")
    with pytest.raises(CertificateError, match="subject"):
        _assert_certificate_grants_verdicts(good, other, key)

    aged = dict(CLAIM)
    cert_aged = issue_claim_certificate(aged, _gate_results(),
                                        issuer_tool="run_pipeline",
                                        key_path=key_path,
        profile=LEGACY_RELATION_PROFILE)
    cert_aged_body = {k: v for k, v in cert_aged.items() if k != "signature"}
    cert_aged_body["graph_revision"] = 6
    resigned = {**cert_aged_body, "signature": ci.sign(
        cert_aged_body, key, domain="obligation-certificate")}
    # 서명은 유효(키 보유자가 재서명)하지만 revision이 claim과 어긋남 —
    # revision 결박이 서명과 독립으로 검사됨을 증명
    with pytest.raises(CertificateError, match="revision"):
        _assert_certificate_grants_verdicts(resigned, CLAIM, key)


# ---------------------------------------------------------------------------
# 진단이 원인을 구별한다 — 2026-09-01, E2E MVP 가 드러낸 요구사항 #2
# ---------------------------------------------------------------------------
#
# 이 문구를 내는 원인이 **4종**인데 전부 같은 말을 했다(실측): 서명 필드 부재 ·
# 서명 변조 · 본문 변조 · **키 불일치(문서는 정당)**. 넷째만 성격이 다르다 —
# 문서가 부정한 것이 아니라 **검증자가 다른 키를 들고 온 것**이다. E2E MVP 를
# 조립할 때 이것 때문에 헤맸고, 그 사실이 이미 두 곳에 기록돼 있었는데
# (`test_e2e_mvp_file_to_certified.py` docstring · `HANDOFF.md`) 처분이
# "테스트로 요구를 고정"에서 멈춰 있었다.
#
# 선례를 따른다 — `2c8df63`("오류 메시지가 자기 키를 말하게")의 형태:
# **읽은 것 + 받은 것 + 두 어휘층의 대응**을 넣고 값·시크릿은 넣지 않았다.
# 여기서 검증부가 읽은 것은 **키 파일**이다.
#
# oracle 규율(`:986` "조작 진행도를 알려주는 oracle")은 **위반하지 않는다**:
# 발원 커밋 원문이 oracle 을 "an oracle for how far a forgery got" 으로 좁게
# 정의하고, 키 경로는 **문서의 함수가 아니라 호스트 설정의 함수**여서 어떤
# 위조 문서에도 같은 값이 나온다 — 진행도를 한 비트도 전달하지 않는다.
# 그리고 같은 모듈이 이미 키 파일명을 오류에 넣는다(`cg_identity.py:150`).
# 전체 경로가 아니라 `path.name` 만 쓴다 — `str(exc)` 가 MCP client 로
# 나가므로(`server.py:898`) 홈디렉터리·사용자명을 흘리지 않기 위해서다.


def test_the_signature_failure_names_the_key_it_verified_with(tmp_path, key_path):
    """문구가 **검증에 쓴 키 파일명**을 말한다 — 없으면 "손으로 쓴 문서"라는
    단정만 남아서, 정당한 문서를 다른 키로 검증한 사람이 원인을 못 찾는다."""
    cert = issue_claim_certificate(CLAIM, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path,
                                   profile=LEGACY_RELATION_PROFILE)
    other = tmp_path / "다른키.json"
    with pytest.raises(CertificateError) as exc:
        _assert_certificate_grants_verdicts(
            cert, CLAIM, ci.load_or_create_key(other),
            key_source=other.name)
    assert other.name in str(exc.value)


def test_the_signature_failure_offers_the_key_mismatch_hypothesis(tmp_path, key_path):
    """원인을 **두 가설로 병렬 제시**해야 오진이 사라진다 — 경로만 붙이면
    문구는 여전히 "손으로 쓴 문서"를 단정한다(선례의 `fix` 필드가 한 일)."""
    cert = issue_claim_certificate(CLAIM, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path,
                                   profile=LEGACY_RELATION_PROFILE)
    with pytest.raises(CertificateError) as exc:
        _assert_certificate_grants_verdicts(
            cert, CLAIM, ci.load_or_create_key(tmp_path / "o.json"),
            key_source="o.json")
    msg = str(exc.value)
    assert "different key" in msg or "다른 키" in msg
    assert "signature" in msg            # 기존 계약 5건이 이 단어에 걸려 있다


def test_the_diagnostic_does_not_leak_the_absolute_path(tmp_path, key_path):
    """`str(exc)` 가 MCP client 로 나가므로(`server.py:898`) 홈디렉터리·
    사용자명이 딸린 절대경로를 넣지 않는다 — `cg_identity.py:150` 이 이미
    `path.name` 만 쓰는 그 선례를 따른다."""
    cert = issue_claim_certificate(CLAIM, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path,
                                   profile=LEGACY_RELATION_PROFILE)
    other = tmp_path / "비밀디렉터리" / "k.json"
    other.parent.mkdir(parents=True, exist_ok=True)
    with pytest.raises(CertificateError) as exc:
        _assert_certificate_grants_verdicts(
            cert, CLAIM, ci.load_or_create_key(other),
            key_source=other.name)
    assert "비밀디렉터리" not in str(exc.value)
    assert str(tmp_path) not in str(exc.value)


def test_key_source_is_optional_so_existing_callers_keep_working(key_path):
    """가산 도입 — `key_source` 를 주지 않는 호출자(19곳 계열)가 그대로
    돈다. 없으면 문구에서 키 절만 빠진다."""
    cert = issue_claim_certificate(CLAIM, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path,
                                   profile=LEGACY_RELATION_PROFILE)
    granted = _assert_certificate_grants_verdicts(
        cert, CLAIM, ci.load_or_create_key(key_path))
    assert granted["source.snapshot_hash"] is Verdict.PASS


def test_the_authenticity_check_stays_first(tmp_path, key_path):
    """**순서 계약 불변**(`:986` "authenticity 먼저"). 키 절을 더해도
    서명 실패가 결박 검사보다 먼저 보고되어야 한다 — 다른 claim 의
    인증서를 다른 키로 넣으면 subject 오류가 아니라 signature 오류다."""
    cert = issue_claim_certificate(CLAIM, _gate_results(),
                                   issuer_tool="run_pipeline",
                                   key_path=key_path,
                                   profile=LEGACY_RELATION_PROFILE)
    other_claim = dict(CLAIM, claim_id="c2", id="c2")
    with pytest.raises(CertificateError) as exc:
        _assert_certificate_grants_verdicts(
            cert, other_claim, ci.load_or_create_key(tmp_path / "o.json"),
            key_source="o.json")
    assert "signature" in str(exc.value)
    assert "subject" not in str(exc.value)
