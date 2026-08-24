"""코호트 수락 파라미터를 생략할 수 없게 만드는 게이트.

## 무엇을 막는가

드라이런(2026-08-24)이 적발했다: `ingest_outputs`의 `stratum_floors`가 선택
인자여서 **생략하면 사전등록이 금지한 수락이 조용히 통과한다.** 채점기
docstring이 그 회피를 이름까지 대며 경고하고 있었는데도 호출 측에서 도달
가능했다 — 경고는 호출자를 막지 못한다.

`_stage2_score.py:18-21`의 그 문구:
> Stratum floor addition (D-E2E-v1-22 §3·§16): … 15 PMB passes + 1
> multi_quantifier pass out of 5 = 16/20 PASS overall, but fails floor

## 왜 유도인가

`COHORT_ACCEPTANCE`는 사전등록 산문의 전사이고 **전사는 드리프트한다.**
그래서 (a) 원문과 대조해 고정하고, (b) `strata` 지도는 손으로 적지 않고
manifest·plan에서 유도하고, (c) manifest의 stratum 크기가 하한의 `n_min`과
어긋나면 멈춘다.

## 음성 테스트가 왜 이 파일의 핵심인가

가드를 넣었다는 것과 가드가 결과를 바꾼다는 것은 다르다. `test_the_evasion_*`
쌍이 **같은 입력에서 판정이 뒤집히는 것**을 보인다 — 그것이 없으면 정상
가드와 공허한 가드의 관측값이 같다.
"""
from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
for p in (str(HERE), str(REPO)):
    if p not in sys.path:
        sys.path.insert(0, p)

import _stage2_run as R  # noqa: E402
from conceptgate import cg_fol_adapter as fol, cg_sbn_adapter as sbn  # noqa: E402

MANIFEST = HERE / "stage2_fixture_manifest_v5.json"
PLAN = HERE / "stage2_cohort_plan_v5.json"
PREREG = HERE / "PREREGISTRATION_STAGE2_V4.md"
CACHE = REPO / ".oracle_cache"


def test_acceptance_constants_match_the_preregistration_text():
    """전사 드리프트 고정 — 상수가 사전등록 산문과 어긋나면 실패한다."""
    text = PREREG.read_text(encoding="utf-8")
    assert re.search(r"N=20", text), "사전등록에서 N=20을 못 찾았다"
    assert re.search(r"PASS[≥>]=?\s*16", text), "PASS≥16을 못 찾았다"
    assert re.search(r"multi[- ]quantifier stratum 4/5|multi 4/5", text), \
        "multi-quantifier 4/5를 못 찾았다"
    A = R.COHORT_ACCEPTANCE
    assert A["n_preregistered"] == 20
    assert A["pass_min"] == 16
    assert A["stratum_floors"] == {"multi_quantifier": (5, 4)}


def test_strata_map_is_derived_not_transcribed():
    a = R.derive_acceptance_inputs(MANIFEST, PLAN)
    assert len(a["strata"]) == 20
    sizes: dict[str, int] = {}
    for s in a["strata"].values():
        sizes[s] = sizes.get(s, 0) + 1
    assert sizes["multi_quantifier"] == 5
    assert sum(sizes.values()) == 20
    assert a["pass_min"] == 16
    assert a["stratum_floors"]["multi_quantifier"] == (5, 4)


def test_derive_refuses_population_change(tmp_path):
    """음성 — manifest 항목이 20이 아니면 멈춘다(모집단 변경은 사전등록 개정)."""
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["entries"] = m["entries"][:19]
    p = tmp_path / "m.json"
    p.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="모집단이 바뀌었다"):
        R.derive_acceptance_inputs(p, PLAN)


def test_derive_refuses_stratum_size_drift(tmp_path):
    """음성 — multi_quantifier가 5가 아니면 멈춘다."""
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    for e in m["entries"]:
        if e.get("stratum") == "multi_quantifier":
            e["stratum"] = "cardinal"
            break
    p = tmp_path / "m.json"
    p.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(ValueError, match="n_min"):
        R.derive_acceptance_inputs(p, PLAN)


def test_derive_refuses_plan_case_not_in_manifest(tmp_path):
    """음성 — plan이 manifest에 없는 case를 가리키면 멈춘다."""
    pl = json.loads(PLAN.read_text(encoding="utf-8"))
    pl["trials"][0]["case_id"] = "PMB-ghost-d0000"
    p = tmp_path / "plan.json"
    p.write_text(json.dumps(pl), encoding="utf-8")
    with pytest.raises(ValueError, match="manifest에 없는 case"):
        R.derive_acceptance_inputs(MANIFEST, p)


# --------------------------------------------------- 회피 시나리오 (핵심) ---

def _oracle_and_strata():
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    oracle, stratum = {}, {}
    for e in m["entries"]:
        r = R.resolve_bytes(e["lf_sha256"], CACHE)
        if r["execution"] != "ok":
            pytest.skip(f"오라클 캐시 부재: {e['case_id']}")
        data = r["data"]
        ir = (sbn.adapt_sbn(data.decode("utf-8", "replace"))
              if e["case_id"].startswith("PMB-")
              else fol.adapt_fol(data.decode("utf-8")))
        oracle[e["case_id"]] = ir
        stratum[e["case_id"]] = e.get("stratum")
    return oracle, stratum


