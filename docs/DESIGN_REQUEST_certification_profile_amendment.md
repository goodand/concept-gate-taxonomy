# DESIGN REQUEST — 인증 프로파일에 새 필수 의무를 추가하는 절차 (Q38)

- 발신: 2026-09-01, 운영 세션 · 수신: 외부 설계 담당
- **판정자 전제: 저장소 접근 없음.** 자기완결적이다 — 인용·실측·재현 결과를
  전부 본문에 싣는다. 코드를 실행하거나 파일을 열 수 없다고 가정하고 썼다.
- **새 발견의 상신이 아니다.** 이 질문은 이미 우리 계약에 "별도 판단"으로
  유보해 둔 것이고(§2 인용), 그 예고된 판정을 청하는 것이다.
- 상태: **코호트 dispatch 누계 0건** 유지 · 발급되어 저장된 인증서 **0건**.
- 대상 층은 `conceptgate/` **제품 코드**이고 E2E-v1 Stage 2 실험 apparatus가
  아니다. 두 금지(`operational_patch` · `immediate_projection`)가 걸리는지는
  §3.4에서 우리 실측과 함께 올린다.

## 1. 계기 — 검사하던 명제가 우리가 생각한 명제가 아니었다

2026-09-01 사슬 감사에서 다음을 실측했다.

```text
원문(문서)   "돌체는 액체금속을 포함하지 않는다."
호출자 입력  evidence_texts = {"ev1": "돌체 는 액체금속 을 포함한다"}   ← 원문에 없는 문장
판정         claim.evidence_anchoring → PASS · RULE_CHECKED
```

`results_from_claim_anchoring(claims, evidence_texts)`는 호출자가 준 dict
**안에서** claim의 concept·feature 문자열이 등장하는지 본다. 그 dict가 문서와
아무 관계가 없어도 알 방법이 없다. 즉 검사되던 명제는

- 의도: `document ⊨ claim`
- 실제: **`호출자가 준 문장 ⊨ claim`**

이었다. 목적 계층에서 L2는 "document ⊨ formal model을 기계가 보증"이므로,
이것은 L2의 **뿌리**에 있는 공백이다.

**우리가 한 조치(판정 대상 아님, 보고)**: 새 의무
`claim.evidence_provenance`를 만들어 인용 본문을 **문서 snapshot에서 유도**
한다. 유도하면 위조는 존재할 자리가 없다(호출자가 줄 수 없으므로). span
검증은 기존 단일 출처 함수를 재사용했고, 계약 9개로 고정했다. 판정 결과:

| 입력 | 판정 |
|---|---|
| 선언된 span의 인용문이 문서와 불일치 | **FAIL** |
| 선언 span이 문서 범위 밖 | **FAIL** |
| 문서에서 유도된 인용 | PASS |
| 인용을 선언하지 않은 claim | UNKNOWN(부재는 위조가 아니다) |
| 해소를 시도하지 않은 인용 | UNKNOWN(부재와 미확인을 가른다) |

## 1a. 판정 재료 — 현행 프로파일 전문 (수신자가 볼 수 없으므로 그대로 싣는다)

우리 저장소의 인증 프로파일은 **하나뿐**이고 전문이 다음이다. 설계 지시 §15가
준 형태(`simple_source_relation_v0` 예시)를 그대로 따랐다.

```python
LEGACY_RELATION_PROFILE = CertificationProfile(
    profile_id="legacy_relation_claim_v0",
    applies_to_claim_kind="relation_assertion",
    required=(
        "source.snapshot_hash",      # 출처 무결성
        "source.span_evidence",      # span+quote+hash
        "claim.evidence_anchoring",  # 결정론적 어휘 결박
        "relation.antisymmetry",
        "relation.acyclicity",
        "relation.isa_hasa_exclusivity",
    ),
    allowed_na=("quantifier_scope", "modal_scope"),
)
```

인증 판정 규칙 전문(같은 모듈):

```python
def is_certified(profile, check_verdicts) -> bool:
    """claim is certified iff profile.required checks가 전부 PASS (지시 §15).

    없는 검사는 PASS가 아니다 — dict.get의 기본값이 UNKNOWN인 이유.
    '검사 안 됨'이 '통과'로 세탁되지 않는다는 이 모듈의 기존 원칙 그대로.
    """
    return all(check_verdicts.get(name, Verdict.UNKNOWN) is Verdict.PASS
               for name in profile.required)
```

