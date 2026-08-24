#!/bin/sh
# ConceptGate O1 Scope MCP 서버 런처.
#
# 왜 런처인가: Claude Desktop 설정에 인터프리터 경로와 cwd를 직접 적으면
# 그 설정이 정본이 되고 저장소가 그것을 모른다. 런처를 저장소에 두면
# 경로 결정이 버전 관리 대상이 된다.
#
# 인터프리터를 고정하는 이유: /usr/bin/python3 는 3.9 이고 fastmcp 가 없다.
# 실측(2026-08-24): homebrew python@3.13 = fastmcp 3.4.6.
set -eu

HERE=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PINNED="/opt/homebrew/opt/python@3.13/bin/python3.13"

if [ -x "$PINNED" ]; then
    PY="$PINNED"
else
    PY="python3"
fi

if ! "$PY" -c "import fastmcp" >/dev/null 2>&1; then
    printf '%s\n' "fastmcp 가 없다: $PY. 설치: $PY -m pip install fastmcp" >&2
    exit 127
fi

cd "$HERE"
exec "$PY" -m conceptgate.server_o1_scope "$@"
