"""Scorer for the H1a anchor-sensitivity diagnostic.

WRITTEN BEFORE ANY DIAGNOSTIC TRIAL RAN. That is the whole point: §11.2 and
§11.2a were preregistered as prose, but prose is not a decision procedure
until someone writes the code, and whoever writes that code after seeing the
data can -- without any bad intent -- pick the reading that fits what they
saw. This file mechanically transcribes the preregistered text and adds no
judgment of its own.

The two rules, verbatim from PREREGISTRATION.md
------------------------------------------------

§11.2 (external ruling, gross anchor sensitivity):

    Treat gross anchor sensitivity as present if flipping only the anchor
    changes the modal behavior category or modal selected type in either arm,
    or changes the selection/defer count by at least 2 out of 5 in either arm
    comparison.

§11.2a (external ruling Q4, pre-freeze interpretability condition):

    If all four diagnostic cells fall into the same modal behavior category
    (`select_type` or `defer`), the diagnostic does not establish that the
    anchor and prompt surface are free of ceiling effects. In that case, a null
    main result is uninterpretable with respect to anchor or prompt-surface
    ceiling effects.

    This rule is not an additional trial, not a post-hoc exclusion, not a new
    blocking rule, and not a new success criterion. It is a pre-freeze
    interpretability condition for reading the diagnostic gate.

Reading notes that the code makes explicit
--------------------------------------------
Both rules speak of a "modal behavior category". The behavioral coder
(`_coder.py`, P5) emits three categories -- `selection` / `deferral` /
`invalid` -- while §11.2a's parenthetical names two (`select_type` or
`defer`). These are the same axis under two vocabularies: the coder's
`selection` is the schema's `select_type`, `deferral` is `defer`. `invalid`
is a third observed category that P6 requires be kept in the denominator and
never dropped. So:

- the modal category is computed over ALL completed trials in the cell,
  including `invalid` (P6: "invalid을 분모에서 빼지 않는다")
- `invalid` can therefore itself be modal, and if it is, that is reported as
  such rather than silently resolved -- §11.2a asks whether all four cells
  share one modal category, and "all four are mostly invalid" is a real,
  reportable answer to that question, not an error

Ties are not broken. If two categories tie for modal in a cell, the modal
category is reported as a frozenset of the tied values and any comparison
involving it is reported as `changed` unless the tied sets are identical --
silently picking one would be exactly the post-hoc freedom this file exists
to remove.

Stdlib only.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


coder = _load("h1a_coder_for_score", HERE / "_coder.py")
diag = _load("h1a_diag_for_score", HERE / "_h1a_diag.py")

# §11.2's threshold, transcribed. Named rather than inlined so the test suite
# can assert the preregistered number is what the code actually uses.
COUNT_CHANGE_THRESHOLD = 2
R_DIAG = diag.R_DIAG  # 5


class ScoreError(Exception):
    """Raised when the diagnostic cannot be scored as preregistered."""


# --------------------------------------------------------------------------
# per-cell aggregation
# --------------------------------------------------------------------------

def _modal(categories: list[str]) -> frozenset:
    """The modal category, as a frozenset so ties survive instead of being
    silently broken. A single-element set is the ordinary case."""
    if not categories:
        raise ScoreError("cannot compute a modal category over zero trials")
    counts = Counter(categories)
    top = max(counts.values())
    return frozenset(c for c, n in counts.items() if n == top)


def _modal_selected_type(outputs: list) -> frozenset:
    """§11.2 also watches the modal *selected type*. Only trials the coder
    called `selection` carry one; if a cell has none, the modal selected type
    is the empty set, which compares unequal to any non-empty set."""
    types = [
        o["selected_type"] for o in outputs
        if isinstance(o, dict) and coder.code(o) == coder.SELECTION
    ]
    if not types:
        return frozenset()
    counts = Counter(types)
    top = max(counts.values())
    return frozenset(t for t, n in counts.items() if n == top)


def score_cell(outputs: list) -> dict:
    """Aggregate one (arm, anchor) cell. `outputs` are parsed model responses."""
    categories = [coder.code(o) for o in outputs]
    counts = Counter(categories)
    return {
        "n": len(outputs),
        "categories": dict(counts),
        "modal_category": _modal(categories),
        "modal_selected_type": _modal_selected_type(outputs),
        "selection": counts.get(coder.SELECTION, 0),
        "deferral": counts.get(coder.DEFERRAL, 0),
        "invalid": counts.get(coder.INVALID, 0),
    }


def score_cells(trials: list[dict]) -> dict:
    """Group trials by (arm, anchor) and aggregate each cell.

    Each trial must carry `arm`, `anchor`, and `output` (the parsed response).
    """
    grouped: dict[tuple, list] = {}
    for trial in trials:
        for key in ("arm", "anchor", "output"):
            if key not in trial:
                raise ScoreError(f"trial missing {key!r}: {trial.get('trial_id')}")
        grouped.setdefault((trial["arm"], trial["anchor"]), []).append(trial["output"])

    expected = {(a, k) for a in diag.ARMS for k in diag.ANCHORS}
    if set(grouped) != expected:
        missing = sorted(expected - set(grouped))
        extra = sorted(set(grouped) - expected)
        raise ScoreError(f"cell set mismatch; missing={missing} unexpected={extra}")

    return {cell: score_cell(outputs) for cell, outputs in grouped.items()}


# --------------------------------------------------------------------------
# §11.2 -- gross anchor sensitivity (the external ruling's blocking rule)
# --------------------------------------------------------------------------

def gross_anchor_sensitivity(cells: dict) -> dict:
    """Within each arm, flip only the anchor and ask whether anything moved.

    Present if, IN EITHER ARM:
      - the modal behavior category changed, OR
      - the modal selected type changed, OR
      - the selection/defer count changed by >= 2 out of 5.

    All three are checked per arm and reported individually, so a later reader
    can see which limb fired rather than only the verdict.
    """
    per_arm = {}
    for arm in diag.ARMS:
        a, b = cells[(arm, diag.ANCHORS[0])], cells[(arm, diag.ANCHORS[1])]
        selection_delta = abs(a["selection"] - b["selection"])
        deferral_delta = abs(a["deferral"] - b["deferral"])
        limbs = {
            "modal_category_changed": a["modal_category"] != b["modal_category"],
            "modal_selected_type_changed":
                a["modal_selected_type"] != b["modal_selected_type"],
            "count_changed_by_threshold":
                selection_delta >= COUNT_CHANGE_THRESHOLD
                or deferral_delta >= COUNT_CHANGE_THRESHOLD,
        }
        per_arm[arm] = {
            **limbs,
            "selection_delta": selection_delta,
            "deferral_delta": deferral_delta,
            "present": any(limbs.values()),
        }
    return {
        "present": any(v["present"] for v in per_arm.values()),
        "by_arm": per_arm,
        "rule": "PREREGISTRATION.md §11.2 (external ruling Q2=B)",
    }


# --------------------------------------------------------------------------
# §11.2a -- pre-freeze interpretability condition (Q4)
# --------------------------------------------------------------------------

def uniform_modal_category(cells: dict) -> dict:
    """Do all four cells share one modal behavior category?

    NOT a blocking rule and NOT a success criterion (the ruling says so in as
    many words). It records whether the diagnostic established what it set out
    to establish. If it fires, a null main result cannot be read as evidence
    about anchor or prompt-surface ceiling effects.
    """
    modals = {cell: cells[cell]["modal_category"] for cell in cells}
    distinct = {frozenset(m) for m in modals.values()}
    uniform = len(distinct) == 1
    shared = next(iter(distinct)) if uniform else None
    return {
        "uniform": uniform,
        "shared_modal_category": sorted(shared) if shared else None,
        "modal_by_cell": {f"{a}|{k}": sorted(m) for (a, k), m in modals.items()},
        "consequence": (
            "The diagnostic does not establish that the anchor and prompt "
            "surface are free of ceiling effects. A null main result is "
            "uninterpretable with respect to anchor or prompt-surface "
            "ceiling effects."
        ) if uniform else (
            "Cells differ in modal category; this condition does not fire."
        ),
        "rule": "PREREGISTRATION.md §11.2a (external ruling Q4, approved)",
        "is_blocking_rule": False,
        "is_success_criterion": False,
    }


# --------------------------------------------------------------------------
# top level
# --------------------------------------------------------------------------

def score(trials: list[dict]) -> dict:
    """Full diagnostic verdict. Both rules always run and are always reported;
    neither can be skipped on the basis of the other's outcome."""
    cells = score_cells(trials)
    invalid_total = sum(c["invalid"] for c in cells.values())
    return {
        "label": diag.DIAGNOSTIC_LABEL,
        "coder_version": coder.CODER_VERSION,
        "n_trials": sum(c["n"] for c in cells.values()),
        "cells": {
            f"{a}|{k}": {
                **{kk: vv for kk, vv in c.items()
                   if kk not in ("modal_category", "modal_selected_type")},
                "modal_category": sorted(c["modal_category"]),
                "modal_selected_type": sorted(c["modal_selected_type"]),
            }
            for (a, k), c in cells.items()
        },
        "invalid_total": invalid_total,
        "gross_anchor_sensitivity": gross_anchor_sensitivity(cells),
        "uniform_modal_category": uniform_modal_category(cells),
        "merge_into_main_cohort": False,
    }


def main() -> int:
    if len(sys.argv) < 2:
        raise SystemExit("usage: python3 _h1a_diag_score.py <trials.json>")
    trials = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    print(json.dumps(score(trials), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
