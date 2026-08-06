"""Protocol gate. Both directions for every boundary this experiment claims.

Positive-only tests cannot distinguish a working boundary from a vacuous one,
so each check here has a partner that feeds the violating input. The frozen
conditions from the preregistration are checked BY MACHINE, not by reading --
including the 0%-overlap condition on DS05, which a human eyeballing the two
strings would have called satisfied while lexical search still found the target
at rank 2 (measured 2026-08-07).
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _contract import (ARMS, ContractError, UPSTREAM, tokens,  # noqa: E402
                       validate_case, validate_gold, validate_subagent_output,
                       validate_trace)
from _controllers import AnswersImmediately, leaky_subagent, make  # noqa: E402
from _evaluator import (evaluate, frozen_surface_drift, frozen_surface_hashes,
                        run_clean_judge, source_hashes)  # noqa: E402
from _runner import BudgetGuard, Corpus, run_case  # noqa: E402
from run_calibration import load, reference_trace  # noqa: E402
from run_smoke import calibration_surface_drift  # noqa: E402

CORPUS_L = HERE / "public_corpus" / "variant-L"
CORPUS_M = HERE / "public_corpus" / "variant-M"


@pytest.fixture(scope="module")
def data():
    cases, gold = load()
    return cases, gold, Corpus(CORPUS_L)


# --------------------------------------------------------------------------
# frozen case conditions -- checked mechanically
# --------------------------------------------------------------------------
def test_DS05_target_shares_no_vocabulary_with_the_question(data):
    """The prereg's operational definition, not an impression of it."""
    cases, gold, _ = data
    query = cases["DS05"]["query"]
    target = gold["DS05"]["critical_paths"][0]
    title = (CORPUS_L / target).read_text(encoding="utf-8").splitlines()[0]
    assert tokens(query) & tokens(f"{target} {title}") == set()


def test_DS05_is_not_reachable_by_the_first_search(data):
    """0% overlap in the NAME is not enough: the first version kept the query's
    content words in the BODY, lexical search returned the target at rank 2,
    and the case tested nothing. Recall gain saturating at the first action is
    what exposed it."""
    cases, gold, corpus = data
    assert gold["DS05"]["critical_paths"][0] not in corpus.search(cases["DS05"]["query"])


def test_DS05_is_reachable_by_a_link(data):
    """A case that is unreachable by ANY route is broken, not hard."""
    _, gold, corpus = data
    assert gold["DS05"]["critical_paths"][0] in corpus.links(
        "docs/directory-cleanup-plan.md")


def test_the_two_variants_differ_in_exactly_one_file():
    """The paired attack is only paired if nothing else moved."""
    def h(root):
        return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(root.rglob("*")) if p.is_file()}
    left, right = h(CORPUS_L), h(CORPUS_M)
    assert set(left) == set(right)
    assert [k for k in left if left[k] != right[k]] == ["docs/HANDOFF.md"]


def test_discovery_cases_never_reveal_the_handoff_path(data):
    cases, _, _ = data
    for case in cases.values():
        if case["condition"] == "discovery":
            assert "handoff_path" not in case


# --------------------------------------------------------------------------
# public/hidden boundary -- both directions
# --------------------------------------------------------------------------
def test_no_public_artifact_carries_a_gold_key(data):
    cases, _, _ = data
    for case in cases.values():
        validate_case(case)          # raises on leakage


def test_a_case_carrying_a_gold_key_is_rejected(data):
    cases, _, _ = data
    bad = dict(cases["HD01"], critical_paths=["docs/HANDOFF.md"])
    with pytest.raises(ContractError, match="gold key"):
        validate_case(bad)


def test_an_honest_subagent_output_validates(data):
    _, _, corpus = data
    from _runner import retrieval_subagent
    cases, _, _ = data
    validate_subagent_output(retrieval_subagent(corpus, cases["HD01"]))


def test_a_subagent_that_returns_a_conclusion_is_C3(data):
    cases, _, corpus = data
    with pytest.raises(ContractError, match="C3"):
        validate_subagent_output(leaky_subagent(corpus, cases["HD01"]))


