# 독립 의미 리뷰 — D-H1a-13 Q13.5 (2026-08-16)

- 대상: H1a 렌더 프롬프트 양 arm(payload 치환 완료), expected policy graph,
  compiler diff
- 절차: `_h1a_review_protocol.py`(코드화된 프로토콜)
- 리뷰어 5명, 배정 범위 선언 후 blinded mutation pack으로 자격 검증 → 자격
  통과자만 실물 아티팩트 판정
- 판정: **condition_11 충족 · condition_12 충족**

> ⚠️ 이 문서는 **기록**이다. `INDEPENDENT_SEMANTIC_REVIEW_PASSED` 플래그는
> 사람이 설정한다(`_h1a_review_protocol.py`가 그렇게 설계됐다). 이 리뷰가
> 그 플래그를 자동으로 바꾸지 않는다.

---

## 1. condition_11 — 리뷰어 자격 (통과)

| 요구 | 충족 |
|---|---|
| `reviewer_scope_declared` | ✅ 5개 범위 사전 선언 |
| `rendered_prompt_reviewed` | ✅ 양 arm 실물(payload 치환) |
| `expected_policy_graph_reviewed` | ✅ 정본 DSL 유래 기대 graph |
| `compiler_diff_reviewed` | ✅ 관측-기대 비교 결과 |
| `adversarial_mutation_pack_used` | ✅ blinded, clean packet 혼재 |

**자격 결과: 5/5 통과. 변이 6건 전원 탐지, 오탐 0, 누락 0.**

| 리뷰어 | 범위 | 탐지 |
|---|---|---|
| R1 | target axis | M1(잔여 금지 KO), M2(잔여 금지 EN) |
| R2 | referential | M3(dangling reference) |
| R3 | non-target axes | M4(presentation order 의미 확장) |
| R4 | evidence scope | M5(recorded fields 축소) |
| R5 | decision mapping | M6(conflict→defer 하드 매핑) |

## 2. condition_12 — 판정 (충족)

**자격 통과자 5명 전원 승인. blocker 0건, major 0건.** 각 리뷰어가 자기
범위의 target-critical 상태를 **compiler에 의존하지 않고 직접 독해로** 해소
했다고 명시했다.

핵심 확인 사항(리뷰어들이 독립적으로 실측):
- 양 arm 차이는 **Q1 liveness 절 단 하나**. `kept.replace(Q1,'',1) == removed`
- Q7 비표적 불릿·payload 모두 **바이트 동일**(payload sha256 `4f6cf263c7e6d061`)
- REMOVED의 `absent_verified`는 **침묵이 아니라 GLOBAL_DEFAULT 절이 적극
  담보**(R1·R2)
- payload가 양 arm 모두 **최종 위치**, 뒤에 지시문 없음 — R2가 1차에서 제기한
  trust-boundary 가설을 실물 확인 후 **스스로 철회**
- `unless the packet explicitly authorizes that basis` 예외는 실제 payload에
  발동 조건이 없어 미발동(R3)
- 옛 conflict→defer 문구가 `cohort_prompts.json`에 남아 있으나 **폐기된
  2026-08-03 코호트의 의도적 provenance**이며 live render 경로가 읽지 않음(R5)

## 3. 리뷰어가 찾은 계측(instrument) 결함

### 3.1 수정 완료 — 미입증 detector의 `agreed` 편입

**리뷰어 5명 중 4명(R1·R2·R4·R5)이 서로 독립적으로 같은 지점을 지적했고 R3도
같은 취지를 냈다.** `EVIDENCE_COUNT_PROHIBITION`이 capability report에는
`unproven`인데 동시에 `agreed`에 계상돼 커버리지를 과대 표시했다.

> "An instrument that has not demonstrated it can detect a family cannot earn
> an agreement claim about it." (R4)

수정: `agreed`(입증된 detector)와 `agreed_by_unproven_detector`로 분리.

