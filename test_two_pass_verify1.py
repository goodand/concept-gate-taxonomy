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

## 변이 실측 — 이 하네스가 고장을 실제로 빨갛게 만드는가 (2026-08-31)

초록 8/8 은 "하네스가 작동한다"의 증명이 아니다 — 고장을 넣어 재야 한다.
생산자를 네 가지로 고장 내고 빨강 수를 쟀다(대조군 0/8, 변이마다 reload 격리):

    변이1 항상 PASS 반환            → 4/8 빨강 (pass0·분해·미수리·어휘)
    변이2 항상 UNKNOWN 반환         → 3/8 빨강 (pass1·분해·어휘)
    변이3 graph 수정(판정은 정상)   → 3/8 빨강 (fingerprint 계약 포함)
    변이4 stale 감지 무능(빈 목록)  → 1/8 빨강 (stale 계약, 정확히 그것만)

네 고장 계열 모두 ≥1 계약이 적발하고, 각 고장의 **전담 계약이 빨강 목록에
들어 있다.** 첫 측정은 변이3 이 모듈 픽스처 dict 를 오염시켜 대조군까지
빨개졌다 — 측정 스크립트의 격리 결함이었고(하네스 결함 아님), reload 격리로
재측정했다. pytest 는 실행마다 새로 import 하므로 이 오염 경로가 없다.

## 뮤테이션 테스트 — 연산자 단위 전수 (2026-08-31, 위 손 변이 4종과 별개)

위 4종은 손으로 고른 행동 변이다. 별도로 **대상 함수 2개**
(`results_from_claim_anchoring` · `stale_obligations`) 안의 변이 지점을
AST 로 전수 열거해 쟀다(연산자: 비교 반전 · Verdict 치환 · any↔all ·
not 제거 · if→True/False · continue→pass; 도구 선례는
`evidence-evaluator/docs/TOOL_SURVEY_MUTATION_20260817.md` — mutatest 는
coverage 충돌·무작위 표본·범위 한정 불가로 기각, in-process 러너 자작):

    1차: 14/14 kill (100%) — **공허했다.** 검산 결과 전부 exec 실패를
         kill 로 오인(통파일 exec 가 dataclass 에서 죽음). P25 형태를
         검산이 자체 적발.
    2차: 13/14 — 생존 1(`any→all`, 픽스처가 인용 1개뿐이라 구별 불가)
         → 계약 신설로 사살, 14/14.
    3차(동료 검토 채택으로 생산자 수리 후): 지점 14→21, **21/21 kill.**

**수치의 정본은 docstring 이 아니라 측정기다** — 산문 수치는 코드가 바뀌면
조용히 거짓이 된다(동료 검토 ④, P4 형태). 재측정:
`python3 scripts/mutation_two_pass_verify1.py` (위 수치는 2026-08-31,
동료 검토 반영 커밋 시점). 측정 한계(잔여): comprehension guard 일부는
변이 지점에서 빠져 있다 · 두 함수 밖(서명·certify 등)은 담당 밖.

## 동료 검토에서 채택한 것 (2026-08-31, 전건 probe 재실측 후)

- **MAJOR-1 채택**: 어휘 둘 다 빈 입력에 PASS+RULE_CHECKED+거짓 evidence
  문장 — 생산자 수리(어휘 없음 → UNKNOWN) + 계약.
- **MAJOR-2 채택**: any 는 본문 축이 아니라 **어휘 축** — 계약 docstring
  정정 + 흩어진 결박 현행(PASS) 고정 계약(강화 여부는 설계 판단 미결).
