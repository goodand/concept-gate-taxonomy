"""동결 표면을 바이트로 고정하는 게이트.

## 왜 생겼나

2026-08-24: 운영 세션이 드라이런 결과를 기록하려고
`PREREGISTRATION_STAGE2_V4.md`에 부록 58행을 **append했다.** 사전등록서는
동결 표면이고 편집 금지인데, `run_gates.py`가 13/0으로 통과했다 — **어떤
테스트도 사전등록서 바이트를 보고 있지 않았다.** 세션이 스스로 알아채고
되돌렸으나, 알아채지 못했으면 동결이 조용히 깨진 채 남았다.

**동결이 관습으로만 지켜지면 그것은 동결이 아니다.**

## 무엇을 고정하는가

사전등록서·fixture manifest·freeze 스크립트. 이것들은 "무엇을 측정하기로
했는가"의 정본이고, 사후 편집은 관측 결과에 맞춰 계약을 바꾸는 경로다
(D-35가 `ANA` 배제 되돌리기를 금지한 것과 같은 이유).

## 고정하지 않는 것

`_stage2_run.py`·`_stage2_score.py` 같은 **러너·채점기**는 고정하지 않는다.
V5 manifest의 `contract_hashes`가 고정하는 것은 정규화·투영·충족성·평가
프로파일 모듈이고 러너는 거기 없다 — 호출측 구멍을 고칠 수 있어야 한다
(실제로 2026-08-24에 층 하한 생략 회피를 그렇게 고쳤다).

## 개정하려면

`freeze_*`로 **새 파일**을 만들고 이 표에 새 항목을 추가한다. 기존 항목의
해시를 고쳐 쓰는 것은 개정이 아니라 은폐다 — 그렇게 하려면 왜 그것이
개정인지를 커밋 메시지가 말해야 한다.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent

# 2026-08-24 실측. 새 동결 표면을 만들면 여기에 항목을 추가한다 —
# 아래 완전성 검사가 누락을 실패시킨다.
FROZEN: dict[str, str] = {
    "PREREGISTRATION_STAGE2.md":
        "af63dfb41180315febcf58fddaa98f31b812646695c6c0a17ce4451cff0f1b8e",
    "PREREGISTRATION_STAGE2_V2.md":
        "f7d85b193183c86795032094f511a712b4aaa2b08a9dbec5cdff98ac87b3b601",
    "PREREGISTRATION_STAGE2_V4.md":
        "5b36082802bca06ec0c33f76c1d9913e2217ac9852fd91bdf1711866bba39198",
    "stage2_fixture_manifest.json":
        "13b47362d5fb9c5bec2c6f6f4956215d6d6156924ce97b0920b4a434a2c76c14",
    "stage2_fixture_manifest_v2.json":
        "7eac95dd74fa96ce036f7d66c3c2f251fe83b33eab0f3628036ad146bbde0bfc",
    "stage2_fixture_manifest_v4.json":
        "723ed98c2ce1c2d9edb7892c6aeb2760dc18e03ad93b94081d9e0d5dbc8b4ec8",
    "stage2_fixture_manifest_v5.json":
        "fb836692a6508b008cb4f30776c78cb637ba1a484bcbc9c9792af2b18562a98c",
    "freeze_stage2.py":
        "3361d0d752288860c47042d1820177775a36dae99c26bac29a95c287ed4c59c5",
    "freeze_stage2_v2.py":
        "e142fa72def7283052f1737284acf0ce13396f94437faeee7169efb366f5249d",
    "freeze_stage2_v4.py":
        "caaba947b92605c0f05b008fd08c32e2317c46f4bc435519cc560baf161fa3d7",
    "freeze_stage2_v5.py":
        "20e96c225d46361be65150f407a187cc768a5d93b66f5a73f3d19dc5e1dbf13b",
}

# 완전성 검사의 범위 — 이 무늬에 걸리는 파일은 전부 고정 대상이다
FROZEN_GLOBS = ("PREREGISTRATION_*.md", "stage2_fixture_manifest*.json",
                "freeze_stage2*.py")


def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


@pytest.mark.parametrize("name", sorted(FROZEN), ids=lambda n: n)
def test_frozen_surface_is_byte_identical(name):
    p = HERE / name
    assert p.exists(), f"{name}: 고정된 동결 표면이 사라졌다"
    assert _sha256(p) == FROZEN[name], (
        f"{name}의 바이트가 바뀌었다. 동결 표면은 편집하지 않는다 — "
        f"개정이라면 freeze_* 로 **새 파일**을 만들고 이 표에 항목을 추가하라. "
        f"기록 {FROZEN[name][:16]}… vs 현재 {_sha256(p)[:16]}…")


def test_every_frozen_shaped_file_is_pinned():
    """완전성 — 새 동결 표면이 고정 없이 추가되는 경로를 막는다.

    이것이 없으면 `PREREGISTRATION_STAGE2_V5.md`를 만들어도 아무 테스트가
    보지 않고, 그것이 정확히 이 게이트가 생긴 이유의 재발이다.
    """
    found = {p.name for g in FROZEN_GLOBS for p in HERE.glob(g)}
    missing = sorted(found - set(FROZEN))
    assert not missing, (
        f"동결 표면 모양인데 고정되지 않은 파일: {missing}. "
        f"해시를 계산해 FROZEN에 추가하라")


def test_the_comparison_is_not_vacuous(tmp_path):
    """음성 — 1바이트만 바뀌어도 검출된다.

    긍정 검사만 있으면 `_sha256`이 상수를 반환하도록 망가져도 초록이다.
    """
    src = HERE / "PREREGISTRATION_STAGE2_V4.md"
    tampered = tmp_path / src.name
    tampered.write_bytes(src.read_bytes() + b"\n")
    assert _sha256(tampered) != FROZEN[src.name], (
        "개행 하나를 더해도 해시가 같다면 이 게이트는 아무것도 보지 않는다")


def test_the_runner_is_deliberately_not_frozen():
    """러너·채점기는 고정 대상이 아니다 — 호출측 구멍을 고칠 수 있어야 한다.

    이 테스트는 그 결정을 **기록으로 고정**한다. 누가 러너를 FROZEN에 넣으면
    여기서 실패하고, 그때 왜 그것을 동결하는지 설명해야 한다.
    """
    for runner in ("_stage2_run.py", "_stage2_score.py"):
        assert (HERE / runner).exists()
        assert runner not in FROZEN, (
            f"{runner}를 동결하면 층 하한 생략 회피 같은 호출측 결함을 "
            f"고칠 수 없다 — V5 manifest의 contract_hashes도 러너를 "
            f"고정하지 않는다")
