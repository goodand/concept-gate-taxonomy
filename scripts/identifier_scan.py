"""식별자 출현 분류기 — 출현은 **원문 텍스트**에서 열거하고, 구조는 그것을 덮는다.

계약(TDD): `test_identifier_scan.py`. 그 파일의 모듈 docstring 이 이 모듈이 왜
이렇게 만들어졌는지, 무엇을 쓰지 않는지(외부 md 파서 금지 — stdlib 만)를 정의한다.
여기서는 그 계약을 만족하는 구현만 둔다.

## 핵심 설계 (2026-08-31 2차 — 열거·피복 분리)

1차 구현은 출현을 `ast` 노드·블록 규칙에서 **만들어 냈다.** 그래서 규칙이
닿지 않는 곳(바이트 리터럴 · 속성 접근)은 오분류가 아니라 **소실**됐고,
`UNRESOLVED` 가 도달 불가능해 `test_residual_is_zero_across_the_repo` 가
공허하게 초록이었다(계약 §5). 그래서 순서를 뒤집는다:

1. **열거**: 원문에 정규식(`IDENT_RE`)을 돌려 **모든** 후보 출현을 offset 과
   함께 뽑는다 — 이것이 ground truth 다. 파이썬은 물리적 줄 단위로,
   markdown 링크 대상 문자열은 경로 구분자(`/` `_` `-` `.`)로 먼저 쪼갠
   뒤 각 조각에 전체 일치(fullmatch)를 요구한다(아래 참조).
2. **피복(cover)**: 구조(AST `Name`/`Constant` 노드 span · `tokenize`
   COMMENT span · markdown 블록 문맥)를 각 후보의 offset 에 매칭해 종류를
   정한다.
3. **잔여**: 아무 구조도 덮지 못한 후보가 `UNRESOLVED` 다 — 파이썬에서
   바이트 리터럴(`b"G1"`)·속성 이름(`obj.G2`)이 정확히 이 경우다(둘 다
   AST 상 문자열 `Constant`/`Name` 이 아니라서 피복 규칙이 의도적으로
   닿지 않는다). **`PROSE` 는 markdown 본문이라는 실체이지 낙수 규칙이
   아니다** — 파이썬 경로는 `PROSE` 를 절대 배정하지 않는다.

- **식별자 패턴** `[A-Z]\\d{1,3}` 은 좌우로 영문자/숫자/`_` 가 붙으면 매치하지
  않는다(`G1abc`·`SHA G1f4c9`·`G164_note` 는 전역에서 식별자가 아니다).
  단, 점(`.`) 뒤에 오는 것은 별도 규칙이다: **점 뒤에 숫자가 오면**(`E2.4`)
  전체를 식별자로 보지 않고, **점 뒤에 공백/문장끝이 오면**(`A1.`) 식별자로 본다.
- **markdown 링크 대상만 예외**: `[[docs/G164_note]]` 의 `G164` 는 잡아야
  한다 — 파일명 안 `_` 는 단어 결합이 아니라 경로 구분자이기 때문이다.
  이 경계 완화는 **링크 대상 문자열 안에서만** 적용한다(전역으로 풀지
  않는다): 대상 문자열을 `/`·`_`·`-`·`.` 로 쪼갠 뒤 각 조각이 식별자 전체와
  정확히 일치할 때만 잡는다.
- **markdown**: 펜스 열림/닫힘과 info-string 을 행 단위로 추적한다. 펜스가
  **닫히지 않고 EOF 에 도달하면** 그 안의 내용은 통째로 버린다(보수적 — 종류를
  추측하지 않는다). 표 행은 이스케이프되지 않은 `|` 개수로 셀 위치를 판정한다
  (`\\|` 는 구분자가 아니다). 인라인 코드(`` `x` ``)·wikilink(`[[x]]`)·markdown
  링크(`[t](x)`)는 표/제목/산문보다 우선한다. `§` 바로 뒤의 식별자는 SECTION_REF.
- **python**: 물리적 줄마다 `IDENT_RE` 로 후보를 전부 열거한 뒤, `ast` 의
  `Name`(→ PY_NAME)·문자열 `Constant`(→ DICT_KEY/STRING, 딕셔너리 키 여부로
  분기) span 과 `tokenize` 의 COMMENT span 으로 덮는다. 어느 것도 덮지 못하면
  `UNRESOLVED`. 구문 오류면 정규식으로 되돌아가되 종류를 PY_UNPARSED 로
  표시한다(조용히 건너뛰지 않는다).
"""
from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path


