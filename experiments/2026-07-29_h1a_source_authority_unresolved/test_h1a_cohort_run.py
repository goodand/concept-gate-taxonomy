"""Tests for the confirmatory cohort's execution and persistence layer.

Two things are pinned here that nothing else pins: that the schema validator
is still verbatim from E2.4, and that the dispatch plan's prompt bytes are the
frozen manifest's bytes rather than a re-render.
"""
from __future__ import annotations

import importlib.util
import inspect
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import _h1a_cohort as cohort_mod      # noqa: E402
import _h1a_cohort_run as run         # noqa: E402

TYPED = cohort_mod.TYPED_SCOPE_COHORT
E24 = HERE.parent / "2026-07-25_e2.4_repo_grounded_contract_transfer"


def _load_e24_cohort():
    """Load E2.4's module under a UNIQUE sys.modules key.

    E2.4_ISSUE_REGISTER [DONE] #6 is one experiment silently executing
    another's module. `_h1a_surface.py`'s docstring records the same
    precaution, for the same reason.
    """
    spec = importlib.util.spec_from_file_location(
        "_e24_cohort_for_h1a_pin", E24 / "_cohort.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["_e24_cohort_for_h1a_pin"] = module
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------
# the reused validator
# --------------------------------------------------------------------------

def test_schema_errors_is_verbatim_from_e2_4() -> None:
    """The drift pin for the copy.

    `schema_errors` is reused rather than hand-written, and copied rather than
    imported for the reason `_h1a_surface.py` records: D-H1a-1 forbids
    retroactively changing E2.4's frozen implementation. A copy without a pin
    is just two validators that will eventually disagree, and the disagreement
    would surface as "H1a accepts an output E2.4 rejects" -- silently.
    """
    e24 = _load_e24_cohort()
    assert inspect.getsource(run.schema_errors) == inspect.getsource(
        e24.schema_errors), (
        "the H1a copy of schema_errors has drifted from E2.4's original. "
        "Reconcile them; do not update this test to match."
    )


def test_the_validator_accepts_a_conforming_output() -> None:
    """Precision. A validator that rejected everything would pass the recall
    test below and make the cohort unscoreable."""
    schema = run.build_dispatch_plan(TYPED)["decision_schema"]
    ok = {"decision": "select_type", "selected_type": "essential_feature",
          "cited_evidence_ids": ["ev1"], "rationale": "x"}
    assert run.schema_errors(ok, schema) == []


@pytest.mark.parametrize("bad,why", [
    ({"decision": "select_type", "selected_type": "not_a_type",
      "cited_evidence_ids": ["ev1"], "rationale": "x"}, "type outside the enum"),
    ({"decision": "invented", "selected_type": None,
      "cited_evidence_ids": [], "rationale": "x"}, "decision outside the enum"),
    ({"decision": "defer", "selected_type": None,
      "cited_evidence_ids": []}, "missing rationale"),
    ({"decision": "defer", "selected_type": None, "cited_evidence_ids": [],
      "rationale": "x", "extra": 1}, "additional property"),
])
def test_the_validator_rejects_non_conforming_outputs(bad, why) -> None:
    """Recall, four ways. This is what makes 'all 40 conform' a re-runnable
    fact instead of the runner's word about the transport."""
    schema = run.build_dispatch_plan(TYPED)["decision_schema"]
    assert run.schema_errors(bad, schema), f"not caught: {why}"


def test_build_raw_refuses_a_non_conforming_output() -> None:
    """The validator must be ON the assembly path, not merely available.

    That is this folder's most-repeated defect shape: a check that exists and
    is not called by the code that needed it.
    """
    plan = run.build_dispatch_plan(TYPED)
    outputs = {
        item["trial_id"]: {
            "decision": "select_type", "selected_type": "essential_feature",
            "cited_evidence_ids": ["ev1"], "rationale": "x",
        } for item in plan["items"]
    }
    victim = plan["items"][0]["trial_id"]
    outputs[victim]["selected_type"] = "not_a_type"

    with pytest.raises(run.DispatchError, match="do not conform"):
        run.build_raw(plan, outputs, dispatch_script_sha256="0" * 64,
                      run_date="2026-08-18")


def test_transport_failures_are_not_schema_violations() -> None:
    """P4: a null is re-run, not recorded. Counting it as a schema violation
    would make a flaky dispatch look like a non-conforming subject."""
    plan = run.build_dispatch_plan(TYPED)
    outputs = {item["trial_id"]: None for item in plan["items"]}
    raw = run.build_raw(plan, outputs, dispatch_script_sha256="0" * 64,
                        run_date="2026-08-18")
    conf = raw["provenance"]["schema_conformance"]
    assert conf["transport_failures_skipped"] == 40
    assert conf["outputs_checked"] == 0
    assert conf["violations"] == 0


# --------------------------------------------------------------------------
# the dispatch plan
# --------------------------------------------------------------------------

def test_the_plan_dispatches_the_frozen_bytes() -> None:
    """The plan must hand over the manifest's prompt, not a re-render.

    `build_dispatch_plan` hashes each prompt it is about to dispatch and
    compares it to the hash the trial manifest recorded, so the bytes the
    model sees are the bytes the freeze certified.
    """
    manifest = json.loads(TYPED.cohort_path.read_text(encoding="utf-8"))
    plan = run.build_dispatch_plan(TYPED)

    assert plan["n"] == 40
    recorded = {t["trial_id"]: t["manifest"]["rendered_prompt_sha256"]
                for t in manifest["trials"]}
    for item in plan["items"]:
        assert item["prompt"] == manifest["rendered_prompts"][item["arm"]]
        assert item["rendered_prompt_sha256"] == recorded[item["trial_id"]]


def test_the_plan_preserves_the_frozen_execution_order() -> None:
    """The order is part of the freeze (`sha256_blocked_sort`, seed
    `H1A-typed-scope-fixed-order-v1`). It is bundle-level -- 20 bundles x 2
    arms -- because the block is the paired replicate index, so the pairing is
    the design and must not be flattened."""
    plan = run.build_dispatch_plan(TYPED)
    orders = [item["execution_order"] for item in plan["items"]]

    assert orders == sorted(orders)
    assert sorted(set(orders)) == list(range(1, 21))
    for order in set(orders):
        arms = {item["arm"] for item in plan["items"]
                if item["execution_order"] == order}
        assert arms == {"PROHIBITION_KEPT", "PROHIBITION_REMOVED"}, (
            f"bundle {order} is not a complete arm pair"
        )


def test_outputs_missing_a_planned_trial_are_refused() -> None:
    """A missing key and a null are DIFFERENT. Null is a recorded transport
    failure P4 re-runs; a missing key is an incomplete dispatch whose cause is
    unknown. Conflating them would let a partial run look complete."""
    plan = run.build_dispatch_plan(TYPED)
    outputs = {item["trial_id"]: None for item in plan["items"]}
    outputs.pop(plan["items"][0]["trial_id"])

    with pytest.raises(run.DispatchError, match="missing"):
        run.build_raw(plan, outputs, dispatch_script_sha256="0" * 64,
                      run_date="2026-08-18")


def test_unplanned_trial_ids_are_refused() -> None:
    plan = run.build_dispatch_plan(TYPED)
    outputs = {item["trial_id"]: None for item in plan["items"]}
    outputs["H1AT-PROHIBITION_KEPT-99"] = None

    with pytest.raises(run.DispatchError, match="unplanned"):
        run.build_raw(plan, outputs, dispatch_script_sha256="0" * 64,
                      run_date="2026-08-18")


def test_write_raw_refuses_to_replace_recorded_observations(
    monkeypatch, tmp_path
) -> None:
    """Same fail-closed discipline as freeze() and score.main(): observations
    are written once. Precision first, then recall."""
    spec = cohort_mod.CohortSpec(
        cohort_id="run-test", fixture_path=TYPED.fixture_path,
        cohort_path=tmp_path / "c.json",
        raw_path=tmp_path / "raw.json",
        trials_path=tmp_path / "t.json",
        score_path=tmp_path / "s.json",
        order_seed="H1A-RUN-TEST-v1", trial_id_prefix="H1ART", n_per_arm=2,
        stage_a_replicates=[1, 2],
    )
    run.write_raw({"record_class": "h1a_cohort_raw"}, spec)
    assert spec.raw_path.exists()
    before = spec.raw_path.read_bytes()

    with pytest.raises(run.DispatchError, match="run-test"):
        run.write_raw({"record_class": "h1a_cohort_raw"}, spec)
    assert spec.raw_path.read_bytes() == before


# --------------------------------------------------------------------------
# Direct negative calls. The two tests above reach these guards through
# `build_raw`; the negative-coverage scanner requires the raising call itself,
# and it is right to: a refactor that stopped calling them from `build_raw`
# would otherwise leave their recall untested while the suite stayed green.
# --------------------------------------------------------------------------

def test_the_coverage_guard_fires_when_called_directly() -> None:
    plan = run.build_dispatch_plan(TYPED)
    with pytest.raises(run.DispatchError, match="missing"):
        run._assert_outputs_cover_the_plan(plan, {})


def test_the_conformance_guard_fires_when_called_directly() -> None:
    plan = run.build_dispatch_plan(TYPED)
    outputs = {item["trial_id"]: {"decision": "nonsense"}
               for item in plan["items"]}
    with pytest.raises(run.DispatchError, match="do not conform"):
        run._assert_outputs_conform_to_the_frozen_schema(plan, outputs)
