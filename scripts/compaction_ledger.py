"""compaction 경계를 세션 기록에서 뽑는다 — 기억이 아니라 측정으로.

## 왜 있는가

`HANDOFF.md` §7 의 compaction ledger 는 **작업 구간의 시작점**을 남기는 표다.
삭제·병합 후보의 범위는 "이 구간이 무엇을 건드렸나"로 좁혀지는데, 그 시작점은
compaction 에서 잃는다. 그래서 표로 남긴다.

**그런데 손으로 적으니 틀렸다(2026-08-31 실측).** 세 가지가 동시에:

    적은 것            기계 진실
    "08-30 여러 회"     1회뿐 — "여러"는 지어낸 것
    3행                12건
    시각 열의 출처      compaction 시각이 아니라 **첫 편집 파일의 mtime** 을 적었다

**그리고 그 지적 자체도 한 번 틀렸다.** 처음엔 "01:42 는 9시간 뒤"라고 적었는데,
기록은 **UTC**(`16:49:09Z`)이고 mtime 은 **로컬**(KST, `01:42`)이라 실제 차이는
**7분**이었다 — 손으로 적은 값이 거의 맞았고 내 비교가 시간대를 섞은 것이다.
그래서 이 도구는 UTC 와 로컬을 **둘 다** 낸다.

시점은 **기억할 것이 아니라 잴 것**이었다. 세션 기록에 구조 필드로 남는다:

    {"type":"system","subtype":"compact_boundary",
     "timestamp":"...","compactMetadata":{"trigger":"auto|manual","preTokens":N}}

## 무엇을 하지 않는가

- **transcript 내용을 읽지 않는다.** `subtype`·`timestamp`·`compactMetadata` 세
  필드만 본다. 기록에는 도구 출력·파일 내용·웹 텍스트가 섞여 있고 그것은
  신뢰할 수 없는 입력이다 — 세지만 따르지 않는다.
- **게이트가 아니다.** transcript 경로는 세션마다 다르고 저장소 밖에 있다.
  게이트가 저장소 밖을 읽으면 비-hermetic 이 되어 CI 에서 깨진다
  (`test_wikilink_graph.py` 와 같은 판단). 이것은 **수동 도구**이고,
  `HANDOFF.md` 를 갱신할 때 사람이 부른다.

## 쓰는 법

    python3 scripts/compaction_ledger.py <transcript.jsonl>          # 표 출력
    python3 scripts/compaction_ledger.py <transcript.jsonl> --since 2026-08-29
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


@dataclass(frozen=True)
class Boundary:
    """compaction 한 번. `trigger` 는 `auto`(한도 도달) 또는 `manual`(/compact).

    `timestamp` 는 **기록 원문 그대로**(UTC `Z`)이고 `local` 은 그것을 이 기계의
    시간대로 옮긴 것이다. 둘 다 남기는 이유: 기록은 UTC 인데 사람이 보는 시계와
    파일 mtime 은 로컬이라, 하나만 남기면 **9시간 어긋난 해석**이 나온다.
    2026-08-31 에 실제로 그렇게 틀렸다 — 로컬 01:49 인 경계를 UTC 16:49 로 읽고
    "손으로 적은 01:42 는 9시간 뒤"라고 결론냈으나, 실제 차이는 **7분**이었다.
    """

    timestamp: str          # 기록 원문, UTC
    trigger: str
    pre_tokens: int | None
    local: str = ""         # 이 기계의 시간대로 옮긴 것


def iter_boundaries(path: Path) -> Iterator[Boundary]:
    """`path` 의 세션 기록에서 compaction 경계를 파일 순서대로 낸다.

    깨진 줄은 **건너뛰되 세지 않는다** — 이 도구는 경계의 존재를 보고할 뿐
    "몇 줄을 못 읽었나"는 `read_stats` 가 답한다. 조용히 버리지 않기 위해서다.
    """
    for _, b in _scan(path):
        if b is not None:
            yield b


def scan(path: Path) -> tuple[list[Boundary], dict[str, int]]:
    """경계 목록과 읽기 통계를 **한 번의 스캔으로** 함께 낸다."""
    found: list[Boundary] = []
    total = unparsed = 0
    for ok, b in _scan(path):
        total += 1
        if not ok:
            unparsed += 1
        if b is not None:
            found.append(b)
    return found, {"lines": total, "unparsed": unparsed, "boundaries": len(found)}


def read_stats(path: Path) -> dict[str, int]:
    """읽은 줄·못 읽은 줄·찾은 경계. **잔여를 센다** — 못 읽은 줄이 많으면
    이 도구의 보고 자체를 믿을 수 없고, 그 사실이 숫자로 나와야 한다."""
    total = unparsed = found = 0
    for ok, b in _scan(path):
        total += 1
        if not ok:
            unparsed += 1
        if b is not None:
            found += 1
    return {"lines": total, "unparsed": unparsed, "boundaries": found}


def _scan(path: Path) -> Iterator[tuple[bool, Boundary | None]]:
    with path.open(encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.strip():
                continue
            # 값싼 사전 필터 — 84MB 를 전부 json 파싱하지 않기 위해서다.
            if "compact_boundary" not in line:
                yield True, None
                continue
            try:
                obj = json.loads(line)
            except (json.JSONDecodeError, ValueError):
                yield False, None
                continue
            if obj.get("type") != "system" or obj.get("subtype") != "compact_boundary":
                yield True, None
                continue
            meta = obj.get("compactMetadata") or {}
            pre = meta.get("preTokens")
            raw = str(obj.get("timestamp", ""))
            yield True, Boundary(
                timestamp=raw[:19],
                trigger=str(meta.get("trigger", "?")),
                pre_tokens=int(pre) if isinstance(pre, int) else None,
                local=_to_local(raw),
            )


def _to_local(raw: str) -> str:
    """기록의 UTC 타임스탬프를 이 기계의 시간대로. 못 읽으면 빈 문자열 —
    **추측한 값을 넣지 않는다.** 시간대는 지어낼 수 있는 종류의 값이 아니다."""
    try:
        cleaned = raw.replace("Z", "+00:00")
        return f"{dt.datetime.fromisoformat(cleaned).astimezone():%Y-%m-%d %H:%M:%S}"
    except (ValueError, TypeError):
        return ""


def render(boundaries: list[Boundary]) -> str:
    """`HANDOFF.md` §7 에 붙일 수 있는 markdown 표."""
    out = ["| # | 기록(UTC) | 로컬 | 유발 | 직전 토큰 |", "|---:|---|---|---|---:|"]
    for i, b in enumerate(boundaries, 1):
        pre = f"{b.pre_tokens:,}" if b.pre_tokens is not None else "—"
        out.append(f"| {i} | `{b.timestamp}` | `{b.local or '—'}` | {b.trigger} | {pre} |")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("transcript", type=Path)
    ap.add_argument("--since", help="이 날짜(YYYY-MM-DD) 이후만")
    args = ap.parse_args(argv)

    if not args.transcript.is_file():
        print(f"기록 파일이 없다: {args.transcript}")
        return 2

    if args.since and not _DATE_RE.fullmatch(args.since):
        # 사전식 비교라 `2026-8-1` 은 조용히 **전부 제외**한다 — 빈 표가
        # "경계가 없다"로 읽힌다. 형식을 강제해서 그 침묵을 없앤다.
        print(f"--since 는 YYYY-MM-DD 여야 한다 (받은 값: {args.since})")
        return 2

    # **한 번만 읽는다.** 두 번 읽으면 그 사이에 기록이 자라(세션 진행 중)
    # 총계와 통계가 어긋난다 — 같은 실행이 서로 다른 파일을 본 셈이 된다.
    found, stats = scan(args.transcript)
    shown = [b for b in found if not args.since or b.timestamp[:10] >= args.since]

    print(render(shown))
    print()
    print(f"경계 {len(found)}건" + (f" (표시 {len(shown)}건, --since {args.since})" if args.since else ""))
    if stats["unparsed"]:
        # 조용히 넘기지 않는다 — 못 읽은 줄이 있으면 보고가 불완전할 수 있다.
        print(f"**경고**: 파싱 실패 {stats['unparsed']}줄 / 전체 {stats['lines']}줄 "
              "— 이 보고는 완전하지 않을 수 있다")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
