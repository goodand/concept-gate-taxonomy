# H3 공통 action 표면 + dispatcher (사전등록)

- 작성: 2026-07-29
- 지위: **사전등록**. 이 문서는 `_h3.py`가 어떤 trial도 얼리기(freeze) 전에
  커밋된다. 판정 기준을 결과를 본 뒤에 정하면 그것은 기준이 아니라 사후
  합리화다(같은 규율을 `DESIGN_D4_constraint_11_review.md`가 이미 적용했다).
- 근거: `DESIGN_DECISION_H3.md`(외부 설계 판정, decided_by: OpenAI Codex,
  2026-07-29) D-H3-1·D-H3-3·D-H3-4. `docs/E2.4_ISSUE_REGISTER.md` [DESIGN] D6.
- **동결 원칙**: `_surface.py`, `_cohort.py`, `contract_prompt.md`,
  `decision_schema.json`, 기존 4개 fixture, `_score.py`, `_review_11.py`는
  이 작업으로 **한 바이트도 바뀌지 않는다.** 새 파일만 추가한다.

## 1. 왜 이 문서가 필요한가

외부 판정은 native-schema 3-arm H3 실행을 승인하지 않았다 — legacy arm은
`abstain`을 표현할 수 없어, abstain 부재가 "판단 안 함"인지 "표현 못 함"인지
분해되지 않기 때문이다. 판정은 세 arm에 동일한 공통 action 표면
(`accept_report`/`repair`/`defer`)을 부여하고, 기존 whitelist builder를
공유하는 단일 dispatcher를 요구했다(D-H3-1, D-H3-4). 이 문서는 그 표면과
dispatcher를 실제로 얼리기 전에 설계를 고정한다.

## 2. 미판정 3건(Q1~Q3)의 처리 — 가정, 판정 아님

`DESIGN_DECISION_H3.md` §8.2가 표시만 하고 판정을 유보한 3건이다. 운영
세션이 임의로 "판정"하지 않는다는 규율은 유지하되, 이 3건은 실험적 타당성
질문이 아니라 판정문 자체의 예시 표기를 어떻게 읽을지에 대한 구현 판단이라
아래를 **가정으로 진행**한다 — pilot은 비인증이고 trial이 아직 0건이므로
재동결 비용이 없다. 사용자가 다르게 보면 이 문서와 스키마를 다시 얼리면
그만이다.

| # | 가정 | 근거 |
|---|---|---|
| Q1 | `report`는 **string** | 판정문 §4의 `"report": {}`는 `"repaired_concepts": []`·`"cited_evidence_ids": []`와 나란한 빈 값 예시로 읽는 편이 더 정합적이다. 두 기존 schema variant 모두 `report`는 지금까지 string이었고, 판정문 §2~§6 어디도 report의 내부 구조를 논하지 않는다 |
| Q2 | `cited_evidence_ids`는 **유효성 게이트**, 1차 지표 아님 | D-H3-3: "1차 결과에는 코더가 필요 없다"; estimand는 `action`만 쓴다. 미존재 evidence_id 인용은 schema-invalid로 invalid-output rate에 집계되고, 1차 Δ 계산에는 관여하지 않는다 |
| Q3 | pilot은 **제약 #11 리뷰를 실행하지 않는다** | #11 리뷰(`_review_11.py`)는 인증(certification) 게이트용 장치였다(D4). Pilot은 비인증이므로(D-H3-6) 이 단계에서 불필요. `contract_assessment`로 진단부를 재배치해도 무방 — 확증 실험에서 필요해지면 그때 경로를 다시 설계한다 |

## 3. 스키마 — `decision_schema_h3.json`

전문은 해당 파일 참조. 요지:

| variant | 사용 arm | 필드 |
|---|---|---|
| `h3_common_action` | CONTROL_REPO_H3, A_REPO_H3 | `action`(`accept_report`\|`repair`\|`defer`), `repaired_concepts`, `cited_evidence_ids`, `report` — 이 넷이 전부. 두 arm은 스키마가 **완전히 같다**(new_constraints: 차이는 프롬프트 규칙뿐) |
| `h3_contract_action` | CONTRACT_REPO_H3 | 위 4필드 + `contract_assessment`(구 `evidence_contract_v1`에서 `decision`·`report` 제거하고 나머지 그대로 이전: `contract_verdict`/`evidence_scope`/`evidence_audit`/`feature_judgments`/`invariant_checks`/`repair_plan`/`abstain`) |

`semantic_constraints`는 기존 11개를 필드 경로만 교체(`decision`→`action`,
`abstain`→`defer`, `contract_verdict`→`contract_assessment.contract_verdict`
등)하고, Q2를 12번째 항으로 명시했다. #11(liveness 비재판정)은
CONTRACT_REPO_H3의 `contract_assessment` rationale에만 적용된다 — CONTROL/A
프롬프트는 애초에 liveness 비재판정을 지시하지 않으므로(그 차이 자체가
연구 대상), 확장하지 않는다.

## 4. 프롬프트 구성 — `_h3.py: render_h3_prompt(arm, payload)`

세 arm 모두 **동일한 payload**(같은 fixture의 `qualify_fixture` +
`build_model_payload` 결과, 기존 `_surface.py` 재사용, 바이트 동일)를 받는다.
차이는 프롬프트 규칙 텍스트와 응답 schema뿐(new_constraints).

- **CONTROL_REPO_H3**: 6-type 온톨로지 vocab 힌트만. E2.3 `_gen_prompts.py`의
  `VOCAB_HINT`와 동일한 taxonomy를 이 실험 어휘로 재서술(전역 invariant
  규칙은 주지 않음 — README.md: "ordinary client decision prompt")
