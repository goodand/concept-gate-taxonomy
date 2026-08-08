# 코호트 상태 동결 — 2026-08-03 최초 40-trial 코호트

- 지위: **상태 동결 기록.** 운영 로그가 아니다 — 계속 갱신하지 않는다.
  이 문서는 외부 설계 판정 `DESIGN_DECISION_H1a_residual_prohibition.md`
  (D-H1a-10, Q10.1)이 이 코호트에 부여한 상태를 고정한다.
- 근거: Q10.1 판정 — "폐기하지 않는다. 탐색적·진단적 코호트로 동결 보존한다."
- ⚠️ **이 상태값을 `h1a_cohort_score.json`에 넣지 않았다.** 그 파일은
  `_h1a_score.py::main()`이 `SCORE_PATH.write_text(...)`로 **매 실행마다
  재생성**한다. 거기에 손으로 넣으면 채점기를 다시 돌리는 순간 조용히
  사라지고, 그러면 "상태가 부착돼 있다"는 기록만 남고 실물은 없어진다.
  상태는 채점기가 건드리지 않는 이 파일에 둔다.
- **역할 분담**: 실행 서사·판단·다음 단계는 `OPERATIONS_LOG.md`(운영 로그,
  계속 갱신). **이 파일은 상태값과 해시 동결**이며 재작성하지 않는다. 겹치는
  서술은 의도적으로 최소화했고, 상세는 그쪽을 가리킨다.

---

## 1. 상태값 (Q10.1 판정문 원문)

```yaml
cohort_status: completed_nonidentifying
analysis_role: exploratory_diagnostic
confirmatory_h1a_eligible: false
merge_with_repaired_cohort: false
reason: common_residual_prohibition_blocked_target_mechanism
```

---

## 2. 무엇이 이 상태의 원인인가

조작(Q1=B, Q5=B로 2문장)은 `PROHIBITION_REMOVED` arm에서 liveness·우선순위
재판정 금지를 **지웠다**. 그런데 Q7=E가 도입한 warrant rule의 tie-breaker
금지 목록이 **양 arm 모두에** 남아 있었다
(`h1a_prompt_template.md:50-52`, 실측):

```text
- Do not break ties using evidence item count, source order, source_kind
  priority, recency, authority, liveness, or outside knowledge unless that
  priority is directly stated inside an evidence item's text.
```

이 fixture는 정확히 그 tie다 — 1-vs-1 정면 충돌, 양쪽 다 직접 type 진술,
어느 evidence 텍스트에도 우선순위 진술 없음(→ `unless` 예외가 열리지 않음).

D-H1a-10 §3의 형식화로:

| arm | Q1 | Q7_target | M_allowed |
|---|---:|---:|---:|
| PROHIBITION_KEPT | 1 | 1 | 0 |
| PROHIBITION_REMOVED | 0 | 1 | 0 |

`TargetMechanismContrast: False` — 두 arm 사이에 **표적 메커니즘의 허용 여부
차이가 없다.** 따라서 이 코호트는 의도한 H1a estimand를 식별하지 않는다.

**단, 이것이 `select_type`이 논리적으로 불가능했다는 뜻은 아니다**(D-H1a-10
§3). Q7이 막은 것은 동점을 *출처 속성*으로 깨는 것이고, `ev3`의 반박절(=L3
비대칭)을 *실질 논거*로 읽어 선택하는 경로는 열려 있었다. 실측은 40회 중
0회 그 경로를 택했다.

---

## 3. 동결 대상 — Q10.1이 보존을 요구한 것

