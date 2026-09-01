"""E2E MVP — **실제 파일**에서 `certifying` 까지, 손 verdict 0.

## 왜 이 파일이 있는가

기존 e2e(`test_e2e_v0_refine_verify.py`)는 문서를 dict 리터럴로 두고 `[4]`·
`[6]` 의 판정을 손으로 썼다(사슬 감사 실측: 9단계 중 계산 판정 1개, 문서를
파일에서 읽는 코드 0건). 즉 "document ⊨ …" 의 **document 쪽이 없었다.**

이 파일은 그 반대다 — **디스크의 파일**에서 시작해 인증까지 간다:

```text
파일 → make_snapshot → bundle(concepts + evidence_span)
     → server.issue_claim_certificates   (의무 7종을 in-process 계산·서명)
     → certify_relation_claims(prior_certificates=…)
     → authority: certifying · certified_claim_ids: ['c1']
```

**손으로 쓴 verdict 가 하나도 없다.** 판정은 전부 실제 span·해시·게이트에서
나온다. 이것이 L2("document ⊨ formal model 을 기계가 보증")의 **최소 실물**이다.

## MVP 가 드러낸 요구사항 (만들어 보니 알게 된 것)

1. **키 공유가 필수다.** 발급자(server)와 검증자가 다른 `key_path` 를 쓰면
   `CertificateError: signature is absent or does not verify` 로 막힌다 —
   설계대로 fail-closed 이지만, E2E 를 조립할 때 가장 먼저 걸린다.
   이 계약이 그 요구를 명시적으로 고정한다.
2. **문서 → claim 생산자가 없다.** Refine 은 LLM 이고 저장소에 asserted
   claim 생성기가 0건이다(probe 실측). 그래서 claim 은 여전히 이 파일이
   준다 — **MVP 의 경계이고, 남은 L2 작업의 정확한 위치다.**
3. **profile 을 선언해야 인증이 성립한다.** D-38 이후 검증부가 commitment 를
   대조하므로 발급 시 `profile=` 이 필요하다(server 가 이미 명시한다).
4. **`relation.is_a` 는 `unknown` 이어도 인증된다** — 프로파일 `required` 에
   없기 때문이다. 그것이 이 프로파일의 계약이고, 이 파일이 그 사실을 고정해
   다음 사람이 "인증인데 왜 unknown 이 있나" 로 오독하지 않게 한다.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from conceptgate import cg_identity as ci                    # noqa: E402
from conceptgate import cg_normalizer as nz                  # noqa: E402
from conceptgate import cg_obligations as ob                 # noqa: E402
from conceptgate import server                               # noqa: E402

SOURCE_TEXT = ("# 개요\n\n"
               "개는 갯과의 가축화된 동물이다. 고양이는 고양잇과의 동물이다.\n")
CLAIM = {"claim_id": "c1", "id": "c1", "concept": "개", "feature": "동물",
         "relation": "is_a", "cited_evidence_ids": ["ev1"], "graph_revision": 1}


def _span(text: str, sub: str) -> dict:
    i = text.index(sub)
    return {"start": i, "end": i + len(sub), "quote": sub}


def _write_source(tmp_path: Path) -> Path:
    """**디스크의 실제 파일** — 이 파일이 존재하는 이유의 절반이다."""
    p = tmp_path / "source.md"
    p.write_text(SOURCE_TEXT, encoding="utf-8")
    return p


def _bundle_from_file(doc: Path) -> dict:
    text = doc.read_text(encoding="utf-8")          # ← 파일에서 읽는다
    snap = nz.make_snapshot(text, uri=f"file://{doc}")["snapshot"]
    return {"snapshot": snap, "concepts": [
        {"name": "동물", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(text, "가축화된 동물이다")}]},
        {"name": "개", "features": [
            {"label": "동물", "relation": "is_a",
             "evidence_span": _span(text, "가축화된 동물이다")},
            {"label": "갯과", "relation": "is_a",
             "evidence_span": _span(text, "갯과의 가축화된")}]},
    ]}


# ---------------------------------------------------------------------------
# 1. 본체 — 파일에서 certifying 까지
# ---------------------------------------------------------------------------

def test_a_real_file_reaches_certifying_with_zero_hand_written_verdicts(tmp_path):
    """**이 파일의 존재 이유.** 디스크의 파일에서 시작해 `certifying` 에
    도달하고, 그 사이 어떤 verdict 도 손으로 쓰지 않는다."""
    doc = _write_source(tmp_path)
    assert doc.is_file()                             # 전제: 실물이다
    bundle = _bundle_from_file(doc)

    issued = server.issue_claim_certificates([CLAIM], bundle)
    assert issued["ok"], issued
    certs = issued["certificates"]
    assert len(certs) == 1

    out = ob.certify_relation_claims(
        [CLAIM], {"ev1": "개는 갯과의 가축화된 동물이다"},
        prior_certificates=certs, profile=ob.LEGACY_RELATION_PROFILE,
        key_path=ci.default_key_path())
    assert out["authority"] == "certifying"
    assert out["certified_claim_ids"] == ["c1"]


def test_the_snapshot_is_bound_to_the_file_not_to_a_literal(tmp_path):
    """document 쪽 결박 — snapshot 의 uri 가 그 파일을 가리키고 해시가
    파일 내용에서 나온다. 이것이 없으면 "파일에서 왔다"가 주장이다."""
    doc = _write_source(tmp_path)
    snap = _bundle_from_file(doc)["snapshot"]
    assert snap["uri"].endswith(doc.name)
    assert snap["sha256"] == nz.make_snapshot(
        doc.read_text(encoding="utf-8"))["snapshot"]["sha256"]


def test_every_certified_verdict_came_from_computation(tmp_path):
    """손 verdict 0 의 증명 — 인증서에 실린 의무가 **7종**이고 전부
    in-process 계산이다(span·해시·게이트). 이 계수가 줄면 어딘가에서
    손 사전이 다시 끼어든 것이다."""
    doc = _write_source(tmp_path)
    certs = server.issue_claim_certificates([CLAIM], _bundle_from_file(doc))["certificates"]
    obligations = [r["obligation"] for r in certs[0]["results"]]
    assert len(obligations) == 7
    assert "source.snapshot_hash" in obligations      # 해시에서
    assert "source.span_evidence" in obligations      # span+quote 에서
    assert "relation.antisymmetry" in obligations     # 실게이트에서


# ---------------------------------------------------------------------------
# 2. MVP 가 드러낸 요구사항 — 계약으로 고정한다
# ---------------------------------------------------------------------------

def test_a_different_key_is_refused_not_silently_accepted(tmp_path):
    """**MVP 조립 시 가장 먼저 걸린 것.** 발급자와 검증자의 키가 다르면
    fail-closed 로 막힌다 — 설계대로이고, E2E 를 세울 때 이 요구를 모르면
    "왜 certifying 이 안 되나" 로 헤맨다(실제로 헤맸다)."""
    import pytest
    doc = _write_source(tmp_path)
    certs = server.issue_claim_certificates([CLAIM], _bundle_from_file(doc))["certificates"]
    with pytest.raises(ob.CertificateError, match="signature"):
        ob.certify_relation_claims(
            [CLAIM], {"ev1": "개는 갯과의 가축화된 동물이다"},
            prior_certificates=certs, profile=ob.LEGACY_RELATION_PROFILE,
            key_path=tmp_path / "다른키.json")


def test_the_certificate_declares_its_profile(tmp_path):
    """D-38 이후 검증부가 commitment 를 대조하므로 발급이 계약을 선언해야
    한다 — server 가 이미 그렇게 한다는 것을 이 계약이 고정한다."""
    doc = _write_source(tmp_path)
    certs = server.issue_claim_certificates([CLAIM], _bundle_from_file(doc))["certificates"]
    assert certs[0]["profile"]["profile_id"] == "legacy_relation_claim_v0"
    assert certs[0]["schema"] == ob.CERTIFICATE_SCHEMA


def test_an_unknown_outside_required_does_not_block_certification(tmp_path):
    """`relation.is_a` 가 `unknown` 이어도 인증된다 — 프로파일 `required` 에
    없기 때문이다. 이 사실을 고정하지 않으면 다음 사람이 "인증인데 unknown
    이 있다" 를 결함으로 읽는다."""
    doc = _write_source(tmp_path)
    certs = server.issue_claim_certificates([CLAIM], _bundle_from_file(doc))["certificates"]
    out = ob.certify_relation_claims(
        [CLAIM], {"ev1": "개는 갯과의 가축화된 동물이다"},
        prior_certificates=certs, profile=ob.LEGACY_RELATION_PROFILE,
        key_path=ci.default_key_path())
    verdicts = out["verdicts_by_claim"]["c1"]
    assert verdicts["relation.is_a"] == "unknown"
    assert "relation.is_a" not in ob.LEGACY_RELATION_PROFILE.required
    assert out["certified_claim_ids"] == ["c1"]


def test_there_is_still_no_document_to_claim_producer():
    """**MVP 의 경계 — 남은 L2 작업의 정확한 위치.** claim 은 이 파일이
    준다. 문서에서 claim 을 뽑는 생산자가 저장소에 없기 때문이다(Refine 은
    LLM). 그 생산자가 생기면 이 계약이 실패해야 하고, 그때가 이 파일을
    갱신할 시점이다."""
    for name in ("extract_claims", "propose_claims", "derive_claims"):
        assert not hasattr(nz, name), f"{name} 이 생겼다 — MVP 경계를 갱신하라"
