"""서버측 certificate 발급 orchestration의 TDD 테스트.

P1이 남긴 마지막 공백의 해소: P1 테스트는 source.* 자리를 손으로 채웠다.
이 파일의 기준은 **손으로 채우는 verdict 0** — snapshot부터 인증까지 전부
서버 in-process 계산이며, 클라이언트가 공급하는 것은 원문 텍스트와 claim뿐.
(클라이언트가 normalizer '응답'을 공급하는 설계는 W5의 재판이 된다 —
응답 조작이 곧 laundering이므로, 발급 도구는 bundle을 받아 직접 계산한다.)
"""
from __future__ import annotations

import pytest

from conceptgate import cg_normalizer as N
from conceptgate import server
from conceptgate.cg_obligations import (
    CertificateError, certify_relation_claims,
)

TEXT = ("개는 갯과의 가축화된 동물이다. 고양이는 고양잇과의 동물이다. "
        "말은 초식 동물이다.")


def _span(t, phrase):
    i = t.find(phrase)
    assert i >= 0, phrase
    return {"start": i, "end": i + len(phrase)}


def _bundle():
    snap = N.make_snapshot(TEXT, uri="local:test")["snapshot"]
    t = snap["text"]
    return {"snapshot": snap, "concepts": [
        {"name": "동물", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(t, "가축화된 동물이다")}]},
        {"name": "개", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(t, "가축화된 동물이다")},
            {"label": "갯과", "relation": "is_a",
             "evidence_span": _span(t, "갯과의 가축화된")}]},
        {"name": "고양이", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(t, "가축화된 동물이다")},
            {"label": "고양잇과", "relation": "is_a",
             "evidence_span": _span(t, "고양잇과의 동물")}]},
    ]}


CLAIM = {"id": "dog-animal", "claim_kind": "relation_assertion",
         "concept": "개", "feature": "동물", "relation": "is_a",
         "cited_evidence_ids": ["e1"],
         "origin": "asserted", "lifecycle": "candidate",
         "graph_revision": 1}
EVIDENCE = {"e1": "개는 갯과의 가축화된 동물이다."}


@pytest.fixture
def key_env(tmp_path, monkeypatch):
    kp = tmp_path / "host.key"
    monkeypatch.setenv("CONCEPTGATE_KEY_PATH", str(kp))
    return kp


def test_full_loop_with_zero_hand_filled_verdicts(key_env):
    """THE 테스트: snapshot → 서버 발급 → certify_claims → certifying.

    P1 테스트와의 차이가 이 파일의 존재 이유다 — source.*를 포함한 모든
    verdict가 서버 in-process 계산에서 나오고, 손으로 채운 것이 없다.
    """
    out = server.issue_claim_certificates([CLAIM], _bundle())
    assert out["ok"], out
    certs = out["certificates"]
    assert len(certs) == 1

    result = certify_relation_claims([CLAIM], EVIDENCE,
                                     prior_certificates=certs,
                                     key_path=key_env)
    assert result["certified_claim_ids"] == ["dog-animal"]
    assert result["authority"] == "certifying"


def test_each_claim_gets_its_own_bound_certificate(key_env):
    """claim 2개 → cert 2개, subject fingerprint가 서로 다르고 교차 사용은
    검증측 결박이 거부한다(발급 루프가 결박을 실제로 채우는지의 증거)."""
    other = dict(CLAIM, id="cat-animal", concept="고양이")
    out = server.issue_claim_certificates([CLAIM, other], _bundle())
    certs = out["certificates"]
    assert len(certs) == 2
    assert certs[0]["subject_fingerprint"] != certs[1]["subject_fingerprint"]

    swapped = [certs[1]]  # cat의 인증서로 dog만 제시
    with pytest.raises(CertificateError, match="subject"):
        certify_relation_claims([CLAIM], EVIDENCE,
                                prior_certificates=swapped, key_path=key_env)


def test_a_failing_bundle_issues_nothing(key_env):
    """normalizer가 거부하는 bundle(해시 불일치)에서는 인증서가 발급되지
    않는다 — 실패 위에 서명하지 않는다."""
    bad = _bundle()
    bad["snapshot"]["sha256"] = "0" * 64
    out = server.issue_claim_certificates([CLAIM], bad)
    assert out["ok"] is False
    assert out.get("certificates", []) == []


def test_malformed_claims_are_refused(key_env):
    out = server.issue_claim_certificates([{"no_id": True}], _bundle())
    assert out["ok"] is False
    assert out["errors"][0]["code"] == "CLAIMS_NOT_OBJECT_LIST"


def test_issued_certificate_survives_only_its_own_revision(key_env):
    """revision 결박이 발급 경로에서도 실효: revision 2로 재조립된 claim은
    revision 1의 인증서로 인증되지 않는다."""
    out = server.issue_claim_certificates([CLAIM], _bundle())
    certs = out["certificates"]
    moved = dict(CLAIM, graph_revision=2)
    with pytest.raises(CertificateError):
        certify_relation_claims([moved], EVIDENCE,
                                prior_certificates=certs, key_path=key_env)
