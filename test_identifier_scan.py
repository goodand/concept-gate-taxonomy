"""식별자 출현 분류기 — 정규식·AST·codex 하네스가 각각 못 하는 것을 한다.

구현보다 먼저 쓴 계약(TDD). `scripts/identifier_scan.py` 는 아직 없다.

## 왜 새로 만드나 — 셋의 한계를 실측했다 (2026-08-31)

**① 정규식**(내 `test_identifier_register.py` 의 추출기 · codex
`build_retrieval_index.py:53 WIKILINK`)이 **구별하지 못하는 것 넷**:

| 입력 | 정규식이 내는 것 | 실제 |
|---|---|---|
| `B -->\|Yes\| X1["버림"]` | `X1` | **mermaid 노드** — 그림 문법 |
| `§A9 참조` | `A9` | **절 번호** |
| `R1 = compute()` | `R1` | **파이썬 변수명** |
| `` | `retro:G` 표 헤더가 `\| # \|` | `` | **`[]` — 추출 실패** (표 셀 안 `\|` 이스케이프) |

**② AST** 는 markdown 에 없다(파이썬 전용). 그리고 파이썬에서도 **주석을 못 본다** —
`# P1 이 남긴 공백` 은 AST 트리에 존재하지 않아 `tokenize` 가 함께 필요하다.
codex 하네스의 AST 사용도 심볼 열거뿐이고 **문맥 분류가 아니다**.

**③ codex 하네스**는 md 본문 파싱이 **전부 정규식**이다(`build_retrieval_index.py:53·56·59`
· `retrieval_interpretation.py:34` · `generate_vault_mocs.py:833`). 펜스 인식은
`claude_controller.py:39 _FENCE` 하나뿐인데 그것은 **Claude 응답에서 JSON 을 뽑는 용도**이고
**md 본문에는 쓰이지 않는다** — 코드블록 내용이 그대로 FTS5 에 색인된다.

**단, "조용히 버린다"는 하네스 전체에 대해서는 거짓이다(2026-08-31 재실측 정정).**
`build_retrieval_index.py:271·281·296·305` 는 해소 실패를 `continue` 로 버리지만,
`generate_vault_mocs.py:832-844` 는 `unresolved` 를 누적해 **예외를 던지고**,
`index_freshness.py:462` 는 `skipped` 를 **세어 보고한다**. 즉 잔여 계수 규율은
저쪽에도 있다 — 모듈마다 다를 뿐이다. 이 모듈은 그 규율을 **한 군데로 모으는** 것이지
없던 것을 들여오는 것이 아니다.

**비교 축을 좁힌다.** 저 하네스는 FTS5/BM25·다중채널 퓨전·합성질문 채널을 갖는다
(`build_retrieval_index.py:449` · `advanced_retrieval.py:101-193`). 그것은 **검색 랭커의
미덕**이고 이 모듈은 **게이트**다. 여기서 겨루는 축은 **markdown 구조 해석의 정확성**
하나이며, 랭킹·색인·퓨전은 **이 모듈의 목표가 아니다**(범위 밖으로 명시한다).

## 이 모듈이 다르게 하는 것 셋

1. **블록 구조로 판정한다.** mermaid 노드 106건이 **전부 ```` ```mermaid ```` 펜스
   안**이고 밖은 **0건**이다(실측). 텍스트 패턴으로는 못 가르고 블록 문맥으로는 갈린다.
   펜스 info-string 분포도 실측했다 — `text` 1192 · `yaml` 187 · `mermaid` 8.
2. **AST + tokenize 를 함께 쓴다.** AST 만으로는 주석이 보이지 않는다.
3. **잔여를 센다.** 모든 출현은 알려진 종류로 분류되거나 `UNRESOLVED` 로 계수되고,
   **`UNRESOLVED` 가 0 이 아니면 실패**한다 — 동료 세션(evidence-evaluator)의
   `test_scanner_residual.py` 규율. 매처를 넓히는 것은 끝이 없으므로 넓히지 않고
   **못 읽은 것을 센다**.

## 의존성 — stdlib 만

`markdown_it` 이 빌린 venv 에 설치돼 있으나 **쓰지 않는다.** 게이트가 선택 의존성에
걸리면 부재 시 `BLOCKED` 가 되고, 이 저장소에서 BLOCKED 는 "검증하지 못함"이라
언제나 도는 stdlib 게이트보다 나쁘다(CLAUDE.md PASS/FAIL/BLOCKED).

## 적대적 검증에서 기각한 지적 (2026-08-31)

- **"`§11.0`·`§11.2` 도 SECTION_REF 로 잡아야 한다"** — 기각. 이 모듈이 세는 것은
  `[A-Z]\d{1,3}` 이고 `§11.0` 에는 **글자가 없다.** 제안된 단언
  `("11", "SECTION_REF")` 은 숫자만 있는 토큰을 요구하는데 그것은 이 모듈의 대상이
  아니다. 숫자 절 번호는 애초에 식별자로 오인될 수 없으므로 잡을 이유도 없다.
- **"`scan_repo` 범위가 좁다"** — 결함이 아니라 범위 선언으로 답했다
  (`test_residual_is_zero_across_the_repo` docstring 참조).

## 재사용 — `scripts/wikilink_graph.py`

같은 저장소의 `_fenced_mask`(`:65`)가 펜스를 이미 추적한다. 그러나 **bool 만 돌려주고
info-string 이 없어** mermaid 를 구별하지 못한다. 그 한계가 이 모듈이 필요한 이유의
일부이고, 여기서는 언어명을 포함한 블록 문맥을 낸다.
"""
from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))

