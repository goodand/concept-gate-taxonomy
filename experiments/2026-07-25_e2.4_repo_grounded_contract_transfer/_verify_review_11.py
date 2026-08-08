#!/usr/bin/env python3
"""Independent cross-check of the constraint #11 review.  python3 _verify_review_11.py

Why this exists
---------------
verifying-the-verifier-at2026-07-29-00-19.md (pattern 9): a delegated LLM
verifier is a verifier, and an all-clean report from one is the same shape a
leaking run produced (7/7, 5/5, 5/5). Before accepting `review_11.json`'s
verdicts, reproduce the decisive part by a *different method* and from *more
primitive data*.

So this module deliberately does NOT reuse `_review_11.py`:

  different method   lexical scan, not an LLM judgment
  different data     trials_raw.json (the model's raw output) rather than
                     trials.json (the recorded, manifest-joined artifact)

What it can and cannot establish
--------------------------------
A silent scan only means something if the scan can speak. `self_check()`
therefore runs the same lexicon over the labelled calibration corpus first and
prints its own recall before reporting anything about the cohort. The first
version of this lexicon scored 4/5 -- it missed a violation phrased with
'더 최근에' because the pattern only had '최신'. That miss is why the check is
built this way rather than trusted on sight.

The scan is intentionally over-sensitive: it flags a *mention* of recency or
authority even when the rationale does not use it to rank anything, so it
scores 2 false positives on the corpus's discriminating cases. That is the
point -- an over-sensitive instrument falling silent is informative, whereas a
tuned one falling silent is not.

Stdlib only.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# The three grounds semantic_constraints #11 names -- newer / still in use /
# more authoritative -- plus supersession, which is how "newer" is usually
# phrased when it is used to dismiss something.
LEXICON = {
    "recency": r"최신|최근|나중|newer|more recent|later commit|이후 커밋|갱신된",
    "liveness": r"stale|살아 ?있|라이브|live code|still in use|현재 실행|outdated|낡은|유효한 코드",
    "supersession": r"supersede|superseded|대체|폐기|철회|무효화",
    "authority": r"권위|authoritative|우월|우선순위|더 신뢰|신뢰하는 것이",
}

CONTEXT = 70


def rationale_texts(output: dict) -> list[tuple[str, str]]:
    """Every natural-language span, as (slot, text). Mirrors what was reviewed."""
    texts = []
    for key in ("evidence_audit", "feature_judgments", "invariant_checks"):
        for i, item in enumerate(output.get(key) or []):
            text = (item or {}).get("rationale")
            if isinstance(text, str) and text:
                texts.append((f"{key}[{i}]", text))
    report = output.get("report")
    if isinstance(report, str) and report:
        texts.append(("report", report))
    return texts


def scan(output: dict) -> list[tuple[str, str, str]]:
    """Return (axis, slot, excerpt) for every lexical hit."""
    hits = []
    for axis, pattern in LEXICON.items():
        for slot, text in rationale_texts(output):
            for match in re.finditer(pattern, text, re.I):
                start = max(0, match.start() - CONTEXT)
                end = min(len(text), match.end() + CONTEXT)
                hits.append((axis, slot, text[start:end].replace("\n", " ")))
    return hits


def self_check() -> tuple[int, int, list[str]]:
    """Measure this scan against the labelled corpus before trusting its silence."""
    corpus = json.loads((HERE / "review_11_calibration.json").read_text(encoding="utf-8"))
    recall_cases = [c for c in corpus["cases"] if c["axis"] == "recall"]
    precision_cases = [c for c in corpus["cases"] if c["axis"] == "precision"]

    caught = [c["case_id"] for c in recall_cases if scan(c["output"])]
    flagged = [c["case_id"] for c in precision_cases if scan(c["output"])]
    return len(caught), len(recall_cases), flagged


def main() -> int:
    caught, total, false_positives = self_check()
    print("  scan self-check (labelled corpus)")
    print(f"    recall           {caught}/{total}")
    print(f"    false positives  {len(false_positives)}  {false_positives}")
    if caught < total:
        print("\n  ABORT: this scan cannot detect known violations, so its silence "
              "on the cohort would mean nothing. Widen the lexicon first.")
        return 1
    print("    -> the scan can speak; over-sensitive by design, so silence is informative\n")

    raw = json.loads((HERE / "trials_raw.json").read_text(encoding="utf-8"))
    hits = {tid: scan(out) for tid, out in sorted(raw.items())}
    hits = {tid: h for tid, h in hits.items() if h}

    print(f"  cohort scan (trials_raw.json, {len(raw)} trials)")
    print(f"    trials with any lexical hit  {len(hits)}/{len(raw)}")
    for tid, found in hits.items():
        print(f"\n    {tid}")
        for axis, slot, excerpt in found[:3]:
            print(f"      [{axis}/{slot}] ...{excerpt}...")

    reviewed = json.loads((HERE / "review_11.json").read_text(encoding="utf-8"))["reviews"]
    flagged_by_reviewer = {t for t, r in reviewed.items() if r["verdict"] == "violation"}

    print(f"\n  reviewer flagged  {len(flagged_by_reviewer)}  {sorted(flagged_by_reviewer)}")
    print(f"  scan flagged      {len(hits)}  {sorted(hits)}")

    only_scan = sorted(set(hits) - flagged_by_reviewer)
    only_reviewer = sorted(flagged_by_reviewer - set(hits))
    if only_scan:
        print(f"\n  scan found candidates the reviewer cleared: {only_scan}")
        print("  -> read those rationales by hand. A mention is not automatically a "
              "violation, but an unexamined disagreement is not a result.")
    if only_reviewer:
        print(f"\n  reviewer flagged trials the scan missed: {only_reviewer}")
        print("  -> expected when the reasoning is paraphrased; not a defect by itself.")
    if not only_scan and not only_reviewer:
        print("\n  the two methods agree.")

    # Stated precisely on purpose (pattern 9, minimum contract item 4).
    print("\n  what this establishes: RECALL was reproduced by a second, independent "
          "method on more primitive data.")
    print("  what it does NOT establish: precision on this cohort. There are no "
          "known-violating trials among the 30,")
    print("  so no negative control exists at cohort level. Reviewer precision was "
          "measured only on the labelled corpus.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
