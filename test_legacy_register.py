"""LEGACY 등록부가 거짓말하지 못하게 하는 게이트.

## 무엇을 막는가

운영 세션이 `scripts/handoff_reachability.py`를 backlink 게이트로 **재사용
하자고 추천했다**(2026-08-24). 그 파일은 이미 legacy였고 목적에 맞는 MCP
도구가 따로 있었는데 어디에도 "죽었다"고 적혀 있지 않았다 — P21. 사용자
지적으로 멈췄다.

디스크 공간은 이 저장소의 문제였던 적이 없다(정리 3라운드 누계 삭제 6파일).
**실제 피해는 잘못된 재사용**이고 그것을 막는 것은 삭제가 아니라 표기다.
그런데 표기와 등록부는 **드리프트한다** — 그래서 기제로 내린다.

## 네 가지 불변식

1. 등록된 `path`는 실재한다 (`REMOVED`만 예외, 그때는 복구 명령 필수)
2. 파일에 `LEGACY` 표기를 넣었으면 등록부에 행이 있다
3. 모든 행에 `superseded_by`가 있다 — **후계자를 못 적으면 legacy가 아니라
   미결정이다.** P21의 원인이 정확히 이것이었다("쓰지 마라"는 알았어도
   "대신 무엇을"이 없었다)
4. 등록부는 비어 있지 않다 (게이트 공허화 방지)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
REGISTER = ROOT / "docs" / "LEGACY_REGISTER.md"

# 등록부 본문의 표 행: | `path` | 무엇 | superseded_by | status | 사유 |
_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|([^|]*)\|([^|]*)\|\s*([A-Z_]+)\s*\|(.*)\|\s*$")
STATUSES = {"RETAINED", "REMOVED", "REMOVABLE"}

# 표기를 찾을 범위 — 소스 트리만. 실험 폴더의 동결 사본은 제외하지 않는다
# (거기에 표기를 넣었다면 그것도 등록돼야 한다).
SEARCH_GLOBS = ("*.py", "scripts/*.py", "conceptgate/*.py", "docs/*.md")
HEADER_LINES = 40   # "상단"의 정의 — 파일 본문 깊숙한 언급은 표기가 아니다
MARKER = re.compile(r"\bLEGACY\b")


def _rows() -> list[tuple[str, str, str, str]]:
    """(path, superseded_by, status, 사유) — '등록부' 절의 표만 읽는다."""
    text = REGISTER.read_text(encoding="utf-8")
    start = text.index("## 등록부")
    end = text.index("## 명시적 **비**-legacy", start)
    out = []
    for line in text[start:end].splitlines():
        m = _ROW.match(line)
        if m:
            out.append((m.group(1).strip(), m.group(3).strip(),
                        m.group(4).strip(), m.group(5).strip()))
    return out


def test_register_exists_and_is_not_empty():
    """불변식 4 — 이 게이트가 공허해지는 유일한 경로를 막는다."""
    assert REGISTER.exists()
    assert len(_rows()) >= 5


def test_every_status_is_from_the_closed_vocabulary():
    for path, _, status, _ in _rows():
        assert status in STATUSES, (path, status)


@pytest.mark.parametrize("row", _rows(), ids=lambda r: r[0])
def test_registered_path_exists_unless_removed(row):
    """불변식 1 — 등록부가 없는 파일을 가리키면 그것은 낡은 지도다."""
    path, _, status, reason = row
    if status == "REMOVED":
        assert "git show" in reason or "복구" in reason, (
            f"{path}: REMOVED인데 복구 방법이 없다 — 되돌릴 수 없는 기록은 "
            "legacy 표기가 아니라 소실이다")
        return
    assert (ROOT / path).exists(), (
        f"{path}: 등록됐지만 실재하지 않는다. 지웠다면 status를 REMOVED로 "
        "바꾸고 복구 명령을 적어라")


@pytest.mark.parametrize("row", _rows(), ids=lambda r: r[0])
def test_every_row_names_its_successor(row):
    """불변식 3 — 후계자 없는 legacy는 P21을 재발시킨다."""
    path, superseded_by, _, _ = row
    assert superseded_by and superseded_by not in ("-", "—", "없음"), (
        f"{path}: superseded_by가 비어 있다. 대신 무엇을 쓰는지 못 적으면 "
        "이것은 legacy가 아니라 미결정이다")


def _files_with_marker() -> list[Path]:
    # 자기참조 배제: 이 게이트와 등록부 자신은 검색 대상이 아니다. 둘 다
    # 제목·본문에 LEGACY를 쓰므로 포함하면 게이트가 스스로를 신고한다
    # (첫 실행이 실제로 그랬다 — 배제 원장 게이트에서 겪은 것과 같은 부류).
    excluded = {Path(__file__).resolve(), REGISTER.resolve()}
    seen: set[Path] = set()
    for pattern in SEARCH_GLOBS:
        for p in ROOT.glob(pattern):
            if p.is_file() and p.resolve() not in excluded:
                seen.add(p)
    hits = []
    for p in sorted(seen):
        try:
            head = "\n".join(p.read_text(encoding="utf-8").splitlines()[:HEADER_LINES])
        except (UnicodeDecodeError, OSError):
            continue
        if MARKER.search(head):
            hits.append(p)
    return hits


def test_marked_files_are_registered():
    """불변식 2 — 표기만 있고 등록이 없으면 grep으로만 발견된다."""
    registered = {r[0] for r in _rows()}
    missing = [str(p.relative_to(ROOT)) for p in _files_with_marker()
               if str(p.relative_to(ROOT)) not in registered]
    assert not missing, (
        f"파일 상단에 LEGACY 표기가 있으나 등록부에 없다: {missing}. "
        "표기와 등록부는 함께 고친다")


def test_the_marker_search_is_not_vacuous():
    """음성 테스트 — 위 검사가 대상 0건이어서 통과하는 것이 아님을 보인다."""
    assert _files_with_marker(), (
        "LEGACY 표기가 있는 파일이 하나도 없다 — 표기 규약이 실제로 쓰이지 "
        "않으면 test_marked_files_are_registered는 자명하게 통과한다")


def test_non_legacy_section_names_what_would_break():
    """이름 때문에 legacy로 오해되는 것들이 사유와 함께 적혀 있는가.

    `_stage2_scope_projection.py`(V1인데 V2 채점의 전처리)와
    `freeze_stage2.py`(V1인데 SEED·층 술어의 정본)를 지우면 조용히 깨진다.
    """
    text = REGISTER.read_text(encoding="utf-8")
    section = text[text.index("## 명시적 **비**-legacy"):]
    for must in ("_stage2_scope_projection.py", "freeze_stage2.py",
                 ".oracle_cache", "vendor/"):
        assert must in section, f"비-legacy 절에 {must}가 없다"
