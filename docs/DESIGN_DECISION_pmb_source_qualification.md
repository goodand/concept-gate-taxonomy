# DESIGN DECISION — D-E2E-v1-22: PMB source 자격 판정 (Q22)

- 사슬 항법: 이전 [[DESIGN_DECISION_o1_oracle_unit_and_coverage|D-21]] · **D-22** · 다음 [[DESIGN_DECISION_folio_second_source|D-23]] · 색인 [[RULING_CHAIN_INDEX]]
- 수령: 2026-08-23, 사용자 경유 (설계 담당, Wolfram MCP 형식 검토 명시)
- 상신 원문: `DESIGN_REQUEST_pmb_source_qualification.md` (Q22)
- 요지: **Q22.1=(b)** 다중 양화는 독립 제2 source가 담당(경계 축소 없음) /
  **Q22.2=(a) 제한적** — ¬∃¬→∀는 source-profile 결박 codec으로만(일반 논리
  재작성 금지), adapter 자격 7→9 / **Q22.3=(a\*)** WSD는 estimand 밖 —
  O1-PMB 평가 profile에서 lemma 정규화하되 술어 occurrence·arity·argument
  topology 보존(동일 lemma 노드 병합 금지, 커널 전역 정규화 금지) /
  **Q22.4** 제2 source 최소 5건·25%(load-bearing 최소치) + 다중 양화
  stratum floor 4/5. **PMB = QUALIFIED_PARTIAL_SOURCE** (최대 15건, 단독
  공급 불가).
- 검증: 수령 당일 6건 — 이 문서 말미 "수신 검증 기록". **판정 본문은 수신
  그대로이며 편집하지 않는다.**

---

## 판정 원문 (verbatim)

Wolfram MCP로 Q22의 네 쟁점을 형식 검토했습니다. 결론은 다음과 같습니다.

> **Q22.1 = (b)** — 다중 양화를 공급하는 제2 source를 추가합니다.
> **Q22.2 = (a), 단 source-specific definitional decoding으로 제한**합니다.
> **Q22.3 = (a*)** — WSD는 중립화하되, 단순 문자열 치환이 아니라 **lemma-normalized predicate identity + argument topology 보존**으로 제한합니다.
> **Q22.4 = “유의미 비율 포함”**으로 판정하되, 최소 **5/20 = 25%**를 요구합니다. 그리고 다중 양화 stratum에는 별도 **4/5 PASS floor**를 둡니다.

PMB 자체는 O1 source 후보 자격을 상당 부분 충족하지만, 현재 스캔에서 `multi_quantifier_scope`를 인스턴스화하지 못하므로 **PMB 단독으로 기존 O1 boundary 전체를 대표한다고 승인할 수는 없습니다.** 

---

# 1. Q22.1 — 다중 양화 부재

## 판정: **(b) 제2 source 추가**

현재 O1 boundary는 다섯 family를 명시합니다.

```text
quantifier_scope
generalized_quantifier
cardinal_quantifier
proportional_quantifier
multi_quantifier_scope
```

여기서 `multi_quantifier_scope`만 제거하면 단순 fixture composition 수정이 아니라 **측정 경계 자체가 좁아집니다.**

Wolfram 확인:

```text
RemovingMultiQuantifierChangesBoundary = True
FullBoundaryCount    = 5
ReducedBoundaryCount = 4
```

따라서 `(a)`를 선택하려면 사실상:

```text
O1-v1 ≠ 기존 O1
```

로 versioned estimand amendment를 해야 합니다.

현재는 그럴 이유가 없습니다. 이미 governance상 독립 제2 source도 필요한 상황이므로, **제2 source가 multi-quantifier material을 담당하게 하는 것이 두 문제를 동시에 해결**합니다.

---

# 2. N과 기존 16/20 threshold는 유지

다음은 변경하지 않습니다.

```yaml
N: 20
overall_PASS_min: 16
final_ERROR: 0
unexpected_UNSCORABLE: 0
primary_metric: DirectMatch
```