**이 두 블록이 §4 질문 ㄱ·ㄷ의 판정 재료 전부다.** 제안하는 변경은 위
`required` 6-튜플에 `"claim.evidence_provenance"` 한 줄을 더하는 것이고,
`is_certified`의 기본값이 `UNKNOWN`이므로 그 검사를 돌리지 않은 호출은
**즉시** 미충족이 된다(§5 재현 C).

의무 이름의 뜻(수신자 기준 신규 어휘 둘만):

| 의무 | 검사하는 명제 |
|---|---|
| `claim.evidence_anchoring` | claim의 concept·feature 문자열이 **주어진** evidence 본문에 등장한다. 어휘 부재는 `UNKNOWN`(의미적 비지지의 증명이 아니므로 `FAIL`이 아니다) |
| `claim.evidence_provenance` **(신규)** | 인용 본문이 **문서 snapshot의 선언된 span에서 유도됐다**. 불일치는 `FAIL`(부재가 아니라 불일치의 적극적 증거) |

## 2. 그래서 생긴 질문 — 우리가 스스로 유보한 것

새 의무를 **레지스트리에는 등재**했으나 **인증 프로파일의 `required`에는
넣지 않았다.** 그 유보를 계약 자신이 기록하고 있다:

> **프로파일 `required`에 넣지 않았다.** 넣으면 기존 인증의 의미가 바뀐다
> (인증받던 claim들이 갑자기 미충족이 된다) — **그것은 별도 판단이다.**
>
> — `test_evidence_provenance.py:30-31` (우리 계약 문서, 2026-09-01)

그리고 그 유보를 **기계로 고정**했다 — 지금 `required`에 넣으면 이 테스트가
실패하므로, 변경은 반드시 이 테스트 수정을 동반하고 그 수정 자리가 곧 판정
인용 지점이 된다:

```python
def test_it_is_registered_but_not_yet_required_by_the_profile():
    assert "claim.evidence_provenance" in ob.OBLIGATION_REGISTRY
    assert "claim.evidence_provenance" not in ob.LEGACY_RELATION_PROFILE.required
```

## 3. 선행 확인 — 이미 다뤄진 것 다섯 (판정 청하지 않음)

이 절은 CLAUDE.md 규율(“모르는 것을 미해결로 단정하지 않는다”)에 따라,
**같은 문제를 이 저장소가 이미 다뤘는지** 먼저 찾은 결과다. 다섯 건은 이미
답이 있으므로 **문항에서 뺐다.**

### 3.1 “required를 늘리면 기존 인증이 무너지는 것”이 결함인가 — 이미 판정됨

