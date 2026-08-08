#!/usr/bin/env python3
"""H1a behavioral coder.  python3 _coder.py calibrate | status

Classifies each response as `selection` / `deferral` / `invalid`, per
PREREGISTRATION.md P5 -- frozen before any trial ran.

Why this file is so short
-------------------------
Because the response schema already did the work. D-H1a-2/D-H1a-3 gave the
model a closed `decision` enum, so the coder reads structured fields and
returns a category. It is not an NLP judge and must never become one.

    The coder does not read `rationale`.

That single rule is the load-bearing one. This experiment measures the
boundary between selecting and deferring; if the coder may consult prose, then
hedged wording -- not the one manipulated sentence -- decides which side a
trial lands on, and the study measures the coder's leniency instead. The
calibration corpus is built around exactly that trap: seven selection cases
carry doubt-laden rationales, one of which literally says it should defer.

Contradictory field combinations are not read charitably. `decision=defer`
with a named type is invalid, not a lenient deferral: a model that cannot
report its own action consistently is an observation worth keeping, and
coercing it into a behavior erases it.

Stdlib only.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent

CODER_VERSION = "h1a-behavioral-coder-v1"
SCHEMA_PATH = HERE / "h1a_schema.json"
CALIBRATION_PATH = HERE / "h1a_coder_calibration.json"

SELECTION, DEFERRAL, INVALID = "selection", "deferral", "invalid"
CATEGORIES = (SELECTION, DEFERRAL, INVALID)

REQUIRED_KEYS = ("decision", "selected_type", "cited_evidence_ids", "rationale")

# Read from the schema rather than restated here: two hand-maintained copies of
# an enum drift, and a drift would mean coding against a contract the model
# never saw.
def _enum(*path: str) -> list:
    node = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    for key in path:
        node = node[key]
    return node


def decision_values() -> list:
    return _enum("variants", "h1a_response", "schema", "properties", "decision", "enum")


def selected_type_values() -> list:
    branches = _enum("variants", "h1a_response", "schema", "properties",
                     "selected_type", "anyOf")
    for branch in branches:
        if "enum" in branch:
            return branch["enum"]
    raise CoderError("selected_type has no enum branch in h1a_schema.json")


class CoderError(Exception):
    """Raised when the coder cannot be trusted to run, never to skip a case."""


def code(output) -> str:
    """The whole coding rule (PREREGISTRATION.md P5 §5.2).

    `rationale` is required to be present and a string, but its *content* is
    never inspected -- that is the point.
    """
    if not isinstance(output, dict):
        return INVALID
    if set(output) != set(REQUIRED_KEYS):
        return INVALID
    if not isinstance(output["rationale"], str):
        return INVALID
    if not isinstance(output["cited_evidence_ids"], list):
        return INVALID
    if not all(isinstance(item, str) for item in output["cited_evidence_ids"]):
        return INVALID

    decision, selected = output["decision"], output["selected_type"]
    if decision == "select_type" and selected in selected_type_values():
        return SELECTION
    if decision == "defer" and selected is None:
        return DEFERRAL
    return INVALID


# --------------------------------------------------------------------------
# calibration -- the instrument must speak before its silence means anything
# --------------------------------------------------------------------------

def calibration_corpus() -> dict:
    return json.loads(CALIBRATION_PATH.read_text(encoding="utf-8"))


def run_calibration() -> dict:
    corpus = calibration_corpus()
    results, mismatches = [], []
    for case in corpus["cases"]:
        observed = code(case["output"])
        row = {
            "case_id": case["case_id"],
            "axis": case["axis"],
            "expected": case["expected"],
            "observed": observed,
            "match": observed == case["expected"],
        }
        results.append(row)
        if not row["match"]:
            mismatches.append(row)
    return {
        "coder_version": CODER_VERSION,
        "cases": len(results),
        "matched": len(results) - len(mismatches),
        "state": "passed" if not mismatches else "failed",
        "by_axis": dict(Counter(r["axis"] for r in results)),
        "mismatches": mismatches,
        "results": results,
    }


def calibration_status() -> dict:
    """Whether the coder may be used on real trials at all."""
    corpus = calibration_corpus()
    recorded = corpus.get("results") or []
    if not recorded:
        return {"state": "not_run",
                "note": "calibration has not been run; coder output is not data yet"}
    mismatches = [r for r in recorded if not r.get("match")]
    return {
        "state": "passed" if not mismatches else "failed",
        "cases": len(recorded),
        "matched": len(recorded) - len(mismatches),
        "mismatches": mismatches,
    }


def record_calibration() -> int:
    outcome = run_calibration()
    corpus = calibration_corpus()
    corpus["results"] = outcome["results"]
    corpus["calibration_state"] = outcome["state"]
    corpus["coder_version"] = CODER_VERSION
    CALIBRATION_PATH.write_text(
        json.dumps(corpus, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"  {outcome['matched']}/{outcome['cases']} matched  "
          f"[{outcome['state'].upper()}]")
    for axis, n in sorted(outcome["by_axis"].items()):
        hits = sum(1 for r in outcome["results"] if r["axis"] == axis and r["match"])
        print(f"    {axis:12s} {hits}/{n}")
    for m in outcome["mismatches"]:
        print(f"    MISMATCH {m['case_id']}: expected {m['expected']}, got {m['observed']}")
    if outcome["mismatches"]:
        print("\n  The coder is NOT usable. Fix the coder -- not the corpus -- "
              "and re-run.\n  Editing a labelled case to match the coder is how "
              "an instrument gets\n  calibrated to itself.")
        return 1
    print(f"\n  -> {CALIBRATION_PATH.name} (results recorded)")
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "calibrate":
        return record_calibration()
    if mode == "status":
        print(json.dumps(calibration_status(), ensure_ascii=False, indent=2))
        return 0
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
