#!/usr/bin/env python3
"""Stage 1 measurement qualification 실행기 (H1a record_calibration 패턴).

control 8종을 cg_evaluate에 통과시켜 기대 범주와 대조하고, 결과를 corpus에
기록한다. 8/8이 아니면 qualification_state는 FAIL — 침묵하는 계측기의
침묵은 의미가 없다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from conceptgate import cg_evaluate  # noqa: E402

CONTROLS_PATH = HERE / "stage1_controls.json"


def run_qualification() -> dict:
    corpus = json.loads(CONTROLS_PATH.read_text(encoding="utf-8"))
    results, mismatches = [], []
    for c in corpus["controls"]:
        out = cg_evaluate.evaluate(c["predicted"], c["oracle"])
        row = {"control_id": c["control_id"], "expected": c["expected"],
               "observed": out["result"], "match": out["result"] == c["expected"],
               "detail": {k: out[k] for k in ("mismatch_dimensions", "reason")
                          if k in out and out[k]}}
        results.append(row)
        if not row["match"]:
            mismatches.append(row)
    return {"results": results,
            "matched": len(results) - len(mismatches),
            "cases": len(results),
            "state": "passed" if not mismatches else "failed",
            "mismatches": mismatches}


def record_qualification() -> int:
    outcome = run_qualification()
    corpus = json.loads(CONTROLS_PATH.read_text(encoding="utf-8"))
    corpus["results"] = outcome["results"]
    corpus["qualification_state"] = (
        "PASS" if outcome["state"] == "passed" else "FAIL")
    CONTROLS_PATH.write_text(
        json.dumps(corpus, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8")
    print(f"  {outcome['matched']}/{outcome['cases']} matched "
          f"[{corpus['qualification_state']}]")
    for m in outcome["mismatches"]:
        print(f"  MISMATCH {m['control_id']}: expected {m['expected']}, "
              f"observed {m['observed']}")
    return 0 if outcome["state"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(record_qualification())
