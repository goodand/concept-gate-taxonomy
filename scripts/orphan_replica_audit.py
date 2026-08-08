#!/usr/bin/env python3
"""Is an orphan finding a real gap, or a replica whose canonical copy is
already linked from a different worktree?

WHY THIS EXISTS
---------------
`handoff_reachability.py` measures link reachability *inside one worktree's
graph*. It cannot see that the exact same file, byte-for-byte, also exists in
five other worktrees -- because each worktree registered with `git worktree
list` is a separate vault path with its own independent Obsidian backlink
count. A file can show 0 backlinks in worktree A while its byte-identical
twin in worktree B is linked from that worktree's README. Naively "fixing"
every 0-backlink copy by hand-editing five more READMEs is exactly the
anti-pattern `CLAUDE.md` names: "worktree 간 동명 파일... 손으로 복사하면
사본 두 벌, 한쪽만 수정, 거짓 통과"의 orphan 버전.

This tool answers the actual question: after collapsing byte-identical
replicas across every registered worktree to one canonical copy (using this
repo's already-adopted precedence order), how many *logical* documents are
still unreachable from anywhere?

WHAT IT REUSES, NOT REIMPLEMENTS
---------------------------------
`.vault-harness/vault-md-retrieval/` is a protected dirty worktree -- read
only, never modified here. Its replica-collapse logic is imported, not
copied:

- `vault_md_harness.discover_worktrees()` -- the exact lifecycle/dirty
  classification this repo already computes for retrieval.
- `vault_md_harness.safety_class()` -- P0/P1/P2/L0/N0 precedence input.
- `advanced_retrieval.collapse_replicas()` / `precedence()` -- the exact
  canonical-selection rule already used to rank search results.

This script only adds: a filename-pattern walk for a *class* of documents
(default: `DESIGN_REQUEST*.md` / `DESIGN_DECISION*.md`), and a live
`obsidian backlinks` check per canonical path (Obsidian IPC; falls back to
reporting `unknown` if the CLI is unavailable rather than assuming 0).

WHAT A GREEN RUN MEANS
-----------------------
Every logical document in the scanned family has at least one canonical copy
that is linked from somewhere in the vault. It does NOT mean every physical
replica is linked -- replicas are not supposed to be linked individually;
that is the entire point of collapsing them. It does NOT propagate a link
fix across worktrees -- per `CLAUDE.md`, the only sanctioned path for that is
commit -> merge/rebase, never hand-copying.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_ROOT = Path(__file__).resolve().parent.parent  # concept-gate-codex-mcp-wt
VAULT_ROOT = SCRIPT_ROOT.parent  # Project_in_progress
HARNESS_DIR = VAULT_ROOT / ".vault-harness" / "vault-md-retrieval"

if not HARNESS_DIR.is_dir():
    raise SystemExit(f"protected harness not found (read-only import target): {HARNESS_DIR}")
sys.path.insert(0, str(HARNESS_DIR))
import advanced_retrieval as ar  # noqa: E402
import vault_md_harness as vh  # noqa: E402

DEFAULT_PATTERNS = ("DESIGN_REQUEST*.md", "DESIGN_DECISION*.md")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_documents(worktrees: list, patterns: tuple[str, ...]) -> dict[str, dict]:
    """One entry per physical file, keyed by vault-relative path -- the same
    key shape `collapse_replicas` expects in its `documents` mapping."""
    documents: dict[str, dict] = {}
    for wt in worktrees:
        for pattern in patterns:
            for hit in wt.path.rglob(pattern):
                if not hit.is_file() or ".git" in hit.parts:
                    continue
                try:
                    rel_to_wt = hit.relative_to(wt.path).as_posix()
                    rel_to_vault = hit.relative_to(VAULT_ROOT).as_posix()
                except ValueError:
                    continue
                dirty_path = rel_to_wt in wt.dirty_paths
                sc = vh.safety_class(wt.lifecycle, rel_to_wt, dirty_path)
                documents[rel_to_vault] = {
                    "path": rel_to_vault,
                    "sha256": _sha256(hit),
                    "safety_class": sc,
                    "lifecycle": wt.lifecycle,
                    "worktree": wt.relative_path,
                }
    # `notes/` sits at the vault root and is not a registered git worktree,
    # so `discover_worktrees()` never sees it -- confirmed blind spot
    # (2026-08-08): `notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md` was a
    # byte-identical pre-import replica invisible to the worktree scan.
    # `safety_class()` already has a "notes" branch (-> N0, lowest
    # precedence) for exactly this source; it is never picked as canonical
    # over a worktree copy, so including it only adds coverage, never
    # changes an existing verdict.
    notes_dir = VAULT_ROOT / "notes"
    if notes_dir.is_dir():
        for pattern in patterns:
            for hit in notes_dir.rglob(pattern):
                if not hit.is_file() or ".git" in hit.parts:
                    continue
                rel_to_vault = hit.relative_to(VAULT_ROOT).as_posix()
                if rel_to_vault in documents:
                    continue
                documents[rel_to_vault] = {
                    "path": rel_to_vault,
                    "sha256": _sha256(hit),
                    "safety_class": vh.safety_class("notes", rel_to_vault, False),
                    "lifecycle": "notes",
                    "worktree": "notes",
                }
    return documents


def collapse(documents: dict[str, dict]) -> list[dict]:
    ranked = [(path, 0.0) for path in documents]
    return ar.collapse_replicas(ranked, documents, channel_ranks={})


def obsidian_backlink_count(vault_relative_path: str) -> int | None:
    """None means the Obsidian CLI/IPC was unavailable -- never silently
    treated as 0. Distinguishing 'no backlinks' from 'could not check' is
    the same discipline `PROVIDER_ADAPTERS.md` applies to provider errors."""
    proc = subprocess.run(
        ["obsidian", "backlinks", f"path={vault_relative_path}", "counts", "format=json"],
        capture_output=True, text=True, timeout=15, check=False,
    )
    text = (proc.stdout or "") + (proc.stderr or "")
    if "No backlinks found" in text:
        return 0
    if "not found" in text or "unable to find" in text.lower() or proc.returncode not in (0, 1):
        return None
    try:
        return len(json.loads(proc.stdout))
    except (json.JSONDecodeError, ValueError):
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pattern", action="append", default=None,
                    help="filename glob, repeatable (default: DESIGN_REQUEST*.md, "
                         "DESIGN_DECISION*.md)")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args()
    patterns = tuple(args.pattern) if args.pattern else DEFAULT_PATTERNS

    worktrees = vh.discover_worktrees(VAULT_ROOT)
    if not worktrees:
        print("no registered worktrees found", file=sys.stderr)
        return 2

    documents = scan_documents(worktrees, patterns)
    groups = collapse(documents)

    rows = []
    for group in groups:
        canonical = group["canonical_path"]
        backlinks = obsidian_backlink_count(canonical)
        rows.append({
            "canonical_path": canonical,
            "safety_class": group["safety_class"],
            "replica_count": len(group["replica_paths"]),
            "replica_paths": group["replica_paths"],
            "backlinks": backlinks,
            "status": (
                "unknown" if backlinks is None
                else "orphan" if backlinks == 0
                else "linked"
            ),
        })

    physical = len(documents)
    logical = len(rows)
    orphan_rows = [r for r in rows if r["status"] == "orphan"]
    unknown_rows = [r for r in rows if r["status"] == "unknown"]

    if args.json:
        print(json.dumps({
            "patterns": patterns, "physical_files": physical, "logical_documents": logical,
            "orphan_canonicals": len(orphan_rows), "unknown_status": len(unknown_rows),
            "rows": rows,
        }, indent=2, ensure_ascii=False))
    else:
        print(f"patterns           : {', '.join(patterns)}")
        print(f"physical files     : {physical}")
        print(f"logical documents  : {logical}  (after replica-collapse)")
        print(f"orphan canonicals  : {len(orphan_rows)}")
        print(f"unknown (no IPC)   : {len(unknown_rows)}")
        if orphan_rows:
            print("\nORPHAN canonical documents (real gaps -- no replica anywhere is linked):")
            for r in orphan_rows:
                print(f"  {r['canonical_path']}  [{r['safety_class']}]  "
                      f"({r['replica_count']} replica(s))")
        if unknown_rows:
            print("\nUNKNOWN status (Obsidian IPC unavailable -- not assumed 0):")
            for r in unknown_rows:
                print(f"  {r['canonical_path']}")

    return 1 if orphan_rows else 0


if __name__ == "__main__":
    raise SystemExit(main())