import identifier_scan as sc  # noqa: E402


def _kinds(text: str, suffix: str = ".md") -> list[tuple[str, str]]:
    """(식별자, 종류 이름) 목록."""
    return [(o.token, o.kind.name) for o in sc.scan_text(textwrap.dedent(text), suffix)]


# ---------------------------------------------------------------------------
# 1. markdown 블록 문맥 — 정규식이 못 하는 것
# ---------------------------------------------------------------------------

def test_table_first_cell_is_an_issuance_in_all_three_written_forms():
    """실측(2026-08-31, 이 저장소 md 전체): **굵기 없는 형식이 다수다.**

        굵기 없음        640   `| V1 | 5문항 응답… |`
        **굵기**         295   `| **V2** | qualification… |`
        **굵기**+수식어    71   `| **Q32.1 붕괴 단위** | … |`

    처음 이 계약은 굵은 형식 하나만 실었다 — 그것을 통과하면서 640건을 놓치는 구현이
    가능했다. 적대적 검증이 지목했고 재실측이 확증했다."""
    assert _kinds("| G1 | 내용 |") == [("G1", "TABLE_HEAD_CELL")]
    assert _kinds("| **G164** | 내용 |") == [("G164", "TABLE_HEAD_CELL")]
    assert _kinds("| **G66 BLOCKER** | 내용 |") == [("G66", "TABLE_HEAD_CELL")]


def test_table_later_cell_is_a_citation_not_an_issuance():
    """첫 셀만 발행이다. 둘째 셀의 `P24` 는 그 행이 P24 를 **발행**하는 게 아니라
    언급하는 것이다 — 회고 누계표가 정확히 이 형태다."""
    kinds = _kinds("| **G164** | 앞서 P24 로 등록한 형태 |")
    assert kinds == [("G164", "TABLE_HEAD_CELL"), ("P24", "TABLE_BODY_CELL")]


def test_heading_is_an_issuance():
    assert _kinds("### G3 절 제목") == [("G3", "HEADING")]


def test_prose_is_a_citation():
    assert _kinds("앞서 **G1** 이 보인 형태다") == [("G1", "PROSE")]


def test_mermaid_node_is_recognised_by_the_fence_language():
    """실측: mermaid 노드 106건이 전부 펜스 안, 밖 0건. 텍스트로는 못 가른다."""
    text = """
    ```mermaid
    flowchart TD
        B -->|Yes| X1["버림"]
        N1[equivalence_groups 생성]
    ```
    """
    assert _kinds(text) == [("X1", "FENCE_MERMAID"), ("N1", "FENCE_MERMAID")]


