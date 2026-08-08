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

STATUS AFTER ADVERSARIAL REVIEW (2026-08-06) -- READ THIS FIRST
---------------------------------------------------------------
An independent red team reached PASS by **three** routes and found that this
module's own docstring claimed five guards while implementing three:
`tracked_file_count()` was defined and never called (G4), and `main()` was
single-shot with no loop (G5). That is the exact defect class this repo has
been cataloguing all along -- a stated proposition that the code does not
make true -- committed inside a tool written to catch it. The claim came
first and was never checked against the implementation.

G2/G4/G5 and the input-set check are now implemented. **G1 remains bypassable
and is documented as such below -- do not treat a green run as tamper-proof.**

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
G4 input set may not      IMPLEMENTED 2026-08-06. Orphans must fall because
   shrink                 links were ADDED, not because files left the audit's
                          input. The red team cleared the only orphan by adding
                          it to .gitignore, and by deleting the dangling links
                          outright -- reachability measured 135 files before
                          AND after, metric 9 -> 0 with zero real improvement.
                          So: tracked-file count may not drop, `.gitignore` is
                          pinned, and the changed-file set may not lose members.
G5 monotonic progress     IMPLEMENTED 2026-08-06 as `--require-progress`:
                          compare against a recorded previous findings count
                          and refuse to accept a run that did not reduce it.

KNOWN UNCLOSED BYPASS -- G1 pins the wrong artifact
---------------------------------------------------
G1 hashes the auditor's SOURCE bytes, but CPython executes BYTECODE. The red
team compiled a patched `audit()` into a hash-based UNCHECKED .pyc, restored
the source byte-for-byte, and got PASS with the G1 pin matching exactly and
`git status` clean (`__pycache__/` is gitignored). `python3 -B` does not
defend -- it only disables writing.

This is NOT fixed here. Closing it means running the auditor in a subprocess
with `-B -E -P -I` and a purged/redirected cache rather than importing it.
Until then: **a green run of this loop is evidence about the documents, not
evidence that nobody tampered with the grader.** Stated rather than silently
carried, per this repo's own rule about naming conditions you cannot check.

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
    # G4: the red team cleared the only orphan by adding it to .gitignore --
    # narrowing the audit's input rather than repairing anything.
    ".gitignore",
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
    paths = [line.strip() for line in proc.stdout.splitlines()]
    # Untracked markdown must be inspected too: the red team put a 40-link
    # dump in a NEW file and linked to it, and `git diff` never mentions it.
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT,
        capture_output=True, text=True, check=True,
    )
    paths += [line.strip() for line in untracked.stdout.splitlines()]
    return [
        ROOT / rel for rel in paths
        if rel.endswith(".md") and (ROOT / rel).is_file()
    ]


def audit_input_set(ref: str) -> set[str]:
    """G4. The exact set the auditor will consider 'changed'. Snapshotted at
    loop start; a member disappearing means the input was narrowed, not that a
    file was repaired."""
    return {str(p.relative_to(ROOT)) for p in hr.changed_since(ref)}


def skip_worktree_paths() -> list[str]:
    """G4/G2. `git update-index --skip-worktree` makes a modified file vanish
    from `git diff` while the auditor still reads it from disk -- the red team
    blinded the edit guards with one reversible command and no commit."""
    proc = subprocess.run(
        ["git", "ls-files", "-v"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [
        line[2:].strip() for line in proc.stdout.splitlines()
        if line and line[0] not in "H"
    ]


def assert_input_not_narrowed(before: dict) -> list[str]:
    """G4. Returns violations rather than raising, so one run reports all."""
    out: list[str] = []
    now_tracked = tracked_file_count()
    if now_tracked < before["tracked_file_count"]:
        out.append(
            f"G4: tracked files dropped {before['tracked_file_count']} -> "
            f"{now_tracked}. Findings must fall because links were added, not "
            f"because files left the repo."
        )
    now_inputs = audit_input_set(before["ref"])
    lost = set(before["audit_inputs"]) - now_inputs
    if lost:
        out.append(
            f"G4: these files left the audit input set: {sorted(lost)}. "
            f"Gitignoring or deleting an orphan is not a repair."
        )
    flagged = skip_worktree_paths()
    if flagged:
        out.append(
            f"G4: skip-worktree/assume-unchanged is set on {flagged}. That "
            f"hides real edits from the guards while the auditor still reads "
            f"them. Clear it with `git update-index --no-skip-worktree`."
        )
    return out


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
        if not proc.stdout.strip():
            # An untracked file produces no diff at all. Its entire content is
            # new, so inspect all of it -- otherwise a fresh file is a free
            # dumping ground (red team Attack 5).
            added = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        if not added:
            continue
        link_lines = [line for line in added if _LINK_LINE.search(line)]
        # Count LINKS, not linked lines. The red team put 12 links on one
        # prose line and the old per-line count read it as 1.
        link_count = sum(len(_LINK_LINE.findall(line)) for line in added)
        if link_count > max_links:
            violations.append(
                f"G2 {rel}: added {link_count} links across "
                f"{len(link_lines)} line(s) (max {max_links}). Split the repair "
                f"or write context, do not dump links."
            )
        nonblank = [line for line in added if line.strip()]
        # `>=`, not `>`: one padding prose line beside one link line gave
        # exactly 0.5 and slipped through.
        if nonblank and len(link_lines) / len(nonblank) >= dump_ratio:
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
                    help="print the grader hashes + baseline and exit "
                         "(run before editing)")
    ap.add_argument("--require-progress", type=int, default=None,
                    metavar="PREV",
                    help="G5: fail unless findings dropped below PREV")
    args = ap.parse_args()

    if args.emit_pins:
        # G4 needs a baseline, not just hashes -- capture it in the same blob
        # so a caller cannot forget one half.
        print(json.dumps({
            "hashes": pin(),
            "tracked_file_count": tracked_file_count(),
            "ref": args.ref,
            "audit_inputs": sorted(audit_input_set(args.ref)),
        }, indent=2))
        return 0

    baseline = args.baseline or "HEAD"

    # G1 -- refuse to grade if the grader moved.
    baseline_state = None
    if args.pins:
        blob = json.loads(args.pins)
        blob = blob if "hashes" in blob else {"hashes": blob}
        try:
            assert_pins_intact(blob["hashes"])
        except GameDetected as exc:
            print(f"BLOCKED  {exc}", file=sys.stderr)
            return 2
        if "audit_inputs" in blob:
            baseline_state = blob

    # G2/G3 -- inspect what the repair actually did.
    violations = inspect_edits(
        baseline, args.max_links_per_file, args.dump_ratio, args.min_context_chars
    )
    # G4 -- did the input set shrink instead of the findings?
    if baseline_state:
        violations += assert_input_not_narrowed(baseline_state)
    elif args.pins:
        violations.append(
            "G4: --pins lacks a baseline snapshot (re-run --emit-pins with this "
            "version). Input-narrowing cannot be detected without it."
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

    if args.require_progress is not None and total >= args.require_progress:
        print(f"\nG5 STALL: findings {total} did not drop below "
              f"{args.require_progress}. Stop and re-read the findings rather "
              f"than iterating.")
        return 1

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
