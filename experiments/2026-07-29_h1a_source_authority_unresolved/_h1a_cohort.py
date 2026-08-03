"""H1a cohort freeze harness -- builds cohort_prompts.json for the main
40-trial run (N=20/arm, PREREGISTRATION.md P1).

This module does not reimplement anything _h1a_surface.py or _h1a_contract.py
already do and test. It only adds what neither of those has: replicate/bundle
generation, execution-order fixing (PREREGISTRATION.md P2, same
sha256_blocked_sort pattern as
experiments/2026-07-25_e2.3_global_invariant_generalization/_gen_prompts.py),
and trial manifest assembly across both arms.

K=1 fixture (PREREGISTRATION.md 0): there is exactly one rendered prompt per
arm. All 20 replicates of an arm share that one prompt byte-for-byte -- R=20
resamples the same prompt, it does not vary fixture content per replicate.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import _h1a_surface as surface
import _h1a_contract as contract

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]  # concept-gate-h1-wt/

FIXTURE_PATH = HERE / "fixture_source_authority.json"
SCHEMA_PATH = HERE / "h1a_schema.json"
COHORT_PATH = HERE / "cohort_prompts.json"

# The trial subject's system prompt is a model-facing surface, and
# trial_manifest() does not hash it -- that function is E2.4's frozen copy
# (three documented deviations, pinned by test_h1a_surface_deviates_from_e2_4_
# only_where_documented), so the hash is added here at cohort level instead of
# editing it. E2.4 hit this exact hole: moving the output contract into the
# trial subject's system prompt left two model-facing surfaces unhashed, and
# `system_prompt_sha256`/`presented_schema_sha256` were added in response
# (HANDOFF.md §11.1). Recording it does not make the definition frozen; it
# makes a later edit to it detectable.
AGENT_DEFINITION_PATH = Path.home() / ".claude" / "agents" / "h1a-decider.md"
TRIAL_SUBJECT = "h1a-decider"

N_PER_ARM = 20
ORDER_SEED = "H1A-fixed-order-v1"
MODEL = "claude-opus-5"
PARAMETERS = {
    "sampling": "transport_default_unspecified",
    "tool_access": "no_tools",
    "context_isolation": "cold_subagent",
}


def _git_head() -> str:
    proc = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT),
        capture_output=True, text=True, check=True,
    )
    return proc.stdout.strip()


class SurfaceDrift(Exception):
    """Trial-subject definition no longer matches what the freeze assumes."""


def _trial_subject_surface() -> dict:
    """Hash the trial subject definition, and separately the system-prompt body
    the model actually receives.

    Two hashes, because they assert different things: the file hash notices any
    edit at all (including `tools:`), the body hash notices only what reaches
    the model. Also asserts `tools: []` here rather than trusting the
    description -- PREREGISTRATION.md P3 records `no_tools`, and the harness's
    own agent listing renders this agent as "All tools", so the definition file
    is the only place that claim can be checked.
    """
    raw = AGENT_DEFINITION_PATH.read_text(encoding="utf-8")
    parts = raw.split("---", 2)
    if len(parts) < 3:
        raise SurfaceDrift(f"{AGENT_DEFINITION_PATH}: no YAML frontmatter found")
    frontmatter, body = parts[1], parts[2]
    if "tools: []" not in frontmatter:
        raise SurfaceDrift(
            f"{AGENT_DEFINITION_PATH}: P3 requires the trial subject to have "
            f"`tools: []`; frontmatter says otherwise"
        )
    return {
        "trial_subject": TRIAL_SUBJECT,
        "definition_path": str(AGENT_DEFINITION_PATH),
        "definition_sha256": hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        "system_prompt_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "tools": [],
    }


def _order_key(bundle: int) -> tuple:
    """Same sha256_blocked_sort shape as E2.3's _gen_prompts.py::_order_key,
    blocked by bundle/replicate index -- bundle order only, since content is
    identical within an arm (K=1) and cannot itself be perturbed by order."""
    material = "\0".join((ORDER_SEED, str(bundle)))
    return (bundle, hashlib.sha256(material.encode("utf-8")).hexdigest())


def build_cohort() -> dict:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    schema_doc = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    decision_schema = schema_doc["variants"]["h1a_response"]["schema"]

    qualification = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=True)
    if qualification["status"] != "passed":
        raise surface.SurfaceError(f"fixture qualification failed: {qualification}")

    model_payload = surface.build_model_payload(fixture, qualification)
    surface.assert_no_model_facing_type_anchor(model_payload)

    template = contract.load_h1a_native_template()
    arm_templates = {arm: contract.render_arm(template, arm) for arm in contract.ARMS}

    # Structural guards -- run them here rather than trusting the test suite
    # ran them last (this module is a fresh, independent invocation).
    contract.assert_no_residual_prohibition(arm_templates["PROHIBITION_REMOVED"])
    ok, detail = contract.diff_is_restricted_to_the_liveness_clause(
        arm_templates["PROHIBITION_KEPT"], arm_templates["PROHIBITION_REMOVED"]
    )
    if not ok:
        raise contract.ContractDriftError(f"arm diff not restricted to liveness clause: {detail}")

    rendered_prompts = {
        arm: surface.render_prompt(arm_templates[arm], model_payload)
        for arm in contract.ARMS
    }

    builder_commit = _git_head()
    trial_subject = _trial_subject_surface()

    trials = []
    bundles = []
    for replicate in range(1, N_PER_ARM + 1):
        bundle_id = replicate
        order = _order_key(bundle_id)
        bundles.append({"bundle": bundle_id, "order_key": order[1]})
        for arm in contract.ARMS:
            trial_id = f"H1A-{arm}-{replicate:02d}"
            manifest = surface.trial_manifest(
                trial_id=trial_id,
                fixture=fixture,
                qualification_manifest=qualification,
                model_payload=model_payload,
                contract_prompt=arm_templates[arm],
                rendered_prompt=rendered_prompts[arm],
                decision_schema=decision_schema,
                builder_commit=builder_commit,
                model=MODEL,
                parameters=PARAMETERS,
            )
            trials.append({
                "trial_id": trial_id,
                "arm": arm,
                "replicate": replicate,
                "bundle": bundle_id,
                "manifest": manifest,
            })

    bundles.sort(key=lambda b: b["order_key"])
    for execution_order, b in enumerate(bundles, start=1):
        b["execution_order"] = execution_order
    bundle_order_by_id = {b["bundle"]: b["execution_order"] for b in bundles}
    for t in trials:
        t["execution_order"] = bundle_order_by_id[t["bundle"]]

    trials.sort(key=lambda t: (t["execution_order"], t["arm"]))

    return {
        "record_class": "prompt_manifest",
        "protocol": {
            "experiment_id": "H1a",
            "builder_commit": builder_commit,
            "context_isolation": "workflow_cold_subagent",
            "tool_access": "no_tools",
            "transport": "schema_forced_structured_output",
            "trial_model": MODEL,
            "expected_trials": len(trials),
            "n_per_arm": N_PER_ARM,
            "randomization": {
                "method": "sha256_blocked_sort",
                "seed": ORDER_SEED,
                "block": "bundle (paired replicate index across both arms)",
            },
            "stage_a_replicates": list(range(1, 6)),
            "stage_b_replicates": list(range(6, N_PER_ARM + 1)),
        },
        "trial_subject_surface": trial_subject,
        "fixture_sha256": surface.sha256_of(fixture),
        "qualification": qualification,
        "model_payload_sha256": surface.sha256_of(model_payload),
        "decision_schema": decision_schema,
        "rendered_prompts": rendered_prompts,
        "n": len(trials),
        "trials": trials,
    }


def freeze() -> dict:
    cohort = build_cohort()
    COHORT_PATH.write_text(
        json.dumps(cohort, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return cohort


def main() -> int:
    cohort = freeze()
    print(f"wrote {COHORT_PATH} ({cohort['n']} trials, "
          f"builder_commit={cohort['protocol']['builder_commit']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