그러나 **fixture composition constraint를 추가**합니다.

권장:

```yaml
source_mix:
  PMB:
    max: 15
  independent_second_source:
    min: 5

multi_quantifier_scope:
  min_fixtures: 5
```

왜 최소 5인가를 Wolfram으로 계산했습니다.

현재 전체 gate는 16/20이므로 최대 실패 허용 수는 4입니다.

```text
second source = 4건
→ 그 4건을 전부 실패해도
→ PMB 16/16이면 16/20
→ 전체 PASS 가능
```

반면:

```text
second source = 5건
→ 그 5건을 전부 실패하면
→ 최대 15/20
→ 전체 gate를 통과할 수 없음
```

Wolfram 결과:

```text
MinimumIndependentSourceFixturesForCompleteSourceFailureToForceOverallFailure = 5
MinimumShare = 0.25

4 fixtures all fail → overall can still PASS = True
5 fixtures all fail → overall can still PASS = False
```

따라서 **25%는 임의 비율이 아니라, 독립 source가 acceptance에 실제로 load-bearing이 되는 최소 비율**입니다.

---

# 3. 그런데 5건 포함만으로는 부족하다

여기서 한 단계 더 필요합니다.

15 PMB + 5 multi-quantifier라고 하면:

```text
PMB       15/15 PASS
Multi      1/5 PASS
-------------------
Total     16/20 PASS
```

가 가능합니다.

Wolfram에서도:

```text
AllPMBPass_OnlyOneMultiPass_OverallPasses = True
```

입니다.

그러면 `multi_quantifier_scope`가 semantic boundary에 들어 있는데도 해당 family 성능이 20%여도 전체 O1을 PASS할 수 있습니다.

따라서 추가로:

```yaml
multi_quantifier_scope:
  N: 5
  PASS_min: 4
```

를 둡니다.

즉:

[
4/5=80%
]

의 동일한 engineering criterion을 family floor로 적용합니다.

### 최종 Stage 2 acceptance

```text
overall PASS >= 16/20
AND
multi_quantifier PASS >= 4/5
AND
final ERROR = 0
AND
unexpected UNSCORABLE = 0
```

이것은 population claim이 아니라 기존과 동일한 engineering gate입니다.

---

# 4. Q22.2 — `¬∃¬ → ∀`

## 판정: **(a), 단 매우 좁은 의미에서**

핵심 구분은 이것입니다.

```text
source formalism decoding
≠
general logical simplification
```

PMB/SBN 명세가 특정 paired-negation 구조를 **보편양화의 encoding 자체**로 정의한다면:

```text
SBN universal encoding
→ FORALL IR node
```

는 허용합니다.

반대로 Shared Kernel 또는 일반 canonicalizer가 임의의:

```text
NOT EXISTS NOT ...
```

를 찾아서:

```text
FORALL ...
```

로 논리적 동치 변환하는 것은 금지합니다.

---

## Wolfram에서 두 경우를 분리

source-specific decoder:

```text
documented PairedNegationTemplate
→ Forall
```

만 허용하고, 인접한 임의 `¬∃¬`는 거부하도록 모델링했습니다.

결과:

```text
DocumentedTemplateDecodes                 = True
NearbyArbitraryNegExistsNegNotDecoded     = True
GeneralLogicalRewriteWouldBeBroader       = True
```

따라서 `(a)`가 성립하려면 **source profile에 결박된 codec**이어야 합니다.

---

# 5. Q22.2 구현 계약

권장:

```yaml
decoder:
  profile: PMB_SBN_5_1
  rule: universal_via_documented_negation_pair

  scope:
    source_adapter_only: true

  forbidden:
    global_not_exists_not_rewrite: true
    theorem_simplification: true
```

qualification에 두 항목을 추가합니다.

### 8. documented universal decoding

정확한 SBN universal pattern이 `forall`로 복호되는지.

