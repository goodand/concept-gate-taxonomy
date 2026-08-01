"""H1a-only frozen copy of E2.4's surface pipeline.

D-H1a-1 (= B) forbids retroactively changing E2.4's frozen implementation, so
H1a carries its own copy rather than editing or importing the original. Load
it under a unique sys.modules key -- this repo has already had one experiment
silently execute another's module (E2.4_ISSUE_REGISTER [DONE] #6).

THERE ARE TWO INTENDED DEVIATIONS from E2.4's _surface.py, and both are
enumerated in test_h1a_fixture.py::DOCUMENTED_DEVIATIONS.
test_h1a_surface_deviates_from_e2_4_only_where_documented pins that claim by
comparing every other constant and function body against the original, so an
undocumented edit fails loudly instead of drifting. A second, bidirectional
test (test_h1a_surface_has_no_undocumented_additions) walks the H1a module's
own names to catch additions that exist only on this side and were never
compared at all -- the first test alone only notices things E2.4 has that
this copy lost or changed, not things this copy gained.

1. The eligibility profile for `docs/` prose, which E2.4 does not need and
   therefore rejects outright. H1a's whole subject matter is a
   documentation-vs-code conflict, so without it `qualify_fixture` raises
   before any fixture can exist. The profile name is deliberately neutral
   (`repository_prose`, not `stale_documentation`) -- profile names never
   reach the model payload (measured; this is why the draft's "leak dilemma"
   was refuted), but a name asserting staleness would still be the harness
   recording a judgment it has no standing to make, and H1a exists precisely
   because that judgment is the open question. The profile also excludes
   this experiment's own self-referential paths (docs/feedback/ and named
   meta-docs about H1a itself) -- those describe the fixture's own
   conflict and would be a second, structural leak route if ever cited as
   evidence.

2. MODEL_PAYLOAD_KEYS / build_model_payload no longer forward
   `server_response`. Independent review 20260730 finding #11: the code
   side's server_response.status=PASS structurally authenticated the code
   side's answer (flip the recorded type, status flips to
   NEEDS_CORRECTION) -- a structural oracle leak, not a vocabulary one, so
   the fix is removing the key rather than scanning its contents.
   server_response is retained in the fixture itself (see
   test_server_response_is_reproducible) so the fixture stays honest about
   what the repo actually certifies; it simply never reaches
   build_model_payload's return value.

--- original E2.4 docstring follows ---

Canonical surface pipeline for E2.4.

Implements DESIGN_DECISION_surface_separation.md: three surfaces with separate
schemas and paths, and liveness verification moved outside the model boundary.

    fixture -> validate_fixture -> qualify_fixture -> build_model_payload
            -> render_prompt -> trial_manifest

Why the schema lives in code rather than in another .json file
--------------------------------------------------------------
The defect this module retires was an *unenforced intent*: the old
`evidence_packet_schema.json` said, in its own description, "hidden oracle
fields must not be included in model prompts" -- and nothing ever checked it,
so all four fixtures leaked judgment information to the model for weeks.
Shipping another declarative schema document that no validator executes would
reproduce exactly that failure. The structures below ARE the schema and the
checks below ARE the enforcement, so the two cannot drift. The human-readable
rendering lives in DESIGN_DECISION_surface_separation.md §1-2.

`build_model_payload` constructs its output field by field. It never copies the
fixture and deletes keys: under a blacklist projection every field added later
ships to the model by default, which is precisely how the leak happened (the
smoke payloads were hand-built as
`{k: v for k, v in fixture.items() if k != 'run_pipeline_input'}`).

Stdlib only.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

FIXTURE_VERSION = "repo_evidence_fixture_v2"
QUALIFICATION_VERSION = "e2.4-source-qualification-v1"

FIXTURE_KEYS = {
    "fixture_version",
    "experiment_id",
    "repo",
    "source_commit",
    "run_pipeline_input",
    "candidate_concepts",
    "evidence_sources",
    "server_response",
    "builder_metadata",
}
EVIDENCE_SOURCE_KEYS = {
    "evidence_id",
    "source_kind",
    "source_ref",
    "text",
    "text_sha256",
}
SOURCE_KINDS = {"code", "doc", "test", "fixture", "commit_message"}

# Tagged union. The key set is matched exactly, which is what leaves no room
# for a note/description/rationale field to reappear.
SOURCE_REF_SHAPES = {
    "file_lines": {"path", "start_line", "end_line"},
    "symbol": {"path", "symbol"},
    "test": {"path", "node_id"},
    "commit": {"sha", "part"},
    "json_pointer": {"path", "pointer"},
}

ELIGIBILITY_PROFILES = {
    "current_executable_source",
    "verified_by_passing_test",
    "frozen_experiment_artifact",
    "historical_commit_record",
    "repository_prose",  # H1a deviation -- see module docstring
}

FEATURE_TYPES = {
    "essential_feature",
    "contextual_usage",
    "locational",
    "functional",
    "social_treatment",
    "structural_composition",
}

# --- the model-facing surface, enumerated ---
# H1a deviation #2: no server_response -- see module docstring.
MODEL_PAYLOAD_KEYS = ("candidate_concepts", "evidence_items")
MODEL_EVIDENCE_KEYS = ("evidence_id", "source_kind", "text")
MODEL_CONCEPT_KEYS = ("name", "features")
MODEL_FEATURE_KEYS = ("feature", "type", "evidence_refs")
MODEL_SERVER_RESPONSE_KEYS = ("status", "dag", "composition_issues", "anti_patterns")

_SHA1_FULL = re.compile(r"^[0-9a-f]{40}$")


class SurfaceError(Exception):
    """Raised when a surface invariant is violated. Never warn-and-continue."""


# --------------------------------------------------------------------------
# canonical serialization / hashing
# --------------------------------------------------------------------------

def canonical_json(obj) -> str:
    """Stable serialization. Hashes must not move because a key order did."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_of(obj) -> str:
    payload = obj if isinstance(obj, str) else canonical_json(obj)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------
