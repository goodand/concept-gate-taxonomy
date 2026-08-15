"""Regression tests for the 2026-08-04 fixes to _h1a_cohort.py.

Not a full test_protocol.py-grade self-check for this harness -- that gap is
recorded, not closed, in OPERATIONS_LOG.md ("neither harness has a
test_protocol.py-grade self-check"). These two tests pin only the two
specific defects two independent reviews found in this file:

  1. freeze() would silently overwrite the preserved, non-identifying cohort.
  2. build_cohort() never ran the D-H1a-11 policy layer against the arms it
     actually renders, so a repaired cohort would have been protected by
     exactly the guard class that already failed once.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    key = f"_h1a_cohort_test__{name}"
    if key in sys.modules:
        return sys.modules[key]
    spec = importlib.util.spec_from_file_location(key, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[key] = module
    # _h1a_cohort.py imports its siblings as plain `import _h1a_contract as
    # contract`, which requires HERE on sys.path -- match that rather than
    # loading it in isolation.
    if str(HERE) not in sys.path:
        sys.path.insert(0, str(HERE))
    spec.loader.exec_module(module)
    return module


cohort = _load("cohort", "_h1a_cohort.py")


def test_freeze_refuses_to_overwrite_the_preserved_cohort():
    """cohort_prompts.json is the 2026-08-03 cohort D-H1a-10 ordered preserved.
    It exists in this repo state, so freeze() must refuse rather than write."""
    assert cohort.COHORT_PATH.exists(), (
        "this test assumes the preserved cohort manifest is present; if it is "
        "not, the guard this test pins cannot be exercised"
    )
    before = cohort.COHORT_PATH.read_bytes()
    with pytest.raises(cohort.CohortOverwriteRefused):
        cohort.freeze()
    after = cohort.COHORT_PATH.read_bytes()
    assert before == after, "the preserved cohort's bytes must be untouched"


def test_build_cohort_runs_the_policy_layer_against_the_real_rendered_arms():
    """build_cohort() must call the D-H1a-11 policy layer, not just the two
    pre-existing contract guards. Condition 5 is unmet by design, so this
    must currently raise FreezeGateBlocked -- from build_cohort() itself, not
    only from a test that calls assert_freezable() directly."""
    with pytest.raises(cohort.policy.FreezeGateBlocked, match="independent semantic review"):
        cohort.build_cohort()


def test_two_independent_gates_both_block_freeze_right_now():
    """freeze() checks the overwrite guard BEFORE calling build_cohort(), so
    with the preserved manifest present it raises CohortOverwriteRefused, not
    FreezeGateBlocked -- confirming the two guards are independent layers,
    not one masking the other. If the preserved manifest is ever moved aside,
    build_cohort()'s own FreezeGateBlocked (pinned above) still stands as a
    second, independent block."""
    with pytest.raises(cohort.CohortOverwriteRefused):
        cohort.freeze()


# --- D-H1a-13 wiring: CohortSpec parameterization (2026-08-15) -------------
# freeze()'s own docstring recorded for over a week that the repaired cohort
# "needs its own manifest path, ORDER_SEED and trial-id prefix. That wiring is
# not done." The qualification gate (Q13.3) needs exactly the same thing, so
# it was done once. These pin that the default path did not move a byte and
# that a new spec genuinely changes what it claims to change.

def test_default_cohort_spec_matches_the_module_constants():
    """ORIGINAL_COHORT and the module constants are two statements of the same
    fact. If they drift, the default build silently stops describing the
    preserved cohort while every other test still passes."""
    assert cohort.ORIGINAL_COHORT.fixture_path == cohort.FIXTURE_PATH
    assert cohort.ORIGINAL_COHORT.cohort_path == cohort.COHORT_PATH
    assert cohort.ORIGINAL_COHORT.order_seed == cohort.ORDER_SEED
    assert cohort.ORIGINAL_COHORT.n_per_arm == cohort.N_PER_ARM
    assert cohort.ORIGINAL_COHORT.trial_id_prefix == "H1A"


def test_a_new_spec_changes_id_prefix_seed_and_n(monkeypatch, tmp_path):
    """Recall for the parameterization: a second cohort must not silently
    reuse the preserved cohort's trial ids or execution order. Q10.1 forbids
    confusing the two, and identical ids are the most direct way to do it."""
    monkeypatch.setattr(cohort.policy, "INDEPENDENT_SEMANTIC_REVIEW_PASSED", True)
    spec = cohort.CohortSpec(
        cohort_id="qf-test", fixture_path=cohort.FIXTURE_PATH,
        cohort_path=tmp_path / "qf.json", order_seed="H1A-QF-TEST-v1",
        trial_id_prefix="H1AQT", n_per_arm=5, stage_a_replicates=[1, 2, 3, 4, 5],
    )
    built = cohort.build_cohort(spec)

    assert built["n"] == 10, "5 replicates x 2 arms"
    assert all(t["trial_id"].startswith("H1AQT-") for t in built["trials"])
    assert not any(t["trial_id"].startswith("H1A-") for t in built["trials"])
    assert built["protocol"]["randomization"]["seed"] == "H1A-QF-TEST-v1"
    assert built["protocol"]["n_per_arm"] == 5
    # Whole run is Stage A for a qualification control, so Stage B is empty --
    # inheriting the main cohort's 1..5 / 6..20 split would be wrong here.
    assert built["protocol"]["stage_a_replicates"] == [1, 2, 3, 4, 5]
    assert built["protocol"]["stage_b_replicates"] == []


def test_the_overwrite_guard_is_per_spec_not_only_the_original_path(
    monkeypatch, tmp_path
):
    """Precision + recall for the refusal: it must protect whatever path the
    spec names (so a second cohort cannot be clobbered either), and must not
    fire when that path is free."""
    monkeypatch.setattr(cohort.policy, "INDEPENDENT_SEMANTIC_REVIEW_PASSED", True)
    target = tmp_path / "qf.json"
    spec = cohort.CohortSpec(
        cohort_id="qf-test", fixture_path=cohort.FIXTURE_PATH,
        cohort_path=target, order_seed="H1A-QF-TEST-v1",
        trial_id_prefix="H1AQT", n_per_arm=5, stage_a_replicates=[1, 2, 3, 4, 5],
    )
    cohort.freeze(spec)                       # precision: free path, must write
    assert target.exists()
    before = target.read_bytes()

    with pytest.raises(cohort.CohortOverwriteRefused, match="qf-test"):
        cohort.freeze(spec)                   # recall: now occupied, must refuse
    assert target.read_bytes() == before