### 9. decode/re-encode round trip

```text
SBN universal pattern
→ canonical FORALL
→ reference SBN encoding
```

이 원래 구조와 alpha-equivalent인지.

그리고 반드시 negative controls:

```text
ordinary negation
nested existential negation
unrelated NOT/EXISTS pattern
```

이 `forall`로 오인되지 않아야 합니다.

---

# 6. 따라서 adapter qualification은 7 → 9

기존 Q21의 7개:

1. syntax parse
2. alpha rename invariance
3. quantifier-reordering negative control
4. binding preservation
5. deterministic replay
6. output schema validity
7. closed-form preservation

에 추가:

8. **source-defined universal decoding**
9. **universal encoding round-trip / negative discrimination**

을 둡니다.

이건 estimand 확장이 아니라 PMB source formalism을 정확히 project IR로 옮기기 위한 **Oracle Adapter qualification**입니다.

---

# 7. Q22.3 — WordNet synset와 WSD

## 단순 exact synset match는 기각

예:

```text
oracle: happy.a.01
subject: happy
```

에서 scope와 binding이 완전히 맞아도 exact match라면 FAIL입니다.

그러면 실제 estimand가:

[
QuantifierScope
+
WSD
]

가 됩니다.

이는 O1의 선언된 semantic boundary를 넘습니다. 

Wolfram counterexample도:

```text
ScopeCorrect = True
WSDCorrect   = False

ExactPredicateMatch = False
```

가 가능하므로,

```text
correct scope
↛ exact predicate score PASS
```

임을 확인합니다.

---

# 8. Q22.3 판정: **(a*)**

사용자 선택지 `(a)`의 방향은 맞습니다.

다만 단순:

```text
happy.a.01 → happy
```

를 global canonicalization으로 넣는 것은 조금 넓습니다.

권장 형태는:

> **PMB/O1 evaluation profile 내부에서 sense suffix를 제거한 lemma identity로 predicate를 비교하되, predicate node 자체와 argument incidence는 보존한다.**

즉:

### BEFORE

```text
happy.a.01(x)
```

vs

```text
happy(x)
```

→ FAIL

### AFTER

```text
predicate_label(happy.a.01)
→ normalized_label = happy
```

subject:

```text
predicate_label(happy)
→ normalized_label = happy
```

그리고 비교:

```text
same normalized predicate label
AND
same arity
AND
same argument topology
```

이면 label dimension은 일치.

---

# 9. 중요한 제한 — lemma가 같다고 predicate node를 합치지 않는다

예를 들어 한 문장에 sense가 다른 동일 lemma가 두 번 등장할 수 있습니다.

따라서:

```text
happy.a.01
happy.a.02
```

를 모두 문자열 `"happy"`로 바꾼 뒤 **동일 node로 merge**하면 안 됩니다.

허용:

```text
predicate_1:
  normalized_label: happy

predicate_2:
  normalized_label: happy
```

두 occurrence는 별도 node로 유지합니다.

즉:

```text
sense distinction ignored
≠
predicate occurrence identity collapsed
```

입니다.

---

# 10. 이 정규화는 Shared Kernel 전역 규칙이 아니다

위치도 중요합니다.

넣을 곳:

```text
O1 PMB evaluation/canonical comparison profile
```

넣지 않을 곳:

```text
Shared Semantic Kernel global canonicalizer
```

왜냐하면 다른 실험에서는 WSD가 실제 estimand일 수 있기 때문입니다.

따라서:

```yaml
predicate_label_profile:
  id: O1_PMB_LEMMA_NO_SENSE_V1

  remove:
    - wordnet_pos
    - sense_number

  preserve:
    - predicate_occurrence
    - arity
    - argument_edges
    - scope_position
```

형태가 좋습니다.

---

# 11. `predicate_arguments` 차원은 유지

Q22.3의 `(c)`처럼 predicate 차원을 완전히 제외하는 것은 권하지 않습니다.

이유는:

