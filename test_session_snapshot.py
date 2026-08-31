"""`scripts/session_snapshot.py` 계약 — compaction 이 잃는 것만, 생성으로.

## 무엇을 푸는가

`HANDOFF.md` 는 **프로젝트 상태**를 담고 손으로 유지한다(§0 상태 블록 · §3 다음
실행 절차 · §7 compaction ledger). 그런데 compaction 이 잃는 것은 그것이 아니다:

    HANDOFF 가 담는 것        프로젝트가 어디까지 왔나 · 다음에 무엇을 하나
    compaction 이 잃는 것      **지금 진행 중인 것** · **이미 잰 사실**

두 번째가 특히 비싸다. 2026-08-31 에 같은 것을 다른 정규식으로 두 번 재서 다른
답을 얻었다(G213: 손 측정이 `C-P7` 을 `P7` 로 오탐, 게이트 규칙을 썼으면 0건).
**재측정은 낭비가 아니라 위험이다** — 방법이 달라지면 답이 달라진다.

## 왜 손으로 쓰지 않는가

`pre_compact.md` 를 손으로 유지하면 `HANDOFF` 갱신일이 8일 낡았던 것(P4 14회차)과
같은 일이 난다. 그리고 compaction 은 **자동 유발**(실측 12건 중 9건이 `auto`)이라
"쓸 시점"을 사람이 고를 수 없다.

그래서 **생성**한다. 방금 성문화한 어휘대로 — authoritative 출처(git · 세션 기록 ·
`HANDOFF.md`)에서 뽑고, **이 스냅샷 자신은 advisory 다.** 스냅샷이 정본과 어긋나면
정본이 이긴다.

## 무엇을 담지 않는가

- **정본이 이미 담는 것을 복사하지 않는다.** `state_code`·`next_action_code` 는
  **가리키기만** 한다 — 복사하면 두 벌이 되고 갈라진다(G199·G213).
- **판단을 담지 않는다.** "다음에 무엇을 해야 한다"는 `HANDOFF` §3 의 일이다.

## 프로토콜 8단(Sonnet 구현 위임) PASS 사유

읽기 전용 보고 도구이고 계약과 구현이 분리 위임할 크기가 아니다(`compaction_ledger`
와 같은 판단). 7단 적대검증은 별도로 돌린다.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "scripts"))

import session_snapshot as ss  # noqa: E402


def _git(tmp_path: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=tmp_path, check=True,
                   capture_output=True, text=True)


def _repo(tmp_path: Path) -> Path:
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.email", "t@t")
    _git(tmp_path, "config", "user.name", "t")
    (tmp_path / "a.txt").write_text("x\n")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-qm", "first")
    return tmp_path


# ---------------------------------------------------------------------------
# 진행 중 상태 — compaction 이 잃는 절반
# ---------------------------------------------------------------------------

def test_a_clean_tree_reports_nothing_in_flight(tmp_path):
    assert ss.in_flight(_repo(tmp_path)) == []


def test_an_uncommitted_change_is_in_flight(tmp_path):
    r = _repo(tmp_path)
    (r / "a.txt").write_text("changed\n")
    assert [c.path for c in ss.in_flight(r)] == ["a.txt"]


def test_an_untracked_file_is_in_flight(tmp_path):
    """미추적 파일이 진행 중 목록에서 빠지면, compaction 뒤에 **만들다 만 것**이
    안 보인다 — 이 도구가 존재하는 이유의 절반이 그것이다."""
    r = _repo(tmp_path)
    (r / "새것.py").write_text("x\n")
    assert [c.path for c in ss.in_flight(r)] == ["새것.py"]


def test_in_flight_carries_the_status_code(tmp_path):
    r = _repo(tmp_path)
    (r / "a.txt").write_text("changed\n")
    (r / "b.txt").write_text("new\n")
    codes = {c.path: c.code for c in ss.in_flight(r)}
    assert codes["a.txt"] == " M" and codes["b.txt"] == "??"


# ---------------------------------------------------------------------------
# 정본을 가리키기만 한다 — 복사하지 않는다
# ---------------------------------------------------------------------------

def test_it_points_at_the_handoff_codes_without_copying_prose(tmp_path):
    """`state_code`·`next_action_code` 의 **코드만** 싣고 뒤따르는 산문 설명은
    싣지 않는다. 산문을 복사하면 두 벌이 되고 정본이 바뀔 때 갈라진다."""
    (tmp_path / "HANDOFF.md").write_text(
        "```yaml\n"
        "updated: 2026-08-31\n"
        "state_code: SOME_STATE   # 긴 산문 설명이 뒤에 붙는다\n"
        "next_action_code: SOME_ACTION   # 여기에도 붙는다\n"
        "```\n", encoding="utf-8")
    got = ss.handoff_pointer(tmp_path)
    assert got == {"updated": "2026-08-31",
                   "state_code": "SOME_STATE",
                   "next_action_code": "SOME_ACTION"}


def test_a_missing_handoff_is_reported_not_guessed(tmp_path):
    """없는 것을 빈 문자열로 채우면 "없다"와 "못 읽었다"가 섞인다."""
    assert ss.handoff_pointer(tmp_path) is None


# ---------------------------------------------------------------------------
# 렌더 — advisory 임을 문서가 스스로 말한다
# ---------------------------------------------------------------------------

def test_the_render_declares_itself_advisory(tmp_path):
    """스냅샷이 정본처럼 읽히면 다음 세션이 이것을 근거로 판단한다. **문서가
    자기 지위를 말해야** 한다 — 오늘 성문화한 authoritative/advisory 경계."""
    out = ss.render(ss.snapshot(_repo(tmp_path)))
    assert "advisory" in out and "정본" in out


def test_the_render_names_its_sources(tmp_path):
    """무엇에서 뽑았는지 없으면 재현할 수 없고, 재현할 수 없으면 검증할 수 없다."""
    out = ss.render(ss.snapshot(_repo(tmp_path)))
    assert "git" in out and "HANDOFF" in out


def test_the_render_shows_in_flight_paths(tmp_path):
    r = _repo(tmp_path)
    (r / "진행중.py").write_text("x\n")
    assert "진행중.py" in ss.render(ss.snapshot(r))


def test_a_clean_tree_says_so_explicitly(tmp_path):
    """빈 목록을 빈칸으로 두면 "없다"와 "안 쟀다"가 구별되지 않는다."""
    assert "없음" in ss.render(ss.snapshot(_repo(tmp_path)))


# ---------------------------------------------------------------------------
# 실패를 감추지 않는다
# ---------------------------------------------------------------------------

def test_a_non_repo_directory_is_an_error_not_an_empty_report(tmp_path):
    """git 저장소가 아닌 곳에서 "진행 중 없음"을 내면 **거짓**이다."""
    assert ss.main([str(tmp_path)]) == 2


def test_main_succeeds_on_a_repo(tmp_path, capsys):
    assert ss.main([str(_repo(tmp_path))]) == 0
    assert "advisory" in capsys.readouterr().out
