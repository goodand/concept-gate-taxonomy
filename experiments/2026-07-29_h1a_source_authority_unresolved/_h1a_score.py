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

import hashlib
import json
from collections import Counter
from pathlib import Path

import _coder
import _h1a_cohort as cohort_mod

HERE = Path(__file__).resolve().parent

STAGE_A_MAX_INVALID_RATE = 0.50  # P7 §7.1 condition 3

# 2026-08-18: which cohort is being scored is now a PARAMETER, not four module
# constants. Every path below comes from a `_h1a_cohort.CohortSpec`, which is
# the same object `build_cohort()`/`freeze()` already take -- so the manifest a
# run was frozen from and the files its scores land in cannot name different
# cohorts. main()'s docstring called this out as the missing half of the
# D-H1a-13 wiring; it is done here.
#
# The default stays ORIGINAL_COHORT so every existing caller and every recorded
# sha256 in COHORT_STATUS_20260803_nonidentifying.md still refers to the same
# bytes. Passing a spec is the supported way to score a second cohort.


def load_cohort(spec=None) -> dict:
    spec = spec or cohort_mod.ORIGINAL_COHORT
    return json.loads(spec.cohort_path.read_text(encoding="utf-8"))


def load_raw(spec=None) -> dict:
    spec = spec or cohort_mod.ORIGINAL_COHORT
    return json.loads(spec.raw_path.read_text(encoding="utf-8"))


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


def score(spec=None) -> dict:
    spec = spec or cohort_mod.ORIGINAL_COHORT
    cohort = load_cohort(spec)
    raw = load_raw(spec)

    _assert_manifest_belongs_to_the_spec(cohort, spec)
    freeze_proof = _assert_the_freeze_proof_is_recorded(spec)
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
        # Which cohort these numbers describe. Without it a score file is
        # ambiguous between three cohort identities that share this folder.
        "cohort_id": spec.cohort_id,
        "trial_id_prefix": spec.trial_id_prefix,
        "order_seed": spec.order_seed,
        "builder_commit": cohort["protocol"]["builder_commit"],
        "fixture_sha256": cohort["fixture_sha256"],
        "model_payload_sha256": cohort["model_payload_sha256"],
        "trial_subject_surface": cohort["trial_subject_surface"],
        "coder_calibration": calibration,
        # §7: the item-level values of the licensed source-evaluation path,
        # carried into the results so the basis of the arm contrast is
        # reconstructable from the score file alone.
        "licensed_source_evaluation_path": freeze_proof[
            "licensed_source_evaluation_path"
        ],
        "freeze_proof_manifest_sha256": freeze_proof["cohort_manifest_sha256"],
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


class ScoreOverwriteRefused(Exception):
    """main() would destroy a cohort's already-written scored output."""


class CohortIdentityMismatch(Exception):
    """The manifest being scored does not belong to the spec that named the
    output paths."""


class FreezeProofMissing(Exception):
    """§7's licensed-path record is absent or describes a different manifest."""


def _assert_the_freeze_proof_is_recorded(spec) -> dict:
    """PREREGISTRATION_TYPED_SCOPE_COHORT.md §7: `licensed_source_evaluation_path`
    의 항목별 값을 결과와 함께 기록한다.

    Enforced HERE, on the scoring path, rather than trusted to whoever runs the
    freeze. `build_cohort()` certified the freeze and then threw the proof away
    for every cohort built before 2026-08-18, so "record it" was an obligation
    with nothing checking it -- the same shape as the 2026-08-06 blocker where
    the policy layer existed but was not on the execution path.

    The proof must also be BOUND to the manifest actually being scored. A proof
    computed against different manifest bytes describes a different freeze, and
    would be indistinguishable from a correct one by inspection.
    """
    path = spec.freeze_proof_path
    if not path.exists():
        raise FreezeProofMissing(
            f"{path.name} is absent, so how the {spec.cohort_id!r} cohort's "
            f"freeze was certified is not recorded and §7's reporting "
            f"requirement cannot be met. Write it with "
            f"_h1a_cohort.write_freeze_proof(spec) BEFORE scoring -- it is "
            f"derived from the frozen manifest, so recording it after reading "
            f"results would still be honest, but leaving it absent means the "
            f"licensed-path contrast that licensed this freeze is unrecoverable."
        )
    proof = json.loads(path.read_text(encoding="utf-8"))
    actual = hashlib.sha256(spec.cohort_path.read_bytes()).hexdigest()
    if proof.get("cohort_manifest_sha256") != actual:
        raise FreezeProofMissing(
            f"{path.name} records cohort_manifest_sha256="
            f"{proof.get('cohort_manifest_sha256')!r} but "
            f"{spec.cohort_path.name} hashes to {actual!r}. The proof does not "
            f"describe the manifest being scored."
        )
    return proof


