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
    """본체 — 경우 B. repair(ev3 본문 공급 + r2) 후 **같은 생산자**가 PASS 를 낸다."""
    repaired = dict(CLAIM_R1, graph_revision=2)
    o1 = _verify(repaired, EVIDENCE_R2)
    assert o1.verdict is Verdict.PASS
    assert o1.obligation == "claim.evidence_anchoring"
    assert o1.graph_revision == 2                      # r2 에 결박


def test_a_repair_that_does_not_address_o0_stays_unknown():
    """음성 쌍. 무관한 수리(revision 만 올림, ev3 본문 여전히 없음) → 여전히
    UNKNOWN. **이 검사가 없으면 "항상 PASS" 구현이 본체를 통과한다.**"""
    unrelated = dict(CLAIM_R1, graph_revision=2, lifecycle="candidate2")
    o1 = _verify(unrelated, EVIDENCE_R1)
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
