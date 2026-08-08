---
name: adversarial-review
description: >-
  설계 문서에 대해 ground-truth-axis가 서로 다른 4개 독립 reviewer agent와 1개 lead
  합성 agent로 적대 검증팀을 구성한다. persona 분할이 아닌 근거 축 분할이므로 발견이
  서로 상관되지 않는다. 설계 제안서·아키텍처 문서·기능 명세를 채택 전에 검증할 때 사용한다.
---

# adversarial-review

설계 문서를 4개의 독립 근거 축에서 동시에 공격하고, lead가 합성·교차검증하는 검토 규율이다.

## 핵심 규칙

> **근거(ground truth)가 다른 agent는 같은 결함을 독립적으로 발견한다 — persona가 달라도
> 같은 근거를 보면 발견이 상관된다. 분리 기준은 '무엇에 대조하는가'다.**

## 1. Agent 구성 (4 reviewer + 1 lead)

| Agent | 검증 기준 | 권장 모델 | 특화 지시 |
|-------|-----------|-----------|-----------|
| A. 기준선 감사 | 현재 코드베이스 — 문서의 §1 기준선 주장을 file:line 대조 | Haiku (비용) | CONFIRMED/PARTIAL/REFUTED/UNVERIFIABLE만 출력; 코드 없는 finding 폐기 |
| B. 형식 건전성 | 해당 형식 이론 (OWL 2 DL / OntoClean / 범주론 / 논리 일관성) | Fable (추론) | 공리 위반·비-MECE 어휘·미정의 연산자 탐색; 직접 인용 필수 |
| C. 출처 검증 | 외부 논문·저장소 — 웹 실측 | Sonnet (검색) | URL/DOI 확인; 404·오인용·라이선스 미기재 탐지 |
| D. 실현 가능성 | 프로젝트 제약 (CLAUDE.md 규칙·로드맵·테스트 계약·배포 환경) | Fable (추론) | 현재 인프라로 불가한 설계 결정 탐지; Ponytail Rules 위반 계산 |

### Lead (합성)
- 4개 보고서를 수집한 후 finding severity 상위 7건을 코드·자산에서 **직접 재실측** (환각 방어)
- 충돌하는 평가(동일 finding, 다른 severity)는 더 보수적인 판정을 채택 + 사유 기록
- 합성 출력: TL;DR · 섹션별 verdict matrix · 채택 조건 목록 · 교차검증 기록

## 2. 출력 계약

모든 reviewer는 이 JSON 스키마로 finding을 보고한다:

```json
{
  "id": 1,
  "section": "§N",
  "claim": "문서가 주장하는 내용 (직접 인용 권장)",
  "verdict": "CONFIRMED | PARTIAL | REFUTED | UNVERIFIABLE",
  "evidence": "file:line 또는 DOI/URL 또는 공리 명칭",
  "severity": "blocker | major | minor",
  "note": "판정 근거 1–2줄"
}
```

**evidence 없는 finding은 즉시 폐기한다.** 이 규칙이 환각 전파를 막는 핵심 장치다.

## 3. Severity 기준

| 등급 | 기준 |
|------|------|
| blocker | 채택 불가 — 이 finding이 해소되지 않으면 문서를 실행할 수 없다 |
| major | 채택 전 재작성 필요 — 무시하면 예측 가능한 방식으로 실패한다 |
| minor | 채택 후 개선 가능 — 무시해도 즉각 실패하지 않는다 |

## 4. 실행 절차

```
1. 검토 대상 문서를 4개 agent에게 전달한다.
2. 각 agent에게 자신의 근거(ground truth)만 사용하도록 제한한다.
   (B agent는 코드베이스 접근 금지, C agent는 로컬 파일 접근 금지 등)
3. 4개 agent를 병렬로 실행한다.
4. Lead가 모든 보고서를 수집하고 finding severity Top-N을 직접 재실측한다.
5. 합성 결과를 docs/feedback/<문서명>_review_<YYYYMMDD>.md에 저장한다.
   - Part A: 합성 (TL;DR + verdict matrix + 채택 조건)
   - Part B: 4개 원본 보고서 전문 (선택, 로컬 전용 가능)
```

## 5. 안티패턴

- **persona 분할** ("비판적 reviewer", "호의적 reviewer"): 동일 근거를 보는 한 발견이 상관됨
- **evidence 없는 finding 허용**: 환각이 합성 단계까지 전파됨
- **Lead의 재실측 생략**: 가장 영향력 있는 finding이 환각일 수 있음
- **모든 agent를 동일한 강력한 모델로 실행**: 비용 최적화 없음 (A는 Haiku로 충분)
- **REFUTED 없이 CONFIRMED만 수집**: 문서가 자기 일관성만 확인하고 공격에서 살아남지 못함

## 6. 적용 범위

이 스킬이 가장 효과적인 문서 유형:
- 아키텍처 제안서 (새 모듈·계층 도입)
- 형식 언어 사용 설계 (OWL·Datalog·타입 시스템)
- 외부 라이브러리 도입 결정 (라이선스·성능·유지보수 부담)
- 로드맵 단계별 실현 가능성 검토

단순 버그 수정·코드 스타일 변경에는 `/code-review`가 적합하다.

## 근거

이 규율의 각 항목은 실제 검토에서 나왔다:
`docs/feedback/expansion_strategy_review_20260717.md` — ConceptGate semantic-to-OWL
compiler 확장 전략(§1~§18, 1169행) 검토. 4 agent × ground-truth-axis 분리 → 43 finding,
blocker 4건 발견. Lead 재실측 7건에서 환각 finding 0건.
