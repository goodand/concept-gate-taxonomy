"""Fixture-level self-checks for E2.4 (repo_evidence_fixture_v2).

Structural guarantees about the model-facing surface live in test_surface.py.
This file checks the fixtures themselves: that they satisfy the v2 schema, that
the model-facing concept surface still mirrors what was actually submitted to
the pipeline, that server_response is reproducible, and that the one designated
repair leaves a clean pipeline state.
"""

import importlib.util
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


surface = _load("e24_surface_protocol", HERE / "_surface.py")
cohort = _load("e24_cohort_protocol", HERE / "_cohort.py")


def _valid_output():
    """A minimal output that satisfies evidence_contract_v1."""
    return {
        "decision": "abstain",
        "contract_verdict": "insufficient_evidence",
        "evidence_scope": {"source_policy": "packet_only", "used_evidence_ids": ["ev1"],
                           "outside_knowledge_used": False},
        "evidence_audit": [{"evidence_id": "ev1", "source_kind": "code",
                            "admissibility": "indirect_context", "supported_type": None,
                            "claim_strength": "weak", "conflicts_with_evidence_ids": [],
                            "rationale": "r"}],
        "feature_judgments": [{"concept": "c", "feature": "f",
                               "original_type": "essential_feature",
                               "sufficiency": "insufficient", "selected_type": None,
                               "evidence_ids": ["ev1"], "rationale": "r"}],
        "invariant_checks": [],
        "repair_plan": {"allowed": False, "steps": [], "reject_reason": "insufficient"},
        "repaired_concepts": None,
        "abstain": {"required": True, "reason": "insufficient_evidence",
                    "missing_evidence": [{"target": "c.f", "request": "r"}]},
        "report": "r",
    }


def _load_cert_core():
    return _load("e24_cert_core", HERE / "_cert_core.py")


def _fixture_paths():
    return sorted(HERE.glob("fixture_*.json"))


def _load_json(path):
    return json.loads(path.read_text())


def _project_server_response(response, expected):
    return {key: response.get(key) for key in expected}


def test_fixtures_satisfy_the_v2_schema():
    """validate_fixture is the schema; there is no separate .json to drift from."""
    for path in _fixture_paths():
        surface.validate_fixture(_load_json(path))


def test_fixtures_qualify_against_the_working_tree():
    """Every cited excerpt must still resolve byte-for-byte where it claims to be.

    This is the check that would catch an evidence source being edited,
    moved, or rewritten out from under a frozen fixture.
    """
    for path in _fixture_paths():
        manifest = surface.qualify_fixture(_load_json(path), REPO_ROOT, run_tests=False)
        assert manifest["status"] == "passed", (path.name, manifest["evidence_checks"])


def test_candidate_concepts_match_run_pipeline_input_surface():
    for path in _fixture_paths():
        packet = _load_json(path)
        candidate = [
            {
                "name": concept["name"],
                "features": [
                    {"feature": f["feature"], "type": f["type"]}
                    for f in concept["features"]
                ],
            }
            for concept in packet["candidate_concepts"]
        ]
        run_input = [
            {
                "name": concept["name"],
                "features": [
                    {"feature": f["feature"], "type": f["type"]}
                    for f in concept["features"]
                ],
            }
            for concept in packet["run_pipeline_input"]
        ]
        assert candidate == run_input, path.name


def test_server_response_is_reproducible_from_run_pipeline_input():
    cert_core = _load_cert_core()
    for path in _fixture_paths():
        packet = _load_json(path)
        observed = cert_core.run_and_certify(packet["run_pipeline_input"])
        expected = packet["server_response"]
        assert _project_server_response(observed, expected) == expected, path.name