def _evasion_outputs(oracle, stratum):
    """사전등록이 금지한 형태: 전체 16/20이지만 multi_quantifier는 1/5."""
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    mq = [t["trial_id"] for t in plan["trials"]
          if stratum[t["case_id"]] == "multi_quantifier"]
    fail = set(mq[:4])
    out = []
    for t in plan["trials"]:
        ir = copy.deepcopy(oracle[t["case_id"]])
        if t["trial_id"] in fail:
            ir = {"op": "not", "arg": ir}
        out.append({"trial_id": t["trial_id"], "ir": ir})
    return out


def test_the_evasion_is_rejected_through_ingest_cohort(tmp_path):
    """ingest_cohort는 층 하한을 유도하므로 회피가 통과하지 못한다."""
    oracle, stratum = _oracle_and_strata()
    res = R.ingest_cohort(
        PLAN, _evasion_outputs(oracle, stratum),
        manifest_path=MANIFEST, cache_dir=CACHE,
        results_path=tmp_path / "r.json")
    rep = res["report"]
    assert rep["counts"]["pass"] == 16, "회피 시나리오는 전체 16/20이어야 한다"
    assert rep["acceptance"]["accepted"] is False
    assert rep["acceptance"]["stratum_floors_met"] is False


def test_the_evasion_succeeds_without_floors_so_the_gate_is_not_vacuous(tmp_path):
    """음성 대조 — **같은 입력**이 층 하한 없이는 수락된다.

    이 테스트가 없으면 위 테스트가 가드 때문에 통과하는지, 애초에 그 입력이
    거부되는 입력이라서 통과하는지 구별할 수 없다.
    """
    oracle, stratum = _oracle_and_strata()
    res = R.ingest_outputs(
        PLAN, _evasion_outputs(oracle, stratum), oracle,
        results_path=tmp_path / "r.json", pass_min=16)   # floors 생략
    rep = res["report"]
    assert rep["counts"]["pass"] == 16
    assert rep["acceptance"]["accepted"] is True, (
        "층 하한 없이도 거부된다면 위 테스트는 하한을 증명하지 못한다")


# --------------------------------------------- 오라클 유도 (같은 결함 2호) ---
# L0 그래프 정합성 검증(2026-08-24)이 적발했다: `ingest_cohort`가 층 하한은
# 유도하면서 **오라클은 인자로 받고 있었다.** 즉 커밋 해시 검사를 호출자가
# 빼먹을 수 있었다 — 층 하한과 같은 모양의 구멍이 같은 함수 안에 하나 더
# 있었다. 서명에서 `expected_irs`를 없애 그 경로를 닫았다.


def test_cohort_oracle_is_derived_and_verified():
    o = R.derive_cohort_oracle(MANIFEST, CACHE)
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert set(o) == {e["case_id"] for e in m["entries"]}
    assert len(o) == 20


def test_ingest_cohort_signature_has_no_omittable_contract_inputs():
    """서명 자체가 계약이다 — 셋 중 하나라도 인자로 남으면 생략 가능해진다."""
    import inspect
    params = set(inspect.signature(R.ingest_cohort).parameters)
    for forbidden in ("expected_irs", "stratum_floors", "strata", "pass_min"):
        assert forbidden not in params, (
            f"{forbidden}가 서명에 있으면 호출자가 그것을 빼먹을 수 있다 — "
            f"층 하한 생략 회피가 정확히 그 경로였다")


def test_oracle_drift_halts_on_commitment_mismatch(tmp_path):
    """음성 — 커밋 해시가 어긋나면 멈춘다(조용히 다른 오라클로 채점 금지)."""
    m = json.loads(MANIFEST.read_text(encoding="utf-8"))
    m["entries"][0]["expected_ir_sha256"] = "0" * 64
    mp = tmp_path / "m.json"
    mp.write_text(json.dumps(m), encoding="utf-8")
    with pytest.raises(R.OracleDrift, match="commitment mismatch"):
        R.derive_cohort_oracle(mp, CACHE)


def test_oracle_drift_halts_on_cache_miss(tmp_path):
    """음성 — 캐시가 없으면 멈춘다(재료 없이 채점 금지)."""
    with pytest.raises(R.OracleDrift, match="unavailable"):
        R.derive_cohort_oracle(MANIFEST, tmp_path / "empty_cache")


def test_cohort_adapter_dispatch_matches_the_freeze_script():
    """어댑터 분기가 동결 스크립트의 규칙과 같은가 — 다르면 채점이 다른
    오라클을 쓴다. 동결 스크립트를 읽어 접두어 규칙을 대조한다."""
    src = (HERE / "freeze_stage2_v5.py").read_text(encoding="utf-8")
    assert 'case_id.startswith("PMB-")' in src, (
        "동결 스크립트의 분기 규칙이 바뀌었다 — cohort_adapter도 함께 고쳐라")
    assert "adapt_sbn" in src and "adapt_fol" in src
