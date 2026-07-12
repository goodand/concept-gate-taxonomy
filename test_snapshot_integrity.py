#!/usr/bin/env python3
"""snapshot 정합 회귀 테스트 — 리뷰 발견 1 / 아키텍처 분석 §7.3 고정.

배경: assemble/map은 caller가 제출한 snapshot.sha256을 재계산 없이 신뢰했다.
그래서 sha256='deadbeef'처럼 text와 무관한 hash로도 유효 span만 있으면
verification_status='source_span_verified'가 발급됐다. L1이 약속하는
'span 실존 + 해시 일치' 중 해시 일치가 검증되지 않은 것.

수정: 세 진입점(validate_selection/assemble_concepts/map_to_owl)이
진입 시 sha256(text)를 재계산해 불일치하면 stage='snapshot'의
SOURCE_HASH_MISMATCH로 거부한다.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import cg_normalizer as N

TEXT = "개는 갯과의 가축화된 동물이다."
VALID_SNAP = N.make_snapshot(TEXT)["snapshot"]
FORGED = {"text": TEXT, "sha256": "deadbeef", "uri": "x"}


def _is_hash_mismatch(r):
    return (not r["ok"] and r["stage"] == "snapshot"
            and any(e["code"] == "SOURCE_HASH_MISMATCH" for e in r["errors"]))


# ── 위조 hash 거부 (세 진입점 모두) ─────────────────────────────────

def test_map_to_owl_rejects_forged_hash():
    r = N.map_to_owl({"snapshot": FORGED, "concepts": [
        {"name": "개", "definition_kind": "primitive"}]})
    assert _is_hash_mismatch(r), r


def test_assemble_rejects_forged_hash():
    r = N.assemble_concepts({"snapshot": FORGED, "concepts": [
        {"name": "개", "features": [
            {"label": "가축", "relation": "is_a", "evidence_text": "가축화된"}]}]})
    assert _is_hash_mismatch(r), r


def test_validate_selection_rejects_forged_hash():
    r = N.validate_selection(
        {"sense_id": "local:개:001"}, [], FORGED)
    assert _is_hash_mismatch(r), r


# ── text 있는데 hash 누락도 거부 ────────────────────────────────────

def test_text_without_hash_rejected():
    r = N.map_to_owl({"snapshot": {"text": TEXT}, "concepts": [
        {"name": "개", "definition_kind": "primitive"}]})
    assert not r["ok"] and r["stage"] == "snapshot"
    assert any(e["code"] == "MISSING_SOURCE_HASH" for e in r["errors"]), r


# ── 정상 경로는 영향 없음 ──────────────────────────────────────────

def test_valid_snapshot_passes():
    r = N.map_to_owl({"snapshot": VALID_SNAP, "concepts": [
        {"name": "개", "definition_kind": "primitive"}]})
    assert r["ok"], r


def test_absent_snapshot_still_allowed_unverified():
    """snapshot 미제공(빈 dict)은 통과 — 그 경로는 unverified만 낸다."""
    r = N.map_to_owl({"concepts": [
        {"name": "개", "definition_kind": "primitive"}]})
    assert r["ok"], r


def test_forged_hash_would_have_passed_before_fix():
    """회귀 방어: 위조 snapshot도 span은 유효하므로, 정합 검사가 없으면
    이전처럼 통과했을 것임을 명시한다 (검사 제거 시 이 테스트가 깨진다)."""
    # span은 실존 (0:1 = '개') — 정합 검사만이 유일한 방어선
    assert 0 <= 1 <= len(FORGED["text"])
    r = N.assemble_concepts({"snapshot": FORGED, "concepts": [
        {"name": "개", "features": [{"label": "가축", "relation": "is_a",
         "evidence_span": {"start": 0, "end": 1}}]}]})
    assert _is_hash_mismatch(r), r


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-q"]))