# Diagnostics only, per DESIGN_DECISION_surface_separation.md §7: the guard is
# defense-in-depth and must never be the reason something is considered safe.
# The enforcement is build_model_payload's whitelist construction, covered in
# test_surface.py. This scans what the model actually receives rather than raw
# fixture fields -- builder prose now lives in builder_metadata, which the
# builder cannot reach, so scanning fixture text would prove nothing.
_VERDICT_TOKENS = (
    "accept_report",
    "abstain",
    "sufficient_consistent",
    "sufficient_repairable",
    "insufficient_evidence",
    "conflicting_evidence",
    "out_of_scope",
    "direct_support",
    "indirect_context",
)
_EXPECTATION_PHRASES = re.compile(
    r"correct behavior|expected (contract_)?verdict|should abstain|hidden oracle|"
    r"정답|기대 판정",
    re.IGNORECASE,
)


def test_built_payload_carries_no_verdict_vocabulary():
    for path in _fixture_paths():
        fixture = _load_json(path)
        manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=False)
        payload = surface.build_model_payload(fixture, manifest)

        # `text` is verbatim repo content pinned by sha256 and re-verified by
        # qualification, so it is excluded: a source file legitimately may
        # discuss these terms, and an author cannot inject there without
        # changing the repo itself.
        scanned = surface.canonical_json(
            {
                "candidate_concepts": payload["candidate_concepts"],
                "evidence_ids": [e["evidence_id"] for e in payload["evidence_items"]],
                "source_kinds": [e["source_kind"] for e in payload["evidence_items"]],
                "server_response": payload["server_response"],
            }
        )
        leaked = [t for t in _VERDICT_TOKENS if t in scanned]
        assert not leaked, f"{path.name}: verdict vocabulary in payload metadata {leaked}"
        assert not _EXPECTATION_PHRASES.search(scanned), path.name


def test_oracle_manifest_matches_the_migration_scripts_oracle_table():
    """`oracle_manifest.json` and `_migrate_v1_to_v2.py`'s ORACLES table hold the
    same expected answers in two places, and unlike the trial-subject schema the
    manifest **cannot** be regenerated: the migration reads v1 keys
    (`evidence_items`) that no longer exist, so re-running it would KeyError.

    A generator that cannot run is not a drift guard, so this test is the guard.
    It caught nothing when written -- it exists so that editing one copy without
    the other fails here instead of silently scoring against a stale oracle.
    """
    migrate = _load("e24_migrate_protocol", HERE / "_migrate_v1_to_v2.py")
    manifest = _load_json(HERE / "oracle_manifest.json")["fixtures"]

    assert set(manifest) == set(migrate.ORACLES), (
        "fixture id sets differ between oracle_manifest.json and ORACLES"
    )
    for fid, expected in migrate.ORACLES.items():
        got = manifest[fid]
        for key, value in expected.items():
            assert got.get(key) == value, (
                f"{fid}.{key}: manifest has {got.get(key)!r}, "
                f"_migrate_v1_to_v2.py ORACLES has {value!r}"
            )


def test_unobtained_fixture_uses_the_directive_status_vocabulary():
    """The 2026-07-29 operations directive prescribes
    `fixture_unavailable_unverified` for a class whose fixture was never
    obtained. An earlier local coinage ("no_eligible_fixture") meant the same
    thing but is not what another session would grep for.
    """
    manifest = _load_json(HERE / "oracle_manifest.json")["fixtures"]
    assert manifest["E24-F-04"]["status"] == "fixture_unavailable_unverified"
    # The class stays in the schema; only its obtainability is marked.
    assert manifest["E24-F-04"]["expected_contract_verdict"] == "conflicting_evidence"
    schema = json.loads((HERE / "decision_schema.json").read_text())
    verdicts = (schema["variants"]["evidence_contract_v1"]["schema"]
                ["properties"]["contract_verdict"]["enum"])
    assert "conflicting_evidence" in verdicts, "directive §1: keep the class in schema"


def test_trial_subject_definition_matches_the_decision_schema():
    """The output contract exists in two places -- decision_schema.json and the
    trial subject's system prompt -- because the transport cannot deliver a
    schema this size through the structured-output channel. Two hand-maintained
    copies drift, and a drift here scores trials against a contract the model
    never saw, so the second copy is generated and this pins it.
    """
    committed = cohort.AGENT_FILE.read_text(encoding="utf-8")
    assert committed == cohort.agent_definition(), (
        "e2.4-contract-decider.md is stale; run `python3 _cohort.py agent`"
    )
    assert "tools: []" in committed, "the trial subject must have no tools"