class Kind(Enum):
    TABLE_HEAD_CELL = auto()
    TABLE_BODY_CELL = auto()
    HEADING = auto()
    PROSE = auto()
    INLINE_CODE = auto()
    SECTION_REF = auto()
    LINK_TARGET = auto()
    FENCE_MERMAID = auto()
    FENCE_CODE = auto()
    FENCE_TEXT = auto()
    FENCE_PLAIN = auto()
    FRONTMATTER = auto()
    DICT_KEY = auto()
    COMMENT = auto()
    STRING = auto()
    PY_NAME = auto()
    PY_UNPARSED = auto()
    UNRESOLVED = auto()


ISSUANCE_KINDS = {Kind.TABLE_HEAD_CELL, Kind.HEADING, Kind.DICT_KEY}
FALSE_POSITIVE_KINDS = {Kind.FENCE_MERMAID, Kind.SECTION_REF, Kind.PY_NAME}
CITATION_KINDS = {
    Kind.TABLE_BODY_CELL, Kind.PROSE, Kind.INLINE_CODE, Kind.LINK_TARGET,
    Kind.FENCE_CODE, Kind.FENCE_TEXT, Kind.FENCE_PLAIN, Kind.FRONTMATTER,
    Kind.COMMENT, Kind.STRING, Kind.PY_UNPARSED,
}


@dataclass
class Occurrence:
    token: str
    kind: Kind
    line: int
    raw: str
    path: str = ""


@dataclass
class Report:
    all: list[Occurrence] = field(default_factory=list)
    unresolved: list[Occurrence] = field(default_factory=list)


# 식별자: 좌우로 alnum/_ 가 붙으면 매치하지 않는다(더 긴 이름·해시·산문 단어의
# 부분 문자열을 배제 — `G1abc`·`SHA G1f4c9`·`G164_note` 는 전역에서 식별자가
# 아니다). 점 뒤에 숫자가 오는 경우만 추가로 배제한다(`E2.4`); 점 뒤에
# 공백/문장끝은 배제하지 않는다(`A1.`). 링크 대상 문자열 안에서의 예외적 완화는
# `_split_path_pieces` 가 별도로 처리한다(전역 정규식은 그대로 엄격하다).
IDENT_RE = re.compile(r"(?<![A-Za-z0-9_])([A-Z]\d{1,3})(?![A-Za-z0-9_])(?!\.\d)")

_HEADING_RE = re.compile(r"^[ \t]{0,3}#{1,6}(?:\s|$)")
_FENCE_RE = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})[ \t]*(.*)$")
_BACKTICK_RUN_RE = re.compile(r"`+")
_WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|[^\]]*)?\]\]")
_MDLINK_RE = re.compile(r"(?<!\!)\[([^\]]*)\]\(([^)]+)\)")
_PATH_TOKEN_RE = re.compile(r"[^/_\-.]+")
_IDENT_FULL_RE = re.compile(r"[A-Z]\d{1,3}")

_EXCLUDED_DIRS = {".git", ".venv", "node_modules"}


def _find_code_spans(line: str) -> list[tuple[int, int, int, int]]:
    """CommonMark 규칙: 여는 백틱 런과 **같은 길이**의 런이 닫는다. 같은
    길이의 닫는 런을 줄 끝까지 못 찾으면 그 여는 런은 코드 스팬이 아니다
    (미종결 스팬이 줄 나머지를 삼키지 않는다). 반환: (전체시작, 전체끝,
    내용시작, 내용끝) 목록, 등장 순."""
    spans: list[tuple[int, int, int, int]] = []
    n = len(line)
    i = 0
    while i < n:
        m = _BACKTICK_RUN_RE.match(line, i)
        if not m:
            i += 1
            continue
        run_len = m.end() - m.start()
        content_start = m.end()
        j = content_start
        closer = None
        while j < n:
            m2 = _BACKTICK_RUN_RE.match(line, j)
            if not m2:
                j += 1
                continue
            if m2.end() - m2.start() == run_len:
                closer = m2
                break
            j = m2.end()
        if closer:
            spans.append((m.start(), closer.end(), content_start, closer.start()))
            i = closer.end()
        else:
            i = m.end()
    return spans


