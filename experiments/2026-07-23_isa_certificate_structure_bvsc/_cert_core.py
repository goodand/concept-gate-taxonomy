"""Shared certify-core for E2.2 (B-C structure confirmatory experiment).

Copied verbatim from the frozen E2.1 scorer
(experiments/2026-07-19_isa_certificate_only_ab_clean_baseline/evaluate.py,
commit c0cddee) so builder / scorer / prompt-gen share one implementation and
cannot drift. The E2.1 file itself is NOT modified — this is a copy, per the
preregistration rule that E2.1 stays frozen.

Provides: run_and_certify (production wiring), the relation.is_a helpers, and
make_arm (A/C/B/FULL projection). make_arm derives C (_isa_warning_text) and B
(_isa_only_certificate) from the SAME relation.is_a result, so B and C carry
identical information content by construction — only the representation differs.
"""

import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)

from conceptgate.concept_gate_v7 import ConceptPipeline, ParseGate  # noqa: E402
from conceptgate.cg_obligations import (  # noqa: E402
    certify, results_from_isa, results_from_pipeline)


def _serialize_min(output):
    return {
        "status": output["status"],
        "dag": dict(output["result"]["dag"]),
        "composition_issues": output.get("composition_issues", []),
        "anti_patterns": output.get("anti_patterns", []),
    }


def run_and_certify(concepts):
    parsed, report = ParseGate.parse(
        json.dumps({"concepts": concepts}, ensure_ascii=False))
    if not report.passed:
        return {
            "status": "PARSE_FAIL",
            "dag": {},
            "composition_issues": [],
            "anti_patterns": [],
            "obligations": {"ok": False, "verdict": "fail", "results": []},
        }
    output = ConceptPipeline().run([parsed])
    serialized = _serialize_min(output)
    ontoclean_names = {c.name for c in parsed if c.ontoclean is not None}
    results = results_from_pipeline(serialized)
    results += results_from_isa(serialized["dag"], ontoclean_names)
    return {
        **serialized,
        "obligations": certify(results),
    }


def isa_results(canonical):
    return [
        result
        for result in canonical.get("obligations", {}).get("results", [])
        if result.get("obligation") == "relation.is_a"
    ]


def _isa_only_certificate(canonical):
    results = isa_results(canonical)
    if not results:
        verdict = "unknown"
    elif all(result.get("verdict") == "pass" for result in results):
        verdict = "pass"
    else:
        verdict = "unknown"
    return {
        "ok": verdict == "pass",
        "verdict": verdict,
        "errors": [],
        "results": results,
        "verifier": canonical.get("obligations", {}).get("verifier", {}),
    }


def _isa_warning_text(canonical):
    certificate = _isa_only_certificate(canonical)
    if not certificate["results"]:
        return "relation.is_a verdict=unknown; no relation.is_a result was emitted"
    result = certificate["results"][0]
    bits = [
        f"relation.is_a verdict={result.get('verdict')}",
        f"assurance={result.get('assurance')}",
    ]
    if result.get("reason"):
        bits.append(f"reason={result['reason']}")
    if result.get("evidence"):
        bits.append(f"evidence={result['evidence']}")
    return "; ".join(bits)


def make_arm(canonical, arm):
    """Project one canonical response into A/C/B/FULL views.

    A    : no obligations, no warning (silent baseline)
    C    : same relation.is_a content as a plaintext `warning` string
    B    : same relation.is_a content as a structured certificate
    FULL : the entire response as produced (positive controls)
    """
    projected = copy.deepcopy(canonical)
    if arm == "FULL":
        return projected
    projected.pop("obligations", None)
    if arm == "A":
        return projected
    if arm == "C":
        projected["warning"] = _isa_warning_text(canonical)
        return projected
    if arm == "B":
        projected["obligations"] = _isa_only_certificate(canonical)
        return projected
    raise ValueError(f"unknown arm: {arm}")
