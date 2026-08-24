"""외부 정본(판정·조사 회신)의 verbatim 블록이 기록된 해시와 일치하는가.

이 세션에 이 검사를 **손으로 다섯 번** 했다: 판정 4건과 조사 회신 1건에 항법
링크를 넣을 때마다 `VERBATIM-BEGIN/END` **바깥**만 건드렸는지 확인하려고 해시를
재계산했다. 손으로 하는 검사는 잊는다 — 그래서 기제로 옮긴다.

무엇을 지키는가: 외부 정본은 **바이트 그대로** 보존돼야 한다. 우리가 그것을
인용하고 계약을 그것에 걸기 때문이다. 헤더에 링크를 추가하거나 오타를 고치다가
verbatim 구간을 한 글자 건드리면 이후 모든 인용이 대조 불가가 된다 —
P13(적용된 정본의 원문 부재)의 반대 방향, **원문이 조용히 바뀌는** 실패다.

## 규약이 두 변종이라는 사실 (첫 실행이 발견했다)

해시 기록 범위가 사슬 안에서 갈린다. 어느 쪽도 오염이 아니다.

* D-24~D-29 · 조사 회신: `BEGIN` 다음 개행 ~ **`END` 직전 개행을 포함**
* D-30~D-31: `BEGIN` 다음 개행 ~ **`END` 직전(개행 제외)**

그래서 이 게이트는 **두 범위를 모두 후보로 두고 하나라도 맞으면 통과**시킨다.
어느 한쪽을 강요하면 통과시키려고 기록된 해시를 고치게 되고, 그것은 정본
provenance를 파괴한다(기록된 해시가 수신 바이트의 유일한 증인일 수 있다).

필드명도 갈린다 — `VERBATIM_SHA256` / "도착 파일 sha256". 둘 다 인정한다.

## fail-closed 방향

해시가 어디에도 기록돼 있지 않은 verbatim 문서는 실패다. 기록 없는 정본은
"바뀌었는지 알 수 없는" 상태이고 그것은 무결과 구별되지 않는다.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

DOCS = Path(__file__).resolve().parent / "docs"
BEGIN = "<!-- VERBATIM-BEGIN -->\n"
END_MARK = "<!-- VERBATIM-END -->"
# 64-hex를 sha256 언급 근처에서 찾는다. 필드명이 사슬 안에서 갈렸으므로
# 이름을 고정하지 않는다(위 docstring 참조).
#
# 적대 검증(2026-08-24, Haiku red team) 반영:
# * 대소문자(F1/F2) — hexdigest는 소문자지만 사람이 대문자로 옮겨 적으면
#   이전 정규식([0-9a-f] 전용)이 "기록 없음"으로 **오발**했다. 게이트 오발은
#   신뢰를 깎고, 신뢰 잃은 게이트는 꺼진다. IGNORECASE + 소문자 정규화로 수리.
# * 기록 위치(F3/F4)는 **제약하지 않는다 — 수리가 아니라 한계로 문서화**:
#   red team은 code fence 안의 해시도 "기록"으로 세어짐을 지적했으나,
#   재실측하면 그것은 이미 알려진 잔여 우회("블록과 기록을 둘 다 고치면
#   통과")와 등가다 — 기록이 어디 있든 고치는 행위는 같고 방어층도 같다:
#   **git diff에 반드시 드러난다**. 위치를 제약하면 규약 두 변종을 깬다.
#   같은 철학이 커널에 이미 있다: `cg_normalizer.verify_snapshot`의
#   "hash는 증거가 아니다" — 기록된 값을 믿지 않고 재계산으로 대조한다.
_HASH = re.compile(r"sha256[^\n`]*`?([0-9a-fA-F]{64})", re.IGNORECASE)


def _recorded_hashes(text: str) -> set:
    """기록 해시를 소문자로 정규화해 수집한다 — 대조는 항상 소문자 대 소문자."""
    return {h.lower() for h in _HASH.findall(text)}


def _marker_lines(text: str, marker: str) -> int:
    """**행 전체가** 마커인 경우만 센다 — 문서가 규약을 산문으로 설명하며
    백틱으로 마커를 인용하기 때문이다(첫 실행이 이 오측정을 했다)."""
    return sum(1 for line in text.splitlines() if line.strip() == marker)


def _candidates(text: str) -> list[str]:
    """규약 두 변종에 대응하는 블록 바이트 후보."""
    start = text.index(BEGIN) + len(BEGIN)
    end = text.index("\n" + END_MARK, start)
    body = text[start:end]
    return [body, body + "\n"]


def _docs_with_verbatim() -> list[Path]:
    return sorted(p for p in DOCS.glob("*.md")
                  if BEGIN in p.read_text(encoding="utf-8"))


def test_the_corpus_of_verbatim_documents_is_not_empty():
    """이 게이트가 공허해지는 유일한 경로를 막는다 — 대상이 0건이 되는 것."""
    assert len(_docs_with_verbatim()) >= 8


@pytest.mark.parametrize("path", _docs_with_verbatim(), ids=lambda p: p.name)
def test_verbatim_block_matches_a_recorded_hash(path: Path):
    text = path.read_text(encoding="utf-8")
    assert "\n" + END_MARK in text, f"{path.name}: BEGIN만 있고 END가 없다"

    recorded = _recorded_hashes(text)
    assert recorded, (
        f"{path.name}: verbatim 블록이 있는데 sha256 기록이 없다. "
        "기록 없는 정본은 바뀌었는지 알 수 없고 그것은 무결과 구별되지 않는다")

    got = {hashlib.sha256(c.encode("utf-8")).hexdigest()
           for c in _candidates(text)}
    assert got & recorded, (
        f"{path.name}: verbatim 구간이 기록된 어느 해시와도 맞지 않는다.\n"
        f"  실측 {sorted(got)}\n  기록 {sorted(recorded)}\n"
        "헤더를 고칠 때 BEGIN/END **바깥**만 건드려야 한다.")


@pytest.mark.parametrize("path", _docs_with_verbatim(), ids=lambda p: p.name)
def test_verbatim_markers_delimit_exactly_one_block(path: Path):
    text = path.read_text(encoding="utf-8")
    assert _marker_lines(text, BEGIN.strip()) == 1
    assert _marker_lines(text, END_MARK) == 1


def test_mutating_a_verbatim_block_is_detected():
    """음성 테스트 — 이 가드가 공허하지 않다는 증거.

    실제 문서를 건드리지 않고 같은 판정 로직에 변조된 사본을 먹인다.
    """
    path = _docs_with_verbatim()[0]
    text = path.read_text(encoding="utf-8")
    recorded = _recorded_hashes(text)
    body = _candidates(text)[0]
    tampered = body.replace("판정", "판단", 1)
    if tampered == body:
        tampered = body + " x"
    assert hashlib.sha256(tampered.encode("utf-8")).hexdigest() not in recorded


def test_prose_mention_of_a_marker_does_not_break_the_count():
    """음성 테스트 — 첫 실행이 저지른 오측정이 재발하지 않는다는 증거."""
    fake = f"{BEGIN}body\n{END_MARK}\n\n설명: `{END_MARK}` 직전까지의 바이트열.\n"
    assert _marker_lines(fake, END_MARK) == 1


def test_uppercase_recorded_hash_is_still_recognised():
    """red team F1의 수리 증거 — 대문자 기록도 인식한다(오발 방지)."""
    fake = ("- VERBATIM_SHA256: `2FAB19ECFE9FBE9DEA8409F319AD4C23036BDC82"
            "F309C220D04EF0C7B43D096D`\n")
    assert _recorded_hashes(fake) == {
        "2fab19ecfe9fbe9dea8409f319ad4c23036bdc82f309c220d04ef0c7b43d096d"}


def test_mixed_case_field_name_is_still_recognised():
    """red team F2의 수리 증거 — 필드명 대소문자 변형도 인식한다."""
    fake = "- Verbatim_Sha256: 0123456789abcdef" + "0" * 48 + "\n"
    assert len(_recorded_hashes(fake)) == 1
