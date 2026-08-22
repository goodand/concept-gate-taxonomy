"""Stage 2 실행기의 TDD 계약 — RED 먼저 (독립 준비물 ①: 코호트 실행기).

dispatch 자체는 세션의 Workflow 하네스만 수행할 수 있으므로(리허설 실측),
실행기는 세 python 함수로 분리된다:
  export_dispatch_args : plan → dispatch 인자 (프롬프트 verbatim — 재렌더
                         금지, plan이 유일 출처)
  derive_expected_irs  : manifest+캐시 → oracle IR — canonical_sha256이
                         entry.expected_ir_sha256과 일치해야만 반환
                         (commitment 동일성 검증. ≠correctness는 자격이 담당)
  ingest_outputs       : subject 산출 수집 → evaluate → 평가 profile →
                         _stage2_score → 기록 (덮어쓰기 거부, ERROR 캡처)
규율 계보: _h1a_cohort_run(드리프트 단언·기록 보존), 리허설(스키마 강제
경로), D-19(mechanical retry는 dispatch층 — 실행기는 최종 산출만 회계).
모든 재료는 발명이다(ORACLE-12).
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

import _stage2_cohort as C  # noqa: E402
import _stage2_run as R  # noqa: E402
from conceptgate.cg_identity import canonical_sha256  # noqa: E402

V = lambda n: {"kind": "var", "name": n}
P = lambda name, *args: {"kind": "pred", "name": name, "args": list(args)}
EX = lambda v, b: {"kind": "exists", "var": v,
                   "restriction": P("True"), "body": b}


def put(cache: Path, data: bytes) -> str:
    h = hashlib.sha256(data).hexdigest()
    (cache / h).write_bytes(data)
    return h


@pytest.fixture()
def world(tmp_path):
    cache = tmp_path / "cache"; cache.mkdir()
    fixtures = [
        ("R-01", "Every zorble glims.", EX("x", P("zorble.n.01", V("x")))),
        ("R-02", "Some tikk praxes.",   EX("y", P("tikk.n.01", V("y")))),
    ]
    entries, oracle = [], {}
    for cid, sent, ir in fixtures:
        lfb = f"(invented-lf {cid})".encode()
        entries.append({
            "case_id": cid,
            "source_locator": {"corpus_id": "inv", "corpus_version": "v0",
                               "artifact": "none", "record_locator": cid,
                               "retrieval_urls": []},
            "text_sha256": put(cache, sent.encode()),
            "lf_sha256": put(cache, lfb),
            "adapter_version": "inv-handmade",
            "adapter_code_sha256": "0" * 64,
            "canonicalization_profile_hash": "1" * 64,
            "expected_ir_sha256": canonical_sha256(ir)})
        oracle[cid] = ir
    mpath = tmp_path / "manifest.json"
    mpath.write_text(json.dumps({"entries": entries}, ensure_ascii=False))
    spec = C.CohortSpec(mpath, tmp_path / "plan.json", cache,
                        "RUN-test-v1", "RT", "claude-haiku-4-5-20251001")
    C.write_cohort(spec)
    # 리허설 어댑터: 발명 lf 바이트 → 손제작 oracle IR (결정적 조회는 이
    # 테스트 하네스의 장비다 — 프로덕션 adapter의 대역)
    def adapter(lf_bytes: bytes):
        cid = lf_bytes.decode().split()[-1].rstrip(")")
        return oracle[cid]
    return spec, adapter, oracle, tmp_path


# ------------------------------------------------------- export 축 ---------

def test_export_uses_plan_prompts_verbatim(world):
    spec, *_ = world
    args = R.export_dispatch_args(spec.cohort_path)
    plan = json.loads(spec.cohort_path.read_text())
    assert [t["prompt"] for t in args["trials"]] == \
           [t["prompt"] for t in plan["trials"]]
    assert args["schema"] == plan["provenance"]["output_schema"]
    assert args["model"] == plan["provenance"]["model"]


# ------------------------------------------------ oracle 파생·동일성 축 ----

def test_derive_expected_irs_verifies_commitment(world):
    spec, adapter, oracle, _ = world
    out = R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter)
    assert set(out) == {"R-01", "R-02"}
    assert out["R-01"] == oracle["R-01"]


def test_derive_refuses_hash_mismatch(world):
    """adapter 산출이 사전등록 해시와 다르면 — 코드가 바뀌었든 조작이든 —
    그 oracle은 존재하지 않는 것과 같다. 반환은 위조 통과다."""
    spec, adapter, oracle, _ = world
    wrong = dict(oracle); wrong["R-02"] = EX("z", P("prax.n.01", V("z")))
    def bad_adapter(lf):  # R-02만 다른 IR
        cid = lf.decode().split()[-1].rstrip(")")
        return wrong[cid]
    with pytest.raises(R.OracleDrift) as ei:
        R.derive_expected_irs(spec.manifest_path, spec.cache_dir, bad_adapter)
    assert "R-02" in str(ei.value)


def test_derive_refuses_missing_cache(world):
    spec, adapter, _, tmp = world
    m = json.loads(spec.manifest_path.read_text())
    (spec.cache_dir / m["entries"][0]["lf_sha256"]).unlink()
    with pytest.raises(R.OracleDrift):
        R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter)


# ------------------------------------------------------- ingest 축 ---------

def _outputs(spec, oracle, mutate=None):
    plan = json.loads(spec.cohort_path.read_text())
    outs = []
    for t in plan["trials"]:
        ir = json.loads(json.dumps(oracle[t["case_id"]]))
        outs.append({"trial_id": t["trial_id"], "ir": ir})
    if mutate:
        mutate(outs)
    return outs


def test_ingest_happy_path_scores_pass(world):
    spec, adapter, oracle, tmp = world
    res = R.ingest_outputs(
        spec.cohort_path, _outputs(spec, oracle),
        R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter),
        results_path=tmp / "results.json", pass_min=2)
    assert res["report"]["acceptance"]["accepted"] is True
    assert [r["result"] for r in res["trial_rows"]] == ["pass", "pass"]


def test_ingest_applies_evaluation_profile_both_sides(world):
    """subject가 lemma를 내고 oracle이 synset이어도 profile이 흡수 —
    리허설 실패 형태의 실행기 수준 재확인."""
    spec, adapter, oracle, tmp = world
    def to_lemma(outs):
        for o in outs:
            o["ir"] = json.loads(
                json.dumps(o["ir"]).replace("zorble.n.01", "zorble")
                                   .replace("tikk.n.01", "tikk"))
    res = R.ingest_outputs(
        spec.cohort_path, _outputs(spec, oracle, to_lemma),
        R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter),
        results_path=tmp / "results.json", pass_min=2)
    assert [r["result"] for r in res["trial_rows"]] == ["pass", "pass"]


def test_missing_output_becomes_error_row_not_row_loss(world):
    """행 손실은 조용한 분모 조작 — 누락 trial은 ERROR로 회계된다."""
    spec, adapter, oracle, tmp = world
    outs = _outputs(spec, oracle)[:1]
    res = R.ingest_outputs(
        spec.cohort_path, outs,
        R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter),
        results_path=tmp / "results.json", pass_min=2)
    rows = {r["trial_id"]: r["result"] for r in res["trial_rows"]}
    assert len(rows) == 2 and "error" in rows.values()
    assert res["report"]["acceptance"]["no_final_error"] is False


def test_non_dict_output_is_error_captured_not_raised(world):
    spec, adapter, oracle, tmp = world
    def fence(outs):
        outs[0]["ir"] = "```json\n{}\n```"
    res = R.ingest_outputs(
        spec.cohort_path, _outputs(spec, oracle, fence),
        R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter),
        results_path=tmp / "results.json", pass_min=2)
    rows = {r["trial_id"]: r["result"] for r in res["trial_rows"]}
    assert sorted(rows.values()) == ["error", "pass"]


def test_unknown_or_duplicate_trial_ids_refused(world):
    spec, adapter, oracle, tmp = world
    exp = R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter)
    bad = _outputs(spec, oracle); bad[1]["trial_id"] = bad[0]["trial_id"]
    with pytest.raises(ValueError):
        R.ingest_outputs(spec.cohort_path, bad, exp,
                         results_path=tmp / "r1.json", pass_min=2)
    alien = _outputs(spec, oracle); alien[0]["trial_id"] = "GHOST-99"
    with pytest.raises(ValueError):
        R.ingest_outputs(spec.cohort_path, alien, exp,
                         results_path=tmp / "r2.json", pass_min=2)


def test_certified_map_reaches_the_two_by_two(world):
    spec, adapter, oracle, tmp = world
    res = R.ingest_outputs(
        spec.cohort_path, _outputs(spec, oracle),
        R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter),
        results_path=tmp / "results.json", pass_min=2,
        certified={"RT-01": True})
    q = res["report"]["two_by_two"]
    assert q["A"] == 1 and q["C"] == 1


def test_results_overwrite_refused_and_bytes_deterministic(world):
    spec, adapter, oracle, tmp = world
    exp = R.derive_expected_irs(spec.manifest_path, spec.cache_dir, adapter)
    rp = tmp / "results.json"
    R.ingest_outputs(spec.cohort_path, _outputs(spec, oracle), exp,
                     results_path=rp, pass_min=2)
    on_disk = rp.read_text()
    with pytest.raises(R.ResultsOverwriteRefused):
        R.ingest_outputs(spec.cohort_path, _outputs(spec, oracle), exp,
                         results_path=rp, pass_min=2)
    assert rp.read_text() == on_disk, "거부가 파일을 건드리면 안 된다"
