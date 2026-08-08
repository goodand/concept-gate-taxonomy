"""obligation_certificate_ab 실험 채점 스크립트.

trials.json(클라이언트 LLM의 결정 출력 10건)을 결정적으로 채점한다.
에이전트 자기보고를 쓰지 않는다 — repair 여부는 출력 JSON의 구조로,
수리 효과는 수리본을 실제 파이프라인 + certify에 통과시켜 판정한다.

실행 (repo 루트에서):
    venv/bin/python experiments/2026-07-18_obligation_certificate_ab/evaluate.py

stdlib + repo 모듈만 사용.
"""

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from conceptgate.concept_gate_v7 import ConceptPipeline, ParseGate  # noqa: E402
from conceptgate.cg_obligations import (  # noqa: E402
    certify, results_from_pipeline)


def _serialize_min(out):
    """채점에 필요한 축만 — server._serialize_pipeline_output의 부분집합."""
    return {
        "status": out["status"],
        "composition_issues": out.get("composition_issues", []),
        "anti_patterns": out.get("anti_patterns", []),
    }


def score_trial(output):
    """클라이언트 결정 출력 1건 → 채점 행.

    decision=repair면 수리본을 파이프라인+certify에 통과시켜
    post-repair verdict/anti_patterns를 계산한다 (자기보고 배제).
    """
    decision = output.get("decision")
    repaired = output.get("repaired_concepts")
    row = {"decision": decision or "INVALID", "post_status": "-",
           "post_anti": "-", "post_verdict": "-", "effective": False}
    if decision != "repair" or not repaired:
        return row
    try:
        parsed, rep = ParseGate.parse(
            json.dumps({"concepts": repaired}, ensure_ascii=False))
        if not rep.passed:
            row.update(post_status="PARSE_FAIL")
            return row
        out = ConceptPipeline().run([parsed])
        ser = _serialize_min(out)
        cert = certify(results_from_pipeline(ser))
        row.update(
            post_status=out["status"],
            post_anti=len(ser["anti_patterns"]),
            post_verdict=cert["verdict"],
            effective=(len(ser["anti_patterns"]) == 0
                       and cert["verdict"] == "pass"),
        )
    except Exception as exc:  # 수리본이 스키마 밖이면 무효 수리
        row.update(post_status=f"ERROR:{type(exc).__name__}")
    return row


def main():
    data = json.load(open(os.path.join(HERE, "trials.json"), encoding="utf-8"))
    rows = []
    for t in data["results"]:
        out = t.get("output") or {}
        rows.append((t["arm"], t["trial"], score_trial(out)))

    print(f"{'arm':<4}{'trial':<6}{'decision':<12}{'post_status':<20}"
          f"{'post_anti':<10}{'post_verdict':<13}effective")
    for arm, trial, s in rows:
        print(f"{arm:<4}{trial:<6}{s['decision']:<12}{s['post_status']:<20}"
              f"{str(s['post_anti']):<10}{s['post_verdict']:<13}"
              f"{s['effective']}")

    print()
    for arm in ("A", "B"):
        sub = [s for a, _, s in rows if a == arm]
        n = len(sub)
        repair = sum(1 for s in sub if s["decision"] == "repair")
        eff = sum(1 for s in sub if s["effective"])
        # 원 응답의 certificate verdict는 fixture상 fail —
        # 완료 보고는 전부 false-done이다.
        false_done = sum(1 for s in sub if s["decision"] == "report_done")
        print(f"ARM {arm}: repair {repair}/{n} | effective repair {eff}/{n}"
              f" | false-done {false_done}/{n}")


if __name__ == "__main__":
    main()
