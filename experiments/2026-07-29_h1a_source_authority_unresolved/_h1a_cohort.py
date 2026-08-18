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
import _h1a_policy as policy

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[1]  # concept-gate-h1-wt/

FIXTURE_PATH = HERE / "fixture_source_authority.json"
SCHEMA_PATH = HERE / "h1a_schema.json"
COHORT_PATH = HERE / "cohort_prompts.json"

# The preserved 2026-08-03 cohort's observation and scored-output paths.
# Defined here rather than in `_h1a_score.py` so ORIGINAL_COHORT can carry
# them: the scorer used to own these names as module constants, which is
# why a second cohort had nowhere to write.
RAW_PATH = HERE / "trials_raw.json"
TRIALS_PATH = HERE / "trials.json"
SCORE_PATH = HERE / "h1a_cohort_score.json"

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

# What a raw trial-output file must declare about the conditions its outputs
# were produced under, shared by the confirmatory cohort and the capability
# diagnostics so the two cannot drift apart.
#
# The 2026-08-15 QF-SELECT run is why this exists. Its outputs were valid and
# its rendered prompt was byte-correct, but it ran WITHOUT schema forcing and
# on whatever model the dispatching session happened to use -- and neither
# fact was recoverable, because the artifact recorded neither. Byte-identity
# of the prompt was verified and was NOT sufficient: a trial identifies a
# SUBJECT under a TRANSPORT, not just a prompt.
#
# The prompt-hash key is deliberately NOT in this tuple. A diagnostic has one
# surface (`rendered_prompt_sha256`, a string); the cohort has one per arm
# (`rendered_prompt_sha256_by_arm`, a mapping). Giving the same key name two
# value shapes is how a checker ends up comparing a string to a dict and
# passing because both are truthy.
SHARED_PROVENANCE_KEYS = (
    "transport", "trial_model", "tool_access", "context_isolation",
    "trial_subject_definition_sha256", "decision_schema_sha256",
)

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


def _order_key(bundle: int, order_seed: str = ORDER_SEED) -> tuple:
    """Same sha256_blocked_sort shape as E2.3's _gen_prompts.py::_order_key,
    blocked by bundle/replicate index -- bundle order only, since content is
    identical within an arm (K=1) and cannot itself be perturbed by order.

    `order_seed` is a parameter (D-H1a-13 wiring) so a second cohort gets a
    different execution order rather than silently reusing the preserved
    cohort's. The default keeps every existing call byte-identical."""
    material = "\0".join((order_seed, str(bundle)))
    return (bundle, hashlib.sha256(material.encode("utf-8")).hexdigest())


class CohortSpec:
    """Which cohort is being built (D-H1a-13 Q13.3 / D-H1a-10 Q10.1).

    Everything a second cohort must NOT share with the preserved 2026-08-03
    one, in a single object. Q10.1 forbids merging or reusing that cohort, and
    `freeze()`'s docstring already recorded that the repaired cohort needs its
    own manifest path, ORDER_SEED and trial-id prefix -- "that wiring is not
    done". This is that wiring, and the qualification gate needs the same
    thing, so it is done once here rather than twice.

    The default instance reproduces the original cohort byte-for-byte
    (verified: `build_cohort()` with no argument hashes identically to the
    pre-refactor implementation), so no existing caller changes behavior.
    """

    def __init__(self, *, cohort_id: str, fixture_path, cohort_path,
                 raw_path, trials_path, score_path,
                 order_seed: str, trial_id_prefix: str, n_per_arm: int,
                 stage_a_replicates=None):
        self.cohort_id = cohort_id
        self.fixture_path = fixture_path
        self.cohort_path = cohort_path
        # 2026-08-18: the SCORED-output half of the same separation.
        #
        # `_h1a_score.py::main()`'s docstring said the repaired cohort "needs
        # its own scored-output paths (a cohort_id-qualified path or filename)
        # ... that wiring is not done", exactly as freeze()'s docstring once
        # said about the manifest path. The manifest half was wired on
        # 2026-08-15; this is the other half. Until it existed, a second
        # cohort's 40 observations had nowhere to be scored to, and the only
        # thing standing between them and the preserved 2026-08-03 cohort's
        # `trials.json` / `h1a_cohort_score.json` was main()'s exists() refusal.
        #
        # KEYWORD-ONLY WITH NO DEFAULTS, on purpose -- same discipline as
        # `_h1a_policy.assert_freezable`'s V/H. A default here would point at
        # whichever cohort was written first, and "a stale default silently
        # certified/overwrote the preserved artifact" is the precise failure
        # this folder has now fixed three times (freeze(), main(), the subject
        # hash guard). A new cohort must state its own output paths.
        self.raw_path = raw_path
        self.trials_path = trials_path
        self.score_path = score_path
        self.order_seed = order_seed
        self.trial_id_prefix = trial_id_prefix
        self.n_per_arm = n_per_arm
        # Stage A is the harness-integrity slice (P7 sec 7.1). For a 5-trial
        # qualification control the whole run is the check, so callers pass
        # their own range rather than inheriting the main cohort's 1..5.
        self.stage_a_replicates = (
            list(stage_a_replicates) if stage_a_replicates is not None
            else list(range(1, 6))
        )

    @property
    def freeze_proof_path(self):
        """DERIVED from cohort_path, not a separate field.

        The three output paths above take no defaults because a stale default
        could point at another cohort's artifact. That hazard does not exist
        here: this path is a function of `cohort_path`, so it cannot name a
        different cohort than the manifest it sits beside. Deriving is strictly
        safer than another required field a caller could get wrong.
        """
        return self.cohort_path.with_name(
            self.cohort_path.stem + "_freeze_proof.json"
        )


