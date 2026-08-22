"""Stage 2 scoring module.

Metric definitions are D-E2E-v1-19 verbatim (§UCR·§8·§9):
  UCR = PASS / N_preregistered            (primary)
  DirectMatch = DirectPASS / N
  CertificationCoverage = Certified / N
  CertifiedCorrectYield = (Certified ∧ PASS) / N   ← denominator is N, not Certified
  P(PASS|Certified)                        (secondary diagnostic ONLY)
  2×2: A=Cert∧Pass, B=Cert∧¬Pass(=certification false-positive, first product metric),
       C=¬Cert∧Pass, D=¬Cert∧¬Pass

Acceptance criteria (D-E2E-v1-21-confirmed): PASS≥16 ∧ final ERROR=0 ∧ unexpected UNSCORABLE=0.

Why CertifiedCorrectYield uses N as denominator: dividing by certified_count would
allow a certifier that certifies almost nothing to appear perfect. The yield must be
held against the full preregistered set to expose certification sparsity.

Stratum floor addition (D-E2E-v1-22 §3·§16): When stratum_floors is provided,
acceptance additionally checks that each named stratum meets its pass minimum.
This prevents silent evasion by under-supplying rows within a stratum (§3 counterexample:
15 PMB passes + 1 multi_quantifier pass out of 5 = 16/20 PASS overall, but fails floor).
"""
from __future__ import annotations


def _assert_trial_rows_wellformed(trials: list[dict], n_preregistered: int) -> None:
    """Guard: validate trial rows match contract.

    Raises ValueError when:
    - Row count does not match n_preregistered (silent row loss is denominator manipulation)
    - Duplicate trial_id
    - Unknown result vocabulary
    - Missing required keys (stratum is optional)
    """
    if len(trials) != n_preregistered:
        raise ValueError(
            f"Row count mismatch: got {len(trials)}, expected {n_preregistered}"
        )

    required_keys = {"trial_id", "result", "certified", "unscorable_expected"}
    valid_results = {"pass", "fail", "unscorable", "error"}
    seen_ids = set()

    for trial in trials:
        # Check for missing required keys (stratum is optional)
        if not required_keys.issubset(trial.keys()):
            missing = required_keys - set(trial.keys())
            raise ValueError(f"Missing keys in trial: {missing}")

        # Check for duplicate trial_id
        trial_id = trial["trial_id"]
        if trial_id in seen_ids:
            raise ValueError(f"Duplicate trial_id: {trial_id}")
        seen_ids.add(trial_id)

        # Check result vocabulary
        result = trial["result"]
        if result not in valid_results:
            raise ValueError(f"Unknown result: {result}")


