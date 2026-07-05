"""tool_description_ab 실험 채점 스크립트.

trials.json(클라이언트 LLM이 생성한 concepts 입력 10건)을 실제 파이프라인과
linter에 통과시켜 arm별 DAG 형성률을 결정적으로 계산한다.

에이전트 자기보고를 쓰지 않는다 — 채점은 전부 이 스크립트(코어 파이프라인)가 한다.

실행 (repo 루트에서):
    python3 experiments/2026-07-06_tool_description_ab/evaluate.py

stdlib + repo 모듈만 사용.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from concept_gate_v7 import ConceptPipeline, ParseGate  # noqa: E402
from cg_input_linter import lint_concepts  # noqa: E402

CROSS_CODES = {"NO_SHARED_ESSENTIAL_LABELS", "ISA_CLAIM_FEATURE"}


def score_trial(concepts):
    parsed, rep = ParseGate.parse(
        json.dumps({"concepts": concepts}, ensure_ascii=False))
    if not rep.passed:
        return {"status": "PARSE_FAIL", "edges": 0,
                "isolated": len(concepts), "lint_codes": []}
    out = ConceptPipeline().run([parsed])
    r = out["result"]
    lint = lint_concepts(concepts)
    return {
        "status": out["status"],
        "edges": sum(len(v) for v in r["dag"].values()),
        "isolated": len(r["isolated"]),
        "lint_codes": sorted({i["code"] for i in lint["issues"]}),
    }


def main():
    data = json.load(open(os.path.join(HERE, "trials.json"), encoding="utf-8"))
    rows = []
    for t in data["results"]:
        if "error" in t:
            rows.append((t["arm"], t["trial"],
                         {"status": "AGENT_ERR", "edges": 0,
                          "isolated": 4, "lint_codes": []}))
            continue
        rows.append((t["arm"], t["trial"], score_trial(t["concepts"])))

    print(f"{'arm':<4}{'trial':<6}{'status':<20}{'edges':<7}{'isolated':<9}cross-lint")
    for arm, trial, s in rows:
        cross = [c for c in s["lint_codes"] if c in CROSS_CODES]
        print(f"{arm:<4}{trial:<6}{s['status']:<20}{s['edges']:<7}"
              f"{s['isolated']:<9}{','.join(cross) or '-'}")

    for arm in ("A", "B"):
        sub = [s for a, _, s in rows if a == arm]
        full = sum(1 for s in sub if s["edges"] >= 3)
        cross = sum(1 for s in sub
                    if any(c in CROSS_CODES for c in s["lint_codes"]))
        print(f"\nARM {arm}: full-hierarchy(3+ edges) {full}/{len(sub)} | "
              f"mean edges {sum(s['edges'] for s in sub) / len(sub):.1f} | "
              f"cross-lint fired {cross}/{len(sub)}")


if __name__ == "__main__":
    main()
