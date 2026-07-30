#!/usr/bin/env python3
"""Descriptive statistics for the H3 pilot.  python3 _h3_score.py [trials.json]

This is NOT `_score.py`. That module scores the CONTRACT_REPO certification
cohort against a 0.90 threshold and emits certified/ambiguous bands. This one
must never do that: DESIGN_DECISION_H3.md D-H3-6 rules the pilot
**non-certifying**, because the three fixtures were selected using CONTRACT's
own results (PROBLEM_1_sufficient_consistent.md §1 records two candidate
fixtures discarded specifically because CONTRACT abstained on them). Estimating
CONTRACT's performance on material screened by CONTRACT is not an independent
test, so nothing here produces a pass/fail verdict or a superiority claim --
only observed action distributions on these packets.

Primary estimand (D-H3-3), computed on the common `action` field alone:

    Delta_CONTROL = P(defer | insufficient, CONTRACT_REPO_H3)
                  - P(defer | insufficient, CONTROL_REPO_H3)
    Delta_A       = P(defer | insufficient, CONTRACT_REPO_H3)
                  - P(defer | insufficient, A_REPO_H3)

`contract_assessment.contract_verdict` is diagnostic only and never the primary
outcome. It appears below in exactly one place -- the CONTRACT-internal
action/verdict mismatch rate, which is a self-consistency measure of the
contract, not a comparison between arms.

Stdlib only.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

ARMS = ("CONTROL_REPO_H3", "A_REPO_H3", "CONTRACT_REPO_H3")
ACTIONS = ("accept_report", "repair", "defer")
CONTRACT_ARM = "CONTRACT_REPO_H3"

# D-H3-3's hidden-oracle target action, by semantic class.
TARGET_ACTION = {
    "sufficient_consistent": "accept_report",
    "sufficient_repairable": "repair",
    "insufficient": "defer",
}
PRIMARY_CLASS = "insufficient"

# The oracle is read here and only here. _h3.py cannot reach it -- test_h3.py
# gate 5 asserts the renderer never so much as names the file, so no target
# action can leak into a prompt.
ORACLE_PATH = HERE / "oracle_manifest.json"

# contract_verdict values consistent with each common action, for the
# CONTRACT-internal self-consistency check (semantic_constraints 1-3).
VERDICT_FOR_ACTION = {
    "accept_report": {"sufficient_consistent"},
    "repair": {"sufficient_repairable"},
    "defer": {"insufficient_evidence", "conflicting_evidence", "out_of_scope"},
}


class ScoreError(Exception):
    """Raised when the inputs cannot support an honest statistic."""


def fixture_classes() -> dict[str, str]:
    oracle = json.loads(ORACLE_PATH.read_text(encoding="utf-8"))
    classes = {fid: spec["semantic_class"] for fid, spec in oracle["fixtures"].items()}
    # Cross-check the class->action table against the oracle's own
    # expected_decision, renaming abstain to the common vocabulary's defer. If
    # these ever disagree, the mapping in this file is stale and every number
    # below would be silently wrong.
    for fid, spec in oracle["fixtures"].items():
        cls = spec["semantic_class"]
        if cls not in TARGET_ACTION:
            continue
        expected = spec["expected_decision"]
        expected = "defer" if expected == "abstain" else expected
        if TARGET_ACTION[cls] != expected:
            raise ScoreError(
                f"{fid}: TARGET_ACTION[{cls}]={TARGET_ACTION[cls]!r} disagrees with "
                f"oracle_manifest expected_decision={expected!r}"
            )
    return classes


def load_trials(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["trials"]


def action_of(trial: dict) -> str | None:
    """The recorded action, or None when the output is not usable.

    A schema-invalid output is not repaired into a guess: it is counted as
    invalid and excluded from the action distribution, and the invalid rate is
    reported alongside every distribution so a shrinking denominator can never
    pass for a cleaner result.
    """
    if trial.get("schema_violations"):
        return None
    action = (trial.get("output") or {}).get("action")
    return action if action in ACTIONS else None


def cells(trials: list[dict], classes: dict[str, str]) -> dict[tuple[str, str], dict]:
    """(semantic_class, arm) -> counts."""
    out: dict[tuple[str, str], dict] = {}
    for trial in trials:
        params = trial["parameters"]
        key = (classes[params["fixture_id"]], params["arm"])
        cell = out.setdefault(key, {"n": 0, "invalid": 0, "actions": Counter()})
        cell["n"] += 1
        action = action_of(trial)
        if action is None:
            cell["invalid"] += 1
        else:
            cell["actions"][action] += 1
    return out


def rate(cell: dict, action: str) -> float | None:
    """Share of *all* trials in the cell taking `action`.

    The denominator is every trial, not just the schema-valid ones, because
    DESIGN_DECISION_H3.md §4 requires invalid responses to be treated as
    action-incorrect and the invalid rate reported separately -- both, not
    either. Dropping invalid outputs from the denominator would be a third
    thing nobody pre-registered, and it flatters whichever arm produces the
    most malformed output: an arm that emits garbage half the time would score
    on the half that parsed.
    """
    return None if cell["n"] == 0 else cell["actions"][action] / cell["n"]


def deltas(cell_map: dict) -> dict:
    """The primary estimand. None-safe: a missing cell yields None, not 0.0 --
    an absent comparison is not a zero difference."""
    contract = cell_map.get((PRIMARY_CLASS, CONTRACT_ARM))
    p_contract = rate(contract, "defer") if contract else None
    out = {"p_defer_insufficient": {}, "delta": {}}
    for arm in ARMS:
        cell = cell_map.get((PRIMARY_CLASS, arm))
        out["p_defer_insufficient"][arm] = rate(cell, "defer") if cell else None
    for arm in ARMS:
        if arm == CONTRACT_ARM:
            continue
        other = out["p_defer_insufficient"][arm]
        out["delta"][f"vs_{arm}"] = (
            None if p_contract is None or other is None else p_contract - other
        )
    return out


def defer_diagnostics(cell_map: dict) -> dict:
    """defer treated as a diagnostic positive: recall and precision as a pair.

    D-H3C-4 (DESIGN_DECISION_H3_CONFIRMATORY.md): a single
    Delta on P(defer | insufficient) cannot express both failure directions at
    once, because the arms differ in *where* they defer rather than how much.
    Recall alone rewards an arm that defers everywhere; precision alone rewards
    one that defers almost never. Reported together, neither is gameable.

        recall_defer    = P(defer | insufficient)
        precision_defer = P(insufficient | defer)

    POST HOC for the existing 45-trial pilot. This pair was adopted after the
    pilot's results were seen, so per D-H3C-4 it must not be applied
    retroactively as a confirmatory score -- it is descriptive here, and
    becomes a pre-registered primary metric only from the next cohort onward.
    """
    out = {}
    for arm in ARMS:
        defers = 0
        defers_on_target = 0
        n_primary = 0
        for (cls, cell_arm), cell in cell_map.items():
            if cell_arm != arm:
                continue
            defers += cell["actions"]["defer"]
            if cls == PRIMARY_CLASS:
                defers_on_target += cell["actions"]["defer"]
                n_primary += cell["n"]
        out[arm] = {
            "recall_defer": (defers_on_target / n_primary) if n_primary else None,
            "precision_defer": (defers_on_target / defers) if defers else None,
            "defers_total": defers,
            "defers_on_insufficient": defers_on_target,
        }
    return out


def secondary(trials: list[dict], cell_map: dict, classes: dict[str, str]) -> dict:
    false_defer = {}
    for cls in ("sufficient_consistent", "sufficient_repairable"):
        for arm in ARMS:
            cell = cell_map.get((cls, arm))
            if cell:
                false_defer[f"{cls}|{arm}"] = rate(cell, "defer")

    macro, invalid_rate = {}, {}
    for arm in ARMS:
        accuracies, n_total, n_invalid = [], 0, 0
        for cls, target in TARGET_ACTION.items():
            cell = cell_map.get((cls, arm))
            if not cell:
                continue
            n_total += cell["n"]
            n_invalid += cell["invalid"]
            hit = rate(cell, target)
            if hit is not None:
                accuracies.append(hit)
        macro[arm] = sum(accuracies) / len(accuracies) if accuracies else None
        invalid_rate[arm] = n_invalid / n_total if n_total else None

    # Contract self-consistency: does the diagnostic verdict agree with the
    # common action the same response reported? Disagreement is a fact about
    # the contract, not about the other arms, so it is reported on its own.
    mismatches, checked = [], 0
    for trial in trials:
        if trial["parameters"]["arm"] != CONTRACT_ARM:
            continue
        action = action_of(trial)
        if action is None:
            continue
        verdict = ((trial.get("output") or {}).get("contract_assessment") or {}).get(
            "contract_verdict"
        )
        checked += 1
        if verdict not in VERDICT_FOR_ACTION[action]:
            mismatches.append(
                {"trial_id": trial["trial_id"], "action": action, "contract_verdict": verdict}
            )

    return {
        "defer_diagnostics": defer_diagnostics(cell_map),
        "false_defer_rate": false_defer,
        "macro_action_accuracy": macro,
        "invalid_output_rate": invalid_rate,
        "contract_action_verdict_mismatch": {
            "checked": checked,
            "mismatched": len(mismatches),
            "rate": (len(mismatches) / checked) if checked else None,
            "cases": mismatches,
        },
    }


def score(path: Path) -> dict:
    classes = fixture_classes()
    trials = load_trials(path)
    cell_map = cells(trials, classes)

    distribution = {
        f"{cls}|{arm}": {
            "n": cell["n"],
            "invalid": cell["invalid"],
            **{action: cell["actions"][action] for action in ACTIONS},
            "target_action": TARGET_ACTION[cls],
        }
        for (cls, arm), cell in sorted(cell_map.items())
    }
    return {
        "record_class": "h3_pilot_descriptive",
        "certifying": False,
        "note": "Non-certifying pilot (D-H3-6). The three fixtures were selected "
                "using CONTRACT's own results, so this is not an independent test "
                "set and these numbers support no superiority claim.",
        "allowed_conclusion": (
            "Existence-level, descriptive, conditional on a fixed packet, a fixed "
            "model, and fixed parameters (D-H3C-1 = A, D-H3C-2 = existential). "
            "Permitted: 'the contract interface elicited different defer behavior "
            "from the comparison arms on this packet.' Not permitted: any "
            "class-general, insufficient-general, or repo-derived-general "
            "superiority claim -- those are not formally identified without a "
            "sampling frame and independent held-out fixtures."
        ),
        "repo_derived_provenance": {
            "note": "'repo-derived' does not mean the same thing for every class "
                    "(D-H3C new_constraints). Stating it per class is mandatory.",
            "insufficient": "actual repository source code",
            "sufficient_consistent": "a synthetic sentence reused from a prior "
                                     "experiment's frozen fixture (E2.3)",
            "sufficient_repairable": "a synthetic sentence reused from a prior "
                                     "experiment's frozen fixture (E2.2.1)",
        },
        "sampling_units": {
            "R": 5, "R_meaning": "model-sampling repetitions of one fixed packet",
            "K": 1, "K_meaning": "independent fixtures per class",
            "warning": "R is not K (D-H3C new_constraints). Raising R sharpens the "
                       "within-packet estimate and generalizes to nothing.",
        },
        "post_hoc_metrics": [
            "secondary.defer_diagnostics -- the recall/precision pair was adopted "
            "after these results were seen (D-H3C-4). Descriptive here; it is a "
            "pre-registered primary metric only from the next cohort onward, and "
            "must not be used retroactively as a confirmatory score."
        ],
        "source": path.name,
        "n_trials": len(trials),
        "action_distribution": distribution,
        "primary": deltas(cell_map),
        "secondary": secondary(trials, cell_map, classes),
    }


def main() -> int:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "h3_pilot_trials.json"
    if not path.exists():
        raise SystemExit(f"{path.name} not found; run `_h3.py record` first")
    result = score(path)
    (HERE / "h3_pilot_score.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"  {result['n_trials']} trials from {path.name}  [NON-CERTIFYING]\n")
    for key, cell in result["action_distribution"].items():
        counts = "  ".join(f"{a}={cell[a]}" for a in ACTIONS)
        star = "  <- target " + cell["target_action"]
        print(f"  {key:44s} n={cell['n']:2d} invalid={cell['invalid']}  {counts}{star}")

    primary = result["primary"]
    print("\n  primary -- P(defer | insufficient)")
    for arm, value in primary["p_defer_insufficient"].items():
        print(f"    {arm:20s} {'n/a' if value is None else f'{value:.2f}'}")
    for name, value in primary["delta"].items():
        print(f"    Delta {name:16s} {'n/a' if value is None else f'{value:+.2f}'}")

    secondary_stats = result["secondary"]
    print("\n  defer as a diagnostic positive  [POST HOC -- descriptive only, D-H3C-4]")
    for arm, d in secondary_stats["defer_diagnostics"].items():
        rec = "n/a" if d["recall_defer"] is None else f"{d['recall_defer']:.2f}"
        pre = "n/a" if d["precision_defer"] is None else f"{d['precision_defer']:.2f}"
        print(f"    {arm:20s} recall {rec}   precision {pre}   "
              f"({d['defers_on_insufficient']}/{d['defers_total']} defers on target)")

    print("\n  secondary")
    for key, value in secondary_stats["false_defer_rate"].items():
        print(f"    false-defer {key:42s} {'n/a' if value is None else f'{value:.2f}'}")
    for arm, value in secondary_stats["macro_action_accuracy"].items():
        print(f"    macro action accuracy {arm:20s} {'n/a' if value is None else f'{value:.2f}'}")
    for arm, value in secondary_stats["invalid_output_rate"].items():
        print(f"    invalid-output rate   {arm:20s} {'n/a' if value is None else f'{value:.2f}'}")
    mismatch = secondary_stats["contract_action_verdict_mismatch"]
    print(f"    contract action/verdict mismatch  {mismatch['mismatched']}/{mismatch['checked']}")
    for case in mismatch["cases"][:5]:
        print(f"      {case['trial_id']}: action={case['action']} verdict={case['contract_verdict']}")

    print("\n  -> h3_pilot_score.json")
    print("  Allowed conclusion (D-H3C-1=A, D-H3C-2=existential): existence-level "
          "and descriptive,")
    print("  conditional on a fixed packet, model, and parameters. No class-general "
          "or repo-derived-general")
    print("  superiority claim is identified without a sampling frame. R=5 is "
          "model-sampling repetition, not K.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