def test_other_fences_are_a_distinct_kind_not_silently_dropped():
    """```text · ```python 안의 것은 mermaid 와 다른 종류다. **버리지 않고 분류한다** —
    버리면 잔여 계수가 그것을 못 본다."""
    text = """
    ```python
    CODES = {"T1": "x"}
    ```
    ```text
    E1 는 예시다
    ```
    """
    assert _kinds(text) == [("T1", "FENCE_CODE"), ("E1", "FENCE_TEXT")]


def test_inline_code_is_a_distinct_kind():
    assert _kinds("regex `G164` 와 산문 G1") == [
        ("G164", "INLINE_CODE"), ("G1", "PROSE"),
    ]


def test_section_reference_is_recognised():
    """`§A9` 는 절 번호이지 계열이 아니다 — 등록부의 `FP_SECTION`."""
    assert _kinds("§A9 참조와 §A2. 의미보존") == [
        ("A9", "SECTION_REF"), ("A2", "SECTION_REF"),
    ]


def test_escaped_pipe_does_not_shift_the_cell_index():
    """정규식이 `[]` 를 냈던 입력. 표 셀 안 `\\|` 는 셀 구분자가 **아니다** — 그것을
    구분자로 세면 첫 셀의 위치가 밀려 발행이 인용으로 오분류된다.

    처음 이 계약의 단언은 `... or not got` 으로 끝나서 **파싱 완전 실패(`[]`)도
    통과시켰다.** 적대적 검증이 blocker 로 지목했다. 이제 셀 번호를 직접 고정한다."""
    got = _kinds(r"| **G164** | 헤더가 `\| # \| 정의 \|` 인 표에서 P24 를 쓴다 |")
    assert got == [("G164", "TABLE_HEAD_CELL"), ("P24", "TABLE_BODY_CELL")], got


def test_link_target_is_a_distinct_kind():
    assert _kinds("[[docs/G164_note]] 와 [보기](docs/P25.md)") == [
        ("G164", "LINK_TARGET"), ("P25", "LINK_TARGET"),
    ]


def test_dotted_experiment_name_is_not_an_identifier():
    """`E2.4` 를 `E2` 로 잡은 것이 G169 다."""
    assert _kinds("E2.4 surface 와 E2.2 결과") == []


def test_unclosed_fence_is_conservative():
    assert _kinds("| **G1** | x |\n```\nG2 G3") == [("G1", "TABLE_HEAD_CELL")]


# ---------------------------------------------------------------------------
# 2. 파이썬 문맥 — AST 만으로는 부족하다
# ---------------------------------------------------------------------------

def test_dict_key_string_is_an_issuance():
    assert _kinds('CODES = {"T1": "answer"}', ".py") == [("T1", "DICT_KEY")]


def test_comment_is_a_citation_and_ast_alone_cannot_see_it():
    """AST 트리에 주석이 없다 — `tokenize` 가 함께 필요하다는 것이 이 계약의 핵심이다."""
    assert _kinds("# P1 이 남긴 마지막 공백", ".py") == [("P1", "COMMENT")]


def test_variable_name_is_a_code_symbol_not_an_identifier():
    """`R1 = compute()` 의 `R1` 은 계열이 아니라 파이썬 이름이다."""
    assert _kinds("R1 = compute()", ".py") == [("R1", "PY_NAME")]


def test_plain_string_literal_is_a_citation():
    assert _kinds('msg = "G164 를 인용"', ".py") == [("G164", "STRING")]


def test_docstring_is_a_citation():
    assert _kinds('def f():\n    """P25 참조."""\n', ".py") == [("P25", "STRING")]


def test_python_that_does_not_parse_is_reported_not_silently_skipped():
    """구문 오류가 나면 **조용히 건너뛰지 않는다** — codex `resolve_links` 의 `continue`
    가 제거 사유였다. 정규식으로 되돌아가되 그 사실을 종류로 표시한다."""
    got = _kinds("def broken(:\n    T1 = 1\n", ".py")
    assert got == [("T1", "PY_UNPARSED")]