**R2가 붙인 제약(이 문서가 준수함)**:
> "if the freeze record cites compiler_diff as independent confirmation for
> EVIDENCE_COUNT_PROHIBITION or GLOBAL_DEFAULT_PERMISSION, that citation is
> not sound."

→ 이 리뷰는 그 두 family에 대해 **compiler를 근거로 인용하지 않는다.**
해당 상태는 R2·R4·R5의 직접 독해로 해소됐다.

### 3.2 미수정 — 다음 세션 이관

1. **정본 DSL에 기대값이 없는 target-critical family 3개**(R2·R4).
   `GLOBAL_DEFAULT_PERMISSION`·`RECORDED_FIELDS_ACCESS`·`TEXT_TYPE_SUPPORT_RULE`은
   `expected_state: null`이라 **compiler로는 구조적으로 반증 불가**하고 오직
   리뷰어 독해로만 해소된다. 특히 `GLOBAL_DEFAULT_PERMISSION`은 REMOVED의
   target-critical `absent_verified`를 담보하는 **유일한 carrier**인데
   compiler가 판정을 보류하는 자리다 — 정본이 template-level 규칙을 담지
   않는 데서 오는 상류 공백이다.
2. **분기 상보성(branch complementarity)을 표현하는 family가 없다**(R5).
   conflict→defer 하드 매핑 부재는 필요조건이지 충분조건이 아닌데, compiler
   어휘에 select/defer 분기가 결과 공간을 분할하는지 검사할 수단이 없다.
3. **조건부 carve-out의 payload 의존성**(R3). `unless the packet explicitly
   authorizes that basis`는 상태를 payload 의존으로 만드는데 compiler는 평면
   `present`로 보고한다. R3가 payload를 수동 확인했다 — 계측이 해야 할 일이다.

## 4. minor 소견 (차단 아님, 한계로 등재 권고)

- Q1 carrier가 영어 지시문 블록 중 **유일한 한국어 지시문**이라 조작에
  code-switch가 동반된다. 다만 concept/feature/evidence가 양 arm 모두 한국어라
  한국어 자체가 REMOVED에 새롭지 않다(R1)
- Q1 절이 outside-knowledge 문단에 **인라인 추가**돼 그 문단의 disclaimer가
  조작을 부분 중화하는 것으로 읽힐 여지(R4). 실패 방향은 **보수적**(효과를
  null 쪽으로 약화)
- Q7이 count/order를 **tie-break 역할에서만** 금지하고 일반 가중치로는
  금지하지 않는다. 본 코호트는 doc 1 / code 1로 균형이라 무력(R3)
- select/defer 분기가 축자적 상보가 아니다. 유일한 정합적 독해에서는 상보이며
  양 arm 동일 문구라 common-mode로 상쇄(R5)
- 줄바꿈 폭 비대칭 — Q1 절이 ~190자 한 줄로 렌더돼 표면 단서가 됨(R2)

## 5. 이 리뷰의 한계

- 리뷰어는 이 세션이 spawn한 subagent다. **배정 범위·자료·mutation pack을
  이 세션이 설계**했다. 프로토콜 코드화·blinding·자격 사전 채점으로 재량을
  줄였으나 범위 설계 자체는 여전히 제작자 손에 있다.
- 1차 실행에서 **제작자의 프로토콜 실행 결함 2건을 리뷰어가 잡았다**:
  condition_11이 별개로 나열한 `rendered_prompt_reviewed`와
  `adversarial_mutation_pack_used`를 합쳐 변이 패킷만 준 것, 그리고
  `{payload_json}` 미치환 템플릿을 준 것(R4). 둘 다 시정 후 2차 실행.
- 중간에 조직 지출 한도로 4명이 중단됐고 한도 복구 후 재실행했다. 자격
  검증(1차)은 재실행하지 않았다 — 이미 통과했고 대상이 바뀌지 않았다.