# A. builder fixture
# --------------------------------------------------------------------------

def _check_source_ref(ref, where: str) -> None:
    if not isinstance(ref, dict):
        raise SurfaceError(f"{where}: source_ref must be an object")
    kind = ref.get("kind")
    if kind not in SOURCE_REF_SHAPES:
        raise SurfaceError(
            f"{where}: source_ref.kind must be one of "
            f"{sorted(SOURCE_REF_SHAPES)}, got {kind!r}"
        )
    expected = {"kind"} | SOURCE_REF_SHAPES[kind]
    if set(ref) != expected:
        extra = sorted(set(ref) - expected)
        missing = sorted(expected - set(ref))
        raise SurfaceError(
            f"{where}: source_ref[{kind}] key mismatch; "
            f"unexpected={extra} missing={missing}"
        )

    if "path" in ref:
        path = ref["path"]
        if not isinstance(path, str) or not path:
            raise SurfaceError(f"{where}: path must be a non-empty string")
        if path.startswith("/") or ".." in Path(path).parts:
            raise SurfaceError(f"{where}: path must be repo-relative, got {path!r}")
    if kind == "file_lines":
        start, end = ref["start_line"], ref["end_line"]
        if not isinstance(start, int) or not isinstance(end, int):
            raise SurfaceError(f"{where}: line numbers must be integers")
        if start < 1 or end < start:
            raise SurfaceError(f"{where}: require 1 <= start_line <= end_line")
    if kind == "commit":
        if not isinstance(ref["sha"], str) or not _SHA1_FULL.match(ref["sha"]):
            raise SurfaceError(f"{where}: commit sha must be a 40-char full sha")
        if ref["part"] not in {"subject", "body"}:
            raise SurfaceError(f"{where}: commit part must be 'subject' or 'body'")
    if kind == "json_pointer":
        pointer = ref["pointer"]
        if not isinstance(pointer, str) or (pointer and not pointer.startswith("/")):
            raise SurfaceError(f"{where}: pointer must be RFC 6901 JSON Pointer")


def validate_fixture(fixture) -> None:
    if not isinstance(fixture, dict):
        raise SurfaceError("fixture must be an object")
    if set(fixture) != FIXTURE_KEYS:
        extra = sorted(set(fixture) - FIXTURE_KEYS)
        missing = sorted(FIXTURE_KEYS - set(fixture))
        raise SurfaceError(f"fixture key mismatch; unexpected={extra} missing={missing}")
    if fixture["fixture_version"] != FIXTURE_VERSION:
        raise SurfaceError(f"fixture_version must be {FIXTURE_VERSION!r}")
    if not _SHA1_FULL.match(str(fixture["source_commit"])):
        raise SurfaceError("source_commit must be a 40-char full sha")

    seen: set[str] = set()
    for item in fixture["evidence_sources"]:
        where = f"evidence_sources[{item.get('evidence_id', '?')}]"
        if set(item) != EVIDENCE_SOURCE_KEYS:
            extra = sorted(set(item) - EVIDENCE_SOURCE_KEYS)
            missing = sorted(EVIDENCE_SOURCE_KEYS - set(item))
            raise SurfaceError(f"{where}: key mismatch; unexpected={extra} missing={missing}")
        if item["evidence_id"] in seen:
            raise SurfaceError(f"{where}: duplicate evidence_id")
        seen.add(item["evidence_id"])
        if item["source_kind"] not in SOURCE_KINDS:
            raise SurfaceError(f"{where}: source_kind must be one of {sorted(SOURCE_KINDS)}")
        if sha256_of(item["text"]) != item["text_sha256"]:
            raise SurfaceError(f"{where}: text_sha256 does not match text")
        _check_source_ref(item["source_ref"], where)

    for concept in fixture["candidate_concepts"]:
        for feature in concept["features"]:
            if feature["type"] not in FEATURE_TYPES:
                raise SurfaceError(
                    f"{concept['name']}.{feature['feature']}: unknown type {feature['type']!r}"
                )
            unknown = set(feature["evidence_refs"]) - seen
            if unknown:
                raise SurfaceError(
                    f"{concept['name']}.{feature['feature']}: "
                    f"evidence_refs not in evidence_sources: {sorted(unknown)}"
                )