# ---------------------------------------------------------------------------
# 3. 잔여 — 못 읽은 것을 센다
# ---------------------------------------------------------------------------

def test_every_occurrence_gets_a_kind():
    """분류되지 않은 출현이 있으면 `UNRESOLVED` 로 계수된다. 종류를 늘리는 것은
    끝이 없으므로 늘리지 않고, **못 읽은 것을 센다**."""
    text = "| **G1** | x |\n산문 G2\n```mermaid\nX1[a]\n```\n`G3`\n"
    report = sc.scan_text(text, ".md")
    assert all(o.kind is not sc.Kind.UNRESOLVED for o in report)
    assert {o.token for o in report} == {"G1", "G2", "X1", "G3"}


def test_residual_is_zero_across_the_repo():
    """이 저장소 전체에서 `UNRESOLVED` 가 0 이어야 한다. 0 이 아니면 **분류기가 못 읽는
    형태가 실재**하는 것이고, 그 형태를 보고 종류를 추가하거나 무시 규칙을 명시한다.

    **범위는 이 worktree 안뿐이다 — 결함이 아니라 의도다.** 게이트가 저장소 밖
    (`../notes/`·`../evidence-evaluator/`·다른 worktree)을 읽으면 비-hermetic 이 되어
    CI·배포에서 깨진다(`test_wikilink_graph.py` 와 같은 판단). 저장소 밖 범위는
    등록부(`docs/IDENTIFIER_REGISTER.md`)가 **문서군 표**로 감당하고, 그것은 사람이
    갱신한다. 적대적 검증이 이 좁음을 major 로 지목했으나 **범위 선언으로 답한다.**"""
    unresolved = sc.scan_repo(ROOT).unresolved
    assert not unresolved, "분류되지 않은 출현:\n" + "\n".join(
        f"  {o.path}:{o.line}  {o.token}  {o.raw[:60]}" for o in unresolved[:20])


def test_the_three_sets_partition_every_kind():
    """**모든 종류는 발행·인용·위양성 중 정확히 하나다.**

    처음 이 계약은 `ISSUANCE_KINDS` 와 `FALSE_POSITIVE_KINDS` 만 못박았고, 그 결과
    `LINK_TARGET`·`TABLE_BODY_CELL` 이 **어느 집합에도 속하지 않은 채 떠 있었다** —
    적대적 검증이 자기모순으로 지목했다. 개별 집합을 나열하는 것으로는 이 결함이
    다시 생긴다. 그러므로 **분할(partition)** 을 단언한다: 새 종류를 추가하면서 어느
    집합에도 넣지 않으면 이 검사가 운다."""
    assert sc.ISSUANCE_KINDS == {
        sc.Kind.TABLE_HEAD_CELL, sc.Kind.HEADING, sc.Kind.DICT_KEY,
    }
    assert sc.FALSE_POSITIVE_KINDS == {
        sc.Kind.FENCE_MERMAID, sc.Kind.SECTION_REF, sc.Kind.PY_NAME,
    }
    classified = sc.ISSUANCE_KINDS | sc.CITATION_KINDS | sc.FALSE_POSITIVE_KINDS
    every = set(sc.Kind) - {sc.Kind.UNRESOLVED}
    assert classified == every, f"미분류 종류: {every - classified}"
    pairs = [(sc.ISSUANCE_KINDS, sc.CITATION_KINDS),
             (sc.ISSUANCE_KINDS, sc.FALSE_POSITIVE_KINDS),
             (sc.CITATION_KINDS, sc.FALSE_POSITIVE_KINDS)]
    for a, b in pairs:
        assert not (a & b), f"두 집합에 동시에 든 종류: {a & b}"


def test_a_bare_fence_gets_its_own_kind_because_a_real_series_lives_there():
    """빈 info-string 펜스(``` 뒤에 언어명 없음) 안에 **식별자 62건**이 있고, 그중
    `docs/obligation_layer_roadmap.md:16-17` 의 `L1`·`L2` 는 **진짜 계열**(상위목적
    사다리)이다. 빈 펜스를 '코드니까 무시'로 처리하면 실재하는 계열을 잃는다."""
    assert _kinds("```\nL1 궁극: …\nL2 조건: …\n```") == [
        ("L1", "FENCE_PLAIN"), ("L2", "FENCE_PLAIN"),
    ]
    assert sc.Kind.FENCE_PLAIN in sc.CITATION_KINDS


