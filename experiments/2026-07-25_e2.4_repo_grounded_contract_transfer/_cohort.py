#!/usr/bin/env python3
"""Clean rerun cohort for E2.4 CONTRACT_REPO: freeze the surface, then record.

  python3 _cohort.py freeze    -> writes cohort_prompts.json  (commit before running)
  python3 _cohort.py record    -> reads trials_raw.json, writes trials.json

Two steps on purpose. `freeze` is deterministic and produces the exact bytes
every trial will see, hashed per DESIGN_DECISION_surface_separation.md §6; it is
committed *before* any trial runs, so the surface cannot be adjusted after
seeing a result. `record` only attaches outputs to already-frozen trial ids and
recomputes the hashes to prove the surface did not move underneath the run.

Terminology (§8): this is a **clean rerun cohort**, not a re-score and not a
reproduction. The pre-migration prompts were never preserved byte-for-byte, and
they were rendered from v1 fixtures that leaked the expected verdict through
extraction_note. Nothing here is comparable to those numbers.

Cohort composition -- 17 trials, opaque ids only:

    E24-F-01  x7    E24-F-02  x5    E24-F-03  x5

E24-F-04 is excluded: closed as unobtainable from live, equal-strength evidence
in this repo (PROBLEM_2_conflicting.md §5.2). The schema class is retained. Max
attainable coverage for this cohort is therefore 3 classes, and certification
status before it runs is 0 classes.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

spec = importlib.util.spec_from_file_location("e24_surface_cohort", HERE / "_surface.py")
surface = importlib.util.module_from_spec(spec)
sys.modules["e24_surface_cohort"] = surface
spec.loader.exec_module(surface)

COHORT_VERSION = "e2.4-clean-rerun-cohort-v1"
MODEL = "claude-opus-5"

# Opaque ids only. The oracle lives in oracle_manifest.json and is not read
# here -- this file must stay runnable by an operator who cannot see it.
COHORT = [("E24-F-01", 7), ("E24-F-02", 5), ("E24-F-03", 5)]

FIXTURE_FILES = {
    "E24-F-01": "fixture_sufficient_consistent.json",
    "E24-F-02": "fixture_sufficient_repairable.json",
    "E24-F-03": "fixture_insufficient.json",
    "E24-F-04": "fixture_conflicting.json",
}


def head_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT),
        capture_output=True, text=True, check=True,
    ).stdout.strip()


def build(fixture_id: str):
    """fixture -> qualification -> payload -> rendered prompt, canonical path only."""
    fixture = json.loads((HERE / FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8"))
    manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=True)
    if manifest["status"] != "passed":
        raise SystemExit(f"{fixture_id}: qualification failed, refusing to freeze")
    payload = surface.build_model_payload(fixture, manifest)
    contract = surface.load_contract_prompt(HERE / "contract_prompt.md")
    rendered = surface.render_prompt(contract, payload)
    schema = json.loads((HERE / "decision_schema.json").read_text(encoding="utf-8"))
    return fixture, manifest, payload, contract, rendered, schema


def freeze() -> int:
    builder_commit = head_sha()
    trials, prompts = [], {}

    for fixture_id, n in COHORT:
        fixture, manifest, payload, contract, rendered, schema = build(fixture_id)
        prompts[fixture_id] = rendered
        for i in range(1, n + 1):
            trials.append(
                surface.trial_manifest(
                    trial_id=f"E24-R2-{fixture_id[-2:]}-{i:02d}",
                    fixture=fixture,
                    qualification_manifest=manifest,
                    model_payload=payload,
                    contract_prompt=contract,
                    rendered_prompt=rendered,
                    decision_schema=schema,
                    builder_commit=builder_commit,
                    model=MODEL,
                    parameters={"fixture_id": fixture_id, "replicate": i,
                                "arm": "CONTRACT_REPO", "tool_access": "schema_only"},
                )
            )

    # Trials of the same fixture must be byte-identical. If they are not, the
    # builder is not deterministic and no per-trial comparison means anything.
    for fixture_id, _ in COHORT:
        hashes = {t["rendered_prompt_sha256"] for t in trials
                  if t["parameters"]["fixture_id"] == fixture_id}
        if len(hashes) != 1:
            raise SystemExit(f"{fixture_id}: builder is not deterministic {hashes}")

    (HERE / "cohort_prompts.json").write_text(
        json.dumps(
            {
                "cohort_version": COHORT_VERSION,
                "note": "Frozen model-facing surface. Committed before any trial "
                        "ran. The prompt text here is exactly what the model "
                        "received; rendered_prompt_sha256 in each trial pins it.",
                "builder_commit": builder_commit,
                "rendered_prompts": prompts,
                "trials": trials,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    for fixture_id, n in COHORT:
        h = next(t["rendered_prompt_sha256"] for t in trials
                 if t["parameters"]["fixture_id"] == fixture_id)
        print(f"  {fixture_id}  x{n}  rendered_prompt_sha256={h[:16]}  "
              f"{len(prompts[fixture_id])} chars")
    print(f"\n  froze {len(trials)} trials -> cohort_prompts.json")
    return 0


def record() -> int:
    frozen = json.loads((HERE / "cohort_prompts.json").read_text(encoding="utf-8"))
    raw = json.loads((HERE / "trials_raw.json").read_text(encoding="utf-8"))

    by_id = {t["trial_id"]: t for t in frozen["trials"]}
    missing = sorted(set(by_id) - set(raw))
    extra = sorted(set(raw) - set(by_id))
    if missing or extra:
        raise SystemExit(f"trial id mismatch  missing={missing}  extra={extra}")

    # Re-derive the surface now and compare against what was frozen. A drift
    # here means the fixtures or prompt moved mid-cohort and the run is void.
    current = {}
    for fixture_id, _ in COHORT:
        _, _, _, _, rendered, _ = build(fixture_id)
        current[fixture_id] = surface.sha256_of(rendered)

    records = []
    for trial_id, manifest in sorted(by_id.items()):
        fixture_id = manifest["parameters"]["fixture_id"]
        if current[fixture_id] != manifest["rendered_prompt_sha256"]:
            raise SystemExit(
                f"{trial_id}: rendered prompt changed since freeze "
                f"({fixture_id}); cohort is void, re-freeze and re-run"
            )
        records.append({**manifest, "output": raw[trial_id]})

    (HERE / "trials.json").write_text(
        json.dumps(
            {
                "cohort_version": COHORT_VERSION,
                "surface_verified_at_record_time": True,
                "excluded": {
                    "E24-F-04": "no eligible fixture; see PROBLEM_2_conflicting.md 5.2"
                },
                "trials": records,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"  recorded {len(records)} trials -> trials.json")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "freeze":
        raise SystemExit(freeze())
    if mode == "record":
        raise SystemExit(record())
    raise SystemExit(__doc__)
