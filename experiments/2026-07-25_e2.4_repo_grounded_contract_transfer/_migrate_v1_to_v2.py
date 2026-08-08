#!/usr/bin/env python3
"""One-off migration: repo_evidence_packet (v1) -> repo_evidence_fixture_v2.

Run once, from this directory:  python3 _migrate_v1_to_v2.py

What moves where (DESIGN_DECISION_surface_separation.md §8):

  extraction_note   -> builder_metadata.evidence_notes[evidence_id]   (hidden)
  source_path+locator -> source_ref tagged union                      (hidden)
  fixture class/oracle -> oracle_manifest.json                        (hidden)
  extraction_policy -> dropped; source restriction lives in the frozen
                       contract_prompt.md, not in fixture data

The source_ref mappings below are *claims* about where each excerpt lives. They
are not trusted: the script runs qualify_fixture, which resolves every ref
against the working tree and compares the excerpt byte for byte, and refuses to
write anything unless every fixture qualifies. A wrong line range fails here
rather than silently shipping.

Kept deliberately as a committed artifact rather than run and deleted, so the
v1 -> v2 transformation is auditable later.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent

spec = importlib.util.spec_from_file_location("e24_surface", HERE / "_surface.py")
surface = importlib.util.module_from_spec(spec)
sys.modules["e24_surface"] = surface
spec.loader.exec_module(surface)

FIXTURE_JSON_POINTER = "/fixtures/0/input_concepts/0/features/0/evidence"

# evidence_id -> source_ref. Verified by qualification, not by assertion.
SOURCE_REFS = {
    "ev1": {
        "kind": "json_pointer",
        "path": "experiments/2026-07-24_e2.2.1_directed_pc_vocabulary_fix/fixture.json",
        "pointer": FIXTURE_JSON_POINTER,
    },
    "ev4": {
        "kind": "file_lines",
        "path": "conceptgate/concept_gate_v7.py",
        "start_line": 556,
        "end_line": 560,
    },
    "ev5": {
        "kind": "commit",
        "sha": "4017aff822b7d24cdc85f6c94fbdf3a640eaee0f",
        "part": "body",
    },
    "ev6": {
        "kind": "commit",
        "sha": "559f61f4d9ba2db9394cbc999b35f0b257f60b83",
        "part": "body",
    },
    "ev9": {
        "kind": "file_lines",
        "path": "conceptgate/server.py",
        "start_line": 380,
        "end_line": 382,
    },
    "ev10": {
        "kind": "json_pointer",
        "path": "experiments/2026-07-25_e2.3_global_invariant_generalization/fixture.json",
        "pointer": FIXTURE_JSON_POINTER,
    },
}

# Opaque ids. Class names must not travel with the run: an operator who can see
# "sufficient_repairable" in a filename or a log line while assembling a prompt
# is one slip away from the leak this redesign exists to prevent.
OPAQUE_IDS = {
    "fixture_sufficient_consistent.json": "E24-F-01",
    "fixture_sufficient_repairable.json": "E24-F-02",
    "fixture_insufficient.json": "E24-F-03",
    "fixture_conflicting.json": "E24-F-04",
}

ORACLES = {
    "E24-F-01": {"semantic_class": "sufficient_consistent",
                 "expected_decision": "accept_report",
                 "expected_contract_verdict": "sufficient_consistent"},
    "E24-F-02": {"semantic_class": "sufficient_repairable",
                 "expected_decision": "repair",
                 "expected_contract_verdict": "sufficient_repairable"},
    "E24-F-03": {"semantic_class": "insufficient",
                 "expected_decision": "abstain",
                 "expected_contract_verdict": "insufficient_evidence"},
    # status string is the one the 2026-07-29 operations directive prescribes
    # ("fixture_unavailable_unverified"). It replaced an equivalent local
    # coinage ("no_eligible_fixture") -- same meaning, but the directive's
    # vocabulary is the one other sessions will grep for.
    "E24-F-04": {"semantic_class": "conflicting",
                 "expected_decision": "abstain",
                 "expected_contract_verdict": "conflicting_evidence",
                 "status": "fixture_unavailable_unverified",
                 "note": "Closed as unobtainable from live, equal-strength evidence "
                         "in this repo (PROBLEM_2_conflicting.md §5.2). Excluded from "
                         "the rerun cohort; the schema class is retained."},
}

# ev6's note asserted "one commit later than ev5". git log 4017aff..559f61f
# shows three, and the intervening ce3699a records that ev5's attribution had
# already been measured NO_GO -- an error that ran in the direction that
# affects the equal-strength judgment. Corrected here per §8.
NOTE_CORRECTIONS = {
    "ev6": (
        "E2.2.2's design commit message. States that root-cause analysis of "
        "E2.2.1's trial reports found the real gap was two unstated structural "
        "contracts, not vocabulary, addressing the same referent as ev5 and "
        "reaching the opposite attribution. PROVENANCE CORRECTION (2026-07-28): "
        "an earlier version of this note said 'one commit later than ev5'. That "
        "is wrong -- git log 4017aff..559f61f shows three commits, with ce3699a "
        "('record 20-trial results -- NO_GO, rate=0.15') and d706152 in between. "
        "ce3699a matters: ev5's attribution had already been measured as failing "
        "before ev6 was written, which bears directly on whether the two are of "
        "equal strength."
    ),
}


def head_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(REPO_ROOT),
        capture_output=True, text=True,
    ).stdout.strip()


def migrate(v1: dict, source_commit: str) -> dict:
    notes = {}
    sources = []
    for item in v1["evidence_items"]:
        eid = item["evidence_id"]
        if eid not in SOURCE_REFS:
            raise SystemExit(f"no source_ref mapping for {eid}")
        notes[eid] = NOTE_CORRECTIONS.get(eid, item["extraction_note"])
        sources.append({
            "evidence_id": eid,
            "source_kind": item["source_kind"],
            "source_ref": SOURCE_REFS[eid],
            "text": item["text"],
            "text_sha256": item["text_sha256"],
        })

    return {
        "fixture_version": surface.FIXTURE_VERSION,
        "experiment_id": v1["experiment_id"],
        "repo": v1["repo"],
        "source_commit": source_commit,
        "run_pipeline_input": v1["run_pipeline_input"],
        "candidate_concepts": v1["candidate_concepts"],
        "evidence_sources": sources,
        "server_response": v1["server_response"],
        "builder_metadata": {
            "evidence_notes": notes,
            "change_history": [
                {
                    "date": "2026-07-28",
                    "change": "migrated from repo_evidence_packet v1",
                    "detail": "extraction_note moved out of the model-facing surface "
                              "into builder_metadata; source_path+locator replaced by "
                              "a source_ref tagged union; extraction_policy dropped "
                              "(source restriction now lives in contract_prompt.md).",
                }
            ],
        },
    }


def main() -> int:
    source_commit = head_sha()
    migrated: dict[str, dict] = {}

    for filename in sorted(OPAQUE_IDS):
        path = HERE / filename
        v1 = json.loads(path.read_text(encoding="utf-8"))
        v2 = migrate(v1, source_commit)

        manifest = surface.qualify_fixture(v2, REPO_ROOT, run_tests=True)
        if manifest["status"] != "passed":
            for check in manifest["evidence_checks"]:
                if not all((check["locator_resolved"], check["excerpt_exact_match"],
                            check["text_sha256_verified"])):
                    print(f"  FAIL {filename} {check['evidence_id']}: {check}")
            raise SystemExit(f"{filename}: qualification failed; not writing anything")

        profiles = {c["evidence_id"]: c["eligibility_profile"]
                    for c in manifest["evidence_checks"]}
        print(f"  ok  {filename} -> {OPAQUE_IDS[filename]}  {profiles}")
        migrated[filename] = v2

    # Only write once every fixture has qualified.
    for filename, v2 in migrated.items():
        (HERE / filename).write_text(
            json.dumps(v2, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    (HERE / "oracle_manifest.json").write_text(
        json.dumps(
            {
                "experiment_id": "E2.4",
                "note": "Hidden oracle. Never part of any model payload; the "
                        "canonical builder cannot reach this file.",
                "fixtures": {
                    OPAQUE_IDS[name]: {"file": name, **ORACLES[OPAQUE_IDS[name]]}
                    for name in sorted(OPAQUE_IDS)
                },
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"\n  wrote {len(migrated)} fixtures + oracle_manifest.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
