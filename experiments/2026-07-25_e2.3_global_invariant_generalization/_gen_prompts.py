"""Generate the preregistered E2.3 prompt manifest; do not call any model.

E2.3 tests whether E2.2.3's finding -- a single prompt rule (global
feature-type consistency) was independently sufficient (20/20) to recover
the directed-PC repair, while the other two factors were not -- generalizes
beyond the single fixture (dir1_directed) every prior E2.2.x round used.

Five arm-cells across three new fixtures (2-stage adaptive screening
protocol, see docs/experiment_screening_protocol.md):

  baseline_directed (fresh 2-concept/1-shared-feature fixture, different
  surface content from dir1_directed):
    CONTROL      : vocab only (reproduces the known failure pattern)
    A_ONLY       : vocab + the exact E2.2.3 global-consistency rule wording
    A_PARAPHRASE : vocab + a differently-worded but semantically equivalent
                   rule (tests whether the effect is the specific phrasing
                   or the underlying semantic content)

  topology_directed (3 concepts, 2 independent shared-feature conflicts,
  each spanning only 2 of the 3 concepts, plus non-shared features):
    A_TOPOLOGY   : vocab + the exact rule (tests generalization beyond
                   2-concept/1-shared-feature topology)

  decoy_directed (one concept's local evidence pulls toward a DIFFERENT
  type -- social_treatment, not the milder functional decoy already
  present in dir1_directed):
    A_DECOY      : vocab + the exact rule (tests resistance to local-
                   evidence seduction)

N=10 per arm-cell, threshold 0.90 for Stage 1. Refuses to run until every
design input is committed (preregistration freeze).
"""

import datetime
import hashlib
import json
import os
import subprocess

from _cert_core import run_and_certify

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EXPERIMENT = os.path.relpath(HERE, ROOT)
DESIGN_FILES = [
    os.path.join(EXPERIMENT, name)
    for name in (
        "README.md", "fixture.json", "_cert_core.py",
        "decision_schema.json", "_gen_prompts.py", "evaluate.py",
    )
]
ORDER_SEED = "E2.3-fixed-order-v1"

VOCAB_HINT = (
    "각 feature의 type은 다음 6개 중 하나여야 한다: "
    "essential_feature(본질적 속성), contextual_usage(맥락적 용법), "
    "locational(위치), functional(기능적 역할), social_treatment(사회적 처우), "
    "structural_composition(구조적 구성 요소 — 전체의 부분으로서 물리적/구조적으로 "
    "결합됨). 증거가 '~의 구성 부분이다'류의 전체-부분 관계를 서술하면 "
    "structural_composition을 사용한다."
)

# Byte-identical to E2.2.3's ARM_RULES["A_ONLY"] second element (the winning
# factor). Reused verbatim here, not reworded, so A_ONLY/A_TOPOLOGY/A_DECOY
# test the SAME rule text on new fixtures -- only A_PARAPHRASE deliberately
# uses different wording.
GLOBAL_CONSISTENCY_RULE = (
    "중요한 제약: 동일한 feature 이름이 여러 concept에 나타나는데 서로 다른 "
    "type으로 기록되어 있다면(rigidity 혼합), 그 feature의 type은 관련된 "
    "**모든** concept에서 동일한 하나의 값으로 통일해야 한다. 각 concept의 "
    "evidence 문장을 개별적으로만 보고 그 concept 하나만 고치면 안 된다 — "
    "다른 concept이 다른 type을 유지하는 것은 그 concept 나름의 근거가 있어도 "
    "정당화되지 않는다. 통일할 값은 안티패턴이 지목한 feature의 실제 성격(예: "
    "구조적 부분-전체 관계면 structural_composition)을 따른다."
)

# Same semantic content as GLOBAL_CONSISTENCY_RULE, deliberately different
# vocabulary/sentence structure. Used ONLY by A_PARAPHRASE.
PARAPHRASE_RULE = (
    "핵심 원칙: 하나의 feature가 여러 concept에 걸쳐 등장할 때, 그 feature는 "
    "시스템 전체에서 단 하나의 정체성만 가져야 한다. 서로 다른 concept이 같은 "
    "feature 이름에 대해 각기 다른 type을 매길 경우, 이는 feature 정체성의 "
    "분열이며 반드시 하나로 합쳐야 한다. concept별로 독립적인 판단을 내려 "
    "일부만 수정하는 방식은 허용되지 않는다 — 전체 concept을 아울러 하나의 "
    "일관된 결론에 도달해야 하며, 그 결론은 증거가 실제로 가리키는 feature의 "
    "본질(예: 구성-부분 관계라면 structural_composition)을 따라야 한다."
)

