---
name: verify-conceptgate
description: >-
  Verify a conceptgate change actually works before claiming "done" — run the
  5-suite, exercise the DEPLOYED Render MCP surface (not just local), and test
  the gUFO special path. Use whenever changing cg_owl / cg_normalizer /
  server.py, deploying to Render, or when a build/deploy log looks green but you
  have not yet observed the real output. Guards against false-green signals,
  stale docs/config, and untested special paths.
---

# verify-conceptgate

이 저장소에서 반복적으로 물렸던 함정 5종을 방지하는 검증 규율이다.
built-in `verify` 스킬의 conceptgate 특화판 — 범용 절차 대신 이 프로젝트의
실제 관측 경계(5종 스위트·Render MCP·gUFO 경로)를 구체 명령으로 못박는다.

## 핵심 규칙 (한 줄)

> **"완료"라고 말하기 전에, 기억·로그·빌드 성공 신호가 아니라 실제 관측
> 경계에서 결과를 눈으로 확인한다.**

이 세션에서 배포 "green 로그"가 반영을 뜻하지 않았고(옛 코드가 떠 있었음),
소스가 uncommitted라던 내 기억이 틀렸으며(이미 푸시됨), base case 통과가
gUFO 경로 버그를 못 잡았다. 전부 "신호 대신 실측"으로 풀렸다.

## 1. 검증 사다리 — 아래에서 위로, 각 단은 위를 대체하지 않는다

### (a) 로컬 5종 스위트 (전부 그린이어야 머지)

```bash
venv/bin/python -m pytest -q                        # 전체 (P8·P9 포함, ~91+)
venv/bin/python test_server.py                      # 73/73
venv/bin/python qa_v7.py                            # 101/101
venv/bin/python -m conceptgate.concept_gate_v7      # 60/60 (인라인)
venv/bin/python fuzz_normalizer_types.py            # total=209 CRASH=0
```

숫자는 테스트가 늘면 커진다 — 핵심은 **전부 pass + CRASH=0**. 특정 수치가
아니라 실패 0을 확인하라.

### (b) 로컬 MCP 표면 (in-memory FastMCP)

함수 직접호출이 통과해도 MCP 직렬화 경계(JSON, set/frozenset 누수)는 다르다.

```python
import asyncio; from fastmcp import Client
from conceptgate.server import mcp
async def main():
    async with Client(mcp) as c:
        r = await c.call_tool("classify_owl", {"owl": {...}})
        print(r.data)   # 실제 반환 필드를 눈으로 확인
asyncio.run(main())
```

### (c) 배포 서버 MCP (Render) — "배포됐다"의 유일한 증거

빌드 로그·"Deploy live"는 반영의 증거가 **아니다**. 배포 서버에 실제로
호출해 응답 필드를 확인하라. 번들 스크립트를 쓴다:

```bash
venv/bin/python .claude/skills/verify-conceptgate/scripts/render_mcp_smoke.py
```

이 스크립트는 5시나리오(단순 동치·gUFO 부모복원·전이 동치·동치없음·unsat
격리)를 세션 재초기화+재시도+백오프로 배포 서버에 친다. URL:
`https://concept-gate-taxonomy-docker.onrender.com/mcp`.

## 2. gUFO 특수경로를 항상 대조군으로 (가장 많은 버그가 여기서만)

`classify()`/OWL을 건드렸다면 stereotype **유/무 대조군**을 같이 돌려라.
base case(비-gUFO)는 멀쩡한데 gUFO import 경로에서만 깨진 사례:
- `INDIRECT_equivalent_to`가 명명 클래스 누락 → 직접 `equivalent_to` 사용
- HermiT가 동치류 부모를 대표에만 부여 → hierarchy 부모 유실(P9로 고정)

특수경로 버그는 반드시 `test_cg_owl.py`에 회귀(P-넘버)로 고정한다.

## 3. stale 참조 추적 — 코드만 고치고 방치 금지

`classify()` 출력이나 도구 계약을 바꾸면 아래를 **함께** 동기화:
- `conceptgate/server.py`의 도구 docstring (= MCP `tools/list` 설명으로 노출)
- `docs/mechanism.md` (출력 축·증명 표)
- `docs/MCP_SERVER.md` (도구 표)

패키지/디렉터리 구조를 바꾸면 Render 대시보드 설정도 확인:
- **Root Directory** (옛 `files` 경로가 삭제되면 배포 실패)
- **Branch** (main이 아닌 작업 브랜치를 배포하려면 여기서 바꿔야 함 —
  "Deploy latest commit"만으론 브랜치가 안 바뀐다)

## 4. 인프라 간헐 실패 → 재시도·우회

- Render Free: cold start ~20s, 재배포 중 세션 드롭. MCP 호출은 **세션
  재초기화 + 재시도 + 백오프**로 감싼다(번들 스크립트가 이미 그렇게 함).
- 네트워크 403(프록시 정책)·`git checkout -B` 분류기 차단·서브에이전트 세션
  한도·tool 스트림 실패는 이 환경에서 흔하다. 막히면 대체 경로로 진행하고,
  못 넘으면 사용자에게 정확한 사유를 보고한다(추측 금지).

## 5. 컨텍스트 단절 후 ground truth 재확립

"Continue from where you left off" 뒤에는 행동 전에 실제 상태부터 확인:

```bash
git status --short          # 작업트리 실제 상태 (기억 신뢰 금지)
git log --oneline -5        # 로컬 커밋
git log --oneline -5 origin/<branch>   # 원격 실제 상태
```

## 안티패턴 (하지 마라)

- 배포 로그가 green이라고 "반영됨"으로 단정 → 서버에 직접 호출해 필드 확인
- base case만 테스트하고 gUFO 경로 생략
- 코드만 고치고 docstring·mechanism.md·Render 설정 방치
- 라이브러리 편의 API를 실험 없이 신뢰(예: INDIRECT_equivalent_to)
- 컨텍스트 단절 후 기억으로 상태 가정

## 근거 (실제 사례)

이 규율의 각 항목은 실제 발견에서 나왔다:
`docs/feedback/adversarial_equivalence_20260716_041610.md` (발견 #1 gUFO
부모 유실 / #3 문서 stale).
