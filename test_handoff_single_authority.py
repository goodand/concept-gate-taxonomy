"""HANDOFF 정본은 저장소당 하나 — 남은 사본은 supersede 표시를 달아야 한다.

2026-08-23 실측(zero-context handoff 평가기, evidence-evaluator canary):
독립 독자가 `vault_search`로 "현재 상태"를 물었을 때 루트 `HANDOFF.md`와
2026-08-22자 `docs/HANDOFF.md`가 **함께** 검색됐다. 후자는 40 trial 시대의
상태를 서술하고 있어서, 독자가 어느 쪽을 정본으로 읽느냐에 따라 상태·다음
행동·정지 조건이 전부 달라진다(P4 이중 정본).

경로를 지우거나 옮기면 inbound wikilink가 깨지고, 옮겨도 검색에는 여전히
걸린다 — 그래서 해법은 "제거"가 아니라 **능동 재유도**다: 사본은 남기되
첫 머리에서 자신이 superseded임을 선언하고 정본을 지목한다. 이 게이트는
그 표시가 실제로 붙어 있는지만 검사한다(규율이 아니라 기제 — CLAUDE.md
"가드를 쓰면 음성 테스트가 함께 온다" 절과 같은 이유).

불변식은 "SUPERSEDED라고 써라"가 아니라 **"루트 밖의 HANDOFF는 머리에서
자신이 현재 상태가 아님을 선언한다"**다. 이 게이트를 처음 돌렸을 때 종료된
E2.2 실험의 `HANDOFF.md`가 걸렸는데, 그 문서는 이미 머리에 "완료됨
(2026-07-24) … 기록으로 보존한다"를 달고 있었다 — 즉 불변식은 충족했고
표시 어휘가 영어 한 단어로 좁았던 것이 결함이었다. 어휘 목록을 넓힌 것은
게이트를 느슨하게 한 것이 아니다: 아래 음성 테스트가 "현재 상태처럼 읽히는
머리"를 여전히 잡는다.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 머리에서 "이건 현재 상태가 아니다"를 선언하는 표시 어휘.
NOT_CURRENT_MARKERS = ("SUPERSEDED", "완료됨", "ARCHIVED", "보존한다")
HEADER_LINES = 6


def handoff_paths(root: Path) -> list[Path]:
    """root 안에서 HANDOFF.md로 이름 붙은 파일 전부(추적 여부 무관)."""
    return sorted(p for p in root.rglob("HANDOFF.md") if ".git" not in p.parts)


def unmarked_handoff_copies(root: Path) -> list[str]:
    """루트 정본이 아닌데 supersede 표시가 없는 HANDOFF 사본의 상대경로 목록."""
    offenders = []
    for path in handoff_paths(root):
        if path.parent == root:
            continue
        header = "\n".join(path.read_text().splitlines()[:HEADER_LINES])
        upper = header.upper()
        if not any(m.upper() in upper for m in NOT_CURRENT_MARKERS):
            offenders.append(str(path.relative_to(root)))
    return offenders


def test_repo_root_has_a_handoff():
    assert (HERE / "HANDOFF.md").is_file()


def test_no_unmarked_handoff_copies_in_repo():
    assert unmarked_handoff_copies(HERE) == []


def test_gate_catches_an_unmarked_copy(tmp_path):
    """음성 테스트 — 표시 없는 사본을 심으면 반드시 잡혀야 한다."""
    (tmp_path / "HANDOFF.md").write_text("# HANDOFF — canonical\n")
    stale = tmp_path / "docs"
    stale.mkdir()
    (stale / "HANDOFF.md").write_text("# HANDOFF — 2026-08-22 상태\n\n40 trial 완료.\n")
    assert unmarked_handoff_copies(tmp_path) == ["docs/HANDOFF.md"]


def test_gate_accepts_a_marked_copy(tmp_path):
    (tmp_path / "HANDOFF.md").write_text("# HANDOFF — canonical\n")
    stale = tmp_path / "docs"
    stale.mkdir()
    (stale / "HANDOFF.md").write_text("# (SUPERSEDED) — 정본은 루트 HANDOFF.md\n")
    assert unmarked_handoff_copies(tmp_path) == []


def test_marker_must_be_in_the_header_not_buried(tmp_path):
    """표시가 문서 끝에 묻혀 있으면 독자를 재유도하지 못한다 — 잡아야 한다."""
    (tmp_path / "HANDOFF.md").write_text("# HANDOFF — canonical\n")
    stale = tmp_path / "docs"
    stale.mkdir()
    (stale / "HANDOFF.md").write_text(
        "# HANDOFF — 2026-08-22 상태\n" + "본문\n" * 30 + "이 문서는 SUPERSEDED다.\n"
    )
    assert unmarked_handoff_copies(tmp_path) == ["docs/HANDOFF.md"]


def test_gate_still_catches_a_header_that_reads_as_current(tmp_path):
    """어휘를 넓혀도 '현재 상태'처럼 읽히는 머리는 잡혀야 한다(공허화 방지)."""
    (tmp_path / "HANDOFF.md").write_text("# HANDOFF — canonical\n")
    stale = tmp_path / "experiments" / "old"
    stale.mkdir(parents=True)
    (stale / "HANDOFF.md").write_text(
        "# HANDOFF — 현재 상태\n\n- 갱신: 2026-08-22\n- 다음 행동: 코호트 실행\n"
    )
    assert unmarked_handoff_copies(tmp_path) == ["experiments/old/HANDOFF.md"]
