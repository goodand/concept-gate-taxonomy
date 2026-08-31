"""compaction 경계를 세션 기록에서 뽑는다 — 기억이 아니라 측정으로.

## 왜 있는가

`HANDOFF.md` §7 의 compaction ledger 는 **작업 구간의 시작점**을 남기는 표다.
삭제·병합 후보의 범위는 "이 구간이 무엇을 건드렸나"로 좁혀지는데, 그 시작점은
compaction 에서 잃는다. 그래서 표로 남긴다.

**그런데 손으로 적으니 틀렸다(2026-08-31 실측).** 세 가지가 동시에:

    적은 것                    기계 진실
    "08-31 01:42 compaction"   실제는 08-30T16:49:09 — 01:42 는 9시간 뒤 첫 편집
                               (시각 열에 파일 mtime 을 적었다)
    "08-30 여러 회"             08-30 은 1회뿐 — "여러"는 지어낸 것
    3행                        12건

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
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class Boundary:
    """compaction 한 번. `trigger` 는 `auto`(한도 도달) 또는 `manual`(/compact)."""

    timestamp: str          # ISO8601, 초까지
    trigger: str
    pre_tokens: int | None


def iter_boundaries(path: Path) -> Iterator[Boundary]:
    """`path` 의 세션 기록에서 compaction 경계를 파일 순서대로 낸다.

    깨진 줄은 **건너뛰되 세지 않는다** — 이 도구는 경계의 존재를 보고할 뿐
    "몇 줄을 못 읽었나"는 `read_stats` 가 답한다. 조용히 버리지 않기 위해서다.
    """
    for _, b in _scan(path):
        if b is not None:
            yield b


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
            yield True, Boundary(
                timestamp=str(obj.get("timestamp", ""))[:19],
                trigger=str(meta.get("trigger", "?")),
                pre_tokens=int(pre) if isinstance(pre, int) else None,
            )


def render(boundaries: list[Boundary]) -> str:
    """`HANDOFF.md` §7 에 붙일 수 있는 markdown 표."""
    out = ["| # | compaction 시각 | 유발 | 직전 토큰 |", "|---:|---|---|---:|"]
    for i, b in enumerate(boundaries, 1):
        pre = f"{b.pre_tokens:,}" if b.pre_tokens is not None else "—"
        out.append(f"| {i} | `{b.timestamp}` | {b.trigger} | {pre} |")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("transcript", type=Path)
    ap.add_argument("--since", help="이 날짜(YYYY-MM-DD) 이후만")
    args = ap.parse_args(argv)

    if not args.transcript.is_file():
        print(f"기록 파일이 없다: {args.transcript}")
        return 2

    found = list(iter_boundaries(args.transcript))
    shown = [b for b in found if not args.since or b.timestamp[:10] >= args.since]
    stats = read_stats(args.transcript)

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
