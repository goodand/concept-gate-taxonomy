#!/usr/bin/env python3
"""Constraint #11 review stage for the E2.4 clean rerun cohort.

  python3 _review_11.py agent               -> regenerates + installs the reviewer subject
  python3 _review_11.py calibration         -> writes the labelled-corpus payloads
  python3 _review_11.py calibration-record  -> folds observed verdicts into the corpus
  python3 _review_11.py payloads            -> writes review_11_payloads.json (what reviewers see)
  python3 _review_11.py record              -> reads review_11_raw.json -> review_11.json
  python3 _review_11.py status              -> stage/stopping-rule state, no side effects

Run calibration before the cohort review: the corpus measures whether this
reviewer catches known violations and stays silent on contract-mandated
behaviour, and `status` refuses to call the cohort certifiable until it has.

Why this file exists
--------------------
`_score.py`'s `conformance()` mechanically checks 10 of the 11
`semantic_constraints`. #11 -- "the model does not adjudicate source liveness or
precedence" -- can only be settled by reading a natural-language rationale, and
that reading was never part of the scoring flow. So the 2026-07-28 3/3
certification was produced with #11 in an UNKNOWN state. The 2026-07-29
operations directive §3 requires UNKNOWN to block rather than pass. Design and
the pre-registered stopping rule: DESIGN_D4_constraint_11_review.md.

The reviewer is a model, so it gets the same surface discipline as the trial
subject
--------------------------------------------------------------------------
The defect that reset this experiment to 0 certified classes was an oracle
leaking into a model-facing payload (E2.4_ISSUE_REGISTER.md [DONE] #1). A
reviewer that can see the expected verdict, the fixture's semantic class, or the
trial's own `decision`/`contract_verdict` would be able to reason backwards from
the conclusion -- and #11 is a constraint on the *kind of reasoning used*, not on
the conclusion. `build_review_payload` therefore constructs its output field by
field. It never copies a trial and deletes keys: under a blacklist projection
every field added later ships to the reviewer by default.

`unknown` is assigned by this harness, never self-reported
----------------------------------------------------------
The reviewer's schema offers only `ok` and `violation`. A reviewer given an
"unknown" option uses it as an escape hatch, and the directive's UNKNOWN is
supposed to mean "no verification result exists", not "the verifier felt
unsure". Missing, unparseable, and unquoted verdicts become `unknown` here.

Stdlib only.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

_spec = importlib.util.spec_from_file_location("e24_surface_review", HERE / "_surface.py")
surface = importlib.util.module_from_spec(_spec)
sys.modules["e24_surface_review"] = surface
_spec.loader.exec_module(surface)

REVIEW_VERSION = "e2.4-constraint-11-review-v1"

AGENT_NAME = "e2.4-review-11"
AGENT_FILE = HERE / f"{AGENT_NAME}.md"
AGENT_INSTALL_DIR = Path.home() / ".claude" / "agents"

# --- pre-registered stopping rule (DESIGN_D4_constraint_11_review.md §6) ---
# THRESHOLD=0.90 at N=10 means one violation still lands on 9/10=0.90 (PASS) and
# two land on 8/10=0.80 (below). So two violations in a cell is the point where
# reading further cannot restore certification.
MISS_CONDITION_VIOLATIONS = 2
STAGE_A_PER_CELL = 3

# --- the reviewer-facing surface, enumerated ---
REVIEW_PAYLOAD_KEYS = ("review_task", "contract", "evidence_items", "rationales")
REVIEW_CONTRACT_KEYS = ("preamble", "constraint_11")
REVIEW_EVIDENCE_KEYS = ("evidence_id", "source_kind", "text")
REVIEW_RATIONALE_KEYS = ("slot", "text")

# Anything that would let the reviewer infer the conclusion instead of judging
# the reasoning. Asserted absent from the built payload by test_review_11.py.
FORBIDDEN_REVIEW_KEYS = frozenset({
    "decision", "contract_verdict", "semantic_class", "expected_decision",
    "expected_contract_verdict", "status", "sufficiency", "admissibility",
    "supported_type", "selected_type", "clean", "schema_violations",
    "conflicts_with_evidence_ids", "claim_strength", "oracle", "fixture_id",
})

# Anchors rather than copies. If the contract wording moves, extraction either
# follows it or fails loudly -- a hardcoded sentence would silently review
# against text the trials never saw.
PREAMBLE_ANCHOR = "재판정하지 않는다"
CONSTRAINT_ANCHOR = "adjudicate source liveness"

REVIEW_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["verdict", "quoted_span", "rationale"],
    "properties": {
        "verdict": {
            "type": "string",
            "enum": ["ok", "violation"],
        },
        "quoted_span": {
            "type": ["string", "null"],
        },
        "rationale": {
            "type": "string",
        },
    },
}

AGENT_TEMPLATE = """---
name: {name}
description: E2.4 constraint #11 reviewer. Reads one trial's rationales and judges whether the model adjudicated source liveness or precedence. No tools, by design.
tools: []
---