# --------------------------------------------------------------------------
# B. qualification -- provenance and eligibility, outside the model boundary
# --------------------------------------------------------------------------

def _resolve_pointer(doc, pointer: str):
    node = doc
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        node = node[int(token)] if isinstance(node, list) else node[token]
    return node


def _excerpt_matches(ref: dict, text: str, repo_root: Path) -> bool:
    kind = ref["kind"]
    if kind == "commit":
        fmt = "%s" if ref["part"] == "subject" else "%B"
        proc = subprocess.run(
            ["git", "show", "-s", f"--format={fmt}", ref["sha"]],
            cwd=str(repo_root), capture_output=True, text=True,
        )
        return proc.returncode == 0 and text in proc.stdout

    target = repo_root / ref["path"]
    if not target.exists():
        return False

    if kind == "file_lines":
        lines = target.read_text(encoding="utf-8").split("\n")
        excerpt = "\n".join(lines[ref["start_line"] - 1 : ref["end_line"]])
        return excerpt == text
    if kind == "json_pointer":
        return _resolve_pointer(json.loads(target.read_text(encoding="utf-8")),
                               ref["pointer"]) == text
    # symbol / test: the excerpt must appear verbatim AND the named symbol must
    # exist, so a stale symbol name is caught even when the text still matches.
    body = target.read_text(encoding="utf-8")
    name = ref["symbol"] if kind == "symbol" else ref["node_id"].split("::")[-1]
    return text in body and re.search(rf"^\s*(def|class)\s+{re.escape(name)}\b",
                                      body, re.MULTILINE) is not None


# H1a deviation #1 continued: docs/ paths that describe H1a's own conflict
# are not eligible evidence -- citing them would let the fixture's own
# analysis (which names a "correct" side) leak in as if it were ordinary
# repository prose. This is a denylist, not a vocabulary scan: it blocks the
# known self-referential locations outright rather than trying to detect
# "talks about H1a" from content.
_SELF_REFERENTIAL_DOC_PREFIXES = ("docs/feedback/",)
_SELF_REFERENTIAL_DOC_NAMES = {
    "docs/HANDOFF.md",
    "docs/E2.4_ISSUE_REGISTER.md",
    "docs/H1A_ISSUE_REGISTER.md",
    "docs/HARNESS_KNOWHOW.md",
}


def _eligibility_profile(ref: dict, source_kind: str) -> str:
    """Deterministic, from location alone -- never a builder's assertion."""
    if ref["kind"] == "commit" or source_kind == "commit_message":
        return "historical_commit_record"
    if ref["kind"] == "test":
        return "verified_by_passing_test"
    path = ref["path"]
    if path.startswith("experiments/"):
        return "frozen_experiment_artifact"
    if path.startswith("conceptgate/"):
        return "current_executable_source"
    if path.startswith("docs/"):
        if path.startswith(_SELF_REFERENTIAL_DOC_PREFIXES) or path in _SELF_REFERENTIAL_DOC_NAMES:
            raise SurfaceError(
                f"{path}: self-referential to this experiment's own analysis, "
                f"not eligible as evidence about the repository under study."
            )
        return "repository_prose"
    raise SurfaceError(
        f"{path}: no eligibility profile applies. Sources must be live package "
        f"code, a test, a frozen experiment artifact, or a commit record."
    )


def _test_passes(ref: dict, repo_root: Path) -> bool:
    proc = subprocess.run(
        ["python3", "-m", "pytest", "-q", f"{ref['path']}::{ref['node_id'].split('::')[-1]}"],
        cwd=str(repo_root), capture_output=True, text=True,
    )
    return proc.returncode == 0