def test_a_period_terminated_identifier_is_still_an_identifier():
    """`qa_v7.py:88` 은 `# A1. concepts not list` 로 A1~A6 을 **주석에서 발행**한다.
    처음 쓴 부정 전방탐색 `(?![A-Za-z0-9_.])` 은 뒤따르는 `.` 때문에 이것을 통째로
    버렸다 — `E2.4`(점 뒤에 숫자)를 막으려던 규칙이 `A1.`(점 뒤에 공백·문장끝)까지
    막은 것이다. **점 뒤에 숫자가 오는 것만** 배제한다."""
    assert _kinds("# A1. concepts not list", ".py") == [("A1", "COMMENT")]
    assert _kinds("E2.4 는 실험이다", ".py") == []


# ---------------------------------------------------------------------------
# 4. 실측 재현 — 이 분류기가 앞선 측정의 오류를 내지 않는가
# ---------------------------------------------------------------------------

def test_it_reproduces_the_mermaid_finding_without_human_judgement():
    """`h1a-scope` 의 `X1` 을 위양성으로 판정한 것은 사람이었다(G171). 분류기는
    `FENCE_MERMAID` 로 **기계가** 낸다."""
    other = ROOT.parent / "concept-gate-h1a-scope-wt"
    if not other.exists():
        pytest.skip("h1a-scope worktree 없음")
    report = sc.scan_repo(other)
    x1 = [o for o in report.all if o.token.startswith("X") and o.kind is sc.Kind.FENCE_MERMAID]
    assert x1, "mermaid 안 X 계열이 기계로 분류되어야 한다"


def test_it_does_not_count_dotted_experiment_names(tmp_path):
    """G169 — `E2.4` 를 `E2` 로 잡아 notes 에서 1,040 건이 나왔던 결함."""
    (tmp_path / "a.md").write_text("E2.4 와 E2.2 는 실험이다\n")
    assert sc.scan_repo(tmp_path).all == []


# ---------------------------------------------------------------------------
# 5. 잔여가 공허하지 않다 — 2026-08-31 구현 1차 후 계약 보강
# ---------------------------------------------------------------------------
#
# 1차 구현(300행)은 25개를 전부 통과했으나 보고에서 스스로 밝혔다:
#
#   "PROSE 를 항상 최종 낙수 규칙으로 둬서 정상 입력에서는 Kind.UNRESOLVED 가
#    실제로 발생하지 않습니다"
#
# 그러면 `test_residual_is_zero_across_the_repo` 는 **영원히 초록**이다. 잔여를
# 세는 것이 이 모듈의 존재 이유인데 셀 수 없는 것을 세고 있었다. 적대적 검증이
# 계약 쪽에서 지적한 "공허한 단언"이 구현 쪽에서 재발한 것이다.
#
# 원인은 **열거 방식**이다. 출현을 AST·블록 규칙에서 만들어 내면, 그 규칙이 닿지
# 않는 곳은 "미분류"가 아니라 **아예 없는 것**이 된다. 그래서 계약을 뒤집는다:
#
#   출현의 근거는 **원문 텍스트**다 — 정규식으로 전부 열거하고, 구조는 그 각각을
#   **덮는(cover)** 데에만 쓴다. 아무 구조도 덮지 못한 출현이 `UNRESOLVED` 다.
#
# 이것이 동료 세션 `test_scanner_residual.py` 의 규율("분류가 맞는지는 검증 못 해도
# 분류 안 된 것이 있는지는 검증한다")을 실제로 성립시키는 유일한 배치다.


