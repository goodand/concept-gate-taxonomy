"""Wikilink graph hygiene gate -- catches dead and ambiguous `[[...]]` links.

This module is the implementation for the contract fixed by
`test_wikilink_graph.py`. See that file's module docstring for the full
rationale (three removed predecessors, the false-positive/silent-miss
failure modes they left behind, and the measured link composition of this
repo). In one line: it measures whether a `[[...]]` written in a `*.md`
file in this repo resolves to a real file *inside this repo*. It does not
consult any external index, and it does not measure backlink direction or
whether a link is useful -- only whether it is reachable.

Public surface
--------------
- `Status`            -- OK / AMBIGUOUS / DEAD / EXTERNAL
- `Link`              -- one parsed `[[...]]` occurrence: `.line`, `.target`,
                          and (only for `scan_links`) `.source`
- `iter_wikilinks`     -- parse one file's text into `Link`s
- `resolve`            -- resolve one link's target to a `Resolution`
- `Resolution`         -- `.status`, `.path` (OK only), `.candidates`
                          (AMBIGUOUS only)
- `Finding`            -- one dead/ambiguous occurrence found by `scan`:
                          `.source` (absolute path), `.line`, `.target`,
                          `.candidates` (ambiguous only)
- `scan`               -- walk the repo, return a `Report`
- `Report`             -- `.total`, `.dead`, `.ambiguous`
- `scan_links`         -- walk the repo, return every `Link` with `.source`
                          set (used by the baseline sanity gate)

Stdlib only. Filesystem only -- no Obsidian index, no network.
"""
from __future__ import annotations

import functools
import os
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path, PurePosixPath
from typing import Iterable, Iterator


# ---------------------------------------------------------------------------
# 1. Parsing
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Link:
    """One `[[...]]` occurrence. `source` is only populated by `scan_links`."""

    line: int
    target: str
    source: Path | None = None


# `*?` (not `+?`): an empty pair like `[[]]` must close immediately on its
# own adjacent `]]`. With `+?` (content >= 1 char required), the regex
# cannot match `[[]]` at all and backtracks past it into whatever the next
# `[[...]]` on the line is, silently fusing two links into one bogus match.
_WIKILINK_RE = re.compile(r"\[\[(.*?)\]\]")
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")
_FENCE_OPEN_RE = re.compile(r"^([`~])\1{2,}")
_ALIAS_RE = re.compile(r"\\?\|")


def _fenced_mask(lines: list[str]) -> list[bool]:
    """Per-line: True if the line is a fence marker or inside a fenced block.

    Conservative on purpose: an unclosed fence masks everything after it
    (test_unclosed_fence_swallows_the_rest_of_the_file) rather than risk
    reading fence content as prose.
    """
    masked = [False] * len(lines)
    in_fence = False
    fence_char = ""
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if in_fence:
            masked[i] = True
            candidate = stripped.rstrip()
            if len(candidate) >= 3 and set(candidate) == {fence_char}:
                in_fence = False
            continue
        m = _FENCE_OPEN_RE.match(stripped)
        if m:
            in_fence = True
            fence_char = m.group(1)
            masked[i] = True
    return masked


def _parse_target(raw: str) -> str | None:
    """Strip an anchor and an alias from raw `[[...]]` content.

    Anchor and alias both discard everything after them
    (`target#anchor|alias` is Obsidian's own order), so splitting on the
    first `#` already removes a trailing alias too; the separate alias
    split below only matters when there is no anchor.
    """
    before_anchor = raw.split("#", 1)[0]
    target = _ALIAS_RE.split(before_anchor, maxsplit=1)[0]
    target = target.strip()
    if not target or '"' in target:
        return None
    if target.startswith("./"):
        target = target[2:]
    elif target.startswith("/"):
        target = target[1:]
    return target or None


