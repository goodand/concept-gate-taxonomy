"""2-pass Verify₁ — 경우 A 를 경우 B 로 올린다 (SURVEY §8.3, HANDOFF next_action).

## 무엇을 증명하나

    경우 A   G₀ → Verify₀ → UNKNOWN(O₀) → repair → G₁ → STOP
    경우 B   G₀ → Verify₀ → UNKNOWN(O₀) → repair → G₁ → Verify₁ → PASS

기존 e2e(`test_e2e_v0_refine_verify.py`)는 [4] 의 O₀ 와 [6] 의 `all_pass` 를
**둘 다 손으로** 만든다(초안 정정에서 실측). 이 파일은 두 패스를 **같은 실제
생산자**(`results_from_claim_anchoring`, `cg_obligations.py:574`)로 계산한다 —
검사기 신설 없음, 어댑터 없음.

## 무엇을 증명하지 않나 (SURVEY §8.2 — 지우지 마라)

**반복 수렴·oscillation 부재는 여전히 증명 불가다.** repair 1회 설계이고, 수렴은
수열의 성질이라 n=1 에서는 진짜 수렴/우연한 통과/진동이 구별되지 않는다. 이
파일이 주는 것은 "**그 obligation 을 해결하는 방향으로 한 단계**"까지다.
이것을 "v0 가 수렴을 입증했다"로 읽으면 §8.2 를 위반하는 오독이다.

## 형태 (KNOWHOW §D)

두 패스 계산(D1: 손 사전이 아니라 원문에서) · 음성 쌍(해소 안 하는 repair →
여전히 UNKNOWN — 없으면 "항상 PASS" 구현이 통과) · 층 격리(directive:I3) ·
시점 결박(stale) · 범위 절제(invariant 는 None 그대로).

## 적대적 검증에서 채택·기각한 것 (2026-08-31)

- **채택(MAJOR)**: repair 가 revision 과 evidence 를 동시에 바꿔 **어느 것이
  O₀ 를 해결했는지** 파일이 말하지 않았다. probe 재실측: evidence 만 공급
  (revision 1 유지) → PASS, revision 만 올림 → UNKNOWN. **fix 는 evidence
  공급이고 revision 은 메타데이터다** — 분해 테스트로 못박았다(아래).
- **채택(MAJOR, 명명만)**: 음성 테스트 docstring 이 "무관한 수리"라 했으나
  실제는 **미수리**(O₀ 의 원인인 ev3 부재를 건드리지 않음)다. 정정했다.
  진짜 "무관한 수리"(evidence 는 공급했으나 결박이 깨진 claim 변이)는
  재실측(probe) 결과 UNKNOWN 이고, 그 경로(`:598-606` 어휘 부재)는
  `test_vocabulary_absence_is_unknown_not_fail` 이 이미 밟는다.
- **기각**: 검증자의 수정안 원문 — "evidence 공급 + 생산자가 무시하는 필드
  변경 → 여전히 UNKNOWN 인지 검증하라". 재실측 결과 그 입력은 **PASS** 다.
  생산자가 lifecycle 등을 안 보는 것은 결함이 아니라 이 obligation 의 범위이고,
  그 입력에 UNKNOWN 을 요구하는 테스트는 멀쩡한 생산자를 빨갛게 만든다.
- **채택(MINOR)**: `graph_revision` 은 생산자가 claim 에서 읽어 **기록만**
  한다(`cg_obligations.py:595,606,613`) — 본체 테스트에 주석으로 명시.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from conceptgate import cg_identity as ci                      # noqa: E402
from conceptgate.cg_obligations import (                       # noqa: E402
    Verdict, results_from_claim_anchoring, stale_obligations)

# G₀ (r1): ev3 를 인용하지만 그 본문이 아직 없다 — Verify₀ 가 UNKNOWN 을 **계산**할 재료.
CLAIM_R1 = {"id": "c1", "concept": "충돌출처", "feature": "액체금속",
            "cited_evidence_ids": ["ev3"], "graph_revision": 1,
            "lifecycle": "candidate"}
EVIDENCE_R1 = {"ev1": "무관한 본문"}                            # ev3 본문 없음
# G₁ (r2): repair 가 ev3 본문을 공급하고 새 revision 을 만든다.
EVIDENCE_R2 = dict(EVIDENCE_R1, ev3="충돌출처 는 액체금속 을 포함한다")


def _verify(claim, evidence):
    (result,) = results_from_claim_anchoring([claim], evidence)
    return result


def test_pass0_is_computed_unknown_not_hand_written():
    """Verify₀ 부터 계산이다 — 기존 e2e [4] 는 O₀ 를 손으로 만들었다."""
    o0 = _verify(CLAIM_R1, EVIDENCE_R1)
    assert o0.verdict is Verdict.UNKNOWN
    assert "본문 없음" in o0.reason
    assert o0.graph_revision == 1


def test_pass1_resolves_the_same_obligation_with_the_same_producer():
    """본체 — 경우 B. repair(ev3 본문 공급 + r2) 후 **같은 생산자**가 PASS 를 낸다.

    repair 는 둘을 바꾼다 — evidence 공급(이것이 fix)과 revision 갱신(이것은
    생산자가 claim 에서 읽어 **기록만** 하는 메타데이터, stale 결박용). 어느
    쪽이 판정을 바꿨는지는 아래 분해 테스트가 못박는다(적대검증 채택)."""
    repaired = dict(CLAIM_R1, graph_revision=2)
    o1 = _verify(repaired, EVIDENCE_R2)
    assert o1.verdict is Verdict.PASS
    assert o1.obligation == "claim.evidence_anchoring"
    assert o1.graph_revision == 2                      # r2 에 결박


def test_the_fix_is_the_evidence_supply_not_the_revision_bump():
    """분해 — 적대검증(MAJOR, 채택). 본체는 revision 과 evidence 를 동시에
    바꾸므로 혼자서는 "무엇이 O₀ 를 해결했는가"를 말하지 못한다. 여기서 가른다:
    evidence 만으로 충분하고, revision 만으로는 아무것도 안 된다."""
    evidence_only = _verify(CLAIM_R1, EVIDENCE_R2)          # revision 1 그대로
    assert evidence_only.verdict is Verdict.PASS
    assert evidence_only.graph_revision == 1
    revision_only = _verify(dict(CLAIM_R1, graph_revision=2), EVIDENCE_R1)
    assert revision_only.verdict is Verdict.UNKNOWN


def test_a_repair_that_does_not_address_o0_stays_unknown():
    """음성 쌍. **미수리** — claim 메타데이터(revision·lifecycle)만 바꾸고 O₀ 의
    원인(ev3 본문 부재)은 건드리지 않음 → 여전히 UNKNOWN. **이 검사가 없으면
    "항상 PASS" 구현이 본체를 통과한다.**

    적대검증 정정(채택): 초판 docstring 은 이것을 "무관한 수리"라 불렀다 —
    거짓이다. evidence 를 공급하고도 결박이 깨지는 진짜 "무관한 수리"는
    `test_vocabulary_absence_is_unknown_not_fail` 의 경로다."""
    unrepaired = dict(CLAIM_R1, graph_revision=2, lifecycle="candidate2")
    o1 = _verify(unrepaired, EVIDENCE_R1)
    assert o1.verdict is Verdict.UNKNOWN


def test_vocabulary_absence_is_unknown_not_fail():
    """ev3 본문은 있는데 어휘가 결박 안 되는 경우 — UNKNOWN 이지 FAIL 이 아니다
    (어휘 부재는 의미적 비지지의 증명이 아니다, 생산자 docstring)."""
    o1 = _verify(dict(CLAIM_R1, graph_revision=2),
                 dict(EVIDENCE_R1, ev3="다른 이야기"))
    assert o1.verdict is Verdict.UNKNOWN
    assert "문자적으로" in o1.reason or "부재" in o1.reason


def test_verify_does_not_mutate_the_graph():
    """directive:I3 — Verify 는 asserted graph 를 수정하지 않는다.
    fingerprint 전/후 동일로 증명한다."""
    claim = dict(CLAIM_R1, graph_revision=2)
    before = ci.claim_fingerprint(claim)
    _verify(claim, EVIDENCE_R2)
    assert ci.claim_fingerprint(claim) == before


def test_o0_is_stale_against_r2_and_o1_is_not():
    """시점 결박 — r1 의 O₀ 는 r2 에 적용되지 않고(stale), Verify₁ 산출은
    r2 결박이라 stale 이 아니다."""
    o0 = _verify(CLAIM_R1, EVIDENCE_R1)
    o1 = _verify(dict(CLAIM_R1, graph_revision=2), EVIDENCE_R2)
    assert stale_obligations([o0], current_revision=2) == ["claim.evidence_anchoring"]
    assert stale_obligations([o1], current_revision=2) == []


def test_invariant_stays_none_here():
    """범위 절제 — invariant 값 채움은 별도 설계 판단(회고 2부 §미해결)이다.
    이 파일에서 슬쩍 채우면 그 판단을 우회하는 것이 된다."""
    o1 = _verify(dict(CLAIM_R1, graph_revision=2), EVIDENCE_R2)
    assert o1.invariant is None
