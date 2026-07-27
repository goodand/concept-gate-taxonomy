# 문제 정의서 — `conflicting` class: 오라클 유출로 기존 검증 무효 + class 자체의 구성 가능성 의문

- 상태: **종결(미확보로 확정)**. 오라클 유출은 수정·가드 완료, N=5 실측
  완료, 처리 방향 사용자 결정 완료(§5.2). `conflicting_evidence`는 "현
  저장소의 live·동등강도 evidence로 구성 가능한 fixture 미확보"로 표시하고,
  E2.4는 유효 커버리지 **3 class**로 보고한다. Schema의 class는 유지.
- 작성: 2026-07-27
- 관련 파일: `fixture_conflicting.json`, `contract_prompt.md`,
  `decision_schema.json`, `evidence_packet_schema.json`, `test_protocol.py`
- 선행 문서: `PROBLEM_1_sufficient_consistent.md`(다른 class, 해결됨)

## 1. 한 줄 요약

`conflicting` fixture의 유일한 검증(N=1)은 **모델에게 정답을 알려준 상태에서
얻은 것**이라 무효다. 유출은 제거하고 기계적 가드를 넣었으나, 더 근본적인
문제가 드러났다 — 계약이 요구하는 `conflicting_evidence`의 성립 조건을
이 저장소의 실제 텍스트로 만족시킬 수 있는지 자체가 의문이다.

## 2. 발견 1 — 오라클 유출 (해결)

`ev5`의 `extraction_note`에 다음이 들어 있었다(원문):

> "...Kept as-is because it is still a genuine, real, directly-opposed pair of
> statements about the same referent, and **CONTRACT_REPO's correct behavior is
> still to abstain** rather than force a decision -- but **the expected
> contract_verdict is loosened to 'abstain via insufficient_evidence,
> conflicting_evidence, or out_of_scope (any of the three)'**..."

`ev6`의 note도 "Same caveat as ev5's note"로 이를 참조했다.

**왜 치명적인가**: `extraction_note`는 `evidence_items`의 필드이고,
`evidence_items`는 모델 payload에 그대로 들어간다. 즉 fixture가 모델에게
"abstain이 정답이다"라고 직접 알려주고 있었다.
`evidence_packet_schema.json`은 자기 description에 "hidden oracle fields must
not be included in model prompts"라고 명시하는데, 그 규칙을 이 fixture가
위반한 상태였다.

**조치**:
1. 양쪽 `extraction_note`를 인용 텍스트가 무엇을 말하는지만 서술하도록
   재작성(리뷰 이력·agent ID·기대 판정 전부 제거). `text_sha256`은 `text`만
   해싱하므로 무결성에는 영향 없음 — `test_protocol.py` 통과 유지 확인.
2. 나머지 3개 fixture 동일 스캔 — 전부 clean.
3. **기계적 가드 추가**: `test_protocol.py::test_model_facing_metadata_does_not_leak_the_oracle`.
   `extraction_note`/`locator`에서 decision·contract_verdict enum 토큰과
   기대 표명 구문(`correct behavior`, `expected contract_verdict`,
   `should abstain`, `hidden oracle`, `정답`, `기대 판정`)을 검출한다.
   음성 대조로 위 옛 유출 텍스트를 실제로 잡는지 확인함(토큰 4개 + 구문 적중).
   - bare `repair`는 의도적으로 제외 — ev5의 원 커밋이 실제로 "an available
     repair value"를 논하므로 불가피한 도메인 단어다.
   - 이 가드는 "self-citation은 고칠 때마다 다른 위치에서 재발하므로 주의력이
     아니라 기계적으로 막아야 한다"는 교훈의 적용이다.

**남은 것**: 유출 제거 후의 fixture에 대해 독립 리뷰와 N=5 스모크를 아직
못 돌렸다(API 세션 한도). 기존 N=1 결과는 폐기.

## 3. 발견 2 — `conflicting_evidence`는 양쪽 동등 강도를 요구한다 (미해결)

계약 텍스트를 정확히 읽으면:

- `contract_prompt.md` 규칙 3: "`conflicting`: 서로 양립 불가능한
  selected_type을 **직접 지지하는** evidence가 함께 있다"
- 같은 규칙의 `sufficient` 조건: "적어도 하나의 direct_support evidence가
  selected_type을 명시적으로 지지하고, **동등한** 직접 충돌 evidence가 없다"
