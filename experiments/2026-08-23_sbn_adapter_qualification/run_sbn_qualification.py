#!/usr/bin/env python3
"""SBN adapter 자격 실행기 (D-E2E-v1-22 §5-§6, 9항목).

record_calibration 계보(stage1 → wikisem adapter 자격과 동일): spec 적재 →
검사 실행 → 같은 json에 기록. 전 검사 match가 아니면 FAIL(부분 점수 없음).
provenance의 소스 sha256을 게이트가 라이브 모듈과 대조하므로 adapter 변경
시 자격은 자동 실효한다.

참조 재인코더(_reencode_universal)는 이 하네스의 장비다 — adapter는 복호
전용(ORACLE-10). 재인코더는 spec의 발명 형태 class(단항 술어 restriction +
이항 role body)만 다룬다. 자격 항목 9의 명제는 "복호∘재인코딩∘복호가 첫
복호와 α-동치"이지 "임의 IR을 인코딩할 수 있다"가 아니다.
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

from conceptgate import cg_ir, cg_sbn_adapter as sa  # noqa: E402

SPEC_PATH = HERE / "sbn_qualification_controls.json"
PINNED_MODULES = ("cg_sbn_adapter.py", "cg_ir.py")


def module_source_sha256(name: str) -> str:
    raw = (REPO / "conceptgate" / name).read_text(encoding="utf-8")
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _fp(sbn: str) -> str:
    return cg_ir.formula_fingerprint(sa.adapt_sbn(sbn))


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


def _reencode_universal(ir: dict) -> str:
    """forall IR → 참조 SBN(짝 NEGATION) — spec의 발명 class 한정."""
    if ir.get("kind") != "forall":
        raise ValueError("reference encoder handles forall roots only")
    lines = ["            NEGATION <1"]
    order: list[str] = []

    def emit_conjuncts(node, into, var_order):
        if node.get("kind") == "and":
            for a in node["args"]:
                emit_conjuncts(a, into, var_order)
        elif node.get("kind") == "exists":
            var_order.append(node["var"])
            emit_conjuncts(node["body"], into, var_order)
        elif node.get("kind") == "pred":
            into.append(node)
        else:
            raise ValueError(f"encoder class exceeded: {node.get('kind')}")

    # restriction: 첫 지시체 = forall var
    r_preds: list[dict] = []
    r_vars = [ir["var"]]
    emit_conjuncts(ir["restriction"], r_preds, r_vars)
    b_preds: list[dict] = []
    b_vars: list[str] = []
    emit_conjuncts(ir["body"], b_preds, b_vars)
    all_vars = r_vars + b_vars

    def line_for(owner_var, preds):
        # owner의 단항 synset pred가 행 머리, 나머지는 role 쌍
        head = next(p for p in preds
                    if len(p["args"]) == 1 and p["args"][0].get("name") == owner_var
                    and "." in p["name"])
        parts = [head["name"]]
        for p in preds:
            if p is head or len(p["args"]) != 2:
                continue
            if p["args"][0].get("name") != owner_var:
                continue
            tgt = p["args"][1]
            if tgt["kind"] == "entity":
                tok = f'"{tgt["name"]}"' if " " in tgt["name"] or tgt["name"][0].isupper() else tgt["name"]
            else:
                tok = f"{all_vars.index(tgt['name']) - all_vars.index(owner_var):+d}"
            parts.append(f"{p['name']} {tok}")
        return " ".join(parts)

    for v in r_vars:
        lines.append(line_for(v, r_preds))
    lines.append("            NEGATION <1")
    for v in b_vars:
        lines.append(line_for(v, b_preds))
    return "\n".join(lines)


def run_check(check: dict) -> dict:
    kind = check["kind"]
    row = {"check_id": check["check_id"], "kind": kind}
    try:
        if kind == "adapt_ok":
            sa.adapt_sbn(check["sbn"]); row["observed"], row["match"] = "ok", True
        elif kind == "adapt_refused":
            try:
                sa.adapt_sbn(check["sbn"]); row["observed"], row["match"] = "accepted", False
            except (sa.AdapterUnsupported, sa.AdapterSyntaxError) as e:
                row["observed"], row["match"] = type(e).__name__, True
        elif kind == "adapt_refused_msg":
            try:
                sa.adapt_sbn(check["sbn"]); row["observed"], row["match"] = "accepted", False
            except (sa.AdapterUnsupported, sa.AdapterSyntaxError) as e:
                row["observed"] = f"{type(e).__name__}: {e}"
                row["match"] = check["expected_in_message"] in str(e)
        elif kind == "fp_eq":
            row["observed"] = "eq" if _fp(check["sbn_a"]) == _fp(check["sbn_b"]) else "ne"
            row["match"] = row["observed"] == "eq"
        elif kind == "fp_ne":
            row["observed"] = "eq" if _fp(check["sbn_a"]) == _fp(check["sbn_b"]) else "ne"
            row["match"] = row["observed"] == "ne"
        elif kind == "replay_eq":
            row["observed"] = "eq" if sa.adapt_sbn(check["sbn"]) == sa.adapt_sbn(check["sbn"]) else "ne"
            row["match"] = row["observed"] == "eq"
        elif kind == "adapt_schema_valid":
            errors = cg_ir.validate_formula(sa.adapt_sbn(check["sbn"]))
            row["observed"] = "valid" if not errors else f"invalid:{[e['code'] for e in errors]}"
            row["match"] = not errors
        elif kind == "free_vars":
            fv = sorted(cg_ir.free_variables(sa.adapt_sbn(check["sbn"])))
            row["observed"], row["match"] = fv, fv == check["expected_free"]
        elif kind == "kind_census":
            ir = sa.adapt_sbn(check["sbn"])
            ks = _kinds(ir, set())
            ok = (ir.get("kind") == check["root_kind"]
                  and all(k in ks for k in check["must_contain"])
                  and all(k not in ks for k in check["must_not_contain"]))
            row["observed"] = {"root": ir.get("kind"), "kinds": sorted(ks)}
            row["match"] = ok
        elif kind == "round_trip":
            ir1 = sa.adapt_sbn(check["sbn"])
            sbn2 = _reencode_universal(ir1)
            ir2 = sa.adapt_sbn(sbn2)
            row["observed"] = {"reencoded": sbn2.count("\n") + 1,
                               "fp_equal": cg_ir.formula_fingerprint(ir1)
                                           == cg_ir.formula_fingerprint(ir2)}
            row["match"] = row["observed"]["fp_equal"] and ir1["kind"] == "forall"
        else:
            row["observed"], row["match"] = f"unknown kind {kind!r}", False
    except Exception as e:  # 예상 밖 crash도 기록
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
    spec["provenance"] = {
        "sbn_adapter_source_sha256": module_source_sha256("cg_sbn_adapter.py"),
        "cg_ir_source_sha256": module_source_sha256("cg_ir.py"),
        "python_version": platform.python_version(),
    }
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
