# 설계 리뷰 정리 — cg_owl 동치 보고 + 코어 전략

- 작성 일시: 2026-07-16 01:40 UTC
- 원문: [`design_review_20260716_014000.md`](./design_review_20260716_014000.md)
- 목적: 리뷰어 피드백을 **행동 가능한 결정 항목**으로 압축. 원문은 길고 반복이 많아,
  여기서는 "무엇을 바꿀지 / 무엇을 안 바꿀지 / 미결정"만 남긴다.

---

## 0. 한 줄 결론

> 2-pass 제안은 **방향은 맞지만 형태가 위험**하다. `equivalences`는 노출하되,
> `hierarchy` 안에서 **부모를 동치 그룹으로 펼치지 말 것.** 최소 diff는
> "`hierarchy` 의미 유지 + `equivalence_groups` 필드 추가".

원래 우리 제안과의 핵심 차이:

| 항목 | 우리 원안 (2-pass) | 리뷰어 권고 |
|---|---|---|
| `equivalences` 노출 | ✅ 추가 | ✅ 동의 (`equivalence_groups`로 명명) |
| 부모 펼치기 | `RichEncoder → [Decoder, Encoder]` | ❌ **하지 말 것** — `hierarchy`가 quotient graph 의미를 잃음 |
| 대표(representative) | 없음 | ➕ `representatives` 맵 추가 권고 |
| 동치를 경고로? | 중립 보고만 | core는 중립, **MCP 표면에 diagnostic 분리** |

---

## 1. 즉시 반영 권고 (최소 diff)

리뷰어가 "가장 작은 diff"로 지목한 것. 우리 원안에서 **부모 펼치기만 빼면** 된다.

```json
{
  "hierarchy": { "RichEncoder": ["Decoder"] },   // ← 그대로 (펼치지 않음)
  "equivalence_groups": [["Encoder", "Decoder"]], // ← 추가
  "representatives": { "Encoder": "Decoder", "Decoder": "Decoder" }, // ← 권장
  "unsatisfiable": [],
  "stereotypes": {}
}
```

- **약점 A(동치 미보고)** → `equivalence_groups`로 해소.
- **약점 B(부모 일부 누락)** → 펼치기 대신 `representatives`로 quotient 정보를 주면,
  클라이언트가 필요 시 스스로 펼침. `hierarchy` 의미(직계 부모)는 보존.

## 2. 2-pass 구현 시 반드시 지킬 함정 6개

리뷰어가 열거한 것. `classify()` 재작성 시 체크리스트로 사용.

| # | 함정 | 대응 |
|---|---|---|
| A | 부모 펼치기가 `hierarchy` 의미(직계 부모)를 깨뜨림 | 펼치지 말 것 (§1) |
| B | `equivalent_to`에 anonymous restriction 섞임 | named class만 union-find, 표현식 노드 제외 |
| C | `Thing`/`Nothing`/import된 gUFO 클래스 혼입 | 부모 필터와 **동일한 hygiene**를 동치 수집에도 적용 (기존 `cg_owl.py:377-382` 필터 재사용) |
| D | 동치 그룹 내 stereotype 충돌 (한쪽 Kind, 한쪽 Phase) | 병합은 하되 `EQUIVALENCE_STEREOTYPE_CONFLICT` 진단 발행 |
| E | 대표 선택 비결정성 → 테스트/응답 diff 흔들림 | 결정적 규칙 고정 (예: lexicographically smallest) |
| F | alias cycle/self-parent 착시 | **quotient graph 먼저, alias 나중** 순서 엄수 |

## 3. 방어선 위치 (§5-3 답)

> **예방은 상류(map_owl/lint), 판정 결과 보고는 하류(classify).**

진짜 원인은 "has-a를 defined 정의에 밀어넣은 것" → reasoner 잘못이 아니라 **입력 모델링 오류**.
따라서 1차 방어선은 직렬화 직전 lint:

- `definition_kind = defined`인데 genus 없음/약함
- `differentia`가 전부 `∃hasPart.*`
- sibling 여럿이 동일 parthood differentia만 가짐

classify는 침묵하면 안 됨 (2차 방어선) — 상류 lint는 휴리스틱, 실제 동치는 reasoner만 최종 판정.

## 4. 미결정 — 사용자 판단 필요

리뷰어는 더 큰 재구성을 권했으나, **범위가 커서 별도 결정**이 필요하다.
CLAUDE.md의 "삭제 > 추가, 최소 diff" 원칙과 충돌 가능.

- **(가) facts / diagnostics / lint 3층 분리** — `classify()`를 `classify_facts()` +
  `diagnose_model()` + `lint_before_reasoning()`으로 찢기. **큰 변경.**
- **(나) `diagnose_model()` 진단 코드 도입** — `POSSIBLE_ACCIDENTAL_EQUIVALENCE`,
  `DEFINED_BY_PARTHOOD_ONLY`, `WEAK_GENUS` 등. MCP 표면에 warning 계층 추가.
- **(다) MCP 도구 분해** — `normalize_input / lint_model / build_ontology /
  classify_facts / diagnose_model / explain_collapse`. 현재 `run_pipeline` 중심 구조 변경.
- **(라) provenance (asserted vs inferred)** — 부모가 LLM 제안인지 HermiT 유도인지 구분.
  "LLM proposes, determinism judges" 표어엔 부합하나 추가 배관 필요.

> 리뷰어 자신도 (가)~(다)는 "구조를 정말 재설계할 생각이라면"이라는 조건을 달았다.
> 현재 목표(PR 머지 + 배포 검증)를 넘어서는 로드맵 항목으로 보류 권장.

## 5. 이번 결함과 무관한 코어 비판 (참고용, 이번 스코프 밖)

원문 전반부는 별도 세션의 코어 비판이다. 이번 동치 이슈와 직접 관련 없으나 기록:

- **코어는 label identity 기반 subsumption** (semantic 아님) — 의도된 범위 제한
- **surface-form signature 의존** — `PreDAGSignatureGate`/`PostDAGSiblingGate` exact-equality
- **semantic typing 하드코딩** (한국어 마커) — 설정 파일 분리 권고
- **heuristic fallback이 수렴 우선** — `"{개념명}_고유속성"` tautology 방지 필요
- **`verification_status`가 core `NormalizedFeature`에 없음** — 경계층 검증 정보 단절

이 항목들은 로드맵(1~3순위)으로 원문에 정리돼 있다.

---

## 다음 행동 제안

1. **§1 최소 diff만 우선 반영** — `equivalence_groups` + `representatives` 추가,
   `hierarchy` 불변. 함정 6개(§2) 준수. 테스트 P8로 고정.
2. §4(재구성)·§5(코어 비판)는 **별도 이슈로 백로그**. 지금 건드리지 않음.
3. 반영 후 배포 서버에 Encoder/Decoder 케이스 재실행 → `equivalence_groups`가
   실제로 내려오는지 원격 확인.
