"""D-E2E-v1-24 Q24.3: V1↔V2 재동결 불변식 게이트.

판정 §7-9: V1은 불변 역사적 artifact(SUPERSEDED_PRE_EXECUTION), V2는 신규
동결. 이 게이트가 기계로 보증하는 것:
  1. V1 manifest는 동결 커밋(f57ae12) 시점 그대로 — 바이트 해시 고정
  2. PMB 15: 선별·commitment 필드(text/lf/expected_ir 등) V1과 동일,
     canonicalization_profile_hash 필드만 V2 값
  3. FOLIO 재선별분(두 stratum 전체)은 신규 적격성 불변식
     predicate_label_reachability를 전건 만족
  4. profile hash V2는 descriptor에서 재계산 가능(단일 출처)
  5. seed·N·층 구성은 V1에서 상속(재타이핑 아님 — freeze_stage2_v2가
     import하는 것을 여기서 값으로 재확인)

이 게이트가 있는 한 "V1을 몰래 고쳐 결함을 없던 일로 만들기"와
"PMB 표본을 재선별 틈에 바꿔치기"가 조용히 통과할 수 없다.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from conceptgate.cg_identity import canonical_sha256  # noqa: E402

# V1 동결 산출물의 바이트 해시 — f57ae12 시점 고정값.
# 이 값이 틀려지면 V1이 사후 수정된 것이다 (판정 §8: 금지).
V1_MANIFEST_SHA256 = (
    "13b47362d5fb9c5bec2c6f6f4956215d6d6156924ce97b0920b4a434a2c76c14")

V1_PATH = HERE / "stage2_fixture_manifest.json"
V2_PATH = HERE / "stage2_fixture_manifest_v2.json"
REACH_PATH = HERE / "folio_reachability_scan_v2.json"

INVARIANT_FIELDS = ("case_id", "stratum", "source_locator", "subcorpus",
                    "text_sha256", "lf_sha256", "adapter_version",
                    "adapter_code_sha256", "expected_ir_sha256")


def _load():
    return (json.loads(V1_PATH.read_text(encoding="utf-8")),
            json.loads(V2_PATH.read_text(encoding="utf-8")))


def test_v1_manifest_is_byte_immutable():
    assert hashlib.sha256(V1_PATH.read_bytes()).hexdigest() == V1_MANIFEST_SHA256


def test_v2_exists_and_declares_amendment():
    _, v2 = _load()
    assert v2["manifest_version"] == "e2e-v1-c-fixtures-v2"
    am = v2["amendment"]
    assert am["ruling"] == "D-E2E-v1-24"
    assert am["v1_status"] == "SUPERSEDED_PRE_EXECUTION"
    assert "no cohort outcomes observed" in am["defect"]


def diff_pmb(v1: dict, v2: dict) -> list[str]:
    """PMB 15의 불변식 위반 목록 — 게이트와 음성 테스트가 공유하는 판정기."""
    p1 = {e["case_id"]: e for e in v1["entries"] if e["case_id"].startswith("PMB-")}
    p2 = {e["case_id"]: e for e in v2["entries"] if e["case_id"].startswith("PMB-")}
    bad = []
    if set(p1) != set(p2):
        bad.append(f"selection changed: {sorted(set(p1) ^ set(p2))}")
        return bad
    for cid, e1 in p1.items():
        e2 = p2[cid]
        for f in INVARIANT_FIELDS:
            if e1.get(f) != e2.get(f):
                bad.append(f"{cid}.{f}")
        if e2["canonicalization_profile_hash"] != v2["profile_hash"]:
            bad.append(f"{cid}.canonicalization_profile_hash != V2 profile_hash")
    return bad


def test_pmb_15_selection_and_commitments_unchanged():
    v1, v2 = _load()
    assert diff_pmb(v1, v2) == []
    assert len([e for e in v2["entries"] if e["case_id"].startswith("PMB-")]) == 15


def test_diff_gate_catches_a_swapped_pmb_commitment():
    """음성: PMB commitment를 바꿔치면 반드시 잡혀야 한다(공허화 방지)."""
    v1, v2 = _load()
    tampered = json.loads(json.dumps(v2))
    victim = next(e for e in tampered["entries"] if e["case_id"].startswith("PMB-"))
    victim["expected_ir_sha256"] = "0" * 64
    assert any(".expected_ir_sha256" in b for b in diff_pmb(v1, tampered))


def test_profile_hash_v2_recomputable_from_descriptor():
    _, v2 = _load()
    assert canonical_sha256(v2["profile"]) == v2["profile_hash"]
    labels = v2["profile"]["comparison_core"]["predicate_labels"]
    assert labels == {"PMB": "O1_PMB_LEMMA_NO_SENSE_V1",
                      "FOLIO": "FOLIO_LABEL_LOWERCASE_V1"}


def test_seed_and_strata_inherited_from_v1():
    v1, v2 = _load()
    assert v2["order_seed"] == v1["order_seed"]
    assert v2["strata_counts"] == v1["strata_counts"]
    assert len(v2["entries"]) == 20
    assert len(v2["folio_simple_controls"]) == 3


def test_folio_entries_all_satisfy_reachability():
    """재선별분 전건이 동결 규칙으로 도달 가능해야 한다 — 캐시의 실물로 재판정."""
    import scan_folio_eligibility_v2 as reach
    _, v2 = _load()
    cache = REPO / ".oracle_cache"
    folio = ([e for e in v2["entries"] if e["case_id"].startswith("FOLIO-")]
             + v2["folio_simple_controls"])
    assert len(folio) == 8
    for e in folio:
        fol = (cache / e["lf_sha256"]).read_bytes().decode()
        sent = (cache / e["text_sha256"]).read_bytes().decode()
        r = reach.fixture_reachability(fol, sent)
        assert r["reachable"] and r["paths_agree"], (e["case_id"], r)


def test_reachability_scan_record_pinned_in_selection_inputs():
    _, v2 = _load()
    rec = json.loads(REACH_PATH.read_text(encoding="utf-8"))
    assert (v2["selection_inputs"]["folio_reachability_scan_v2_sha256"]
            == canonical_sha256(rec))
    assert v2["selection_inputs"]["pmb_scan_sha256"] \
        == json.loads(V1_PATH.read_text())["selection_inputs"]["pmb_scan_sha256"]
