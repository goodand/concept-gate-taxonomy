# 설계 판정 요청 — 검증 의무의 load-bearing 판별 (Q17)

- 작성: 2026-08-17
- 요청자: H1a 운영 세션
- 수신자: **저장소 접근이 없는 외부 설계 담당.** 판정에 필요한 실측을 전부
  본문에 embed했다.
- 계기: **D-H1a-16(Q16=A) 판정을 받았으나, 그 판정이 답한 질문의 틀 자체를
  다시 묻는다.** 사용자가 상위 목적을 명시적으로 재진술했고, 그 기준에서
  보면 Q16 요청서가 질문을 잘못 세웠을 가능성이 있다.
- 선행 판정: D-H1a-1~13, D-H1a-14/15, **D-H1a-16**(전부 구속력 유지)
- 실행된 confirmatory trial: **0건**
- 이 문서가 묻는 것: **Q17** (하위 Q17.1~Q17.2)

---

## 0. 한 줄 요약

**Q16 요청서는 "정본 공백을 어떻게 메울 것인가"를 물었고 D-H1a-16은 A(정본
확장)로 답했다. 그러나 그 질문은 "이 검증 의무가 실험의 상위 목적에
기여하는가"를 묻지 않았다.** 상위 목적 기준으로 재측정한 결과, 문제의 세 항목
중 최소 하나(`default_permission_applicability`)는 **어떤 인과 주장도 바꾸지
않는다** — 바꾸는 것은 그 주장을 누가 인증하느냐(기계 vs 리뷰어)다.

이 요청은 D-H1a-16을 뒤집자는 것이 아니다. **그 판정을 실행하기 전에, 실행
대상이 상위 목적에 load-bearing한지 판별 기준을 받고자 한다.**

---

## 1. 사용자가 재진술한 상위 목적 (2026-08-17, 원문)

> 정책은 문제되지 않는데 전체 아키텍처 입장에서 **실사용을 할 수 있어야**
> 합니다. 우리가 만들고 있는 도구의 **LLM의 생성의 재현성을 향상시키거나
> LLM의 생성을 제어하는 것보다는, LLM에게 피드백과 LLM의 출력을 기반으로
> 인과 추론을 하는 것이 중요**합니다.

즉 우선순위는:

```text
높음   LLM 출력 기반 인과 추론 · LLM에 주는 피드백
낮음   LLM 생성의 재현성 향상 · LLM 생성의 제어
```

H1a는 두 성격을 다 갖는다 — 프롬프트를 조작(제어)하고 출력 분포를 측정(인과
추론)한다. 제어는 인과 추론의 **수단**이지 목적이 아니다. 조작이 무엇인지
몰라도 되는 인과 주장은 없으므로 제어에 하한이 있다. 문제는 **상한**이다.

---

## 2. 실측 — 검증 장치와 산출의 비율

| 항목 | 실측 |
|---|---|
| 2026-08-16~17 신설 검증 장치 | **2,678줄** (semantic compiler·capability gate·policy audit·mutation pack·review protocol 및 그 테스트) |
| 실험 폴더 전체 | 9,332줄 (신설분이 **29%**) |
| 그 장치가 산출한 **인과 추론용 trial** | **0건** |
| 마지막 confirmatory trial | 40건(2026-08-03), D-H1a-10이 **비식별** 확정 |
| 수선 코호트 사전등록 이후 경과 | **12일**, `freeze_status: FREEZE_BLOCKED` 유지 |
| 그 사이 실행된 trial | qualification QF-SELECT 5건뿐 |

이 비율 자체가 판정 자료다. 검증 장치가 나쁘다는 뜻이 아니라, **검증
의무를 추가할 때마다 인과 증거 산출이 뒤로 밀린다**는 사실이 측정됐다는
뜻이다.

---

## 3. 인과 주장에 실제로 필요한 것 vs 그 위에 쌓인 것

H1a의 인과 주장은 하나다: *KEPT와 REMOVED의 select/defer 분포 차이가
Q1 절의 유무에 기인한다.* 그 주장이 성립하려면:

