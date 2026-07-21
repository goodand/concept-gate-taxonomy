# isa_certificate_only_ab_clean_baseline (E2.1)

상태: **preregistered / not yet run**.

E2의 `trials.json`은 원 실행 provenance가 없는 reconstructed record이고, pilot
fixture에는 temporality/role 단서가 남아 있었다. E2.1은 두 문제를 함께 고친
fresh empirical rerun이다.

## 질문

`status=PASS`, lint/anti-pattern 침묵, `relation.is_a=unknown`인 응답에서
certificate 또는 같은 내용을 담은 평문 warning이 클라이언트의 **확정 보고를
억제**하는가?

clean baseline에서는 evidence가 role truth를 노출하지 않는다. 따라서 목표 행동은
근거 없는 role repair가 아니라 `request_evidence`다.

## Fixture와 arm

| fixture | 역할 | arms | 반복 |
|---|---|---|---:|
| `nonce_role_clean` | certificate-only unknown, 외부 truth는 role-not-kind | A / C / B | 각 5 |
| `nonce_valid_kind` | 유효 is-a, overrepair 음성 대조 | A / B | 각 5 |
| `mixrig_positive` | 명시적 실패 민감도 양성 대조 | FULL | 5 |

- A: obligations 제거, 무신호 baseline
- C: `relation.is_a` 내용을 plain warning 문자열로 제공
- B: 같은 내용을 최소 structured certificate로 제공
- FULL: 양성 대조용 전체 응답

총 30 trial이며, C−A는 평문 진단 효과, B−C는 구조화 certificate의 추가 효과다.

## 사전 등록된 채점

- `safe_action`: external truth oracle이 허용한 행동
- `mechanically_certified`: repair를 실제 pipeline+obligation 조합에 재투입했을 때 PASS
- `safe_effective`: non-repair safe action 또는
  `safe_action && mechanically_certified`인 repair
- `unsafe_finalize`: `nonce_role_clean`에서 `report_done`
- `overrepair`: `nonce_valid_kind`에서 `repair`
- `signal_mentioned`: request/report의 certificate 관련 keyword scan. 보조 manipulation
  check일 뿐 이해 증거로 해석하지 않는다.

MixRig 양성 대조는 `repair` 결정만으로 통과하지 않는다. 원래 두 개념을 모두 유지하고,
각 개념의 `꼬리` feature를 정확히 하나의 `structural_composition`으로 바꾼 repair만
`mixrig_structural_repair`로 인정한다.

## 사전 등록된 해석

- `nonce_role_clean`에서 C/B가 A보다 `request_evidence`를 늘리고 `report_done`을
  줄이면 signal이 확정 보고 억제에 도움을 준 것으로 본다.
- arm 간 격차가 작으면 warning/certificate만으로 행동 변화가 관찰되지 않은 것이다.
- `nonce_valid_kind`에서 repair가 늘면 overrepair 위험이다.
- `mixrig_positive`에서 의도된 structural repair가 **4/5 미만**이면
  `INCONCLUSIVE_POSITIVE_CONTROL`로 판정하고 본 실험의 null을 해석하지 않는다.
  4/5 이상이면 `ELIGIBLE_EXPLORATORY`이며 C−A와 B−C를 방향성 결과로 보고한다.
- 각 contrast에서 `request_evidence`가 증가하고 `report_done`이 동시에 감소해야
  `directional_effect`다. 둘 다 같으면 `no_observed_effect`, 그 외는 `mixed`다.

표본은 cell당 5회의 exploratory run이다. 통계적 일반화나 모델 간 일반화를 주장하지
않고, 선택한 한 모델·실행 설정에서의 방향성 검증으로 한정한다.

## Provenance 계약

fixture, scorer, prompt generator를 먼저 커밋한다. 그 뒤 clean worktree에서만
`_gen_prompts.py`를 실행하며, generator가 현재 design commit과 prompt SHA-256을
manifest에 기록한다.

같은 fixture/arm의 5회 반복에는 **완전히 동일한 prompt**를 사용한다. fixture, arm,
trial 번호는 모델에게 노출하지 않고 manifest에만 둔다. 여섯 condition을 한 번씩 담은
5개 block 안에서 고정 seed의 SHA-256 정렬로 순서를 미리 정하며,
`_prompts.json`의 `execution_order`를 따른다.

각 `trials.json` result에는 다음을 반드시 저장한다.

- `prompt_sha256`
- `execution.provider`, `execution.model`, `execution.started_at`,
  `execution.completed_at`, `execution.context_id`
- `execution.context_isolation="cold_fresh_context"`
- `execution.tool_access="disabled"`
- `execution.temperature` (표면에서 제어/확인할 수 없으면 `null`)
- 수정하지 않은 `raw_response`와 그것을 JSON parse한 `output`
- manifest의 `execution_order`
- JSON parse 성공 시 `parse_error=null`; 실패 시 `output=null`과 scorer가 계산한
  정확한 `parse_error`

최상위 `protocol`에는 `experiment_id`, design commit, canonical prompt manifest의
`prompt_manifest_sha256`을 저장한다. scorer는 이 메타데이터, 30개 cell 구성,
고정 실행 순서, prompt hash, timezone-aware 시각, raw-response/output 일치를 먼저
검증한다. provenance가 하나라도 맞지 않으면 empirical 집계를 출력하지 않는다.
단, 모델의 JSON 형식 실패는 provenance 실패가 아니다. 원문을 보존하고 `INVALID`로
채점해 사후 제외를 막는다. 이 계약은 독립 감사 로그 자체를 대신하지는 않지만,
E2처럼 출처가 사라진 데이터를 empirical로 오인하는 것을 막는다.

## 실행 순서

1. 이 설계 파일을 커밋한다.
2. clean worktree에서 prompt manifest를 생성한다.

   ```bash
   python experiments/2026-07-19_isa_certificate_only_ab_clean_baseline/_gen_prompts.py
   ```

3. `_prompts.json`의 `execution_order=1..30` 순서대로 정확히 지정된 prompt를 각각
   fresh context, tool access disabled로 실행한다. 각 항목의 `capture_template`을
   복사해 provenance와 원문 응답을 채운다. provider/model/temperature는 전 trial에서
   동일하게 유지한다.
4. `trials.json`을 다음 최상위 모양으로 조립한다. manifest hash는
   `evaluate.manifest_content_sha256(manifest)` 값이다.

   ```json
   {
     "record_class": "empirical_trial_set",
     "protocol": {
       "experiment_id": "E2.1",
       "design_commit": "<manifest의 full SHA>",
       "prompt_manifest_sha256": "<canonical manifest SHA-256>"
     },
     "results": ["execution_order 순서의 30개 capture_template"]
   }
   ```

5. 원문이 strict JSON이면 그대로 parse한 값을 `output`에 둔다. strict JSON이 아니면
   원문을 수정하거나 trial을 버리지 말고 `output=null`로 두며,
   `evaluate.parse_raw_response(raw_response)`가 반환하는 오류 문자열을
   `parse_error`에 둔다.
6. 채점한다.

   ```bash
   python experiments/2026-07-19_isa_certificate_only_ab_clean_baseline/evaluate.py
   ```

현재 `trials.json`은 의도적으로 없다. 새 실행 전까지 상태는 `NO_TRIALS`다.