def _split_path_pieces(s: str) -> list[tuple[int, str]]:
    """경로 구분자(`/` `_` `-` `.`)로 쪼갠 조각과 그 시작 offset."""
    return [(m.start(), m.group(0)) for m in _PATH_TOKEN_RE.finditer(s)]


# ---------------------------------------------------------------------------
# markdown
# ---------------------------------------------------------------------------

def _fence_kind(info: str) -> Kind:
    lang = info.split()[0].lower() if info.split() else ""
    if lang == "mermaid":
        return Kind.FENCE_MERMAID
    if lang == "text":
        return Kind.FENCE_TEXT
    if lang == "":
        return Kind.FENCE_PLAIN
    return Kind.FENCE_CODE


def _count_unescaped_pipes_before(line: str, pos: int) -> int:
    count = 0
    i = 0
    while i < pos:
        if line[i] == "\\" and i + 1 < len(line) and line[i + 1] == "|":
            i += 2
            continue
        if line[i] == "|":
            count += 1
        i += 1
    return count


def _classify_markdown_line(line: str) -> list[tuple[str, Kind]]:
    is_table = line.lstrip().startswith("|")
    is_heading = bool(_HEADING_RE.match(line))

    consumed = bytearray(len(line))
    results: list[tuple[int, str, Kind]] = []

    # 인라인 코드 스팬(이중 백틱 스팬 포함) — 우선순위 최상.
    for whole_s, whole_e, inner_s, inner_e in _find_code_spans(line):
        inner = line[inner_s:inner_e]
        for im in IDENT_RE.finditer(inner):
            results.append((inner_s + im.start(1), im.group(1), Kind.INLINE_CODE))
        for i in range(whole_s, whole_e):
            consumed[i] = 1

    # 링크(wikilink · markdown 링크) 대상 — 경로 구분자로 쪼갠 뒤 조각 단위로
    # 전체 일치를 요구한다(전역 경계 완화가 아니라 링크 안에서만의 예외).
    link_matches: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for m in _WIKILINK_RE.finditer(line):
        link_matches.append((m.span(), m.span(1)))
    for m in _MDLINK_RE.finditer(line):
        link_matches.append((m.span(), m.span(2)))
    for whole_span, target_span in link_matches:
        ws, we = whole_span
        if any(consumed[ws:we]):
            continue
        ts, te = target_span
        target_text = line[ts:te]
        for piece_start, piece in _split_path_pieces(target_text):
            if _IDENT_FULL_RE.fullmatch(piece):
                results.append((ts + piece_start, piece, Kind.LINK_TARGET))
        for i in range(ws, we):
            consumed[i] = 1

    # 나머지 텍스트 — 표/제목/절참조/산문.
    for m in IDENT_RE.finditer(line):
        start, end = m.start(1), m.end(1)
        if any(consumed[start:end]):
            continue
        if start > 0 and line[start - 1] == "§":
            kind = Kind.SECTION_REF
        elif is_table:
            cnt = _count_unescaped_pipes_before(line, start)
            kind = Kind.TABLE_HEAD_CELL if cnt <= 1 else Kind.TABLE_BODY_CELL
        elif is_heading:
            kind = Kind.HEADING
        else:
            kind = Kind.PROSE
        results.append((start, m.group(1), kind))

    results.sort(key=lambda r: r[0])
    return [(tok, kind) for _, tok, kind in results]