# The preserved 2026-08-03 cohort. Values match the module constants above so
# the two cannot drift; changing either without the other is caught by
# test_default_cohort_spec_matches_the_module_constants.
ORIGINAL_COHORT = CohortSpec(
    cohort_id="h1a-original-20260803",
    fixture_path=FIXTURE_PATH,
    cohort_path=COHORT_PATH,
    raw_path=RAW_PATH,
    trials_path=TRIALS_PATH,
    score_path=SCORE_PATH,
    order_seed=ORDER_SEED,
    trial_id_prefix="H1A",
    n_per_arm=N_PER_ARM,
)



# The typed-scope cohort (D-H1a-12 Q12=F), frozen 2026-08-17 once
# INDEPENDENT_SEMANTIC_REVIEW_PASSED was set and every other freeze condition
# passed.
#
# WHY A THIRD IDENTITY AND NOT THE REPAIRED COHORT'S
# `PREREGISTRATION_REPAIRED_COHORT.md` sec 5 fixed `H1A-repaired-fixed-order-v1`
# / `H1AR` for the D-H1a-10/11 repair, but that cohort was never executed --
# three independent reviewers returned FREEZE_BLOCKED. D-H1a-12's typed-scope
# split is a THIRD design, so reusing `H1AR` would label these trials as the
# repair's, and reusing `H1A` would make them indistinguishable from the
# preserved 40 that D-H1a-10 ruled non-identifying.
#
# `PREREGISTRATION_TYPED_SCOPE_COHORT.md` sec 6 requires that `cohort_id` and
# the output files be SEPARATE from the existing cohorts but does not fix the
# strings, so these were chosen to satisfy that and verified by dry-run before
# any write: no trial_id overlap with the preserved cohort, a distinct seed
# (which demonstrably yields a different execution order), and a distinct
# manifest path.
#
# `H1AT` does not collide with `H1A` under the prefix checks in this folder --
# they match on `"H1A-"` with the hyphen, which `H1AT-` does not satisfy.
#
# The fixture is deliberately UNCHANGED (`fixture_source_authority.json`, the
# Q8=B 1-vs-1 form: ev1 doc / ev3 code). Preregistration sec 1 lists it as
# 불변 and Q9=A keeps L3 in force; the dry-run confirmed
# `fixture_sha256` matches the preserved cohort's, so the only thing that
# differs between cohorts is the prompt surface.
TYPED_SCOPE_COHORT = CohortSpec(
    cohort_id="h1a-typed-scope-20260817",
    fixture_path=FIXTURE_PATH,
    cohort_path=HERE / "cohort_prompts_typed_scope.json",
    raw_path=HERE / "trials_raw_typed_scope.json",
    trials_path=HERE / "trials_typed_scope.json",
    score_path=HERE / "h1a_cohort_score_typed_scope.json",
    order_seed="H1A-typed-scope-fixed-order-v1",
    trial_id_prefix="H1AT",
    n_per_arm=N_PER_ARM,
)


