"""`BearerTokenAuth._check_token` 게이트.

## 무엇을 고쳤나

`_check_token` 의 docstring 은 **"fail-closed: HTTP 요청인데 헤더를 못 읽으면
거부"** 라고 적어 두고, 코드는 헤더 읽기가 실패하면 `return` 했다 — 즉
**통과**시켰다. 주석이 코드와 정반대였다(2026-08-25 적발).

그 경로가 지금 발동하지 않는다는 것은 확인했다(로컬 HTTP 실측·배포본 실측
모두 헤더를 정상으로 읽는다). 그러나 **발동하지 않는 fail-open 은 고쳐지지
않은 fail-open 이다** — fastmcp 판이 바뀌어 `get_http_headers` 가 다르게
행동하는 순간 인증이 통째로 열린다. 그리고 그때 아무도 모른다: 관측값이
"정상 통과"와 같기 때문이다.

## 왜 `MCP_TRANSPORT` 로 판단하나

`conceptgate/server.py` 의 `__main__` 이 그 환경변수로 transport 를 고른다.
같은 값으로 엄격도를 정하면 두 결정이 갈라지지 않는다.

## 음성 테스트가 이 파일의 전부다

인증 게이트는 **막아야 할 것을 막는지**로만 검증된다. 통과 경로만 시험하면
게이트를 통째로 지워도 초록이다.
"""
from __future__ import annotations

import pytest

from conceptgate import server as S


@pytest.fixture
def auth():
    return S.BearerTokenAuth()


def _headers(monkeypatch, value):
    """`get_http_headers` 를 원하는 동작으로 바꾼다 (server 모듈 이름공간)."""
    if isinstance(value, Exception):
        def boom(*a, **k):
            raise value
        monkeypatch.setattr(S, "get_http_headers", boom)
    else:
        monkeypatch.setattr(S, "get_http_headers", lambda *a, **k: value)


# ------------------------------------------------------------ 통과 경로 ---

def test_no_token_configured_allows(monkeypatch, auth):
    """토큰 미설정은 로컬 개발 — 인증하지 않는다."""
    monkeypatch.delenv("MCP_API_TOKEN", raising=False)
    _headers(monkeypatch, RuntimeError("no http context"))
    auth._check_token()          # 예외가 나면 실패


def test_valid_bearer_passes(monkeypatch, auth):
    monkeypatch.setenv("MCP_API_TOKEN", "s3cret")
    _headers(monkeypatch, {"authorization": "Bearer s3cret"})
    auth._check_token()


# ------------------------------------------------------------ 음성 경로 ---

def test_missing_bearer_is_denied(monkeypatch, auth):
    monkeypatch.setenv("MCP_API_TOKEN", "s3cret")
    _headers(monkeypatch, {})
    with pytest.raises(S.ToolError, match="missing Bearer token"):
        auth._check_token()


def test_wrong_token_is_denied(monkeypatch, auth):
    monkeypatch.setenv("MCP_API_TOKEN", "s3cret")
    _headers(monkeypatch, {"authorization": "Bearer wrong"})
    with pytest.raises(S.ToolError, match="invalid token"):
        auth._check_token()


def test_header_failure_under_http_is_denied(monkeypatch, auth):
    """**이 파일이 생긴 이유.** HTTP 인데 헤더를 못 읽으면 거부해야 한다.

    수리 전에는 여기서 `return` 해서 **인증이 통째로 열렸다.**
    """
    monkeypatch.setenv("MCP_API_TOKEN", "s3cret")
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    _headers(monkeypatch, RuntimeError("no request context"))
    with pytest.raises(S.ToolError, match="headers unavailable"):
        auth._check_token()


@pytest.mark.parametrize("value", ["HTTP", " http ", "Http"])
def test_http_detection_is_case_and_space_tolerant(monkeypatch, auth, value):
    """대소문자·공백으로 fail-open 으로 되돌아가지 않는다."""
    monkeypatch.setenv("MCP_API_TOKEN", "s3cret")
    monkeypatch.setenv("MCP_TRANSPORT", value)
    _headers(monkeypatch, RuntimeError("no request context"))
    with pytest.raises(S.ToolError):
        auth._check_token()


def test_header_failure_under_stdio_still_allows(monkeypatch, auth):
    """stdio 는 HTTP 컨텍스트가 없는 것이 정상 — 막으면 로컬이 못 쓴다."""
    monkeypatch.setenv("MCP_API_TOKEN", "s3cret")
    monkeypatch.delenv("MCP_TRANSPORT", raising=False)
    _headers(monkeypatch, RuntimeError("no request context"))
    auth._check_token()


def test_the_docstring_and_the_code_agree(monkeypatch, auth):
    """주석이 코드와 반대인 상태로 되돌아가지 못하게 고정한다.

    docstring 이 fail-closed 를 약속하면, HTTP 경로가 실제로 거부해야 한다.
    """
    doc = S.BearerTokenAuth.__doc__ or ""
    assert "fail-closed" in doc, "docstring 에서 fail-closed 약속이 사라졌다"
    monkeypatch.setenv("MCP_API_TOKEN", "s3cret")
    monkeypatch.setenv("MCP_TRANSPORT", "http")
    _headers(monkeypatch, RuntimeError("boom"))
    with pytest.raises(S.ToolError):
        auth._check_token()


def test_all_six_middleware_hooks_check_the_token():
    """훅 하나를 빠뜨리면 그 경로만 조용히 열린다."""
    import inspect
    for hook in ("on_call_tool", "on_read_resource", "on_get_prompt",
                 "on_list_tools", "on_list_resources", "on_list_prompts"):
        fn = getattr(S.BearerTokenAuth, hook, None)
        assert fn is not None, f"{hook} 훅이 없다"
        assert "_check_token" in inspect.getsource(fn), f"{hook} 이 토큰을 안 본다"