E2.4에서 구조가 동일한 사건이 있었다(제약 #11이 `UNKNOWN`인 채 `certified
3/3`이 났고, 검증 항목이 하나 빠져 있었다). 채택된 판정:

> **중간 상태**: 채점기가 `certified 0/3`을 보고했다. **회귀가 아니라 D4가
> 지적한 상태를 처음으로 정직하게 표시한 것이었고**, 지시문 §3대로 검증
> 결과 없음이 통과가 아니라 차단으로 작동함을 보였다.
>
> — `docs/E2.4_ISSUE_REGISTER.md:169-171`

집행된 처분:

> **독립 리뷰어로 30 trial 전수 재검토. 새 trial 없음.** `clean`을 **4중
> 논리곱**으로 확장. 결과 30/30 `ok` → `certified 3/3` **복구**
>
> — 같은 문서 `:601`

→ **“소급 미충족”은 결함이 아니라 정직한 표시**이고, 처분은 **required 확장 +
기존 모집단 전수 재판정**이다. 이 부분은 다시 묻지 않는다.

### 3.2 개정 시 지켜야 할 절차 형태 — 이미 정본화됨

- `PRE_EXECUTION_FREEZE_AMENDMENT_V1`(D-24 §9): 7단 절차. `trigger`에
  **`frozen profile implementation mismatch`** 포함. 원본 동결 보존
  (`mutation_of_old_manifest: forbidden`), `record_amendment`에 defect·
  discovery_method·affected_contract·external_design_ruling·exact_before_after_diff
  필수.
- D-32 Q32.4: profile 변경 시 **“둘 다”** — amendment 절차 재사용 **+** 새
  버전 profile 신설(`O1_SCOPE_PROJECTION_V2`), `existing_fixtures retain:
  true`, `whole_cohort_reprojection: required`, `V1_V2_score_comparable: false`.

### 3.3 동결 표면이 이 변경에 걸리는가 — **걸리지 않는다(실측)**

동결 표면 11건(사전등록서 3종·fixture manifest 4종·freeze 스크립트 4종)과
manifest의 `contract_hashes` 8종을 전수 grep했다. `cg_obligations` ·
`LEGACY_RELATION` · `certify_relation_claims` · `CertificationProfile` →
**0건**. manifest의 `profile`/`profile_hash` 키는 실험의 **평가 프로파일**
(`O1_PMB_LEMMA_NO_SENSE_V1` 계열)이고 `CertificationProfile`과 **다른
이름공간**이다.

### 3.4 두 금지가 걸리는가 — **우리 읽기로는 걸리지 않는다(정정 대상)**

`operational_patch: forbidden`(D-33) · `immediate_projection: forbidden`
(D-34/D-35/D-37)의 원문 문맥을 전수 확인했다. 금지의 주체는 전부
**`boundary_definition`(measurand 경계)** 이고 대상은 referential ∃ 경계 ·
scope signature · 주석 층의 진리 승격이다. `conceptgate/`의 결정론적 의무
추가는 그 대상이 아니라고 읽는다.

**단서를 우리가 스스로 건다**: `claim.evidence_provenance`는 span/quote
유도라는 결정론 검사이고 **의미 경계를 긋지 않는다.** 그 경계를 계약으로
고정해 뒀다 — 유도된 본문으로 어휘 결박을 돌려도 **부정문 원문에서 PASS가
난다**는 것을 단언하는 테스트가 있다(§5 재현 E). 만약 이 의무가 semantic
support를 주장하기 시작하면 그때 `operational_patch`가 걸린다고 본다.

**이 읽기가 틀렸다면 그것이 이 요청의 첫 번째 답이다.**

### 3.5 인증 상태가 저장되는가 — **저장되지 않는다(질문의 형태를 바꾼다)**

- `certified_projection`은 **view이지 DB가 아니다**(설계 지시 §6 · `directive:I6`). asserted
  graph를 수정하지 않고 projection 멤버십만 결정한다.
- 설계 지시 §32.8 “이번 수정에서 하지 말 것” 8번: **“별도 Certified database를
  성급히 도입”** 금지.
- 실측: 저장된 인증서 파일 **0건**.

→ 따라서 “이미 발급된 인증서의 지위”라는 우리 초안 문항은 **형태가 부정확
했다.** 소급 무효화될 저장물이 없다. `required`를 늘리면 그 다음 호출부터
projection 멤버십이 줄어든다. 이 문항도 뺀다.

## 4. 새 질문 셋 — 이것만 판정을 청한다

하위 번호는 붙이지 않는다 — 문항 번호는 판정이 부여하는 것이 이 사슬의 관행이다(직전 상신 Q37도 그렇게 했다).

### 질문 ㄱ — `_v0` 제자리 확장인가, `_v1` 신설인가

우리 저장소에 **서로 다른 두 선례**가 있고, 어느 것이 `CertificationProfile`에
적용되는지 판정된 바 없다.

| 선례 | 처분 |
|---|---|
| D4 (§3.1) | 정의를 **제자리 확장**(`clean` → 4중 논리곱), 기존 모집단 전수 재판정 후 복구 |
| D-32 Q32.4 (§3.2) | **새 버전 profile 신설** + amendment 절차, 구/신 점수 비교 불가 선언 |

그리고 `PRE_EXECUTION_FREEZE_AMENDMENT_V1`의 전제조건이 걸림돌이다:

```yaml
prerequisites:
  cohort_execution_started: false
  confirmatory_outcomes_observed: false
```

즉 **“아직 아무것도 관측되지 않았을 때만”** 개정을 허용한다. `LEGACY_RELATION_
PROFILE`(`profile_id: legacy_relation_claim_v0`)은 배포된 MCP 도구의 계약이라
이 전제가 성립하는지 자체가 미판정이다.

**묻는 것**: `required`에 새 의무를 추가할 때 (a) `_v0`를 제자리 확장해도
되는가, (b) `_v1` 신설이 필수인가, (c) 조건에 따라 갈리는가 — 갈린다면 그
조건은 무엇인가.

### 질문 ㄴ — 서명된 인증서에 `profile`이 실리지 않는다

발급되는 서명 문서의 **서명 본체**는 다음뿐이다(실측, §5 재현 B):

```text
schema · issuer · subject_fingerprint · graph_revision · results[]
results[] 각 행: obligation · verdict · assurance · decider · evidence ·
                 reason · graph_revision · invariant
```

`profile`이 **없다.** 반면 응답 dict에는 `"profile": profile.profile_id`와
`"profile_required": [...]`가 실린다 — **서명 밖**이다.

결과: 과거 응답이 **어느 profile로 판정됐는지 서명으로 증명할 수 없다.**
기존 무효화 축은 `graph_revision`(claim 리비전)뿐이고, **profile 변화는 어느
축에도 나타나지 않는다.**

같은 파일에 선례가 있다 — 우리는 2026-08-31에 서명 본체가 바뀔 때 스키마
식별자를 올린 적이 있다:

> `CERTIFICATE_SCHEMA = "obligation_certificate_v1"` — v0 → v1: 서명 본체에
> invariant FQN이 추가되며 몸체 형태가 바뀌었다. … **올리지 않으면 나중에
> v0/v1 문서를 구별할 근거 자체가 없어진다.**

**묻는 것**: `profile`(또는 `profile_id` + `required` 해시)을 서명 본체에
넣어야 하는가. 넣는다면 그것은 스키마 개정(`obligation_certificate_v1` →
`_v2`)을 요구하는가. 넣지 않는다면, profile 개정 이력을 무엇이 담지하는가.

### 질문 ㄷ — 배포된 MCP 계약 변경이 “관측 후”인가

배포 도구의 docstring이 `legacy_relation_claim_v0`를 명시하고, 응답의
`profile_required`가 클라이언트에 노출된다. `required` 추가는 **배포된 도구의
관측 가능한 출력을 바꾼다**(`certified_claim_ids` 축소).

**묻는 것**: 실험 층의 “관측 전이면 개정 가능” 전제(질문 ㄱ의 prerequisites)를
제품 층에 옮길 수 있는가. 즉 **MCP 호출 이력이 실험의 dispatch에 상응하는가.**
상응한다면 이미 “관측 후”이므로 제자리 확장이 봉쇄된다.

## 5. 실측 자료 (재현 결과 원문)

판정자가 실행할 수 없으므로 결과를 그대로 싣는다. 전부 2026-09-01 실측.

| # | 무엇 | 결과 |
|---|---|---|
| A | 문서 결박 없는 PASS | 원문 “포함하지 **않는다**” + 날조 “포함한다” → `PASS` / `RULE_CHECKED`, 판정문에 snapshot 해시 참조 없음 |
| B | 인증서 서명 본체 | 최상위 키 6개(`graph_revision` `issuer` `results` `schema` `signature` `subject_fingerprint`) — `profile` **부재** |
| C | `required` 추가의 즉시 효과 | 현 6종에서 인증 `True` → provenance 추가 시 **같은 판정 집합에서 `False`**. 원인: 미실행 검사는 `UNKNOWN`이고 “없는 검사는 PASS가 아니다”가 이 모듈의 규약 |
| D | 결정의 크기 | 저장된 인증서 **0건**, 코호트 dispatch **0건** — 지금은 비용 0, 뒤로 갈수록 영구 |
| E | 의미 판정이 아님(우리 자기 제약) | 유도된 본문으로 어휘 결박을 돌리면 **부정문 원문에서도 PASS** — 계약으로 단언돼 있다 |
| F | 동결 표면 | FROZEN 11건 + `contract_hashes` 8종에 `cg_obligations` 참조 **0건** |
| G | 새 의무의 배선 | 레지스트리 등재 + 계약만 있고 **production 호출 0건** — 아직 배포 경로에 붙지 않았다 |
| H | 프로파일 수 | 1개(`legacy_relation_claim_v0`). `_v0` 접미는 설계 지시 §15의 예시 id(`simple_source_relation_v0` 등)에서 온 관례이고, **v1을 만드는 절차·조건은 지시문에 없다** |

## 6. 우리 권고 (비구속 — 앵커링 주의)

정하지 않는다. 다만 §5 D가 시간에 민감하므로 그 사실만 강조한다: **지금은
저장된 인증서가 0건이라 어느 선택도 소급 비용이 0이고, 발급이 시작되면
질문 ㄴ의 표현 공백이 영구화된다.**

## 7. 탐색 기록 — “미해결”이라고 쓴 근거

부재를 단정하기 전에 밟은 것(CLAUDE.md 규율):

- **코드 어휘 채취 후 `git log -S` 전 이력**: `recertif` · `reverif` ·
  `인증서 재검증` · `profile amendment` · `CERTIFICATION_PROFILE_AMENDMENT` ·
  `invalidate_certificates` · `프로파일 개정` → **git log -S로도 0건**.
- **그래프 순회**: 색인 freshness를 먼저 확인(초기 상태 `stale` ·
  `negative_claims_supported: false`)하고 **재구축 후 `fresh`**
  (2,381문서 · 간선 21,276 · `negative_claims_supported: true`)에서 조회.
  4턴 graph-deepen까지 돌렸다.
- **읽은 판정·규약**: 설계 지시 §15(profile 원설계)·§32.8(Certified DB 금지) ·
  D-24 §9(amendment 절차) · D-32 Q32.3/Q32.4 · D-33 · D-34 · D-35 · D-37 ·
  D-36 §“재료의 무효화와 측정 계약의 미완성 구분” · E2.4 이슈 등록부 D4 ·
  `DESIGN_DECISION_refine_verify_v0_review` 판정표.
- **새로 찾은 관련 자료(그래프가 찾았고 grep은 못 찾았다)**:
  `docs/KERNEL_INTEGRATION_SURVEY.md` §5. 수신자가 열 수 없으므로 원문을
  싣는다:

  > kernel 통합은 새 마일스톤이 아니라 **M1의 "핵심 실증 완료 + 재설계 대기"
  > 칸**이다. M1 재해석(E2.2.1~E2.2.3): certificate는 경고 신호가 아니라
  > **불변조건을 운반하는 reasoning contract**이고, 실증된 레버는 자연어
  > 불변조건(A_ONLY 20/20)이지 스키마 강제(C_ONLY 0/20)가 아니다.

  이 요청과 직접 충돌하지는 않으나, 질문 ㄴ이 “무엇을 서명에 싣는가”를
  다루므로 판정자가 함께 볼 가치가 있다고 보고 올린다 — 서명 본체가
  “불변조건을 운반하는 계약”이라면 `profile`(무엇을 요구했는가)의 부재가
  단순 표현 공백이 아닐 수 있다.
- **확인하지 못한 것**: `docs/H1A_PROBLEM_ANALYSIS.md`(2,800행 이상) 전문 ·
  `docs/feedback/` 회고 문서군 전문 · 원격 저장소의 더 최신 판정 유무.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 이 질문을 만든 계약: `test_evidence_provenance.py` §“무엇을 닫지 않는가” (코드 파일 — 링크 대상 아님)
- 목적 계층 정본 [[concept-gate-h1-wt/docs/obligation_layer_roadmap|obligation_layer_roadmap]] §목적 계층
- 절차 선례 [[DESIGN_DECISION_folio_predicate_labels|D-24]] §9 · [[DESIGN_DECISION_restriction_projection|D-32]] Q32.4
- 금지 범위 [[DESIGN_DECISION_referential_participant_quantification|D-33]] · [[DESIGN_DECISION_annotation_layer_admissibility|D-35]] · [[DESIGN_DECISION_r4_source_equivalence|D-37]]
- 직전 상신 [[DESIGN_REQUEST_r4_source_equivalence|Q37]]
- 새로 찾은 관련 자료 [[concept-gate-h1-wt/docs/KERNEL_INTEGRATION_SURVEY|KERNEL_INTEGRATION_SURVEY]] §5
