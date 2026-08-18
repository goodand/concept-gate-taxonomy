"""Execution and persistence for the confirmatory cohort's trials.

WHY THIS EXISTS AS CODE RATHER THAN A ONE-OFF SCRIPT
The 2026-08-15 QF-SELECT run was dispatched by hand. Its outputs were valid
and its prompt was byte-correct, but the transport and the model were never
recorded, so neither could be established afterwards and the five trials had
to be re-run. `_h1a_qualification_run.py` was written in response, for the
diagnostics. This is its counterpart for the cohort that carries the actual
research question.

WHAT IS AND IS NOT ESTABLISHED BY THE PROVENANCE THIS WRITES
Stated plainly, because a checker that looks stronger than it is is worse
than no checker:

  ESTABLISHED from artifacts, independent of anyone's report --
    - the prompt bytes actually dispatched (hashed here from the dispatch
      plan this module wrote, then compared to the frozen manifest)
    - the trial ids dispatched and which arm each belonged to
    - the dispatch script that ran, by sha256 of the persisted script file:
      the model override and the schema forcing are written in that script,
      so a third party can read what was requested rather than trust a claim
    - that the outputs conform to the decision schema

  NOT ESTABLISHED, and recorded as self-report --
    - that the transport layer honored the model override it was given
    - that the sampling parameters were the defaults

  The second list is why `parameters.sampling` is
  `transport_default_unspecified` in the manifest rather than a number. This
  module does not close that gap and does not pretend to; it narrows it from
  "nothing recorded" to "what was requested is recorded and readable".
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import _h1a_cohort as cohort_mod

HERE = Path(__file__).resolve().parent

# The runner's OWN declarations of what its dispatch path does. Deliberately
# not read from the manifest: the guard in `_h1a_score.py` compares provenance
# to the manifest, and a runner that copied its values out of the manifest
# would make that comparison compare the manifest to itself -- true, and about
# the wrong object. These are what the dispatch script is required to do, and
# a disagreement with the manifest is meant to fail loudly.
TRANSPORT = "schema_forced_structured_output"
TRIAL_MODEL = cohort_mod.MODEL
TOOL_ACCESS = "no_tools"
CONTEXT_ISOLATION = "workflow_cold_subagent"

PLAN_NAME = "dispatch_plan_typed_scope.json"


# ==========================================================================
# REUSED FROM E2.4, NOT HAND-WRITTEN
#
# `schema_errors` below is a VERBATIM copy of
# `experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/_cohort.py::schema_errors`.
#
# Copied rather than imported, following this folder's established convention
# and for its documented reason: D-H1a-1 forbids retroactively changing E2.4's
# frozen implementation, and this repo has already had one experiment silently
# execute another's module (E2.4_ISSUE_REGISTER [DONE] #6). `_h1a_surface.py`
# is the same pattern -- an H1a-only copy pinned by a body-comparison test.
#
# The drift pin is `test_schema_errors_is_verbatim_from_e2_4` in
# test_h1a_cohort_run.py: it compares this function's source to E2.4's with
# `inspect.getsource`, so an edit on either side fails loudly instead of
# leaving two validators that disagree.
#
# WHY THIS FUNCTION AND NOT A DEPENDENCY
# Its own docstring states the reason it exists and the reason it matters
# here: "Recorded outputs are validated here even when the transport already
# forced the schema: the transport's enforcement is not visible in the
# artifact, and a claim that all N outputs conform should rest on something
# re-runnable." That is precisely the gap the independent review named -- the
# transport's schema forcing was self-report. Local validation converts part
# of it into an artifact-checkable fact. `jsonschema` is not installed and
# this project keeps its tooling stdlib-only.
# ==========================================================================

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


class DispatchError(Exception):
    """The dispatch plan, the outputs, or the manifest disagree."""


def build_dispatch_plan(spec=None) -> dict:
    """The 40 trials in the frozen execution order, with the prompt each gets.

    Reads the manifest and does not modify it. `execution_order` is
    bundle-level (20 bundles x 2 arms) because `randomization.block` is the
    paired replicate index -- the pairing is the design, not a defect, so the
    plan preserves it rather than flattening to 1..40.
    """
    spec = spec or cohort_mod.TYPED_SCOPE_COHORT
    cohort = json.loads(spec.cohort_path.read_text(encoding="utf-8"))
    prompts = cohort["rendered_prompts"]

    ordered = sorted(cohort["trials"],
                     key=lambda t: (t["execution_order"], t["arm"]))
    items = []
    for trial in ordered:
        prompt = prompts[trial["arm"]]
        actual = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
        recorded = trial["manifest"]["rendered_prompt_sha256"]
        if actual != recorded:
            raise DispatchError(
                f"{trial['trial_id']}: the prompt in `rendered_prompts` hashes "
                f"to {actual} but the trial manifest recorded {recorded}. The "
                f"frozen manifest is internally inconsistent; do not dispatch."
            )
        items.append({
            "trial_id": trial["trial_id"],
            "arm": trial["arm"],
            "replicate": trial["replicate"],
            "execution_order": trial["execution_order"],
            "prompt": prompt,
            "rendered_prompt_sha256": actual,
        })

    return {
        "record_class": "h1a_dispatch_plan",
        "cohort_id": spec.cohort_id,
        "cohort_manifest_sha256": hashlib.sha256(
            spec.cohort_path.read_bytes()).hexdigest(),
        "required_transport": TRANSPORT,
        "required_trial_model": TRIAL_MODEL,
        "required_tool_access": TOOL_ACCESS,
        "required_context_isolation": CONTEXT_ISOLATION,
        "trial_subject": cohort["trial_subject_surface"]["trial_subject"],
        "decision_schema": cohort["decision_schema"],
        "n": len(items),
        "items": items,
    }


def write_dispatch_plan(directory: Path, spec=None) -> Path:
    """Write the plan somewhere outside the repo (a scratch dir).

    It is a working file, not an experimental artifact: it contains only what
    the frozen manifest already contains, and the record that matters -- the
    hash of the bytes dispatched -- goes into the raw file's provenance.
    """
    plan = build_dispatch_plan(spec)
    path = Path(directory) / PLAN_NAME
    path.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    return path


def _assert_outputs_cover_the_plan(plan: dict, outputs: dict) -> None:
    """Every planned trial must have an entry, and no entry may be unplanned.

    A missing key and a `null` value are DIFFERENT: `null` is a recorded
    transport failure that P4 sends to re-run, while a missing key is an
    incomplete dispatch whose cause is unknown. Silently treating the second
    as the first would let a partially-executed cohort look like a
    fully-executed one with some failures.
    """
    planned = {item["trial_id"] for item in plan["items"]}
    got = set(outputs)
    missing, extra = sorted(planned - got), sorted(got - planned)
    if missing or extra:
        raise DispatchError(
            f"outputs do not cover the dispatch plan. missing={missing} "
            f"unplanned={extra}. Dispatch every planned trial, or record a "
            f"null for a transport failure -- do not omit the key."
        )


def _assert_outputs_conform_to_the_frozen_schema(plan: dict, outputs: dict) -> dict:
    """Validate every recorded output against the FROZEN decision schema.

    Independent review 2026-08-18 finding P1: `transport:
    schema_forced_structured_output` was the runner's own claim, unverifiable
    from any artifact. This does not verify that the transport forced the
    schema -- it verifies the proposition that mattered downstream, that the
    outputs conform to it, and it does so re-runnably from the artifact by
    anyone.

    A `null` is a transport failure, not a non-conforming output: P4 sends it
    to re-run rather than recording it as an outcome, so it is counted and
    skipped, not reported as a schema violation.
    """
    schema = plan["decision_schema"]
    violations, conforming, failures = {}, 0, 0
    for item in plan["items"]:
        out = outputs.get(item["trial_id"])
        if out is None:
            failures += 1
            continue
        errs = schema_errors(out, schema)
        if errs:
            violations[item["trial_id"]] = errs
        else:
            conforming += 1
    if violations:
        raise DispatchError(
            f"{len(violations)} recorded output(s) do not conform to the frozen "
            f"decision schema, so they were not produced under "
            f"`schema_forced_structured_output` as the manifest requires: "
            f"{json.dumps(violations, ensure_ascii=False)[:800]}"
        )
    return {
        "validator": "e2.4_cohort_schema_errors_verbatim",
        "schema_sha256": hashlib.sha256(
            json.dumps(schema, ensure_ascii=False, sort_keys=True)
            .encode("utf-8")).hexdigest(),
        "outputs_checked": conforming,
        "transport_failures_skipped": failures,
        "violations": 0,
    }


def build_raw(plan: dict, outputs: dict, *, dispatch_script_sha256: str,
             run_date: str, notes: str | None = None) -> dict:
    """Assemble the raw artifact `_h1a_score.py` will require.

    `rendered_prompt_sha256_by_arm` comes from the PLAN -- the bytes this
    module verified and handed to the dispatcher -- not from the manifest.
    That is what makes the scorer's comparison a real check rather than the
    manifest agreeing with itself.
    """
    _assert_outputs_cover_the_plan(plan, outputs)
    conformance = _assert_outputs_conform_to_the_frozen_schema(plan, outputs)

    by_arm: dict[str, set[str]] = {}
    for item in plan["items"]:
        by_arm.setdefault(item["arm"], set()).add(item["rendered_prompt_sha256"])
    for arm, hashes in by_arm.items():
        if len(hashes) != 1:
            raise DispatchError(
                f"arm {arm} was dispatched with {len(hashes)} distinct prompts; "
                f"the arms must each be a single surface"
            )

    cohort = json.loads(
        cohort_mod.TYPED_SCOPE_COHORT.cohort_path.read_text(encoding="utf-8"))
    schema_hashes = {t["manifest"]["decision_schema_sha256"]
                     for t in cohort["trials"]}
    if len(schema_hashes) != 1:
        raise DispatchError("the manifest's trials disagree on the schema hash")

    provenance = {
        "transport": TRANSPORT,
        "trial_model": TRIAL_MODEL,
        "tool_access": TOOL_ACCESS,
        "context_isolation": CONTEXT_ISOLATION,
        "trial_subject_definition_sha256":
            cohort["trial_subject_surface"]["definition_sha256"],
        "decision_schema_sha256": schema_hashes.pop(),
        "rendered_prompt_sha256_by_arm": {
            arm: next(iter(hashes)) for arm, hashes in by_arm.items()
        },
        # The dispatch script is the readable record of what was REQUESTED of
        # the transport (model override, schema forcing). It does not prove the
        # transport complied -- see the module docstring.
        "dispatch_script_sha256": dispatch_script_sha256,
        "dispatch_plan_sha256": hashlib.sha256(
            json.dumps(plan, ensure_ascii=False, sort_keys=True)
            .encode("utf-8")).hexdigest(),
        "run_date": run_date,
        # Re-runnable evidence, not a claim: every recorded output was
        # validated against the frozen schema by a validator copied verbatim
        # from E2.4 and pinned against it by test.
        "schema_conformance": conformance,
    }
    if notes:
        provenance["notes"] = notes

    return {
        "record_class": "h1a_cohort_raw",
        "cohort_id": plan["cohort_id"],
        "cohort_manifest_sha256": plan["cohort_manifest_sha256"],
        "provenance": provenance,
        "outputs": outputs,
    }


def write_raw(raw: dict, spec=None) -> Path:
    """Fail-closed, same discipline as `freeze()` and `_h1a_score.main()`:
    trial observations are written once."""
    spec = spec or cohort_mod.TYPED_SCOPE_COHORT
    if spec.raw_path.exists():
        raise DispatchError(
            f"{spec.raw_path.name} already holds the {spec.cohort_id!r} "
            f"cohort's observations. Re-running the cohort over them would "
            f"destroy the recorded trials irreversibly. A re-run is a new "
            f"cohort with its own spec."
        )
    spec.raw_path.write_text(
        json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return spec.raw_path
