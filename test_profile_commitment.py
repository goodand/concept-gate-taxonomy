"""D-38 처분 — 인증서가 **어떤 계약으로 인증했는지**를 서명 아래에 싣는다.

## 판정이 명령한 것

D-38(`docs/DESIGN_DECISION_certification_profile_amendment.md`) 셋:

1. **ㄱ** `NEW_PROFILE_IDENTITY_PREFERRED` — `_v0` 제자리 확장은 논리적으로
   가능하나 계약 안전하지 않다. `_v1` 신설(`_v0` 보존).
2. **ㄴ** profile commitment를 **서명 본체**에 — 없으면 verifier가 동일
   `results[]`를 가진 두 문서를 구별하지 못한다.
3. **ㄴ + V5** 서명 payload shape이 바뀌므로 `CERTIFICATE_SCHEMA` bump.

## 우리 실측이 판정보다 강했던 것 (수신 검증 V3)

판정은 두 profile의 signed payload가 "동일할 **수 있다**"고 했다. 실측하니
**항상 바이트 동일**이었다 — 같은 입력을 `profile=C₀`·`C₁`로 인증해 얻은
인증서 payload의 sha256이 양쪽 `e5f9ff2796a271f8`이고, 그 payload에는
`signature` 필드조차 없었다. 이 파일의 첫 계약이 그 구멍을 닫는다.

## V8 은 이 처분을 막지 않는다 — 정정

수신 검증 §4는 "V8 미결 판단이 처분 1의 전제"라고 적었다. **과하게 보수적
이었다.** 판정 ㄱ은 `_v1`을 **조건 없이** 선호한다("원칙적으로 맞다",
`decision: NEW_PROFILE_IDENTITY_PREFERRED`). V8의 조건("v0의 역사적 의미를
보존해야 하는가")은 **제자리 확장이 허용되는지**만 가르므로, `_v1`로 가는
쪽에서는 어느 분기든 안전하다.

**V8이 실제로 거는 자리는 하나다** — 배포된 MCP 도구의 **기본 profile을
`_v1`으로 바꾸는가.** 그것은 기존 호출자의 관측 가능한 출력을 바꾸고,
판정 ㄷ가 "제품 계약 변경에 별도 backward-compatibility 규칙이 필요하다는
근거"라고 지목한 바로 그 지점이다. 그래서 이 변경은 **기본값을 건드리지
않는다**(마지막 계약이 그것을 고정한다).

## 구현 적대검증에서 채택·기각한 것 (2026-09-01)

- **채택(blocker 2, 뿌리 하나)**: profile 을 서명에 넣었는데 **검증부가 읽지
  않았다** — `_v0` 에만 commit 한 인증서와 `profile: None` 인증서가 `_v1`
  검증에서 `certifying` 을 받았고(재실측 확인), 생산 발급자(server)는 profile
  을 넘기지도 않았다. 수리: `_assert_certificate_grants_verdicts` 가 schema
  와 commitment 를 대조하고, `certify_relation_claims` 가 자기 profile 을
  넘기고, server 발급자가 `_v0` 를 명시한다(암묵 동작의 명시화 — V8 무관).
  검증자 정식화가 정확했다: **"서명 아래에 넣는 이유는 verifier 가 읽기
  때문이다 — 읽지 않으면 필드는 주석과 같은 지위다."**
- **채택(major)**: schema=`v1` 인 낡은 인증서가 조용히 통과했다 — v0→v1 때도
  "검증부는 대조하지 않는다"는 주석을 남겼고 같은 주석을 세 번째로 쓰는 대신
  대조를 넣었다. fail-closed: 저장된 인증서 0건이라 비용 0.
- **기록(major, 미수선)**: `profile_id → CertificationProfile` 레지스트리가
  없어 판정이 약속한 "exact required-set 재구성"은 불가하고 후보 검증만
  가능하다. 지금 집행은 호출자가 기대 profile 을 넘기므로 재구성이 필요
  없다 — 레지스트리는 필요해질 때 만든다(YAGNI).
- **기록(minor 2)**: required_hash 정의가 판정 원문(`H(required)`)과 달리
  profile_id 를 포함한다(별칭 구별에 필요했음을 검증자도 실측 확인) ·
  commitment 는 `allowed_na`·`applies_to_claim_kind` 를 결박하지 않는다
  (`is_certified` 가 읽지 않는 동안은 무해, 읽기 시작하면 결함으로 전환).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from conceptgate import cg_identity as ci                 # noqa: E402
from conceptgate import cg_obligations as ob              # noqa: E402

CLAIM = {"claim_id": "c1", "id": "c1", "concept": "돌체", "feature": "액체금속",
         "cited_evidence_ids": ["ev1"], "graph_revision": 1}


def _result(**kw):
    base = dict(obligation="claim.evidence_anchoring", verdict=ob.Verdict.PASS,
                assurance=ob.Assurance.RULE_CHECKED,
                decider=ob.DeciderKind.LOCAL_RULE, evidence="x")
    base.update(kw)
    return ob.ObligationResult(**base)


# ---------------------------------------------------------------------------
# 1. 판정 ㄴ — 두 profile 이 구별되어야 한다 (V3 이 잰 그 구멍)
# ---------------------------------------------------------------------------

def test_two_profiles_no_longer_produce_identical_signed_bytes(tmp_path):
    """**이 파일의 존재 이유.** 같은 `results[]` 를 서로 다른 profile 로 인증한
    두 인증서의 서명 대상이 달라야 한다. 이전에는 바이트 동일했다(V3)."""
    key_path = tmp_path / "k.json"
    a = ob.issue_claim_certificate(CLAIM, [_result()], issuer_tool="t",
                                   key_path=key_path,
                                   profile=ob.LEGACY_RELATION_PROFILE)
    b = ob.issue_claim_certificate(CLAIM, [_result()], issuer_tool="t",
                                   key_path=key_path,
                                   profile=ob.RELATION_CLAIM_V1_PROFILE)
    assert a["profile"] != b["profile"]
    assert a["signature"] != b["signature"]        # 서명 대상이 달라졌다


def test_the_commitment_names_the_profile_and_pins_its_required_set(tmp_path):
    """`profile_id` 만으로는 “그 이름이 무엇을 요구했는가”를 재구성할 수 없다.
    판정이 더 강한 형태로 권한 `required_hash` 를 함께 싣는다."""
    cert = ob.issue_claim_certificate(CLAIM, [_result()], issuer_tool="t",
                                      key_path=tmp_path / "k.json",
                                      profile=ob.RELATION_CLAIM_V1_PROFILE)
    commitment = cert["profile"]
    assert commitment["profile_id"] == "relation_claim_v1"
    assert commitment["required_hash"] == ob.profile_commitment(
        ob.RELATION_CLAIM_V1_PROFILE)["required_hash"]


def test_the_required_hash_is_order_independent():
    """`required` 의 나열 순서가 바뀌었다는 이유로 해시가 달라지면, 무관한
    편집이 인증서 불일치를 만든다 — 게이트가 울면 사람이 게이트를 끈다."""
    from dataclasses import replace
    p = ob.RELATION_CLAIM_V1_PROFILE
    shuffled = replace(p, required=tuple(reversed(p.required)))
    assert (ob.profile_commitment(p)["required_hash"]
            == ob.profile_commitment(shuffled)["required_hash"])


def test_the_required_hash_separates_different_required_sets():
    """위 계약의 짝 — 순서 불변이 “아무 것도 구별하지 않는다”가 되면 안 된다."""
    assert (ob.profile_commitment(ob.LEGACY_RELATION_PROFILE)["required_hash"]
            != ob.profile_commitment(ob.RELATION_CLAIM_V1_PROFILE)["required_hash"])


def test_tampering_with_the_commitment_breaks_the_signature(tmp_path):
    """음성 증명. 서명 **아래**에 있다면 고치는 순간 검증이 깨져야 한다 —
    이것이 없으면 “서명 본체에 넣었다”가 문자열 존재 확인으로 끝난다."""
    key_path = tmp_path / "k.json"
    cert = ob.issue_claim_certificate(CLAIM, [_result()], issuer_tool="t",
                                      key_path=key_path,
                                      profile=ob.RELATION_CLAIM_V1_PROFILE)
    cert["profile"]["profile_id"] = "legacy_relation_claim_v0"
    key = ci.load_or_create_key(key_path)
    with pytest.raises(ob.CertificateError):
        ob._assert_certificate_grants_verdicts(cert, CLAIM, key)


def test_an_untampered_certificate_still_verifies(tmp_path):
    """위 음성 증명의 짝 — 없으면 “항상 예외가 난다”도 통과한다."""
    key_path = tmp_path / "k.json"
    cert = ob.issue_claim_certificate(CLAIM, [_result()], issuer_tool="t",
                                      key_path=key_path,
                                      profile=ob.RELATION_CLAIM_V1_PROFILE)
    granted = ob._assert_certificate_grants_verdicts(
        cert, CLAIM, ci.load_or_create_key(key_path))
    assert granted["claim.evidence_anchoring"] is ob.Verdict.PASS


# ---------------------------------------------------------------------------
# 1a. 집행 — 구별 가능한 것은 구별되어야 한다 (적대검증 blocker 의 계약화)
# ---------------------------------------------------------------------------

def _valid_results():
    out = []
    for name in ob.RELATION_CLAIM_V1_PROFILE.required:
        spec = ob.OBLIGATION_REGISTRY[name]
        out.append(ob.ObligationResult(name, ob.Verdict.PASS,
                                       spec.min_assurance, spec.decider,
                                       evidence="x"))
    return out


def test_a_certificate_committed_to_v0_cannot_certify_under_v1(tmp_path):
    """적대검증이 잰 그 우회(D2). commitment 는 서명 아래 있었지만 아무도
    읽지 않아서 `_v0` 인증서가 `_v1` 검증을 통과했다 — 이제 거부된다."""
    kp = tmp_path / "k.json"
    cert = ob.issue_claim_certificate(CLAIM, _valid_results(), issuer_tool="t",
                                      key_path=kp,
                                      profile=ob.LEGACY_RELATION_PROFILE)
    with pytest.raises(ob.CertificateError, match="profile commitment"):
        ob.certify_relation_claims([CLAIM], {"ev1": "돌체 액체금속"},
                                   prior_certificates=[cert],
                                   profile=ob.RELATION_CLAIM_V1_PROFILE,
                                   key_path=kp)


def test_an_uncommitted_certificate_is_not_a_wildcard(tmp_path):
    """`profile: None` 이 모든 profile 을 통과하면 이 필드가 닫으려던 우회가
    형태만 바꿔 열린다(D3) — None 은 wildcard 가 아니다."""
    kp = tmp_path / "k.json"
    cert = ob.issue_claim_certificate(CLAIM, _valid_results(), issuer_tool="t",
                                      key_path=kp)                 # 미선언
    with pytest.raises(ob.CertificateError, match="profile commitment"):
        ob.certify_relation_claims([CLAIM], {"ev1": "돌체 액체금속"},
                                   prior_certificates=[cert],
                                   profile=ob.LEGACY_RELATION_PROFILE,
                                   key_path=kp)


def test_a_matching_commitment_certifies(tmp_path):
    """위 두 음성의 짝 — 없으면 "항상 거부" 구현이 통과한다."""
    kp = tmp_path / "k.json"
    cert = ob.issue_claim_certificate(CLAIM, _valid_results(), issuer_tool="t",
                                      key_path=kp,
                                      profile=ob.RELATION_CLAIM_V1_PROFILE)
    out = ob.certify_relation_claims([CLAIM], {"ev1": "돌체 액체금속"},
                                     prior_certificates=[cert],
                                     profile=ob.RELATION_CLAIM_V1_PROFILE,
                                     key_path=kp)
    assert out["certified_claim_ids"] == ["c1"]
    assert out["authority"] == "certifying"


def test_a_stale_schema_certificate_is_refused_not_reinterpreted(tmp_path):
    """적대검증 3a. schema=`v1` 문서가 조용히 통과했다 — 옛 서명 계약의
    문서를 새 계약 아래 재해석하지 않는다(fail-closed). 서명은 유효해야
    하므로 위조가 아니라 **정직하게 낡은** 문서를 만들어 검사한다."""
    kp = tmp_path / "k.json"
    import conceptgate.cg_obligations as mod
    orig = mod.CERTIFICATE_SCHEMA
    try:
        mod.CERTIFICATE_SCHEMA = "obligation_certificate_v1"
        old_cert = ob.issue_claim_certificate(CLAIM, _valid_results(),
                                              issuer_tool="t", key_path=kp,
                                              profile=ob.LEGACY_RELATION_PROFILE)
    finally:
        mod.CERTIFICATE_SCHEMA = orig
    key = ci.load_or_create_key(kp)
    with pytest.raises(ob.CertificateError, match="schema"):
        ob._assert_certificate_grants_verdicts(old_cert, CLAIM, key)


# ---------------------------------------------------------------------------
# 2. 판정 ㄴ+V5 — 서명 payload shape 이 바뀌면 schema 를 올린다
# ---------------------------------------------------------------------------

def test_the_certificate_schema_was_bumped():
    """08-31 `v0 → v1` 이 `results` 행에 `invariant` 를 더했을 때 올린 것과
    같은 종류의 변경이다(수신 검증 V5). 올리지 않으면 새 payload 를 옛 이름으로
    부르게 되고, 그것이 판정이 “위험하다”고 한 상태다."""
    assert ob.CERTIFICATE_SCHEMA == "obligation_certificate_v2"


def test_the_commitment_is_present_even_when_no_profile_is_asserted(tmp_path):
    """**형태가 조건부로 갈리지 않는다.** profile 을 주지 않은 호출도 같은
    shape 을 내고 값이 `None` 이다 — 하나의 schema 이름 아래 두 shape 이
    있으면 그것이 판정이 경계한 상황이다."""
    cert = ob.issue_claim_certificate(CLAIM, [_result()], issuer_tool="t",
                                      key_path=tmp_path / "k.json")
    assert "profile" in cert and cert["profile"] is None


# ---------------------------------------------------------------------------
# 3. 판정 ㄱ — `_v1` 신설, `_v0` 보존
# ---------------------------------------------------------------------------

def test_v0_is_preserved_unchanged():
    """제자리 재정의 금지. `_v0` 의 `required` 는 D-38 이전과 같아야 한다."""
    assert ob.LEGACY_RELATION_PROFILE.profile_id == "legacy_relation_claim_v0"
    assert ob.LEGACY_RELATION_PROFILE.required == (
        "source.snapshot_hash", "source.span_evidence",
        "claim.evidence_anchoring", "relation.antisymmetry",
        "relation.acyclicity", "relation.isa_hasa_exclusivity")
    assert "claim.evidence_provenance" not in ob.LEGACY_RELATION_PROFILE.required


def test_v1_is_v0_plus_provenance():
    """Q38 이 물은 그 변경 — 새 identity 안에서 이루어진다."""
    v0, v1 = ob.LEGACY_RELATION_PROFILE, ob.RELATION_CLAIM_V1_PROFILE
    assert set(v1.required) == set(v0.required) | {"claim.evidence_provenance"}
    assert v1.profile_id != v0.profile_id


def test_the_deployed_default_profile_is_not_switched():
    """**V8 이 실제로 거는 자리.** 기본 profile 을 `_v1` 로 바꾸면 배포된 호출자의
    관측 가능한 출력이 바뀐다(`certified_claim_ids` 축소) — 판정 ㄷ가 “제품 계약
    변경에 별도 backward-compatibility 규칙이 필요하다는 근거”라고 지목한 지점이다.
    그 판단이 내려지기 전까지 기본값은 `_v0` 다.

    이 계약을 뒤집는 것이 그 판단의 형식이다."""
    import inspect
    sig = inspect.signature(ob.certify_relation_claims)
    assert sig.parameters["profile"].default is ob.LEGACY_RELATION_PROFILE