- `decision_schema.json` semantic_constraints: "A feature judgment can be
  sufficient only when it cites at least one direct_support evidence item for
  selected_type and no conflicting direct evidence **of equal strength**"

즉 `conflicting_evidence`가 성립하려면 **양쪽이 모두 direct_support이고
강도가 동등**해야 한다. 한쪽이 강하고 다른 쪽이 약하면 그건 conflict가 아니라
"강한 쪽으로 sufficient"다.

### 3.1 현재 fixture는 이 조건을 만족하지 않을 가능성이 높다

현재 evidence는 E2.2.1/E2.2.2 커밋 메시지 쌍이다. 두 텍스트는 "directed-PC
실패 원인이 어휘 미노출인가, 미명시 구조 계약인가"를 두고 서로 반대 주장을
한다 — **사실 주장의 충돌은 진짜다.** 그러나:

- 판정 대상은 concept `directed_pc_실패원인_설명` / feature
  `vocabulary_기여도` = `essential_feature`다.
- 두 커밋 메시지 어디에도 `essential_feature`, rigidity, is-a, 부분-전체 같은
  **온톨로지적 성격에 대한 서술이 없다.** 실험이 왜 실패했는지를 논할 뿐이다.
- 규칙 2는 direct_support가 되려면 feature의 온톨로지적 성격을 **명시적으로
  서술**해야 한다고 요구한다.

따라서 정직한 감사 결과는 **양쪽 다 `out_of_scope`(또는 `indirect_context`)**
이고, 그러면 verdict는 `conflicting_evidence`가 아니라
`insufficient_evidence`/`out_of_scope`가 된다. **서로 모순되는 두 텍스트가
둘 다 feature-type 판정에 무관하면, type evidence로서는 충돌하지 않는다.**

