"""Both directions for the handoff reachability auditor.

An auditor whose findings nobody trusts is worse than none (this repo's
tripwire-precision lesson). Its first run reported 404 "dangling" findings,
nearly all prose; these tests pin the fix so the distinction between a LINK
(a promise the target exists) and a MENTION (prose naming a file) cannot be
silently collapsed again.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
import handoff_reachability as hr  # noqa: E402


# --------------------------------------------------------------------------
# extract_targets: links vs mentions
# --------------------------------------------------------------------------
def test_markdown_links_and_wikilinks_are_links():
    links, mentions = hr.extract_targets(
        "see [the ruling](docs/D.md) and [[notes/other]] for context"
    )
    assert links == {"docs/D.md", "notes/other"}
    assert mentions == set()


def test_inline_code_filename_is_a_mention_not_a_link():
    """The 404-finding bug: prose naming a file was treated as a broken link."""
    links, mentions = hr.extract_targets("the policy lives in `_h1a_policy.py`")
    assert links == set()
    assert mentions == {"_h1a_policy.py"}


def test_a_glob_is_never_a_target():
    """`experiments/*/test_protocol.py` describes a set, it does not link."""
    links, mentions = hr.extract_targets(
        "runs [all](experiments/*/test_protocol.py) and `DESIGN_DECISION*.md`"
    )
    assert links == set()
    assert mentions == set()


def test_urls_are_not_repo_targets():
    links, _ = hr.extract_targets("[spec](https://example.com/x.md)")
    assert links == set()


def test_anchors_and_aliases_are_stripped():
    links, _ = hr.extract_targets("[x](docs/D.md#section) and [[notes/n|Alias]]")
    assert links == {"docs/D.md", "notes/n"}


def test_a_file_named_by_both_a_link_and_a_mention_counts_once_as_a_link():
    links, mentions = hr.extract_targets("[D](docs/D.md) — see `docs/D.md`")
    assert links == {"docs/D.md"}
    assert "docs/D.md" not in mentions


# --------------------------------------------------------------------------
# reachability: recall (finds orphans) and precision (does not invent them)
# --------------------------------------------------------------------------
def _write(root: Path, rel: str, body: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")
    return path


def test_reachable_follows_links_transitively(tmp_path, monkeypatch):
    monkeypatch.setattr(hr, "ROOT", tmp_path)
    entry = _write(tmp_path, "H.md", "[a](a.md)")
    _write(tmp_path, "a.md", "[b](sub/b.md)")
    _write(tmp_path, "sub/b.md", "leaf")
    reachable, dangling = hr.reachable_from(entry)
    assert {p.name for p in reachable} == {"H.md", "a.md", "b.md"}
    assert dangling == []


def test_reachable_follows_mentions_too(tmp_path, monkeypatch):
    """A mention still makes the file findable -- only its *failure* is silent."""
    monkeypatch.setattr(hr, "ROOT", tmp_path)
    entry = _write(tmp_path, "H.md", "the code is in `impl.py`")
    _write(tmp_path, "impl.py", "x = 1")
    reachable, dangling = hr.reachable_from(entry)
    assert {p.name for p in reachable} == {"H.md", "impl.py"}
    assert dangling == []


def test_a_broken_link_is_reported_dangling(tmp_path, monkeypatch):
    """RECALL. This is the Q13-shaped defect at link level."""
    monkeypatch.setattr(hr, "ROOT", tmp_path)
    entry = _write(tmp_path, "H.md", "[gone](does/not/exist.md)")
    _, dangling = hr.reachable_from(entry)
    assert [t for _, t in dangling] == ["does/not/exist.md"]


def test_a_broken_mention_is_NOT_reported_dangling(tmp_path, monkeypatch):
    """PRECISION. The exact false-positive class that produced 404 findings."""
    monkeypatch.setattr(hr, "ROOT", tmp_path)
    entry = _write(tmp_path, "H.md", "compare against `NEXT_SESSION_TRAPS.md`")
    reachable, dangling = hr.reachable_from(entry)
    assert dangling == []
    assert {p.name for p in reachable} == {"H.md"}


def test_max_hops_bounds_the_walk(tmp_path, monkeypatch):
    monkeypatch.setattr(hr, "ROOT", tmp_path)
    entry = _write(tmp_path, "H.md", "[a](a.md)")
    _write(tmp_path, "a.md", "[b](b.md)")
    _write(tmp_path, "b.md", "leaf")
    reachable, _ = hr.reachable_from(entry, max_hops=1)
    assert {p.name for p in reachable} == {"H.md", "a.md"}


def test_a_cycle_terminates(tmp_path, monkeypatch):
    monkeypatch.setattr(hr, "ROOT", tmp_path)
    entry = _write(tmp_path, "H.md", "[a](a.md)")
    _write(tmp_path, "a.md", "[back](H.md)")
    reachable, _ = hr.reachable_from(entry)
    assert {p.name for p in reachable} == {"H.md", "a.md"}


def test_a_path_escaping_the_root_is_not_resolved(tmp_path, monkeypatch):
    """`../other-worktree/X.md` must not count as reachable in THIS repo."""
    monkeypatch.setattr(hr, "ROOT", tmp_path / "repo")
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "X.md").write_text("x", encoding="utf-8")
    entry = _write(tmp_path / "repo", "H.md", "[x](../outside/X.md)")
    _, dangling = hr.reachable_from(entry)
    assert [t for _, t in dangling] == ["../outside/X.md"]


def test_missing_entry_point_raises_rather_than_reporting_clean(tmp_path, monkeypatch):
    """Silence must not be mistaken for a pass when the entry does not exist."""
    monkeypatch.setattr(hr, "ROOT", tmp_path)
    with pytest.raises(FileNotFoundError):
        hr.reachable_from(tmp_path / "nope.md")


# --------------------------------------------------------------------------
# the auditor's own scope claim
# --------------------------------------------------------------------------
def test_report_states_what_it_does_not_measure(tmp_path, monkeypatch):
    """Patterns 8/10: say which proposition a pass proves. A green run here
    must never read as 'the handoff is good'."""
    monkeypatch.setattr(hr, "ROOT", tmp_path)
    _write(tmp_path, "H.md", "entry")
    report = hr.audit("H.md", "HEAD", None)
    assert report["measures"] == "link reachability only"
    assert any("understandable" in s for s in report["does_not_measure"])
    assert any("subject agent" in s for s in report["does_not_measure"])