- **A_REPO_H3**: 위 + E2.3 `_gen_prompts.py`의 `GLOBAL_CONSISTENCY_RULE`을
  **바이트 그대로 import**(README.md: "repo evidence + E2.3 global
  feature-type invariant" — 이미 E2.2.3에서 검증된 문구를 재서술 없이 재사용)
- **CONTRACT_REPO_H3**: `contract_prompt.md`의 규칙 1~7 본문을 **앵커 기반으로
  추출**(끝의 "출력은 decision_schema.json의 evidence_contract_v1 schema를
  따른다." 줄만 H3용 문장으로 교체 — `_review_11.py`가 이미 쓰는 앵커 추출
  관례와 동일: 원문이 바뀌면 조용히 drift하는 대신 `SurfaceError`로 시끄럽게
  실패한다)

세 프롬프트 전부에 공통 action 지시문 블록 하나를 이어붙인다:

> 최종 결정은 다음 중 하나의 action이어야 한다.
> - `accept_report`: 현재 상태가 안전하며 추가 조치가 필요 없다.
> - `repair`: 근거가 있는 concept/feature 수정이 필요하다. `repaired_concepts`에
>   input의 모든 concept과 feature를 포함해 채운다.
> - `defer`: 이 packet만으로는 판단을 확정할 수 없어 보류한다. 이때
>   `repaired_concepts`는 `null`이다.
>
> `cited_evidence_ids`에는 이번 판단에 실제로 근거로 쓴 evidence_id만 적는다.
> payload에 없는 id를 적으면 안 된다. `report`에 판단 근거를 자유 서술로
> 요약한다.

## 5. Smoke 단계 — 사전등록 (2026-07-29 중간 지시 반영)

세션 중 사용자 지시: *"smoke로 2-3개 정도 test 하는 것은 허용해, 3개 중에서
2개가 문제가 있으면 그 실험은 수정 해야 하는 것이고."*

- **규모**: 3 trial — 같은 fixture(`insufficient`, D-H3-2의 1차 표적 class)에
  대해 세 arm 각각 1회. 이것이 D-H3-5가 말하는 "같은 fixture·replicate index의
  3-arm bundle" 실행 단위 그 자체다
- **판정 기준**: 3건 중 **2건 이상**에서 구조적 문제가 나오면 **설계
  수정 필요**로 표시하고 45-trial pilot으로 확장하지 않는다. "구조적 문제"란
  ─ schema-invalid 출력, 금지 필드(오라클) 접근·유출 흔적, 계약을 완전히
  무시한 반응 ─ 이지 "class 판정이 기대와 다르다"가 아니다. 후자는 H3가
  측정하려는 대상 그 자체이며 harness 결함이 아니다
- **0~1건 문제**: pilot(45 trial) 확장으로 진행 가능 — 단, 이 단계는 이번
  작업 범위 밖이며 별도 승인 필요
- 이 3건은 **비인증(non-certifying)**이다. 결과를 보고 프롬프트·스키마를
  바꾸면 이 3건은 pilot에 병합하지 않는다(D-H3-5 원칙 재사용)

## 6. 구현 전 합격 게이트 10항 → `test_h3.py` 매핑

`DESIGN_DECISION_H3.md` §6의 10항을 그대로 옮긴다.

| # | 게이트 | 테스트 |
|---|---|---|
| 1 | 세 arm의 payload canonical bytes·hash 동일 | `test_payload_bytes_identical_across_arms_same_fixture` |
| 2 | evidence item key set = `evidence_id`/`source_kind`/`text` | `test_evidence_item_keys_match_model_evidence_keys` |
| 3 | 공통 action schema subtree byte-equivalent | `test_common_action_subtree_identical_in_all_three_variants` |
| 4 | prompt diff = 등록된 계약 텍스트·진단 schema 차이뿐 | `test_rendered_prompt_diff_is_only_registered_rule_text` |
| 5 | hidden oracle·fixture class·기대 action 접근 불가 | `test_h3_module_never_imports_oracle_manifest` |
| 6 | 기존 유출 positive-control 미검출 | `test_known_leak_sentences_absent_from_h3_prompts` |
| 7 | qualification manifest가 fixture hash에 결합 | `test_stale_fixture_after_qualification_is_refused` |
| 8 | smoke·pilot·본실행이 같은 dispatcher 사용 | `test_single_render_entrypoint` |
| 9 | 모든 hash 기록 | `test_freeze_records_all_required_hashes` |
| 10 | 루트 테스트에서 실제 수집·통과 | `scripts/run_gates.py`가 `experiments/*/test_*.py`를 glob(구조상 자동 편입) |

추가(재사용 검증 전용): `test_contract_repo_h3_reuses_contract_prompt_rules_verbatim`,
`test_a_repo_h3_uses_the_same_global_consistency_rule_text_as_e2_3`.

## 7. 실행 순서 (이번 세션)

1. 이 문서 + `decision_schema_h3.json` 커밋(코드보다 먼저 — 사전등록 규율)
2. `_h3.py`, `test_h3.py` 작성 + 커밋
3. `python3 _h3.py agent` — 3개 trial subject 정의 생성·설치(모델 호출 없음)
4. `python3 _h3.py freeze` — pilot 45-trial 매니페스트 사전등록(모델 호출
   없음, 순수 결정론적 해시 계산)
5. `pytest`(via `scripts/run_gates.py`)로 게이트 10항 확인
6. **3건 smoke trial**(§5) — Agent 호출로 실제 실행. 결과에 따라 pilot 확장
   여부를 이번 세션에서 판단하되, 45-trial 실행 자체는 별도 승인 후