def test_occurrences_are_enumerated_from_the_text_not_from_the_structure():
    """구조가 닿지 않는 곳도 **출현으로 존재해야** 한다.

    1차 구현은 파이썬 출현을 `ast` 노드에서 만들었다. 그래서 `ast` 가 문자열로
    보지 않는 것(바이트 리터럴·속성 이름)은 오분류가 아니라 **소실**됐다 —
    구현자 스스로 "범위 밖으로 뒀다"고 적었다. 소실은 잔여 계수를 무력화한다."""
    got = _kinds('payload = b"G1"\nvalue = obj.G2\n', ".py")
    tokens = {t for t, _ in got}
    assert "G1" in tokens, f"바이트 리터럴 안 출현이 사라졌다: {got}"
    assert "G2" in tokens, f"속성 이름 안 출현이 사라졌다: {got}"


def test_unresolved_is_actually_reachable():
    """`UNRESOLVED` 가 **도달 가능**해야 한다. 도달 불가능한 값은 계수의 대상이
    아니라 장식이다.

    구조가 덮지 못한 출현은 `PROSE` 로 흘려보내지 말고 `UNRESOLVED` 로 남긴다.
    위 두 형태(바이트 리터럴·속성)가 바로 그것이다 — 파이썬 파일에는 산문이
    없으므로 낙수할 곳도 없다."""
    got = sc.scan_text('payload = b"G1"\nvalue = obj.G2\n', ".py")
    assert any(o.kind is sc.Kind.UNRESOLVED for o in got), (
        f"UNRESOLVED 가 한 번도 나오지 않는다 — 잔여 게이트가 공허하다: "
        f"{[(o.token, o.kind.name) for o in got]}")


def test_prose_is_never_assigned_in_python():
    """`PROSE` 는 markdown 의 **본문**이라는 실체이지 '나머지 전부'가 아니다.
    파이썬 파일에서 `PROSE` 가 나오면 그것은 낙수 규칙이 살아 있다는 증거다."""
    src = 'payload = b"G1"\nvalue = obj.G2\nx = "G3"\n# G4\nG5 = 1\n'
    assert not [o for o in sc.scan_text(src, ".py") if o.kind is sc.Kind.PROSE]


def test_a_hash_like_token_is_not_an_identifier():
    """느슨한 우측 경계가 만든 위양성. 1차 구현은 `(?!\\d)(?!\\.\\d)` 만 두어
    `SHA G1f4c9` 에서 `G1` 을, `G1abc` 에서 `G1` 을 뽑았다.

    경계를 다시 조인다 — **뒤에 영문자·숫자·밑줄이 오면 식별자가 아니다.**"""
    assert _kinds("SHA G1f4c9 해시") == []
    assert _kinds("G1abc 는 무엇인가") == []
    assert _kinds("변수 G164_note 참조") == []


def test_a_link_target_is_split_on_path_separators_before_matching():
    """그런데 `[[docs/G164_note]]` 의 `G164` 는 **잡아야** 한다 — 위 규칙과
    충돌한다. 해소: 링크 **대상 문자열**은 경로 구분자(`/`·`_`·`-`·`.`)로 먼저
    쪼갠 뒤 조인 경계로 맞춘다. 경계를 전역으로 푸는 것이 아니라 **링크 안에서만**
    쪼개는 것이다 — 1차 구현은 이 구분을 못 해서 전역으로 풀었다."""
    assert _kinds("[[docs/G164_note]] 와 [보기](docs/P25.md)") == [
        ("G164", "LINK_TARGET"), ("P25", "LINK_TARGET"),
    ]
    assert _kinds("산문 G164_note 는 링크가 아니다") == []


# ---------------------------------------------------------------------------
# 6. Edge case — 코퍼스를 실제로 읽고 찾은 형태 (2026-08-31)
# ---------------------------------------------------------------------------
#
# 사용자: "Edge Case, Risk, Dirty는 More READ 한다". 가정하지 않고 이 저장소의
# md 를 전수해 기이한 형태를 셌다. 실측:
#
#     167  펜스 안 표          `docs/obligation_layer_roadmap.md:94`
#      93  펜스 안 제목         `README.md:57`  (bash 펜스 안 `# 주석`)
#      26  백틱 홀수(미종결 스팬)
#       8  이중 백틱 스팬       `CLAUDE.md:397`  ``  `docs/X.md`  ``
#       7  frontmatter 안 식별자
#       6  들여쓰기 코드블록
#
# **앞의 둘이 위험하다.** 펜스 상태보다 표·제목을 먼저 보면 그것들이
# `TABLE_HEAD_CELL`·`HEADING` — 즉 **발행**으로 판정된다. 발행 오판은 등록부에
# 가짜 행을 요구하게 만든다. 이 모듈이 존재하는 이유가 정확히 그 실패이므로
# 계약에 넣는다.


