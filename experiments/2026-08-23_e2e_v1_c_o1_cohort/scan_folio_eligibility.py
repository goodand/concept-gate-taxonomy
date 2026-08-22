#!/usr/bin/env python3
"""FOLIO v0.0의 O1 적격성 스캔 — Path A(실 adapter) + Path B(기호 census).

D-23 §15의 fixture eligibility 전 조건을 기계 판정한다:
  FOLIO source ∧ multi-quantifier(혼합 ∀·∃) ∧ 연산자 ⊆ FOLIO_FOL_V0 ∧
  번역 후 closed ∧ schema-valid ∧ **Path A = Path B**.
불일치는 FREEZE_BLOCKED(D-21 §15). 아울러 D-23 §17의 단순-양화 control
풀(단일 양화, N 밖 자격용)도 같은 스캔에서 산출한다.

출력: 문서 ID(example_id + premise index)·text/FOL sha256만 — 원문 0바이트.
입력: 로컬 캐시의 v0.0 jsonl (train sha256 008d34b7…, val 6922c988…).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO))

from conceptgate import cg_ir, cg_fol_adapter as fa  # noqa: E402

FORBIDDEN = "∨=⊕↔"
Q = re.compile(r"[∀∃]")


def path_b_class(fol: str) -> str:
    """기호 census만으로 분류 — adapter 무경유(독립 경로)."""
    if any(c in fol for c in FORBIDDEN):
        return "ineligible_operator"
    qs = Q.findall(fol)
    if len(qs) >= 2 and "∀" in qs and "∃" in qs:
        return "multi_mixed"
    if len(qs) == 1:
        return "single"
    return "other"


def path_a_class(fol: str) -> str:
    """실 adapter 경유."""
    try:
        ir = fa.adapt_fol(fol)
    except fa.AdapterUnsupported:
        return "ineligible_operator"
    except fa.AdapterSyntaxError:
        return "syntax"
    if cg_ir.validate_formula(ir) or cg_ir.free_variables(ir):
        return "invalid"
    kinds = set()
    def walk(n):
        if isinstance(n, dict):
            if "kind" in n: kinds.add(n["kind"])
            for v in n.values(): walk(v)
        elif isinstance(n, list):
            for v in n: walk(v)
    walk(ir)
    qs = Q.findall(fol)
    if "forall" in kinds and "exists" in kinds and len(qs) >= 2:
        return "multi_mixed"
    if len(qs) == 1:
        return "single"
    return "other"


def scan(files: list[Path]) -> dict:
    seen = set()
    out = {"multi_mixed": [], "single_controls": [],
           "mismatches": [], "counts": {}}
    tally = {"a": {}, "b": {}}
    for fp_ in files:
        for line in fp_.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            prems = rec.get("premises-FOL") or []
            txts = rec.get("premises") or []
            for i, fol in enumerate(prems):
                fol = fol.strip()
                if fol in seen:
                    continue
                seen.add(fol)
                a, b = path_a_class(fol), path_b_class(fol)
                tally["a"][a] = tally["a"].get(a, 0) + 1
                tally["b"][b] = tally["b"].get(b, 0) + 1
                ident = {"file": fp_.name,
                         "example_id": rec.get("example_id"),
                         "premise_index": i,
                         "story_id": rec.get("story_id"),
                         "folio_source_field": rec.get("source"),
                         "text_sha256": hashlib.sha256(
                             (txts[i] if i < len(txts) else "").encode()).hexdigest(),
                         "fol_sha256": hashlib.sha256(fol.encode()).hexdigest()}
                # 교차 판정: multi/single 자격은 두 경로 합의 필요
                if a == "multi_mixed" and b == "multi_mixed":
                    out["multi_mixed"].append(ident)
                elif a == "single" and b == "single":
                    out["single_controls"].append(ident)
                elif {a, b} & {"multi_mixed", "single"} and a != b:
                    out["mismatches"].append({**ident, "path_a": a, "path_b": b})
    out["counts"] = {"path_a": tally["a"], "path_b": tally["b"],
                     "agreed_multi_mixed": len(out["multi_mixed"]),
                     "agreed_single_controls": len(out["single_controls"]),
                     "mismatches": len(out["mismatches"])}
    return out


if __name__ == "__main__":
    files = [Path(a) for a in sys.argv[1:]]
    result = scan(files)
    print(json.dumps(result["counts"], ensure_ascii=False, indent=2))
    outp = HERE / "folio_eligibility_scan.json"
    outp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    print(f"written: {outp.name}")
