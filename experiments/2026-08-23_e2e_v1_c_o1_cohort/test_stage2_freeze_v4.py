"""V4 재동결 불변식 게이트 (D-25 + D-26).

보증하는 것:
  1. V1·V2 manifest는 바이트 불변 (V1 pin은 test_stage2_freeze_v2가 이미
     보유 — 여기서는 V2를 pin)
  2. PMB in-N 15: V2와 선별·commitment 불변, profile hash 필드만 V4
  3. V4의 모든 fixture(20 + FOLIO control 3 + PMB control 3)가
     MEASUREMENT_SATISFIABILITY_V2를 통과 — 캐시 실물로 재판정
  4. contract_hashes가 라이브 모듈과 일치 — **projection·satisfiability·
     canonical core·eval profile을 고치면 V4 동결이 자동 실효**
     (adapter 자격의 코드 결박과 같은 기제)
  5. profile hash 재계산 가능, 방언 6종(implies 포함), seed·층 상속
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
from conceptgate.cg_ir_schema import dispatch_envelope_schema  # noqa: E402

V2_MANIFEST_SHA256 = "7eac95dd74fa96ce036f7d66c3c2f251fe83b33eab0f3628036ad146bbde0bfc"

V2_PATH = HERE / "stage2_fixture_manifest_v2.json"
V4_PATH = HERE / "stage2_fixture_manifest_v4.json"
SAT_SCAN_PATH = HERE / "stage2_sat_scan_v4.json"

INVARIANT_FIELDS = ("case_id", "stratum", "source_locator", "subcorpus",
                    "text_sha256", "lf_sha256", "adapter_version",
                    "adapter_code_sha256", "expected_ir_sha256")


def _load():
    return (json.loads(V2_PATH.read_text(encoding="utf-8")),
            json.loads(V4_PATH.read_text(encoding="utf-8")))


def test_v2_manifest_is_byte_immutable():
    assert hashlib.sha256(V2_PATH.read_bytes()).hexdigest() == V2_MANIFEST_SHA256


def test_v4_declares_lineage():
    _, v4 = _load()
    assert v4["manifest_version"] == "e2e-v1-c-fixtures-v4"
    am = v4["amendment"]
    assert am["rulings"] == ["D-E2E-v1-25", "D-E2E-v1-26"]
    assert am["v2_status"] == "SUPERSEDED_PRE_EXECUTION"
    assert "ABORTED_PRE_FREEZE" in am["v3_status"]
    assert "no cohort outcomes observed" in am["defect"]


def test_pmb_15_invariant_from_v2():
    v2, v4 = _load()
    p2 = {e["case_id"]: e for e in v2["entries"] if e["case_id"].startswith("PMB-")}
    p4 = {e["case_id"]: e for e in v4["entries"] if e["case_id"].startswith("PMB-")}
    assert set(p2) == set(p4) and len(p4) == 15
    for cid, e2 in p2.items():
        e4 = p4[cid]
        for f in INVARIANT_FIELDS:
            assert e2.get(f) == e4.get(f), (cid, f)
        assert e4["canonicalization_profile_hash"] == v4["profile_hash"]


def test_profile_v4_recomputable_and_has_implies_dialect():
    _, v4 = _load()
    assert canonical_sha256(v4["profile"]) == v4["profile_hash"]
    assert v4["profile"]["constructors"] == \
        ["forall", "exists", "and", "pred", "not", "implies"]
    assert v4["profile"]["comparison_core"]["scope_projection"] == \
        "O1_SCOPE_PROJECTION_V1"
    labels = v4["profile"]["comparison_core"]["predicate_labels"]
    assert "diagnostic_only" in labels["status"]


def test_contract_hashes_bind_live_modules():
    """코드 결박: 측정 경로 모듈을 고치면 이 게이트가 동결 실효를 알린다."""
    _, v4 = _load()
    ch = v4["contract_hashes"]
    for key, rel in (("canonicalization_core_sha256", "_stage2_canonical_core.py"),
                     ("projection_module_sha256", "_stage2_scope_projection.py"),
                     ("satisfiability_module_sha256", "_stage2_satisfiability.py"),
                     ("eval_profile_module_sha256", "_stage2_eval_profile.py")):
        live = hashlib.sha256((HERE / rel).read_bytes()).hexdigest()
        assert ch[key] == live, f"{rel} 변경 — V4 동결 실효 (재자격·재동결 필요)"
    assert ch["prompt_template_v4_sha256"] == hashlib.sha256(
        (HERE / "stage2_prompt_template_v4.md").read_bytes()).hexdigest()
    assert ch["dispatch_schema_sha256"] == canonical_sha256(
        dispatch_envelope_schema(("forall", "exists", "and", "pred", "not", "implies")))


def test_all_v4_fixtures_satisfiable_from_cache():
    import _stage2_satisfiability as sat
    from conceptgate import cg_sbn_adapter as sbn, cg_fol_adapter as fol
    _, v4 = _load()
    cache = REPO / ".oracle_cache"
    everything = (v4["entries"] + v4["folio_simple_controls"]
                  + v4["pmb_projection_controls"])
    assert len(everything) == 26
    for e in everything:
        lf = (cache / e["lf_sha256"]).read_bytes().decode()
        ir = (sbn.adapt_sbn(lf) if e["case_id"].startswith("PMB-")
              else fol.adapt_fol(lf))
        rec = sat.check_oracle_ir(e["case_id"], ir)
        assert rec["verdict"] == "SATISFIABLE", (e["case_id"], rec)


def test_sat_scan_pinned_and_gate_v2():
    _, v4 = _load()
    ss = json.loads(SAT_SCAN_PATH.read_text(encoding="utf-8"))
    assert ss["gate"] == "MEASUREMENT_SATISFIABILITY_V2"
    assert (v4["selection_inputs"]["satisfiability_scan_v4_sha256"]
            == canonical_sha256(ss))


def test_seed_and_strata_inherited():
    v2, v4 = _load()
    assert v4["order_seed"] == v2["order_seed"]
    assert v4["strata_counts"] == v2["strata_counts"]
    assert len(v4["entries"]) == 20
    assert len(v4["folio_simple_controls"]) == 3
    assert len(v4["pmb_projection_controls"]) == 3
    assert all(e["stratum"] == "pmb_projection_control"
               for e in v4["pmb_projection_controls"])


def test_diff_gate_catches_pmb_swap():
    v2, v4 = _load()
    tampered = json.loads(json.dumps(v4))
    victim = next(e for e in tampered["entries"] if e["case_id"].startswith("PMB-"))
    victim["expected_ir_sha256"] = "0" * 64
    p2 = {e["case_id"]: e for e in v2["entries"] if e["case_id"].startswith("PMB-")}
    bad = [cid for cid, e in
           ((x["case_id"], x) for x in tampered["entries"]
            if x["case_id"].startswith("PMB-"))
           if any(e.get(f) != p2[cid].get(f) for f in INVARIANT_FIELDS)]
    assert bad, "바꿔치기가 잡히지 않으면 이 게이트는 공허하다"