def build_cohort(spec: "CohortSpec | None" = None) -> dict:
    spec = spec or ORIGINAL_COHORT
    fixture = json.loads(spec.fixture_path.read_text(encoding="utf-8"))
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

    # D-H1a-11's policy layer, run against the ACTUAL rendered arms.
    #
    # Two independent reviews (docs/feedback/h1a_repair_review_20260804.md)
    # found this call absent: build_cohort() ran only the two guards above --
    # exactly the guard class that passed on the 2026-08-03 cohort and let it
    # become non-identifying -- while every _h1a_policy assertion was
    # exercised only against a synthetic string or the frozen JSON, never
    # against what render_arm() actually produces. That is the same shape of
    # error the policy layer was built to fix: asserting a true proposition
    # about the wrong object. Calling assert_freezable() here closes that gap
    # and, because condition 5 is unmet by design
    # (INDEPENDENT_SEMANTIC_REVIEW_PASSED = False), this also means
    # build_cohort() cannot produce a manifest until that flag is set --
    # freeze() cannot outrun the freeze gate.
    _certify_freezable(arm_templates)

    rendered_prompts = {
        arm: surface.render_prompt(arm_templates[arm], model_payload)
        for arm in contract.ARMS
    }

    builder_commit = _git_head()
    trial_subject = _trial_subject_surface()

    trials = []
    bundles = []
    for replicate in range(1, spec.n_per_arm + 1):
        bundle_id = replicate
        order = _order_key(bundle_id, spec.order_seed)
        bundles.append({"bundle": bundle_id, "order_key": order[1]})
        for arm in contract.ARMS:
            trial_id = f"{spec.trial_id_prefix}-{arm}-{replicate:02d}"
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
            "n_per_arm": spec.n_per_arm,
            "randomization": {
                "method": "sha256_blocked_sort",
                "seed": spec.order_seed,
                "block": "bundle (paired replicate index across both arms)",
            },
            "stage_a_replicates": list(spec.stage_a_replicates),
            "stage_b_replicates": [
                r for r in range(1, spec.n_per_arm + 1)
                if r not in set(spec.stage_a_replicates)
            ],
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


class CohortOverwriteRefused(Exception):
    """freeze() would destroy a preserved cohort. Never proceed."""


def _certify_freezable(arm_templates: dict[str, str]) -> dict:
    """The ONE place the freeze gate is invoked, and the one place V and H live.

    `assert_freezable` makes V/H keyword-only with no defaults precisely so a
    stale default cannot certify a freeze. Two call sites passing them
    separately would reintroduce that hazard one level up -- they could drift
    apart and each would still look explicit. So the values are stated once,
    here, and both the freeze path (`build_cohort`) and the proof-recording
    path (`build_freeze_proof`) go through this function.

    D-H1a-12 sec 10: these are fixture and shared-prompt facts this module
    cannot derive. `source_attributes_visible=True` because the fixture exposes
    source attributes; `hard_defer_mapping=False` because no prompt maps a
    source attribute to a forced defer.
    """
    return policy.assert_freezable(
        arm_templates,
        contract.LIVENESS_CLAUSE_TEXT,
        source_attributes_visible=True,
        hard_defer_mapping=False,
    )


class FreezeProofOverwriteRefused(Exception):
    """write_freeze_proof() would destroy an already-recorded proof."""


def build_freeze_proof(spec: "CohortSpec | None" = None) -> dict:
    """The freeze certification, as a recordable artifact.

    WHY THIS EXISTS
    `build_cohort()` called `assert_freezable()` for its SIDE EFFECT only and
    discarded the returned proof, so nothing about how the freeze was certified
    reached disk. But PREREGISTRATION_TYPED_SCOPE_COHORT.md sec 7 requires
    "`licensed_source_evaluation_path`의 항목별 값을 결과와 함께 기록한다 --
    대비가 성립한 근거가 무엇이었는지 사후에 재구성 가능해야 한다", and the
    frozen manifest has no such key (verified 2026-08-18: absent).

    A sidecar rather than a manifest field, deliberately. The typed-scope
    manifest is already frozen and `freeze()` refuses to overwrite it; adding
    the key to `build_cohort()`'s output would leave the code and the frozen
    artifact permanently disagreeing about the manifest's shape, which is a
    worse defect than the one being fixed. Binding by `cohort_manifest_sha256`
    gives the same guarantee without rewriting a frozen file.

    Deterministic: every input (the template, the arm renderer, V, H) is frozen,
    so this recomputes bit-identically to what certified the freeze. The
    equality is not assumed -- `_certify_freezable` is the single call site both
    paths use.
    """
    spec = spec or ORIGINAL_COHORT
    template = contract.load_h1a_native_template()
    arm_templates = {arm: contract.render_arm(template, arm) for arm in contract.ARMS}
    proof = _certify_freezable(arm_templates)

    manifest_bytes = spec.cohort_path.read_bytes()
    return {
        "record_class": "h1a_freeze_proof",
        "cohort_id": spec.cohort_id,
        "cohort_manifest": spec.cohort_path.name,
        # Binds this proof to the exact manifest bytes it certifies. A proof
        # that floats free of the manifest proves nothing about it.
        "cohort_manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
        "recorded_commit": _git_head(),
        "freeze_conditions": {
            k: v for k, v in proof.items()
            if k != "licensed_source_evaluation_path"
        },
        "licensed_source_evaluation_path": proof["licensed_source_evaluation_path"],
    }


