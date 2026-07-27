# 문제 정의서 — `conflicting` class: 오라클 유출로 기존 검증 무효 + class 자체의 구성 가능성 의문

- 상태: 미해결. H1(`docs/HANDOFF.md` §6) 진행 중 작성.
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

## 6. 완료 기준 (Definition of Done)

- 오라클 유출 제거 + 기계적 가드 — **완료**
- 유출 제거 후 독립 리뷰 통과 — 미완(세션 한도)
- N=5 스모크에서 안정적 abstain 확인 — 미완
- `contract_verdict`가 실제로 무엇으로 나오는지 실측 기록 — 미완
- `conflicting_evidence` 자체를 검증하는 fixture 확보, **또는** §5의 (B)/(C)
  중 하나를 사용자 결정으로 채택 — 미완
