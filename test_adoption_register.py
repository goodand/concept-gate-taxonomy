"""ADOPTION 원장이 거짓 주장을 담지 못하게 한다.

## 무엇을 막는가

2026-08-24 실측: 운영 세션이 `scripts/handoff_reachability.py`를 backlink
게이트로 재사용하자고 추천했다. 그 파일은 **테스트가 있었고 아무도 부르지
않았다.** 테스트가 있으니 살아 있어 보였고 채택되지 않았다는 사실이 어디에도
없었다(P21).

**테스트 통과는 채택의 증거가 아니다.** 계약을 지킨다는 것과 누가 쓴다는 것은
다른 사실이다.

그런데 원장에 "채택됐다"고 적는 것만으로는 부족하다 — **그 주장 자체가 거짓일
수 있다.** 그래서 이 게이트의 핵심은 존재 확인이 아니라 **인용 검증**이다:
`MANUAL_TOOL` 행이 인용한 문서에 그 파일 이름이 **실제로 있는지** 본다. 내가
"HANDOFF에 배선했다"고 쓰고 배선하지 않으면 잡힌다.

이 검사는 **원장을 쓰는 도중에 이미 한 번 값을 냈다**: 첫 판에서
`conftest.py`의 인용처를 `pytest.ini`로 적었는데, 게이트를 쓰기 전 실측하니
그 파일은 `conftest.py`를 언급하지 않았다(pytest가 규약으로 자동 발견한다).
그래서 `INFRASTRUCTURE`·`WIRED_PYTEST`는 인용 검사를 면제한다 — 인용처가
없는 것이 정상인 부류다.

## 하지 않는 것

인용처가 그 도구를 **쓰라고** 하는지는 보지 않는다. 이름이 있는지만 본다.
문서가 "이 도구는 쓰지 마라"라고 적어도 통과한다 — 그것까지 판정하려면 문서를
읽어야 하고 그것은 기제가 아니라 사람의 일이다.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent
REGISTER = ROOT / "docs" / "ADOPTION_REGISTER.md"
LEGACY = ROOT / "docs" / "LEGACY_REGISTER.md"
RUNNER = ROOT / "scripts" / "run_gates.py"

STATUSES = {"WIRED_GATE", "WIRED_PYTEST", "MANUAL_TOOL",
            "INFRASTRUCTURE", "NOT_ADOPTED"}
CITATION_ENFORCED = {"MANUAL_TOOL"}
CITATION_EXEMPT = {"INFRASTRUCTURE", "WIRED_PYTEST"}

_ROW = re.compile(r"^\|\s*`([^`]+\.py)`\s*\|([^|]*)\|\s*([A-Z_]+)\s*\|(.*)\|\s*$")
_DOCREF = re.compile(r"`([^`]+\.(?:md|py|ini|json))`")


def _rows() -> list[tuple[str, str, str]]:
    """(path, status, 호출처 셀) — '## 원장' 절의 표만 읽는다."""
    text = REGISTER.read_text(encoding="utf-8")
    start = text.index("## 원장")
    end = text.index("## 이 원장이 하지 않는 것", start)
    out = []
    for line in text[start:end].splitlines():
        m = _ROW.match(line)
        if m:
            out.append((m.group(1).strip(), m.group(3).strip(), m.group(4)))
    return out


def _inventory() -> set[str]:
    """채택이 자명하지 않은 것 — scripts/*.py + 루트의 비-test *.py."""
    inv = {f"scripts/{p.name}" for p in (ROOT / "scripts").glob("*.py")}
    inv |= {p.name for p in ROOT.glob("*.py") if not p.name.startswith("test_")}
    return inv


# ---- 선언 --------------------------------------------------------------

def test_register_exists_and_is_not_empty():
    assert REGISTER.exists()
    assert len(_rows()) >= 5


def test_status_vocabulary_is_closed():
    for path, status, _ in _rows():
        assert status in STATUSES, (path, status)


def test_the_citation_check_has_real_subjects():
    """음성 방어 — MANUAL_TOOL이 0건이면 핵심 검사가 자명하게 통과한다."""
    assert [r for r in _rows() if r[1] in CITATION_ENFORCED]


# ---- 인벤토리 누락 -----------------------------------------------------

def test_every_tool_is_registered():
    """새 스크립트를 만들고 등록하지 않으면 잡힌다 — P21의 입구다."""
    registered = {r[0] for r in _rows()}
    missing = sorted(_inventory() - registered)
    assert not missing, (
        f"채택 여부가 기록되지 않은 파일: {missing}. 만든 것이 불리는지 "
        "적지 않으면 '테스트가 있다'가 '쓰인다'로 읽힌다")


def test_registered_paths_exist():
    for path, _, _ in _rows():
        assert (ROOT / path).exists(), f"{path}: 등록됐지만 실재하지 않는다"


# ---- 핵심: 인용 검증 ---------------------------------------------------

@pytest.mark.parametrize(
    "row", [r for r in _rows() if r[1] in CITATION_ENFORCED], ids=lambda r: r[0])
def test_manual_tool_citation_actually_names_the_file(row):
    """"배선했다"는 주장이 참인지 인용처를 열어 확인한다."""
    path, _, cell = row
    name = Path(path).name
    docs = [d for d in _DOCREF.findall(cell) if not d.endswith(".py")]
    assert docs, f"{path}: MANUAL_TOOL인데 인용처가 없다"
    hits = []
    for d in docs:
        f = ROOT / d
        assert f.exists(), f"{path}: 인용처 {d}가 실재하지 않는다"
        if name in f.read_text(encoding="utf-8", errors="replace"):
            hits.append(d)
    assert hits, (
        f"{path}: 인용처 {docs}에 `{name}`이 없다. 배선하지 않았거나 "
        "인용처를 잘못 적었다 — 둘 다 이 게이트가 잡아야 하는 것이다")


@pytest.mark.parametrize(
    "row", [r for r in _rows() if r[1] == "WIRED_GATE"], ids=lambda r: r[0])
def test_wired_gate_is_in_the_runner(row):
    path, _, _ = row
    assert Path(path).name in RUNNER.read_text(encoding="utf-8"), (
        f"{path}: WIRED_GATE인데 run_gates.py가 부르지 않는다")


@pytest.mark.parametrize(
    "row", [r for r in _rows() if r[1] == "NOT_ADOPTED"], ids=lambda r: r[0])
def test_not_adopted_has_a_reason_and_is_cross_listed(row):
    path, _, cell = row
    assert "사유" in cell, f"{path}: NOT_ADOPTED인데 사유가 없다"
    assert Path(path).name in LEGACY.read_text(encoding="utf-8"), (
        f"{path}: NOT_ADOPTED인데 LEGACY_REGISTER에 없다 — 죽은 것은 두 원장이 "
        "함께 알아야 한다")


def test_exempt_statuses_are_not_required_to_cite():
    """면제 부류가 실제로 면제되는지 — 첫 판의 오류(conftest.py)가 재발하지 않는다."""
    exempt = [r for r in _rows() if r[1] in CITATION_EXEMPT]
    assert exempt, "면제 부류가 0건이면 이 규칙이 검증되지 않는다"


# ---- 루트 테스트의 채택은 수집으로 성립한다 ---------------------------

def test_root_tests_are_collected_by_pytest():
    ini = (ROOT / "pytest.ini").read_text(encoding="utf-8")
    m = re.search(r"^norecursedirs\s*=\s*(.+)$", ini, re.M)
    assert m, "pytest.ini에 norecursedirs가 없다"
    excluded = m.group(1).split()
    assert "." not in excluded and "test" not in excluded
    assert len(list(ROOT.glob("test_*.py"))) >= 10


# ---- 음성 테스트: 게이트가 공허하지 않다 ------------------------------

def test_a_false_citation_would_be_caught(tmp_path):
    """거짓 주장을 실제로 잡는지 — 이 게이트의 존재 이유를 증명한다."""
    doc = tmp_path / "procedure.md"
    doc.write_text("이 문서는 아무 도구도 언급하지 않는다\n", encoding="utf-8")
    name = "verify_dispatch_prompts.py"
    assert name not in doc.read_text(encoding="utf-8")