```text
dog(x) bites(y,x)
```

와

```text
dog(y) bites(x,y)
```

처럼 scope가 같더라도 predicate-argument binding이 틀린 출력을 구별해야 하기 때문입니다.

O1이 WSD를 시험할 필요는 없지만 **binding topology를 시험할 필요는 있습니다.**

따라서:

```text
sense identity → neutralized
predicate/argument topology → retained
```

이 맞습니다.

---

# 12. Q22.4 — PMB 단독 금지의 해소

## 판정: “20건 전부를 양쪽 source가 공급”할 필요는 없다

기존 governance의 의미는:

```text
PMB가 initial acceptance의 유일한 authority가 되지 않는다
```

이지:

```text
각 source가 10건씩 정확히 제공해야 한다
```

가 아닙니다.

따라서 **유의미한 독립 source 비율이면 충분**합니다.

다만 “유의미”를 모호하게 두면 안 되므로 앞서 계산한 load-bearing criterion을 그대로 사용합니다.

### 최소 조건

```yaml
independent_second_source:
  fixtures_min: 5
  share_min: 0.25
```

이렇게 해야 두 번째 source가 전멸할 경우 전체 acceptance도 반드시 실패합니다.

---

# 13. 제2 source의 독립성 조건

단순 다른 파일이면 안 됩니다.

다음이 필요합니다.

```yaml
second_source:
  different_corpus_authority: true
  independently_authored_gold: true
  not_derived_from_PMB: true
  not_project_generated: true
  separate_source_locator: true
  separate_adapter_profile_if_formalism_differs: true
```

즉:

```text
PMB re-export
PMB 변환판
PMB에서 우리가 생성한 pair
```

은 독립 source로 세지 않습니다.

---

# 14. 제2 source를 multi-quantifier에 쓰는 것을 승인

가장 자연스러운 구성은:

```text
PMB:                    15
Independent Source:      5
                         ──
Total:                   20
```

그리고 두 번째 source 5건은 모두:

```text
multi_quantifier_scope
```

를 인스턴스화합니다.

이렇게 하면:

1. PMB 단독 source 금지 해소
2. 기존 O1 `multi_quantifier_scope` boundary 보존
3. N=20 유지

세 가지를 한 번에 해결합니다.

---

# 15. 다만 source와 phenomenon이 confounded 된다

이 구성에서는:

```text
second source
≡
multi-quantifier fixtures
```

가 됩니다.

따라서 second-source 5개가 실패하면:

```text
multi-quantifier가 어려워서 실패?
OR
새 formalism adapter가 잘못돼서 실패?
```

를 바로 구별하기 어렵습니다.

이 문제를 main cohort를 늘려 해결할 필요는 없습니다.

### 별도 qualification controls를 둡니다

제2 source에서:

```text
2~4 simple single-quantifier controls
```

를 **Stage 2 N=20 밖의 source-adapter qualification**으로 두십시오.

이 controls는:

```text
새 source formalism
→ 우리 canonical IR
```

경로가 정상임을 검증합니다.

통과 후 main 5개 multi-quantifier를 실행합니다.

그러면 실패 attribution이 훨씬 좋아집니다.

---

# 16. 새로운 O1 cohort 구조

권장 최종 구조:

```yaml
O1_v1_cohort:

  qualification:
    PMB_adapter:
      required: PASS

    second_source_adapter:
      simple_quantifier_controls: ">=2"
      required: PASS

  confirmatory:
    N: 20

    PMB:
      N: 15
      phenomena:
        - single_quantifier
        - quantifier_negation_scope
        - cardinal
        - proportional_if_available

    independent_second_source:
      N: 5
      phenomenon:
        - multi_quantifier_scope

  acceptance:
    overall:
      PASS_min: 16

    multi_quantifier:
      PASS_min: 4
      N: 5

    final_ERROR: 0
    unexpected_UNSCORABLE: 0
```

---

# 17. PMB source qualification 상태