def test_an_action_outside_the_closed_set_is_C2():
    trace = {"contract_version": "handoff-dyn-trace-v1", "arm": "S_STATIC",
             "reads": [], "actions": [{"action": "call_a_friend",
                                       "candidates_before": [], "candidates_after": []}]}
    with pytest.raises(ContractError, match="C2"):
        validate_trace(trace)


# --------------------------------------------------------------------------
# budget guard -- both directions
# --------------------------------------------------------------------------
def test_guard_refuses_a_terminal_action_before_exploration():
    guard = BudgetGuard()
    guard.first_search_paths = {"docs/HANDOFF.md"}
    guard.queries.add("q")
    assert guard.check("answer") is not None


def test_guard_allows_a_terminal_action_after_exploration():
    """PRECISION. A guard that never lets anything through would make every arm
    C1 and manufacture the comparison."""
    guard = BudgetGuard()
    guard.first_search_paths = {"docs/HANDOFF.md"}
    guard.queries.add("q")
    guard.follow_links = 1
    guard.reads = 1
    guard.beyond_first_search = 1
    assert guard.check("answer") is None


def test_abstention_needs_more_than_an_answer_does():
    """A first-search miss is not evidence of absence."""
    guard = BudgetGuard()
    guard.first_search_paths = {"docs/HANDOFF.md"}
    guard.queries.add("q")
    guard.follow_links = 1
    guard.reads = 1
    guard.beyond_first_search = 1
    assert guard.check("answer") is None
    assert guard.check("abstain") is not None      # reformulations == 0


def test_a_controller_that_only_tries_to_answer_ends_in_C1(data):
    cases, _, corpus = data
    trace = run_case(cases["HD01"], "S_DYNAMIC", AnswersImmediately(), corpus)
    assert "C1" in trace["failure_codes"]


def test_the_honest_controllers_do_reach_an_answer(data):
    """PRECISION for the guard, measured through the runner rather than the
    hand-built reference -- a runner bug once made every honest run read None
    and the reference-only calibration could not see it."""
    cases, gold, corpus = data
    for arm in ARMS:
        trace = run_case(cases["HD01"], arm, make(arm), corpus)
        assert trace["stop_reason"] == "answer", (arm, trace["stop_reason"])
        assert None not in {r["path"] for r in trace["reads"]}
        assert gold["HD01"]["handoff_path"] in {r["path"] for r in trace["reads"]}


# --------------------------------------------------------------------------
# evaluator -- both directions
# --------------------------------------------------------------------------
def test_the_reference_trace_passes_every_hard_gate(data):
    cases, gold, corpus = data
    for cid, case in cases.items():
        res = evaluate(reference_trace(case, gold[cid], corpus), gold[cid], case)
        assert res["full_hard_gate"], (cid, res["failure_codes"])


@pytest.mark.parametrize("mutate,code", [
    (lambda t: t.update(reads=[]) or t, "R1"),
    (lambda t: t.update(declared_absent=True) or t, "A1"),
    (lambda t: t.update(claims=[{"claim_id": "x", "support": [
        {"path": "docs/glossary.md", "start": 1, "end": 5}]}]) or t, "C4"),
    (lambda t: t.update(uncertainties=[{"critical_paths": ["x"]}]) or t, "E1"),
    (lambda t: t.update(recommended_actions=["restart the nightly job"]) or t, "S1"),
])
def test_each_defect_produces_its_code(data, mutate, code):
    cases, gold, corpus = data
    cid = "DS06" if code == "S1" else ("DS07" if code == "A1" else "HD01")
    trace = mutate(reference_trace(cases[cid], gold[cid], corpus))
    assert code in evaluate(trace, gold[cid], cases[cid])["failure_codes"]


def test_a_gold_forbidden_term_never_occurs_in_its_own_authority(data):
    """Substring matching cannot see negation: `["freeze"]` matched "there is no
    freeze in effect" and failed the correct answer. Three gold entries had this
    defect when written."""
    _, gold, corpus = data
    for cid, g in gold.items():
        text = "\n".join(corpus.read(p, 1, 40) for p in g["expected_authority"]).lower()
        for group in g.get("forbidden_terms", []):
            assert not all(t.lower() in text for t in group), (cid, group)