def _assert_manifest_belongs_to_the_spec(cohort: dict, spec) -> None:
    """The manifest and the output paths must name the SAME cohort.

    Three cohort identities share this folder (`H1A` preserved, `H1AR` designed
    but never run, `H1AT` typed-scope). Nothing in the manifest records
    `cohort_id` -- `build_cohort()` writes the protocol block but not the spec's
    id -- so the trial-id prefix is what is actually on disk to check against.

    This is the guard that stops the mirror-image of the freeze accident: not
    "wrote a manifest over another cohort's", but "read cohort A's manifest and
    wrote its scores to cohort B's filenames", which would be silent because
    both files would parse and both would look complete.

    The prefix is compared WITH the hyphen. `H1AT` and `H1A` share three
    characters, and `H1AT-KEPT-01".startswith("H1A")` is True -- comparing bare
    prefixes would classify every typed-scope trial as a preserved-cohort one.
    HANDOFF.md flags this hazard for exactly this reason.
    """
    expected = spec.trial_id_prefix + "-"
    wrong = sorted(
        t["trial_id"] for t in cohort["trials"]
        if not t["trial_id"].startswith(expected)
    )
    if wrong:
        raise CohortIdentityMismatch(
            f"{spec.cohort_path.name} holds trials whose ids do not carry "
            f"{expected!r}, so it is not the {spec.cohort_id!r} cohort's "
            f"manifest: {wrong[:4]}{' ...' if len(wrong) > 4 else ''}. "
            f"Scoring it into {spec.score_path.name} would file one cohort's "
            f"observations under another's identity. Pass the matching "
            f"CohortSpec instead."
        )


def main(spec=None) -> int:
    """⚠️ FAIL-CLOSED SINCE 2026-08-06 (F9, independent review 20260806 axis c).

    `_h1a_cohort.py::freeze()` refuses to overwrite the preserved original
    cohort's manifest. This function had no equivalent guard: running it
    unconditionally overwrote `trials.json` and `h1a_cohort_score.json`,
    which is exactly the preserved output `COHORT_STATUS_20260803_nonidentifying.md`
    rests its sha256 values on. Re-scoring for any reason (a coder fix, a
    repaired-cohort run wired to the same paths by mistake) would silently
    re-write those files in place -- the same irreversibility freeze() was
    fixed for, on the other half of the harness.

    Refuses whenever either output file already exists.

    2026-08-18: the "pending change" this docstring used to name is now DONE.
    The output paths live on `CohortSpec` alongside the manifest path, seed and
    trial-id prefix, so a second cohort scores to its own files instead of
    needing this refusal as its only protection. The refusal is now per-spec --
    it protects whatever `spec.trials_path`/`spec.score_path` point at, not only
    the original cohort's -- and deleting it is still not the way to re-score.
    """
    spec = spec or cohort_mod.ORIGINAL_COHORT
    for path in (spec.trials_path, spec.score_path):
        if path.exists():
            raise ScoreOverwriteRefused(
                f"{path.name} already exists and holds the {spec.cohort_id!r} "
                f"cohort's scored output. For the preserved 2026-08-03 cohort "
                f"that is the artifact COHORT_STATUS_20260803_nonidentifying.md "
                f"rests its sha256 values on. Re-running the scorer here would "
                f"overwrite it irreversibly.\n\n"
                f"A different cohort needs its own CohortSpec -- its own "
                f"cohort_path, raw_path, trials_path, score_path, order_seed "
                f"and trial_id_prefix. Score it with main(spec). Do not delete "
                f"this check to proceed."
            )
    result = score(spec)
    spec.trials_path.write_text(
        json.dumps({"records": result["records"]}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    summary = {k: v for k, v in result.items() if k != "records"}
    spec.score_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
