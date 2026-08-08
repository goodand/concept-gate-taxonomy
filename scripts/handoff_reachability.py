#!/usr/bin/env python3
"""Can a cold-start session reach everything this session changed?

WHY THIS EXISTS
---------------
`HANDOFF_REUSE_VALIDATION.md` (portable standard, in `.vault-harness/`) asks
whether an agent with no prior context can find the sources, read the context,
and reconstruct a safe next action. Most of that standard needs a subject agent
and a hand-built gold set. **One part does not**: whether the files a session
actually touched are reachable from the handoff entry point at all. That part
is graph reachability over markdown links, and it is fully deterministic.

This tool measures only that part, and says so. A pass here does NOT mean the
handoff is good -- it means nothing the session changed is *structurally
unreachable*. The interpretive half of the standard is still manual.

WHAT IT CATCHES, WITH REAL EXAMPLES FROM THIS REPO
--------------------------------------------------
ORPHAN -- a file the session changed that no reachable document mentions.
  Observed 2026-08-06: an independent reviewer found that
  `PREREGISTRATION_REPAIRED_COHORT.md` contained zero references to the
  preregistration that superseded it, so a reader starting there could not
  reach the governing document. That is an orphan edge in this exact sense,
  and it was found by a human-instructed reviewer rather than by any check.

DANGLING -- a reachable document links to a path that does not exist.
  Same class as the defect filed as Q13: a sentence that names a governing
  clause which is absent. Prose-level dangling references need semantics, but
  the *link*-level ones are mechanical, so catch those here for free.

WHAT IT DELIBERATELY DOES NOT DO
--------------------------------
- It does not judge whether the handoff text is *understandable*. Reachable
  and useful are different propositions (patterns 8/10: state which one you
  are proving).
- It does not run a subject agent. `HANDOFF_REUSE_VALIDATION.md` sec 11's
  contract needs one; this is the pre-check that makes that run worth doing.
- It does not read `vault_search`. Search recall is a separate measurement
  with its own harness; link reachability is the floor beneath it.

Both directions of this auditor are pinned in `test_handoff_reachability.py`
at the repo root -- recall (a broken link IS reported) and precision (a broken
*mention* is NOT), the latter being the class that made the first run useless.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ENTRY = "docs/HANDOFF.md"

# Markdown link/target forms that actually appear in this repo's docs:
#   [text](path.md)              standard link
#   [[wiki/style/path]]          obsidian wikilink
#   `path/to/file.py`            inline code naming a file
# TWO KINDS OF EDGE, deliberately separated after the first run reported 404
# "dangling" findings that were almost all prose.
#
# LINKS are promises: `[text](path)` and `[[wikilink]]` assert the target
# exists, so a broken one is a real defect worth reporting.
#
# MENTIONS are `inline code` naming a file. They still make the file reachable
# -- a session reading "see `_h1a_policy.py`" can find it -- but a mention of a
# filename in prose is not a promise that a path resolves from THIS directory.
# Reporting those as dangling produced 404 findings on first run, nearly all
# false: bare filenames, globs (`experiments/*/test_protocol.py`), and paths
# relative to a different worktree. A checker whose findings are mostly noise
# gets ignored wholesale, which is worse than not having it (the tripwire
# precision lesson recorded in NEXT_SESSION_TRAPS sec 3.2).
_LINK_PATTERNS = (
    re.compile(r"\[[^\]]*\]\(([^)#]+)"),      # markdown link, strip anchor
    re.compile(r"\[\[([^\]|#]+)"),            # wikilink, strip alias/anchor
)
_MENTION_PATTERN = re.compile(r"`([^`\s]+\.(?:md|py|json|js|txt))`")

SKIP_PARTS = {".git", "venv", ".venv", "node_modules", "__pycache__", "vendor"}


def _skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def _clean(raw: str) -> str | None:
    target = raw.strip()
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None
    if "*" in target:
        return None          # a glob is a description, not a link
    return target


def extract_targets(text: str) -> tuple[set[str], set[str]]:
    """Return (link targets, mention targets). Only links can be dangling."""
    links: set[str] = set()
    for pattern in _LINK_PATTERNS:
        for raw in pattern.findall(text):
            target = _clean(raw)
            if target:
                links.add(target)
    mentions: set[str] = set()
    for raw in _MENTION_PATTERN.findall(text):
        target = _clean(raw)
        if target and target not in links:
            mentions.add(target)
    return links, mentions


def resolve(target: str, from_file: Path) -> Path | None:
    """Resolve a link target to a repo file, or None if it points nowhere.

    Tries, in order: relative to the linking file, relative to the repo root,
    and -- for wikilinks, which omit the extension -- the same with `.md`.
    """
    candidates = []
    for base in (from_file.parent, ROOT):
        candidates.append(base / target)
        if not target.endswith((".md", ".py", ".json", ".js", ".txt")):
            candidates.append(base / (target + ".md"))
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        if resolved.is_file() and ROOT in resolved.parents:
            return resolved
    return None


def reachable_from(entry: Path, max_hops: int | None = None) -> tuple[set[Path], list[tuple[Path, str]]]:
    """BFS over links. Returns (reachable files, dangling (source, target) pairs)."""
    if not entry.is_file():
        raise FileNotFoundError(f"entry point does not exist: {entry}")
    seen = {entry.resolve()}
    dangling: list[tuple[Path, str]] = []
    queue: deque[tuple[Path, int]] = deque([(entry.resolve(), 0)])
    while queue:
        current, hops = queue.popleft()
        if max_hops is not None and hops >= max_hops:
            continue
        if current.suffix != ".md":
            continue  # only markdown carries links we follow
        try:
            text = current.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        links, mentions = extract_targets(text)
        for target in links:
            resolved = resolve(target, current)
            if resolved is None:
                dangling.append((current, target))   # a link is a promise
                continue
            if resolved not in seen:
                seen.add(resolved)
                queue.append((resolved, hops + 1))
        for target in mentions:
            resolved = resolve(target, current)
            if resolved is not None and resolved not in seen:
                # reachable via the mention, but never reported as dangling
                seen.add(resolved)
                queue.append((resolved, hops + 1))
    return seen, dangling


def changed_since(ref: str) -> set[Path]:
    """Files changed since `ref`, per git. Untracked files are included --
    a file that was never committed is exactly the kind a handoff forgets."""
    out: set[Path] = set()
    for args in (
        ["git", "diff", "--name-only", f"{ref}...HEAD"],
        ["git", "ls-files", "--others", "--exclude-standard"],
    ):
        try:
            proc = subprocess.run(
                args, cwd=ROOT, capture_output=True, text=True, check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
        for line in proc.stdout.splitlines():
            path = (ROOT / line.strip()).resolve()
            if line.strip() and path.is_file() and not _skip(path):
                out.add(path)
    return out


def audit(entry_rel: str, ref: str, max_hops: int | None) -> dict:
    entry = (ROOT / entry_rel).resolve()
    reachable, dangling = reachable_from(entry, max_hops)
    changed = changed_since(ref)
    orphans = sorted(changed - reachable)
    return {
        "entry": entry_rel,
        "ref": ref,
        "max_hops": max_hops,
        "reachable_count": len(reachable),
        "changed_count": len(changed),
        "orphans": [str(p.relative_to(ROOT)) for p in orphans],
        "dangling": [
            {"source": str(s.relative_to(ROOT)), "target": t}
            for s, t in sorted(dangling, key=lambda x: (str(x[0]), x[1]))
        ],
        # Stated, not implied: what a pass here does and does not mean.
        "measures": "link reachability only",
        "does_not_measure": [
            "whether the handoff text is understandable",
            "whether a subject agent can reconstruct the next action",
            "search recall",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit whether changed files are reachable from the handoff entry point."
    )
    parser.add_argument("--entry", default=DEFAULT_ENTRY)
    parser.add_argument(
        "--ref",
        default="origin/HEAD",
        help="git ref to diff against (default: origin/HEAD)",
    )
    parser.add_argument("--max-hops", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--fail-on",
        choices=("none", "orphans", "any"),
        default="none",
        help="exit 1 when the named findings exist (default: none -- report only)",
    )
    args = parser.parse_args()

    try:
        report = audit(args.entry, args.ref, args.max_hops)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"entry     : {report['entry']}  (ref {report['ref']})")
        print(f"reachable : {report['reachable_count']} files")
        print(f"changed   : {report['changed_count']} files")
        print(f"orphans   : {len(report['orphans'])}")
        for path in report["orphans"]:
            print(f"    ORPHAN   {path}")
        print(f"dangling  : {len(report['dangling'])}")
        for item in report["dangling"]:
            print(f"    DANGLING {item['source']} -> {item['target']}")
        print()
        print("measures link reachability only -- NOT whether the handoff is")
        print("understandable, and NOT whether a subject agent could resume.")

    if args.fail_on == "orphans" and report["orphans"]:
        return 1
    if args.fail_on == "any" and (report["orphans"] or report["dangling"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
