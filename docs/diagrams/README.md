# Refine ↔ Verify 아키텍처 — Semantic Zoom 다이어그램

- 작성: 2026-08-22. 대상:
  [`../DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md`](../DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md)
  + [`../DESIGN_RESPONSE_refine_verify_gap_analysis.md`](../DESIGN_RESPONSE_refine_verify_gap_analysis.md)
- 렌더러: 등록된 `mcp-kroki` MCP 서버(`download_diagram`, mermaid → SVG).
  `.mmd`가 canonical source, `.svg`가 현재 확인된 렌더 — codex 실험
  `diagrams/` 규약과 동일
- **superseded된 legacy mermaid 소스는 보관하지 않고 삭제한다** (사용자 선호,
  2026-08-22). 이 폴더의 이전 판(`refine-verify-L0-context.*`)은 그 규칙으로
  제거됐다

## 왜 drill-down이 아니라 Semantic Zoom인가 (사용자 선호, 2026-08-22)

단순 drill-down은 단계마다 **상자가 늘어난다**. Semantic Zoom은 단계마다
**같은 시스템의 의미 레지스터가 바뀐다** — 모든 레벨이 동일한 불변 모듈
골격(Source · Refine · Semantic Graph · Verify · Certified Projection ·
Reason/Derive · Evaluate · Oracle · Shared Kernel)을 유지하고, 모듈은 레벨과
무관하게 **같은 색**이다(정체 연속성). 바뀌는 것은 라벨이 말하는 내용이다:

| 레벨 | 레지스터 | 같은 Refine 상자가 말하는 것 |
|---|---|---|
| [Z0](refine-verify-Z0-roles.svg) | **역할** — 동사 6개 | "proposes" |
| [Z1](refine-verify-Z1-authority.svg) | **권한** — §28 matrix | "graph 쓰기 유일 보유 · certify X · oracle X" |
| [Z2](refine-verify-Z2-mechanism.svg) | **기제** — 계약의 집행 수단 | "stale obligation 거부: revision 불일치 → STALE_OBLIGATION" |
| [Z3](refine-verify-Z3-asbuilt.svg) | **실체** — as-built vs delta | "= 클라이언트 LLM + assemble_concepts ○ / 수리 계약 X" |

## as-built 정직성 (codex diagrams README 선례를 따름)

Z0~Z2는 **지시문의 target 아키텍처**다. **Z3만이 as-built**이며, 빨간 점선이
아직 존재하지 않는 것(gap 분석 D1~D8)이다. Z0~Z2를 현재 코드의 서술로 읽으면
안 된다 — "다이어그램이 코드보다 앞서 있었다"가 codex 라인이 Amendment 36에서
겪고 기록한 실패 형태이고, 이 표기가 그 재발 방지다.

## 재렌더 방법

```bash
# mcp-kroki가 user scope에 등록돼 있다 (claude mcp list)
# 세션 도구로 안 보이면 stdio JSON-RPC로 직접:
python3 <scratchpad>/kroki_client.py render <file>.mmd <file>.svg
```

글리프 주의: kroki PNG/SVG 폰트에 ✕(U+2715)·✅·⚠ 가 없어 tofu가 된다 —
ASCII `X`, `○`(U+25CB), "주의:"를 쓴다 (2026-08-22 실측).

## 추상화 시 남기는 특성의 우선순위 (사용자 규약, 2026-08-23)

아키텍처 변경안은 **mcp-kroki graphviz 렌더 → SVG READ → 평가**로 표현을
검증한다. **가장 추상화된 그래프(L0)를 먼저 완료·검증한 뒤**에만 다음
레벨을 구체화한다(drill-down 순서, 레벨 간 골격은 위 Semantic Zoom 규약대로
불변). 실증: D-E2E-v1-24 amendment 설계에서 L2 구체화 단계가 "PMB verbatim
복사 ↔ 신규 profile_hash" 모순을 실행 전에 적발했다 — L0·L1에서는 보이지
않던 결함이다.

추상화 단계에서 **남기는(살아남는) 특성의 우선순위**:

| 순위 | 남기는 것 | 근거 예시 |
|---|---|---|
| (0) | 절대 불변인 것 (never modified) | 동결 커밋·SEED·N·임계값 |
| (1) | 궁극 목적·대상 — **상위 목적의 상위 목적을 재귀 추론**해 얻는다 | `concept-gate-taxonomy/docs/HANDOFF_EXPERIMENT_PURPOSE_HIERARCHY.md` (직접 목적→상위→상위의 상위 표) |
| (2) | expected_output | 산출물·상태 전이의 종점 |
| (3) | possible_conditions | 분기 조건 (BLOCKED·게이트 실패 등) |
| (4) | 기계 판정 가능한 확실성 (규칙 기반) | 해시 대조·결정론 선별 |

기본 레지스터는 **input-task-output**이다 — 실물 예시: 워크스페이스 루트
`diagrams/01-architecture.mmd`(`IN["입력: …"]` → 과제 대역 → `OUT["출력: …"]`),
`diagrams/03-stage-pipeline.mmd`. 우선순위 (0)~(4)에서 탈락한 세부는 하위
레벨(Z1~Z3)로 내려보내고, L0에는 위 표의 특성만 남긴다.