def test_a_table_inside_a_fence_is_not_an_issuance():
    """실측 167건. 펜스 판정이 표 판정보다 **먼저** 와야 한다."""
    text = """
    ```text
    | arm | 내용 | rate | 판정 |
    |---|---|---|---|
    | **G1** | x | y | z |
    ```
    """
    kinds = {k for _, k in _kinds(text)}
    assert kinds <= {"FENCE_TEXT"}, f"펜스 안 표가 발행으로 샜다: {_kinds(text)}"


def test_a_heading_inside_a_fence_is_not_an_issuance():
    """실측 93건. `README.md:57` 의 `# 저장소 루트에서 실행` 은 bash 주석이지
    절 제목이 아니다."""
    text = """
    ```bash
    # G3 저장소 루트에서 실행
    make test
    ```
    """
    assert _kinds(text) == [("G3", "FENCE_CODE")]


def test_a_double_backtick_span_containing_a_backtick():
    """실측 8건(`CLAUDE.md:397`). 순진한 `` `([^`]+)` `` 는 이중 백틱 스팬의
    안쪽 백틱에 걸려 경계를 잘못 잡는다."""
    got = _kinds("이중 스팬 `` `G1` `` 과 산문 G2")
    assert got == [("G1", "INLINE_CODE"), ("G2", "PROSE")], got


def test_yaml_frontmatter_is_not_prose():
    """실측 7건. 파일 첫 줄의 `---` 로 열리는 YAML 머리말은 **본문이 아니다.**
    `PROSE` 로 흘리면 산문 인용과 구별되지 않는다."""
    text = "---\ndescription: G1 을 다루는 문서\n---\n\n산문 G2\n"
    got = _kinds(text)
    assert ("G2", "PROSE") in got
    assert ("G1", "PROSE") not in got, f"frontmatter 가 산문으로 샜다: {got}"


def test_an_unclosed_inline_code_span_does_not_swallow_the_rest_of_the_line():
    """실측 26건 — 한 줄 안에서 백틱 개수가 홀수다. 미종결 스팬이 줄 끝까지
    삼키면 그 줄의 나머지 식별자가 통째로 `INLINE_CODE` 로 오분류된다."""
    got = _kinds("**Q32.2** 닫힌 profile — 보존 `{forall, G1")
    assert ("G1", "INLINE_CODE") not in got, f"미종결 스팬이 삼켰다: {got}"


def test_a_class_or_function_name_is_a_python_name_like_a_variable():
    """`G9 = 1` 은 `PY_NAME` 인데 `class G9:` 는 `UNRESOLVED` 였다(2026-08-31 검증).
    같은 것을 다르게 분류한 것이다 — 클래스·함수 이름도 파이썬 이름이다.

    **왜 이것을 `UNRESOLVED` 로 두면 안 되나.** 잔여는 "분류기가 **못 읽은** 것"을
    담는 자리이지 "분류할 수 있는데 안 한 것"의 자리가 아니다. 명백한 것을 잔여로
    보내면 게이트가 뻔한 입력에 울고, **사람은 그런 게이트를 끈다**(§24 G187 에서
    잰 Risk 가 정확히 이 형태다). 잔여의 신호 대 잡음을 지키는 것이 이 검사다."""
    assert _kinds("G9 = 1", ".py") == [("G9", "PY_NAME")]
    assert _kinds("class G9:\n    pass\n", ".py") == [("G9", "PY_NAME")]
    assert _kinds("def G8():\n    pass\n", ".py") == [("G8", "PY_NAME")]
    assert _kinds("async def G7():\n    pass\n", ".py") == [("G7", "PY_NAME")]
