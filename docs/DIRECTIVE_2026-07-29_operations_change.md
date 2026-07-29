# 실험 운영 변경 지시 (2026-07-29) — 원문

- 수신: 2026-07-29, E2.4 실험 운영 세션
- 지위: **외부 실험 설계 담당이 보낸 지시문의 원문 보존본.** 해설·요약이 아니다.
- 왜 이 파일이 있는가: 이 지시문이 현재 E2.4 운영을 지배하는데, 저장소에는
  `docs/E2.4_ISSUE_REGISTER.md`의 **요약과 대조표**만 있고 원문이 없었다.
  2026-07-29 H1a 설계 적대 검증에서 "§3을 인용한 문장이 저장소에서 검증
  불가"라는 지적이 나왔고(reviewer C·A가 독립적으로), 실제로 `grep`한 결과
  원문이 어디에도 커밋돼 있지 않았다. 인용의 근거가 대화 로그에만 있으면
  후속 세션은 그것을 확인할 수 없다.
- 대응 기록: 8개 차단 조건 실측 대조표, ACK 회신, 충돌 3건(C1/D4/D5) 처리는
  [`E2.4_ISSUE_REGISTER.md`](E2.4_ISSUE_REGISTER.md) §0 참조.

---

이 지시는 기존 E2.4 실행·평가 지시를 대체합니다. 각 세션과 에이전트는 현재
작업을 아래 기준에 맞춰 재분류하고, 확인 응답 전까지 신규 trial을 실행하지
마세요.

## 1. 즉시 적용할 상태

- 기존 E2.4 실행 결과는 모두 legacy_leaky로 분류합니다.
- 기존 결과는 삭제하지 않지만 인증·성공률·class coverage 통계에서 제외합니다.
- 현재 인증된 class 수는 0입니다.
- conflicting_evidence class는 schema에서 유지하지만
  fixture_unavailable_unverified로 표시합니다.
- 기존 prompt 또는 수동 구성 payload를 사용한 재실행을 중지합니다.
- 기존 결과를 "재채점", "재현", "clean result"로 표현하지 마세요.

## 2. 신규 실행 차단 조건

다음 항목이 구현·검증되기 전에는 E2.4 신규 trial을 실행하지 마세요.

1. 제작용 fixture와 모델-facing payload의 분리
2. 정본 `build_model_payload()` 화이트리스트 builder
3. 실행 전 qualification gate
4. 모델 입력 필드의 닫힌 집합 적용
5. 실제 rendered prompt와 관련 스키마의 hash 기록
6. hidden-field noninterference 및 기존 유출문 positive-control 테스트
7. 저장소 루트에서 관련 테스트가 실제 수집·통과함을 확인
8. 모든 실행 경로가 동일한 canonical builder를 사용함을 확인

모델-facing evidence item의 허용 필드는 다음 세 개뿐입니다.

```json
{
  "evidence_id": "...",
  "source_kind": "...",
  "text": "..."
}
```

다음 정보는 모델에게 노출하면 안 됩니다.

- `source_path`
- `locator` 또는 `source_ref`
- `text_sha256`
- `builder_metadata`와 제작자 note
- qualification 결과
- liveness·authority·supersession 정보
- fixture class와 기대 판정
- oracle 또는 정답을 암시하는 자유서술

## 3. 책임 경계

- provenance, locator, 원문 일치, hash, liveness 및 evidence 적격성은 실행 전
  qualification 단계가 검증합니다.
- 모델은 evidence text가 대상 concept/feature의 type을 직접 지지하는지와
  evidence 사이의 의미 충돌만 판정합니다.
- 검증기를 실행할 수 없거나 검증 결과가 없으면 FAIL로 추정하지 말고
  UNKNOWN으로 기록하고 실행을 차단합니다.
- stale source와 live source의 권위 충돌은 E2.4 conflicting_evidence로
  처리하지 않습니다. 이는 향후 별도 source_authority_unresolved 실험
  대상입니다.

## 4. 재실행 기준

입력 표면과 builder가 동결된 후 기존 17 trials를 전부 새 cohort로 실행합니다.

정식 명칭:

```
clean rerun cohort
```

재실행마다 다음을 보존해야 합니다.

- raw model output
- fixture hash
- qualification manifest hash
- model payload hash
- contract prompt hash
- rendered prompt hash
- decision schema hash
- builder commit
- model과 실행 parameters

재실행 결과를 class별로 다시 인증하며, conflicting_evidence fixture가
확보되지 않는 한 최대 유효 coverage는 3개 class입니다.

## 5. 현재 진행 중인 작업 처리

각 세션은 현재 작업을 다음 중 하나로 응답하세요.

```
ACK
session/agent:
current task:
execution status: not_started | running | completed
affected artifacts:
legacy_leaky artifacts:
stopped actions:
uncommitted changes:
conflicts with this directive:
next safe action:
```

- 실행 중이면 가능한 안전한 지점에서 중단하고 부분 결과를
  non_certifying_partial로 보존하세요.
- 이미 완료했다면 사용한 실제 모델 입력 표면과 payload 생성 경로를 보고하세요.
- 설계와 충돌하는 구현을 발견해도 임의로 확장 수정하지 말고 충돌 사항으로
  보고하세요.
- 확인되지 않은 저장소 사실이나 다른 세션의 결과를 사실처럼 계승하지 마세요.

---

## 이 저장소의 대응 요약 (원문 아님 — 탐색용 포인터)

| 지시문 항목 | 이 저장소의 상태 |
|---|---|
| §1 `fixture_unavailable_unverified` 표기 | 반영됨 — `oracle_manifest.json` E24-F-04, 드리프트 가드 테스트 2건 |
| §2 차단 조건 8개 | **전부 충족** — 실측 대조표는 등록부 §0 |
| §2 금지 필드 14종 | payload 부재 전수 확인 (등록부 §0) |
| §3 UNKNOWN 규칙 | **D4의 근거.** 제약 #11이 UNKNOWN인데 인증이 났던 문제 → `_review_11.py`로 해소 중 |
| §3 stale/live 권위 충돌 분리 | H1a 실험으로 분리 — `experiments/2026-07-29_h1a_source_authority_unresolved/` |
| §4 "17 trials" | 사전등록 N=10/cell(=30)과 충돌 → D5. 단계적 조기중단 정책으로 해소 |
| §5 ACK | 등록부 §0의 ACK 블록 |