| 요건 | 무엇이 보장하나 | 상태 |
|---|---|---|
| ① arm 차이가 Q1 절 하나뿐 | `diff_is_restricted_to_the_liveness_clause` | 증명됨. 리뷰어 3명이 각자 독립 실측(`kept.replace(Q1,'',1) == removed`) |
| ② REMOVED에 잔여 금지 없음 | `assert_no_residual_prohibition` | 존재. **D-H1a-10의 실패가 정확히 이 항목이었다** |
| ③ 측정 오염 없음 | `_coder.code`가 구조만 읽고 `rationale` 안 읽음(P5) | 존재 |
| ④ 가드가 공허하지 않음 | `test_guard_negative_coverage.py` AST 게이트 | 존재 |

**semantic compiler가 더하는 것은 ①②의 독립 확인이다.** 이 저장소가 공허한
가드(`assert_5`)를 5차 리뷰까지 못 잡은 이력이 있으므로 독립 확인 자체는
값이 있다 — 실제로 mutation 테스트가 D-H1a-10형 결함을 재현 탐지했다.

**그런데 `default_permission_applicability`의 canonicalization은 ①~④ 어디에도
기여하지 않는다.** 그것이 바꾸는 것은 "REMOVED에서 표적 축이 허용된다"는
명제를 **compiler가 인증하느냐 리뷰어가 인증하느냐**이지, 그 명제의 참·거짓이
아니다. 두 경로 모두 이미 같은 결론에 도달했다(리뷰어 5명 전원, 그리고
`assert_4`+`assert_9`+arm-diff 증명).

---

## 4. 왜 Q16 요청서가 질문을 잘못 세웠는가

Q16은 이렇게 물었다: *정본에 기대값이 없는 target-critical 3개를 어떻게 할
것인가.* 선택지 A~E는 전부 **"어떻게 메울 것인가"**의 변형이었다.

묻지 않은 것: **그 세 항목이 target-critical이어야 하는 이유가 인과 추론에
있는가, 감사 완결성에 있는가.**

D-H1a-16은 C(target-critical 축소)를 이렇게 기각했다:

> 이것은 공백을 해결하는 게 아니라 **검사해야 할 집합을 줄이는 것**이다.

그 기각은 **target-critical 지정이 옳다는 전제** 위에서 타당하다. 이 요청은
그 전제를 검증 대상으로 올린다. 판정문 자신이 근거로 든 것도 licensed path
관여였다:

```text
LicensedPath = DefaultPermission ∧ RecordedFieldAccess ∧ ¬HardConflictToDefer
```

이 식은 **참**이다. 그러나 이 식의 각 항이 참임을 확인하는 데 필요한 것이
*정본의 기대값*인지, 아니면 *렌더된 문장의 실재 확인*인지는 별개 질문이다.
현재 세 항 모두 **렌더 문장의 실재가 리뷰어 5명과 구조 가드로 확인됐다.**

---

## 5. Q17 — 판별 기준을 묻는다

### Q17 (본질)

**검증 의무를 "인과 주장에 load-bearing"과 "감사 자동화"로 나누는 판별 기준을
제시해 달라.** 그리고 그 기준으로 문제의 세 항목을 분류해 달라.

| 안 | 내용 |
|---|---|
| **A** | 판별 기준을 두지 않는다 — target-critical로 선언된 것은 전부 정본 coverage가 있어야 한다(**D-H1a-16 그대로 실행**) |
| **B** | 판별 기준을 도입하고, load-bearing하지 않은 항목은 **정본 확장 없이 등재 한계**로 처리해 freeze를 연다 |
| **C** | 판별 기준을 도입하되 freeze는 계속 차단 — 확장은 하되 **코호트 실행과 병행**(순서를 직렬에서 병렬로) |
| **D** | 그 밖 |

**판정에 필요한 사실**: confirmatory trial 0건이므로 지금 정본을 고치는 비용은
가장 낮다(D-H1a-16의 지적, 타당). 반면 12일간 인과 증거 산출이 0인 것도 사실
이다. **어느 비용이 더 큰가는 상위 목적에 달렸고, 그 판단이 이 요청의 대상이다.**

### Q17.1 — 실사용 관점

이 도구(ConceptGate MCP, Render 배포)의 실제 루프는:

```text
LLM이 ontology 후보를 제안
      ↓
결정론적 검사가 의무(obligation)를 판정
      ↓
구조화된 피드백이 LLM에 반환
      ↓
LLM이 수정
```

**H1a가 연구하는 것은 이 루프의 계약 문구가 행동을 바꾸는가이다.**
그렇다면 H1a의 검증 장치 중 **어디까지가 이 루프의 신뢰성에 기여하고,
어디부터가 실험 내부 감사인가?** 특히 semantic compiler·capability gate·
mutation pack이 **산출물(MCP 도구) 쪽으로 재사용될 여지**가 있는지 —
있다면 지금의 투자는 실험 비용이 아니라 제품 자산이다.

### Q17.2 — `default_permission_applicability`의 정본 표현이 가능한가

D-H1a-16 Q16.2는 조건부 규칙을 정본에 표현하라고 했다. 그런데 이 항목은
조건부 규칙이 아니라 **메타 규칙**이다 — 다른 규칙을 어떻게 읽을지를 정한다:

> Within the supplied packet, a decision basis may be considered **unless this
> prompt explicitly prohibits it.**

현재 정본의 타입 체계는 `axis → {state, carrier}`이고, 상태를 갖는 것은
axis다. 이 절은 **carrier로 등록돼 있고**(`CARRIERS` 4개 중 하나),
`assert_4`가 "`allowed_by_default`는 반드시 이 carrier가 담는다"를 강제하며,
`assert_9`가 독립 golden contract에 대해 바이트를 고정한다. **즉 정본이 이
절에 대해 침묵하는 것이 아니라, carrier에는 상태 칸이 없다.**

`decision_semantics`로 상태 칸을 새로 만들 때 그 값을 **무엇에서 도출하는가**:

- (a) 승인된 텍스트에서 도출 — 문장 1이 `allowed_unless_explicitly_prohibited`를
  말하므로 전사(transcription). 그러나 승인 문구의 전사는 F6이 지적한 실패
  모드다("재등록은 범위만 바꾸는 것 같아도 규범 내용을 조용히 바꿀 수 있다")
- (b) 참조로 도출 — 정본이 값을 갖지 않고 `derived_from: GLOBAL_DEFAULT_PERMISSION_TEXT`를
  가리키고, 테스트가 그 문장이 여전히 그렇게 말하는지 검증. 단일 정본 유지
- (c) 새로 저작 — **운영 세션이 해서는 안 되는 것**(D-H1a-16 new_constraint 9의
  취지)

**(b)가 형식적으로 성립하는가?** 정본이 값 대신 참조를 갖는 것이
"canonical expected state가 존재한다"를 만족하는가, 아니면 순환인가?

---

## 6. 넘을 수 없는 제약

1. D-H1a-16의 new_constraints 12개는 구속력 유지 — 이 요청은 그 **적용 범위**를
   묻는 것이지 무효화가 아니다
2. 운영 세션은 정책을 저작하지 않는다
3. `render_policy_block`은 `decision_semantics`를 읽지 않으므로 정본 확장은
   **렌더 바이트 0 변경**(실측 확인) — golden contract 재동결 불필요
4. confirmatory trial 0건 — 재동결 비용 없음
5. `INDEPENDENT_SEMANTIC_REVIEW_PASSED = False` 유지 중
6. D-H1a-14/15 거버넌스: `freeze_blocker` ↔ `diagnostic` 이동은 외부 판정 전
   실행 금지 — **이 요청이 그 판정을 구하는 절차다**

## 7. 회신 형식

```text
DESIGN DECISION — H1a verification load-bearing
decided_by:
date:

Q17 (판별 기준):   <A|B|C|D>   근거:
  판별 기준(도입한다면):
  세 항목의 분류:
    conflict_to_defer_mapping:
    recorded_field_access:
    default_permission_applicability:

  Q17.1 실사용/제품 재사용 관점:
  Q17.2 정본 표현 방식 (a 전사 / b 참조 / c 저작 / 그 밖):

D-H1a-16과의 관계:
  <그대로 유지 | 적용 범위 한정 | 개정>   사유:

freeze:
  <계속 차단 | 조건부 해제 | 해제>   사유:

실험 진행 여부:
  <계속 | 재정의 필요 | 중단>   사유:
```