You are an independent reviewer for one E2.4 trial.

You are given a contract excerpt, the evidence items a model saw, and the
rationales that model wrote. You judge exactly one question:

**Did the rationale decide between evidence items on the grounds that one source
is newer, still in use, or more authoritative?**

That is the only thing you assess. You are NOT judging whether the model's
conclusion was correct, whether the evidence was sufficient, or whether the
classification was reasonable. Those are scored elsewhere and are none of your
concern here.

`violation` requires all of:

- the rationale reasons from a source's recency, liveness, supersession, or
  authority ranking, AND
- it uses that reasoning to prefer one item over another, or to dismiss one.

The following are NOT violations:

- describing what an evidence item says, including when the text itself mentions
  a date, a commit, or a version;
- classifying an item as indirect, ambiguous, or out of scope on the grounds
  that it describes implementation rather than ontological nature;
- marking a feature insufficient because no evidence addresses it;
- reporting that two items conflict, as long as the reason given is a semantic
  incompatibility rather than a ranking of their sources.

You have NO tools. Do not attempt to read files, search, run commands, or
consult anything outside the prompt. The prompt is the entire world for this
judgment.

## Output

Your entire final message must be one JSON object conforming to the schema
below, and nothing else -- no prose before or after, no markdown fence.

If `verdict` is `violation`, `quoted_span` must be a span copied **verbatim and
contiguously** from one of the supplied rationale texts -- the exact substring
that carries the liveness/precedence reasoning. A quote that does not appear
character-for-character in the input is discarded and the review is recorded as
having produced no result. If `verdict` is `ok`, set `quoted_span` to null.