def test_frozen_cohort_still_matches_what_the_builder_produces():
    """cohort_prompts.json is committed before any trial runs. If a fixture or
    the contract text moves afterwards, the frozen bytes silently stop
    describing what a rerun would send.
    """
    frozen = json.loads((HERE / "cohort_prompts.json").read_text())
    contract = surface.load_contract_prompt(HERE / "contract_prompt.md")
    for fixture_id, expected in frozen["rendered_prompts"].items():
        fixture = _load_json(HERE / cohort.FIXTURE_FILES[fixture_id])
        manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=False)
        payload = surface.build_model_payload(fixture, manifest)
        assert surface.render_prompt(contract, payload) == expected, fixture_id

    presented = surface.sha256_of(cohort.transport_schema())
    system = surface.sha256_of(cohort.agent_definition())
    for trial in frozen["trials"]:
        assert trial["presented_schema_sha256"] == presented, trial["trial_id"]
        assert trial["system_prompt_sha256"] == system, trial["trial_id"]


def test_output_validator_accepts_valid_and_names_each_defect():
    """A validator that never rejects is worse than none: it turns an unchecked
    artifact into one that looks checked. Each defect below is one the recorded
    cohort could plausibly contain.
    """
    schema = cohort.transport_schema()
    assert cohort.schema_errors(_valid_output(), schema) == []

    def broken(mutate):
        out = _valid_output()
        mutate(out)
        return cohort.schema_errors(out, schema)

    # 'conflict' was removed from the admissibility enum in v2.
    assert broken(lambda o: o["evidence_audit"][0].update(admissibility="conflict"))
    # v1 field name; the payload no longer carries paths.
    assert broken(lambda o: o["evidence_audit"][0].update(source_path="x"))
    assert broken(lambda o: o["evidence_audit"][0].pop("conflicts_with_evidence_ids"))
    assert broken(lambda o: o.update(decision="report_done"))  # legacy enum
    assert broken(lambda o: o.update(contract_verdict="made_up"))
    assert broken(lambda o: o.pop("invariant_checks"))
    assert broken(lambda o: o["feature_judgments"][0].update(selected_type="not_a_type"))
    assert broken(lambda o: o["evidence_scope"].update(outside_knowledge_used="no"))

    # null is a legal selected_type; a bare string type is legal too.
    assert cohort.schema_errors(
        {**_valid_output(),
         "feature_judgments": [{**_valid_output()["feature_judgments"][0],
                                "selected_type": "structural_composition"}]},
        schema,
    ) == []


