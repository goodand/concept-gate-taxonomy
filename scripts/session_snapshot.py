"""compaction 이 잃는 것만 authoritative 출처에서 뽑는다.

계약: `test_session_snapshot.py`. 그 파일의 모듈 docstring 이 왜 이렇게 만드는지를
적고 있다 — 요약하면:

- `HANDOFF.md` 는 **프로젝트 상태**(손으로 유지). compaction 이 잃는 것은
  **진행 중인 것**과 **이미 잰 사실**이다.
- 손으로 쓰지 않는다. compaction 은 자동 유발이라(실측 12건 중 9건 `auto`)
  "쓸 시점"을 고를 수 없고, 손으로 유지하면 낡는다(P4).
- **이 스냅샷은 advisory 다.** 정본과 어긋나면 정본이 이긴다.

쓰는 법:

    python3 scripts/session_snapshot.py [저장소경로]
"""
from __future__ import annotations

import argparse
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

_YAML_CODE = re.compile(r"^(updated|state_code|next_action_code):\s*(\S+)", re.MULTILINE)


@dataclass(frozen=True)
class Change:
    """미커밋 변경 하나. `code` 는 `git status --porcelain` 의 두 글자."""

    code: str
    path: str


@dataclass(frozen=True)
class Snapshot:
    root: Path
    branch: str
    in_flight: list[Change] = field(default_factory=list)
    unpushed: int | None = None
    recent: list[str] = field(default_factory=list)
    handoff: dict[str, str] | None = None
    touched: list[str] = field(default_factory=list)   # 최근 수정 파일 (mtime 순)


def _git(root: Path, *args: str) -> str | None:
    """git 출력 또는 `None`(실패). **실패를 빈 문자열로 바꾸지 않는다** — 그러면
    "결과 없음"과 "못 물었음"이 섞이고, 그것이 전임 도구의 제거 사유였다."""
    proc = subprocess.run(["git", *args], cwd=root, capture_output=True,
                          text=True, check=False)
    return proc.stdout if proc.returncode == 0 else None


def is_repo(root: Path) -> bool:
    return _git(root, "rev-parse", "--git-dir") is not None


def in_flight(root: Path) -> list[Change]:
    """미커밋 변경. **미추적 파일도 포함**한다 — 만들다 만 것이 안 보이면
    이 도구가 존재하는 이유의 절반이 사라진다."""
    out = _git(root, "status", "--porcelain")
    if out is None:
        return []
    changes = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        changes.append(Change(code=line[:2], path=_unquote(line[3:].strip())))
    return changes


def _unquote(raw: str) -> str:
    r"""git 의 따옴표 경로를 원래 이름으로.

    `core.quotepath` 기본값이 켜져 있어 **비-ASCII 파일명이 `"\354\203\210…"`
    8진 이스케이프**로 나온다. 그대로 두면 한글 파일이 진행 중 목록에서 읽을 수
    없는 문자열이 되고, 이 도구의 독자는 사람이다(2026-08-31 실측: 이 저장소의
    파일 상당수가 한글 이름을 쓰지 않지만 문서·회고는 한글 본문을 쓴다).

    따옴표가 없으면 git 이 이스케이프하지 않은 것이므로 **그대로 돌려준다** —
    추측해서 디코드하지 않는다.
    """
    if not (raw.startswith('"') and raw.endswith('"')):
        return raw
    body = raw[1:-1]
    try:
        # 8진 이스케이프를 바이트로 되돌린 뒤 UTF-8 로 읽는다.
        return body.encode("latin-1", "backslashreplace").decode("unicode_escape") \
                   .encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        # 못 읽으면 원문 그대로 — 지어낸 이름을 넣지 않는다.
        return raw


def handoff_pointer(root: Path) -> dict[str, str] | None:
    """`HANDOFF.md` 기계 블록의 **코드만**. 뒤따르는 산문 설명은 싣지 않는다 —
    복사하면 두 벌이 되고 정본이 바뀔 때 갈라진다(G199·G213).

    파일이 없으면 `None` — 없는 것을 빈 값으로 채우면 "없다"와 "못 읽었다"가
    섞인다."""
    path = root / "HANDOFF.md"
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8", errors="replace")
    return {k: v for k, v in _YAML_CODE.findall(text)}


