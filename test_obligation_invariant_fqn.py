"""판정이 자기가 지목하는 불변식을 FQN 으로 싣는다 (SURVEY §14.2 대안 B).

## 무엇을 푸는가

축 지도(SURVEY §14.1a)가 격차를 드러냈다: **상태 계약 축(`mechspec:I1`~`mechspec:I7`)
을 코드가 이름으로 부르는 곳이 0건**이다. 권한 축은 11 중 8이 코드에 언급되는데
그쪽은 하나도 없다. 원인은 단순하다 — **판정이 불변식을 지목할 자리가 없다.**

`ObligationResult` 의 9개 필드(`obligation`·`verdict`·`assurance`·`decider`·
`evidence`·`reason`·`depends_on`·`graph_revision`·`execution`) 어디에도 "이 판정이
어느 불변식에 대한 것인가"가 없다. 그래서 "Verify 가 어긴 것이 무엇인가"를 물으면
답할 수단이 없고, 축 지도가 종이 위에만 남는다.

## 왜 FQN 이어야 하나

같은 번호가 발행자마다 다른 뜻이다 — `directive:I3`("Verify 는 graph 를 수정하지
않는다") ≠ `mechspec:I3`("verified-region protection") ≠ `h1a-scope:I3`. 맨 `I3` 를
실으면 판정이 **무엇을 어겼는지 여전히 말하지 못한다.** 등록부 규약
(`docs/IDENTIFIER_REGISTER.md:25`)의 `<문서군>:<글자><번호>` 를 그대로 쓴다.

## 설계 제약 — 서명이 걸려 있다 (실측 2026-08-31)

인증서 **서명 본체**(`cg_obligations.py:645-660`)가 결과를 직렬화한다:

```python
"results": [{"obligation": …, "verdict": …, …, "graph_revision": r.graph_revision}
            for r in results]
```

새 필드를 여기 넣으면 **서명이 바뀐다.** 그리고 `"schema": CERTIFICATE_SCHEMA` 가
본체에 있는데 **검증부는 그것을 대조하지 않는다**(`:665-690` 에 schema 검사 없음) —
즉 스키마가 바뀌어도 옛 인증서가 조용히 통과한다. 그러므로:

- 필드는 **`None` 기본값으로 가산 도입**한다. `graph_revision` 이 그 선례다
  (`:156-163`, "None = revision 개념이 없는 호출자 — 유효하다").
- 서명 본체에 **넣는다.** 서명되지 않은 지목은 위조 가능하고, 그러면 "어느 불변식을
  어겼다"가 증거가 아니라 주장이 된다.
- 스키마 문자열을 **함께 올린다.** 검증부가 지금 안 보더라도, 올리지 않으면 나중에
  구별할 근거 자체가 없어진다.

## 적대적 검증에서 기각한 것 (2026-08-31)

지적 10건 중 **8건이 "구현이 아직 없다"** 였다 — `INVARIANT_GROUPS` 미정의 ·
`invariant` 필드 부재 · `validate_result` 로직 부재 · 서명 본체 미포함 ·
재구성 경로 미읽음 등. **그것은 TDD 빨강이지 계약 결함이 아니다.** 구현 전
계약을 공격하라는 요청이었으므로 전부 기각한다.

**위임 하네스의 구멍이 드러났다**: "구현은 아직 없다"를 프롬프트에 적었으나
**그 부재를 결함으로 보고하지 말라**고 명시하지 않았다. 다음 계약 검증 위임에는
그 문장을 넣는다.

채택한 둘은 아래 두 테스트에 반영돼 있다(스키마 단언 약함 · 빈 문자열).
그리고 검증자가 답하지 않은 질문(등록부 I 행과 `INVARIANT_GROUPS` 스냅샷 일치)은
**직접 실측했다** — 5개 문서군이 정확히 일치한다.

## 무엇을 하지 않는가

- **필수로 만들지 않는다.** 생산자가 19곳(`cg_obligations.py`)이고 테스트까지
  21곳이다. 전부 고치면 이 변경이 커지고, 커지면 되돌리기 어렵다.
- **불변식의 내용을 검사하지 않는다.** 이 계약은 "지목이 해소되는가"만 본다.
  "그 불변식을 실제로 어겼는가"는 다른 문제이고 이 층의 일이 아니다.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from conceptgate import cg_obligations as ob  # noqa: E402


def _result(**kw):
    base = dict(obligation="source.span_evidence", verdict=ob.Verdict.PASS,
                assurance=ob.Assurance.RULE_CHECKED,
                decider=ob.DeciderKind.LOCAL_RULE,
                evidence="cg_normalizer.py:170")
    base.update(kw)
    return ob.ObligationResult(**base)


# ---------------------------------------------------------------------------
# 1. 필드가 있고, 없어도 된다 (가산 도입)
# ---------------------------------------------------------------------------

def test_the_field_defaults_to_none(_=None):
    """기존 생산자 19곳을 고치지 않고 들어간다 — `graph_revision` 과 같은 선례."""
    assert _result().invariant is None


def test_an_existing_producer_still_validates():
    """가산 도입의 핵심: 필드를 안 넣은 판정이 여전히 유효하다."""
    assert ob.validate_result(_result()) == []


def test_the_field_accepts_an_fqn():
    assert _result(invariant="directive:I3").invariant == "directive:I3"


# ---------------------------------------------------------------------------
# 2. 지목은 해소되어야 한다 — 맨 번호는 지목이 아니다
# ---------------------------------------------------------------------------

def test_a_bare_number_is_rejected():
    """맨 `I3` 는 세 발행자(`directive`·`mechspec`·`h1a-scope`)에 걸쳐 있어
    **무엇을 어겼는지 말하지 못한다.** 지목의 목적을 달성하지 못하므로 위반이다."""
    codes = {v["code"] for v in ob.validate_result(_result(invariant="I3"))}
    assert "INVARIANT_NOT_FULLY_QUALIFIED" in codes


def test_an_unknown_group_is_rejected():
    """등록부에 없는 문서군은 해소되지 않는다 — 오타가 조용히 통과하면
    지목이 있는 것처럼 보이면서 아무것도 가리키지 않는다."""
    codes = {v["code"] for v in ob.validate_result(_result(invariant="nosuch:I3"))}
    assert "INVARIANT_UNKNOWN_GROUP" in codes


def test_an_empty_string_is_rejected():
    """빈 문자열은 `None`(지목 안 함)도 FQN(지목함)도 아니다 — **"지목했다고
    적혀 있는데 아무것도 안 가리키는"** 상태이고 그게 이 필드가 막으려던 것이다.
    적대검증 지적(채택): 이 검사가 없으면 `"invariant": ""` 를 넣는 구현이
    계약을 통과하면서 아무것도 보증하지 않는다."""
    codes = {v["code"] for v in ob.validate_result(_result(invariant=""))}
    assert "INVARIANT_NOT_FULLY_QUALIFIED" in codes


def test_a_registered_group_passes():
    for fqn in ("directive:I3", "mechspec:I7", "h1a-scope:I1"):
        assert ob.validate_result(_result(invariant=fqn)) == [], fqn


def test_the_groups_come_from_the_register_not_a_hand_copy():
    """손으로 베낀 목록은 등록부가 바뀌면 갈라진다(G199·G213). 등록부에서
    도출하고, 도출 결과를 스냅샷으로 고정해 의도치 않은 변화가 울게 한다."""
    assert ob.INVARIANT_GROUPS == frozenset(
        {"directive", "mechspec", "h1a-scope", "ev-eval", "ev-eval-code"})


# ---------------------------------------------------------------------------
# 3. 서명 — 지목이 서명 밖에 있으면 증거가 아니라 주장이다
# ---------------------------------------------------------------------------

def _issue(tmp_path, *results):
    """실제 API 로 인증서를 낸다. 검증 함수 이름은 `_assert_certificate_grants_verdicts`
    이고 `verify_claim_certificate` 가 **아니다**(2026-08-31 실측 — 계약 초안이
    없는 이름을 불렀다)."""
    from conceptgate import cg_identity
    key_path = tmp_path / "k.json"
    claim = {"claim_id": "c1", "graph_revision": 7}
    cert = ob.issue_claim_certificate(claim, list(results),
                                      issuer_tool="test", key_path=key_path)
    return cert, claim, cg_identity.load_or_create_key(key_path)


def test_the_invariant_is_inside_the_signed_body(tmp_path):
    """서명되지 않은 지목은 위조 가능하다. 그러면 "어느 불변식을 어겼다"가
    증거가 아니라 **주장**이 된다 — 이 필드의 목적이 사라진다."""
    cert, _, _ = _issue(tmp_path, _result(invariant="directive:I3"))
    assert cert["results"][0]["invariant"] == "directive:I3"


def test_tampering_with_the_invariant_breaks_the_signature(tmp_path):
    """음성 증명. 서명 안에 있다면 고치는 순간 검증이 깨져야 한다 — 이 검사가
    없으면 "서명 본체에 넣었다"가 **문자열 존재 확인**으로 끝난다."""
    cert, claim, key = _issue(tmp_path, _result(invariant="directive:I3"))
    cert["results"][0]["invariant"] = "mechspec:I3"
    with pytest.raises(ob.CertificateError):
        ob._assert_certificate_grants_verdicts(cert, claim, key)


def test_an_untampered_certificate_still_verifies(tmp_path):
    """위 음성 증명의 짝. 이것이 없으면 "항상 예외가 난다"도 통과한다."""
    cert, claim, key = _issue(tmp_path, _result(invariant="directive:I3"))
    granted = ob._assert_certificate_grants_verdicts(cert, claim, key)
    assert granted["source.span_evidence"] is ob.Verdict.PASS


def test_the_certificate_schema_string_was_raised():
    """스키마가 바뀌었으면 문자열도 바뀌어야 한다. 검증부가 지금 대조하지
    않더라도(실측: `:665-690` 에 schema 검사 없음), 올리지 않으면 나중에
    **구별할 근거 자체가 없어진다.**

    초안 단언은 `!= "…_v0"` 과 `endswith("v1")` 이라 **`"cert_v1"` 같은 아무
    문자열이나 통과**했다(적대검증 지적, 채택). 이름 자체를 못박는다 — 느슨한
    단언은 "올렸다"를 확인하지 못하고 "달라졌다"만 확인한다.

    **v1 → v2 갱신 (2026-09-01, D-38 ㄴ)**: 서명 본체에 profile commitment 가
    추가되며 몸체 형태가 또 바뀌었다. 이 계약의 목적이 바로 그 변화를 이름에
    반영하게 하는 것이므로, 단언 값을 올리는 것이 계약을 지키는 방식이다
    (지우거나 느슨하게 하는 것이 아니다). 이 파일이 08-31 에 만든 `invariant`
    필드는 그대로 서명 본체에 남아 있다 — 아래 계약들이 그것을 지킨다."""
    assert ob.CERTIFICATE_SCHEMA == "obligation_certificate_v2"


# ---------------------------------------------------------------------------
# 3a. 통합 경로 — 호출자가 준 인증서의 지목도 검사된다 (2026-08-31)
# ---------------------------------------------------------------------------
#
# 스키마 강제 워크플로가 실측으로 잡은 공백: 위 §2 는 `validate_result` 를
# **직접** 부르고 §3 은 서명 훼손을 노린다. 그래서 "잘못된 FQN 을 실은 인증서가
# `certify_relation_claims` 에서 거부되는가"라는 **통합 경로를 밟는 테스트가
# 0건**이었다. 그 공백이 "이 검사 분지는 도달 불가"라는 오독을 낳았다 — 실제로는
# 게이트 어댑터를 하나도 고치지 않아도 `prior_certificates` 로 지금 돈다.

def _cert_with_invariant(tmp_path, value):
    from conceptgate import cg_identity
    key_path = tmp_path / "k.json"
    claim = {"claim_id": "c1", "id": "c1", "concept": "a", "feature": "b",
             "cited_evidence_ids": ["e1"], "graph_revision": 1}
    cert = ob.issue_claim_certificate(
        claim, [_result(invariant=value)], issuer_tool="test", key_path=key_path)
    return cert, claim, key_path


def test_a_caller_supplied_certificate_with_a_bare_number_is_rejected(tmp_path):
    """신뢰 경계 — 호출자가 준 JSON 이 맨 번호를 실어 오면 거부된다.
    이것이 "미래를 기다리는 죽은 코드"가 아니라 **지금 작동하는 입력 검증**
    임의 증거다(MCP 표면 `server.py` 의 `prior_certificates` 로 노출)."""
    cert, claim, key_path = _cert_with_invariant(tmp_path, "I3")
    with pytest.raises(ob.CertificateError) as exc:
        ob.certify_relation_claims([claim], {"e1": "abc"},
                                   prior_certificates=[cert], key_path=key_path)
    assert "invariant" in str(exc.value).lower()


def test_a_caller_supplied_certificate_with_an_unknown_group_is_rejected(tmp_path):
    cert, claim, key_path = _cert_with_invariant(tmp_path, "nosuch:I3")
    with pytest.raises(ob.CertificateError):
        ob.certify_relation_claims([claim], {"e1": "abc"},
                                   prior_certificates=[cert], key_path=key_path)


def test_a_caller_supplied_certificate_with_a_resolvable_fqn_is_accepted(tmp_path):
    """위 둘의 짝 — 이것이 없으면 "항상 거부한다"도 통과한다."""
    cert, claim, key_path = _cert_with_invariant(tmp_path, "directive:I3")
    out = ob.certify_relation_claims([claim], {"e1": "abc"},
                                     prior_certificates=[cert], key_path=key_path)
    assert out.get("ok") is True


# ---------------------------------------------------------------------------
# 4. 이 층이 하지 않는 것
# ---------------------------------------------------------------------------

def test_it_does_not_check_whether_the_invariant_was_actually_violated():
    """`PASS` 인데 불변식을 지목해도 위반이 아니다 — "이 판정은 `directive:I3`
    에 대한 것이고 통과했다"가 정당한 문장이다. **지목과 판정은 다른 축**이고,
    둘을 묶으면 이 필드가 verdict 의 중복이 된다."""
    assert ob.validate_result(
        _result(verdict=ob.Verdict.PASS, invariant="directive:I3")) == []


# ---------------------------------------------------------------------------
# 5. (삭제됨) 등록부 미확인 상태 — 2026-08-31
# ---------------------------------------------------------------------------
#
# 여기 `INVARIANT_REGISTER_UNAVAILABLE` 검사 둘이 있었다. **지웠다.**
#
# 그 코드는 `cg_obligations` 가 import 시점에 `docs/IDENTIFIER_REGISTER.md` 를
# 파싱하던 시절의 것이다 — 배포 이미지에 `docs/` 가 없어 등록부를 못 읽는 상태가
# 실재했고, 그때 "모르는 문서군"이라 말하면 거짓이므로 갈랐다.
#
# 이제 문서군은 `conceptgate/_identifier_groups.py` 로 **생성**되어 패키지 안에
# 있다(`scripts/gen_identifier_groups.py`, 일치는 `test_identifier_groups_sync.py`
# 가 강제). 런타임에 등록부를 읽지 않으므로 **"못 읽음"이라는 상태 자체가
# 존재하지 않는다.**
#
# 지운 이유를 남기는 까닭: 이 코드가 왜 있었고 왜 사라졌는지 모르면, 다음 사람이
# 같은 상황에서 다시 만들거나 반대로 필요한 자리에서 안 만든다.
