"""H1a anchor-sensitivity diagnostic -- payload/cell construction.

PREREGISTRATION.md §11 (external ruling Q2=B). This is a SEPARATE,
NON-CERTIFYING cohort that runs BEFORE the main H1a cohort is frozen. Its
outputs are never merged into the main result table and never used to adjust N.

What it is for
--------------
The main design cannot distinguish, after the fact, between

  (a) the prohibition manipulation having no observable effect, and
  (b) the recorded type anchor in `candidate_concepts` pushing both arms to
      the code-side answer and saturating the observable behavior.

The anchor is arm-constant, so it cannot CONFOUND the arm contrast -- but it
can still INTERACT with treatment by producing a ceiling. With K=1 and no
anchor-flipped counterpart inside the main cohort, a post-hoc null would be
underidentified. So the anchor gets flipped here instead, off-protocol.

Scope of this module
---------------------
Payload construction, cell/batch structure, and prompt rendering.

Rendering was deliberately absent until 2026-07-31: the H1a model-facing
prompt surface was an open design question, and building a renderer before
the ruling would have meant authoring the very thing under adjudication. A
test (`test_module_does_not_render_prompts_yet`) enforced that. The Q3=B
ruling arrived (`DESIGN_DECISION_H1a_prompt_surface.md`), `_h1a_contract.py`
was rebuilt against it, and that guard was retired -- its job was to prevent
a specific premature act, and that act is no longer premature.

Still NOT here: hash freezing and trial execution.

The anchor-flipped cell is a counterfactual artifact
----------------------------------------------------
`essential_feature` contradicts the repository's actual enforced state (R6b
pins 철 as `structural_composition` and passes). That cell never appears in
the main cohort. It exists only to measure whether the anchor, rather than
the manipulation, is driving the observed behavior.

Stdlib only.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent


def _load(name: str, path: Path):
    """Unique sys.modules key -- this repo has already had one experiment
    silently execute another's module (E2.4_ISSUE_REGISTER [DONE] #6)."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


surface = _load("h1a_surface_diag", HERE / "_h1a_surface.py")
contract = _load("h1a_contract_diag", HERE / "_h1a_contract.py")

FIXTURE_PATH = HERE / "fixture_source_authority.json"

# --- the preregistered factor structure (§11.1) ----------------------------

ARMS = ("PROHIBITION_KEPT", "PROHIBITION_REMOVED")
ANCHORS = ("structural_composition", "essential_feature")
R_DIAG = 5  # fixed; changing it after seeing results makes it a new diagnostic
DIAGNOSTIC_LABEL = "non_certifying_diagnostic"

# The concept/feature the anchor is attached to. Named explicitly so that a
# fixture edit that renames either one fails loudly instead of silently
# flipping nothing.
CONCEPT, FEATURE = "칼", "철"

# §11.2b -- batches are a transport-limit accommodation, NOT a sequential
# design. Splitting by ARM keeps each anchor contrast whole inside one batch,
# because every rule in §11.2 is a within-arm comparison.
BATCHES = ({"batch": 1, "arm": ARMS[0]}, {"batch": 2, "arm": ARMS[1]})


# --- preregistration guard (E2.3 / _h3.py pattern, file list swapped) -------

EXPERIMENT_REL = HERE.relative_to(REPO_ROOT)
DESIGN_FILES = [
    str(EXPERIMENT_REL / name)
    for name in (
        "PREREGISTRATION.md",
        "fixture_source_authority.json",
        "h1a_schema.json",
        "_h1a_surface.py",
        "_h1a_contract.py",
        "_h1a_diag.py",
    )
]


def _git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(REPO_ROOT), *args], text=True).strip()


def preregistered_design_commit() -> str:
    """Refuse to freeze until every H1a design file is committed.

    A design frozen after seeing a trial result is not a precommitment, it is
    a rationalization.
    """
    dirty = _git("status", "--porcelain", "--", *DESIGN_FILES)
    if dirty:
        raise SystemExit(
            "PREREGISTRATION_REQUIRED: commit all H1a design files before "
            "freezing.\n" + dirty
        )
    return _git("log", "-1", "--format=%H", "--", *DESIGN_FILES)


# --- anchor flip -----------------------------------------------------------

class DiagnosticError(Exception):
    """Raised when the diagnostic cannot be constructed as preregistered."""


def load_fixture() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def recorded_anchor(fixture: dict) -> str:
    """The type the fixture actually records for the concept/feature pair."""
    for concept in fixture["candidate_concepts"]:
        if concept["name"] != CONCEPT:
            continue
        for feature in concept["features"]:
            if feature["feature"] == FEATURE:
                return feature["type"]
    raise DiagnosticError(
        f"fixture has no {CONCEPT}/{FEATURE} feature to anchor on; "
        f"the diagnostic's factor structure no longer matches the fixture"
    )