이번 Q22 결과를 반영하면:

```yaml
PMB_O1_source:

  sentence_level_1to1: PASS

  external_gold: PASS

  quantity: PASS

  quantifier_scope_relevance:
    single_quantifier: PASS
    quantifier_negation: PASS
    multi_quantifier: NOT_AVAILABLE

  source_formalism:
    universal_encoding:
      status: conditionally_supported
      requires_source_specific_decoder: true

  WSD:
    excluded_from_estimand: true

  O1_role:
    primary_but_not_sole_source: APPROVED
```

즉 **PMB 자체를 기각할 이유는 없습니다.**

단독 source만 기각합니다.

---

# 18. whitelist와 UNSCORABLE 규칙은 그대로

Q21 판정은 유지합니다.

freeze 전에 unsupported constructor를 만나면:

```text
INELIGIBLE
```

입니다.

freeze 후 예상하지 못한 unsupported constructor:

```text
UNEXPECTED_UNSCORABLE
```

입니다.

그리고 acceptance 실패입니다.

PMB의 `¬∃¬ universal`은 이번 Q22.2에서 **지원되는 source encoding pattern**으로 명시적으로 등록하므로 unsupported가 아닙니다.

---

# 19. constructor profile의 표현

다만 profile에는 단순히:

```text
FORALL
```

만 넣지 말고 source adapter capability도 분리해 기록하십시오.

```yaml
semantic_constructor_profile:
  allowed_IR:
    - FORALL
    - EXISTS
    - AND
    - PREDICATE_APPLICATION
    - ...

source_encoding_profiles:

  PMB_SBN:
    documented_encodings:
      universal:
        source_pattern: paired_negation
        target_IR: FORALL
```

이렇게 하면:

```text
IR semantic constructor
```

와:

```text
source syntax encoding
```

을 혼동하지 않습니다.

---

# 20. 최종 판정

```yaml
D_E2E_v1_22:

  Q22_1:
    decision: B

    multi_quantifier_scope:
      retain_in_estimand: true
      defer_to_O1_v2: false
      source: independent_second_source

    cohort:
      N: 20
      PMB_max: 15
      second_source_min: 5

    acceptance:
      overall_PASS_min: 16

      multi_quantifier:
        N_min: 5
        PASS_min: 4

      ERROR_final: 0
      unexpected_UNSCORABLE: 0

  Q22_2:
    decision: A

    paired_negation_to_forall:
      allowed: true
      classification: source_defined_syntax_decoding

    constraints:
      source_profile_specific: true
      generic_logical_rewrite: false
      arbitrary_not_exists_not_rewrite: forbidden

    adapter_qualification_additions:
      - documented_universal_pattern_decode
      - decode_reencode_round_trip_and_negative_controls

    qualification_count:
      previous: 7
      new: 9

  Q22_3:
    decision: A_STAR

    WSD:
      part_of_estimand: false

    normalization:
      scope: O1_PMB_evaluation_profile
      synset_to_lemma: true
      lowercase: true

    preserve:
      - predicate_occurrence_identity
      - predicate_arity
      - argument_topology
      - scope_position

    forbid:
      - merge_same_lemma_predicates
      - global_shared_kernel_WSD_normalization

    predicate_arguments_dimension:
      retain: true

  Q22_4:
    governance:
      PMB_only_initial_acceptance: forbidden

      second_source:
        minimum_fixtures: 5
        minimum_share: 0.25
        independently_authored: true
        not_PMB_derived: true

      second_source_role:
        multi_quantifier_scope: preferred

      second_source_adapter_qualification:
        simple_quantifier_controls: required
        counted_in_main_N: false

  PMB:
    O1_status: QUALIFIED_PARTIAL_SOURCE
    may_supply_all_20: false
    may_supply_up_to_15: true
```

## 핵심 판단

이번 PMB 스캔은 source 교체가 실패했다는 뜻이 아닙니다.

더 정확히는:

> **PMB는 O1-v1의 sentence-level single-quantifier / quantifier-negation material에는 적합하지만, 원래 O1 contract의 `multi_quantifier_scope`까지 혼자 담당할 수는 없다.**

따라서 semantic boundary를 줄이는 대신 **PMB 15 + 독립 multi-quantifier source 5**로 구성하는 것이 가장 작은 수정입니다.

그리고 `¬∃¬→∀`는 일반 논리 simplification으로 허용하는 것이 아니라 **PMB/SBN 형식이 명시한 source encoding을 project IR로 복호하는 Oracle Adapter 규칙**으로만 허용해야 합니다.

---

## 수신 검증 기록 (2026-08-23, 운영 세션 — 판정 본문 밖)

판정 본문 sha256 (이 절 추가 전 파일):
`2effb296f45cf27d1c526871f8212d81d18b2b8c23d8237432760f96b973f8c6`

| # | 판정의 반증가능 주장 | 검증 | 결과 |
|---|---|---|---|
| V1 | 제2 source 최소 5건 = load-bearing 최소치 (4건 전멸→전체 PASS 가능, 5건 전멸→불가) | **우리 채점 모듈(`_stage2_score`)로 합성 코호트 실측** — 16p+4f → accepted True, 15p+5f → accepted False | **일치** — 판정의 Wolfram 산술을 준비물 ④가 독립 재현 |
| V2 | 15 PMB PASS + multi 1/5로도 전체 16/20 PASS 가능(→ family floor 필요) | 같은 방법 | **일치** — floor의 필요성이 우리 코드에서 실증 |
| V3 | O1 boundary = 5 family, multi 제거는 경계 축소 | oracle manifest verbatim(이 세션 Q21 상신에 전문 인용) | **일치** |
| V4 | adapter 자격 7→9 | 기존 자격 기록은 wikisem adapter 코드(`e0c2d193…`)에 결박된 7항목 — SBN adapter는 신규 9항목으로 자격, 기존 기록과 무모순 | **무모순** |
| V5 | lemma 정규화는 O1-PMB 평가 profile 전용, 커널 금지 | `cg_ir`/`cg_evaluate`에 이름 정규화류 0건 실측 — 커널 §29 부정 계약과 정합, profile 배치가 유일한 무충돌 위치 | **정합** |
| V6 | 최종 YAML ↔ 산문 수치 일관성 | PMB_max 15 / second_min 5 / floor 4/5 / 16·0·0 대조 | **일관** |

적용 효과(판정이 명령한 것):

1. **cohort 구성 제약**: N=20 = PMB ≤15 + 독립 제2 source ≥5(전부 다중
   양화), 수용 = 16/20 ∧ **multi stratum 4/5** ∧ ERROR 0 ∧ 예상 밖
   UNSCORABLE 0. → `_stage2_score`에 stratum floor 확장 필요(별도 커밋).
2. **SBN adapter 자격 9항목** — 8: 문서화된 보편 패턴 복호, 9: 복호 왕복
   +음성 판별(일반 부정·중첩 존재 부정·무관 패턴이 ∀로 오인되지 않음).
   codec은 `PMB_SBN_5_1` source profile에 결박 — 커널·일반 canonicalizer의
   ¬∃¬ 재작성은 금지 유지.
3. **O1_PMB_LEMMA_NO_SENSE_V1 평가 profile** — synset→lemma+소문자,
   occurrence·arity·argument topology·scope 위치 보존, 동일 lemma 노드
   병합 금지. 커널 밖.
4. **제2 source 조사 필요** — 독립성 6조건(PMB 파생 금지·프로젝트 생성
   금지 포함), 다중 양화 gold, 문장 단위. 조사 채널(RESEARCH_REQUEST) 위임
   대상. source-adapter 자격용 단순 양화 control 2~4건은 N=20 밖.
5. constructor profile 표현: IR constructor와 source encoding profile을
   분리 기록(§19) — 사전등록 초안에 반영.
