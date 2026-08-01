"""Excludes superseded tests from collection.

These tests exercised the Q2 anchor-flip diagnostic, retired by Q6=A (see
WHY.md). They import sibling modules by path relative to their own directory
(`HERE / "_h1a_surface.py"`), which was correct before this move and is not
rewritten here -- rewriting a superseded file's internals would defeat the
point of preserving it as a historical, once-passing artifact. Collection is
skipped instead of fixed.
"""

collect_ignore = ["test_h1a_diag.py", "test_h1a_diag_score.py"]