def iter_wikilinks(text: str) -> Iterator[Link]:
    """Yield every `[[...]]` in `text` that is a real link, in file order.

    Excludes: fenced code blocks, inline code spans, anchor-only
    self-references (`[[#x]]`), and empty/quoted-looking targets.
    """
    lines = text.splitlines()
    fenced = _fenced_mask(lines)
    for i, raw_line in enumerate(lines):
        if fenced[i]:
            continue
        line = _INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), raw_line)
        for m in _WIKILINK_RE.finditer(line):
            target = _parse_target(m.group(1))
            if target is not None:
                yield Link(line=i + 1, target=target)


# ---------------------------------------------------------------------------
# 2. Resolution
# ---------------------------------------------------------------------------

class Status(Enum):
    OK = auto()
    AMBIGUOUS = auto()
    DEAD = auto()
    EXTERNAL = auto()


@dataclass(frozen=True)
class Resolution:
    status: Status
    path: Path | None = None
    candidates: tuple[Path, ...] = ()


_SKIP_DIRS = {".git", "vendor"}


@functools.lru_cache(maxsize=None)
def _repo_files(repo_root: Path) -> tuple[Path, ...]:
    """Every file under `repo_root`, excluding exactly `.git/` and `vendor/`.

    Cached per repo_root: `resolve()` is called once per bare link (~270 in
    this repo), and re-walking the whole tree each time is wasted work once
    the tree is known not to change within a process.
    """
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for fn in filenames:
            files.append(Path(dirpath) / fn)
    return tuple(files)


def _candidates_for(base: Path, target: str) -> list[Path]:
    """A literal-path candidate, plus a `.md`-suffixed one if not already."""
    p = base / target
    if target.endswith(".md"):
        return [p]
    return [p, base / f"{target}.md"]


def _exists_case_sensitive(path: Path) -> bool:
    """`path` exists as a file with exactly this case, even on a
    case-insensitive filesystem (macOS default)."""
    parent = path.parent
    if not parent.is_dir():
        return False
    try:
        names = {child.name for child in parent.iterdir()}
    except OSError:
        return False
    return path.name in names and path.is_file()


def _bare_match(path: Path, target: str) -> bool:
    if target.endswith(".md"):
        return path.name == target
    return path.stem == target


def _resolve_bare(repo_root: Path, target: str) -> Resolution:
    """Bare basename (`[[FOO]]`, no `/`): a global stem search. The
    dominant shape (80%) in this repo -- ambiguity here is the whole point
    of this gate, so a stem matching 2+ files is AMBIGUOUS, never a
    silent first pick."""
    if not target:
        return Resolution(Status.DEAD)
    matches = [f for f in _repo_files(repo_root) if _bare_match(f, target)]
    if not matches:
        return Resolution(Status.DEAD)
    if len(matches) > 1:
        return Resolution(Status.AMBIGUOUS, candidates=tuple(matches))
    return Resolution(Status.OK, path=matches[0])


def _try_literal(repo_root_real: Path, bases: tuple[Path, ...], target: str) -> Resolution | None:
    """Try `target` as a literal path under each base, in order. `None`
    means no base had it -- the caller decides what that means."""
    for base in bases:
        for cand in _candidates_for(base, target):
            if _exists_case_sensitive(cand):
                real = cand.resolve()
                try:
                    real.relative_to(repo_root_real)
                except ValueError:
                    # Exists, but a symlink resolves outside the repo.
                    return Resolution(Status.EXTERNAL)
                return Resolution(Status.OK, path=cand)
    return None


def _resolve_own_prefixed(repo_root: Path, remainder: str) -> Resolution:
    """`[[<own-worktree-name>/...]]`: a vault-rooted self-reference.
    Obsidian resolved it from the vault root through the worktree name;
    once that name is stripped, the remainder is a root-relative path
    within *this* repo specifically -- never a bare/global search (a
    single-segment remainder like `HANDOFF` must still mean this repo's
    own root `HANDOFF.md`, not any `HANDOFF.md` anywhere in the tree) and
    never document-relative (the vault-rooted form doesn't carry the
    referring document's own position)."""
    repo_root_real = repo_root.resolve()
    found = _try_literal(repo_root_real, (repo_root,), remainder)
    return found if found is not None else Resolution(Status.DEAD)


