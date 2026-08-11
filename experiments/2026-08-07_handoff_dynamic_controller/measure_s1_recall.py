#!/usr/bin/env python3
"""Measure S1's recall against the independently authored fixture.

Amendment 35 (round 13, finding #7). This computation used to live inside
test_protocol.py, which WROTE results/s1_recall_measurement.json on every
pytest run -- making the test suite an artifact writer and putting it in
direct conflict with the append-only rule for results/. A test that
regenerates its own expectation cannot fail on a regression in it.

Now: this script produces the artifact, and the test only compares against
the committed one.

    python3 measure_s1_recall.py                       # print, write nothing
    python3 measure_s1_recall.py results/<new>.json    # write (refuses to
                                                       # overwrite)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _evaluator import _forbidden_terms_status_per_item  # noqa: E402
from run_calibration import load  # noqa: E402

FIXTURE = HERE / "s1_recall_fixture.json"


def measure() -> dict:
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    _, gold = load()

    per_case: dict[str, dict] = {}
    for item in fixture["items"]:
        cid = item["case_id"]
        terms = gold[cid].get("safety_forbidden_terms") or []
        if not terms:
            raise SystemExit(f"{cid} carries no safety terms; fixture is vacuous")
        hit = _forbidden_terms_status_per_item([item["sentence"]], terms) == "hit"
        bucket = per_case.setdefault(cid, {"caught": 0, "positives": 0,
                                           "missed": []})
        bucket["positives"] += 1
        if hit:
            bucket["caught"] += 1
        else:
            bucket["missed"].append(item["sentence"])

    # Negative controls: a refusal must never be scored as an endorsement.
    # Without these, `caught` could be raised to 6/6 by a matcher that fires
    # on everything -- which is the failure S1 already exhibited on live data
    # (100% false positives across 174 cells).
    false_positives = [
        item["sentence"] for item in fixture["negative_controls"]
        if _forbidden_terms_status_per_item(
            [item["sentence"]],
            gold[item["case_id"]].get("safety_forbidden_terms") or []) == "hit"]

    caught = sum(b["caught"] for b in per_case.values())
    positives = sum(b["positives"] for b in per_case.values())
    return {
        "fixture_version": fixture["version"],
        "per_case": per_case,
        "total_caught": caught,
        "total_positives": positives,
        "recall": round(caught / positives, 4),
        "false_positives_on_refusals": false_positives,
        "regenerable": "deterministic; produced by measure_s1_recall.py",
    }


def main(argv: list[str]) -> int:
    out = measure()
    text = json.dumps(out, ensure_ascii=False, indent=1)
    if len(argv) > 1:
        path = Path(argv[1])
        if path.exists():
            print(f"refusing to overwrite {path.name} (results/ is "
                  "append-only)", file=sys.stderr)
            return 2
        path.write_text(text + "\n", encoding="utf-8")
        print(f"-> {path}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
