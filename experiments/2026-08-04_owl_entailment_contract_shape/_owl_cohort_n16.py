"""Freeze the N=16/arm confirmatory-rerun trial manifest.

This is a SEPARATE, post-result cohort -- see PREREGISTRATION_N16.md for why
it may not be called an independent replication of the N=8 exploratory cohort
frozen by `_owl_cohort.py`. Reuses the frozen `_contracts.py` (arm renderers),
`_coder.py` (scoring, unchanged), and both fixtures byte-for-byte. Only N per
arm and the trial-id/cohort-id namespace change, so the N=8 cohort
(`cohort_prompts.json`, `trials.json`, `cohort_score.json`, `RESULTS.md`)
is never touched or merged with.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import _contracts as contracts

HERE = Path(__file__).resolve().parent
N_PER_ARM = 16
COHORT_ID = "owl_ea_eb_n16_confirmatory_20260805"


def _load_template(label: str) -> str:
    text = (HERE / "prompt_templates.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```text\n(.*?)```", text, re.DOTALL)
    if label == "ea":
        return blocks[0]
    if label == "eb":
        return blocks[1]
    raise ValueError(label)


def _sha(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def build_manifest() -> dict:
    fx_a = contracts.load_fixture("fixture_owl_entailment.json")
    fx_b = contracts.load_fixture("fixture_candidate_vs_entailed.json")
    schemas = json.loads((HERE / "schemas.json").read_text(encoding="utf-8"))

    ea_template = _load_template("ea")
    eb_template = _load_template("eb")

    rendered = {}
    trials = []

    for arm, render_fn in contracts.EA_ARMS.items():
        payload = render_fn(fx_a)
        payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
        prompt = ea_template.replace("{payload_json}", payload_json)
        rendered[f"E-A/{arm}"] = prompt
        for r in range(1, N_PER_ARM + 1):
            trials.append({
                "trial_id": f"N16-EA-{arm}-{r:02d}",
                "experiment": "E-A",
                "arm": arm,
                "key": f"E-A/{arm}",
                "prompt_sha256": _sha(prompt),
                "schema_name": "ea_response",
            })

    for arm, render_fn in contracts.EB_ARMS.items():
        payload = render_fn(fx_b)
        payload_json = json.dumps(payload, ensure_ascii=False, indent=2)
        prompt = eb_template.replace("{payload_json}", payload_json)
        rendered[f"E-B/{arm}"] = prompt
        for r in range(1, N_PER_ARM + 1):
            trials.append({
                "trial_id": f"N16-EB-{arm}-{r:02d}",
                "experiment": "E-B",
                "arm": arm,
                "key": f"E-B/{arm}",
                "schema_name": "eb_response",
                "prompt_sha256": _sha(prompt),
            })

    return {
        "record_class": "owl_entailment_cohort_n16_confirmatory",
        "cohort_id": COHORT_ID,
        "predecessor_cohort": "owl_entailment_contract_shape_n8_2026-08-05",
        "predecessor_preregistration": "PREREGISTRATION.md",
        "this_preregistration": "PREREGISTRATION_N16.md",
        "n_per_arm": N_PER_ARM,
        "expected_trials": len(trials),
        "rendered_prompts": rendered,
        "schemas": schemas,
        "trials": trials,
    }


def freeze() -> dict:
    manifest = build_manifest()
    out = HERE / "cohort_prompts_n16.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    m = freeze()
    print(f"wrote cohort_prompts_n16.json ({m['expected_trials']} trials)")
