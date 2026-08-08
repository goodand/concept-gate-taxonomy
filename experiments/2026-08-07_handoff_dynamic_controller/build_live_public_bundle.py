#!/usr/bin/env python3
"""Build a physically isolated public-only bundle for one live subject run.

The subject receives only ``subject/``. The host-owned retrieval server reads
``control/corpus`` through an in-memory ``Corpus`` instance. A Seatbelt profile
denies the subject access to ``control`` and the source repository, so every
source exposure must pass through ``live_subject_tool.py`` and is logged by the
host rather than self-reported by the model.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from _contract import find_forbidden_key, validate_case  # noqa: E402

PUBLIC_FILES = (
    "live_subject_tool.py",
    "live_subject_response.schema.json",
    "retrieval_subagent_response.schema.json",
)
ALLOWED_VARIANTS = ("variant-L", "variant-M")


class BundleError(RuntimeError):
    """The public bundle cannot be proven isolated and immutable."""


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_case(case_id: str) -> dict:
    cases = json.loads((HERE / "public_cases" / "cases.json").read_text(
        encoding="utf-8"))
    try:
        case = next(case for case in cases if case.get("id") == case_id)
    except StopIteration as exc:
        raise BundleError(f"unknown public case: {case_id}") from exc
    return validate_case(case)


def _assert_safe_destination(output: Path) -> None:
    resolved = output.resolve()
    project_root = HERE.parents[2]
    if resolved == project_root or project_root in resolved.parents:
        raise BundleError("live bundles must be outside Project_in_progress")
    if output.exists() and any(output.iterdir()):
        raise BundleError(f"bundle destination is not empty: {output}")


def _copy_regular_file(source: Path, destination: Path) -> None:
    if source.is_symlink() or not source.is_file():
        raise BundleError(f"public input is not a regular file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def _manifest_entries(root: Path) -> dict[str, str]:
    entries: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise BundleError(f"bundle contains a symlink: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative.startswith("subject/run/") or relative == "control/input_manifest.json":
                continue
            entries[relative] = sha256(path)
    return entries


def build_bundle(output: Path, variant: str, case_id: str) -> dict:
    """Build one bundle and return the host-retained expected manifest."""
    if variant not in ALLOWED_VARIANTS:
        raise BundleError(f"unsupported corpus variant: {variant}")
    _assert_safe_destination(output)
    output.mkdir(parents=True, exist_ok=True)
    subject = output / "subject"
    control = output / "control"
    subject.mkdir()
    control.mkdir()

    case = _load_case(case_id)
    if find_forbidden_key(case):
        raise BundleError("public case contains an evaluator-only key")
    (subject / "task.json").write_text(
        json.dumps(case, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    for name in PUBLIC_FILES:
        _copy_regular_file(HERE / name, subject / name)

    source_corpus = HERE / "public_corpus" / variant
    for source in sorted(source_corpus.rglob("*")):
        if source.is_symlink():
            raise BundleError(f"corpus contains a symlink: {source}")
        if source.is_file():
            if source.suffix.lower() != ".md":
                raise BundleError(f"corpus contains a non-Markdown file: {source}")
            _copy_regular_file(source, control / "corpus" / source.relative_to(source_corpus))

    manifest = {
        "contract_version": "handoff-dyn-public-bundle-v1",
        "case_id": case_id,
        "variant": variant,
        "subject_visible_root": "subject",
        "host_only_root": "control",
        "files": _manifest_entries(output),
    }
    (control / "input_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    verify_bundle(output, manifest)
    return manifest


def verify_bundle(output: Path, expected: dict) -> None:
    """Fail if immutable inputs changed, disappeared, or were introduced."""
    actual = _manifest_entries(output)
    if actual != expected.get("files"):
        changed = sorted(
            key for key in set(actual) | set(expected.get("files", {}))
            if actual.get(key) != expected.get("files", {}).get(key)
        )
        raise BundleError(f"bundle input drift: {changed}")
    task = json.loads((output / "subject" / "task.json").read_text(encoding="utf-8"))
    validate_case(task)
    if find_forbidden_key(task):
        raise BundleError("public task leaks an evaluator-only key")
    for path in output.rglob("*"):
        if path.is_symlink():
            raise BundleError(f"bundle gained a symlink: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--variant", choices=ALLOWED_VARIANTS, required=True)
    parser.add_argument("--case-id", required=True)
    args = parser.parse_args()
    try:
        manifest = build_bundle(args.output, args.variant, args.case_id)
    except (BundleError, ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"bundle build failed: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
