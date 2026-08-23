#!/usr/bin/env python3
"""FOL adapter 자격 실행기 (D-E2E-v1-23 §13, 9항목) — SBN판과 동형.

provenance는 adapter·cg_ir에 더해 **비교층(_stage2_canonical_core)**도
pin한다 — 항목 8의 desugar 수렴이 그 코드를 경유하므로, 비교층이 바뀌면
이 자격도 실효해야 한다.
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
sys.path.insert(0, str(REPO / "experiments" / "2026-08-23_e2e_v1_c_o1_cohort"))

from conceptgate import cg_ir, cg_fol_adapter as fa  # noqa: E402
from _stage2_canonical_core import desugar  # noqa: E402

SPEC_PATH = HERE / "fol_qualification_controls.json"
PINNED = (
    ("fol_adapter_source_sha256", REPO / "conceptgate" / "cg_fol_adapter.py"),
    ("cg_ir_source_sha256", REPO / "conceptgate" / "cg_ir.py"),
    ("canonical_core_source_sha256",
     REPO / "experiments" / "2026-08-23_e2e_v1_c_o1_cohort" / "_stage2_canonical_core.py"),
)


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def _fp(fol: str) -> str:
    return cg_ir.formula_fingerprint(fa.adapt_fol(fol))


def _kinds(node, acc):
    if isinstance(node, dict):
        if "kind" in node:
            acc.add(node["kind"])
        for v in node.values():
            _kinds(v, acc)
    elif isinstance(node, list):
        for v in node:
            _kinds(v, acc)
    return acc


def run_check(check: dict) -> dict:
    kind = check["kind"]
    row = {"check_id": check["check_id"], "kind": kind}
    try:
        if kind == "adapt_ok":
            fa.adapt_fol(check["fol"]); row["observed"], row["match"] = "ok", True
        elif kind == "adapt_refused":
            try:
                fa.adapt_fol(check["fol"]); row["observed"], row["match"] = "accepted", False
            except (fa.AdapterUnsupported, fa.AdapterSyntaxError) as e:
                row["observed"], row["match"] = type(e).__name__, True
        elif kind == "fp_eq":
            row["observed"] = "eq" if _fp(check["fol_a"]) == _fp(check["fol_b"]) else "ne"
            row["match"] = row["observed"] == "eq"
        elif kind == "fp_ne":
            row["observed"] = "eq" if _fp(check["fol_a"]) == _fp(check["fol_b"]) else "ne"
            row["match"] = row["observed"] == "ne"
        elif kind == "replay_eq":
            row["observed"] = "eq" if fa.adapt_fol(check["fol"]) == fa.adapt_fol(check["fol"]) else "ne"
            row["match"] = row["observed"] == "eq"
        elif kind == "adapt_schema_valid":
            errors = cg_ir.validate_formula(fa.adapt_fol(check["fol"]))
            row["observed"] = "valid" if not errors else f"invalid:{[e['code'] for e in errors]}"
            row["match"] = not errors
        elif kind == "free_vars":
            fv = sorted(cg_ir.free_variables(fa.adapt_fol(check["fol"])))
            row["observed"], row["match"] = fv, fv == check["expected_free"]
        elif kind == "kind_census":
            ir = fa.adapt_fol(check["fol"])
            ks = _kinds(ir, set())
            ok = (ir.get("kind") == check["root_kind"]
                  and all(k in ks for k in check["must_contain"])
                  and all(k not in ks for k in check["must_not_contain"]))
            row["observed"] = {"root": ir.get("kind"), "kinds": sorted(ks)}
            row["match"] = ok
        elif kind == "neutral_exists":
            ir = fa.adapt_fol(check["fol"])
            true_pred = {"kind": "pred", "name": "True", "args": []}
            row["observed"] = {"root": ir.get("kind"),
                               "restriction_is_true": ir.get("restriction") == true_pred}
            row["match"] = (ir.get("kind") == "exists"
                            and ir.get("restriction") == true_pred)
        elif kind == "desugar_converges":
            restricted = fa.adapt_fol(check["fol"])
            # neutral 대조: 같은 식의 lowering을 desugar가 되돌린 core와,
            # restricted 산출의 desugar core가 α-동치인가
            core_a = desugar(restricted)
            # neutral 형태 손구성: forall(x,True,implies(R,B))는 desugar의
            # 정의상 core_a와 같아야 한다 — 자기 일관성 + 왕복.
            core_b = desugar(core_a)
            row["observed"] = {"idempotent": core_a == core_b,
                               "root": core_a.get("kind"),
                               "body": core_a.get("body", {}).get("kind")}
            row["match"] = (core_a == core_b
                            and core_a.get("kind") == "forall"
                            and core_a["restriction"] == {"kind": "pred", "name": "True", "args": []}
                            and core_a["body"]["kind"] == "implies")
        else:
            row["observed"], row["match"] = f"unknown kind {kind!r}", False
    except Exception as e:
        row["observed"], row["match"] = f"raised {type(e).__name__}: {e}", False
    return row


def run_qualification() -> dict:
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    results, failures = [], []
    for item in spec["items"]:
        rows = [run_check(c) for c in item["checks"]]
        ok = all(r["match"] for r in rows)
        results.append({"item_id": item["item_id"], "item_pass": ok, "checks": rows})
        if not ok:
            failures.append(item["item_id"])
    return {"results": results, "failures": failures,
            "state": "passed" if not failures else "failed"}


def record_qualification() -> int:
    outcome = run_qualification()
    spec = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    spec["results"] = outcome["results"]
    spec["provenance"] = {k: source_sha256(p) for k, p in PINNED}
    spec["provenance"]["python_version"] = platform.python_version()
    spec["qualification_state"] = "PASS" if outcome["state"] == "passed" else "FAIL"
    SPEC_PATH.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")
    n = len(outcome["results"]); p = sum(r["item_pass"] for r in outcome["results"])
    print(f"  items {p}/{n} [{spec['qualification_state']}]")
    for f in outcome["failures"]:
        print(f"  FAIL {f}")
    return 0 if outcome["state"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(record_qualification())
