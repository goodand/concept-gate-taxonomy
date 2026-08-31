"""`scripts/compaction_ledger.py` 계약 — 시점을 기억이 아니라 측정으로.

## 왜 이 계약이 이 형태인가

손으로 적은 ledger 가 **세 가지로 동시에 틀렸다**(2026-08-31 실측): 시각 열에
파일 mtime 을 적었고, 횟수를 "여러 회"로 지어냈고, 12건 중 3건만 적었다.
그래서 이 도구의 계약은 **"기록에 있는 것만, 있는 그대로"** 다.

## 프로토콜 8단(Sonnet 구현 위임) PASS 사유

이 산출물은 **읽기 전용 보고 도구**이고 계약과 구현이 100행 남짓으로 분리 위임할
크기가 아니다. 7단(적대검증)은 별도로 돌린다 — 그쪽이 "다른 눈"을 담당한다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "scripts"))

import compaction_ledger as cl  # noqa: E402


def _write(tmp_path: Path, *objs: dict) -> Path:
    p = tmp_path / "t.jsonl"
    p.write_text("\n".join(json.dumps(o, ensure_ascii=False) for o in objs) + "\n",
                 encoding="utf-8")
    return p


def _boundary(ts: str, trigger: str = "auto", pre: int | None = 1000) -> dict:
    meta: dict = {"trigger": trigger}
    if pre is not None:
        meta["preTokens"] = pre
    return {"type": "system", "subtype": "compact_boundary",
            "timestamp": ts, "compactMetadata": meta}


# ---------------------------------------------------------------------------
# 추출
# ---------------------------------------------------------------------------

def test_it_finds_a_boundary(tmp_path):
    p = _write(tmp_path, _boundary("2026-08-30T16:49:09.123Z", "auto", 1007652))
    got = list(cl.iter_boundaries(p))
    assert [(b.timestamp, b.trigger, b.pre_tokens) for b in got] \
        == [("2026-08-30T16:49:09", "auto", 1007652)]


def test_it_keeps_file_order(tmp_path):
    p = _write(tmp_path, _boundary("2026-07-29T11:32:22Z", "manual"),
                         _boundary("2026-08-30T16:49:09Z", "auto"))
    assert [b.timestamp[:10] for b in cl.iter_boundaries(p)] \
        == ["2026-07-29", "2026-08-30"]


def test_a_line_merely_mentioning_the_word_is_not_a_boundary(tmp_path):
    """값싼 사전 필터가 `compact_boundary` 문자열로 거르는데, **그 뒤에 구조
    검사가 와야 한다.** 대화 안에서 그 단어를 말한 줄이 경계로 세어지면
    이 도구가 자기 문서를 세는 꼴이 된다."""
    p = _write(tmp_path,
               {"type": "assistant", "message": {"content": "compact_boundary 를 설명한다"}},
               _boundary("2026-08-30T16:49:09Z"))
    assert len(list(cl.iter_boundaries(p))) == 1


def test_a_system_line_of_another_subtype_is_not_a_boundary(tmp_path):
    p = _write(tmp_path,
               {"type": "system", "subtype": "turn_duration",
                "timestamp": "2026-08-30T16:00:00Z", "compactMetadata": {"trigger": "auto"}},
               _boundary("2026-08-30T16:49:09Z"))
    assert len(list(cl.iter_boundaries(p))) == 1


def test_missing_metadata_does_not_crash(tmp_path):
    """`compactMetadata` 가 없거나 `preTokens` 가 빠진 기록이 있을 수 있다.
    없는 것을 0 으로 적으면 **거짓이 된다** — `None` 으로 남기고 표에 `—`."""
    p = _write(tmp_path, {"type": "system", "subtype": "compact_boundary",
                          "timestamp": "2026-08-30T16:49:09Z"})
    (b,) = cl.iter_boundaries(p)
    assert (b.trigger, b.pre_tokens) == ("?", None)
    assert "—" in cl.render([b])


# ---------------------------------------------------------------------------
# 잔여 — 못 읽은 것을 센다
# ---------------------------------------------------------------------------

def test_a_broken_line_is_counted_not_swallowed(tmp_path):
    """깨진 줄을 조용히 버리면 "경계 0건"과 "못 읽었다"가 구별되지 않는다 —
    그것이 전임 도구 `handoff_reachability.py` 의 제거 사유였다."""
    p = tmp_path / "t.jsonl"
    p.write_text('{"subtype":"compact_boundary" 깨짐\n'
                 + json.dumps(_boundary("2026-08-30T16:49:09Z")) + "\n",
                 encoding="utf-8")
    stats = cl.read_stats(p)
    assert stats["unparsed"] == 1 and stats["boundaries"] == 1


def test_the_warning_appears_when_lines_are_unreadable(tmp_path, capsys):
    p = tmp_path / "t.jsonl"
    p.write_text('{"subtype":"compact_boundary" 깨짐\n', encoding="utf-8")
    cl.main([str(p)])
    assert "경고" in capsys.readouterr().out


def test_a_clean_file_prints_no_warning(tmp_path, capsys):
    cl.main([str(_write(tmp_path, _boundary("2026-08-30T16:49:09Z")))])
    assert "경고" not in capsys.readouterr().out


# ---------------------------------------------------------------------------
# 출력·인자
# ---------------------------------------------------------------------------

def test_since_filters_but_the_total_still_reports_all(tmp_path, capsys):
    """`--since` 는 **표시**를 줄이지 총계를 줄이지 않는다. 범위를 좁히고
    목록을 완전한 것처럼 보고하는 것이 이 워크스페이스의 반복 결함이다."""
    p = _write(tmp_path, _boundary("2026-07-29T11:32:22Z"),
                         _boundary("2026-08-30T16:49:09Z"))
    cl.main([str(p), "--since", "2026-08-01"])
    out = capsys.readouterr().out
    assert "2026-08-30" in out and "2026-07-29" not in out
    assert "경계 2건" in out and "표시 1건" in out


def test_a_missing_file_is_an_error_not_an_empty_report(tmp_path, capsys):
    """없는 파일에 대해 "경계 0건"을 내면 **부재와 미확인이 섞인다.**"""
    assert cl.main([str(tmp_path / "nope.jsonl")]) == 2
    assert "없다" in capsys.readouterr().out


def test_since_rejects_a_malformed_date(tmp_path, capsys):
    """적대검증 blocker(2026-08-31). `--since 2026-8-1` 은 사전식 비교에서
    `"2026-08-01" >= "2026-8-1"` 이 **False** 라 모든 경계를 조용히 제외하고,
    빈 표가 "경계가 없다"로 읽힌다. 형식을 강제해 그 침묵을 없앤다."""
    p = _write(tmp_path, _boundary("2026-08-01T12:00:00Z"))
    assert cl.main([str(p), "--since", "2026-8-1"]) == 2
    assert "YYYY-MM-DD" in capsys.readouterr().out


def test_a_single_scan_backs_both_the_list_and_the_stats(tmp_path):
    """적대검증 major. 두 번 읽으면 그 사이에 기록이 자라(세션 진행 중) 총계와
    통계가 어긋난다 — 같은 실행이 서로 다른 파일을 본 셈이 된다."""
    p = _write(tmp_path, _boundary("2026-08-30T16:49:09Z"))
    found, stats = cl.scan(p)
    assert len(found) == stats["boundaries"] == 1


def test_utc_and_local_are_both_reported(tmp_path):
    """적대검증 minor → 실제로는 내 해석을 틀리게 만든 원인이었다. 기록은 UTC
    이고 파일 mtime·사람의 시계는 로컬이라, 하나만 남기면 9시간 어긋난 해석이
    나온다(2026-08-31 에 실제로 그렇게 틀렸다)."""
    (b,) = cl.iter_boundaries(_write(tmp_path, _boundary("2026-08-30T16:49:09Z")))
    assert b.timestamp == "2026-08-30T16:49:09"
    assert b.local and b.local != b.timestamp
    assert "기록(UTC)" in cl.render([b]) and "로컬" in cl.render([b])


def test_an_unparsable_timestamp_yields_no_guessed_local(tmp_path):
    """시간대는 지어낼 수 있는 종류의 값이 아니다 — 못 읽으면 빈칸."""
    p = _write(tmp_path, {"type": "system", "subtype": "compact_boundary",
                          "timestamp": "언제인지 모름", "compactMetadata": {}})
    (b,) = cl.iter_boundaries(p)
    assert b.local == "" and "—" in cl.render([b])
