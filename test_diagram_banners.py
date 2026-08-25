"""제안 다이어그램이 as-built로 오독되는 것을 막는 게이트.

## 왜 삭제가 아니라 표기인가 (그리고 왜 표기에 게이트가 붙는가)

2026-08-24, 사용자 질문: "채택되지 않은 것을 지우는 것과 남겨두는 것 중에
오용 방지에 무엇이 더 유리한가."

이 저장소의 실측이 답을 갖고 있다.

- **P21** — 실제 피해 사례. legacy 스크립트를 재사용하자고 추천했고 어디에도
  "죽었다"고 적혀 있지 않았다. `test_legacy_register.py`의 결론:
  "실제 피해는 잘못된 재사용이고 그것을 막는 것은 삭제가 아니라 표기다."
- **등록부 불변식 3** — 후계자를 못 적으면 legacy가 아니라 **미결정**이다.
  `diagrams/`의 제안들은 채택되지 않았을 뿐 대체된 것이 아니므로 후계자가
  없고, 따라서 삭제 대상 자격이 안 선다.
- **재발명 위험** — 지우면 "같은 설계를 모르고 다시 만든다"가 되고, 그것은
  `CLAUDE.md`의 "'아직 안 풀렸다'고 단정하지 마라" 절이 막으려는 실패이며
  이 워크스페이스에서 **실측 2회** 일어났다. 삭제는 라벨링 위험을 재발명
  위험으로 교환하는데, 대가를 치른 쪽은 후자다.

**그러나 표기가 관습이면 드리프트한다.** P1이 7/7 실패한 뒤 이 저장소가
`test_guard_negative_coverage.py`로 기제화한 것과 같은 이유로, 표기가
삭제를 대신하는 기제라면 그 표기에 게이트가 붙어야 한다.

## 왜 등록부의 배너 토큰을 쓰지 않는가

`docs/LEGACY_REGISTER.md`의 배너 토큰은 **후계자가 있는** 것에 쓴다
(불변식 3). 제안들은 후계자가 없으므로 그것을 쓰면 등록부 의미론과 충돌하고,
등록부 게이트는 `.mmd`를 수집하지 않으므로 **조용한 불일치**가 남는다.
그래서 별 토큰을 쓴다.

**이 문단을 처음 쓸 때 그 토큰을 문자 그대로 인용했고 등록부 게이트가
곧바로 실패했다** — 루트 `*.py`가 그 게이트의 검색 범위이기 때문이다.
`docs/H1A_PROBLEM_ANALYSIS.md` §19.3이 기록한 재귀적 실패와 같은 형태다
(결함을 서술하면서 그 결함을 다시 저지른다). 토큰을 이름으로만 부른다.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
DIAGRAM_DIRS = ("diagrams",)
HEADER_LINES = 10

# 두 토큰만 인정한다. 셋 이상이면 무엇이 as-built인지가 다시 불분명해진다.
PROPOSAL = re.compile(r"\[PROPOSAL — NOT AS-BUILT\]")
ASIS = re.compile(r"\[AS-IS — \d{4}-\d{2}-\d{2} 시점\]")


def _diagram_sources() -> list[Path]:
    out: list[Path] = []
    for d in DIAGRAM_DIRS:
        out.extend(sorted((ROOT / d).glob("*.mmd")))
    return out


def _header(p: Path) -> str:
    return "\n".join(p.read_text(encoding="utf-8").splitlines()[:HEADER_LINES])


def test_the_scan_finds_diagrams():
    """음성 — 대상 0건이면 아래 검사가 자명하게 통과한다."""
    assert _diagram_sources(), (
        f"{DIAGRAM_DIRS}에서 .mmd를 하나도 못 찾았다 — 경로가 바뀌었으면 "
        "DIAGRAM_DIRS를 고쳐라. 대상 0건인 게이트는 아무것도 지키지 않는다")


@pytest.mark.parametrize("p", _diagram_sources(), ids=lambda p: p.name)
def test_every_diagram_declares_proposal_or_as_is(p):
    """grep으로 이 파일을 만난 사람이 첫 화면에서 지위를 알 수 있어야 한다.

    별도 README는 읽히지 않는다 — 그것이 P21의 형태였다.
    """
    h = _header(p)
    assert PROPOSAL.search(h) or ASIS.search(h), (
        f"{p.name}: 상단 {HEADER_LINES}행에 지위 표기가 없다. "
        "[PROPOSAL — NOT AS-BUILT] 또는 [AS-IS — YYYY-MM-DD 시점] 중 하나를 "
        "넣어라 — 표기 없는 다이어그램은 as-built로 읽힌다")


@pytest.mark.parametrize("p", _diagram_sources(), ids=lambda p: p.name)
def test_no_diagram_claims_both(p):
    """둘 다 붙으면 지위가 다시 불분명하다."""
    h = _header(p)
    assert not (PROPOSAL.search(h) and ASIS.search(h)), (
        f"{p.name}: PROPOSAL과 AS-IS를 동시에 주장한다")


@pytest.mark.parametrize("p", _diagram_sources(), ids=lambda p: p.name)
def test_the_banner_does_not_break_rendering(p):
    """표기가 렌더를 깨면 다음 사람이 표기를 지운다 — 그러면 게이트도 죽는다."""
    body = [l for l in p.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.strip().startswith("%%")]
    assert body, f"{p.name}: 주석을 걷으면 내용이 없다"
    assert body[0].strip().startswith(
        ("flowchart", "graph", "sequenceDiagram", "classDiagram",
         "stateDiagram", "erDiagram", "journey", "gantt", "pie")), (
        f"{p.name}: 첫 비주석 행이 다이어그램 선언이 아니다 — {body[0][:40]!r}")


def test_the_directory_has_a_readme_stating_the_measurement():
    """배너는 근거를 가리킨다 — 그 근거가 실재해야 한다(거짓 포인터 금지)."""
    for d in DIAGRAM_DIRS:
        readme = ROOT / d / "README.md"
        assert readme.exists(), f"{d}/README.md가 없는데 배너가 그것을 가리킨다"
        t = readme.read_text(encoding="utf-8")
        for token in ("classify_facts", "thin_signal", "as-built"):
            assert token in t, f"{d}/README.md에 {token}이 없다"


# ───────────────────────── pytest 수집 범위 고정 (2026-08-25) ─────────────────
# `norecursedirs` 에서 `.claude` 를 빼면, Claude Code 가 만든 중첩 worktree
# (`.claude/worktrees/<name>/`)의 테스트가 이 브랜치 suite 로 수집되고 같은
# 이름의 `conceptgate` 패키지가 sys.modules 를 선점한다 — 이쪽 테스트가 저쪽
# 코드를 검사하게 된다.
#
# 실측(trunk worktree, 2026-08-25): 수집 250개 중 119개가 다른 브랜치 것.
# 같은 테스트가 단독 48 passed / 전체 수집 11 failed.
#
# 이 저장소는 `experiments` 를 같은 이유로 이미 제외하고 있다. 목록이 조용히
# 줄어들면 그 사고가 돌아오므로 여기서 고정한다.

def test_pytest_excludes_nested_worktrees_from_collection():
    import configparser
    ini = Path(__file__).resolve().parent / "pytest.ini"
    cfg = configparser.ConfigParser()
    cfg.read(ini, encoding="utf-8")
    dirs = cfg["pytest"]["norecursedirs"].split()
    for required in (".claude", "experiments", "vendor"):
        assert required in dirs, (
            f"norecursedirs 에서 {required!r} 가 빠졌다. "
            f"{'중첩 worktree' if required == '.claude' else required} 를 수집하면 "
            "같은 이름의 패키지가 sys.modules 를 선점해 남의 코드로 테스트가 돈다")


def test_the_exclusion_reason_is_written_next_to_it():
    """이유 없는 제외 목록은 다음 사람이 지운다."""
    t = (Path(__file__).resolve().parent / "pytest.ini").read_text(encoding="utf-8")
    assert "sys.modules" in t, "왜 제외하는지가 pytest.ini 에 없다"
    assert "worktree" in t, "`.claude` 제외의 대상이 무엇인지 적혀 있지 않다"