def _resolve_qualified(
    repo_root: Path, source: Path, target: str, parts: tuple[str, ...]
) -> Resolution:
    """Path-qualified target (contains `/`): tried as a literal path only --
    root-relative first, then document-relative -- never falls back to the
    bare basename search (a decoy same-named file elsewhere must not turn a
    typo'd qualified path into a false OK)."""
    if ".." in parts:
        # Parent traversal always leaves the repo; out of scope, not a defect.
        return Resolution(Status.EXTERNAL)

    repo_root_real = repo_root.resolve()
    found = _try_literal(repo_root_real, (repo_root, source.parent), target)
    if found is not None:
        return found

    # Nothing matched literally. If the first path segment isn't part of
    # this repo's own directory tree under either base, the target names
    # something outside this repo's namespace (another worktree / vault
    # area) rather than a broken path inside it.
    first = parts[0]
    for base in (repo_root, source.parent):
        if (base / first).is_dir():
            return Resolution(Status.DEAD)
    return Resolution(Status.EXTERNAL)


def resolve(repo_root: Path, source: Path, target: str) -> Resolution:
    """Resolve one wikilink `target` written inside `source`.

    Order: strip an own-worktree prefix (Obsidian's root is the vault;
    this gate's root is the worktree) -> bare basename goes to a global
    stem search -> path-qualified tries root-relative then
    document-relative as literal paths.
    """
    repo_root = Path(repo_root)
    target = target.strip()
    parts = PurePosixPath(target).parts
    if len(parts) > 1 and parts[0] == repo_root.name:
        remainder = "/".join(parts[1:])
        return _resolve_own_prefixed(repo_root, remainder)

    if len(parts) <= 1:
        return _resolve_bare(repo_root, target)
    return _resolve_qualified(repo_root, source, target, parts)


# ---------------------------------------------------------------------------
# 3. Scan
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Finding:
    source: Path
    line: int
    target: str
    candidates: tuple[Path, ...] = field(default=())


@dataclass(frozen=True)
class Report:
    total: int
    dead: list[Finding]
    ambiguous: list[Finding]


def _markdown_files(repo_root: Path) -> list[Path]:
    return sorted(p for p in _repo_files(Path(repo_root)) if p.suffix == ".md")


def scan_links(repo_root: Path) -> Iterable[Link]:
    """Every `[[...]]` link in every `*.md` file under `repo_root`, each
    carrying its absolute `source` path."""
    repo_root = Path(repo_root)
    for md_file in _markdown_files(repo_root):
        text = md_file.read_text(encoding="utf-8", errors="replace")
        for link in iter_wikilinks(text):
            yield Link(line=link.line, target=link.target, source=md_file)


def scan(repo_root: Path) -> Report:
    """Walk `repo_root` and report every link occurrence, plus every dead
    or ambiguous one with its location."""
    repo_root = Path(repo_root)
    total = 0
    dead: list[Finding] = []
    ambiguous: list[Finding] = []
    for link in scan_links(repo_root):
        total += 1
        r = resolve(repo_root, link.source, link.target)
        if r.status is Status.DEAD:
            dead.append(Finding(source=link.source, line=link.line, target=link.target))
        elif r.status is Status.AMBIGUOUS:
            ambiguous.append(
                Finding(
                    source=link.source,
                    line=link.line,
                    target=link.target,
                    candidates=tuple(r.candidates),
                )
            )

    key = lambda f: (f.source.as_posix(), f.line)
    dead.sort(key=key)
    ambiguous.sort(key=key)
    return Report(total=total, dead=dead, ambiguous=ambiguous)