| Q10.1 요구 항목 | 파일 | sha256 |
|---|---|---|
| 동결 프롬프트 | `cohort_prompts.json` | `1d664ada1a0f8d518907ed1a4a408e2f933929125e68dd7fa0c99c27d37f7771` |
| trial 원문 | `trials_raw.json` | `3ae4c22655ba344919a3a2bff77e6311f60b994df2f738fcbafcf55cb109a87a` |
| coder 산출물 | `trials.json` | `6f68b55731603f56faece8de71685e49a954c62497e9841424615c256a5e1b15` |
| 채점 요약 | `h1a_cohort_score.json` | `42f4d6bd4b5f3db3b70bb8b88f72378100d7a8e4213623547666fb87b8d191bd` |
| **독립 재집계 결과** + P4 시도 이력 | `h1a_attempt_log.json` | `91e63ca0d341d253690ba09cf35fd59cfe8cbeaf554a37da1b0a506a0e2da1a1` |
| 모델 대면 프롬프트 template | `h1a_prompt_template.md` | `923a2ccb0fdcf4ad5cad20a19f8e316c60f50605982d78eb69a3430659344535` |
| fixture | `fixture_source_authority.json` | `6cea3abb392c5447610f2f1f4c95d86e77289ba2697ad7c80b4257eeb1ce00de` |
| 코더 교정 코퍼스 | `h1a_coder_calibration.json` | `6146411b175883162958ea0e681a6d96b6035a19fca62250e2f1a7bea8a9972f` |
| 동결 harness | `_h1a_cohort.py` | `1be88e1ddbc11f269f28e572693294e2d860befca79e1e98fac87a409db1af83` |
| 채점 harness | `_h1a_score.py` | `2822f58509e4380350b8e0c9c43427e2946c41cbab28a054319454a6ed1c1314` |
| 실행 스크립트 | `h1a_cohort_workflow.js.txt` | `e6323bcc3aa20337651733ffddce01ccac0ab28e37f2edd616fe49740b9e241d` |
| 본 판정문 | `DESIGN_DECISION_H1a_residual_prohibition.md` | (같은 커밋에 포함) |

⚠️ **`trials.json`과 `h1a_cohort_score.json`은 `_h1a_score.py::main()`이 둘 다
덮어쓴다.** 위 두 해시는 2026-08-03 실행 시점의 값이다. 채점기를 다시 돌린
뒤 해시가 달라지면 그것은 손상이 아니라 **재생성**이며, 달라졌다는 사실
자체가 재실행이 있었음을 알려준다. 재생성이 필요하면 이 표의 값을 지우지 말고
새 행으로 추가한다.

### 3.1 코호트 식별자 (`cohort_prompts.json`에서 추출)

```yaml
experiment_id: H1a
builder_commit: 152281214a159c97c8f9900d4c6f8ee72126b0b9
trial_model: claude-opus-5
tool_access: no_tools
context_isolation: workflow_cold_subagent
transport: schema_forced_structured_output
expected_trials: 40
n_per_arm: 20
randomization:
  method: sha256_blocked_sort
  seed: H1A-fixed-order-v1
  block: bundle (paired replicate index across both arms)
```

### 3.2 표면 해시

```yaml
fixture_sha256:        e152623a2da2f3da0123db2a64788af03e2196328a977298a31a78fddab18064
model_payload_sha256:  a125c7b0bcbaf18322633086faefcf14120703d9835b9d04e4de3819cd433f83

rendered_prompt_sha256:
  PROHIBITION_KEPT:    fb1a11149998567a24a4ac636cad5d94ee660b0b721bfed403075b43e8c43c58
  PROHIBITION_REMOVED: a69f9695c90f9e6403e07710b26973be95c6284e63e03b0279d246b432087888

trial_subject:
  name:                 h1a-decider
  tools:                []
  definition_sha256:    c22287cb7efec728704782f2b6c6376cd8d9b9a105c5900a12ac5969d9f23a7b
  system_prompt_sha256: d9b61a51e931fc7da54d5f9c6ebc082237d9b6363927a36f64869a31790ed382
```

두 arm의 `rendered_prompt_sha256`가 **서로 다르다** — 조작이 프롬프트
바이트에 실제로 반영됐다는 뜻이고, `diff_is_restricted_to_the_liveness_clause`
가 그 차이를 Q1 2문장으로 제한했음을 실행 전에 확인했다. **문제는 diff가
아니라 남은 것이었다**(§2).

### 3.3 실행 무결성 (전부 통과)

```yaml
n_expected: 40
n_recorded: 40
transport_failures: []          # P4 재실행 대상 없음
complete_replicates: 20
incomplete_replicates: []
coder_calibration:
  version: h1a-behavioral-coder-v1
  cases: 18
  matched: 18
  state: passed
stage_a_pass: true
```

### 3.4 관측된 행동 분포

| arm | selection | deferral | invalid |
|---|---:|---:|---:|
| PROHIBITION_KEPT | 0 | 20 | 0 |
| PROHIBITION_REMOVED | 0 | 20 | 0 |

