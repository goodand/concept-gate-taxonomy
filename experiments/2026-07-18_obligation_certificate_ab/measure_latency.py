"""실험 2 (관측): classify_owl per-call 지연 분포.

HermiT는 sync_reasoner 호출마다 Java subprocess를 새로 띄운다
(owlready2/reasoning.py). warm JVM gateway 도입 트리거
("세션당 >20회 또는 p95 누적 >60s") 판정에 쓸 per-call 분포를 기록한다.

Java 미가용이면 UNKNOWN 경로만 확인하고 지연 측정은 스킵한다 (fail-open).

실행 (repo 루트에서):
    venv/bin/python experiments/2026-07-18_obligation_certificate_ab/measure_latency.py

stdlib time.perf_counter + repo 모듈만.
"""

import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from conceptgate import server  # noqa: E402

N = 10
# 소형 고정 온톨로지 — primitive genus 사슬 (reasoner가 실제로 돌지만 사소)
OWL = {"concepts": [
    {"name": "Animal", "definition_kind": "primitive"},
    {"name": "Mammal", "definition_kind": "primitive", "genus": "Animal"},
    {"name": "Dog", "definition_kind": "primitive", "genus": "Mammal"},
]}


def main():
    # 1회 예열 호출로 경로/가용성 확인
    probe = server.classify_owl(OWL)
    if not probe.get("ok"):
        codes = [e.get("code") for e in probe.get("errors", [])]
        obl = probe.get("obligations", {})
        print(f"REASONER 미가용 — codes={codes}")
        print(f"owl.consistent verdict = "
              f"{obl.get('results', [{}])[0].get('verdict')} (UNKNOWN 기대)")
        print("지연 측정 스킵 (fail-open). Java 있는 환경에서 재실행할 것.")
        return

    samples = []
    for _ in range(N):
        t0 = time.perf_counter()
        server.classify_owl(OWL)
        samples.append((time.perf_counter() - t0) * 1000.0)

    samples.sort()
    p95 = samples[min(len(samples) - 1, int(0.95 * len(samples)))]
    print(f"classify_owl per-call 지연 (n={N}, ms):")
    print(f"  min    = {samples[0]:.0f}")
    print(f"  median = {statistics.median(samples):.0f}")
    print(f"  p95    = {p95:.0f}")
    print(f"  max    = {samples[-1]:.0f}")
    print(f"  합계   = {sum(samples):.0f}")
    print()
    # 트리거 환산
    budget_ms = 60_000
    n_to_budget = int(budget_ms / statistics.median(samples))
    print(f"median 기준 60s 예산 소진 호출 수 ≈ {n_to_budget}회/세션")
    print("→ 이 값이 실사용 세션당 호출 수보다 작으면 warm JVM gateway 검토.")


if __name__ == "__main__":
    main()