def write_freeze_proof(spec: "CohortSpec | None" = None) -> dict:
    """Write the proof beside the manifest it certifies. Fail-closed, per the
    same discipline as `freeze()` and `_h1a_score.main()`: an existing proof is
    evidence about a frozen manifest and is not silently replaced."""
    spec = spec or ORIGINAL_COHORT
    if spec.freeze_proof_path.exists():
        raise FreezeProofOverwriteRefused(
            f"{spec.freeze_proof_path.name} already records how the "
            f"{spec.cohort_id!r} cohort's freeze was certified. Overwriting it "
            f"would replace evidence about a frozen manifest. If the manifest "
            f"itself changed, that is a new cohort with its own spec."
        )
    proof = build_freeze_proof(spec)
    spec.freeze_proof_path.write_text(
        json.dumps(proof, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return proof


def freeze(spec: "CohortSpec | None" = None) -> dict:
    """Build and write the cohort manifest.

    ⚠️ FAIL-CLOSED SINCE 2026-08-04. Three independent reviewers of the
    D-H1a-11 repair found that this function, unchanged since the first cohort,
    would silently destroy that cohort's frozen manifest:

      - COHORT_PATH is the ORIGINAL cohort's manifest. The write below was
        unconditional, so re-running freeze() overwrites the artifact
        `COHORT_STATUS_20260803_nonidentifying.md` and its eleven recorded
        sha256 values rest on.
      - ORDER_SEED is still `H1A-fixed-order-v1` and trial ids are still
        `H1A-{arm}-{replicate:02d}`, but PREREGISTRATION_REPAIRED_COHORT.md §5
        requires `H1A-repaired-fixed-order-v1` and `H1AR-{arm}-{replicate:02d}`
        precisely so the two cohorts cannot be confused. As written, the
        repaired run would emit ids indistinguishable from the preserved ones.

    D-H1a-10 Q10.1 forbids merging or reusing the original cohort, and
    D-H1a-11 §13 repeats it (`merge_original_and_repaired_cohorts: false`).
    Overwriting in place is the most irreversible form of that violation, so
    this refuses rather than warns.

    2026-08-15 (D-H1a-13 wiring): the "pending change" this docstring used to
    name is now done -- `CohortSpec` carries the path, seed, trial-id prefix
    and N, so a second cohort no longer has to reuse the first one's. The
    refusal below is now per-spec: it protects whatever `spec.cohort_path`
    points at, not only the original manifest. Passing a new spec is the
    supported way to build a second cohort; deleting this check is still not.
    """
    spec = spec or ORIGINAL_COHORT
    if spec.cohort_path.exists():
        raise CohortOverwriteRefused(
            f"{spec.cohort_path.name} already exists and holds the "
            f"{spec.cohort_id!r} cohort's frozen manifest. D-H1a-10 Q10.1 "
            f"ordered cohorts PRESERVED and not merged or reused "
            f"(merge_with_repaired_cohort: false), so writing here would "
            f"destroy it irreversibly.\n\n"
            f"A different cohort needs its own CohortSpec -- its own "
            f"cohort_path, order_seed and trial_id_prefix (e.g. "
            f"{'H1A-repaired-fixed-order-v1'!r} / 'H1AR' per "
            f"PREREGISTRATION_REPAIRED_COHORT.md §5). Build it with "
            f"build_cohort(spec) / freeze(spec). Do not delete this check "
            f"to proceed."
        )
    cohort = build_cohort(spec)
    spec.cohort_path.write_text(
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