def last_touched(root: Path, limit: int = 5) -> list[str]:
    """구간의 **닫는 괄호** — 가장 최근에 수정된 파일(추적 여부 무관, mtime 순).

    여는 괄호(compaction 경계 직후 첫 편집)는 `compaction_ledger` 가 담당한다.
    이것이 없으면 "이 구간이 어디까지 갔나"를 다음 세션이 커밋 로그로만 추정하는데,
    **미커밋 편집은 커밋 로그에 없다**(사용자 지적, 2026-08-31).
    """
    out = _git(root, "status", "--porcelain")
    dirty = [_unquote(l[3:].strip()) for l in (out or "").splitlines() if len(l) >= 4]
    # 커밋된 최신 편집도 후보에 넣는다 — clean 트리에서도 답이 나와야 한다.
    committed = (_git(root, "log", "-1", "--name-only", "--format=") or "").splitlines()
    seen, cands = set(), []
    for rel in dirty + [c for c in committed if c]:
        if rel in seen:
            continue
        seen.add(rel)
        f = root / rel
        if f.is_file():
            cands.append((f.stat().st_mtime, rel))
    cands.sort(reverse=True)
    return [rel for _, rel in cands[:limit]]


def snapshot(root: Path) -> Snapshot:
    branch = (_git(root, "rev-parse", "--abbrev-ref", "HEAD") or "?").strip()
    ahead = _git(root, "rev-list", "--count", "@{u}..HEAD")
    log = _git(root, "log", "-5", "--format=%h %s")
    return Snapshot(
        root=root,
        branch=branch,
        in_flight=in_flight(root),
        unpushed=int(ahead.strip()) if ahead and ahead.strip().isdigit() else None,
        recent=[l for l in (log or "").splitlines() if l],
        handoff=handoff_pointer(root),
        touched=last_touched(root),
    )


def render(s: Snapshot) -> str:
    """스냅샷을 markdown 으로. **문서가 자기 지위를 말한다** — 이것을 읽는 쪽이
    정본으로 오인하면 다음 세션이 낡은 값을 근거로 판단한다."""
    out = [
        "# 세션 스냅샷 (생성물 · **advisory**)",
        "",
        "이 문서는 **정본이 아니다.** `git`·`HANDOFF.md` 에서 생성했고, 어긋나면",
        "**정본이 이긴다.** 담는 것은 compaction 이 잃는 것 — 진행 중인 작업뿐이고,",
        "프로젝트 상태·다음 행동은 `HANDOFF.md` 가 정본이다.",
        "",
        f"- 저장소 `{s.root}` · 가지 `{s.branch}`",
        f"- 미푸시 커밋 {s.unpushed if s.unpushed is not None else '확인 못 함(upstream 없음)'}",
        "",
        "## 진행 중 (미커밋)",
        "",
    ]
    if s.in_flight:
        out += [f"- `{c.code}` `{c.path}`" for c in s.in_flight]
    else:
        # 빈칸으로 두면 "없다"와 "안 쟀다"가 구별되지 않는다.
        out.append("- 없음 (worktree clean)")
    out += ["", "## 정본 포인터 (`HANDOFF.md` — 복사가 아니라 가리키기)", ""]
    if s.handoff:
        out += [f"- `{k}`: `{v}`" for k, v in s.handoff.items()]
        out.append("- 산문 설명은 싣지 않는다 — 정본을 읽어라")
    else:
        out.append("- `HANDOFF.md` 를 읽지 못했다 (없음 또는 접근 불가)")
    out += ["", "## 최근 수정 파일 (구간의 닫는 괄호 — mtime 순)", ""]
    out += [f"- `{t}`" for t in s.touched] or ["- 없음"]
    out += ["", "## 최근 커밋", ""]
    out += [f"- `{l}`" for l in s.recent] or ["- 없음"]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="compaction 이 잃는 것만 생성한다")
    ap.add_argument("root", nargs="?", default=".", type=Path)
    args = ap.parse_args(argv)

    if not args.root.is_dir() or not is_repo(args.root):
        # 저장소가 아닌 곳에서 "진행 중 없음"을 내면 거짓이다.
        print(f"git 저장소가 아니다: {args.root}")
        return 2

    print(render(snapshot(args.root)))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