이전 세션의 독립 리뷰가 이 점을 이미 지적했으나("서사적 충돌이지 FeatureType
충돌이 아니다"), 대응이 **evidence를 고치는 게 아니라 기대 오라클을 완화하는
것**이었고, 그 완화 문구가 §2의 오라클 유출이 됐다. 유출을 제거한 지금 이
문제는 다시 열려 있다.

## 4. 진짜 온톨로지 충돌 쌍 탐색 결과 (직접 조사)

`material_of` 관계를 두고 **실재하는 문서-코드 충돌**을 찾았다:

| 출처 | 주장 |
|---|---|
| `docs/phase_a_implementation_packet.md:102` | "(4) 재료-대상: **철은 칼의 재료 → essential_feature** (재료는 본질이 될 수 있음)" — 106행이 "재료-대상(4)만 essential_feature가 될 수 있습니다"로 강조 |
| `conceptgate/cg_partwhole.py` | `"material_of": "structural_composition"` + 주석이 문서의 논리를 **명시적으로 반박**: "Winston 1987의 stuff-object(재료-대상)는 meronymy이지 is-a가 아니다. '재료가 본질적일 수 있다'는 essentiality의 문제로 관계 타입과 별개 축이다" |
| `test_semantic_regressions.py` R6/R6b | 통과 중. R6b의 인스턴스가 **concept `칼`, feature `철`** — 문서의 "철은 칼의 재료"와 **동일한 concept/feature 쌍**이며 type은 `structural_composition` |

**놀랍게도 인스턴스까지 정확히 일치한다** — 문서와 테스트가 같은 `칼`/`철`에
대해 정반대 type을 주장한다. 양쪽 다 실제 저장소 텍스트이고, 양쪽 다
instance-bound이며, 이 E2.4 fixture와 무관하게 먼저 존재했다(C3/C4 통과).

### 4.1 그런데 이것도 조건을 만족하지 못한다

문서 쪽이 **liveness(C1)에서 탈락**한다:

- `test_semantic_regressions.py` 8행 헤더: "R6 `material_of`가
  `essential_feature`로 **오매핑되어 있었다** (Winston stuff-object는 has-a)"
  — 과거형. 즉 문서가 서술하는 매핑은 **수정된 버그 상태**다.
- `git log --follow`: 이 문서는 `4e0214c`("Add Phase ABC composition
  reasoning")에서 추가된 뒤 저장소 전체 리팩터(`cf58c8c`) 외에 손대지 않았다.
- `grep -rln "phase_a_implementation_packet"`: **참조하는 파일이 하나도 없다.**
  고립된 문서다.

따라서 엄격한 감사자는 문서 쪽을 `out_of_scope`/`indirect_context`로, 테스트
쪽을 `direct_support`로 평가할 것이고 → verdict는 `conflicting_evidence`가
아니라 "테스트 쪽으로 sufficient"가 된다.

## 5. 구조적 결론 (설계급 사안 — 사용자/설계 전문 판단 필요)

`conflicting_evidence`는 **양쪽 모두 라이브·인스턴스결박·동등강도인 두 개의
모순된 type 주장**을 요구한다. 그런데 실제 저장소가 그런 쌍을 보존할 이유가
없다 — 그건 곧 버그이고, 발견되면 고쳐진다. 실제로 이 저장소에서 찾은 두
사례 모두 "고쳐진 뒤 한쪽이 stale로 남은" 형태였다:

1. 위 §4의 문서-코드 충돌 (문서가 수정 전 상태를 기록, 고립됨)
2. `cg_input_linter.py`의 fallback dict가 `material_of`를
   `essential_feature`로 매핑해 canonical과 불일치했던 것 — **이건 라이브
   코드 대 라이브 코드 충돌이었으나 오늘 커밋 `c0e3bbb`에서 수정됐다.**
   즉 이 조사 직전까지는 진짜 conflict가 존재했다.

→ **선택지**:

- **(A) 현 fixture로 스모크를 돌려 실측한다.** 유출이 제거됐으니 결과는
  유효하다. 예상은 `insufficient_evidence`/`out_of_scope`이고, 그러면
  "이 fixture는 conflicting을 검증하지 못한다"가 데이터로 확정된다.
  비용 낮음, 정보 있음. **권고: 우선 이것부터.**
- **(B) §4의 문서-코드 쌍으로 재구성한다.** 인스턴스 일치가 완벽하다는
  장점이 있으나, 한쪽이 고립·superseded 문서라 동등강도 요건에서 걸릴
  가능성이 높다. 다만 "모델이 stale 문서를 만났을 때 독단으로 해결하지 않고
  보류하는가"는 그 자체로 **실무적으로 가치 있는 다른 질문**이다 — class
  정의를 그쪽으로 재해석할지는 설계 결정.
- **(C) `conflicting` class가 이 저장소에서 구성 불가능하다고 인정하고**
  E2.4의 커버리지를 3 class로 축소하거나, class 정의를 "동등강도 충돌" 대신
  "권위가 확정되지 않은 상충 출처"로 재정의한다. `README.md`의 class 표와
  `decision_schema.json`의 constraint 수정이 필요 → 설계급.

## 5.1 N=5 스모크 실측 결과 (2026-07-27, 유출 제거 후)

§5의 선택지 (A)를 실행했다. 유출이 제거된 packet으로 N=5.

| trial | decision | contract_verdict | ev5/ev6 admissibility |
|---|---|---|---|
| 1 | abstain | `insufficient_evidence` | out_of_scope / conflict |
| 2 | abstain | `insufficient_evidence` | out_of_scope / out_of_scope |
| 3 | abstain | `insufficient_evidence` | out_of_scope / conflict |
| 4 | abstain | **`conflicting_evidence`** | conflict / conflict |
| 5 | abstain | `insufficient_evidence` | out_of_scope / conflict |

**`decision`은 5/5 안정적으로 `abstain`. 그러나 `contract_verdict`는
불안정하다 — 4× `insufficient_evidence`, 1× `conflicting_evidence`.**

### 왜 verdict가 갈리는가 — 계약 텍스트의 해석 여지

4/5(trial 1,2,3,5)는 §3에서 도출한 것과 **독립적으로 동일한 엄격 해석**에
도달했다. trial 5가 이를 가장 명확히 언어화했다:

> "이 충돌은 selected_type을 직접 지지하는 두 evidence 간 충돌이 아니라
> **사실 귀인 충돌**이므로 contract_verdict를 conflicting_evidence로 만들지는
> 않지만, insufficiency를 더욱 강화한다."

즉 "두 텍스트가 사실 관계에서 서로 모순된다"와 "두 텍스트가 양립 불가능한
**type**을 각각 직접 지지한다"를 구분하고, 후자만 `conflicting_evidence`로
본 것이다. 이건 `semantic_constraints`의 "conflicting direct evidence **of
equal strength**"와 규칙 3의 "양립 불가능한 **selected_type을 직접 지지하는**
evidence"에 부합한다.

trial 4만 느슨하게 읽어 `conflicting_evidence`를 냈고, **그 응답 안에
내적 비일관성이 있다** — ev5/ev6를 둘 다 `conflict`로 두고
`conflicting_evidence`를 선택했으면서, 같은 응답에서 "neither provides
direct_support for any FeatureType"이라고 명시한다. 양쪽이 direct_support가
아니면 계약 정의상 `conflicting_evidence`가 성립하지 않는다.

**결론: verdict 불안정의 원인은 fixture가 아니라 계약 문구다.** 규칙 3이
`conflicting`을 "type 수준 충돌"로 한정한다는 것이 `semantic_constraints`에는
있지만 규칙 3 본문에는 충분히 못박혀 있지 않아, 소수 판정이 "사실 충돌"로
읽을 여지가 남는다.

### 채점에 대한 함의

`OPERATIONS_PLAN.md` Phase 6은 "단순 `decision` 일치가 아니라 기대
`contract_verdict`와의 일치"로 채점하도록 규정한다. 따라서:

- 오라클을 `conflicting_evidence`로 두면 → **1/5 (0.20)**, threshold 0.90에
  크게 미달
- 오라클을 `insufficient_evidence`로 두면 → **4/5 (0.80)**, 역시 0.90 미달
  (`docs/experiment_screening_protocol.md` 기준으로 escalate 구간)

**어느 쪽을 오라클로 잡아도 threshold를 넘지 못한다.** 이전 세션이 오라클을
"abstain이면 3개 verdict 아무거나 허용"으로 완화한 것은 정당한 채점 선택이
아니라 **이 불안정성을 은폐한 것**이었음이 실측으로 확인됐다(그 완화 문구가
동시에 §2의 오라클 유출이기도 했다).

### 부수 확인 — 계약이 표면 유사성 함정을 실제로 막았다

여러 trial이 두 가지 유혹을 명시적으로 거부했다:
1. ev5에 `structural_composition` 문자열이 등장하지만 "스키마에 노출되지
   않았던 enum 값에 대한 어휘적 언급"이므로 type 근거가 아니라고 판단
   (한 trial은 이를 "심볼명 기반 추론이라 금지"라고 정책을 직접 인용)
2. ev6의 "structural **contracts**"는 프롬프트/스키마 계약이지 taxonomy의
   부분-전체(`structural_composition`)가 아니라고 명확히 구분

이건 규칙 2의 전문용어 규율이 의도대로 작동한다는 독립적 방증이다 —
`conflicting` class 자체는 미커버지만, 메커니즘의 이 부분은 재확인됐다.

### 정리

- §5 (A) **완료**. `conflicting` class는 이 fixture로 **실질적으로 미커버**다.
  정직한 다수 판정은 `insufficient_evidence`이며, 이는 §3의 사전 논증과
  실측이 일치한 결과다.
- E2.4의 4개 class 중 `conflicting`만 여전히 미해결. 나머지 3개는 각각
  7/7, 5/5, 5/5로 검증됨.
- **새로 드러난 별도 사안**: 규칙 3의 `conflicting` 정의를 `semantic_constraints`
  수준으로 명확히 하지 않으면, 설령 진짜 conflicting fixture를 만들어도
  verdict가 갈릴 수 있다. 이건 fixture 문제와 독립적인 **계약 문구 개정
  사안**(설계급)이다.

## 5.2 결정 (2026-07-27, 사용자) — 미확보로 표시하고 별도 실험으로 분리

§5.1의 실측(다수 4/5가 `insufficient_evidence`)에 따라 사전에 정한 판정
규칙대로 **현 fixture는 `conflicting` class를 검증하지 못한 것으로 확정**한다.
그에 대한 처리는 다음과 같이 결정됐다.

1. **문서-코드 쌍(§4)으로 즉시 대체하지 않는다.** (B)를 지금 실행하지 않는다.
2. `conflicting_evidence`를 **"현 저장소의 live·동등강도 evidence로 구성
   가능한 fixture 미확보"**로 표시한다. 실패가 아니라 **미확보(未確保)**다 —
   메커니즘이 이 verdict를 낼 수 없다는 주장이 아니고, 이 저장소에서 그
   조건을 만족하는 재료를 찾지 못했다는 기록이다.
3. **E2.4의 유효 커버리지를 3개 class로 보고한다**
   (`sufficient_consistent` 7/7, `sufficient_repairable` 5/5,
   `insufficient` 5/5).
4. **Schema의 class 자체는 유지한다** — `decision_schema.json`의
   `contract_verdict` enum에서 `conflicting_evidence`를 제거하지 않는다.
   계약이 그 verdict를 표현할 수 있다는 사실과, 이 실험이 그것을 검증하는
   fixture를 확보했다는 사실은 별개다.
5. **stale 문서 대 live 코드의 충돌(§4)은 `source_authority_unresolved`
   계열의 별도 실험으로 분리한다.** §4에서 확보한 재료(문서
   `phase_a_implementation_packet.md:102`의 "철은 칼의 재료 →
   essential_feature" 대 R6b/`cg_partwhole.py`의 `structural_composition`,
   인스턴스까지 `칼`/`철`로 일치)는 폐기하지 않고 그 실험의 출발점으로
   보존한다. 그 실험이 묻는 질문은 이 실험의 것과 다르다 — "동등강도
   충돌에서 보류하는가"가 아니라 **"권위가 확정되지 않은 상충 출처를 만났을
   때 독단으로 해결하지 않는가"**다.

### 이 결정이 H3(본 3-arm 실험)에 미치는 영향 — 반드시 반영 필요

`OPERATIONS_PLAN.md` Phase 5의 커버리지 설계는 CONTROL_REPO/A_REPO에
**`sufficient_consistent` + "가장 어려운 class인 `conflicting`"** 2개를
배정했다. `conflicting`이 빠지면:

- **arm 비교의 최고 신호 셀이 사라진다.** 이 실험 전체를 동기부여한 유일한
  arm 비교 관측(초기 스모크에서 CONTROL/A_REPO는 조용히 repair, CONTRACT_REPO만
  abstain)이 바로 `conflicting` fixture에서 나온 것이다 — 그리고 그 관측은
  오라클 유출이 있던 packet에서 얻은 것이므로 **그 자체도 재현이 필요한
  상태**다.
- abstain-target class 중 남는 것은 `insufficient` 하나뿐이다. arm 비교를
  "정답이 abstain인 class"에 집중시키려면 이제 그 하나에 의존해야 한다.
- → Phase 5 커버리지 재설계가 선행돼야 한다. `conflicting` 자리에
  `insufficient`를 넣을지, `sufficient_repairable`을 넣을지, 또는
  `insufficient` 단독에 N을 늘릴지는 설계 결정이다.

## 6. 완료 기준 (Definition of Done)

- 오라클 유출 제거 + 기계적 가드 — **완료**
- N=5 스모크에서 안정적 abstain 확인 — **완료** (decision 5/5 abstain)
- `contract_verdict`가 실제로 무엇으로 나오는지 실측 기록 — **완료** (§5.1,
  4× insufficient_evidence / 1× conflicting_evidence, 불안정)
- (A)/(B)/(C) 중 처리 방향 결정 — **완료** (§5.2, 미확보 표시 + 별도 실험
  분리)
- 유출 제거 후 독립 리뷰 — 진행 중. 이 리뷰의 남은 가치는 대체 후보 판정이
  아니라(그건 §5.2로 분리됨) **유출 가드의 우회 가능성**과
  **`sufficient_repairable`의 scope note가 같은 종류의 유출인지**에 대한
  판단이다. 결과 도착 시 반영한다.

**이 문서 기준의 H1은 종료.** `conflicting`은 "미확보"로 확정 표시되고,
E2.4는 유효 커버리지 3 class로 보고된다.

### 이 문서에서 파생돼 다른 곳으로 넘어간 미결 사안

1. **`source_authority_unresolved` 계열 별도 실험** — §4의 재료로 §5.2-5의
   질문("권위 미확정 상충 출처를 독단으로 해결하지 않는가")을 검증. 이
   실험의 범위 밖.
2. **규칙 3의 `conflicting` 정의 명확화** (설계급) — `semantic_constraints`는
   "equal strength direct evidence"를 요구하는데 규칙 3 본문은 그만큼
   못박지 않아 소수 판정이 "사실 충돌"로 읽을 여지가 있다(§5.1). 위 별도
   실험이나 향후 conflicting fixture를 만들기 **전에** 정리하는 게 맞다.
3. **Phase 5 커버리지 재설계** (§5.2 하단) — arm 비교의 최고 신호 셀이
   사라진 것에 대한 대응.
