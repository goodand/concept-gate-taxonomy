"""Java 런타임 해석 — stub 과 진짜를 가르고, 부재를 의존성 부재로 분류한다.

## 결함 (2026-08-29 실측)

`classify_owl` 은 판정 W2 §4 를 따르려고 `FileNotFoundError` 를
`REASONER_DEPENDENCY_UNAVAILABLE`(의존성 부재)로, 그 외를
`REASONER_RUNTIME_FAILURE`(실행 중 크래시)로 나눈다.

그 분기는 **경로가 아예 없을 때만** 걸린다. macOS 는 `/usr/bin/java` 에
**stub** 을 둔다 — 파일은 있고 실행되지만 `exit 1` 로 "Unable to locate a
Java Runtime" 을 낸다. owlready2 는 그것을 `OwlReadyJavaError` 로 던지고
(`FileNotFoundError` 아님) 결과가 `REASONER_RUNTIME_FAILURE` 가 된다.

판정 W2 §4 원문:

```text
optional reasoner가 deployment profile상 없음 → execution = UNAVAILABLE
HermiT 실행 도중 timeout / crash              → execution = ERROR
```

추론기가 **실행될 수 없는 것**은 전자다. 지금은 후자로 보고한다 — 환경
공백을 버그 신호로 낸다. 이 수리는 **판정 의도의 복원**이다.

## 그리고 이 기계에는 Java 가 있다

`/opt/homebrew/opt/openjdk/bin/java` (OpenJDK 26) 가 설치돼 있으나 brew 가
PATH 에 링크하지 않아 `shutil.which("java")` 가 stub 을 집는다. 우회를 하는
곳은 `test_cg_owl.py` 하나뿐이었다(PATH 조작). 그래서 수리는 두 가지를
동시에 한다 — **찾을 수 있으면 쓰고, 없으면 정직하게 부재로 보고한다.**
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from conceptgate import cg_owl  # noqa: E402


@pytest.fixture(autouse=True)
def _clean_probe(monkeypatch):
    """캐시가 테스트 사이로 새면 뒤 테스트가 앞 테스트의 환경을 본다."""
    cg_owl._reset_java_probe()
    yield
    cg_owl._reset_java_probe()


def _fake_run(mapping):
    """경로 → returncode(또는 던질 예외) 표로 `subprocess.run` 을 대신한다.

    적대검증(2026-08-29)이 지적: 진짜 `subprocess.run` 은 실행 파일 부재 외에
    `TimeoutExpired`·`PermissionError` 도 낸다. 구현의 `except Exception` 이
    그것을 덮는데 표가 `FileNotFoundError` 만 내면 그 분기가 미검증이다.
    그래서 값으로 **예외 인스턴스**를 받으면 그것을 던진다.
    """
    def run(cmd, *a, **k):
        rc = mapping.get(cmd[0])
        if rc is None:
            raise FileNotFoundError(cmd[0])
        if isinstance(rc, BaseException):
            raise rc
        return subprocess.CompletedProcess(cmd, rc, b"", b"")
    return run


# ─────────────────────────────── 해석 규칙 ───────────────────────────────

def test_working_java_on_path_is_used(monkeypatch):
    monkeypatch.delenv("CONCEPTGATE_JAVA", raising=False)
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: "/usr/bin/java")
    monkeypatch.setattr(cg_owl.subprocess, "run", _fake_run({"/usr/bin/java": 0}))
    assert cg_owl._resolve_java() == "/usr/bin/java"


def test_stub_that_exits_nonzero_is_rejected(monkeypatch):
    """음성 — **이 결함의 핵심.** macOS stub 은 실행되지만 exit 1 이다.

    존재 검사(`shutil.which`)로는 못 가른다. 실행해 봐야 안다.
    """
    monkeypatch.delenv("CONCEPTGATE_JAVA", raising=False)
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: "/usr/bin/java")
    monkeypatch.setattr(cg_owl.subprocess, "run", _fake_run({"/usr/bin/java": 1}))
    assert cg_owl._resolve_java() is None


def test_explicit_override_wins(monkeypatch):
    monkeypatch.setenv("CONCEPTGATE_JAVA", "/opt/jdk/bin/java")
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: "/usr/bin/java")
    monkeypatch.setattr(cg_owl.subprocess, "run",
                        _fake_run({"/opt/jdk/bin/java": 0, "/usr/bin/java": 0}))
    assert cg_owl._resolve_java() == "/opt/jdk/bin/java"


def test_java_home_is_honoured(monkeypatch):
    monkeypatch.delenv("CONCEPTGATE_JAVA", raising=False)
    monkeypatch.setenv("JAVA_HOME", "/opt/jdk")
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: "/usr/bin/java")
    monkeypatch.setattr(cg_owl.subprocess, "run",
                        _fake_run({"/opt/jdk/bin/java": 0, "/usr/bin/java": 1}))
    assert cg_owl._resolve_java() == "/opt/jdk/bin/java"


def test_broken_override_falls_through_to_path(monkeypatch):
    """override 가 깨졌다고 전체가 죽지 않는다 — 다음 후보를 본다."""
    monkeypatch.setenv("CONCEPTGATE_JAVA", "/opt/gone/java")
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: "/usr/bin/java")
    monkeypatch.setattr(cg_owl.subprocess, "run", _fake_run({"/usr/bin/java": 0}))
    assert cg_owl._resolve_java() == "/usr/bin/java"


def test_nothing_usable_returns_none(monkeypatch):
    """음성 — 후보가 전부 실패하면 None."""
    monkeypatch.delenv("CONCEPTGATE_JAVA", raising=False)
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: None)
    monkeypatch.setattr(cg_owl.subprocess, "run", _fake_run({}))
    assert cg_owl._resolve_java() is None


def test_probe_is_cached(monkeypatch):
    """프로브는 subprocess 다 — classify 마다 돌면 비용이 된다."""
    calls = []
    monkeypatch.delenv("CONCEPTGATE_JAVA", raising=False)
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: "/usr/bin/java")

    def counting(cmd, *a, **k):
        calls.append(cmd[0])
        return subprocess.CompletedProcess(cmd, 0, b"", b"")
    monkeypatch.setattr(cg_owl.subprocess, "run", counting)
    cg_owl._resolve_java(); cg_owl._resolve_java(); cg_owl._resolve_java()
    assert len(calls) == 1, f"프로브가 {len(calls)}회 돌았다 — 캐시가 없다"


# ───────────────────────────── 분류로 이어지는가 ─────────────────────────

def test_unusable_java_is_dependency_unavailable_not_runtime_failure(monkeypatch):
    """음성 — 이 수리가 존재하는 이유. 판정 W2 §4 의 두 축을 가른다."""
    from conceptgate import server as SV
    monkeypatch.setattr(cg_owl, "_resolve_java", lambda: None)
    fn = getattr(SV, "classify_owl")
    fn = getattr(fn, "fn", None) or fn
    r = fn({"concepts": [{"name": "사변형", "features": [
        {"feature": "다각형", "type": "essential_feature",
         "evidence": "사변형은 다각형"}]}]})
    codes = [e["code"] for e in r["errors"]]
    assert "REASONER_DEPENDENCY_UNAVAILABLE" in codes, codes
    assert "REASONER_RUNTIME_FAILURE" not in codes, (
        "Java 부재가 실행 실패로 분류되면 환경 공백이 버그 신호가 된다")


def test_genuine_crash_is_still_runtime_failure(monkeypatch):
    """양성 대조 — 수리가 크래시 분류를 삼키지 않았는가."""
    from conceptgate import server as SV
    monkeypatch.setattr(cg_owl, "_resolve_java", lambda: "/usr/bin/java")

    # 적대검증 지적: `classify` 를 통째로 갈아끼우면 **실제 classify 경로가
    # 한 번도 안 탄다**. HermiT 호출 지점만 갈아끼워 진짜 경로를 태운다.
    def boom(*a, **k):
        raise RuntimeError("HermiT 가 죽었다")
    monkeypatch.setattr(cg_owl, "sync_reasoner", boom)
    fn = getattr(SV, "classify_owl")
    fn = getattr(fn, "fn", None) or fn
    r = fn({"concepts": [{"name": "사변형", "features": [
        {"feature": "다각형", "type": "essential_feature",
         "evidence": "사변형은 다각형"}]}]})
    assert "REASONER_RUNTIME_FAILURE" in [e["code"] for e in r["errors"]]


def test_reasoner_unavailable_is_caught_by_the_existing_branch():
    """`server.py` 를 편집하지 않는 근거 — 기존 `except FileNotFoundError` 가
    잡도록 **하위 클래스**로 만든다. 그 파일은 380-382행이 E2.4 fixture 에
    원문 인용돼 있어 위쪽 편집이 금지된다."""
    assert issubclass(cg_owl.ReasonerUnavailable, FileNotFoundError)


def test_owlready_java_error_is_not_a_file_not_found():
    """회귀 고정 — 이 결함의 **원인 자체**를 기록으로 남긴다.

    누가 프로브를 지우고 예외 분기로 되돌리면 여기서 실패한다.
    """
    owlready2 = pytest.importorskip("owlready2")
    assert not issubclass(owlready2.OwlReadyJavaError, FileNotFoundError)


# ────────────────── 적대검증(2026-08-29)이 지적한 미커버 경로 ──────────────

def test_timeout_candidate_is_skipped(monkeypatch):
    """음성 — `timeout=10` 초과는 구현의 `except Exception` 이 덮는데
    표가 그것을 내지 않아 미검증이었다."""
    monkeypatch.delenv("CONCEPTGATE_JAVA", raising=False)
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: "/usr/bin/java")
    monkeypatch.setattr(cg_owl.subprocess, "run", _fake_run(
        {"/usr/bin/java": subprocess.TimeoutExpired("java", 10)}))
    assert cg_owl._resolve_java() is None


def test_permission_error_candidate_is_skipped(monkeypatch):
    """음성 — 실행 권한이 없는 java 도 '작동하지 않는' 후보다."""
    monkeypatch.setenv("CONCEPTGATE_JAVA", "/opt/locked/java")
    monkeypatch.delenv("JAVA_HOME", raising=False)
    monkeypatch.setattr(cg_owl.shutil, "which", lambda n: "/usr/bin/java")
    monkeypatch.setattr(cg_owl.subprocess, "run", _fake_run(
        {"/opt/locked/java": PermissionError("no exec"), "/usr/bin/java": 0}))
    assert cg_owl._resolve_java() == "/usr/bin/java", "다음 후보로 넘어가야 한다"


def test_cache_wins_over_later_env_change(monkeypatch):
    """캐시의 절충을 **계약으로 고정**한다 — 조용한 가정으로 두지 않는다.

    적대검증이 지적한 대로 프로세스 수명 동안 기억하므로 도중의 환경 변경은
    반영되지 않는다. 이것이 의도라는 것을 여기서 못 박고, 바꾸려면 이
    테스트를 먼저 고쳐야 한다.
    """
    monkeypatch.setenv("CONCEPTGATE_JAVA", "/opt/a/java")
    monkeypatch.setattr(cg_owl.subprocess, "run",
                        _fake_run({"/opt/a/java": 0, "/opt/b/java": 0}))
    assert cg_owl._resolve_java() == "/opt/a/java"
    monkeypatch.setenv("CONCEPTGATE_JAVA", "/opt/b/java")
    assert cg_owl._resolve_java() == "/opt/a/java", "캐시가 이겨야 한다"
    cg_owl._reset_java_probe()
    assert cg_owl._resolve_java() == "/opt/b/java", "리셋하면 새 값을 본다"


def test_stale_cache_degrades_to_unavailable_not_runtime_failure(monkeypatch):
    """낡은 캐시가 **오분류로 이어지지 않는다**(실측 기반).

    적대검증은 "Java 삭제 후 → ERROR" 를 우려했다. 실측은 반대다 — 죽은
    경로는 owlready2 가 `FileNotFoundError` 로 던지고 기존 분기가 부재로
    잡는다. 그 성질을 고정한다.
    """
    from conceptgate import server as SV
    monkeypatch.setattr(cg_owl, "_JAVA_PROBE", "/nonexistent/java")
    fn = getattr(SV, "classify_owl")
    fn = getattr(fn, "fn", None) or fn
    r = fn({"concepts": [{"name": "사변형", "features": [
        {"feature": "다각형", "type": "essential_feature",
         "evidence": "사변형은 다각형"}]}]})
    codes = [e["code"] for e in r["errors"]]
    assert "REASONER_DEPENDENCY_UNAVAILABLE" in codes, codes
    assert "REASONER_RUNTIME_FAILURE" not in codes
