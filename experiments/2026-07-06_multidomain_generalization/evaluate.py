"""multidomain_generalization 실험 채점 스크립트.

trials.json(클라이언트 LLM이 4개 도메인 × 3 trial로 생성한 concepts 입력)을
실제 파이프라인에 통과시켜 도메인별 is-a DAG 형성률을 결정적으로 계산한다.

에이전트 자기보고를 쓰지 않는다 — 채점은 전부 이 스크립트(코어 파이프라인)가 한다.

실행 (repo 루트에서):
    python3 experiments/2026-07-06_multidomain_generalization/evaluate.py

stdlib + repo 모듈만 사용.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from conceptgate.concept_gate_v7 import ConceptPipeline, ParseGate  # noqa: E402
from cg_input_linter import lint_concepts  # noqa: E402

CROSS_CODES = {"NO_SHARED_ESSENTIAL_LABELS", "ISA_CLAIM_FEATURE"}


def score(concepts):
    parsed, rep = ParseGate.parse(
        json.dumps({"concepts": concepts}, ensure_ascii=False))
    if not rep.passed:
        return {"status": "PARSE_FAIL", "edges": 0,
                "isolated": len(concepts), "cross": []}
    out = ConceptPipeline().run([parsed])
    r = out["result"]
    lint = lint_concepts(concepts)
    return {
        "status": out["status"],
        "edges": sum(len(v) for v in r["dag"].values()),
        "isolated": len(r["isolated"]),
        "cross": [i["code"] for i in lint["issues"] if i["code"] in CROSS_CODES],
    }


def main():
    data = json.load(open(os.path.join(HERE, "trials.json"), encoding="utf-8"))
    by_dom = {}
    print(f"{'domain':<10}{'trial':<6}{'status':<20}{'edges':<7}{'isolated':<9}cross-lint")
    for t in data["results"]:
        dom, tr = t["domain"], t["trial"]
        s = ({"status": "AGENT_ERR", "edges": 0, "isolated": 0, "cross": []}
             if "error" in t else score(t["concepts"]))
        print(f"{dom:<10}{tr:<6}{s['status']:<20}{s['edges']:<7}"
              f"{s['isolated']:<9}{','.join(s['cross']) or '-'}")
        by_dom.setdefault(dom, []).append(s["edges"])

    print()
    total_ok = total = 0
    for dom, es in by_dom.items():
        ok = sum(1 for e in es if e >= 3)
        total_ok += ok
        total += len(es)
        print(f"{dom:<10}: full-hierarchy(3+ edges) {ok}/{len(es)} | "
              f"mean edges {sum(es) / len(es):.1f}")
    print(f"\nTOTAL: {total_ok}/{total} trials formed the full is-a hierarchy")


if __name__ == "__main__":
    main()