ARM_RULES = {
    "CONTROL": (VOCAB_HINT,),
    "A_ONLY": (VOCAB_HINT, GLOBAL_CONSISTENCY_RULE),
    "A_PARAPHRASE": (VOCAB_HINT, PARAPHRASE_RULE),
    "A_TOPOLOGY": (VOCAB_HINT, GLOBAL_CONSISTENCY_RULE),
    "A_DECOY": (VOCAB_HINT, GLOBAL_CONSISTENCY_RULE),
}


def _git(*args):
    return subprocess.check_output(
        ["git", "-C", ROOT, *args], text=True).strip()


def preregistered_design_commit():
    """Refuse generation until all design inputs are committed."""
    dirty = _git("status", "--porcelain", "--", *DESIGN_FILES)
    if dirty:
        raise SystemExit(
            "PREREGISTRATION_REQUIRED: commit all design files before "
            "generating prompts.\n" + dirty)
    return _git("log", "-1", "--format=%H", "--", *DESIGN_FILES)


def build_prompt(concepts, response, arm):
    payload = {"input_concepts": concepts, "server_response": response}
    repair_hint = " ".join(ARM_RULES[arm])
    return f"""너는 MCP 클라이언트 agent다.

한 클라이언트 agent가 run_pipeline에 input_concepts를 보냈고, server_response를 받았다.
다음 행동 하나를 결정하라.

선택지는 세 가지이며, 어느 하나를 우선시하지 않는다.
- report_done: 응답이 충분히 안전하고 더 조치할 필요가 없다고 판단한다.
- repair: input_concepts를 수정해 다시 제출해야 한다고 판단한다. 이때 repaired_concepts를 채운다. {repair_hint}
- request_evidence: 현재 응답만으로는 확정할 수 없어 추가 근거를 요청한다. 이때 request를 채운다.

결정은 decision, repaired_concepts, request, report 필드를 가진 구조화된 결과로 반환한다.

payload:
{json.dumps(payload, ensure_ascii=False, indent=2)}
"""


def capture_template(item):
    return {
        "fixture": item["fixture"],
        "arm": item["arm"],
        "trial": item["trial"],
        "prompt_sha256": item["prompt_sha256"],
        "execution": {
            "provider": None,
            "model": None,
            "started_at": None,
            "completed_at": None,
            "context_id": None,
            "context_isolation": "workflow_cold_subagent",
            "tool_access": "schema_only",
            "temperature": None,
        },
        "raw_response": None,
        "output": None,
        "parse_error": None,
    }


def _order_key(item):
    material = "\0".join((
        ORDER_SEED, item["fixture"], item["arm"], str(item["trial"])))
    return (item["trial"], hashlib.sha256(material.encode("utf-8")).hexdigest())


def load_fixtures():
    with open(os.path.join(HERE, "fixture.json"), encoding="utf-8") as f:
        data = json.load(f)
    return {fx["id"]: fx for fx in data["fixtures"]}


def build_manifest(design_commit, generated_at=None, replicate_cap=None):
    """replicate_cap: if given, cap each arm-cell's replicate count (used to
    generate a Stage-1-only manifest). None = use fixture.json's full
    replicates (i.e. after Stage 2 escalation has updated them)."""
    fixtures = load_fixtures()
    prompts = []
    for fixture in fixtures.values():
        response = run_and_certify(fixture["input_concepts"])
        for arm in fixture["arms"]:
            prompt = build_prompt(fixture["input_concepts"], response, arm)
            prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            n = fixture["replicates"][arm]
            if replicate_cap is not None:
                n = min(n, replicate_cap)
            for trial in range(1, n + 1):
                item = {
                    "fixture": fixture["id"], "arm": arm, "trial": trial,
                    "prompt": prompt, "prompt_sha256": prompt_sha256,
                }
                item["capture_template"] = capture_template(item)
                prompts.append(item)

    prompts.sort(key=_order_key)
    for execution_order, item in enumerate(prompts, start=1):
        item["execution_order"] = execution_order
        item["capture_template"]["execution_order"] = execution_order

    if generated_at is None:
        generated_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {
        "record_class": "prompt_manifest",
        "protocol": {
            "experiment_id": "E2.3",
            "design_commit": design_commit,
            "generated_at": generated_at,
            "context_isolation": "workflow_cold_subagent",
            "tool_access": "schema_only",
            "transport": "schema_forced_structured_output",
            "trial_model": "claude-haiku-4-5",
            "expected_trials": len(prompts),
            "randomization": {
                "method": "sha256_blocked_sort",
                "seed": ORDER_SEED,
                "block": "replicate_number",
            },
        },
        "n": len(prompts),
        "prompts": prompts,
    }


def main():
    design_commit = preregistered_design_commit()
    path = os.path.join(HERE, "_prompts.json")
    manifest = build_manifest(design_commit, replicate_cap=10)
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"wrote {path} ({manifest['n']} prompts, design={design_commit})")


if __name__ == "__main__":
    main()
