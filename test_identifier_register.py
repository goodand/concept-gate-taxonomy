"""식별자 등록부 게이트 — 한 글자가 문서군마다 다른 것을 뜻하는 것을 **기록**하고,
등록되지 않은 계열·형식을 어긴 발행을 잡는다.

왜 있는가 (2026-08-31)
--------------------
단일 대문자+번호 식별자(`P4`·`G32`·`I3`)가 여섯 문서군에서 독립적으로 발행된다.
전수 조사(A~Z) 결과 **17글자가 2개 이상 문서군에 걸치고, 그중 14글자는 같은 번호가
다른 것을 뜻한다** — `I3` 가 `mechanism_spec` 에서는 verified-region protection,
`DESIGN_DIRECTIVE` 에서는 "Verify 는 graph 를 쓰지 않는다". 인용에서 계열을
밝히지 않으면 다음 독자가 다른 문서를 읽는다(회고 G164).

**이 게이트는 충돌을 없애지 않는다.** 14글자 중 우리가 소유한 계열은 소수이고
나머지는 외부 설계 원문(verbatim 보존)·다른 저장소·도구 소관이라 재번호할 수
없다. 게이트가 하는 일은 셋이다:

1. **등록부가 현실과 맞는가** — 사용 중인 글자가 등록돼 있고, 등록된 정의 위치가
   실재하며, 상태 어휘가 닫혀 있다 (`test_adoption_register.py` 와 같은 골격).
2. **발행 형식이 지켜졌는가** — 회고의 G164 가 표 행이 아니라 산문으로, P24~P26 이
   `**P25**(설명)` 꼴로 발행돼 추출기가 셋 다 놓쳤다. 이 세션이 만든 결함이다.
   등록부가 각 계열의 발행 정규식을 적고 게이트가 그것을 강제한다.
3. **추출기가 하나다** — G 를 세는 방법이 둘이면(`**G66**` vs `**G66 BLOCKER**`)
   161 과 164 두 답이 나온다. 등록부의 정규식이 유일한 정의다.

무엇을 재지 않나: 뜻이 실제로 다른가는 사람이 판정해 등록부에 적는다(haiku 감사
2축이 그 판정을 했다). 게이트는 그 판정을 **검증하지 않고 보존**한다.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
REGISTER = ROOT / "docs" / "IDENTIFIER_REGISTER.md"

# 닫힌 어휘 — 등록부 §상태 표와 1:1
STATUSES = {"OWNER", "CITES_ONLY", "COLLIDES", "EXTERNAL",
            # 위양성 — 정규식에는 걸리나 식별자가 아니다. 다음 전수 조사가 같은
            # 판정을 다시 하지 않도록 등록부에 남긴다(동료 세션 제안, 2026-08-31).
            "FP_DIAGRAM", "FP_SECTION", "FP_EXPERIMENT"}
FALSE_POSITIVE = {"FP_DIAGRAM", "FP_SECTION", "FP_EXPERIMENT"}
CONCEPTS = {"문제", "검증", "등급", "규칙", "단계", "불변식", "출처", "요건", "버전", "패턴", "(인용)", "미분류"}
# 문서군 이름 — 등록부 §문서군 표와 1:1. 저장소 밖(notes/, evidence-evaluator/)은
# 게이트가 읽지 못하므로 EXTERNAL 로만 등재되고 정의 위치 실재 검사에서 제외된다.
GROUPS_IN_REPO = {"retro", "rulings", "directive", "roadmap"}
GROUPS_OUTSIDE = {"mechspec", "ev-eval", "ev-eval-code", "vault-tool", "h1a-scope"}


def _rows() -> list[dict]:
    """등록부 §계열 표의 행. 열: 글자 | 문서군 | 뜻 | 정의 위치 | 발행 형식 | 인용 접두 | 상태"""
    assert REGISTER.exists(), "docs/IDENTIFIER_REGISTER.md 가 없다"
    rows = []
    in_table = False
    for line in REGISTER.read_text().splitlines():
        if line.startswith("## 계열"):
            in_table = True
            continue
        if in_table and line.startswith("## "):
            break
        if in_table and line.startswith("| `") and not line.startswith("| 글자"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) < 9:
                continue
            rows.append({
                "letter": cells[0].strip("`"), "group": cells[1].strip("`"),
                "meaning": cells[2], "concept": cells[3].strip("`"),
                "english": cells[4],
                "defined_at": cells[5].strip("`"),
                # 등록부의 `—` 는 "형식 미고정, 검사 제외"다 — 빈 형식으로 읽는다
                "pattern": "" if cells[6].strip("`").startswith("—") else cells[6].strip("`"),
                "cite_prefix": cells[7],
                "status": cells[8].strip("`"),
            })
    return rows


# ---------------------------------------------------------------------------
# 1. 등록부 형식
# ---------------------------------------------------------------------------

def test_register_exists_and_is_not_empty():
    assert len(_rows()) >= 14, "전수 조사가 14글자를 충돌로 확정했다 — 그보다 적으면 등록부가 비었다"


def test_status_vocabulary_is_closed():
    for r in _rows():
        assert r["status"] in STATUSES, (r["letter"], r["group"], r["status"])


def test_no_unclassified_concept_remains():
    """**잔여를 센다** — 동료 세션(evidence-evaluator)의 `test_scanner_residual.py` 규율.

    "이 분류가 옳은가"는 게이트가 못 본다. 그러나 "분류되지 않은 것이 있는가"는 본다.
    `미분류` 는 표시로 남겨두면 안 되고 **0 이어야 한다** — 0 이 아니면 사람이 판정해
    §개념 표에 넣거나, 계열이 아님을 확인해 행을 지운다.

    이 게이트가 없었다면 H·T·A 가 등재 없이 존재하는 것을 계속 놓쳤다(G168)."""
    unclassified = [(r["letter"], r["group"]) for r in _rows() if r["concept"] == "미분류"]
    assert not unclassified, (
        f"개념이 분류되지 않은 계열 {unclassified} — §개념 표에 넣거나 행을 지워라")


def test_concept_vocabulary_is_closed():
    """역방향(뜻 → 글자)의 키. 새 개념을 지어내면 잡힌다 — §개념 표에 먼저 추가할 것."""
    for r in _rows():
        assert r["concept"] in CONCEPTS, (r["letter"], r["group"], r["concept"])


def test_cites_only_rows_do_not_introduce_a_concept():
    for r in _rows():
        if r["status"] in {"CITES_ONLY"} | FALSE_POSITIVE:
            assert r["concept"] == "(인용)", (r["letter"], r["group"])


def test_reverse_table_agrees_with_rows():
    """§개념 표의 글자 목록 == 실제 행. 표가 낡으면 잡힌다."""
    text = REGISTER.read_text()
    m = re.search(r"## 개념.*?\n(\| 개념 \|.*?)\n\n### 정규화", text, re.S)
    assert m, "§개념 표가 없다"
    declared = {}
    for line in m.group(1).splitlines():
        if line.startswith("| `"):
            c = [x.strip() for x in line.strip("|").split("|")]
            letters = set(re.findall(r"\b([A-Z])\b", c[1]))
            if letters:
                declared[c[0].strip("`")] = letters
    actual: dict[str, set[str]] = {}
    for r in _rows():
        if r["status"] not in {"CITES_ONLY"} | FALSE_POSITIVE:
            actual.setdefault(r["concept"], set()).add(r["letter"])
    for concept, letters in declared.items():
        assert actual.get(concept, set()) == letters, (
            f"§개념 `{concept}` 표 {sorted(letters)} ≠ 행 실제 {sorted(actual.get(concept, set()))}")


def test_cite_prefix_is_fully_qualified():
    """접두는 `<문서군>:<글자>` 하나의 형식이다 — 32가지 제멋대로 표기를 7 문서군 이름으로
    고정한 것이 FQN 채택의 전체 비용이었다. 새 어휘를 만들면 잡힌다."""
    for r in _rows():
        if r["status"] in FALSE_POSITIVE:
            continue          # 위양성 행은 식별자가 아니므로 FQN 을 요구하지 않는다
        fq = r["cite_prefix"].strip("`")
        m = re.fullmatch(r"([a-z0-9-]+):([A-Z])", fq)
        assert m, (r["letter"], r["group"], fq, "형식은 <문서군>:<글자>")
        assert m.group(1) in GROUPS_IN_REPO | GROUPS_OUTSIDE, (fq, "문서군 이름이 아니다")
        assert m.group(2) == r["letter"], (fq, "글자가 행과 다르다")
        if r["status"] != "CITES_ONLY":
            assert m.group(1) == r["group"], (fq, "발행 행의 접두는 자기 문서군이어야 한다")


ABBREV_KINDS = {"initial", "arbitrary", "ordinal"}


def test_english_column_declares_kind_and_initial_matches():
    """`영문 (유형)` 열. initial 형은 **글자 == 영문 첫 글자**여야 한다 — 실측 30/30.
    arbitrary·ordinal 은 영문이 `—` 이고 검사하지 않는다(tree 밖, FQN 만이 이름)."""
    for r in _rows():
        if r["status"] in {"CITES_ONLY"} | FALSE_POSITIVE:
            continue
        m = re.fullmatch(r"(.+?)\s*\((initial|arbitrary|ordinal)[^)]*\)", r["english"].strip())
        assert m, (r["letter"], r["group"], r["english"], "형식은 `영문 (유형)`")
        word, kind = m.group(1).strip(), m.group(2)
        if kind == "initial":
            assert word[0].upper() == r["letter"], (r["letter"], r["group"], word, "initial 인데 첫 글자가 다르다")
        else:
            assert word == "—", (r["letter"], r["group"], "arbitrary/ordinal 은 영문이 — 여야 한다")


def test_group_vocabulary_is_closed():
    for r in _rows():
        assert r["group"] in GROUPS_IN_REPO | GROUPS_OUTSIDE, (r["letter"], r["group"])


def test_letter_group_pair_is_unique():
    """키는 (글자, 문서군) 쌍이다. 한 글자 한 행이면 P 의 세 뜻을 적을 수 없다."""
    keys = [(r["letter"], r["group"]) for r in _rows()]
    assert len(keys) == len(set(keys)), sorted(k for k in keys if keys.count(k) > 1)


def test_every_collision_letter_has_at_least_two_rows():
    """COLLIDES 는 정의상 둘 이상이 발행한다 — 한 행뿐이면 상태가 틀렸다."""
    by_letter: dict[str, list[dict]] = {}
    for r in _rows():
        by_letter.setdefault(r["letter"], []).append(r)
    for letter, rows in by_letter.items():
        if any(r["status"] == "COLLIDES" for r in rows):
            assert len(rows) >= 2, f"{letter}: COLLIDES 인데 행이 하나"


def test_outside_groups_are_marked_external():
    for r in _rows():
        if r["group"] in GROUPS_OUTSIDE:
            assert r["status"] in {"EXTERNAL"} | FALSE_POSITIVE, (
                r["letter"], r["group"], "저장소 밖은 EXTERNAL 또는 위양성")


# ---------------------------------------------------------------------------
# 2. 정의 위치 실재 (저장소 안 문서군만)
# ---------------------------------------------------------------------------

def _in_repo_rows():
    return [r for r in _rows() if r["group"] in GROUPS_IN_REPO
            and r["status"] not in {"CITES_ONLY"} | FALSE_POSITIVE]


@pytest.mark.parametrize("row", _in_repo_rows(), ids=lambda r: f"{r['letter']}@{r['group']}")
def test_defined_at_exists_and_contains_the_letter(row):
    """`file:line` 이 실재하고 그 행에 그 글자의 발행이 있다."""
    path, _, line = row["defined_at"].partition(":")
    p = ROOT / path
    assert p.exists(), f"{row['letter']}@{row['group']}: {path} 없음"
    if line:
        text = p.read_text().splitlines()
        n = int(line)
        assert n <= len(text), f"{path}:{line} — 파일이 {len(text)}행뿐"
        assert re.search(rf"\b{row['letter']}\d", text[n - 1]), (
            f"{path}:{line} 에 {row['letter']}<n> 발행이 없다: {text[n-1][:80]}")


# ---------------------------------------------------------------------------
# 3. 발행 형식 강제 — 등록부의 정규식이 유일한 추출기다
# ---------------------------------------------------------------------------

def _owner_rows():
    return [r for r in _rows() if r["status"] == "OWNER" and r["group"] in GROUPS_IN_REPO and r["pattern"]]


@pytest.mark.parametrize("row", _owner_rows(), ids=lambda r: f"{r['letter']}@{r['group']}")
def test_owner_pattern_matches_every_issued_number(row):
    """OWNER 문서에서 그 글자로 발행된 모든 번호가 등록된 형식으로 발행됐다.
    G164(산문)·P24~P26(`**P25**(설명)`)이 이 검사가 잡아야 했던 것이다.

    '발행'의 기준: 표 첫 셀 또는 절 제목에 등장하는 `<L><n>`. 산문 인용은 제외."""
    path, _, _ = row["defined_at"].partition(":")
    text = (ROOT / path).read_text()
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    L = row["letter"]
    # 발행 후보: 표 첫 셀(굵기·수식어 무관) 또는 절 제목
    issued = set()
    for m in re.finditer(rf"^\|\s*\*{{0,2}}{L}(\d+)\b[^|]*\|", text, re.M):
        issued.add(int(m.group(1)))
    for m in re.finditer(rf"^#{{1,4}}\s.*\b{L}(\d+)\b", text, re.M):
        issued.add(int(m.group(1)))
    # 산문 속 굵은 `**G<n>**` 는 보통 인용이다 — 그러나 그 번호가 **표 첫 셀 어디에도
    # 없으면** 인용할 대상이 없으므로 산문 발행이다(G164 가 그랬다). 표에 있는 번호는
    # 인용으로 보고 건드리지 않는다 — 전임 링크 게이트를 죽인 위양성을 피하기 위해.
    in_tables = {int(m.group(1)) for m in re.finditer(rf"^\|\s*\*{{0,2}}{L}(\d+)\b", text, re.M)}
    for m in re.finditer(rf"(?<![|#])\*\*{L}(\d+)\*\*", text):
        n = int(m.group(1))
        if n not in in_tables:
            issued.add(n)
    # 등록된 형식으로 발행된 것
    # 등록부는 셀 내부 모양만 적는다(표 셀 안에 `|` 를 둘 수 없으므로). 골격은 여기서.
    cell_re = re.compile(r"^\|\s*" + row["pattern"] + r"\s*\|", re.M)
    canonical = {int(m.group(1)) for m in cell_re.finditer(text)}
    off_form = sorted(issued - canonical)
    assert not off_form, (
        f"{L}@{row['group']}: 등록 형식 `{row['pattern']}` 을 벗어나 발행된 번호 {off_form}")


@pytest.mark.parametrize("row", _owner_rows(), ids=lambda r: f"{r['letter']}@{r['group']}")
def test_owner_pattern_has_a_capture_group(row):
    assert re.compile(row["pattern"]).groups >= 1, "형식 정규식은 번호를 캡처해야 한다"


# ---------------------------------------------------------------------------
# 4. 인벤토리 누락 — 쓰이는 글자가 등록 안 됨
# ---------------------------------------------------------------------------

SCAN = {
    "retro": [ROOT / "docs" / "H1A_PROBLEM_ANALYSIS.md"],
    "rulings": list((ROOT / "docs").glob("DESIGN_DECISION_*.md")) + list((ROOT / "docs").glob("DESIGN_REQUEST_*.md")),
    "directive": [ROOT / "docs" / "DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md"],
    "roadmap": [ROOT / "docs" / "obligation_layer_roadmap.md"],
}
ID = re.compile(r"(?<![A-Za-z0-9_/.-])([A-Z])(\d{1,3})(?![A-Za-z0-9_])")


def _letters_issued_in_repo() -> dict[str, set[str]]:
    """문서군별로 '발행'(표 첫 셀·절 제목) 형태로 등장하는 글자. 산문 인용은 제외."""
    out: dict[str, set[str]] = {}
    for group, files in SCAN.items():
        for f in files:
            text = re.sub(r"```.*?```", "", f.read_text(errors="replace"), flags=re.S)
            for line in text.splitlines():
                if line.startswith("|") or line.startswith("#"):
                    for L, _ in ID.findall(line.split("|")[1] if line.startswith("|") and "|" in line[1:] else line):
                        out.setdefault(group, set()).add(L)
    return out


def test_every_letter_issued_in_repo_is_registered():
    """P21 의 입구 — 새 계열을 발행하고 등록하지 않으면 잡힌다."""
    registered = {(r["letter"], r["group"]) for r in _rows()}
    issued = _letters_issued_in_repo()
    # 3개 미만 번호로 쓰이는 글자는 산발로 보고 제외한다 (등록부 §범위)
    missing = []
    for group, letters in issued.items():
        for L in letters:
            if (L, group) not in registered:
                n = _count_numbers(L, group)
                if n >= 3:
                    missing.append((L, group, n))
    assert not missing, f"발행되나 등록되지 않은 (글자, 문서군, 번호 수): {sorted(missing)}"


def _count_numbers(L: str, group: str) -> int:
    nums = set()
    for f in SCAN[group]:
        text = re.sub(r"```.*?```", "", f.read_text(errors="replace"), flags=re.S)
        for line in text.splitlines():
            if line.startswith("|") or line.startswith("#"):
                nums.update(n for l, n in ID.findall(line) if l == L)
    return len(nums)


# ---------------------------------------------------------------------------
# 5. 음성 증명 — 게이트가 실제로 우는가
# ---------------------------------------------------------------------------

def test_a_false_row_would_be_caught(tmp_path, monkeypatch):
    """등록부에 실재하지 않는 정의 위치를 심으면 실재 검사가 운다."""
    fake = tmp_path / "IDENTIFIER_REGISTER.md"
    fake.write_text(
        "# x\n\n## 계열\n\n| 글자 | 문서군 | 뜻 | 개념 | 정의 위치 | 발행 형식 | 인용 접두 | 상태 |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| `Z` | `retro` | fake | `등급` | Zoom (initial) | `docs/NOPE.md:1` | `\\*\\*Z(\\d+)\\*\\*` | `retro:Z` | `OWNER` |\n"
    )
    monkeypatch.setattr(__import__(__name__), "REGISTER", fake)
    rows = _rows()
    assert rows and rows[0]["defined_at"] == "docs/NOPE.md:1"
    with pytest.raises(AssertionError):
        test_defined_at_exists_and_contains_the_letter(rows[0])


def test_off_form_issuance_would_be_caught(tmp_path):
    """`**G164** — 산문` 처럼 표 밖 발행이 있으면 형식 검사가 운다."""
    doc = tmp_path / "doc.md"
    doc.write_text(
        "| **G1** | ok |\n| **G2** | ok |\n"
        "### 절 제목에 G3 발행\n"
    )
    row = {"letter": "G", "group": "retro", "defined_at": f"{doc.relative_to(tmp_path)}:1",
           "pattern": r"\*\*G(\d+)\*\*", "status": "OWNER"}
    # ROOT 대신 tmp_path 기준으로 같은 로직을 돌린다
    text = doc.read_text()
    issued = {int(m.group(1)) for m in re.finditer(r"^\|\s*\*{0,2}G(\d+)\b[^|]*\|", text, re.M)}
    issued |= {int(m.group(1)) for m in re.finditer(r"^#{1,4}\s.*\bG(\d+)\b", text, re.M)}
    canonical = {int(m.group(1)) for m in re.finditer(r"^\|\s*" + row["pattern"] + r"\s*\|", text, re.M)}
    assert sorted(issued - canonical) == [3], "절 제목 발행 G3 이 형식 밖으로 잡혀야 한다"

def test_retro_pattern_restatement_has_a_plain_definition():
    """회고 P 는 `| **P9** | 정의 |` 로 정의되고 뒤 절 누계표에서 `| **P9**(설명) |` 로
    재기술된다. **재기술만 있고 정의가 없으면** 그 패턴은 발행된 적이 없다 —
    P24·P25·P26 이 그랬다(이 세션이 만든 결함, 사전 게이트가 잡음)."""
    text = re.sub(r"```.*?```", "", (ROOT / "docs" / "H1A_PROBLEM_ANALYSIS.md").read_text(), flags=re.S)
    plain = {int(n) for n in re.findall(r"^\|\s*\*{0,2}P(\d+)\*{0,2}\s*\|", text, re.M)}
    paren = {int(n) for n in re.findall(r"^\|\s*\*{0,2}P(\d+)\*{0,2}\([^)]*\)\s*\|", text, re.M)}
    orphan = sorted(paren - plain)
    assert not orphan, f"정의 행 없이 누계표 재기술만 있는 P: {orphan}"
