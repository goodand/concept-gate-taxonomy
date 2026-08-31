"""등록부의 문서군 상수를 `conceptgate/_identifier_groups.py` 로 생성한다.

계약: `test_identifier_groups_sync.py`. 그 파일의 모듈 docstring 이 왜 이렇게
만드는지를 적고 있다 — 요약하면:

- `cg_obligations.py` 가 import 시점에 `docs/IDENTIFIER_REGISTER.md` 를 **파싱**했다.
  production 이 사람이 유지하는 마크다운에 의존했고, `Dockerfile` 이 `docs/` 를
  COPY 하지 않아 배포에서 무력했다.
- 정본은 등록부 그대로 두고, 상수를 **생성**해 패키지 안에 둔다. 어긋남은
  게이트가 잡지 **production 이 깨지지 않는다.**

오늘 두 번 쓴 형태와 같다 — `compaction_ledger`(HANDOFF §7 표 생성) ·
`session_snapshot`(git·HANDOFF 에서 생성).

## 등록부가 없으면 실패한다

빈 상수를 내지 않는다. 그러면 "문서군이 없다"와 "등록부를 못 읽었다"가 섞이고,
그것이 전임 도구 `handoff_reachability.py` 의 제거 사유였다
(`docs/LEGACY_REGISTER.md:31`, "색인이 없으면 backlink 0건이라는 조용한 오답").

## 쓰는 법

    python3 scripts/gen_identifier_groups.py            # 파일에 쓴다
    python3 scripts/gen_identifier_groups.py --stdout   # 표준출력 (게이트가 쓴다)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DEFAULT_REGISTER = ROOT / "docs" / "IDENTIFIER_REGISTER.md"
DEFAULT_OUT = ROOT / "conceptgate" / "_identifier_groups.py"

_HEADER = '''"""등록부에서 **생성된** 문서군 상수 — 손으로 고치지 마라.

정본은 `docs/IDENTIFIER_REGISTER.md` §계열 표이고, 이 파일은 그것을
`scripts/gen_identifier_groups.py` 로 생성한 것이다. 값을 바꾸려면 **등록부를**
고치고 생성기를 다시 돌려라 — `test_identifier_groups_sync.py` 가 둘의 바이트
일치를 강제하므로, 여기만 고치면 게이트가 운다.

**왜 생성하나.** `cg_obligations.py` 가 import 시점에 등록부를 파싱했는데,
production 이 사람이 유지하는 마크다운에 의존하는 것이고 `Dockerfile` 이 `docs/`
를 COPY 하지 않아 배포에서는 무력했다. 생성물은 패키지 안에 있으므로 그 둘이
모두 없어진다.
"""

'''


def groups_for_letter(register: Path, letter: str) -> list[str]:
    """등록부 §계열 표에서 `letter` 행의 문서군을 **정렬해** 낸다.

    정렬하는 이유: 생성물이 **결정론적**이어야 "최신인가" 검사가 성립한다.
    표의 행 순서가 바뀌었다는 이유로 게이트가 울면 사람이 게이트를 끈다.
    """
    if not register.is_file():
        # 빈 목록을 내지 않는다 — 부재와 미확인을 가른다.
        raise FileNotFoundError(f"등록부가 없다: {register}")
    found: set[str] = set()
    in_table = False
    for line in register.read_text(encoding="utf-8").splitlines():
        if line.startswith("## 계열"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if not in_table or not line.startswith("| `"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 9:
            # 열이 모자란 행은 표 파서가 읽을 수 없다 — 조용히 넘기지 않고
            # 세지도 않는다. 등록부 게이트가 그 형식을 이미 강제한다.
            continue
        if cells[0].strip("`") == letter:
            found.add(cells[1].strip("`"))
    if not found:
        raise ValueError(f"등록부에 `{letter}` 행이 없다: {register}")
    return sorted(found)


def render(groups: list[str]) -> str:
    body = "".join(f'    "{g}",\n' for g in groups)
    return (
        f"{_HEADER}"
        "# 불변식 계열(`I`)을 발행하는 문서군. 판정이 `<문서군>:<글자><번호>` 로\n"
        "# 불변식을 지목할 때 이 집합으로 해소한다.\n"
        "INVARIANT_GROUPS: \"frozenset[str]\" = frozenset({\n"
        f"{body}"
        "})\n"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--stdout", action="store_true",
                    help="파일에 쓰지 않고 표준출력으로 (게이트가 쓴다)")
    args = ap.parse_args(argv)

    try:
        text = render(groups_for_letter(args.register, "I"))
    except (FileNotFoundError, ValueError) as exc:
        print(f"생성 실패: {exc}", file=sys.stderr)
        return 2

    if args.stdout:
        sys.stdout.write(text)
    else:
        args.out.write_text(text, encoding="utf-8")
        print(f"생성: {args.out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