def _scan_markdown(text: str) -> list[Occurrence]:
    occurrences: list[Occurrence] = []
    lines = text.split("\n")

    # YAML frontmatter: 파일의 **첫** 줄이 `---` 일 때만 연다(본문 중간의
    # `---` 는 수평선이지 frontmatter 가 아니다). 다음 `---` 까지가 머리말이고
    # 그 안의 출현은 본문(PROSE)이 아니라 FRONTMATTER 다.
    body_start = 0
    if lines and lines[0].strip() == "---":
        close_idx = None
        for j in range(1, len(lines)):
            if lines[j].strip() == "---":
                close_idx = j
                break
        front_end = close_idx if close_idx is not None else len(lines)
        for offset, ftext in enumerate(lines[1:front_end], start=2):
            for fm in IDENT_RE.finditer(ftext):
                occurrences.append(Occurrence(fm.group(1), Kind.FRONTMATTER, offset, ftext))
        body_start = (close_idx + 1) if close_idx is not None else len(lines)

    in_fence = False
    fence_char = ""
    fence_len = 0
    fence_info = ""
    fence_buffer: list[tuple[int, str]] = []

    for idx, line in enumerate(lines[body_start:], start=body_start + 1):
        m = _FENCE_RE.match(line)
        if in_fence:
            if (
                m
                and m.group(1)[0] == fence_char
                and len(m.group(1)) >= fence_len
                and m.group(2).strip() == ""
            ):
                kind = _fence_kind(fence_info)
                for bline_no, btext in fence_buffer:
                    for bm in IDENT_RE.finditer(btext):
                        occurrences.append(
                            Occurrence(bm.group(1), kind, bline_no, btext)
                        )
                in_fence = False
                fence_buffer = []
                continue
            fence_buffer.append((idx, line))
            continue

        if m:
            in_fence = True
            fence_char = m.group(1)[0]
            fence_len = len(m.group(1))
            fence_info = m.group(2).strip()
            fence_buffer = []
            continue

        for tok, kind in _classify_markdown_line(line):
            occurrences.append(Occurrence(tok, kind, idx, line))

    # 펜스가 EOF 까지 닫히지 않으면 그 안의 내용은 버린다(보수적).
    return occurrences


# ---------------------------------------------------------------------------
# python
# ---------------------------------------------------------------------------

def _collect_dict_key_ids(tree: ast.AST) -> set[int]:
    ids: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Dict):
            for k in node.keys:
                if isinstance(k, ast.Constant) and isinstance(k.value, (str, bytes)):
                    ids.add(id(k))
    return ids


def _byte_col_to_char_col(line: str, byte_col: int) -> int:
    """`ast` 의 col_offset 은 **UTF-8 바이트** offset 이다(실측: 한글이 섞인
    줄에서 `tokenize` 는 문자 offset, `ast` 는 바이트 offset 을 낸다 — 둘이
    다르면 한글이 하나라도 앞에 있는 줄에서 커버리지가 통째로 어긋난다).
    후보 enumeration 은 `re`(문자 offset)로 하므로 여기서 문자 offset 으로
    되돌린다."""
    encoded = line.encode("utf-8")
    return len(encoded[:byte_col].decode("utf-8", errors="ignore"))


def _scan_python_fallback(text: str) -> list[Occurrence]:
    occurrences: list[Occurrence] = []
    for i, line in enumerate(text.split("\n"), start=1):
        for m in IDENT_RE.finditer(line):
            occurrences.append(Occurrence(m.group(1), Kind.PY_UNPARSED, i, line))
    return occurrences


def _node_span(node: ast.AST, lines: list[str]) -> tuple[int, int, int, int]:
    start_line = node.lineno
    end_line = getattr(node, "end_lineno", start_line)
    start_byte_col = node.col_offset
    end_byte_col = getattr(node, "end_col_offset", start_byte_col)
    start_col = (
        _byte_col_to_char_col(lines[start_line - 1], start_byte_col)
        if 0 < start_line <= len(lines) else start_byte_col
    )
    end_col = (
        _byte_col_to_char_col(lines[end_line - 1], end_byte_col)
        if 0 < end_line <= len(lines) else end_byte_col
    )
    return (start_line, start_col, end_line, end_col)


_DEF_NAME_RE = re.compile(r"(?:async\s+)?(?:def|class)\s+(\w+)")


def _def_name_span(node: ast.AST, lines: list[str]) -> tuple[int, int, int, int] | None:
    """`ClassDef`/`FunctionDef`/`AsyncFunctionDef` 의 `col_offset` 은
    `class`/`def`/`async` 키워드 시작이지 **이름의 위치가 아니다** — 이름은
    별도 AST 노드가 없는 plain string(`node.name`)이라 span 을 직접 구해야
    한다. 데코레이터·주석이 앞줄에 있어도 `node.lineno` 는 항상 keyword 가
    실제로 있는 물리 줄을 가리키므로 그 줄에서 keyword 뒤 이름을 찾는다.
    바이트→문자 변환은 keyword 시작 위치에도 필요하다(그 줄 앞쪽에 한글이
    있으면 keyword 자체의 문자 offset 이 밀린다)."""
    lineno = node.lineno
    if not (0 < lineno <= len(lines)):
        return None
    line = lines[lineno - 1]
    char_start = _byte_col_to_char_col(line, node.col_offset)
    m = _DEF_NAME_RE.match(line, char_start)
    if not m or m.group(1) != node.name:
        return None
    s, e = m.span(1)
    return (lineno, s, lineno, e)