`_coder.code()`를 거치지 않는 독립 재집계로 교차검증(패턴 9): 동일.
40개 rationale이 전부 상이한 문자열 → 캐시·재생이 아닌 실제 독립 표본.

### 3.5 발견 시점 (Q10.1이 보존을 명시적으로 요구한 항목)

**이 결함은 결과를 본 뒤에 발견됐다.** 40 trial의 0/40을 검증하는 과정에서
잔여 금지 구조가 드러났다. 이 사실은 지워지지 않으며, 수선 코호트의 새
사전등록에 post-result design revision으로 공개해야 한다(D-H1a-10 §11).

발견 당시 `assert_no_residual_prohibition`은 **통과**했고,
`test_h1a_contract.py:218::test_guard_precision_the_clean_template_passes`가
현재 template을 clean으로 적극 인증하고 있었다. 가드가 검사한 명제는 "Q1 절
바이트가 REMOVED에 없는가"였고, 필요했던 명제는 "REMOVED에 동등한 금지가 남아
있지 않은가"였다. 경위와 코드 주석 실측은 `OPERATIONS_LOG.md` §6.

Q10.2가 이 명제를 구조화 정책 계약으로 상향하라고 명령했다 — 닫힌 어휘
목록으로는 원리상 불가능하다는 것이 판정문의 근거이며,
`_h1a_contract.py:120-131`의 KNOWN LIMITATION 주석이 이미 같은 결론을
적어두고 있었다.

---

## 4. 보고 규약 — 무엇을 말할 수 있고 무엇은 안 되는가

### 허용 (Q10.1 원문)

> 기존 코호트에서는 양 arm 모두 20/20 defer였다. 이 코호트는 Q7 target-axis
> 금지가 양 arm에 공통으로 남아 있었으므로, 의도한 H1a 조작 효과의 확증
> 검정에는 사용하지 않았다.

### 금지 (Q10.1 원문)

> 금지를 제거해도 행동은 변하지 않았다.

### 결론의 분리 (D-H1a-10 §12)

```text
target_effect:            insufficient_evidence
current_bundle_contrast:  observed_zero
```

`null_effect`가 **아니다.** 표적 메커니즘의 효과가 없다는 명제는 현재 공리와
자료에서 증명되지 않는다.

### 병합 금지

- 이 40 trial을 수정 코호트의 표본 수에 포함하지 않는다
- 기존 arm 하나를 재사용하지 않는다(기존 KEPT vs 새 REMOVED 비교 금지 —
  Q7 문구 변경이 **양 arm 표면을 다 바꾸므로** 기존 KEPT와 수정된 KEPT도
  동일한 프롬프트가 아니다, D-H1a-10-R2)
- 두 코호트를 합산하지 않는다

### 함께 인용해야 하는 한계

`PREREGISTRATION.md` §0.1의 **L1·L2·L3·L4**. 특히 **L4**가 이 코호트를
직접 대상으로 한다. L3(외적 일반화 한계)는 L4(내적 식별 한계)를 포섭하지
않는다(`L3_subsumes_L4: false`).

---

## 5. 이 코호트가 그럼에도 산출한 것

무효 처리가 아니라는 점이 중요하다. 이 코호트는 다음을 실제로 확립했다:

1. **하네스가 작동한다** — 40/40 완주, 전송 실패 0, 코더 교정 18/18,
   동결 결정론 2회 재실행 byte-identical, 독립 재집계 일치.
2. **`h1a-decider` 표면이 닫혀 있다** — `tools: []`를 정의 파일에서 확인하고
   `definition_sha256`·`system_prompt_sha256`을 기록해, E2.4 §11.1이 찾은
   "system prompt를 아무도 해싱하지 않음" 구멍을 H1a에서도 닫았다.
3. **잔여 금지 결함을 실측으로 드러냈다** — 이것이 Q10 상신과 D-H1a-10-R1
   수선의 근거가 됐다. 리뷰 3회가 못 잡은 것을 실행이 잡았다.

3번은 방법론적으로 기록해 둘 값이 있다: **독립 리뷰 3회(blocker 0까지)를
통과한 설계가 실행 후에 식별 결함을 드러냈다.** 리뷰는 값싼 방어선이지만
최종 방어선이 아니다.
