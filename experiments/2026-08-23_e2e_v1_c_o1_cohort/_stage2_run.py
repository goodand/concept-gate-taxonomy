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
from _stage2_eval_profile import normalize_predicate_labels
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
                   certified: dict | None = None) -> dict:
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

                # Apply evaluation profile normalization to both sides
                normalized_predicted = desugar(normalize_predicate_labels(predicted_ir))
                normalized_oracle = desugar(normalize_predicate_labels(oracle_ir))

                # Evaluate
                ev = evaluate(normalized_predicted, normalized_oracle)
                row["result"] = ev["result"]

                # Keep mismatch_dimensions if present (for fail/unscorable)
                if "mismatch_dimensions" in ev:
                    row["mismatch_dimensions"] = ev["mismatch_dimensions"]

        # Add certification flag
        if certified and trial_id in certified:
            row["certified"] = bool(certified[trial_id])
        else:
            row["certified"] = False

        # Mark unscorable as expected (none are expected in this implementation)
        row["unscorable_expected"] = False

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
