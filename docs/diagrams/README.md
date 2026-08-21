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
