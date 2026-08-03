"""H1a cohort scoring -- PREREGISTRATION.md P4/P5/P6/P7.

Written and committed BEFORE the trial outputs were read, for the same reason
the coder calibration corpus was committed with `results` empty: a scoring rule
authored after seeing the data is not a rule, it is a rationalization
(PREREGISTRATION.md P7 §7.2, and skills-catalog
`checker-recall-and-precision` procedure 1).

This module adds no coding logic. Every per-trial verdict comes from
`_coder.code()`, which reads only structure and never `rationale` (P5 §5.1).
What this module adds is the bookkeeping P4/P6/P7 specify around that call:
which trials are outcomes, which are transport failures to re-run, which
bundles are incomplete, and whether the Stage A harness-integrity gate passes.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import _coder
import _h1a_cohort as cohort_mod

HERE = Path(__file__).resolve().parent
COHORT_PATH = HERE / "cohort_prompts.json"
RAW_PATH = HERE / "trials_raw.json"
TRIALS_PATH = HERE / "trials.json"
SCORE_PATH = HERE / "h1a_cohort_score.json"

STAGE_A_MAX_INVALID_RATE = 0.50  # P7 §7.1 condition 3


def load_cohort() -> dict:
    return json.loads(COHORT_PATH.read_text(encoding="utf-8"))


def load_raw() -> dict:
    return json.loads(RAW_PATH.read_text(encoding="utf-8"))


def _assert_instrument_speaks() -> dict:
    """P5's coder is only trustworthy if its calibration still passes. A
    silent instrument's silence means nothing (skills-catalog pattern 8)."""
    status = _coder.run_calibration()
    if status["state"] != "passed":
        raise _coder.CoderError(
            f"coder calibration {status['state']} "
            f"({status['matched']}/{status['cases']}), refusing to score: "
            f"{status['mismatches']}"
        )
    # Drop the per-case rows -- the summary is what belongs in the score file.
    return {k: status[k] for k in ("coder_version", "cases", "matched", "state", "by_axis")}


def score() -> dict:
    cohort = load_cohort()
    raw = load_raw()

    expected = {t["trial_id"]: t for t in cohort["trials"]}
    calibration = _assert_instrument_speaks()

    unexpected = sorted(set(raw) - set(expected))
    missing = sorted(set(expected) - set(raw))
    if unexpected:
        raise ValueError(f"outputs present for trial ids not in the freeze: {unexpected}")

    # P4: transport failures are not outcomes. They are re-run, not recorded.
    transport_failures = sorted(
        tid for tid, out in raw.items() if out is None
    ) + missing

    records = []
    for tid, meta in expected.items():
        out = raw.get(tid)
        if out is None:
            records.append({
                "trial_id": tid, "arm": meta["arm"], "replicate": meta["replicate"],
                "category": None, "status": "transport_failure", "output": None,
            })
            continue
        records.append({
            "trial_id": tid, "arm": meta["arm"], "replicate": meta["replicate"],
            "category": _coder.code(out), "status": "recorded", "output": out,
        })

    # P4: only bundles where BOTH arms completed enter the comparison.
    by_replicate: dict[int, list] = {}
    for r in records:
        by_replicate.setdefault(r["replicate"], []).append(r)
    complete_replicates = sorted(
        rep for rep, rs in by_replicate.items()
        if len(rs) == 2 and all(r["status"] == "recorded" for r in rs)
    )
    incomplete_replicates = sorted(set(by_replicate) - set(complete_replicates))
    for r in records:
        r["in_comparison"] = r["replicate"] in complete_replicates

    def tally(pred) -> dict:
        counts = Counter(
            r["category"] for r in records
            if r["in_comparison"] and r["status"] == "recorded" and pred(r)
        )
        return {c: counts.get(c, 0) for c in _coder.CATEGORIES}

    arms = sorted({r["arm"] for r in records})
    per_arm = {arm: tally(lambda r, a=arm: r["arm"] == a) for arm in arms}

    # P7 §7.1 Stage A -- harness integrity only, on replicates 1-5.
    stage_a_reps = set(cohort["protocol"]["stage_a_replicates"])
    stage_a = {}
    for arm in arms:
        c = Counter(
            r["category"] for r in records
            if r["arm"] == arm and r["status"] == "recorded"
            and r["replicate"] in stage_a_reps
        )
        n = sum(c.values())
        rate = (c.get(_coder.INVALID, 0) / n) if n else 0.0
        stage_a[arm] = {
            "n": n,
            "invalid": c.get(_coder.INVALID, 0),
            "invalid_rate": rate,
            "passes_invalid_gate": rate < STAGE_A_MAX_INVALID_RATE,
        }

    stage_a_pass = (
        all(v["passes_invalid_gate"] for v in stage_a.values())
        and not transport_failures
    )

    return {
        "record_class": "h1a_cohort_score",
        "builder_commit": cohort["protocol"]["builder_commit"],
        "fixture_sha256": cohort["fixture_sha256"],
        "model_payload_sha256": cohort["model_payload_sha256"],
        "trial_subject_surface": cohort["trial_subject_surface"],
        "coder_calibration": calibration,
        "n_expected": cohort["n"],
        "n_recorded": sum(1 for r in records if r["status"] == "recorded"),
        "transport_failures": transport_failures,
        "complete_replicates": complete_replicates,
        "incomplete_replicates": incomplete_replicates,
        "per_arm": per_arm,
        "stage_a": stage_a,
        "stage_a_pass": stage_a_pass,
        "allowed_conclusion": (
            "Descriptive, packet-conditional only: under this one fixed fixture "
            "(K=1, 칼/철), this frozen prompt pair, this trial subject and this "
            "transport, the select_type/defer distribution did or did not differ "
            "between PROHIBITION_KEPT and PROHIBITION_REMOVED. PREREGISTRATION.md "
            "§0 forbids generalizing to other packets, to source-authority "
            "situations at large, or to any claim that either type is correct; "
            "D-H1a-7 forbids causal attribution; L3 forbids reading the code "
            "side's rhetorical advantage as evidence of code authority."
        ),
        "records": records,
    }


def main() -> int:
    result = score()
    TRIALS_PATH.write_text(
        json.dumps({"records": result["records"]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = {k: v for k, v in result.items() if k != "records"}
    SCORE_PATH.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