def score(
    trials: list[dict],
    n_preregistered: int,
    pass_min: int,
    stratum_floors: dict | None = None
) -> dict:
    """Score trials according to D-E2E-v1-19, D-E2E-v1-21, and D-E2E-v1-22.

    Args:
        trials: List of trial dicts with trial_id, result, certified, unscorable_expected,
                and optional stratum (string or None).
        n_preregistered: Expected number of trials (denominator for all metrics).
        pass_min: Minimum passing trials required for acceptance.
        stratum_floors: Optional dict mapping stratum name -> (n_min, pass_min) tuple.
                        When provided, acceptance additionally requires each named
                        stratum to have at least n_min rows with pass_min passes (§3 floor).
                        Absence of rows for a named stratum raises ValueError (silent evasion).

    Returns:
        Dict with counts, metrics, two_by_two, certification_false_positive_ids,
        acceptance, parameters, and optionally strata.
        When stratum_floors is None, acceptance and parameters retain ROUND 1 shape exactly.
    """
    # Guard
    _assert_trial_rows_wellformed(trials, n_preregistered)

    # Count by result
    counts = {"pass": 0, "fail": 0, "unscorable": 0, "error": 0}
    certified_count = 0
    certified_pass_count = 0

    for trial in trials:
        result = trial["result"]
        counts[result] += 1

        if trial["certified"]:
            certified_count += 1
            if result == "pass":
                certified_pass_count += 1

    # Metrics
    pass_count = counts["pass"]

    ucr = pass_count / n_preregistered
    direct_match = pass_count / n_preregistered
    cert_coverage = certified_count / n_preregistered
    certified_correct_yield = certified_pass_count / n_preregistered
    p_pass_given_certified = (
        certified_pass_count / certified_count
        if certified_count > 0
        else None
    )

    metrics = {
        "UCR": ucr,
        "DirectMatch": direct_match,
        "CertificationCoverage": cert_coverage,
        "CertifiedCorrectYield": certified_correct_yield,
        "P_pass_given_certified": p_pass_given_certified,
    }

    # 2x2 matrix
    a = certified_pass_count  # certified & pass
    b_count = 0
    b_ids = []
    c = 0
    d = 0

    for trial in trials:
        is_certified = trial["certified"]
        result = trial["result"]
        is_pass = result == "pass"

        if is_certified and is_pass:
            # A already counted above
            pass
        elif is_certified and not is_pass:
            # B: certified & not pass
            b_count += 1
            b_ids.append(trial["trial_id"])
        elif not is_certified and is_pass:
            # C: not certified & pass
            c += 1
        elif not is_certified and not is_pass:
            # D: not certified & not pass
            d += 1

    two_by_two = {
        "A": a,
        "B": b_count,
        "C": c,
        "D": d,
    }

    certification_false_positive_ids = sorted(b_ids)

    # Acceptance criteria (ROUND 1)
    error_count = counts["error"]
    pass_min_met = pass_count >= pass_min
    no_final_error = error_count == 0

    # Check no unexpected unscorable
    no_unexpected_unscorable = True
    for trial in trials:
        if trial["result"] == "unscorable" and not trial["unscorable_expected"]:
            no_unexpected_unscorable = False
            break

    # Stratum floor logic (ROUND 2)
    strata = None
    stratum_floors_met = None

    if stratum_floors is not None:
        # Count rows and passes per stratum
        stratum_counts = {}
        stratum_passes = {}

        for trial in trials:
            stratum = trial.get("stratum")  # None if absent
            result = trial["result"]

            if stratum not in stratum_counts:
                stratum_counts[stratum] = 0
                stratum_passes[stratum] = 0

            stratum_counts[stratum] += 1
            if result == "pass":
                stratum_passes[stratum] += 1

        # Build strata dict for named strata only
        strata = {}
        stratum_floors_met = True

        for stratum_name, (n_min, pass_min_stratum) in stratum_floors.items():
            n_actual = stratum_counts.get(stratum_name, 0)

            # Raise if declared stratum has insufficient rows
            if n_actual < n_min:
                raise ValueError(
                    f"Stratum '{stratum_name}' has {n_actual} rows, "
                    f"expected at least {n_min} (silent evasion)"
                )

            pass_actual = stratum_passes.get(stratum_name, 0)

            strata[stratum_name] = {
                "n": n_actual,
                "pass": pass_actual,
            }

            if pass_actual < pass_min_stratum:
                stratum_floors_met = False

    # Build acceptance dict
    if stratum_floors is not None:
        # ROUND 2: include stratum_floors_met
        acceptance = {
            "pass_min_met": pass_min_met,
            "no_final_error": no_final_error,
            "no_unexpected_unscorable": no_unexpected_unscorable,
            "stratum_floors_met": stratum_floors_met,
            "accepted": (pass_min_met and no_final_error and
                        no_unexpected_unscorable and stratum_floors_met),
        }
    else:
        # ROUND 1: exact previous shape (no stratum_floors_met)
        acceptance = {
            "pass_min_met": pass_min_met,
            "no_final_error": no_final_error,
            "no_unexpected_unscorable": no_unexpected_unscorable,
            "accepted": pass_min_met and no_final_error and no_unexpected_unscorable,
        }

    # Parameters
    if stratum_floors is not None:
        parameters = {
            "n_preregistered": n_preregistered,
            "pass_min": pass_min,
            "stratum_floors": stratum_floors,
        }
    else:
        # ROUND 1: exact previous shape (no stratum_floors key)
        parameters = {
            "n_preregistered": n_preregistered,
            "pass_min": pass_min,
        }

    # Build result dict
    result_dict = {
        "counts": counts,
        "metrics": metrics,
        "two_by_two": two_by_two,
        "certification_false_positive_ids": certification_false_positive_ids,
        "acceptance": acceptance,
        "parameters": parameters,
    }

    # Add strata only if stratum_floors was provided
    if strata is not None:
        result_dict["strata"] = strata

    return result_dict