def fixture_with_anchor(fixture: dict, anchor: str) -> dict:
    """Return a copy whose recorded type is `anchor`, changing nothing else.

    This is the ONLY payload difference between the two anchor levels
    (§11.1). Evidence text, evidence ids, source kinds, and evidence order
    are untouched -- test_h1a_diag.py proves that by reconstruction rather
    than by inspection.
    """
    if anchor not in ANCHORS:
        raise DiagnosticError(f"anchor must be one of {ANCHORS}, got {anchor!r}")
    if anchor not in surface.FEATURE_TYPES:
        raise DiagnosticError(f"{anchor!r} is not a valid feature type")

    out = copy.deepcopy(fixture)
    flipped = 0
    for concept in out["candidate_concepts"]:
        if concept["name"] != CONCEPT:
            continue
        for feature in concept["features"]:
            if feature["feature"] == FEATURE:
                feature["type"] = anchor
                flipped += 1
    if flipped != 1:
        raise DiagnosticError(
            f"expected exactly 1 {CONCEPT}/{FEATURE} feature to flip, found {flipped}"
        )
    return out


# --- cells and trial ids ---------------------------------------------------

def trial_id(arm: str, anchor: str, replicate: int) -> str:
    """`H1A-DIAG-{ANCHOR}-{ARM}-{replicate:02d}`.

    Anchor is abbreviated to keep ids readable; the full value is also stored
    in the manifest's parameters, which is what any analysis reads.
    """
    short = {"structural_composition": "SC", "essential_feature": "EF"}[anchor]
    return f"H1A-DIAG-{short}-{arm}-{replicate:02d}"


def diagnostic_cells() -> list[dict]:
    """The 4 cells, in a fixed order. Order is fixed so the manifest is
    reproducible; it carries no meaning and no cell is a baseline."""
    return [
        {"arm": arm, "anchor": anchor}
        for arm in ARMS
        for anchor in ANCHORS
    ]


def diagnostic_bundle() -> list[dict]:
    """All 20 diagnostic trials: 2 arms x 2 anchors x R_DIAG."""
    return [
        {
            "trial_id": trial_id(cell["arm"], cell["anchor"], replicate),
            "arm": cell["arm"],
            "anchor": cell["anchor"],
            "replicate": replicate,
            "batch": 1 if cell["arm"] == ARMS[0] else 2,
            "label": DIAGNOSTIC_LABEL,
        }
        for cell in diagnostic_cells()
        for replicate in range(1, R_DIAG + 1)
    ]


def batch(n: int) -> list[dict]:
    """§11.2b. Batch 1 is PROHIBITION_KEPT, batch 2 is PROHIBITION_REMOVED.

    Batch 1's results must NOT change batch 2 -- batching is a transport
    accommodation, not a sequential design (§11.3).
    """
    if n not in (1, 2):
        raise DiagnosticError(f"batch must be 1 or 2, got {n!r}")
    return [t for t in diagnostic_bundle() if t["batch"] == n]


def diagnostic_payloads() -> dict:
    """Model payload per anchor level, built through the frozen whitelist
    builder so the diagnostic cannot expose a field the main cohort hides."""
    fixture = load_fixture()
    out = {}
    for anchor in ANCHORS:
        variant = fixture_with_anchor(fixture, anchor)
        manifest = surface.qualify_fixture(variant, REPO_ROOT, run_tests=False)
        if manifest["status"] != "passed":
            raise DiagnosticError(f"anchor={anchor}: qualification did not pass")
        out[anchor] = surface.build_model_payload(variant, manifest)
    return out


# --- rendering (Q3=B; see module docstring on why this arrived late) --------

AGENT_TYPE = "h1a-decider"


def render_diagnostic_prompt(arm: str, anchor: str, payloads: dict | None = None) -> str:
    """The exact bytes one diagnostic trial's model sees.

    Nothing here varies with `replicate` -- so all R_DIAG trials in a cell
    render byte-identically, which test_h1a_diag.py pins. If that ever stops
    being true, replicates within a cell are no longer replicates.
    """
    if arm not in ARMS:
        raise DiagnosticError(f"arm must be one of {ARMS}, got {arm!r}")
    if anchor not in ANCHORS:
        raise DiagnosticError(f"anchor must be one of {ANCHORS}, got {anchor!r}")
    payloads = payloads if payloads is not None else diagnostic_payloads()
    template = contract.load_h1a_native_template()
    return surface.render_prompt(contract.render_arm(template, arm), payloads[anchor])


def rendered_cells() -> dict:
    """All four distinct prompts, keyed by (arm, anchor). Built once so the
    payload/qualification work is not repeated 20 times."""
    payloads = diagnostic_payloads()
    return {
        (cell["arm"], cell["anchor"]):
            render_diagnostic_prompt(cell["arm"], cell["anchor"], payloads)
        for cell in diagnostic_cells()
    }