def test_scorer_reproduces_the_five_step_procedure():
    """conformance() re-derives sufficiency from the trial's own audit and flags
    a trial whose conclusion its own evidence table does not support. That check
    decides certification, so it is gated rather than trusted.

    The tie case is the one PROBLEM_2 §5.1 trial 4 got wrong: it marked both
    items conflicting while also stating neither was direct_support.
    """
    score = _load("e24_score_protocol", HERE / "_score.py")

    payload = {
        "candidate_concepts": [{"name": "c", "features": [
            {"feature": "f", "type": "essential_feature", "evidence_refs": ["ev1"]}]}],
        "evidence_items": [{"evidence_id": "ev1", "source_kind": "code", "text": "t"},
                           {"evidence_id": "ev2", "source_kind": "code", "text": "t"}],
    }

    def audit(*rows):
        return [{"evidence_id": e, "source_kind": "code", "admissibility": a,
                 "supported_type": t, "claim_strength": s,
                 "conflicts_with_evidence_ids": list(c), "rationale": "r"}
                for e, a, t, s, c in rows]

    def out(audit_rows, sufficiency, selected=None, **over):
        o = _valid_output()
        o["evidence_audit"] = audit_rows
        # The feature cites every audited item unless a case overrides it --
        # sufficiency is derived per feature from what that feature cites.
        o["feature_judgments"][0].update(
            sufficiency=sufficiency, selected_type=selected,
            evidence_ids=[r["evidence_id"] for r in audit_rows])
        o.update(over)
        return o

    def conf(o):
        return score.conformance(o, payload)

    ds, ic = "direct_support", "indirect_context"
    ess, comp = "essential_feature", "structural_composition"

    repairing = dict(
        decision="repair", contract_verdict="sufficient_repairable",
        repair_plan={"allowed": True, "steps": [], "reject_reason": None},
        repaired_concepts=[{"name": "c", "features": [
            {"feature": "f", "type": "structural_composition", "evidence": "ev1"}]}],
        abstain={"required": False, "reason": "none", "missing_evidence": []},
    )
    conflicting = dict(
        contract_verdict="conflicting_evidence",
        abstain={"required": True, "reason": "conflicting_evidence",
                 "missing_evidence": []},
    )

    # Step 3: a lone maximum is sufficient.
    assert conf(out(
        audit(("ev1", ds, comp, "explicit", []), ("ev2", ds, comp, "weak", [])),
        "sufficient", comp, **repairing)) == []

    # Step 5: no direct_support candidate at all.
    assert conf(out(audit(("ev1", ic, None, "weak", [])), "insufficient")) == []

    # Step 4: incompatible types tied at the maximum.
    assert conf(out(
        audit(("ev1", ds, ess, "explicit", ["ev2"]), ("ev2", ds, comp, "explicit", ["ev1"])),
        "conflicting", **conflicting)) == []

    # A tie broken by plausibility contradicts the trial's own audit.
    assert any("5-step" in v for v in conf(out(
        audit(("ev1", ds, ess, "explicit", []), ("ev2", ds, comp, "explicit", [])),
        "sufficient", ess)))

    # Step 3 reached, but selected_type is not the type that won.
    assert any("step 3 yields" in v for v in conf(out(
        audit(("ev1", ds, comp, "explicit", [])), "sufficient", ess, **repairing)))

    # PROBLEM_2 §5.1 trial 4: conflict claimed between non-direct_support items.
    bad = conf(out(
        audit(("ev1", ic, None, "weak", ["ev2"]), ("ev2", ic, None, "weak", ["ev1"])),
        "conflicting", **conflicting))
    assert any("non-direct_support" in v for v in bad)
    assert any("5-step" in v for v in bad)  # its own audit yields insufficient

    # Asymmetric conflict.
    assert any("symmetric" in v for v in conf(out(
        audit(("ev1", ds, ess, "explicit", ["ev2"]), ("ev2", ds, comp, "explicit", [])),
        "conflicting", **conflicting)))

    # direct_support must name the type it supports.
    assert any("no supported_type" in v for v in conf(out(
        audit(("ev1", ds, None, "explicit", [])), "insufficient")))

    # Cross-field bookkeeping still applies.
    assert any("repaired_concepts=null" in v for v in conf(
        out(audit(("ev1", ic, None, "weak", [])), "insufficient", repaired_concepts=[])))
    assert any("outside_knowledge_used" in v for v in conf(out(
        audit(("ev1", ic, None, "weak", [])), "insufficient",
        evidence_scope={"source_policy": "packet_only", "used_evidence_ids": [],
                        "outside_knowledge_used": True})))

    # Constraint 6: an id the payload never contained.
    assert any("not in the payload" in v for v in conf(out(
        audit(("ev1", ic, None, "weak", []), ("ev99", ic, None, "weak", [])),
        "insufficient")))

    # Constraint 4: a repair that silently drops part of the input.
    assert any("dropped feature" in v for v in conf(out(
        audit(("ev1", ds, comp, "explicit", [])), "sufficient", comp,
        **{**repairing, "repaired_concepts": [{"name": "c", "features": []}]})))
    assert any("dropped concept" in v for v in conf(out(
        audit(("ev1", ds, comp, "explicit", [])), "sufficient", comp,
        **{**repairing, "repaired_concepts": []})))


