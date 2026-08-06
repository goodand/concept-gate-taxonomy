#!/usr/bin/env python3
"""Drive an edit-audit-repeat loop over handoff reachability -- with the
anti-gaming guards that make such a loop safe to run at all.

THE PROBLEM WITH "EDIT UNTIL THE CHECKER PASSES"
------------------------------------------------
`orphans: 0` is trivially reachable by appending a list of links to the bottom
of the handoff. That passes the audit and makes the handoff WORSE: a reader
still cannot tell why any of those files matter or in what order to read them.
The metric would be optimized and the goal abandoned -- and this repo has
already recorded that exact failure shape ("가드가 통과하는데도 결함이 남는다").

So this driver does not just loop. It **constrains what a repair may look
like** and refuses to certify a run whose edits are degenerate. The loop is the
easy part; the guards are the point.

GUARDS (each one exists because the cheap fix violates it)
----------------------------------------------------------
G1 checker immutability   The auditor and its tests are hash-pinned before the
                          loop starts. Editing the thing that grades you is the
                          most direct gaming path.
G2 no link dumps          A repair may not add more than `--max-links-per-file`
                          links to one file in one iteration, and may not add a
                          section whose lines are >`--dump-ratio` links. A
                          handoff entry is prose that happens to link, not a
                          link list.
G3 context required       Every added link must sit on a line with at least
                          `--min-context-chars` of non-link text. A bare
                          `- [file](path)` tells the next session nothing.
G4 no deletion to pass    Orphans must fall because links were ADDED, not
                          because files were deleted or the audit's inputs were
                          narrowed. Tracked-file count may not drop.
G5 monotonic progress     Each iteration must strictly reduce findings, else
                          the loop stops and reports a stall rather than
                          burning iterations.

WHAT A GREEN RUN MEANS
----------------------
Exactly what the underlying auditor means and no more: every changed file is
reachable by a link, and no link is broken. It does NOT mean the handoff is
good. G2/G3 raise the floor on edit quality; they do not certify usefulness.
Human or independent review still decides that.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import handoff_reachability as hr  # noqa: E402

# Files the loop must never modify: the grader and its own tests.
PINNED = (
    "scripts/handoff_reachability.py",
    "scripts/handoff_repair_loop.py",
    "test_handoff_reachability.py",
)
_LINK_LINE = re.compile(r"\[[^\]]*\]\([^)]+\)|\[\[[^\]]+\]\]")


class GameDetected(Exception):
    """A repair satisfied the metric by a route the metric was not measuring."""


def pin(paths=PINNED) -> dict[str, str]:
    out = {}
    for rel in paths:
        path = ROOT / rel
        out[rel] = (
            hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else "ABSENT"
        )
    return out


def assert_pins_intact(before: dict[str, str]) -> None:
    """G1. Checked every iteration, not just at the end -- a mid-loop edit to
    the grader would otherwise be laundered by a later revert."""
    now = pin(tuple(before))
    drifted = [rel for rel, digest in before.items() if now[rel] != digest]
    if drifted:
        raise GameDetected(
            f"G1: the grader changed during the loop: {drifted}. A repair may "
            f"not edit the auditor or its tests."
        )


def tracked_file_count() -> int:
    proc = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return len([line for line in proc.stdout.splitlines() if line.strip()])


def changed_markdown(ref: str) -> list[Path]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", ref], cwd=ROOT,
        capture_output=True, text=True, check=True,
    )
    return [
        ROOT / line for line in proc.stdout.splitlines()
        if line.strip().endswith(".md") and (ROOT / line.strip()).is_file()
    ]


def inspect_edits(ref: str, max_links: int, dump_ratio: float,
                  min_context: int) -> list[str]:
    """G2 + G3. Read the diff of this iteration's markdown edits and report
    violations. Returns [] when the edits look like prose that links."""
    violations: list[str] = []
    for path in changed_markdown(ref):
        rel = path.relative_to(ROOT)
        proc = subprocess.run(
            ["git", "diff", "-U0", ref, "--", str(rel)], cwd=ROOT,
            capture_output=True, text=True, check=True,
        )
        added = [
            line[1:] for line in proc.stdout.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
        if not added:
            continue
        link_lines = [line for line in added if _LINK_LINE.search(line)]
        if len(link_lines) > max_links:
            violations.append(
                f"G2 {rel}: added {len(link_lines)} linked lines "
                f"(max {max_links}). Split the repair or write context, do not "
                f"dump links."
            )
        nonblank = [line for line in added if line.strip()]
        if nonblank and len(link_lines) / len(nonblank) > dump_ratio:
            violations.append(
                f"G2 {rel}: {len(link_lines)}/{len(nonblank)} added lines are "
                f"links (>{dump_ratio:.0%}). That is a link dump, not a handoff."
            )
        for line in link_lines:
            bare = _LINK_LINE.sub("", line)
            bare = re.sub(r"[-*|>#\s]", "", bare)
            if len(bare) < min_context:
                violations.append(
                    f"G3 {rel}: link line has {len(bare)} chars of context "
                    f"(min {min_context}): {line.strip()[:70]!r}. Say why the "
                    f"next session needs it."
                )
    return violations


def findings(entry: str, ref: str, max_hops: int | None) -> tuple[int, dict]:
    report = hr.audit(entry, ref, max_hops)
    return len(report["orphans"]) + len(report["dangling"]), report


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--entry", default=hr.DEFAULT_ENTRY)
    ap.add_argument("--ref", default="origin/HEAD")
    ap.add_argument("--max-hops", type=int, default=None)
    ap.add_argument("--max-links-per-file", type=int, default=4)
    ap.add_argument("--dump-ratio", type=float, default=0.5)
    ap.add_argument("--min-context-chars", type=int, default=25)
    ap.add_argument("--baseline", default=None,
                    help="git ref the loop started from, for edit inspection "
                         "(default: HEAD, i.e. inspect uncommitted edits)")
    ap.add_argument("--pins", default=None,
                    help="JSON from a previous --emit-pins run")
    ap.add_argument("--emit-pins", action="store_true",
                    help="print the grader hashes and exit (run before editing)")
    args = ap.parse_args()

    if args.emit_pins:
        print(json.dumps(pin(), indent=2))
        return 0

    baseline = args.baseline or "HEAD"

    # G1 -- refuse to grade if the grader moved.
    if args.pins:
        try:
            assert_pins_intact(json.loads(args.pins))
        except GameDetected as exc:
            print(f"BLOCKED  {exc}", file=sys.stderr)
            return 2

    # G2/G3 -- inspect what the repair actually did.
    violations = inspect_edits(
        baseline, args.max_links_per_file, args.dump_ratio, args.min_context_chars
    )

    total, report = findings(args.entry, args.ref, args.max_hops)

    print(f"findings  : {total}  (orphans {len(report['orphans'])}, "
          f"dangling {len(report['dangling'])})")
    for path in report["orphans"]:
        print(f"    ORPHAN   {path}")
    for item in report["dangling"]:
        print(f"    DANGLING {item['source']} -> {item['target']}")

    if violations:
        print(f"\ngaming guards: {len(violations)} VIOLATION(S)")
        for v in violations:
            print(f"    {v}")
        print("\nThe findings count is NOT accepted while guards are violated --")
        print("a metric satisfied by a degenerate edit is not satisfied.")
        return 1
    print("\ngaming guards: clean")

    if total == 0:
        print("\nPASS -- every changed file is reachable and no link is broken.")
        print("This does NOT mean the handoff is understandable. That still")
        print("needs a subject agent or a human (HANDOFF_REUSE_VALIDATION.md).")
        return 0

    print("\nNOT YET CLEAN -- repair the findings above, then re-run.")
    print("Repairs must be prose that links, from a document that already")
    print("belongs in the reading path. Adding a link section at the end of")
    print("the handoff will trip G2.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
