"""Generate the preregistered E2.2.3 prompt manifest; do not call any model.

E2.2.3 is a one-factor-at-a-time (OFAT) ablation of E2.2.2's combined fix.
E2.2.2 stacked THREE distinct interventions on top of the E2.2.1
vocab-exposure baseline and reached 20/20 (1.00), but combining them means
E2.2.2 alone cannot tell which factor(s) were necessary/sufficient:

  A. global-consistency: a feature name shared by multiple concepts must
     have ONE type across ALL of them (prompt rule).
  B. complete-state: repaired_concepts must return every input concept, not
     only the ones that changed (prompt rule).
  C. schema structural constraint: decision_schema.json's
     repaired_concepts.minItems=2 (fixture-specific structural enforcement
     of contract B).

This design isolates each factor into its own arm, all still on top of the
SAME vocab-exposure baseline shared by E2.2.1/E2.2.2 (vocab is constant
infrastructure, not one of the 3 ablated factors):

  A_ONLY : vocab + rule A only  (no rule B, no schema minItems)
  B_ONLY : vocab + rule B only  (no rule A, no schema minItems)
  C_ONLY : vocab only, no extra prompt rules at all - schema DOES carry
           minItems=2

N=20 per arm (60 trials total), same 0.80 pass-rate threshold, same
execution vehicle (Haiku, `e2.2-decider` agentType, schema-forced
structured output) as E2.2/E2.2.1/E2.2.2.

Refuses to run until every design input is committed (preregistration freeze).
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
ORDER_SEED = "E2.2.3-fixed-order-v1"

VOCAB_HINT = (
    "각 feature의 type은 다음 6개 중 하나여야 한다: "
    "essential_feature(본질적 속성), contextual_usage(맥락적 용법), "
    "locational(위치), functional(기능적 역할), social_treatment(사회적 처우), "
    "structural_composition(구조적 구성 요소 — 전체의 부분으로서 물리적/구조적으로 "
    "결합됨). 증거가 '~의 구성 부분이다'류의 전체-부분 관계를 서술하면 "
    "structural_composition을 사용한다."
)

GLOBAL_CONSISTENCY_RULE = (
    "중요한 제약: 동일한 feature 이름이 여러 concept에 나타나는데 서로 다른 "
    "type으로 기록되어 있다면(rigidity 혼합), 그 feature의 type은 관련된 "
    "**모든** concept에서 동일한 하나의 값으로 통일해야 한다. 각 concept의 "
    "evidence 문장을 개별적으로만 보고 그 concept 하나만 고치면 안 된다 — "
    "다른 concept이 다른 type을 유지하는 것은 그 concept 나름의 근거가 있어도 "
    "정당화되지 않는다. 통일할 값은 안티패턴이 지목한 feature의 실제 성격(예: "
    "구조적 부분-전체 관계면 structural_composition)을 따른다."
)

COMPLETE_STATE_RULE = (
    "중요한 제약: repaired_concepts에는 input_concepts에 있던 **모든** "
    "concept을 빠짐없이 포함해야 한다. 수정이 필요 없는 concept도 원래 "
    "형태 그대로 반드시 포함하라. 변경한 concept만 반환하는 부분 diff는 "
    "허용되지 않는다."
)

# Per-arm subset of rules inserted into the "repair" bullet. VOCAB_HINT is
# always present (constant infrastructure shared by every arm, per design -
# it is NOT one of the 3 ablated factors). This must stay in lockstep with
# decision_schema.json's arm_schema_map: A_ONLY/B_ONLY -> "no_minitems",
# C_ONLY -> "minitems_2" (the schema difference is the ONLY thing carrying
# factor C - C_ONLY's rule tuple below deliberately has no extra rule text).
ARM_RULES = {
    "A_ONLY": (VOCAB_HINT, GLOBAL_CONSISTENCY_RULE),
    "B_ONLY": (VOCAB_HINT, COMPLETE_STATE_RULE),
    "C_ONLY": (VOCAB_HINT,),
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


def build_manifest(design_commit, generated_at=None):
    fixtures = load_fixtures()
    prompts = []
    for fixture in fixtures.values():
        response = run_and_certify(fixture["input_concepts"])
        for arm in fixture["arms"]:
            prompt = build_prompt(fixture["input_concepts"], response, arm)
            prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            for trial in range(1, fixture["replicates"][arm] + 1):
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
            "experiment_id": "E2.2.3",
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
    manifest = build_manifest(design_commit)
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(f"wrote {path} ({manifest['n']} prompts, design={design_commit})")


if __name__ == "__main__":
    main()
