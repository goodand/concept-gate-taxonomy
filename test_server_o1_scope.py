"""O1 Scope MCP·CLI 서버 게이트.

## 왜 이 파일이 필요한가

이 서버는 **동결 계약으로 답한다**고 주장한다. 그 주장이 두 곳에서 깨질 수 있다:

1. 계약 모듈이 드리프트했는데 그대로 답한다 → 실험의 답이 아닌 것을 실험의
   답으로 낸다.
2. 예외를 삼켜 `ok: true`를 낸다 → **엣지 케이스가 숨는다.** 이 서버의 목적이
   "Desktop 쪽에서 실패를 발견하고 고치는 것"이므로 이것은 기능 상실이다.

둘 다 **관측값이 정상과 같다** — 그래서 게이트가 필요하다.

## 음성 테스트가 이 파일의 핵심

`_require_contract`는 가드다. 긍정 테스트만 있으면 공허한 가드와 구별되지
않는다(`CLAUDE.md` "가드를 쓰면 음성 테스트가 함께 온다"). 그리고 실패
형태에도 음성이 필요하다 — 예외를 던지는 입력을 먹여 **구조화된 실패**가
나오는지 본다.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from conceptgate import server_o1_scope as S


# ------------------------------------------------------------- 긍정 (배관) ---

def test_contract_is_not_drifted():
    r = S.contract_status()
    assert r["ok"] is True, r
    assert r["contract_drifted"] == []
    assert r["frozen_surfaces_changed"] == []
    assert len(r["contract_modules"]) == 6
    assert r["paths"]["cache_items"] and r["paths"]["cache_items"] > 0


def test_oracle_resolves_the_whole_cohort():
    r = S.cohort_oracle()
    assert r["ok"] is True, r
    assert r["resolved"] == 20


def test_acceptance_inputs_are_derived():
    r = S.acceptance_inputs()
    assert r["ok"] is True, r
    assert r["pass_min"] == 16
    assert r["stratum_floors"]["multi_quantifier"] == [5, 4]
    assert r["n_trials"] == 20


@pytest.mark.parametrize(
    "kwargs,expected_accept,expected_counts",
    [
        (dict(), True, {"pass": 20, "error": 0}),
        (dict(n_fail=4), True, {"pass": 16}),
        (dict(n_fail=5), False, {"pass": 15}),
        (dict(n_missing=1), False, {"error": 1}),
        (dict(mq_fail=4), False, {"pass": 16}),
    ],
)
def test_dryrun_scenarios_flip_at_the_boundary(kwargs, expected_accept, expected_counts):
    r = S.dryrun(**kwargs)
    assert r["ok"] is True, r
    assert r["acceptance"]["accepted"] is expected_accept, r["counts"]
    for k, v in expected_counts.items():
        assert r["counts"][k] == v, r["counts"]


def test_self_test_passes_in_this_environment():
    r = S.self_test()
    assert r["ok"] is True, [s for s in r["scenarios"] if not s.get("as_expected")]
    assert len(r["scenarios"]) == 5


def test_the_floor_evasion_is_rejected_through_the_server():
    """전체 16/20 인데 mq 1/5 — 사전등록이 금지한 수락이 서버 경로에서도 막힌다."""
    r = S.dryrun(mq_fail=4)
    assert r["counts"]["pass"] == 16
    assert r["acceptance"]["accepted"] is False
    assert r["acceptance"]["stratum_floors_met"] is False


# ------------------------------------------------------- 음성 (실패 형태) ---

def test_contract_guard_refuses_a_drifted_pin(tmp_path, monkeypatch):
    """음성 — 고정 해시가 어긋나면 서비스하지 않는다."""
    man = json.loads(S.MANIFEST.read_text(encoding="utf-8"))
    man["contract_hashes"]["projection_pipeline_module_sha256"] = "0" * 64
    p = tmp_path / "m.json"
    p.write_text(json.dumps(man), encoding="utf-8")
    monkeypatch.setattr(S, "MANIFEST", p)

    with pytest.raises(S.ContractDrift):
        S._require_contract()

    # 도구는 예외를 던지지 않고 **구조화된 실패**를 낸다
    r = S.cohort_oracle()
    assert r["ok"] is False
    assert r["error_type"] == "ContractDrift"
    assert "_stage2_projection_pipeline_v2.py" in r["message"]
    assert r["next"], "고칠 방법을 말하지 않는 실패는 엣지 케이스를 숨긴다"


def test_contract_status_reports_drift_instead_of_raising(tmp_path, monkeypatch):
    """`contract_status`는 드리프트가 있어도 **보고한다** — 진단 도구가 먼저 죽으면
    무엇이 틀렸는지 알 수 없다."""
    man = json.loads(S.MANIFEST.read_text(encoding="utf-8"))
    man["contract_hashes"]["eval_profile_module_sha256"] = "1" * 64
    p = tmp_path / "m.json"
    p.write_text(json.dumps(man), encoding="utf-8")
    monkeypatch.setattr(S, "MANIFEST", p)
    r = S.contract_status()
    assert r["ok"] is False
    assert "_stage2_eval_profile.py" in r["contract_drifted"]


def test_bad_input_becomes_a_structured_verdict_not_a_crash():
    """음성 — 쓰레기 입력이 예외로 새지 않고 판정으로 나온다."""
    r = S.scope_compare("PMB-p05-d1463", "문자열은 formula가 아니다", {"op": "and"})
    assert r["ok"] is True                      # 도구는 돌았다
    assert r["verdict"]["result"] == "error"    # 판정은 error다
    assert "message" not in r or r.get("verdict")


def test_unknown_case_prefix_fails_closed():
    """음성 — 미지 접두어는 거부된다(codec dispatch 와 같은 fail-closed)."""
    r = S.scope_compare("UNKNOWN-x-1", {"op": "and", "args": []}, {"op": "and", "args": []})
    assert r["ok"] is False or r["verdict"]["result"] in ("error", "unscorable"), r


def test_missing_trial_output_is_accounted_as_error_not_dropped():
    """행 손실은 조용한 분모 조작 — 서버 경로에서도 ERROR 로 회계된다."""
    r = S.dryrun(n_missing=3)
    assert r["ok"] is True
    assert r["counts"]["error"] == 3
    assert sum(r["counts"].values()) == 20, "분모가 20이 아니면 행이 사라졌다"


def test_failure_shape_is_uniform():
    """모든 실패가 같은 필드를 갖는가 — 다르면 Desktop 쪽에서 못 읽는다."""
    r = S._fail(ValueError("x"), case_id="c")
    for k in ("ok", "error_type", "message", "context", "traceback", "next"):
        assert k in r, k
    assert r["ok"] is False


# ------------------------------------------------------------------ 배선 ---

def test_every_tool_is_exposed_to_mcp():
    """TOOLS 에 넣고 MCP 등록을 잊는 경로를 막는다."""
    mcp = S.build_mcp()
    assert mcp is not None
    assert set(S.TOOLS) == {
        "contract_status", "cohort_oracle", "acceptance_inputs",
        "scope_compare", "score_cohort", "dryrun", "self_test"}


def test_the_launcher_exists_and_is_executable():
    p = Path(__file__).resolve().parent / "scripts" / "run_o1_scope_mcp.sh"
    assert p.exists(), "런처가 없으면 Desktop 설정이 인터프리터 경로를 직접 들고 있게 된다"
    import os
    assert os.access(p, os.X_OK), f"{p}: 실행 권한 없음"
    t = p.read_text(encoding="utf-8")
    assert "conceptgate.server_o1_scope" in t
    assert "import fastmcp" in t, "의존성 부재를 조용히 넘기면 Desktop 에서 원인 불명으로 죽는다"


def test_no_dispatch_path_exists():
    """이 서버는 모델을 호출하지 않는다 — D-36 `dispatch: blocked` 준수."""
    src = Path(S.__file__).read_text(encoding="utf-8")
    for forbidden in ("Agent(", "Workflow(", "anthropic", "openai", "requests.post"):
        assert forbidden not in src, f"디스패치 경로로 보이는 것: {forbidden}"


# ------------------------------------------- Desktop 진입점 위치 (실측 함정) ---
# 2026-08-24: Desktop 설정이 저장소 안 런처를 가리켰을 때 EPERM 으로 안 떴다
# (macOS 샌드박스는 ~/Desktop 아래 스크립트 exec 를 막는다). 진입점은
# ~/.claude/scripts/ 에 둔다. 이 지식을 다음 세션이 "정리"로 되돌리지 못하게
# 문서와 두 런처의 일치를 고정한다.

HOME_LAUNCHER = Path.home() / ".claude" / "scripts" / "run_o1_scope_mcp.sh"
REPO_LAUNCHER = Path(__file__).resolve().parent / "scripts" / "run_o1_scope_mcp.sh"


def test_the_sandbox_constraint_is_documented():
    """문서가 이유를 담고 있어야 한다 — 없으면 다음 사람이 되돌린다."""
    doc = (Path(__file__).resolve().parent / "docs" / "O1_SCOPE_TOOL.md").read_text(encoding="utf-8")
    assert "Operation not permitted" in doc, "EPERM 실측이 문서에 없다"
    assert ".claude/scripts" in doc, "Desktop 진입점 위치가 문서에 없다"


def test_both_launchers_pin_the_same_interpreter():
    """두 런처가 갈라지면 CLI 와 Desktop 이 다른 파이썬으로 돈다.

    홈 런처는 기계마다 없을 수 있으므로 있을 때만 대조한다.
    """
    if not HOME_LAUNCHER.exists():
        pytest.skip("홈 런처 없음 — 이 기계에는 Desktop 진입점이 설치되지 않았다")
    a = REPO_LAUNCHER.read_text(encoding="utf-8")
    b = HOME_LAUNCHER.read_text(encoding="utf-8")
    pin = "/opt/homebrew/opt/python@3.13/bin/python3.13"
    assert pin in a and pin in b, "인터프리터 고정값이 두 런처에서 다르다"
    for t in ("conceptgate.server_o1_scope", "import fastmcp"):
        assert t in a and t in b, f"{t} 가 한쪽에만 있다"


def test_the_banner_is_suppressed():
    """배너가 stderr 를 채우면 로그에서 실제 오류가 밀린다."""
    src = Path(S.__file__).read_text(encoding="utf-8")
    assert "show_banner=False" in src