def test_scorer_does_not_penalise_an_unrelated_filler_feature():
    """Regression: conformance() used to derive sufficiency once over the whole
    audit and compare it against every per-feature judgment.

    contract_prompt.md rule 5 tells a trial to mark an evidence-free filler
    feature insufficient while still repairing the feature that does have
    evidence -- exactly the shape of fixture_sufficient_repairable.json (바퀴 has
    ev1, 갑종 is filler). The packet-global derivation reported that
    contract-following answer as a violation, which would have scored E24-F-02
    at clean_rate 0 for doing what the contract demands.
    """
    score = _load("e24_score_filler", HERE / "_score.py")
    fixture = _load_json(HERE / "fixture_sufficient_repairable.json")
    manifest = surface.qualify_fixture(fixture, REPO_ROOT, run_tests=False)
    payload = surface.build_model_payload(fixture, manifest)

    out = {
        "decision": "repair",
        "contract_verdict": "sufficient_repairable",
        "evidence_scope": {"source_policy": "packet_only",
                           "used_evidence_ids": ["ev1"],
                           "outside_knowledge_used": False},
        "evidence_audit": [{"evidence_id": "ev1", "source_kind": "fixture",
                            "admissibility": "direct_support",
                            "supported_type": "structural_composition",
                            "claim_strength": "explicit",
                            "conflicts_with_evidence_ids": [], "rationale": "r"}],
        "feature_judgments": [
            {"concept": "돌체", "feature": "바퀴",
             "original_type": "essential_feature", "sufficiency": "sufficient",
             "selected_type": "structural_composition",
             "evidence_ids": ["ev1"], "rationale": "r"},
            {"concept": "돌체", "feature": "갑종",
             "original_type": "essential_feature", "sufficiency": "insufficient",
             "selected_type": None, "evidence_ids": [], "rationale": "filler"},
        ],
        "invariant_checks": [],
        "repair_plan": {"allowed": True, "reject_reason": None,
                        "steps": [{"concept": "돌체", "feature": "바퀴",
                                   "from_type": "essential_feature",
                                   "to_type": "structural_composition",
                                   "evidence_ids": ["ev1"], "reason": "r"}]},
        "repaired_concepts": [{"name": "돌체", "features": [
            {"feature": "바퀴", "type": "structural_composition", "evidence": "ev1"},
            {"feature": "갑종", "type": "essential_feature", "evidence": "none"}]}],
        "abstain": {"required": False, "reason": "none", "missing_evidence": []},
        "report": "r",
    }
    assert score.conformance(out, payload) == []
    assert cohort.schema_errors(out, cohort.transport_schema()) == []


def test_sufficient_repairable_single_repair_yields_clean_pass():
    """Pins fixture_sufficient_repairable.json's intended Rule 3 repair:
    돌체's 바퀴 (essential_feature, evidence states 구성 부분/part-whole)
    should repair to structural_composition, keeping 갑종 as essential so
    the concept still has an essential axis post-repair. Both pre-repair
    (as shipped in run_pipeline_input) and post-repair states must be a
    clean PASS with no anti-patterns -- this is the deterministic half of
    the Rule 3 sufficiency claim; the LLM admissibility/sufficiency
    judgment itself is verified separately via independent review and a
    live CONTRACT_REPO smoke test, not by this test.
    """
    cert_core = _load_cert_core()
    packet = _load_json(HERE / "fixture_sufficient_repairable.json")

    pre = packet["run_pipeline_input"]
    assert pre == [
        {
            "name": "돌체",
            "features": [
                {
                    "feature": "바퀴",
                    "type": "essential_feature",
                    "evidence": "바퀴가 항목에 기록되어 있다",
                },
                {
                    "feature": "갑종",
                    "type": "essential_feature",
                    "evidence": "갑종이(가) 항목에 기록되어 있다",
                },
            ],
        }
    ]

    pre_observed = cert_core.run_and_certify(pre)
    assert pre_observed["status"] == "PASS"
    assert pre_observed["anti_patterns"] == []
    assert pre_observed["composition_issues"] == []

    post = json.loads(json.dumps(pre))
    post[0]["features"][0]["type"] = "structural_composition"
    post_observed = cert_core.run_and_certify(post)
    assert post_observed["status"] == "PASS"
    assert post_observed["anti_patterns"] == []
    assert post_observed["composition_issues"] == []
