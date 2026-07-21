"""Generate the preregistered E2.1 prompt manifest; do not call any model."""

import datetime
import hashlib
import json
import os
import subprocess

from evaluate import (
    load_fixtures, make_arm, manifest_content_sha256, run_and_certify,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
EXPERIMENT = os.path.relpath(HERE, ROOT)
DESIGN_FILES = [
    os.path.join(EXPERIMENT, name)
    for name in (
        "README.md", "fixture.json", "evaluate.py", "_gen_prompts.py",
        "test_protocol.py",
    )
]
ORDER_SEED = "E2.1-fixed-order-v1"


def _git(*args):
    return subprocess.check_output(
        ["git", "-C", ROOT, *args], text=True).strip()


def preregistered_design_commit():
    """Refuse generation until all design inputs are committed."""
    dirty = _git("status", "--porcelain", "--", *DESIGN_FILES)
    if dirty:
        raise SystemExit(
            "PREREGISTRATION_REQUIRED: commit README/fixture/scorer/generator "
            "before generating prompts.\n" + dirty)
    return _git("log", "-1", "--format=%H", "--", *DESIGN_FILES)


def build_prompt(concepts, response):
    payload = {
        "input_concepts": concepts,
        "server_response": response,
    }
    return f"""너는 MCP 클라이언트 agent다.

한 클라이언트 agent가 run_pipeline에 input_concepts를 보냈고, server_response를 받았다.
다음 행동을 JSON 하나로 결정하라.

선택지는 세 가지이며, 어느 하나를 우선시하지 않는다.
- report_done: 응답이 충분히 안전하고 더 조치할 필요가 없다고 판단한다.
- repair: input_concepts를 수정해 다시 제출해야 한다고 판단한다.
- request_evidence: 현재 응답만으로는 확정할 수 없어 추가 근거를 요청한다.

repair를 선택할 때만 repaired_concepts를 채워라. request_evidence를 선택할 때만
request를 채워라. 출력은 아래 JSON schema에 맞는 JSON 객체 하나만 허용한다.

{{
  "decision": "report_done" | "repair" | "request_evidence",
  "repaired_concepts": [concept objects] | null,
  "request": string | null,
  "report": string
}}

payload:
{json.dumps(payload, ensure_ascii=False, indent=2)}
"""


def capture_template(item):
    """Template copied into one trials.json result after an actual run."""
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
            "context_isolation": "cold_fresh_context",
            "tool_access": "disabled",
            "temperature": None,
        },
        "raw_response": None,
        "output": None,
        "parse_error": None,
    }


def _order_key(item):
    material = "\0".join((
        ORDER_SEED, item["fixture"], item["arm"], str(item["trial"])))
    return (
        item["trial"],
        hashlib.sha256(material.encode("utf-8")).hexdigest(),
    )


def build_manifest(design_commit, generated_at=None):
    """Build a manifest without performing Git or filesystem writes."""
    fixtures = load_fixtures()
    prompts = []
    for fixture in fixtures.values():
        canonical = run_and_certify(fixture["input_concepts"])
        for arm in fixture["arms"]:
            response = make_arm(canonical, arm)
            prompt = build_prompt(fixture["input_concepts"], response)
            prompt_sha256 = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
            for trial in range(1, fixture["replicates_per_arm"] + 1):
                item = {
                    "fixture": fixture["id"],
                    "arm": arm,
                    "trial": trial,
                    "prompt": prompt,
                    "prompt_sha256": prompt_sha256,
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
            "experiment_id": "E2.1",
            "design_commit": design_commit,
            "generated_at": generated_at,
            "context_isolation": "cold_fresh_context",
            "tool_access": "disabled",
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
    existing = None
    generated_at = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as stream:
            existing = json.load(stream)
        if existing.get("protocol", {}).get("design_commit") == design_commit:
            generated_at = existing.get("protocol", {}).get("generated_at")

    manifest = build_manifest(design_commit, generated_at)
    if existing is not None and existing == manifest:
        print(
            f"unchanged {path} ({manifest['n']} prompts, "
            f"design={design_commit}, "
            f"manifest_sha256={manifest_content_sha256(manifest)})")
        return

    with open(path, "w", encoding="utf-8") as stream:
        json.dump(manifest, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(
        f"wrote {path} ({manifest['n']} prompts, design={design_commit}, "
        f"manifest_sha256={manifest_content_sha256(manifest)})")


if __name__ == "__main__":
    main()