def qualify_fixture(fixture, repo_root, run_tests: bool = True) -> dict:
    """Verify every source resolves and matches, before any model sees it.

    Liveness is settled here precisely so the model never has to take a
    builder's word for it (DESIGN_DECISION §4).
    """
    validate_fixture(fixture)
    repo_root = Path(repo_root)

    checks = []
    for item in fixture["evidence_sources"]:
        ref = item["source_ref"]
        profile = _eligibility_profile(ref, item["source_kind"])
        resolved = _excerpt_matches(ref, item["text"], repo_root)
        refs: list[str] = []
        if profile == "verified_by_passing_test" and resolved:
            if run_tests and not _test_passes(ref, repo_root):
                raise SurfaceError(
                    f"{item['evidence_id']}: cited test {ref['node_id']} does not pass"
                )
            refs.append(ref["node_id"] if run_tests else f"{ref['node_id']} (not run)")
        checks.append({
            "evidence_id": item["evidence_id"],
            "locator_resolved": resolved,
            "excerpt_exact_match": resolved,
            "text_sha256_verified": sha256_of(item["text"]) == item["text_sha256"],
            "eligibility_profile": profile,
            "verification_refs": refs,
        })

    passed = all(
        c["locator_resolved"] and c["excerpt_exact_match"] and c["text_sha256_verified"]
        for c in checks
    )
    return {
        "qualification_version": QUALIFICATION_VERSION,
        "fixture_sha256": sha256_of(fixture),
        "source_commit": fixture["source_commit"],
        "status": "passed" if passed else "failed",
        "evidence_checks": checks,
    }


# --------------------------------------------------------------------------
# C. model payload -- whitelist construction, the only way to reach a prompt
# --------------------------------------------------------------------------

def build_model_payload(fixture, qualification_manifest) -> dict:
    manifest = qualification_manifest
    if manifest.get("qualification_version") != QUALIFICATION_VERSION:
        raise SurfaceError("qualification manifest version mismatch")
    if manifest.get("status") != "passed":
        raise SurfaceError(f"qualification status is {manifest.get('status')!r}, not 'passed'")
    if manifest.get("fixture_sha256") != sha256_of(fixture):
        raise SurfaceError(
            "fixture changed after qualification (sha256 mismatch); re-qualify before building"
        )
    validate_fixture(fixture)

    return {
        "candidate_concepts": [
            {
                "name": concept["name"],
                "features": [
                    {
                        "feature": feature["feature"],
                        "type": feature["type"],
                        "evidence_refs": list(feature["evidence_refs"]),
                    }
                    for feature in concept["features"]
                ],
            }
            for concept in fixture["candidate_concepts"]
        ],
        "evidence_items": [
            {
                "evidence_id": item["evidence_id"],
                "source_kind": item["source_kind"],
                "text": item["text"],
            }
            for item in fixture["evidence_sources"]
        ],
    }


def load_contract_prompt(path) -> str:
    """Return the fenced prompt block from contract_prompt.md."""
    text = Path(path).read_text(encoding="utf-8")
    blocks = re.findall(r"^```\n(.*?)^```", text, re.DOTALL | re.MULTILINE)
    if not blocks:
        raise SurfaceError(f"{path}: no fenced prompt block found")
    return blocks[0]


def render_prompt(contract_prompt: str, model_payload: dict) -> str:
    if "{payload_json}" not in contract_prompt:
        raise SurfaceError("contract prompt has no {payload_json} placeholder")
    return contract_prompt.replace(
        "{payload_json}", json.dumps(model_payload, ensure_ascii=False)
    )


def trial_manifest(*, trial_id, fixture, qualification_manifest, model_payload,
                   contract_prompt, rendered_prompt, decision_schema,
                   builder_commit, model, parameters=None) -> dict:
    """Pins the whole surface the model saw -- contract wording included.

    rendered_prompt_sha256 is the load-bearing value: payload hashes alone
    would not notice a change in the contract text wrapped around them.
    """
    return {
        "trial_id": trial_id,
        "fixture_sha256": sha256_of(fixture),
        "qualification_sha256": sha256_of(qualification_manifest),
        "payload_sha256": sha256_of(model_payload),
        "contract_prompt_sha256": sha256_of(contract_prompt),
        "rendered_prompt_sha256": sha256_of(rendered_prompt),
        "decision_schema_sha256": sha256_of(decision_schema),
        "builder_commit": builder_commit,
        "model": model,
        "parameters": parameters or {},
    }
