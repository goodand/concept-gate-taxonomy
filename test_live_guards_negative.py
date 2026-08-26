"""실행·발행 가드의 **음성** 검증.

## 왜 이 파일이 생겼나

`test_guard_negative_coverage.py`(저장소 전역 게이트)가 세 가드를 미검증으로
지목했다 — 어떤 테스트도 그것들을 **발화시키지 않는다**(참조 0건):

```text
_assert_provider_preflight   run_live_phase_c.py
_assert_ready                run_live_phase_c.py
_assert_safe_destination     build_live_public_bundle.py
```

셋을 **읽어 보니 공허하지 않았다** — 실질 검사를 하고 있다. 문제는 그것이
증명되지 않았다는 것이다. 나중에 누가 속을 비워도 관측값이 같아서 아무도
모른다. 이 저장소가 P1 을 7번 겪고 기제화한 바로 그 형태다.

## 무엇을 지키는 가드인가 — 되돌릴 수 없는 두 행위

- `_assert_ready` / `_assert_provider_preflight` — **실제 모델 디스패치**.
  보정이 없거나 실패했거나 동결 표면이 드리프트했으면 거부한다. 적대검증
  보고서가 없거나 `passed` 가 아니거나 낡았으면 거부한다.
- `_assert_safe_destination` — **공개 번들 발행**. vault 안에 쓰지 못하게,
  비어 있지 않은 곳을 덮어쓰지 못하게 한다.

두 행위 다 사후에 되돌릴 수 없다. 그래서 가드의 recall 이 측정돼야 한다.

## 규율

**모킹으로 통과시키지 않는다.** 각 테스트는 위반 입력을 실제로 먹이고
`pytest.raises` 로 발화를 확인한다. 유일한 예외는 `frozen_surface_drift`
자체인데, 그것은 별도 함수이고 여기서 검증하는 것은 **가드가 그 결과를
쓰는가**이지 드리프트 계산이 아니다.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

# 이 파일은 **실험 폴더 밖**에 있다. 그 폴더는 `test_*.py` 전부가
# `FROZEN_SURFACE_FILES` 에 등재돼야 한다는 자체 불변식을 갖고 있고,
# `frozen_surface_drift` 가 **새로 추가된 항목도 드리프트로 센다**
# (`set(now) | set(pins)`). 즉 거기에 테스트를 더하면 기존 calibration 과
# 적대검증 보고서가 전부 낡은 것이 되고, **여기서 증명하는 바로 그 가드가
# 실제 실행을 막는다.** 그 재보정은 실험 소유자의 결정이지 내 것이 아니다.
#
# 전역 가드 게이트는 `ROOT.rglob("*.py")` 로 저장소 전체를 훑으므로 위치는
# 자유롭다. 여기 두면 가드는 증명되고 실험의 동결은 그대로다.
EXP = Path(__file__).resolve().parent / "experiments" / "2026-08-07_handoff_dynamic_controller"
sys.path.insert(0, str(EXP))
HERE = EXP

import build_live_public_bundle as BUNDLE  # noqa: E402
import run_live_phase_c as LIVE  # noqa: E402


# ─────────────────────────── _assert_safe_destination ───────────────────────

def test_destination_inside_the_vault_is_refused(tmp_path):
    """음성 — vault 안에 공개 번들을 쓰면 비공개 재료가 공개 경로로 샌다."""
    inside = HERE / "__never_created_bundle_dest"
    with pytest.raises(BUNDLE.BundleError, match="outside Project_in_progress"):
        BUNDLE._assert_safe_destination(inside)


def test_non_empty_destination_is_refused(tmp_path):
    """음성 — 내용이 있는 곳에 쓰면 조용히 덮어쓴다."""
    dest = tmp_path / "bundle"
    dest.mkdir()
    (dest / "existing.txt").write_text("이미 있다", encoding="utf-8")
    with pytest.raises(BUNDLE.BundleError, match="not empty"):
        BUNDLE._assert_safe_destination(dest)


def test_empty_outside_destination_is_allowed(tmp_path):
    """양성 대조 — 정상 입력까지 막으면 가드가 아니라 고장이다."""
    dest = tmp_path / "bundle"
    dest.mkdir()
    BUNDLE._assert_safe_destination(dest)


def test_missing_destination_is_allowed(tmp_path):
    """아직 없는 경로는 정상(생성 전 호출)."""
    BUNDLE._assert_safe_destination(tmp_path / "not-yet")


# ────────────────────────────────── _assert_ready ───────────────────────────

@pytest.fixture
def results(tmp_path, monkeypatch):
    d = tmp_path / "results"
    d.mkdir()
    monkeypatch.setattr(LIVE, "RESULTS_DIR", d)
    return d


def _calibration(results, **over):
    payload = {"failures": [], "frozen_surface_hashes": {}}
    payload.update(over)
    (results / "calibration.json").write_text(
        json.dumps(payload), encoding="utf-8")


def test_missing_calibration_refuses_the_run(results):
    """음성 — 보정 없이 실행하면 결과가 능력인지 계측기 고장인지 모른다."""
    with pytest.raises(LIVE.LiveRunError, match="calibration.json is missing"):
        LIVE._assert_ready()


def test_calibration_with_failures_refuses_the_run(results):
    """음성 — 보정 실패 상태의 출력은 결과로 쓰지 않는다는 규약의 집행부."""
    _calibration(results, failures=["코더가 축 3에서 어긋났다"])
    with pytest.raises(LIVE.LiveRunError, match="calibration has failures"):
        LIVE._assert_ready()


def test_frozen_surface_drift_refuses_the_run(results, monkeypatch):
    """음성 — 보정 이후 동결 표면이 바뀌었으면 그 보정은 이 코드의 것이 아니다."""
    _calibration(results)
    monkeypatch.setattr(LIVE, "frozen_surface_drift",
                        lambda h: ["_runner.py"])
    with pytest.raises(LIVE.LiveRunError, match="frozen surface drifted"):
        LIVE._assert_ready()


def test_ready_returns_config_when_everything_holds(results, monkeypatch):
    """양성 대조 — 정상 경로가 살아 있어야 음성이 의미를 갖는다."""
    _calibration(results)
    monkeypatch.setattr(LIVE, "frozen_surface_drift", lambda h: [])
    monkeypatch.setattr(LIVE, "_assert_provider_preflight", lambda cfg: None)
    cfg = LIVE._assert_ready()
    assert isinstance(cfg, dict)


# ──────────────────────── _assert_provider_preflight ────────────────────────

def test_codex_mcp_without_redteam_is_refused(results):
    """음성 — 격리 적대검증 없이 Codex MCP 를 돌리지 않는다."""
    with pytest.raises(LIVE.LiveRunError, match="MCP-isolation red-team is missing"):
        LIVE._assert_provider_preflight({"provider": "codex-mcp-cli"})


def test_codex_mcp_with_failed_redteam_is_refused(results):
    """음성 — 적대검증이 **실패**한 상태를 통과시키면 게이트가 장식이 된다."""
    (results / "redteam_codex_mcp_isolation.json").write_text(
        json.dumps({"passed": False, "frozen_surface_hashes": {}}), encoding="utf-8")
    with pytest.raises(LIVE.LiveRunError, match="MCP-isolation red-team failed"):
        LIVE._assert_provider_preflight({"provider": "codex-mcp-cli"})


def test_codex_mcp_with_stale_redteam_is_refused(results, monkeypatch):
    """음성 — 통과했더라도 그 뒤 코드가 바뀌었으면 그 통과는 낡았다."""
    (results / "redteam_codex_mcp_isolation.json").write_text(
        json.dumps({"passed": True, "frozen_surface_hashes": {}}), encoding="utf-8")
    monkeypatch.setattr(LIVE, "frozen_surface_drift", lambda h: ["_runner.py"])
    with pytest.raises(LIVE.LiveRunError, match="stale"):
        LIVE._assert_provider_preflight({"provider": "codex-mcp-cli"})


def test_seatbelt_v2_without_redteam_is_refused(results):
    """음성 — 두 번째 분기도 막는다(첫 분기만 검증하면 절반이 미측정이다)."""
    with pytest.raises(LIVE.LiveRunError, match="provider-isolation red-team is missing"):
        LIVE._assert_provider_preflight({"sandbox_policy": "seatbelt-v2"})


def test_unrelated_provider_passes(results):
    """양성 대조 — 해당 없는 설정까지 막으면 가드가 아니라 차단기다."""
    LIVE._assert_provider_preflight({"provider": "claude-cli", "sandbox_policy": ""})


# ───────────────────────────── 게이트 자신에 대한 확인 ──────────────────────

def test_this_file_actually_exercises_all_three_guards():
    """전역 게이트가 지목한 셋을 이 파일이 전부 발화시키는지 스스로 확인한다.

    하나를 빠뜨리면 그 가드만 조용히 미측정으로 남는다.
    """
    src = Path(__file__).read_text(encoding="utf-8")
    for guard in ("_assert_safe_destination", "_assert_ready",
                  "_assert_provider_preflight"):
        assert f"{guard}(" in src, f"{guard} 를 부르지 않는다"
    assert src.count("pytest.raises") >= 9, "음성 테스트가 부족하다"