def _covers(span: tuple[int, int, int, int], lineno: int, col_s: int, col_e: int) -> bool:
    line_s, c_s, line_e, c_e = span
    if lineno < line_s or lineno > line_e:
        return False
    if lineno == line_s and col_s < c_s:
        return False
    if lineno == line_e and col_e > c_e:
        return False
    return True


def _scan_python(text: str) -> list[Occurrence]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _scan_python_fallback(text)

    lines = text.split("\n")

    def raw_for(lineno: int) -> str:
        return lines[lineno - 1] if 0 < lineno <= len(lines) else ""

    # 1. 열거 — 원문에서 후보 출현을 전부 뽑는다(ground truth). `ast` 가 안
    #    보는 것(속성 이름 등)도 여기서는 그대로 후보로 남는다.
    candidates: list[tuple[int, int, int, str]] = []
    for lineno, line in enumerate(lines, start=1):
        for m in IDENT_RE.finditer(line):
            candidates.append((lineno, m.start(1), m.end(1), m.group(1)))

    # 2. 피복 — 구조가 각 후보를 덮는지 span 으로 판정한다. `Name`(변수·함수
    #    호출 등 파이썬 이름) · `alias`(`import x as Y`) · `ClassDef`/
    #    `FunctionDef`/`AsyncFunctionDef` 의 **이름**(class/def 도 파이썬
    #    이름이다 — `G9 = 1` 과 `class G9:` 를 다르게 분류하면 안 된다) ·
    #    문자열/바이트 `Constant`(딕셔너리 키 여부로 DICT_KEY/STRING 분기) ·
    #    주석을 덮는다. **이름 없는 속성 접근**(`obj.G2` 의 `G2` 는
    #    `Attribute.attr` 라는 plain string 일 뿐 별도 span 을 가진 AST 노드가
    #    아니다)은 의도적으로 덮지 않는다 — 잔여가 도달 가능해야 하는 이유가
    #    바로 이것이다.
    dict_key_ids = _collect_dict_key_ids(tree)
    regions: list[tuple[tuple[int, int, int, int], Kind]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            regions.append((_node_span(node, lines), Kind.PY_NAME))
        elif isinstance(node, ast.alias):
            regions.append((_node_span(node, lines), Kind.PY_NAME))
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            span = _def_name_span(node, lines)
            if span is not None:
                regions.append((span, Kind.PY_NAME))
        elif isinstance(node, ast.Constant) and isinstance(node.value, (str, bytes)):
            kind = Kind.DICT_KEY if id(node) in dict_key_ids else Kind.STRING
            regions.append((_node_span(node, lines), kind))

    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT:
                s_line, s_col = tok.start
                e_line, e_col = tok.end
                regions.append(((s_line, s_col, e_line, e_col), Kind.COMMENT))
    except (tokenize.TokenError, IndentationError):
        pass

    # 3. 잔여 — 아무 구조도 덮지 못하면 UNRESOLVED (PROSE 로 흘리지 않는다).
    occurrences: list[Occurrence] = []
    for lineno, col_s, col_e, token in candidates:
        kind = Kind.UNRESOLVED
        for span, region_kind in regions:
            if _covers(span, lineno, col_s, col_e):
                kind = region_kind
                break
        occurrences.append(Occurrence(token, kind, lineno, raw_for(lineno)))

    occurrences.sort(key=lambda o: o.line)
    return occurrences


# ---------------------------------------------------------------------------
# 공개 API
# ---------------------------------------------------------------------------

def scan_text(text: str, suffix: str) -> list[Occurrence]:
    if suffix == ".py":
        return _scan_python(text)
    return _scan_markdown(text)


def scan_repo(root: str | Path) -> Report:
    root = Path(root)
    all_occurrences: list[Occurrence] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if any(part in _EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix not in (".md", ".py"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        occs = scan_text(text, path.suffix)
        rel = str(path.relative_to(root))
        for o in occs:
            o.path = rel
        all_occurrences.extend(occs)

    unresolved = [o for o in all_occurrences if o.kind is Kind.UNRESOLVED]
    return Report(all=all_occurrences, unresolved=unresolved)
