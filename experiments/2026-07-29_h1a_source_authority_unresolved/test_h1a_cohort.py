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
