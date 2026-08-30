"""wikilink 그래프 위생 게이트 — 죽은 링크와 모호한 링크를 잡는다.

구현보다 먼저 쓴 계약(TDD)이다. `scripts/wikilink_graph.py` 는 아직 없고,
아래 테스트가 그 모듈이 무엇이어야 하는지를 정한다.

왜 있는가
---------
2026-08-30 관계 그래프 점검(`docs/REFINE_VERIFY_STAGE_SURVEY_20260830.md` §11):
두 설계 계열을 잇는 유일한 MOC 의 링크 117건 중 34건(29%)이 제거된 worktree 를
가리켰다. 등록부의 거짓말은 `test_legacy_register.py` 가 막는데 **문서 그래프의
거짓말은 아무도 안 막았다.**

전임자 세 세대(`700ecc3` → `e9cea54` → `10fb68f`, 현재 REMOVED)가 남긴 것:

- **위양성이 도구를 죽인다.** 첫 실행이 dangling 404건을 냈고 거의 전부
  위양성이었다. 이 저장소 실측: 펜스 안 `[[` 11건, 인라인코드 안 6건.
- **조용한 오답이 제거 사유였다.** Obsidian 색인이 없으면 "backlink 0" 을 냈다.
  이 해소기는 **파일시스템만** 본다.
- **모호는 부재가 아니다.** codex `resolve_links`(`build_retrieval_index.py:259`)
  는 stem 이 여러 곳이면 부재와 같은 `continue` 로 떨어진다.

이 저장소 링크 구성 실측 (340건)
--------------------------------
    bare basename            273   ← 지배적. AMBIGUOUS 판정이 여기서 값을 한다
    자기 worktree 접두         66   ← `concept-gate-h1-wt/docs/…`
    다른 worktree / vault 영역   1

Obsidian 의 루트는 vault 이고 이 게이트의 루트는 worktree 다. 그래서 66건의
자기 접두를 벗기지 않으면 **전부 거짓 DEAD** 가 된다. 벗기는 데 필요한 것은
자기 디렉터리 이름 하나뿐이므로 게이트는 여전히 hermetic 하다.

무엇을 재고 무엇을 재지 않나
---------------------------
잰다: 이 저장소 안 `*.md` 의 `[[...]]` 가 저장소 안에서 해소되는가.
재지 않는다:
  - **저장소 밖**(`notes/00-moc/` 의 죽은 링크 29% 는 여기 없다). 다른 worktree
    를 가리키는 링크는 `EXTERNAL` 이며 **DEAD 가 아니다** — 범위 밖은 결함이
    아니다. 이 구분을 뭉개면 위양성이 된다.
  - **backlink 방향** — `vault_backlinks` MCP 가 한다. 중복 구현 금지.
  - **링크가 유용한가** — 전임자 표현대로 "measures link reachability only,
    NOT whether the handoff is understandable".
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
# `scripts/` 는 패키지가 아니다. 이 저장소의 선례를 따른다 —
# test_verify_dispatch_prompts.py:43 · test_verify_finding_citations.py:43
sys.path.insert(0, str(ROOT / "scripts"))

import wikilink_graph as wg  # noqa: E402


# ---------------------------------------------------------------------------
# 1. 파싱 — 무엇이 링크이고 무엇이 링크가 아닌가
# ---------------------------------------------------------------------------

def _links(text: str) -> list[str]:
    return [l.target for l in wg.iter_wikilinks(textwrap.dedent(text))]


def test_plain_wikilink_is_found():
    assert _links("see [[docs/HANDOFF]] here") == ["docs/HANDOFF"]


def test_alias_and_anchor_are_stripped_and_order_is_preserved():
    assert _links("[[docs/X|label]] [[docs/Y#sec]] [[docs/Z#a#b|label]]") == [
        "docs/X", "docs/Y", "docs/Z",
    ]


def test_table_escaped_pipe_leaves_no_trailing_backslash():
    # 표 셀 안 `\|` 이스케이프 — 이 저장소 HANDOFF 의 실제 형태.
    assert _links(r"| [[docs/RULING_CHAIN_INDEX\|색인]] |") == ["docs/RULING_CHAIN_INDEX"]


def test_explicit_md_suffix_is_kept_not_doubled():
    assert _links("[[docs/scior_reuse_audit.md]]") == ["docs/scior_reuse_audit.md"]


def test_leading_dot_slash_and_slash_are_normalized_to_root_relative():
    assert _links("[[./docs/A]] [[/docs/B]]") == ["docs/A", "docs/B"]


def test_target_may_contain_spaces_and_non_ascii():
    assert _links("[[docs/my note]] [[문서/설계]]") == ["docs/my note", "문서/설계"]


def test_nested_brackets_are_greedy_to_the_closing_pair():
    assert _links("[[a [b] c]]") == ["a [b] c"]


def test_wikilink_inside_a_markdown_link_label_is_still_a_link():
    # Obsidian 이 그렇게 읽는다. 무시하면 실제 링크를 놓친다.
    assert _links("[see [[docs/X]]](http://e.com)") == ["docs/X"]


def test_anchor_only_link_is_a_self_reference_not_a_link_to_report():
    assert _links("[[#section]] and [[docs/A]]") == ["docs/A"]


# --- 코드 문맥: 위양성의 주된 원천 ---------------------------------------

def test_fenced_code_block_is_not_a_link():
    text = """
    prose [[docs/A]]
    ```python
    x = [["Encoder", "Decoder"]]
    ```
    ~~~
    [[docs/ALSO_NOT]]
    ~~~
    prose [[docs/B]]
    """
    assert _links(text) == ["docs/A", "docs/B"]


def test_fence_with_language_and_trailing_space_still_opens_a_block():
    assert _links("```python  \n[[docs/NOT]]\n```\n[[docs/YES]]") == ["docs/YES"]


def test_unclosed_fence_swallows_the_rest_of_the_file():
    # 보수적으로 간다 — 닫히지 않은 펜스 뒤를 산문으로 읽으면 위양성이 난다.
    assert _links("[[docs/A]]\n```\n[[docs/NOT]]\n[[docs/ALSO_NOT]]") == ["docs/A"]


def test_indented_fence_inside_a_list_item_still_opens_a_block():
    assert _links("- item\n    ```\n    [[docs/NOT]]\n    ```\n[[docs/YES]]") == ["docs/YES"]


def test_inline_code_is_not_a_link():
    # `CLAUDE.md` 의 설명용 `[[wikilink]]` 가 여기 속한다.
    assert _links("regex `[[` and `[[wikilink]]` but [[docs/REAL]]") == ["docs/REAL"]


def test_unpaired_backtick_does_not_swallow_the_line():
    assert _links("a ` b [[docs/A]]") == ["docs/A"]


def test_quoted_or_empty_target_is_not_a_link():
    assert _links('[[]] [[ ]] [["a", "b"]]') == []


def test_crlf_line_endings_do_not_break_fences_or_line_numbers():
    text = "a\r\n```\r\n[[docs/NOT]]\r\n```\r\n[[docs/YES]]\r\n"
    assert [(l.line, l.target) for l in wg.iter_wikilinks(text)] == [(5, "docs/YES")]


def test_line_numbers_are_one_based():
    text = "a\nb [[docs/X]]\nc\n[[docs/Y]]"
    assert [(l.line, l.target) for l in wg.iter_wikilinks(text)] == [
        (2, "docs/X"), (4, "docs/Y"),
    ]


# ---------------------------------------------------------------------------
# 2. 해소 — 순서가 계약이다
# ---------------------------------------------------------------------------

@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """`docs/A.md` 와 `docs/sub/A.md` 를 **둘 다** 둔다 —
    루트 상대와 문서 상대가 서로 다른 파일로 가는 fixture 여야
    해소 순서를 실제로 구분할 수 있다."""
    (tmp_path / "docs" / "sub").mkdir(parents=True)
    (tmp_path / "docs" / "A.md").write_text("# root-relative target\n")
    (tmp_path / "docs" / "sub" / "A.md").write_text("# document-relative target\n")
    (tmp_path / "docs" / "sub" / "B.md").write_text("# B\n")
    (tmp_path / "README.md").write_text("# root\n")
    (tmp_path / "docs" / "README.md").write_text("# docs\n")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "tool.py").write_text("# not markdown\n")
    return tmp_path


def test_root_relative_is_tried_before_document_relative(repo: Path):
    """fixture 는 `docs/A.md` 와 `docs/sub/A.md` 를 **둘 다** 갖는다.
    `docs/sub/B.md` 안에서 `[[docs/A]]` 를 문서 상대로 먼저 읽으면
    `docs/sub/docs/A.md`(없음)이므로 순서를 뒤집은 구현은 여기서 걸린다."""
    r = wg.resolve(repo, repo / "docs" / "sub" / "B.md", "docs/A")
    assert r.status is wg.Status.OK
    assert r.path == repo / "docs" / "A.md"          # 루트 상대. sub/ 아래가 아니다


def test_document_relative_resolves_to_the_sibling_not_the_root_file(repo: Path):
    """반대 방향 — `[[A]]` 는 bare 이므로 basename 색인으로 가고, `A.md` 가
    두 곳이므로 AMBIGUOUS 여야 한다. 조용히 하나를 고르면 안 된다."""
    r = wg.resolve(repo, repo / "docs" / "sub" / "B.md", "A")
    assert r.status is wg.Status.AMBIGUOUS
    assert sorted(p.relative_to(repo).as_posix() for p in r.candidates) == [
        "docs/A.md", "docs/sub/A.md",
    ]


def test_document_relative_is_tried_when_root_relative_misses(repo: Path):
    r = wg.resolve(repo, repo / "docs" / "A.md", "sub/B")
    assert r.status is wg.Status.OK
    assert r.path == repo / "docs" / "sub" / "B.md"


def test_unique_bare_basename_resolves_anywhere(repo: Path):
    r = wg.resolve(repo, repo / "README.md", "B")
    assert r.status is wg.Status.OK and r.path == repo / "docs" / "sub" / "B.md"


def test_duplicate_bare_basename_is_AMBIGUOUS_not_OK(repo: Path):
    """첫 후보를 조용히 고르면 codex `resolve_links` 와 같은 결함이다.
    이 저장소는 bare basename 이 273건(80%)이라 이 판정이 게이트의 값이다."""
    r = wg.resolve(repo, repo / "docs" / "A.md", "README")
    assert r.status is wg.Status.AMBIGUOUS
    assert sorted(p.relative_to(repo).as_posix() for p in r.candidates) == [
        "README.md", "docs/README.md",
    ]


def test_path_qualified_target_does_NOT_fall_back_to_basename(repo: Path):
    """`[[sub/NOPE]]` 가 어딘가의 `NOPE.md` 로 떨어지면 경로 한정이 무의미해진다."""
    (repo / "elsewhere").mkdir()
    (repo / "elsewhere" / "NOPE.md").write_text("# decoy\n")
    r = wg.resolve(repo, repo / "docs" / "A.md", "sub/NOPE")
    assert r.status is wg.Status.DEAD


def test_own_worktree_prefix_is_stripped(repo: Path):
    """이 저장소 링크 66건이 이 형태다. 벗기지 않으면 전부 거짓 DEAD 가 된다."""
    r = wg.resolve(repo, repo / "README.md", f"{repo.name}/docs/A")
    assert r.status is wg.Status.OK and r.path == repo / "docs" / "A.md"


def test_other_worktree_prefix_is_EXTERNAL_not_DEAD(repo: Path):
    """범위 밖은 결함이 아니다. DEAD 로 보고하면 위양성이다."""
    r = wg.resolve(repo, repo / "README.md", "concept-gate-e2.2-wt/docs/X")
    assert r.status is wg.Status.EXTERNAL


def test_parent_traversal_outside_repo_is_EXTERNAL(repo: Path):
    (repo.parent / "outside.md").write_text("# out\n")
    r = wg.resolve(repo, repo / "README.md", "../outside")
    assert r.status is wg.Status.EXTERNAL


def test_missing_target_is_DEAD_with_no_candidates(repo: Path):
    r = wg.resolve(repo, repo / "README.md", "docs/NOPE")
    assert r.status is wg.Status.DEAD and list(r.candidates) == []


def test_directory_target_is_DEAD(repo: Path):
    r = wg.resolve(repo, repo / "README.md", "docs")
    assert r.status is wg.Status.DEAD


def test_existing_non_markdown_file_resolves_OK(repo: Path):
    """실재하는 파일을 가리키는 링크는 죽지 않았다. DEAD 로 보고하면 위양성이다."""
    r = wg.resolve(repo, repo / "README.md", "scripts/tool.py")
    assert r.status is wg.Status.OK and r.path == repo / "scripts" / "tool.py"


def test_symlink_escaping_the_repo_is_EXTERNAL(repo: Path):
    (repo.parent / "target.md").write_text("# out\n")
    (repo / "docs" / "escape.md").symlink_to(repo.parent / "target.md")
    r = wg.resolve(repo, repo / "README.md", "docs/escape")
    assert r.status is wg.Status.EXTERNAL


def test_case_mismatch_is_DEAD_even_on_a_case_insensitive_filesystem(repo: Path):
    """macOS 는 기본이 대소문자 비구분이다. `[[docs/a]]` 가 통과하면 다른
    기계(리눅스 CI·Render)에서만 깨진다 — 조용한 오답의 전형."""
    r = wg.resolve(repo, repo / "README.md", "docs/a")
    assert r.status is wg.Status.DEAD


# ---------------------------------------------------------------------------
# 3. 스캔
# ---------------------------------------------------------------------------

def test_scan_reports_dead_and_ambiguous_with_location(repo: Path):
    (repo / "docs" / "A.md").write_text(
        "ok [[sub/B]]\n"
        "dead [[docs/NOPE]]\n"
        "amb [[README]]\n"
        "ext [[concept-gate-owl-wt/docs/X]]\n"
        "```\n[[docs/IGNORED]]\n```\n"
    )
    r = wg.scan(repo)
    dead = [(f.source.name, f.line, f.target) for f in r.dead]
    amb = [(f.source.name, f.line, f.target) for f in r.ambiguous]
    assert ("A.md", 2, "docs/NOPE") in dead
    assert ("A.md", 3, "README") in amb
    assert not any(t == "docs/IGNORED" for _, _, t in dead)      # 코드블록
    assert not any(t.startswith("concept-gate-owl-wt") for _, _, t in dead)  # EXTERNAL


def test_total_counts_occurrences_not_distinct_targets(repo: Path):
    (repo / "docs" / "A.md").write_text("[[sub/B]] [[sub/B]]\n")
    (repo / "docs" / "README.md").write_text("")
    (repo / "README.md").write_text("")
    (repo / "docs" / "sub" / "A.md").write_text("")
    assert wg.scan(repo).total == 2


def test_scan_skips_exactly_git_and_vendor_not_all_dotdirs(repo: Path):
    """과잉 제외는 조용한 오답이다 — `.claude/` 아래 문서도 검사 대상이다."""
    (repo / ".git").mkdir(); (repo / ".git" / "x.md").write_text("[[docs/NOPE]]")
    (repo / "vendor").mkdir(); (repo / "vendor" / "y.md").write_text("[[docs/NOPE]]")
    (repo / ".claude").mkdir(); (repo / ".claude" / "z.md").write_text("[[docs/NOPE]]")
    dead = {f.source.name for f in wg.scan(repo).dead}
    assert dead == {"z.md"}


def test_findings_are_ordered_deterministically(repo: Path):
    (repo / "docs" / "A.md").write_text("[[docs/N2]]\n[[docs/N1]]\n")
    (repo / "README.md").write_text("[[docs/N0]]\n")
    keys = [(f.source.as_posix(), f.line) for f in wg.scan(repo).dead]
    assert keys == sorted(keys)


def test_finding_source_is_an_absolute_path(repo: Path):
    (repo / "docs" / "A.md").write_text("[[docs/NOPE]]\n")
    f = wg.scan(repo).dead[0]
    assert isinstance(f.source, Path) and f.source.is_absolute()


# ---------------------------------------------------------------------------
# 4. 게이트 — 실제 저장소
# ---------------------------------------------------------------------------

# 의도적 비-링크나 고칠 수 없는 것. 형식은 test_guard_negative_coverage.py 의
# KNOWN_UNPROVEN 을 따른다 — 항목마다 사유. 키는 (파일, 대상)이고 **한 파일 안의
# 같은 대상은 몇 번 나오든 한 항목**이다(test_exemption_key_ignores_line_number).
KNOWN_DEAD: dict[tuple[str, str], str] = {
    # ("docs/foo.md", "bar"): "왜 링크가 아닌가 / 왜 고칠 수 없는가"
}


def _key(f) -> tuple[str, str]:
    return (f.source.relative_to(ROOT).as_posix(), f.target)


def test_the_scanner_actually_finds_this_repo_s_links():
    """**이 테스트가 없으면 빈 리스트만 돌려주는 stub 이 아래 게이트를 전부
    통과한다.** 적대적 검증(2026-08-30, D-003 blocker)이 지적한 구멍이다.
    실측 340건 · 자기 접두 66건 기준으로 하한을 둔다."""
    r = wg.scan(ROOT)
    assert r.total >= 300, f"링크를 {r.total}건밖에 못 찾았다 — 파서가 죽었다"
    assert len({f.source for f in r.dead} | {f.source for f in r.ambiguous}) >= 0
    own = [l for l in wg.scan_links(ROOT) if l.target.startswith(f"{ROOT.name}/")]
    assert len(own) >= 60, f"자기 worktree 접두 링크 {len(own)}건 — 66건이어야 한다"
    assert all(wg.resolve(ROOT, l.source, l.target).status is wg.Status.OK for l in own)


def test_no_dead_wikilinks_in_repo():
    dead = [f for f in wg.scan(ROOT).dead if _key(f) not in KNOWN_DEAD]
    assert not dead, "죽은 wikilink:\n" + "\n".join(
        f"  {_key(f)[0]}:{f.line}  [[{f.target}]]" for f in dead
    )


def test_no_ambiguous_wikilinks_in_repo():
    amb = wg.scan(ROOT).ambiguous
    assert not amb, "모호한 wikilink — 경로를 한정하라(CLAUDE.md 규약):\n" + "\n".join(
        f"  {_key(f)[0]}:{f.line}  [[{f.target}]] → "
        + ", ".join(p.relative_to(ROOT).as_posix() for p in f.candidates)
        for f in amb
    )


def test_exemptions_are_not_stale():
    live = {_key(f) for f in wg.scan(ROOT).dead}
    stale = sorted(k for k in KNOWN_DEAD if k not in live)
    assert not stale, f"KNOWN_DEAD 에 더 이상 죽지 않은 항목: {stale}"


def test_exemptions_have_reasons():
    assert all(v.strip() for v in KNOWN_DEAD.values())


def test_exemption_key_ignores_line_number(repo: Path):
    (repo / "docs" / "A.md").write_text("[[docs/NOPE]]\nx\n[[docs/NOPE]]\n")
    keys = {(f.source.relative_to(repo).as_posix(), f.target) for f in wg.scan(repo).dead}
    assert keys == {("docs/A.md", "docs/NOPE")}
