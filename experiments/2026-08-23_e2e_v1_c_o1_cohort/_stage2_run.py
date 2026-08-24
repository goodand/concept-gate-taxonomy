"""Stage 2 실행기 — dispatch 자체는 세션의 워크플로우 하네스만 수행 가능하므로(리허설
실측), 실행기는 세 python 함수로 분리된다:

  export_dispatch_args : plan → dispatch 인자 (프롬프트 verbatim — 재렌더 금지,
                         plan이 유일 출처)
  derive_expected_irs  : manifest+캐시 → oracle IR — canonical_sha256이
                         entry.expected_ir_sha256과 일치해야만 반환
                         (commitment 동일성 검증. ≠correctness는 자격이 담당)
  ingest_outputs       : subject 산출 수집 → evaluate → 평가 profile →
                         _stage2_score → 기록 (덮어쓰기 거부, ERROR 캡처)

규율 계보: _h1a_cohort_run(드리프트 단언·기록 보존), 리허설(스키마 강제 경로),
D-19(mechanical retry는 dispatch층 — 실행기는 최종 산출만 회계). 모든 재료는
발명이다(ORACLE-12).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from conceptgate.cg_fixture_resolver import resolve_bytes
from conceptgate.cg_identity import canonical_sha256
from conceptgate.cg_evaluate import evaluate
from _stage2_eval_profile import normalize_labels_for_case
from _stage2_projection_pipeline_v2 import evaluate_scope_v2
from _stage2_canonical_core import desugar
from _stage2_score import score


class OracleDrift(Exception):
    """One or more oracles could not be verified (missing cache or commitment mismatch)."""
    pass


class ResultsOverwriteRefused(Exception):
    """Results file already exists; overwriting would destroy a preserved record."""
    pass


def export_dispatch_args(plan_path: Path | str) -> dict:
    """Load the plan JSON and export dispatch arguments.

    Returns {"trials": [...], "schema": ..., "model": ...} where:
    - trials: list of {"trial_id", "case_id", "prompt"} in plan order
    - schema: plan["provenance"]["output_schema"]
    - model: plan["provenance"]["model"]

    Prompts are verbatim from plan (never re-rendered).
    """
    plan_path = Path(plan_path)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))

    schema = plan["provenance"]["output_schema"]
    model = plan["provenance"]["model"]

    # Extract trials with trial_id, case_id, and prompt verbatim
    trials = []
    for trial in plan["trials"]:
        trials.append({
            "trial_id": trial["trial_id"],
            "case_id": trial["case_id"],
            "prompt": trial["prompt"],
        })

    return {
        "trials": trials,
        "schema": schema,
        "model": model,
    }


def derive_expected_irs(manifest_path: Path | str,
                        cache_dir: Path | str,
                        adapter_fn) -> dict[str, dict]:
    """Derive expected IRs from manifest with commitment identity verification.

    For each entry in manifest:
    1. Resolve lf_sha256 via resolve_bytes
    2. On cache miss/mismatch → raise OracleDrift
    3. ir = adapter_fn(lf_bytes)
    4. Verify canonical_sha256(ir) == entry["expected_ir_sha256"]
    5. On mismatch → raise OracleDrift
    6. Return {case_id: ir}

    Raises:
        OracleDrift: if any cache is unavailable or if adapter output doesn't
                     match the preregistered commitment hash.
    """
    manifest_path = Path(manifest_path)
    cache_dir = Path(cache_dir)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = manifest["entries"]

    expected_irs = {}

    for entry in entries:
        case_id = entry["case_id"]
        lf_sha256 = entry["lf_sha256"]
        expected_ir_sha256 = entry["expected_ir_sha256"]

        # Resolve lf bytes from cache
        result = resolve_bytes(lf_sha256, cache_dir)
        if result["execution"] != "ok":
            raise OracleDrift(
                f"Oracle unavailable for {case_id}: {result.get('reason', 'unknown error')}"
            )

        lf_bytes = result["data"]

        # Apply adapter to get IR
        ir = adapter_fn(lf_bytes)

        # Verify commitment identity: canonical_sha256(ir) must match expected
        computed_sha256 = canonical_sha256(ir)
        if computed_sha256 != expected_ir_sha256:
            raise OracleDrift(
                f"Oracle commitment mismatch for {case_id}: "
                f"expected {expected_ir_sha256}, got {computed_sha256}"
            )

        expected_irs[case_id] = ir

    return expected_irs


def ingest_outputs(plan_path: Path | str,
                   outputs: list[dict],
                   expected_irs: dict[str, dict],
                   *,
                   results_path: Path | str,
                   pass_min: int,
                   stratum_floors: dict | None = None,
                   certified: dict | None = None,
                   expected_unscorable: dict | None = None,
                   strata: dict | None = None) -> dict:
    """Ingest subject outputs, evaluate, score, and write results.

    Validates:
    - No duplicate trial_ids in outputs
    - All output trial_ids exist in plan

    For each PLAN trial (never iterate outputs — row loss must be impossible):
    - If no output for that trial_id → row result "error"
    - Elif output ir is not a dict → row result "error" (captured, not raised)
    - Else: evaluate(normalize(predicted), normalize(oracle)) and record result

    Builds score rows and calls score() to generate report.
    Writes results_path as deterministic JSON.

    Raises:
        ValueError: if duplicate or unknown trial_ids in outputs
        ResultsOverwriteRefused: if results_path already exists
    """
    plan_path = Path(plan_path)
    results_path = Path(results_path)

    # Load plan to get population
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan_trials = plan["trials"]
    provenance = plan["provenance"]

    # Build trial_id → output map and validate
    output_map = {}
    plan_trial_ids = {t["trial_id"] for t in plan_trials}

    # 적대검증(2026-08-23): 유령 trial_id를 나르는 map은 오탈자 신호 —
    # 조용한 미인증/미지정이 되기 전에 거부한다.
    for name, mp in (("certified", certified),
                     ("expected_unscorable", expected_unscorable),
                     ("strata", strata)):
        if mp:
            ghosts = set(mp) - plan_trial_ids
            if ghosts:
                raise ValueError(f"{name} names unknown trial_ids: {sorted(ghosts)}")

    for output in outputs:
        trial_id = output["trial_id"]

        # Check for duplicates in outputs
        if trial_id in output_map:
            raise ValueError(f"Duplicate trial_id in outputs: {trial_id}")

        # Check for unknown trial_ids
        if trial_id not in plan_trial_ids:
            raise ValueError(f"Unknown trial_id in outputs: {trial_id}")

        output_map[trial_id] = output

    # Build trial rows by iterating PLAN trials (ensuring no row loss)
    trial_rows = []

    for plan_trial in plan_trials:
        trial_id = plan_trial["trial_id"]
        case_id = plan_trial["case_id"]

        row = {
            "trial_id": trial_id,
            "case_id": case_id,
        }

        # Check if output exists for this trial
        if trial_id not in output_map:
            row["result"] = "error"
        else:
            output = output_map[trial_id]

            # Check if output ir is a dict
            if not isinstance(output.get("ir"), dict):
                row["result"] = "error"
            else:
                # Evaluate: normalize both sides and compare
                predicted_ir = output["ir"]
                oracle_ir = expected_irs[case_id]

                # 채점 = O1ScopeMatch, V2 투영 (D-E2E-v1-32/32-C): V1 전처리
                # (desugar·관용구 정규화·source별 granularity 다리) → V2
                # signature(제한식 opaque 붕괴 + and/or 정체 미채점)의 합성을
                # _stage2_projection_pipeline_v2가 계약으로 pin한다.
                ev = evaluate_scope_v2(case_id, predicted_ir, oracle_ir)
                row["result"] = ev["result"]
                if "mismatch_dimensions" in ev:
                    row["mismatch_dimensions"] = ev["mismatch_dimensions"]

                # 진단 축 (D-25 §16: predicate_label_identity = DIAGNOSTIC_ONLY)
                # — 기존 full-IR 비교(codec+desugar)를 별도 필드로 보존한다.
                # 채점에 절대 관여하지 않는다.
                dv = evaluate(
                    desugar(normalize_labels_for_case(case_id, predicted_ir)),
                    desugar(normalize_labels_for_case(case_id, oracle_ir)))
                row["diagnostic_label_identity"] = {
                    "result": dv["result"],
                    "mismatch_dimensions": sorted(dv.get("mismatch_dimensions", []))}

        # Add certification flag
        if certified and trial_id in certified:
            row["certified"] = bool(certified[trial_id])
        else:
            row["certified"] = False

        # Mark unscorable as expected (none are expected in this implementation)
        row["unscorable_expected"] = bool(
            expected_unscorable.get(trial_id)) if expected_unscorable else False
        if strata and trial_id in strata:
            row["stratum"] = strata[trial_id]

        trial_rows.append(row)

    # Score the trials
    report = score(
        trial_rows,
        n_preregistered=len(plan_trials),
        pass_min=pass_min,
        stratum_floors=stratum_floors
    )

    # Build result dict
    result = {
        "trial_rows": trial_rows,
        "report": report,
        "provenance": provenance,
    }

    # Refuse to overwrite results_path
    if results_path.exists():
        raise ResultsOverwriteRefused(
            f"{results_path.name} already exists and holds a preserved record. "
            f"Overwriting would destroy it irreversibly.\n\n"
            f"Use a different results_path."
        )

    # Write results deterministically
    results_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    return result


# ---------------------------------------------------------------- 코호트 수락 ---
# 드라이런(2026-08-24)이 적발한 구멍: `stratum_floors`가 선택 인자여서 **생략하면
# 사전등록이 금지한 수락이 조용히 통과한다.** 실측 — multi_quantifier 5건 중 1건만
# 통과하고 나머지 15건이 통과해 전체 16/20인 시나리오에서:
#
#     floors 전달  → accepted=False  floors_met=False  mq={'n':5,'pass':1}
#     floors 생략  → accepted=True                       ← 회피 성공
#
# 채점기 docstring이 정확히 이 회피를 명명하고 있었는데도 호출 측에서 도달
# 가능했다. 고치는 방향은 경고를 키우는 것이 아니라 **유도로 그 경로를 없애는
# 것**이다(동료 세션이 preflight의 `--manifest` 생략 구멍을 같은 방향으로 고쳤다).
#
# 아래 상수는 사전등록 산문의 **전사**다. 전사는 드리프트하므로
# `test_stage2_cohort_acceptance.py`가 원문과 대조해 고정한다.
COHORT_ACCEPTANCE = {
    # PREREGISTRATION_STAGE2_V4.md:40 — "N=20, PASS≥16 ∧ multi-quantifier
    # stratum 4/5 ∧ 최종 ERROR=0 ∧ 예상 밖 UNSCORABLE=0" (D-19·D-21·D-22 §2-3·§16)
    "n_preregistered": 20,
    "pass_min": 16,
    "stratum_floors": {"multi_quantifier": (5, 4)},
}


def derive_acceptance_inputs(manifest_path: Path | str,
                             plan_path: Path | str) -> dict:
    """수락 파라미터를 manifest·plan에서 **유도**한다 — 호출 측 생략을 막는다.

    `strata`(trial_id → stratum)는 manifest의 case별 stratum과 plan의
    trial→case 대응으로 유도한다. 손으로 적으면 그 지도가 드리프트한다.

    층 하한의 `n_min`은 manifest의 실제 stratum 크기와 대조한다 — manifest가
    바뀌면 조용히 통과하지 말고 여기서 멈춘다.

    Raises:
        ValueError: manifest의 stratum 구성이 사전등록 하한과 어긋날 때,
                    또는 plan의 case_id가 manifest에 없을 때.
    """
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    plan = json.loads(Path(plan_path).read_text(encoding="utf-8"))

    stratum_of_case = {e["case_id"]: e.get("stratum") for e in manifest["entries"]}
    n = len(manifest["entries"])
    if n != COHORT_ACCEPTANCE["n_preregistered"]:
        raise ValueError(
            f"manifest entries {n} != 사전등록 N "
            f"{COHORT_ACCEPTANCE['n_preregistered']} — 모집단이 바뀌었다")

    strata = {}
    for t in plan["trials"]:
        case_id = t["case_id"]
        if case_id not in stratum_of_case:
            raise ValueError(f"plan이 manifest에 없는 case를 가리킨다: {case_id}")
        strata[t["trial_id"]] = stratum_of_case[case_id]

    sizes: dict[str, int] = {}
    for s in strata.values():
        sizes[s] = sizes.get(s, 0) + 1
    for name, (n_min, _pass_min) in COHORT_ACCEPTANCE["stratum_floors"].items():
        actual = sizes.get(name, 0)
        if actual != n_min:
            raise ValueError(
                f"stratum {name!r} 크기 {actual} != 사전등록 하한의 n_min "
                f"{n_min} — manifest와 사전등록이 어긋났다")

    return {
        "pass_min": COHORT_ACCEPTANCE["pass_min"],
        "stratum_floors": dict(COHORT_ACCEPTANCE["stratum_floors"]),
        "strata": strata,
    }


def ingest_cohort(plan_path: Path | str,
                  outputs: list[dict],
                  expected_irs: dict[str, dict],
                  *,
                  manifest_path: Path | str,
                  results_path: Path | str,
                  certified: dict | None = None,
                  expected_unscorable: dict | None = None) -> dict:
    """본 코호트 채점의 **유일한 진입점.** 층 하한을 생략할 수 없다.

    `ingest_outputs`를 직접 부르면 `stratum_floors`를 빼먹을 수 있고 그러면
    사전등록이 금지한 수락이 통과한다(위 주석의 실측). 코호트는 이 함수로만
    채점한다 — `ingest_outputs`는 control·시험용으로 남긴다.
    """
    acc = derive_acceptance_inputs(manifest_path, plan_path)
    return ingest_outputs(
        plan_path, outputs, expected_irs,
        results_path=results_path,
        pass_min=acc["pass_min"],
        stratum_floors=acc["stratum_floors"],
        strata=acc["strata"],
        certified=certified,
        expected_unscorable=expected_unscorable,
    )
