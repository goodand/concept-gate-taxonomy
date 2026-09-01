# 의존 구조 — L0→L1 drill-down (2026-09-01)

- 대상: `conceptgate/` 패키지의 실제 의존 그래프와 그것을 지키는 격리 게이트.
  구조 조사 결론은 [[concept-gate-h1-wt/docs/HARNESS_KNOWHOW|HARNESS_KNOWHOW]] §C-1.
- 렌더러: `mcp-kroki` MCP(`download_diagram`, graphviz → SVG).
  **`.dot` 이 canonical source, `.svg` 는 렌더 산출물.**
- 방법: 각 층을 렌더 후 SVG 를 직접 READ 하고 **코드와 대조해 정합성을 평가한
  뒤에만** 다음 층으로 내려갔다. 두 층 모두 1차 평가에서 오차가 나와 정정했다 —
  그 정정이 이 방법의 값이다.

## 층

| 층 | 파일 | 내용 | 정합성 |
|---|---|---|---|
| L0 | [`dependency-L0.dot`](dependency-L0.dot) → [svg](dependency-L0.svg) | (0)불변: 정본 패키지 하나·수동목록 없음 · (1)목적: 두 벌 금지 → 층 격리 → 보증 사슬 · (2)DAG+닫힌 import 집합 · (3)배포/실험/테스트 도달의 3분 · (4)격리 게이트·등록부·AST | **4/4 (2차)** — 1차에서 "격리 게이트 5개"라 적었으나 실측은 **2형 5파일 6테스트**(닫힌 집합형 2 · 역방향 미import형 4)였다 |
| L1 | [`dependency-L1.dot`](dependency-L1.dot) → [svg](dependency-L1.svg) | 19모듈의 실제 간선(실선=최상위·점선=lazy), 3영역 분할, 격리 게이트가 지키는 자리 | **간선 14/14 · 행수 7/7 (2차)** — 1차에서 `cg_obligations` 1,145행이 실측 **1,166행**(정규화 수리로 증가)이라 정정 |

## 실측 요지

```text
배포 폐포(server):  server → {v7, graph_export, linter, obligations, normalizer} + lazy owl
                    obligations → {identity, _identifier_groups}
                    linter → partwhole · normalizer ⇢ linter · v7 ⇢ {partwhole, gufo}
순환 import: 0      층 역전: 0 (인터프리터 17모듈 전건 import + AST DAG 확인)
lazy import: 4곳    아무도 import 하지 않는 모듈: 9 (8은 실험·런처가 호출, 1은 테스트 전용)
```

이미지에 들어가지만 `server` 폐포 밖인 **9모듈 3,149행**은 결함이 아니라
`CLAUDE.md` 의 "수동 목록 없음" 설계의 대가다(§C-1). `cg_mrs_reader` 하나만
P21 형태(테스트 1·호출 0)라 채택 등록부에 등재해 처리했다.
