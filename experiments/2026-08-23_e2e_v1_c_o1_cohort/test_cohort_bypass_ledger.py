"""코호트 채점 우회 경로의 **계수를 고정**하는 게이트.

## 무엇을 막는가

`ingest_cohort()`는 오라클·층 하한·strata를 전부 유도하므로 생략 가능한 계약
입력이 없다. 그러나 `ingest_outputs()`는 **여전히 공개이고 `floors=None`
기본값**이다 — control 채점에는 그것이 정당하다(모집단이 달라 층 하한이 없다).

문제는 미래다: 누군가 `ingest_outputs(PLAN, ...)`를 새로 쓰면 사전등록이
금지한 수락이 통과한다. 이 저장소의 음성 대조 테스트가 **그 우회가 실제로
통한다는 것을 증명하고 있다**(`test_the_evasion_succeeds_without_floors_...`).

L0/L1/L2 그래프 정합성 검증(2026-08-24)이 이 공백을 지목했다: 우회 경로가
열려 있고 그것을 세는 것이 없었다.

## 방법 — grep이 아니라 AST

`rg "ingest_outputs("`는 첫 인자가 **실제 plan인지 합성 fixture인지** 구별하지
못한다. 실측: 전체 20건 중 실제 plan을 넘기는 것은 1건이고 나머지는
`spec.cohort_path`(합성) 또는 내부 위임이다. 문맥을 봐야 하므로 AST로 센다.

## 이 게이트가 실패하면

우회 호출이 새로 생겼다는 뜻이다. 둘 중 하나를 하라 — `ingest_cohort`로
바꾸거나, 그것이 정당한 예외라면 `ALLOWED` 에 이유와 함께 등재하라.
등재는 **설명을 강제하는 장치**이고 자동 승인이 아니다.
"""
from __future__ import annotations

import ast
from pathlib import Path

HERE = Path(__file__).resolve().parent
REAL_PLAN_LITERAL = "stage2_cohort_plan_v5.json"
REAL_PLAN_NAMES = {"PLAN"}

# 실제 plan을 `ingest_outputs`에 넘기는 것이 허용된 곳 — 이유를 함께 적는다.
ALLOWED: dict[tuple[str, int], str] = {
    ("test_stage2_cohort_acceptance.py", 163):
        "음성 대조 — 층 하한 없이는 같은 입력이 수락됨을 보여 게이트가 "
        "공허하지 않음을 증명한다. 이 호출이 없으면 위 테스트가 무엇을 "
        "증명하는지 알 수 없다.",
}


def _first_arg_is_real_plan(call: ast.Call) -> bool:
    if not call.args:
        return False
    a = call.args[0]
    if isinstance(a, ast.Name) and a.id in REAL_PLAN_NAMES:
        return True
    return REAL_PLAN_LITERAL in ast.unparse(a)


def _calls(name: str) -> list[tuple[str, int]]:
    out = []
    for f in sorted(HERE.glob("*.py")):
        if f.name == Path(__file__).name:
            continue
        tree = ast.parse(f.read_text(encoding="utf-8"))
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            fn = n.func.attr if isinstance(n.func, ast.Attribute) else getattr(n.func, "id", None)
            if fn == name and _first_arg_is_real_plan(n):
                out.append((f.name, n.lineno))
    return out


def test_every_real_plan_bypass_is_registered():
    """실제 plan을 `ingest_outputs`에 넘기는 곳은 등재된 것뿐이다."""
    found = set(_calls("ingest_outputs"))
    unregistered = sorted(found - set(ALLOWED))
    assert not unregistered, (
        f"실제 코호트 plan을 ingest_outputs에 넘기는 미등재 호출: {unregistered}. "
        f"ingest_cohort로 바꾸거나, 정당한 예외라면 ALLOWED에 이유를 적어라 — "
        f"층 하한이 생략되면 사전등록이 금지한 수락이 통과한다")


def test_the_ledger_has_no_stale_rows():
    """등재가 낡으면 게이트가 조용히 느슨해진다."""
    found = set(_calls("ingest_outputs"))
    stale = sorted(set(ALLOWED) - found)
    assert not stale, (
        f"ALLOWED에 있으나 실재하지 않는 호출: {stale} — 지워라")


def test_the_ast_scan_is_not_vacuous():
    """음성 — 스캔이 실제로 무언가를 찾는다.

    이것이 없으면 `_first_arg_is_real_plan`이 항상 False를 반환하도록
    망가져도 위 두 테스트가 초록이다.
    """
    assert _calls("ingest_outputs"), "우회 호출을 하나도 못 찾았다 — 스캔이 망가졌다"
    assert _calls("ingest_cohort"), "정상 경로 호출도 못 찾았다 — 스캔이 망가졌다"


def test_the_cohort_path_is_actually_used_with_the_real_plan():
    """정상 경로가 실제 plan으로 쓰이고 있는가 — 안 쓰이면 유도가 무의미하다."""
    assert _calls("ingest_cohort"), (
        "ingest_cohort를 실제 plan으로 부르는 곳이 없다 — 유도 진입점이 "
        "죽어 있으면 우회만 남는다")


def test_every_allowed_row_states_a_reason():
    for key, reason in ALLOWED.items():
        assert len(reason) >= 30, f"{key}: 이유가 너무 짧다 — 등재는 설명을 강제한다"
