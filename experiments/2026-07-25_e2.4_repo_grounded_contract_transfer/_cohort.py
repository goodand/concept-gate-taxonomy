#!/usr/bin/env python3
"""Clean rerun cohort for E2.4 CONTRACT_REPO: freeze the surface, then record.

  python3 _cohort.py agent     -> regenerates + installs the trial subject
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

Cohort composition -- 30 trials, opaque ids only, matching Stage 1 of
../../../concept-gate-taxonomy/docs/experiment_screening_protocol.md
(N=10/cell; bands are calibrated for this N, not for the N=7/5/5 this
cohort was first frozen at -- see E2.4_ISSUE_REGISTER.md [GATE] G1):

    E24-F-01  x10    E24-F-02  x10    E24-F-03  x10

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

AGENT_NAME = "e2.4-contract-decider"
AGENT_FILE = HERE / f"{AGENT_NAME}.md"
AGENT_INSTALL_DIR = Path.home() / ".claude" / "agents"

# The trial subject's system prompt. It carries the output contract because the
# workflow transport rejects an output schema this size ("output schema too
# large to classify safely"), so the schema cannot be delivered through the
# structured-output channel. The frozen contract prompt already presupposes
# out-of-band delivery -- it says only "출력은 ... evidence_contract_v1 schema를
# 따른다" and names no fields -- so moving it here leaves rendered_prompt_sha256
# untouched.
#
# Consequence worth stating plainly: this file is part of the model-facing
# surface. freeze() hashes it as system_prompt_sha256 for exactly that reason.
#
# {schema_json} is filled from decision_schema.json, never typed by hand. Two
# hand-maintained copies of a schema drift, and a drift here would mean trials
# scored against a contract the model never saw.
AGENT_TEMPLATE = """---
name: {name}
description: E2.4 CONTRACT_REPO trial subject. Applies the frozen evidence contract to one repo-derived evidence packet and returns an evidence_contract_v1 decision. No tools, by design.
tools: []
---

You are the trial subject for one E2.4 CONTRACT_REPO trial.

The prompt you receive is the complete and only input. It contains the contract
rules and the evidence packet. Follow the contract exactly as written there;
these instructions add nothing to it and override nothing in it.

You have NO tools. Do not attempt to read files, search, run commands, browse a
repository, or consult any external source. In particular, do not try to look up
the repository the evidence was drawn from, and do not rely on any memory of it.
The packet's evidence items are the entire world for this decision.

Reason only from the packet, then return your decision.

## Output

Your entire final message must be one JSON object conforming to the
`evidence_contract_v1` schema below, and nothing else -- no prose before or
after, no markdown fence. Every listed property is required and no other
property is allowed.

