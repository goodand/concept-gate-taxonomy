"""Stage 2 (E2E-v1-C) dispatch-plan builder.

Single-arm cohort dispatch builder with oracle isolation: LF and expected-IR
never reach the dispatch plan. This separation is enforced structurally
(never resolving lf at build time, never including lf_sha256 or
expected_ir_sha256 in trial records) and verified by the contract's leak test
(assertions on the plan's serialized form).

Pattern lineage from _h1a_cohort (freeze refusal, surface pinning, verbatim bytes)
without importing from it.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import NamedTuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1]))

from conceptgate.cg_fixture_resolver import resolve_bytes, _assert_commitment_entry_complete
from conceptgate.cg_ir_schema import formula_json_schema, V0_O1_CONSTRUCTORS


class CohortSpec(NamedTuple):
    """Cohort build configuration."""
    manifest_path: Path
    cohort_path: Path
    cache_dir: Path
    order_seed: str
    trial_id_prefix: str
    model: str


class MaterialUnavailable(Exception):
    """One or more fixture texts could not be resolved."""
    pass


class CohortOverwriteRefused(Exception):
    """Cohort file already exists; overwriting would destroy a preserved plan."""
    pass


def load_template() -> str:
    """Load the Stage 2 prompt template from stage2_prompt_template.md.

    Returns the ```template fenced block content only (stripped of fence lines).
    """
    template_file = HERE / "stage2_prompt_template.md"
    content = template_file.read_text(encoding="utf-8")

    lines = content.split("\n")
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if line.strip() == "```template":
            start_idx = i + 1
        elif start_idx is not None and line.strip() == "```":
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        raise ValueError("template block not found in stage2_prompt_template.md")

    return "\n".join(lines[start_idx:end_idx])


def build_cohort(spec: CohortSpec) -> dict:
    """Build the dispatch plan from a manifest.

    Pure function: no writes. Returns the plan dict ready for serialization.

    Raises:
        MaterialUnavailable: if any text fixture is unavailable or tampered.
        ValueError: if any manifest entry fails commitment validation.
    """
    # Load manifest
    manifest = json.loads(spec.manifest_path.read_text(encoding="utf-8"))
    entries = manifest["entries"]

    # Validate every entry and resolve texts
    resolved_texts = {}  # case_id -> text_bytes
    missing_case_ids = []

    for entry in entries:
        # Validate entry completeness
        _assert_commitment_entry_complete(entry)

        case_id = entry["case_id"]
        text_sha256 = entry["text_sha256"]

        # Resolve text only (NOT lf) — oracle isolation
        result = resolve_bytes(text_sha256, spec.cache_dir)
        if result["execution"] != "ok":
            missing_case_ids.append(case_id)
        else:
            resolved_texts[case_id] = result["data"]

    # All-or-nothing: fail if any text is unavailable
    if missing_case_ids:
        raise MaterialUnavailable(
            f"text not available for: {', '.join(sorted(missing_case_ids))}"
        )

    # Load template and schema
    template = load_template()
    schema = formula_json_schema()

    # Deterministic seeded order: sort by sha256(f"{order_seed}:{case_id}") hex
    entries_with_sort_keys = []
    for entry in entries:
        case_id = entry["case_id"]
        material = f"{spec.order_seed}:{case_id}"
        sort_key = hashlib.sha256(material.encode()).hexdigest()
        entries_with_sort_keys.append((sort_key, entry))

    # Sort by hash in reverse order (descending)
    entries_with_sort_keys.sort(key=lambda x: x[0], reverse=True)

    # Build trial records (1-based indexing after ordering)
    trials = []
    for i, (_, entry) in enumerate(entries_with_sort_keys, start=1):
        case_id = entry["case_id"]
        text_bytes = resolved_texts[case_id]
        text_str = text_bytes.decode("utf-8")

        # Render prompt: template with {sentence} replaced by text
        prompt = template.replace("{sentence}", text_str)

        trial_id = f"{spec.trial_id_prefix}-{i:02d}"
        trials.append({
            "trial_id": trial_id,
            "case_id": case_id,
            "text_sha256": entry["text_sha256"],
            "prompt": prompt,
        })

    # Pin subject definition and assert tools constraint
    subject_definition_path = Path.home() / ".claude" / "agents" / "o1-compiler.md"
    subject_definition_raw = subject_definition_path.read_text(encoding="utf-8")

    # Assert preregistered subject constraint: no tools
    if "tools: []" not in subject_definition_raw:
        raise ValueError(
            f"{subject_definition_path}: preregistered subject must have "
            f"'tools: []' in frontmatter"
        )

    subject_definition_sha256 = hashlib.sha256(
        subject_definition_raw.encode()
    ).hexdigest()

    # Build plan provenance
    template_sha256 = hashlib.sha256(template.encode()).hexdigest()
    schema_sha256 = hashlib.sha256(
        json.dumps(schema, sort_keys=True, ensure_ascii=False).encode()
    ).hexdigest()

    plan = {
        "cohort_version": spec.order_seed,
        "provenance": {
            "trial_subject": {
                "name": "o1-compiler",
                "definition_path": str(subject_definition_path),
                "definition_sha256": subject_definition_sha256,
            },
            "output_schema": schema,
            "output_schema_sha256": schema_sha256,
            "constructor_profile": list(V0_O1_CONSTRUCTORS),
            "prompt_template_sha256": template_sha256,
            "model": spec.model,
        },
        "trials": trials,
    }

    return plan


def write_cohort(spec: CohortSpec) -> dict:
    """Build and write the cohort manifest.

    Fails closed: refuses to overwrite an existing manifest (which could
    destroy a preserved plan). A different cohort needs its own spec.

    Raises:
        CohortOverwriteRefused: if the manifest already exists.
    """
    if spec.cohort_path.exists():
        raise CohortOverwriteRefused(
            f"{spec.cohort_path.name} already exists and holds a frozen "
            f"manifest. Overwriting would destroy it irreversibly.\n\n"
            f"A different cohort needs its own CohortSpec with a distinct "
            f"cohort_path, order_seed, and trial_id_prefix. Do not delete "
            f"this check to proceed."
        )

    plan = build_cohort(spec)
    spec.cohort_path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )
    return plan
