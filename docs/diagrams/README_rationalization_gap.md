# 합리화 공백의 해소 채널 — L0→L2 drill-down (2026-09-01)

- 대상: "명시하지 않은 계약의 공백을 합리화가 채운다"(KNOWHOW §C-0) 문제
  공간의 채널 분해 — structured output / 규칙 기반 / 자연어 계약, 그리고
  규칙 로직의 단순화 4건. 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 렌더러: `mcp-kroki` MCP(`download_diagram`, graphviz → SVG).
  **`.dot`이 canonical source, `.svg`는 렌더 산출물.**
- 방법: 각 층을 렌더 후 SVG 를 직접 READ 하고 코드·실측과 대조해 정합성을
  확인한 뒤에만 다음 층으로 내려갔다.

## 층

| 층 | 파일 | 내용 | 코드 정합성 |
|---|---|---|---|
| L0 | [`rationalization-gap-L0.dot`](rationalization-gap-L0.dot) → [svg](rationalization-gap-L0.svg) | (0)불변: 공백은 합리화가 채운다 · (1)목적 재귀 → L2 → L1 · (2)출력: 명시/판정/정직한 보류 · (3)채널 3종 · (4)집행 | **6/6** |
| L1 | [`rationalization-gap-L1.dot`](rationalization-gap-L1.dot) → [svg](rationalization-gap-L1.svg) | 문제 P1~P7 × 채널 매핑. 핵심: P2 는 유도(자연어)/판정(규칙)으로 갈라진다 | **코드 실명 4/4 실재 + RB5 전제 probe 증명**(돌체/돌체린 위반 검출) |
| L2 | [`rationalization-gap-L2.dot`](rationalization-gap-L2.dot) → [svg](rationalization-gap-L2.svg) | 단순화 S1~S4: 지금 배선 → 접힌 뒤 + 각각의 조건. S4 만 무조건(즉시) | 이중 경로 분기 2/2 · 3값 어휘 실재 확인 |

핵심 발견(S4): E2.2.1 의 hidden contract A(전역 type 일관성)는 LLM decider
없이 **결정론 obligation** 으로 등록 가능 — M1 재설계에서 semantic decider
의 필요 범위가 줄어든다. 단순화의 공통 형태: **삭제가 아니라 상류 계약이
강해질 때 하류 판별이 접히는 것** — 조건 미충족 상태에서 먼저 접으면 그
판별이 막던 실측 결함이 되돌아온다.
