"""Self-checks for the constraint #11 review stage (_review_11.py).

What this file can and cannot establish
---------------------------------------
#11 is judged by a model, so the *judgment's* recall and precision are measured
by the labelled corpus in review_11_calibration.json, which needs a reviewer to
run (the agent registry is fixed at session start, so that is a separate
session). What is deterministic -- and therefore tested here -- is the harness
around that judgment: the whitelist that builds the reviewer's surface, the
quote enforcement that discards hallucinated findings, the UNKNOWN rule that
makes a missing result block rather than pass, and the arithmetic of the
pre-registered stopping rule.

checker-recall-and-precision-at2026-07-28-19-04.md §축 전수화 is applied to the
harness: every collection it iterates is exercised at 0, 1, and 2+ items. The
scorer bug this experiment already hit surfaced only at len>=2.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


review = _load("e24_review11_test", HERE / "_review_11.py")
score = _load("e24_score_review11_test", HERE / "_score.py")


def _payload(rationales):
    return {"rationales": [{"slot": f"s{i}", "text": t}
                           for i, t in enumerate(rationales)]}


# --------------------------------------------------------------------------
# contract extraction -- anchors, not copies
# --------------------------------------------------------------------------

def test_contract_texts_resolve_to_exactly_one_span_each():
    texts = review.contract_texts()
    assert set(texts) == set(review.REVIEW_CONTRACT_KEYS)
    assert review.PREAMBLE_ANCHOR in texts["preamble"]
    assert review.CONSTRAINT_ANCHOR in texts["constraint_11"]


def test_contract_extraction_fails_loudly_when_the_anchor_moves():
    """A reworded contract must stop the review, not review against stale text.

    The failure mode being prevented: someone edits contract_prompt.md, the
    anchor no longer matches, and a hardcoded fallback silently reviews 30
    trials against wording they never saw.
    """
    original = review.PREAMBLE_ANCHOR
    try:
        review.PREAMBLE_ANCHOR = "이 문장은 계약에 존재하지 않는다"
        with pytest.raises(review.ReviewError):
            review.contract_texts()
    finally:
        review.PREAMBLE_ANCHOR = original


# --------------------------------------------------------------------------
# reviewer surface -- whitelist construction
# --------------------------------------------------------------------------

def _all_keys(node):
    if isinstance(node, dict):
        for key, value in node.items():
            yield key
            yield from _all_keys(value)
    elif isinstance(node, list):
        for value in node:
            yield from _all_keys(value)


def test_review_payload_never_carries_conclusion_fields():
    """The whitelist is the enforcement; this is its positive control.

    The trial output below carries every field that would let a reviewer read
    the conclusion off the structure instead of judging the reasoning.
    """
    output = {
        "decision": "accept_report",
        "contract_verdict": "sufficient_consistent",
        "evidence_audit": [{"evidence_id": "ev1", "admissibility": "direct_support",
                            "supported_type": "structural_composition",
                            "claim_strength": "explicit",
                            "conflicts_with_evidence_ids": [],
                            "rationale": "ev1은 부분-전체 관계를 명시한다."}],
        "feature_judgments": [{"concept": "c", "feature": "f",
                               "sufficiency": "sufficient",
                               "selected_type": "structural_composition",
                               "rationale": "확정한다."}],
        "report": "요약",
    }
    model_payload = {"evidence_items": [
        {"evidence_id": "ev1", "source_kind": "code", "text": "t", "text_sha256": "x"}
    ]}

    built = review.build_review_payload(output, model_payload)

    assert tuple(built) == review.REVIEW_PAYLOAD_KEYS
    assert not set(_all_keys(built)) & review.FORBIDDEN_REVIEW_KEYS
    # text_sha256 was present in the source item and must not survive projection
    assert set(built["evidence_items"][0]) == set(review.REVIEW_EVIDENCE_KEYS)
    for item in built["rationales"]:
        assert set(item) == set(review.REVIEW_RATIONALE_KEYS)


def test_contract_excerpt_and_evidence_carry_no_verdict_vocabulary():
    """Separates what the builder controls from what it cannot.

    Verdict words DO reach the reviewer -- trials name their own verdict inside
    `rationale` prose (23/30 say "accept_report"). That is inherent to the text
    under review. What the builder is responsible for is the two surfaces it
    constructs itself, and those must stay clean.
    """
    built = json.loads((HERE / "review_11_payloads.json").read_text(encoding="utf-8"))
    vocabulary = ("accept_report", "sufficient_consistent", "sufficient_repairable",
                  "insufficient_evidence", "conflicting_evidence", "expected_")
    for trial_id, record in built["payloads"].items():
        payload = record["payload"]
        for surface_name in ("contract", "evidence_items"):
            blob = json.dumps(payload[surface_name], ensure_ascii=False)
            for term in vocabulary:
                assert term not in blob, f"{trial_id}.{surface_name} leaked {term!r}"


@pytest.mark.parametrize("n", [0, 1, 2, 3])
def test_rationale_slots_across_the_cardinality_axis(n):
    output = {"evidence_audit": [{"rationale": f"r{i}"} for i in range(n)]}
    assert len(review.rationale_slots(output)) == n


def test_rationale_slots_skips_empty_and_missing_text():
    output = {
        "evidence_audit": [{"rationale": ""}, {"rationale": None}, {}],
        "feature_judgments": [{"rationale": "kept"}],
        "report": "",
    }
    slots = review.rationale_slots(output)
    assert [s["text"] for s in slots] == ["kept"]


def test_rationale_slot_labels_are_stable_and_ordered():
    output = {
        "evidence_audit": [{"rationale": "a"}],
        "feature_judgments": [{"rationale": "b"}],
        "invariant_checks": [{"rationale": "c"}],
        "report": "d",
    }
    assert [s["slot"] for s in review.rationale_slots(output)] == [
        "evidence_audit[0].rationale",
        "feature_judgments[0].rationale",
        "invariant_checks[0].rationale",
        "report",
    ]


# --------------------------------------------------------------------------
# quote enforcement -- a finding must be backed by the text it judges
# --------------------------------------------------------------------------

def test_violation_with_a_verbatim_quote_is_kept():
    payload = _payload(["ev6이 더 나중 커밋이므로 ev5를 대체한다."])
    got = review.validate_verdict(
        {"verdict": "violation", "quoted_span": "더 나중 커밋이므로",
         "rationale": "recency ranking"}, payload)
    assert got["verdict"] == "violation"
    assert got["quoted_span"] == "더 나중 커밋이므로"


def test_violation_with_a_hallucinated_quote_becomes_unknown():
    """A reviewer inventing its own evidence must not remove a trial from
    certification. This is the reviewer-side analogue of the fixture leak: an
    unbacked assertion that changes a score."""
    payload = _payload(["ev1은 부분-전체 관계를 명시한다."])
    got = review.validate_verdict(
        {"verdict": "violation", "quoted_span": "더 권위 있으므로",
         "rationale": "authority ranking"}, payload)
    assert got["verdict"] == "unknown"
    assert "verbatim" in got["rationale"]


@pytest.mark.parametrize("span", [None, "", "   "])
def test_violation_without_a_usable_quote_becomes_unknown(span):
    got = review.validate_verdict(
        {"verdict": "violation", "quoted_span": span, "rationale": "r"},
        _payload(["some text"]))
    assert got["verdict"] == "unknown"


def test_ok_verdict_must_not_carry_a_quote():
    got = review.validate_verdict(
        {"verdict": "ok", "quoted_span": "some text", "rationale": "r"},
        _payload(["some text"]))
    assert got["verdict"] == "unknown"


def test_ok_verdict_with_null_span_is_kept():
    got = review.validate_verdict(
        {"verdict": "ok", "quoted_span": None, "rationale": "no ranking found"},
        _payload(["some text"]))
    assert got["verdict"] == "ok"


@pytest.mark.parametrize("raw", [
    None,
    "violation",
    [],
    {},
    {"verdict": "violation"},
    {"verdict": "unknown", "quoted_span": None, "rationale": "r"},
    {"verdict": "ok", "quoted_span": None, "rationale": ""},
    {"verdict": "ok", "quoted_span": None, "rationale": "r", "extra": 1},
])
def test_malformed_reviewer_output_becomes_unknown(raw):
    got = review.validate_verdict(raw, _payload(["some text"]))
    assert got["verdict"] == "unknown"


def test_reviewer_schema_offers_no_unknown_escape_hatch():
    """`unknown` means "no result exists", not "the reviewer felt unsure"."""
    assert review.REVIEW_SCHEMA["properties"]["verdict"]["enum"] == ["ok", "violation"]


# --------------------------------------------------------------------------
# the stopping rule
# --------------------------------------------------------------------------

def test_miss_condition_is_derived_from_the_scorer_constants():
    """The pre-registered "two violations" is not a free parameter.

    It is the smallest number of violations that pushes a cell below
    THRESHOLD at PROTOCOL_N. Deriving it here means changing the threshold or
    the protocol N without revisiting the stopping rule fails this test rather
    than silently invalidating DESIGN_D4_constraint_11_review.md §6.1.
    """
    n, threshold = score.PROTOCOL_N, score.THRESHOLD
    smallest = next(v for v in range(n + 1) if (n - v) / n < threshold)
    assert review.MISS_CONDITION_VIOLATIONS == smallest


def _cohort_trials(counts):
    trials = []
    for fixture_id, n in counts.items():
        for i in range(1, n + 1):
            trials.append({"trial_id": f"{fixture_id}-{i:02d}",
                           "parameters": {"fixture_id": fixture_id}})
    return trials


def test_unreviewed_trials_count_as_unknown_not_as_pass():
    """Directive §3: absence of a verification result blocks."""
    trials = _cohort_trials({"E24-F-01": 10})
    state = review.stage_status({}, trials)
    cell = state["cells"]["E24-F-01"]
    assert cell["unknown"] == 10 and cell["ok"] == 0
    assert cell["review_term_ceiling"] == 0.0
    assert state["stage"] == "not_started"


@pytest.mark.parametrize("violations,expected", [(0, False), (1, False), (2, True), (3, True)])
def test_miss_condition_triggers_at_two_violations(violations, expected):
    trials = _cohort_trials({"E24-F-01": 10})
    verdicts = {}
    for i, trial in enumerate(trials):
        verdicts[trial["trial_id"]] = "violation" if i < violations else "ok"
    state = review.stage_status(verdicts, trials)
    assert state["cells"]["E24-F-01"]["miss_condition_met"] is expected
    assert (state["stage"] == "aborted_miss_condition") is expected


def test_one_violation_still_clears_the_threshold():
    """9/10 = 0.90 is inside screened_PASS, so a single violation must not abort.

    Stated as a test because the boundary is inclusive and an off-by-one here
    would abort a cell that the pre-registered bands still certify.
    """
    trials = _cohort_trials({"E24-F-01": 10})
    verdicts = {t["trial_id"]: "ok" for t in trials}
    verdicts[trials[0]["trial_id"]] = "violation"
    state = review.stage_status(verdicts, trials)
    assert state["cells"]["E24-F-01"]["review_term_ceiling"] == 0.9
    assert score.band(0.9) == "screened_PASS"
    assert not state["abort_cells"]


def test_stage_progression_reports_complete_only_when_nothing_is_unknown():
    trials = _cohort_trials({"E24-F-01": 10, "E24-F-02": 10})
    partial = {t["trial_id"]: "ok" for t in trials[:review.STAGE_A_PER_CELL]}
    assert review.stage_status(partial, trials)["stage"] == "stage_a_in_progress"

    stage_a = {t["trial_id"]: "ok" for t in trials
               if int(t["trial_id"][-2:]) <= review.STAGE_A_PER_CELL}
    assert review.stage_status(stage_a, trials)["stage"] == "stage_a_complete"

    everything = {t["trial_id"]: "ok" for t in trials}
    assert review.stage_status(everything, trials)["stage"] == "complete"


@pytest.mark.parametrize("cells", [{}, {"E24-F-01": 1}, {"E24-F-01": 2, "E24-F-02": 2}])
def test_stage_status_across_the_cell_cardinality_axis(cells):
    state = review.stage_status({}, _cohort_trials(cells))
    assert len(state["cells"]) == len(cells)


# --------------------------------------------------------------------------
# calibration gate
# --------------------------------------------------------------------------

def test_calibration_blocks_certification_until_it_has_been_run():
    """A guard with no positive control has unmeasured recall, and unmeasured
    things must not be cited as safety grounds. Enforced, not annotated."""
    status = review.calibration_status()
    assert status["state"] in {"not_run", "passed", "failed"}
    if status["state"] == "not_run":
        assert "reason" in status


def test_calibration_corpus_covers_both_directions_and_the_cardinality_axis():
    corpus = json.loads((HERE / "review_11_calibration.json").read_text(encoding="utf-8"))
    axes = {}
    for case in corpus["cases"]:
        axes.setdefault(case["axis"], []).append(case)

    assert axes.get("recall"), "no known-violation cases: reviewer recall would be unmeasured"
    assert axes.get("precision"), "no contract-mandated cases: reviewer precision would be unmeasured"
    assert all(c["expected"] == "violation" for c in axes["recall"])
    assert all(c["expected"] == "ok" for c in axes["precision"])

    lengths = {len(review.rationale_slots(c["output"])) for c in corpus["cases"]}
    assert 0 in lengths and 1 in lengths and max(lengths) >= 2, (
        f"rationale-count axis not exercised at 0/1/2+, saw {sorted(lengths)}"
    )
    evidence_counts = {len(c["evidence_items"]) for c in corpus["cases"]}
    assert 0 in evidence_counts and max(evidence_counts) >= 2, (
        f"evidence-count axis not exercised at 0/1/2+, saw {sorted(evidence_counts)}"
    )


def test_calibration_has_cases_that_mention_recency_without_ranking():
    """The discriminating axis.

    If every ok-case avoided the words "commit", "stale", "newer", a reviewer
    could score perfectly by keyword-matching and the corpus would not have
    measured whether it judges *use of a ranking*.
    """
    corpus = json.loads((HERE / "review_11_calibration.json").read_text(encoding="utf-8"))
    signal = ("커밋", "stale", "최신", "나중")
    ok_cases_with_signal = [
        case for case in corpus["cases"]
        if case["expected"] == "ok"
        and any(word in json.dumps(case, ensure_ascii=False) for word in signal)
    ]
    assert ok_cases_with_signal, (
        "every ok-case avoids recency vocabulary; the corpus cannot tell a "
        "keyword matcher apart from a reviewer that judges the reasoning"
    )


def test_calibration_expectations_are_not_sent_to_the_reviewer():
    """`expected` sits beside the payload for the scorer. It must not be inside
    the payload -- that would be the fixture leak, rebuilt in the review stage."""
    built = json.loads(
        (HERE / "review_11_calibration_payloads.json").read_text(encoding="utf-8")
    )
    for case_id, case in built["cases"].items():
        blob = json.dumps(case["payload"], ensure_ascii=False)
        assert "expected" not in case["payload"]
        assert case["expected"] not in (case["payload"].get("review_task"),)
        assert "violation" not in blob, f"{case_id}: label vocabulary reached the payload"


# --------------------------------------------------------------------------
# generated artifacts stay in sync
# --------------------------------------------------------------------------

def test_reviewer_agent_definition_matches_the_schema_in_code():
    """Two copies exist by necessity (committed + installed). Both are written
    from one source, and this fails if the file was hand-edited."""
    assert review.AGENT_FILE.exists(), "run `python3 _review_11.py agent`"
    assert review.AGENT_FILE.read_text(encoding="utf-8") == review.agent_definition()


def test_review_payloads_cover_every_recorded_trial():
    trials = json.loads((HERE / "trials.json").read_text(encoding="utf-8"))["trials"]
    built = json.loads((HERE / "review_11_payloads.json").read_text(encoding="utf-8"))
    assert set(built["payloads"]) == {t["trial_id"] for t in trials}
