#!/usr/bin/env python3
"""O1 Oracle Adapter 자격 실행기 (D-E2E-v1-21 Q21.4, 7항목).

Stage 1 run_stage1_qualification.py의 record_calibration 패턴 재사용:
spec을 적재해 검사를 실행하고 결과를 같은 json에 기록한다. 7항목 전 검사
match가 아니면 FAIL — 부분 점수 없음(판정 §20 pass_rule: all_required).

provenance에 adapter·cg_ir 소스 sha256을 기록한다. test_protocol.py가 이
값을 라이브 모듈 해시와 대조하므로, adapter가 이후에 바뀌면 이 자격은
자동으로 실효한다(판정 §18: Stage 2 준비상태는 자격된 그 코드에 결박).
"""
from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from conceptgate import cg_ir, cg_oracle_adapter as oa  # noqa: E402

SPEC_PATH = HERE / "adapter_qualification_controls.json"
PINNED_MODULES = ("cg_oracle_adapter.py", "cg_ir.py")


def module_source_sha256(name: str) -> str:
    raw = (REPO / "conceptgate" / name).read_text(encoding="utf-8")
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _canon(lf: str) -> str:
    return cg_ir.formula_fingerprint(oa.adapt(lf))


def run_check(check: dict) -> dict:
    kind = check["kind"]
    row = {"check_id": check["check_id"], "kind": kind}
    try:
        if kind == "adapt_ok":
            oa.adapt(check["lf"])
            row["observed"], row["match"] = "ok", True
        elif kind == "adapt_refused":
            try:
                oa.adapt(check["lf"])
                row["observed"], row["match"] = "accepted", False
            except (oa.AdapterUnsupported, oa.AdapterSyntaxError) as e:
                row["observed"] = type(e).__name__
                row["match"] = row["observed"] == check["expected_error"]
        elif kind == "hash_eq":
            row["observed"] = "eq" if _canon(check["lf_a"]) == _canon(check["lf_b"]) else "ne"
            row["match"] = row["observed"] == "eq"
        elif kind == "hash_ne":
            row["observed"] = "eq" if _canon(check["lf_a"]) == _canon(check["lf_b"]) else "ne"
            row["match"] = row["observed"] == "ne"
        elif kind == "replay_eq":
            row["observed"] = "eq" if oa.adapt(check["lf"]) == oa.adapt(check["lf"]) else "ne"
            row["match"] = row["observed"] == "eq"
        elif kind == "adapt_schema_valid":
            errors = cg_ir.validate_formula(oa.adapt(check["lf"]))
            row["observed"] = "valid" if not errors else f"invalid:{[e['code'] for e in errors]}"
            row["match"] = not errors
        elif kind == "free_vars":
            fv = sorted(cg_ir.free_variables(oa.adapt(check["lf"])))
            row["observed"] = fv
            row["match"] = fv == check["expected_free"]
        else:
            row["observed"], row["match"] = f"unknown kind {kind!r}", False
    except Exception as e:  # 예상 밖 crash도 기록 — 침묵은 데이터가 아니다
        row["observed"], row["match"] = f"raised {type(e).__name__}: {e}", False
    return row


def run_qualification() -> dict:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    results, failures = [], []
    for item in spec["items"]:
        rows = [run_check(c) for c in item["checks"]]
        item_pass = all(r["match"] for r in rows)
        results.append({"item_id": item["item_id"],
                        "item_pass": item_pass, "checks": rows})
        if not item_pass:
            failures.append(item["item_id"])
    return {"results": results, "failures": failures,
            "state": "passed" if not failures else "failed"}


def record_qualification() -> int:
    outcome = run_qualification()
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    spec["results"] = outcome["results"]
    spec["provenance"] = {
        "adapter_source_sha256": module_source_sha256("cg_oracle_adapter.py"),
        "cg_ir_source_sha256": module_source_sha256("cg_ir.py"),
        "python_version": platform.python_version(),
    }
    spec["qualification_state"] = "PASS" if outcome["state"] == "passed" else "FAIL"
    SPEC_PATH.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    n_items = len(outcome["results"])
    n_pass = sum(r["item_pass"] for r in outcome["results"])
    print(f"  items {n_pass}/{n_items} [{spec['qualification_state']}]")
    for f in outcome["failures"]:
        print(f"  FAIL {f}")
    return 0 if outcome["state"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(record_qualification())