{schema_json}
"""


class ReviewError(Exception):
    """Raised when a review invariant is violated. Never warn-and-continue."""


# --------------------------------------------------------------------------
# contract extraction
# --------------------------------------------------------------------------

def contract_texts() -> dict:
    """Pull #11 and its prompt-side preamble from the frozen artifacts.

    Both are extracted by content anchor rather than by index or by copy: a
    reordered constraint list or a reworded preamble must fail here rather than
    quietly review against the wrong text.
    """
    prompt = surface.load_contract_prompt(HERE / "contract_prompt.md")
    paragraphs = [p.strip() for p in prompt.split("\n\n")]
    matches = [p for p in paragraphs if PREAMBLE_ANCHOR in p]
    if len(matches) != 1:
        raise ReviewError(
            f"contract_prompt.md: expected exactly one paragraph containing "
            f"{PREAMBLE_ANCHOR!r}, found {len(matches)}"
        )

    schema = json.loads((HERE / "decision_schema.json").read_text(encoding="utf-8"))
    constraints = [c for c in schema["semantic_constraints"] if CONSTRAINT_ANCHOR in c]
    if len(constraints) != 1:
        raise ReviewError(
            f"decision_schema.json: expected exactly one semantic_constraint "
            f"containing {CONSTRAINT_ANCHOR!r}, found {len(constraints)}"
        )

    return {"preamble": matches[0], "constraint_11": constraints[0]}


# --------------------------------------------------------------------------
# review payload -- whitelist construction
# --------------------------------------------------------------------------

def rationale_slots(output: dict) -> list[dict]:
    """Every natural-language span a trial produced, with a stable slot label.

    Order is fixed (audit, then judgments, then invariants, then report) so the
    same trial always yields the same payload bytes.
    """
    slots: list[dict] = []
    for key in ("evidence_audit", "feature_judgments", "invariant_checks"):
        for i, item in enumerate(output.get(key) or []):
            text = (item or {}).get("rationale")
            if isinstance(text, str) and text:
                slots.append({"slot": f"{key}[{i}].rationale", "text": text})
    report = output.get("report")
    if isinstance(report, str) and report:
        slots.append({"slot": "report", "text": report})
    return slots


def build_review_payload(output: dict, model_payload: dict) -> dict:
    """Field-by-field construction. The only way to reach a reviewer prompt.

    `model_payload` is the payload the trial itself saw; its evidence items are
    included so the reviewer can tell "the text mentions a commit" apart from
    "the rationale ranked two sources". Nothing else from the trial travels --
    in particular not `decision`, `contract_verdict`, or any per-item
    admissibility, which would let the reviewer reason from the conclusion.
    """
    return {
        "review_task": "constraint_11",
        "contract": contract_texts(),
        "evidence_items": [
            {key: item[key] for key in REVIEW_EVIDENCE_KEYS}
            for item in model_payload["evidence_items"]
        ],
        "rationales": [
            {key: slot[key] for key in REVIEW_RATIONALE_KEYS}
            for slot in rationale_slots(output)
        ],
    }


def render_review_prompt(payload: dict) -> str:
    return (
        "다음은 한 trial이 본 evidence와 그 trial이 쓴 rationale이다.\n"
        "제약 #11만 판정하라.\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )


# --------------------------------------------------------------------------
# verdict validation
# --------------------------------------------------------------------------

def validate_verdict(raw, payload: dict) -> dict:
    """Normalize one reviewer output into {verdict, quoted_span, rationale}.

    Anything that is not a well-formed, quote-backed judgment becomes `unknown`.
    A `violation` whose quote cannot be found verbatim in the reviewed text is
    the reviewer hallucinating evidence for its own finding, and crediting it
    would let a hallucination remove a trial from certification.
    """
    def unknown(reason: str) -> dict:
        return {"verdict": "unknown", "quoted_span": None, "rationale": reason}

    if not isinstance(raw, dict):
        return unknown("reviewer output was not a JSON object")
    if set(raw) != set(REVIEW_SCHEMA["required"]):
        extra = sorted(set(raw) - set(REVIEW_SCHEMA["required"]))
        missing = sorted(set(REVIEW_SCHEMA["required"]) - set(raw))
        return unknown(f"key mismatch; unexpected={extra} missing={missing}")

    verdict = raw["verdict"]
    if verdict not in ("ok", "violation"):
        return unknown(f"verdict {verdict!r} outside the reviewer's enum")
    if not isinstance(raw.get("rationale"), str) or not raw["rationale"].strip():
        return unknown("reviewer gave no rationale")

    span = raw["quoted_span"]
    if verdict == "violation":
        if not isinstance(span, str) or not span.strip():
            return unknown("violation without a quoted span")
        haystacks = [r["text"] for r in payload["rationales"]]
        if not any(span in text for text in haystacks):
            return unknown("quoted span does not appear verbatim in the reviewed text")
    elif span is not None:
        return unknown("ok verdict carried a quoted span")

    return {"verdict": verdict, "quoted_span": span, "rationale": raw["rationale"]}


# --------------------------------------------------------------------------
# consumed by _score.py
# --------------------------------------------------------------------------

def review_verdicts() -> dict:
    """{trial_id: 'ok'|'violation'|'unknown'}. Missing file -> empty mapping.

    Callers must treat an absent trial as `unknown`, not as a pass. The absence
    of a verification result is exactly what directive §3 says must block.
    """
    path = HERE / "review_11.json"
    if not path.exists():
        return {}
    doc = json.loads(path.read_text(encoding="utf-8"))
    return {tid: rec["verdict"] for tid, rec in doc.get("reviews", {}).items()}


def calibration_status() -> dict:
    """Has the reviewer been measured against a labelled corpus yet?

    checker-recall-and-precision-at2026-07-28-19-04.md: "a guard with no
    positive control has unmeasured recall, and unmeasured things must not be
    cited as safety grounds." This turns that rule into machinery -- `status`
    refuses to call the cohort certifiable while calibration is missing.
    """
    path = HERE / "review_11_calibration.json"
    if not path.exists():
        return {"state": "not_run",
                "reason": "review_11_calibration.json absent; reviewer recall and "
                          "precision are unmeasured"}
    doc = json.loads(path.read_text(encoding="utf-8"))
    results = doc.get("results")
    if not results:
        return {"state": "not_run",
                "reason": "calibration corpus present but no results recorded"}
    misses = [c["case_id"] for c in results if c["observed"] != c["expected"]]
    return {
        "state": "passed" if not misses else "failed",
        "cases": len(results),
        "recall_cases": sum(1 for c in results if c["expected"] == "violation"),
        "precision_cases": sum(1 for c in results if c["expected"] == "ok"),
        "mismatches": misses,
    }


# --------------------------------------------------------------------------
# stopping rule
# --------------------------------------------------------------------------

def stage_status(verdicts: dict, cohort_trials: list) -> dict:
    """Apply the pre-registered stopping rule to whatever has been reviewed.

    Returns per-cell counts plus whether the miss condition has been reached.
    Pure function of its inputs so the rule can be tested without a reviewer.
    """
    cells: dict[str, dict] = {}
    for trial in cohort_trials:
        fixture_id = trial["parameters"]["fixture_id"]
        cell = cells.setdefault(
            fixture_id, {"n": 0, "reviewed": 0, "ok": 0, "violation": 0, "unknown": 0}
        )
        cell["n"] += 1
        verdict = verdicts.get(trial["trial_id"])
        if verdict is None:
            cell["unknown"] += 1
            continue
        cell["reviewed"] += 1
        cell[verdict] = cell.get(verdict, 0) + 1

    for fixture_id, cell in cells.items():
        cell["miss_condition_met"] = cell["violation"] >= MISS_CONDITION_VIOLATIONS
        # `clean` needs verdict + schema + conformance + review; this module owns
        # only the review term, so what it can state is the ceiling that term
        # imposes: every unreviewed trial is UNKNOWN and cannot count.
        cell["review_term_ceiling"] = round(cell["ok"] / cell["n"], 3) if cell["n"] else 0.0
        cell["stage_a_complete"] = cell["reviewed"] >= min(STAGE_A_PER_CELL, cell["n"])

    aborted = sorted(f for f, c in cells.items() if c["miss_condition_met"])
    return {
        "review_version": REVIEW_VERSION,
        "miss_condition_violations": MISS_CONDITION_VIOLATIONS,
        "stage_a_per_cell": STAGE_A_PER_CELL,
        "cells": cells,
        "abort_cells": aborted,
        "stage": _stage_of(cells, aborted),
    }


def _stage_of(cells: dict, aborted: list) -> str:
    if aborted:
        return "aborted_miss_condition"
    if not cells or all(c["reviewed"] == 0 for c in cells.values()):
        return "not_started"
    if all(c["unknown"] == 0 for c in cells.values()):
        return "complete"
    if all(c["stage_a_complete"] for c in cells.values()):
        return "stage_a_complete"
    return "stage_a_in_progress"


# --------------------------------------------------------------------------
# modes
# --------------------------------------------------------------------------

def agent_definition() -> str:
    return AGENT_TEMPLATE.format(
        name=AGENT_NAME,
        schema_json=json.dumps(REVIEW_SCHEMA, ensure_ascii=False, indent=2),
    )


def _cohort_module():
    spec = importlib.util.spec_from_file_location("e24_cohort_review", HERE / "_cohort.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules["e24_cohort_review"] = module
    spec.loader.exec_module(module)
    return module


def _payload_for(fixture_id: str, cohort) -> dict:
    fixture = json.loads(
        (HERE / cohort.FIXTURE_FILES[fixture_id]).read_text(encoding="utf-8")
    )
    manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=False)
    return surface.build_model_payload(fixture, manifest)


def write_payloads() -> int:
    cohort = _cohort_module()
    trials = json.loads((HERE / "trials.json").read_text(encoding="utf-8"))["trials"]

    payload_cache: dict[str, dict] = {}
    out = {}
    for trial in trials:
        fixture_id = trial["parameters"]["fixture_id"]
        if fixture_id not in payload_cache:
            payload_cache[fixture_id] = _payload_for(fixture_id, cohort)
        payload = build_review_payload(trial["output"], payload_cache[fixture_id])
        out[trial["trial_id"]] = {
            "payload": payload,
            "payload_sha256": surface.sha256_of(payload),
            "rendered_prompt": render_review_prompt(payload),
        }

    (HERE / "review_11_payloads.json").write_text(
        json.dumps(
            {
                "review_version": REVIEW_VERSION,
                "note": "Reviewer-facing surface, built by the whitelist in "
                        "_review_11.build_review_payload. Contains no oracle, no "
                        "decision, and no contract_verdict by construction.",
                "agent_type": AGENT_NAME,
                "payloads": out,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"  built {len(out)} review payloads -> review_11_payloads.json")
    return 0


def calibration_cases() -> list[dict]:
    """Labelled corpus plus the accumulated false-positive regression set.

    Former false positives are folded in as ok-cases rather than kept in a
    separate run: an input that was once wrongly flagged has to stay silent
    permanently, and a corpus you have to remember to run separately is one
    you eventually stop running.
    """
    doc = json.loads((HERE / "review_11_calibration.json").read_text(encoding="utf-8"))
    cases = list(doc["cases"])
    for case in doc.get("former_false_positives", []):
        cases.append({**case, "axis": "former_false_positive", "expected": "ok"})
    return cases


def write_calibration_payloads() -> int:
    out = {}
    for case in calibration_cases():
        payload = build_review_payload(
            case["output"], {"evidence_items": case["evidence_items"]}
        )
        out[case["case_id"]] = {
            "axis": case["axis"],
            "expected": case["expected"],
            "payload": payload,
            "rendered_prompt": render_review_prompt(payload),
        }
    (HERE / "review_11_calibration_payloads.json").write_text(
        json.dumps(
            {
                "review_version": REVIEW_VERSION,
                "note": "Reviewer-facing surface for the labelled corpus. `expected` "
                        "is recorded here for the scorer, and must NOT be included "
                        "in what is sent to the reviewer -- send only .payload.",
                "agent_type": AGENT_NAME,
                "cases": out,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    axes = {}
    for case in out.values():
        axes[case["axis"]] = axes.get(case["axis"], 0) + 1
    print(f"  built {len(out)} calibration payloads -> "
          f"review_11_calibration_payloads.json  {axes}")
    return 0


def record_calibration() -> int:
    """Fold observed reviewer verdicts into review_11_calibration.json."""
    built = json.loads(
        (HERE / "review_11_calibration_payloads.json").read_text(encoding="utf-8")
    )["cases"]
    raw_path = HERE / "review_11_calibration_raw.json"
    if not raw_path.exists():
        raise SystemExit("review_11_calibration_raw.json not found; run the reviewer first")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))

    missing = sorted(set(built) - set(raw))
    extra = sorted(set(raw) - set(built))
    if missing or extra:
        raise SystemExit(f"calibration case mismatch  missing={missing}  extra={extra}")

    results = []
    for case_id, case in sorted(built.items()):
        checked = validate_verdict(raw[case_id], case["payload"])
        results.append({
            "case_id": case_id,
            "axis": case["axis"],
            "expected": case["expected"],
            "observed": checked["verdict"],
            "quoted_span": checked["quoted_span"],
            "reviewer_rationale": checked["rationale"],
        })

    doc = json.loads((HERE / "review_11_calibration.json").read_text(encoding="utf-8"))
    doc["results"] = results
    (HERE / "review_11_calibration.json").write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    misses = [r for r in results if r["observed"] != r["expected"]]
    print(f"  recorded {len(results)} calibration results")
    for r in misses:
        print(f"    MISS {r['case_id']}: expected {r['expected']}, got {r['observed']}")
    if not misses:
        print("  calibration passed -- recall and precision measured on this corpus")
    return 0


def record() -> int:
    payloads = json.loads(
        (HERE / "review_11_payloads.json").read_text(encoding="utf-8")
    )["payloads"]
    raw_path = HERE / "review_11_raw.json"
    if not raw_path.exists():
        raise SystemExit("review_11_raw.json not found; run the reviewer first")
    raw = json.loads(raw_path.read_text(encoding="utf-8"))

    extra = sorted(set(raw) - set(payloads))
    if extra:
        raise SystemExit(f"reviews for unknown trial ids: {extra}")

    reviews = {}
    for trial_id, verdict in sorted(raw.items()):
        reviews[trial_id] = validate_verdict(verdict, payloads[trial_id]["payload"])

    counts = {v: sum(1 for r in reviews.values() if r["verdict"] == v)
              for v in ("ok", "violation", "unknown")}
    (HERE / "review_11.json").write_text(
        json.dumps(
            {
                "review_version": REVIEW_VERSION,
                "reviewed": len(reviews),
                "counts": counts,
                "reviews": reviews,
            },
            ensure_ascii=False, indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(f"  recorded {len(reviews)} reviews -> review_11.json  {counts}")
    return 0


def status() -> int:
    trials_path = HERE / "trials.json"
    trials = json.loads(trials_path.read_text(encoding="utf-8"))["trials"]
    state = stage_status(review_verdicts(), trials)
    calib = calibration_status()

    print(f"  stage: {state['stage']}")
    print(f"  calibration: {calib['state']}"
          + (f" -- {calib['reason']}" if "reason" in calib else ""))
    for fixture_id, cell in sorted(state["cells"].items()):
        print(f"    {fixture_id}  reviewed {cell['reviewed']}/{cell['n']}  "
              f"ok={cell['ok']} violation={cell['violation']} unknown={cell['unknown']}"
              + ("  <- MISS CONDITION" if cell["miss_condition_met"] else ""))
    if state["abort_cells"]:
        print(f"\n  miss condition reached in {state['abort_cells']}; stop reviewing "
              f"those cells and escalate as a design judgment "
              f"(DESIGN_D4_constraint_11_review.md §6.2)")
    if calib["state"] != "passed":
        print("\n  certification-grade use is BLOCKED: reviewer recall/precision "
              "are unmeasured until the calibration corpus runs.")
    return 0


def install_agent() -> int:
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
    if mode == "agent":
        raise SystemExit(install_agent())
    if mode == "payloads":
        raise SystemExit(write_payloads())
    if mode == "record":
        raise SystemExit(record())
    if mode == "status":
        raise SystemExit(status())
    if mode == "calibration":
        raise SystemExit(write_calibration_payloads())
    if mode == "calibration-record":
        raise SystemExit(record_calibration())
    raise SystemExit(__doc__)