- **MAJOR-3 채택**: 매달린 인용 ≠ 빈 본문 — 생산자가 reason 을 가르고,
  픽스처 서사도 정정(초판 EVIDENCE_R1 은 키 부재였는데 주석이 "본문
  없음"이라 적었다 — P4).
- **① 채택**: 부정문·부분문자열 PASS 는 결함이 아니라 이 층이 재지 않는
  것 — 경계 목격자 계약 신설.
- **③ 채택(주석)**: invariant 계약은 값 채움 판단이 내려지면 갱신 대상.
- **④ 채택**: 뮤테이션 측정기를 scripts/ 로 승격, 수치를 시점 기록으로 격하.
- 기각 없음 — probe 8건 전부 동료 주장과 일치했다. certify 결합·bytes
  입력은 동료도 가설로 표시했고 여기서도 미실측 가설로 남긴다.

## 프로토콜 (나) 기록 — 건너뛴 단계와 사유

4단(workspace 재사용)에서 완료 — `results_from_claim_anchoring` 채택, 신규
코드 0줄. 그래서 **5단(subtree) PASS**(조기 중지), **8단(Sonnet 구현 위임)
PASS**(위임할 구현이 없다). 7단 적대검증은 실행했고 결과가 위 절이다.
위반 2건((다)1 위임 순서 · (나)2 Dirty 시점 미실측)의 전말은
`docs/DESIGN_DRAFT_two_pass_verify1.md` §5.
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
# ev3 는 **빈 본문**(수리 대기) — 키 자체가 없는 매달린 인용과 다른 사건이다
# (동료 검토 MAJOR-3: 초판은 키 부재였는데 주석이 "본문 없음"이라 적었다 — P4).
EVIDENCE_R1 = {"ev1": "무관한 본문", "ev3": ""}
# G₁ (r2): repair 가 ev3 본문을 공급하고 새 revision 을 만든다.
EVIDENCE_R2 = dict(EVIDENCE_R1, ev3="충돌출처 는 액체금속 을 포함한다")


def _verify(claim, evidence):
    (result,) = results_from_claim_anchoring([claim], evidence)
    return result


def test_pass0_is_computed_unknown_not_hand_written():
    """Verify₀ 부터 계산이다 — 기존 e2e [4] 는 O₀ 를 손으로 만들었다."""
    o0 = _verify(CLAIM_R1, EVIDENCE_R1)
    assert o0.verdict is Verdict.UNKNOWN
    assert "빈 본문" in o0.reason
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


def test_one_anchored_body_among_several_cited_is_enough():
    """뮤테이션이 낳은 계약 — `any→all` 뮤턴트(유일 생존)를 죽이는 입력.

    정정(동료 검토 MAJOR-2, 채택): 초판 docstring 은 "인용 본문 중 하나면
    된다(any)"라 적었으나 **코드의 any 는 본문 축이 아니라 어휘 축**이다
    (`for t in terms` 바깥, `for body in cited` 안). 이 입력(ev3 가 두 어휘를
    다 담음)은 두 축을 구별하지 못하고, 뮤턴트를 죽인다는 사실만 고정한다.
    축 구별은 아래 흩어진-결박 계약이 한다."""
    claim = dict(CLAIM_R1, cited_evidence_ids=["ev1", "ev3"], graph_revision=2)
    o1 = _verify(claim, EVIDENCE_R2)      # ev1="무관한 본문", ev3 만 결박
    assert o1.verdict is Verdict.PASS


def test_scattered_terms_across_bodies_currently_pass():
    """현행 의미 고정 — **어휘 축 any**: concept 과 feature 가 서로 다른
    본문에 흩어져 어느 본문도 claim 전체를 결박하지 않아도 PASS 다.

    이것이 옳은 의미인지는 **설계 판단 미결**이다(동료 검토 MAJOR-2가
    강요한 결정 — 지금은 판단 없이 이렇게 되어 있다는 사실을 고정하고,
    본문 축 결박으로 강화하려면 이 계약을 뒤집는 것이 그 판단의 형식이
    된다). 부수 효과: 이 입력은 any→all 뮤턴트를 본문 축에서도 죽인다.

    주의(동료 후속 지적): 이 계약은 **틀릴 수 있는 현행 행동을 고정**하고
    있다 — 판단이 내려지면 **바뀌어야 하는 쪽은 이 계약이다.** 이 PASS 를
    설계 의도로 읽지 마라. invariant 계약의 주석과 같은 형태로 남긴다."""
    claim = dict(CLAIM_R1, cited_evidence_ids=["evA", "evB"], graph_revision=2)
    o1 = _verify(claim, {"evA": "충돌출처 만 있다", "evB": "액체금속 만 있다"})
    assert o1.verdict is Verdict.PASS


def test_no_terms_means_unknown_not_vacuous_pass():
    """공허한 가드 차단(동료 검토 MAJOR-1, 채택) — concept·feature 둘 다
    비면 검사가 없으므로 PASS 가 아니라 UNKNOWN 이다. 초판 생산자는 이
    입력에 PASS + RULE_CHECKED + "문자 등장"이라는 **거짓 evidence 문장**을
    냈다(`if t` 가 빈 어휘를 검사 대상에서 빼는 P1 형태)."""
    claim = dict(CLAIM_R1, concept="", feature="", graph_revision=2)
    o1 = _verify(claim, EVIDENCE_R2)
    assert o1.verdict is Verdict.UNKNOWN
    assert "어휘 없음" in o1.reason


def test_dangling_citation_and_hollow_body_are_told_apart():
    """매달린 인용(키 부재 = 그래프 무결성 결함 후보)과 빈 본문(수리 대기
    = 정상 중간 상태)은 다른 사건이다(동료 검토 MAJOR-3, 채택) — 접으면
    Refine 이 무엇을 공급해야 하는지 알 수 없다."""
    dangling = _verify(dict(CLAIM_R1, cited_evidence_ids=["evX"]), {})
    hollow = _verify(dict(CLAIM_R1, cited_evidence_ids=["evX"]), {"evX": ""})
    assert dangling.verdict is Verdict.UNKNOWN
    assert hollow.verdict is Verdict.UNKNOWN
    assert "매달린 인용" in dangling.reason
    assert "빈 본문" in hollow.reason
    assert dangling.reason != hollow.reason


def test_what_anchoring_does_not_measure_negation_and_substring():
    """경계 목격자(동료 검토 ①, 채택) — 이 검사는 **문자 등장**이지 의미
    지지가 아니다(생산자 docstring 의 선언). 그 선언의 목격자가 계약에
    없으면 다음 사람이 이것을 "결박 확인"으로 읽고 상류에서 신뢰한다.

    - 부정문도 PASS 다: "포함하지 않는다"가 두 어휘를 문자로 담는다.
    - 부분문자열도 PASS 다: "금속" 은 "액체금속" 에 결박된다(형태소 경계
      없음). 둘 다 결함이 아니라 **이 층이 재지 않는 것**의 고정이다."""
    negation = _verify(dict(CLAIM_R1, graph_revision=2),
                       dict(EVIDENCE_R1, ev3="충돌출처 는 액체금속 을 포함하지 않는다"))
    assert negation.verdict is Verdict.PASS
    substring = _verify(dict(CLAIM_R1, concept="금속", feature="", graph_revision=2),
                        dict(EVIDENCE_R1, ev3="액체금속 이야기"))
    assert substring.verdict is Verdict.PASS


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
    이 파일에서 슬쩍 채우면 그 판단을 우회하는 것이 된다.

    주의(동료 검토 ③): 그 설계 판단이 내려져 생산자가 invariant 를 채우기
    시작하면 **이 계약이 판단의 반대편을 고정한다** — 그때 이 계약을 갱신
    하는 것까지가 그 판단의 일부다. 여기 적어 두는 이유다."""
    o1 = _verify(dict(CLAIM_R1, graph_revision=2), EVIDENCE_R2)
    assert o1.invariant is None
