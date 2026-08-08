"""Freeze the E-A/E-B trial manifest -- exact prompt bytes, hashed, before any
trial runs. Mirrors H1a's manifest-freeze discipline at a scale appropriate
to a pre-adoption exploratory check (PREREGISTRATION.md sec 3): N=8/arm,
no bundle/randomization infrastructure since this is not a confirmatory
design.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import _contracts as contracts

HERE = Path(__file__).resolve().parent
N_PER_ARM = 8


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
                "trial_id": f"EA-{arm}-{r:02d}",
                "experiment": "E-A",
                "arm": arm,
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
                "trial_id": f"EB-{arm}-{r:02d}",
                "experiment": "E-B",
                "arm": arm,
                "prompt_sha256": _sha(prompt),
                "schema_name": "eb_response",
            })

    return {
        "record_class": "owl_entailment_cohort",
        "n_per_arm": N_PER_ARM,
        "expected_trials": len(trials),
        "rendered_prompts": rendered,
        "schemas": schemas,
        "trials": trials,
    }


def freeze() -> dict:
    manifest = build_manifest()
    out = HERE / "cohort_prompts.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


if __name__ == "__main__":
    m = freeze()
    print(f"wrote cohort_prompts.json ({m['expected_trials']} trials)")