{schema_json}
"""


def strip_descriptions(node):
    """decision_schema.json's descriptions document the contract for readers and
    the scorer. They are not part of what the trial subject is asked to produce,
    and carrying them would bloat the system prompt without changing the shape."""
    if isinstance(node, dict):
        return {k: strip_descriptions(v) for k, v in node.items() if k != "description"}
    if isinstance(node, list):
        return [strip_descriptions(v) for v in node]
    return node


def transport_schema() -> dict:
    schema = json.loads((HERE / "decision_schema.json").read_text(encoding="utf-8"))
    return strip_descriptions(schema["variants"]["evidence_contract_v1"]["schema"])


def agent_definition() -> str:
    return AGENT_TEMPLATE.format(
        name=AGENT_NAME,
        schema_json=json.dumps(transport_schema(), ensure_ascii=False, indent=2),
    )

# Opaque ids only. The oracle lives in oracle_manifest.json and is not read
# here -- this file must stay runnable by an operator who cannot see it.
COHORT = [("E24-F-01", 10), ("E24-F-02", 10), ("E24-F-03", 10)]

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


def schema_errors(value, schema, defs=None, path="$") -> list[str]:
    """Validate against the subset of JSON Schema decision_schema.json uses.

    Written rather than pulled in because `jsonschema` is not installed and the
    project keeps its tooling stdlib-only. Deliberately covers exactly the
    keywords in use -- an unrecognised keyword is silently ignored, so widening
    the schema without widening this function would quietly stop checking.

    Recorded outputs are validated here even when the transport already forced
    the schema: the transport's enforcement is not visible in the artifact, and
    a claim that all 17 outputs conform should rest on something re-runnable.
    """
    defs = schema.get("$defs", defs) or {}
    if "$ref" in schema:
        return schema_errors(value, defs[schema["$ref"].split("/")[-1]], defs, path)
    if "anyOf" in schema:
        if any(not schema_errors(value, s, defs, path) for s in schema["anyOf"]):
            return []
        return [f"{path}: matches no branch of anyOf"]

    errs: list[str] = []
    types = schema.get("type")
    if types:
        types = [types] if isinstance(types, str) else types
        ok = {
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "string": lambda v: isinstance(v, str),
            "boolean": lambda v: isinstance(v, bool),
            "null": lambda v: v is None,
        }
        if not any(ok[t](value) for t in types if t in ok):
            return [f"{path}: expected {'|'.join(types)}, got {type(value).__name__}"]

    if "enum" in schema and value not in schema["enum"]:
        errs.append(f"{path}: {value!r} not in {schema['enum']}")

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errs.append(f"{path}: missing required '{key}'")
        if schema.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errs.append(f"{path}: unexpected property '{key}'")
        for key, sub in props.items():
            if key in value:
                errs += schema_errors(value[key], sub, defs, f"{path}.{key}")
    elif isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errs += schema_errors(item, schema["items"], defs, f"{path}[{i}]")
    return errs


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

    # The output contract reaches the model through the trial subject's system
    # prompt, so both belong in the manifest. decision_schema_sha256 alone would
    # pin the file on disk while saying nothing about what was presented.
    system_prompt = agent_definition()
    if AGENT_FILE.read_text(encoding="utf-8") != system_prompt:
        raise SystemExit(
            f"{AGENT_FILE.name} is stale against decision_schema.json; "
            f"run `python3 _cohort.py agent` before freezing"
        )

    for fixture_id, n in COHORT:
        fixture, manifest, payload, contract, rendered, schema = build(fixture_id)
        prompts[fixture_id] = rendered
        for i in range(1, n + 1):
            trials.append({
                **surface.trial_manifest(
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
                                "arm": "CONTRACT_REPO", "tool_access": "no_tools",
                                "agent_type": AGENT_NAME},
                ),
                "system_prompt_sha256": surface.sha256_of(system_prompt),
                "presented_schema_sha256": surface.sha256_of(transport_schema()),
            })

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

    schema = transport_schema()
    records, malformed = [], {}
    for trial_id, manifest in sorted(by_id.items()):
        fixture_id = manifest["parameters"]["fixture_id"]
        if current[fixture_id] != manifest["rendered_prompt_sha256"]:
            raise SystemExit(
                f"{trial_id}: rendered prompt changed since freeze "
                f"({fixture_id}); cohort is void, re-freeze and re-run"
            )
        # Schema violations are recorded, not rejected. A trial that broke the
        # output contract is a result about the contract, and dropping it would
        # bias the cohort toward the trials that happened to comply.
        errs = schema_errors(raw[trial_id], schema)
        if errs:
            malformed[trial_id] = errs
        records.append({**manifest, "output": raw[trial_id],
                        "schema_violations": errs})

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
    if malformed:
        print(f"  {len(malformed)} with schema violations (kept, not dropped):")
        for tid, errs in malformed.items():
            for e in errs[:3]:
                print(f"    {tid}: {e}")
    return 0


def install_agent() -> int:
    """Regenerate the trial subject from decision_schema.json and install it.

    Two copies exist by necessity -- the committed one travels with the
    experiment, the installed one is what the agent registry reads -- so this
    writes both from one source and freeze() refuses to run if they disagree.
    """
    text = agent_definition()
    AGENT_FILE.write_text(text, encoding="utf-8")
    AGENT_INSTALL_DIR.mkdir(parents=True, exist_ok=True)
    (AGENT_INSTALL_DIR / f"{AGENT_NAME}.md").write_text(text, encoding="utf-8")
    print(f"  wrote {AGENT_FILE.name} and installed to {AGENT_INSTALL_DIR}")
    print("  NOTE: the agent registry is read at session start. A definition "
          "written mid-session is not resolvable until a new session.")
    return 0


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "freeze":
        raise SystemExit(freeze())
    if mode == "record":
        raise SystemExit(record())
    if mode == "agent":
        raise SystemExit(install_agent())
    raise SystemExit(__doc__)
