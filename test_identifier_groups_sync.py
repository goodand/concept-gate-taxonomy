"""문서군 상수는 등록부에서 **생성**되고, 어긋나면 게이트가 운다.

## 무엇을 고치나

`conceptgate/cg_obligations.py:211` 이 import 시점에 `docs/IDENTIFIER_REGISTER.md`
를 **파싱**했다. 결함 셋:

1. **층이 뒤집힌다** — production 모듈이 사람이 유지하는 마크다운에 의존한다.
   실측: `docs/` 파일을 실제로 여는 production 모듈은 그것 하나뿐이었다.
2. **배포에서 무력하다** — `Dockerfile:23-28` 이 `conceptgate/`·`vendor/`·
   `licenses/` 만 COPY 하고 `docs/` 를 넣지 않는다(구현자 자진 보고, 실측 확증).
3. **런타임 실패 모드** — 표 형식이 바뀌면 **production 이 깨진다.** 완전히 정적인
   문자열 5개에 대해 그럴 이유가 없다.

배포 결함은 이것을 **드러낸 것**이지 만든 것이 아니다. 로컬에 `docs/` 가 있어
가려져 있었을 뿐이다.

## 고치는 형태 — 생성물 + 일치 게이트

    docs/IDENTIFIER_REGISTER.md   정본 (사람이 고친다)
              │ 생성
              ▼
    conceptgate/_identifier_groups.py   생성물 (손으로 고치지 않는다)
              │
              ▼  이 게이트가 둘의 일치를 강제한다

오늘 두 번 쓴 형태와 같다 — `compaction_ledger`(HANDOFF §7 표를 생성) ·
`session_snapshot`(git·HANDOFF 에서 생성). **손으로 유지하지 않고 생성하고,
어긋남은 게이트가 잡지 production 이 깨지지 않는다.**

`Dockerfile` 은 **고치지 않는다** — `COPY conceptgate/` 가 통째로 넣으므로
생성물이 그 안에 있으면 자동으로 실린다(조사 회신의 제안 3을 재실측으로 기각).

## 골격은 어디서 베꼈나

`test_verbatim_canon_integrity.py` — 이 저장소에서 **정본과 사본의 일치를 강제하는
유일한 검증된 선례**다(2026-08-24 적대검증 통과). 특히 그 파일의
`test_mutating_a_verbatim_block_is_detected`(`:112`) 처럼 **게이트가 실제로 우는지
증명하는 검사**를 함께 둔다 — 그것이 없으면 일치 검사가 공허해진다.

## 이 게이트가 성공하면 사라질 것

`INVARIANT_REGISTER_UNAVAILABLE` 코드는 **삭제 대상**이다. 런타임에 등록부를 읽지
않으면 "못 읽음"이라는 상태 자체가 존재하지 않는다. 지금 그것은 잘못된 설계를
정직하게 보고하는 임시 장치이지 있어야 할 기능이 아니다. 다만 **이 계약에서는
지우지 않는다** — 지우는 것은 별개 판단이고, 남겨 두면 배포 환경에서 여전히
fail-closed 다.

## 프로토콜

(가) **3단(부분 조합)에서 멈췄다** — 1단 일치 없음(`git log -S` 로 `generated`·
`in sync`·`regenerate`·`재생성` 전부 0건), 2단 조각 셋 존재, 3단에서 합친다.
8단(Sonnet 위임)은 **PASS** — 생성 스크립트 + 게이트 + 상수 모듈이 각각 짧고,
셋이 한 덩어리라 분리 위임의 부하가 값보다 크다. 7단 적대검증은 별도로 돌린다.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "scripts"))

REGISTER = HERE / "docs" / "IDENTIFIER_REGISTER.md"
GENERATED = HERE / "conceptgate" / "_identifier_groups.py"
GENERATOR = HERE / "scripts" / "gen_identifier_groups.py"


def _regenerate() -> str:
    """생성기를 돌려 **표준출력으로** 받는다. 파일을 덮어쓰지 않는다 — 게이트가
    부작용을 내면 그 게이트를 믿을 수 없다."""
    proc = subprocess.run([sys.executable, str(GENERATOR), "--stdout"],
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0, f"생성기가 실패했다: {proc.stderr[:400]}"
    return proc.stdout


# ---------------------------------------------------------------------------
# 1. 생성물이 존재하고 최신이다
# ---------------------------------------------------------------------------

def test_the_generated_module_exists():
    """부재를 "일치"로 읽지 않는다 — 없는 것과 맞는 것은 다르다."""
    assert GENERATED.is_file(), f"생성물이 없다: {GENERATED}"


def test_the_generated_module_is_byte_identical_to_a_fresh_generation():
    """**바이트 일치**를 요구한다. 값만 비교하면 주석·순서가 손으로 편집돼도
    통과하고, 그러면 "생성물"이라는 주장이 거짓이 된다."""
    assert GENERATED.read_text(encoding="utf-8") == _regenerate()


def test_the_generated_module_says_it_is_generated():
    """읽는 사람이 손으로 고치지 않게 **파일이 스스로 말한다.** 오늘 성문화한
    authoritative/advisory 어휘와 같은 이유 — 문서가 자기 지위를 선언한다."""
    text = GENERATED.read_text(encoding="utf-8")
    assert "생성" in text and "scripts/gen_identifier_groups.py" in text


# ---------------------------------------------------------------------------
# 2. 값이 정본과 같다 — 세 경로가 한 곳을 가리킨다
# ---------------------------------------------------------------------------

def test_the_constant_matches_the_register():
    """생성물의 값이 등록부의 `I` 행과 같다. 이것이 이 게이트의 본체다."""
    import test_identifier_register as reg
    from conceptgate import _identifier_groups as gen
    expected = frozenset(r["group"] for r in reg._rows() if r["letter"] == "I")
    assert gen.INVARIANT_GROUPS == expected


def test_the_obligations_module_uses_the_generated_constant():
    """`cg_obligations` 가 **자기 파싱을 지우고** 생성물을 쓴다. 파싱이 남아
    있으면 규칙이 두 벌이고, 두 벌이면 갈라진다(G199·G213)."""
    src = (HERE / "conceptgate" / "cg_obligations.py").read_text(encoding="utf-8")
    assert "_identifier_groups" in src
    assert "_invariant_groups_from_register" not in src, (
        "런타임 파싱 함수가 남아 있다 — 생성물을 쓰기로 했으면 파싱은 지운다")


def test_production_no_longer_reads_the_docs_directory():
    """층이 다시 뒤집히지 않게 못박는다. `conceptgate/` 안의 **어떤 모듈도**
    `docs/` 를 열지 않는다 — 실측(2026-08-31)으로 그런 모듈은 하나뿐이었고
    그것이 이 작업의 대상이었다."""
    offenders = []
    for path in sorted((HERE / "conceptgate").glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for marker in ('"docs"', "'docs'", 'parent / "docs"'):
            if marker in text:
                offenders.append(f"{path.name}: {marker}")
    # **한계**: 문자열 마커라 `("do" + "cs")` 같은 표현은 우회한다(자체 검증
    # 확인). 이 검사는 **악의적 우회가 아니라 실수**를 잡는 것이고, 실수는
    # 리터럴로 나타난다 — 그 한계를 적어 두어 다음 사람이 과신하지 않게 한다.
    assert not offenders, (
        "production 모듈이 docs/ 를 연다 — 배포 이미지에 docs/ 가 없다"
        f"(`Dockerfile:23-28`): {offenders}")


# ---------------------------------------------------------------------------
# 3. 게이트가 실제로 우는가 (골격을 베낀 자리)
# ---------------------------------------------------------------------------

def test_a_stale_generated_module_is_detected():
    """`test_verbatim_canon_integrity.py:112` 의 형태. **일치 검사는 그것이 우는
    것을 보이지 않으면 공허하다.**

    초안은 `tampered != _regenerate()` 만 단언했는데 그건 "문자열 둘이 다르다"이지
    **게이트가 우는지**가 아니었다 — 자체 검증에서 잡았다. 이제 실제로 파일을
    변조하고 **본체 검사를 호출해** 우는지 보고, 반드시 되돌린다."""
    original = GENERATED.read_text(encoding="utf-8")
    tampered = original.replace("directive", "diirective", 1)
    assert tampered != original, "변이가 실제로 다른 내용이어야 한다"
    try:
        GENERATED.write_text(tampered, encoding="utf-8")
        with pytest.raises(AssertionError):
            test_the_generated_module_is_byte_identical_to_a_fresh_generation()
    finally:
        GENERATED.write_text(original, encoding="utf-8")
    # 복원됐는지 확인 — 게이트가 저장소를 더럽히면 그 게이트를 믿을 수 없다
    assert GENERATED.read_text(encoding="utf-8") == original


def test_the_generator_is_deterministic():
    """두 번 돌려 다르면 "최신인가" 검사가 무의미하다 — 매번 빨개진다."""
    assert _regenerate() == _regenerate()


def test_a_missing_register_makes_the_generator_fail_not_emit_empty():
    """등록부가 없으면 **생성기가 실패**해야 한다. 빈 상수를 내면 "문서군이
    없다"와 "등록부를 못 읽었다"가 섞이고, 그것이 전임 도구
    `handoff_reachability.py` 의 제거 사유였다(`docs/LEGACY_REGISTER.md:31`)."""
    assert GENERATOR.is_file(), (
        "생성기가 없으면 `returncode != 0` 이 **우연히** 맞아 이 검사가 공허해진다 — "
        "부재와 거절을 가른다")
    proc = subprocess.run(
        [sys.executable, str(GENERATOR), "--stdout", "--register", "/nonexistent.md"],
        capture_output=True, text=True, check=False)
    assert proc.returncode != 0
    assert "INVARIANT_GROUPS" not in proc.stdout


# ---------------------------------------------------------------------------
# 4. 배포 — 생성물이 이미지에 실린다
# ---------------------------------------------------------------------------

def test_the_generated_module_ships_in_the_image():
    """`Dockerfile` 을 **고치지 않는다** — `COPY conceptgate/` 가 통째로 넣으므로
    생성물이 그 안에 있으면 자동으로 실린다(조사 회신의 "Dockerfile 라인 23
    수정" 제안을 재실측으로 기각한 자리)."""
    docker = (HERE / "Dockerfile").read_text(encoding="utf-8")
    assert "COPY conceptgate/" in docker
    assert GENERATED.parent.name == "conceptgate"