# --------------------------------------------------------------------------
# clean judge
# --------------------------------------------------------------------------
def test_clean_judge_agrees_with_in_process_on_a_good_trace(data, tmp_path):
    cases, gold, corpus = data
    ref = reference_trace(cases["HD01"], gold["HD01"], corpus)
    payload = tmp_path / "p.json"
    payload.write_text(json.dumps(
        {"trace": ref, "gold": gold["HD01"], "case": cases["HD01"]}), encoding="utf-8")
    assert run_clean_judge(payload, source_hashes())["full_hard_gate"] is True


def test_clean_judge_refuses_a_drifted_source_pin(data, tmp_path):
    cases, gold, corpus = data
    ref = reference_trace(cases["HD01"], gold["HD01"], corpus)
    payload = tmp_path / "p.json"
    payload.write_text(json.dumps(
        {"trace": ref, "gold": gold["HD01"], "case": cases["HD01"]}), encoding="utf-8")
    bad = run_clean_judge(payload, {**source_hashes(), "_contract.py": "0" * 64})
    assert bad.get("returncode") == 3


def test_clean_judge_requires_a_command_line_pycache_prefix(data, tmp_path):
    """-E ignores PYTHONPYCACHEPREFIX, so cache isolation must use -X."""
    cases, gold, corpus = data
    ref = reference_trace(cases["HD01"], gold["HD01"], corpus)
    payload = tmp_path / "p.json"
    payload.write_text(json.dumps(
        {"trace": ref, "gold": gold["HD01"], "case": cases["HD01"]}), encoding="utf-8")
    import subprocess
    cmd = [sys.executable, "-B", "-E", "-P", "-I", str(HERE / "_evaluator.py"),
           "--payload", str(payload), "--verify-self", "--pins",
           json.dumps(source_hashes())]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    assert proc.returncode == 4
    assert "pycache_prefix" in proc.stderr


def test_frozen_surface_fingerprint_detects_input_drift():
    pins = frozen_surface_hashes()
    assert frozen_surface_drift(pins) == []
    changed = dict(pins)
    changed["hidden_gold/gold.json"] = "0" * 64
    assert frozen_surface_drift(changed) == ["hidden_gold/gold.json"]


def test_smoke_rejects_a_calibration_from_a_changed_surface():
    calibration = {"frozen_surface_hashes": frozen_surface_hashes()}
    assert calibration_surface_drift(calibration) == []
    calibration["frozen_surface_hashes"]["_runner.py"] = "0" * 64
    assert calibration_surface_drift(calibration) == ["_runner.py"]


def test_smoke_entrypoint_refuses_a_stale_calibration(monkeypatch, tmp_path):
    """Exercise the actual Phase B gate, not only its helper."""
    import run_smoke
    stale = frozen_surface_hashes()
    stale["_runner.py"] = "0" * 64
    result_dir = tmp_path / "results"
    result_dir.mkdir()
    (result_dir / "calibration.json").write_text(
        json.dumps({"failures": [], "frozen_surface_hashes": stale}),
        encoding="utf-8")
    monkeypatch.setattr(run_smoke, "HERE", tmp_path)
    assert run_smoke.main() == 2


# --------------------------------------------------------------------------
# calibration must have run and passed before any smoke result is meaningful
# --------------------------------------------------------------------------
def test_calibration_artifact_exists_and_is_clean():
    path = HERE / "results" / "calibration.json"
    assert path.is_file(), "run_calibration.py has not been executed"
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["failures"] == [], data["failures"]
    assert data["negative_detected"] == data["negative_total"]
    assert frozen_surface_drift(data.get("frozen_surface_hashes")) == []


def test_upstream_drift_is_reported_not_enforced():
    """Upstream lives in a dirty worktree this experiment may not freeze, so
    drift is a warning. The test fails only if the pin table is empty -- an
    empty pin would make the warning unfalsifiable."""
    assert UPSTREAM and all(len(v) == 64 for v in UPSTREAM.values())
    base = Path("/Users/jaehyuntak/Desktop/Project_in_progress/.vault-harness/"
                "vault-md-retrieval")
    drift = []
    for name, want in UPSTREAM.items():
        path = base / name
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() != want:
            drift.append(name)
    if drift:
        pytest.skip(f"upstream drifted (informational): {drift}")
