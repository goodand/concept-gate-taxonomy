"""`claim.evidence_provenance` — document ⊨ … 의 **document 쪽을 결박한다**.

## 무엇을 푸는가 (2026-09-01 실측)

L2 는 "document ⊨ formal model 을 기계가 보증"이다. 그런데 사슬 감사가
**document 쪽이 결박되지 않았다**는 것을 드러냈다:

    원문      "돌체는 액체금속을 포함하지 **않는다**."
    caller    evidence_texts = {"ev1": "돌체 는 액체금속 을 포함한다"}
    판정      claim.evidence_anchoring → PASS · RULE_CHECKED

`results_from_claim_anchoring` 은 caller 가 준 dict **안에서** 어휘를 찾고,
그 dict 가 문서와 무관해도 알 방법이 없다. 즉 검사되던 명제는
"document ⊨ claim" 이 아니라 "**caller 가 준 문장 ⊨ claim**" 이었다.

이 의무가 그 간선이다 — 인용 본문을 **문서 snapshot 에서 유도**한다
(`cg_normalizer.resolve_cited_evidence`, span 검증은 `_span_evidence` 단일
출처 재사용). 유도하면 위조는 존재할 자리가 없다.

## 무엇을 닫지 않는가 — 지우지 마라

- **의미 판정이 아니다.** 유도된 본문으로 anchoring 을 돌려도 그것은 여전히
  문자 등장 검사다. 실측: 위 원문(부정문)에서 유도한 본문으로도 anchoring 은
  PASS 다 — 어휘가 실제로 등장하기 때문이다. **L2 의 의미 층은 이 파일이
  아니라 M1 semantic obligation 의 일**이다(`obligation_layer_roadmap.md:36`).
- **파일에서 문서를 읽지 않는다.** snapshot 은 caller 가 만든다
  (`make_snapshot(text)`). 파일 → 인용 일치를 재는 실물은 실험 층에 있고
  (`_h1a_surface._excerpt_matches`) 아직 obligation 층에 배선되지 않았다.
  즉 이 의무가 닫는 것은 "**snapshot ⊨ 인용**"이고 "파일 ⊨ snapshot"은 남는다.
- **프로파일 `required` 에 넣지 않았다.** 넣으면 기존 인증의 의미가 바뀐다
  (인증받던 claim 들이 갑자기 미충족이 된다) — 그것은 별도 판단이다.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from conceptgate import cg_normalizer as nz          # noqa: E402
from conceptgate import cg_obligations as ob         # noqa: E402

SOURCE = "돌체는 액체금속을 포함하지 않는다."
CLAIM = {"id": "c1", "concept": "돌체", "feature": "액체금속",
         "cited_evidence_ids": ["ev1"], "graph_revision": 1}


def _snapshot() -> dict:
    return nz.make_snapshot(SOURCE)["snapshot"]


def _verdict(citations, claim=CLAIM):
    resp = nz.resolve_cited_evidence(_snapshot(), citations)
    (result,) = ob.results_from_cited_evidence(resp, [claim])
    return result


# ---------------------------------------------------------------------------
# 1. 위조는 FAIL 이다 — 이 파일이 존재하는 이유
# ---------------------------------------------------------------------------

def test_a_quote_absent_from_the_document_fails():
    """실측한 그 구멍. 원문은 "포함하지 않는다" 인데 "포함한다" 를 인용으로
    선언하면 **FAIL** 이다 — 이전에는 anchoring 이 PASS 를 냈다."""
    r = _verdict({"ev1": {"span": {"start": 0, "end": 5},
                          "quote": "돌체 는 액체금속 을 포함한다"}})
    assert r.verdict is ob.Verdict.FAIL
    assert "유도되지 않았다" in r.reason


def test_a_span_outside_the_document_fails():
    """좌표 위조도 같다 — 문서 길이를 넘는 span 은 해소되지 않는다."""
    r = _verdict({"ev1": {"span": {"start": 0, "end": 9999}}})
    assert r.verdict is ob.Verdict.FAIL


def test_evidence_derived_from_the_document_passes():
    """음성 증명의 짝 — 없으면 "항상 FAIL" 구현이 위 둘을 통과한다."""
    r = _verdict({"ev1": {"span": {"start": 0, "end": len(SOURCE)}}})
    assert r.verdict is ob.Verdict.PASS
    assert "선언된 span" in r.evidence


def test_the_verdict_names_the_document_it_was_bound_to():
    """어느 문서에 결박됐는지 판정이 말해야 한다 — 안 말하면 결박이 주장이다."""
    snap = _snapshot()
    resp = nz.resolve_cited_evidence(
        snap, {"ev1": {"span": {"start": 0, "end": len(SOURCE)}}})
    (r,) = ob.results_from_cited_evidence(resp, [CLAIM])
    assert snap["sha256"][:16] in r.evidence


# ---------------------------------------------------------------------------
# 2. 부재와 미확인과 위조를 가른다
# ---------------------------------------------------------------------------

def test_a_claim_citing_nothing_is_unknown_not_fail():
    """인용이 **없다**는 것과 인용이 **위조**라는 것은 다른 사건이다."""
    r = _verdict({}, claim=dict(CLAIM, cited_evidence_ids=[]))
    assert r.verdict is ob.Verdict.UNKNOWN
    assert "인용 선언 없음" in r.reason


def test_an_unattempted_citation_is_unknown_not_pass():
    """해소를 **시도하지 않은** 인용이 PASS 로 흐르면 결박이 공허해진다."""
    r = _verdict({"other": {"span": {"start": 0, "end": 3}}})
    assert r.verdict is ob.Verdict.UNKNOWN
    assert "해소 시도 기록이 없음" in r.reason


def test_partial_resolution_does_not_leak_into_texts():
    """실패한 인용은 `texts` 에 없어야 한다 — 있으면 부분 성공이 조용히
    전체 성공이 되고, 그 다음 단계(anchoring)가 위조 본문을 먹는다."""
    resp = nz.resolve_cited_evidence(
        _snapshot(),
        {"good": {"span": {"start": 0, "end": 3}},
         "bad": {"span": {"start": 0, "end": 3}, "quote": "없는 문장"}})
    assert "good" in resp["texts"] and "bad" not in resp["texts"]
    assert resp["ok"] is False


# ---------------------------------------------------------------------------
# 3. 경계 — 이 의무가 하지 않는 것
# ---------------------------------------------------------------------------

def test_it_is_not_a_semantic_judgment():
    """유도된 본문이라도 anchoring 은 여전히 **문자** 검사다. 원문이 부정문
    ("포함하지 않는다")인데 concept·feature 가 둘 다 등장하므로 PASS 다.

    이 계약이 없으면 "이제 문서 충족을 기계가 보증한다"로 오독된다 — 결박된
    것은 **본문의 출처**이고 그 본문이 주장을 **지지하는지**는 L2 의 의미 층
    (M1 semantic obligation)의 일이다."""
    resp = nz.resolve_cited_evidence(
        _snapshot(), {"ev1": {"span": {"start": 0, "end": len(SOURCE)}}})
    (anchoring,) = ob.results_from_claim_anchoring([CLAIM], resp["texts"])
    assert anchoring.verdict is ob.Verdict.PASS      # 그리고 원문은 부정문이다


def test_it_is_registered_but_not_yet_required_by_the_profile():
    """레지스트리에는 있고 프로파일 `required` 에는 없다. 넣으면 기존
    인증받던 claim 들이 갑자기 미충족이 되므로 별도 판단이다."""
    assert "claim.evidence_provenance" in ob.OBLIGATION_REGISTRY
    assert "claim.evidence_provenance" not in ob.LEGACY_RELATION_PROFILE.required
