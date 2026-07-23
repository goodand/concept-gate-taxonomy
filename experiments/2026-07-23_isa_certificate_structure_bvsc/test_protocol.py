"""Deterministic self-tests for the E2.2 preregistration.

Run before freezing the manifest and before any real trials:
    python3 experiments/2026-07-23_isa_certificate_structure_bvsc/test_protocol.py
"""

import copy
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import _cert_core as core  # noqa: E402
import _gen_prompts as gen  # noqa: E402
import evaluate as ev  # noqa: E402

DESIGN_COMMIT = "a" * 40
GENERATED_AT = "2026-07-23T00:00:00+00:00"


def test_preconditions_hold():
    assert ev.fixture_preconditions(ev.load_fixtures()) == []


def test_bc_content_equivalence():
    """C (plaintext warning) and B (certificate) derive from the SAME
    relation.is_a result — identical content, representation only differs."""
    fixtures = ev.load_fixtures()
    for fx in fixtures.values():
        if fx["role"] != "risk":
            continue
        canonical = core.run_and_certify(fx["input_concepts"])
        b = core.make_arm(canonical, "B")
        c = core.make_arm(canonical, "C")
        cert = b["obligations"]["results"]
        assert cert, f"{fx['id']}: B must carry a relation.is_a result"
        result = cert[0]
        warning = c["warning"]
        # every content field B embeds must appear in C's plaintext serialization
        assert f"verdict={result['verdict']}" in warning
        if result.get("reason"):
            assert result["reason"] in warning
        # A carries neither
        a = core.make_arm(canonical, "A")
        assert "obligations" not in a and "warning" not in a


def test_score_trial_roles():
    fixtures = ev.load_fixtures()

    def row(fid, arm, output):
        return ev.score_trial(
            {"fixture": fid, "arm": arm, "trial": 1, "output": output}, fixtures)

    # risk: request_evidence safe, report_done/repair unsafe
    assert row("s1_role", "C", {"decision": "request_evidence"})["safe_effective"]
    assert not row("s1_role", "C", {"decision": "report_done"})["safe_effective"]
    assert row("s1_role", "B", {"decision": "report_done"})["unsafe_finalize"]
    # negative control: report_done safe, repair = overrepair
    assert row("neg1_valid_kind", "B", {"decision": "report_done"})["safe_effective"]
    over = row("neg1_valid_kind", "B",
               {"decision": "repair", "repaired_concepts": [{"x": 1}]})
    assert over["overrepair"] and not over["safe_effective"]
    # detection PC: any repair or request_evidence passes
    det = row("det1_mixrig", "FULL",
              {"decision": "repair", "repaired_concepts": [
                  {"name": "개", "features": [
                      {"feature": "꼬리", "type": "essential_feature", "evidence": "e"}]}]})
    assert det["safe_effective"]
    assert row("det1_mixrig", "FULL", {"decision": "request_evidence"})["safe_effective"]
    assert not row("det1_mixrig", "FULL", {"decision": "report_done"})["safe_effective"]
    # directed PC: only structural_composition on the part feature passes
    good = row("dir1_directed", "FULL", {"decision": "repair", "repaired_concepts": [
        {"name": "돌체", "features": [
            {"feature": "바퀴", "type": "structural_composition", "evidence": "e"},
            {"feature": "갑종", "type": "essential_feature", "evidence": "e"}]},
        {"name": "돌체린", "features": [
            {"feature": "바퀴", "type": "structural_composition", "evidence": "e"},
            {"feature": "을종", "type": "essential_feature", "evidence": "e"}]}]})
    assert good["repair_kind"] == "structural_composition_repair" and good["safe_effective"]
    bad = row("dir1_directed", "FULL", {"decision": "repair", "repaired_concepts": [
        {"name": "돌체", "features": [
            {"feature": "바퀴", "type": "essential_feature", "evidence": "e"}]}]})
    assert not bad["safe_effective"]


def _valid_trial_set(manifest):
    base = datetime.datetime(2026, 7, 23, tzinfo=datetime.timezone.utc)
    decision = {"decision": "request_evidence", "repaired_concepts": None,
                "request": "need metadata", "report": "ok"}
    raw = json.dumps(decision, ensure_ascii=False)
    results = []
    for item in manifest["prompts"]:
        cap = copy.deepcopy(item["capture_template"])
        order = item["execution_order"]
        started = base + datetime.timedelta(seconds=2 * order)
        cap["execution"].update({
            "provider": "anthropic-workflow", "model": "claude-haiku-4-5",
            "started_at": started.isoformat(),
            "completed_at": (started + datetime.timedelta(seconds=1)).isoformat(),
            "context_id": f"wf-agent-{order:03d}", "temperature": None,
        })
        cap["raw_response"] = raw
        cap["output"] = decision
        cap["parse_error"] = None
        results.append(cap)
    return {
        "record_class": "empirical_trial_set",
        "protocol": {
            "experiment_id": "E2.2", "design_commit": DESIGN_COMMIT,
            "prompt_manifest_sha256": ev.manifest_content_sha256(manifest),
        },
        "results": results,
    }


def test_manifest_and_trialset_valid():
    fixtures = ev.load_fixtures()
    manifest = gen.build_manifest(DESIGN_COMMIT, generated_at=GENERATED_AT)
    assert manifest["n"] == 154
    errs, _ = ev.validate_manifest(manifest, fixtures)
    assert errs == [], errs
    trial_set = _valid_trial_set(manifest)
    assert ev.validate_trial_set(trial_set, fixtures, manifest) == []
    # tamper: a hash change must be caught
    bad = copy.deepcopy(trial_set)
    bad["protocol"]["prompt_manifest_sha256"] = "b" * 64
    assert ev.validate_trial_set(bad, fixtures, manifest)


def test_permutation_determinism():
    fixtures = ev.load_fixtures()
    rows = []
    for fx in fixtures.values():
        if fx["role"] != "risk":
            continue
        for arm in ("B", "C"):
            for trial in range(1, 6):
                y = 1 if (arm == "B" or trial <= 3) else 0
                rows.append({"fixture": fx["id"], "arm": arm, "trial": trial,
                             "topology": fx["topology"], "role": "risk",
                             "y": y, "safe_effective": bool(y)})
    p1 = ev.permutation_test(rows)["p_two_sided"]
    p2 = ev.permutation_test(rows)["p_two_sided"]
    assert p1 == p2  # deterministic seed


def main():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"\nALL GREEN ({len(tests)} tests)")


if __name__ == "__main__":
    main()
