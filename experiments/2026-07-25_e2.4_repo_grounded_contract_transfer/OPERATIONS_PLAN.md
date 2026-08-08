# E2.4 운영 계획

`README.md`(설계 계약)를 실제로 돌리기 위한 단계별 실행 계획이다.
`d581d53`는 설계 패킷만 커밋했다 — fixture/manifest/실행은 이 계획을
따라 이후 세션에서 진행한다.

## 반영한 외부 원칙과 그 이유

공유받은 workflow 설계 노하우 10개 중, 이 실험에 **구조적으로 새로
필요한 것만** 반영한다. 이미 이 프로젝트 관례가 충족하고 있는 원칙은
재구조화하지 않고 한 줄만 확인한다.

**이미 충족(변경 없음)**:
- 원칙 2(파일에 진행상태 저장) — fixture.json/decision_schema.json/
  _gen_prompts.py/evaluate.py/trials.json 커밋 패턴이 이미 이것이다.
- 원칙 8(병렬성은 출력 충돌로 판단) — trial마다 독립 파일 없이 순수
  함수 호출(agent())이라 `pipeline()` 전체 병렬이 항상 안전하다. 이미 그렇게 씀.

**새로 반영(아래 단계에 구조로 들어감)**:
- **원칙 1 (judgment/mechanics 분리)**: CONTRACT_REPO의 LLM 역할은 evidence
  audit·sufficiency 판단(judgment)까지고, `decision`↔`contract_verdict`↔
  `repair_plan.allowed`↔`abstain.required`의 상호 일관성 검사는 LLM
  self-report를 믿지 않고 `evaluate.py`가 `semantic_constraints`를 코드로
  강제한다(mechanics). 이미 스키마에 분리 표현돼 있지만, 이번 계획에서
  "scorer가 검사해야 할 목록"으로 명시화한다(Phase 5).
- **원칙 3+4 (독립 review, implementer≠verifier)**: E2.3까지는 fixture가
  synthetic 문장이라 "정답 방향"이 설계자 의도와 동일했다. E2.4는 실제
  repo 텍스트에서 evidence를 뽑기 때문에, "이 evidence item이 direct_support인가
  ambiguous인가"라는 **fixture 제작자 본인의 판단**이 hidden oracle에
  들어간다 — 이게 검증 없이 그대로 정답으로 쓰이면 implementer가 자기
  작업을 판정하는 것과 같다. 따라서 fixture 제작 직후 **독립 리뷰
  단계(Phase 2)**를 추가한다: fixture 제작자가 아닌 별도 호출(fresh
  subagent 또는 사람)이 각 evidence_item의 admissibility 라벨에 동의하는지
  재확인.
- **원칙 5 (gate pass ≠ artifact existence)**: `_prompts.json`이 존재하는
  것과 `PREREGISTRATION_REQUIRED` 게이트를 통과한 것은 별개로 이미
  구분돼 있다(기존 관례). E2.4에서 새로 추가되는 구분: evidence packet
  파일이 존재하는 것과, 그 packet이 `evidence_packet_schema.json`을
  통과하는 것과, 그 packet의 hidden oracle이 Phase 2 독립 리뷰를 통과한
  것 — **세 가지를 별도 체크리스트 항목**으로 Phase 4에 명시한다.
- **원칙 6 (semantic gate는 runner 밖)**: Workflow 스크립트(runner)는
  schema-forced 출력 여부만 본다(deterministic floor). "이 evidence
  audit이 실제로 맞는 판단인가"는 runner 안에서 검사하지 않고, 실행이
  끝난 뒤 `evaluate.py`가 hidden oracle과 대조해 별도로 채점한다(Phase 6).
  이건 이미 이 프로젝트의 기존 패턴(scorer는 항상 실행 밖)과 같은
  방향이라 구조 변경은 없고, E2.4에서 늘어난 필드(evidence_audit,
  feature_judgments, invariant_checks)까지 채점 대상에 명시적으로
  포함한다는 뜻이다.
- **원칙 7 (human-pause vs automated-recheck 구분)**: 이 세션의 기존
  규칙("push는 명시 승인 후")과 같은 것이지만, E2.4엔 새 pause 지점이
  하나 늘어난다 — Phase 2 독립 리뷰에서 admissibility 라벨에 이견이
  나오면 그건 자동 재검사가 아니라 **사람 판단이 필요한 지점**(사람이
  "이 텍스트가 direct_support가 맞다/아니다"를 판정)이다. Phase 2에서
  이 pause 조건을 명시한다.
- **원칙 9 (selective rerun을 처음부터 설계)**: fixture 4-class ×
  arm 3종 = 12 cell 중 일부만 실패/모호하면 그 cell만 다시 돌릴 수
  있어야 한다 — E2.3의 Stage1→Stage2 증분 패턴을 그대로 재사용하되,
  이번엔 "어떤 cell을 증분할지"를 `evaluate.py` 출력이 명시적으로
  뱉도록 Phase 6에서 설계한다(E2.3의 `escalate_to_stage2` 필드와 동일
  패턴, cell 단위로 일반화).

**반영 안 함(이번 실험 규모에 과함)**: 원칙 10(개선 루프)은 harness
자체를 여러 라운드 반복 성숙시키는 메타 원칙이라 이번 1회성 실행
계획엔 새 구조를 넣지 않는다 — 필요해지면 skills-catalog 쪽 lessons
문서에 기록할 사안.

## 단계

### Phase 0 — 실제 repo evidence 추출 (fixture 제작)

4개 semantic class(README.md 표) 각 최소 1개 fixture. 후보 evidence
소스(전부 `goodand/concept-gate-taxonomy` 내부, `extraction_policy`
준수):

| class | 후보 evidence 소스 | 이유 |
|---|---|---|
| sufficient_consistent | `conceptgate/concept_gate_v7.py`의 `FeatureType` enum 정의 + 그 바로 위 docstring | 명시적이고 일관된 텍스트라 강한 direct_support |
| sufficient_repairable | 서로 다른 두 모듈이 같은 개념(예: `part_feature`)을 다르게 서술하는 실제 docstring 쌍 — 있으면 사용, 없으면 의도적으로 두 함수 docstring에서 발췌해 구성 | E2.3의 MixRig 패턴을 실제 텍스트로 재현 |
| insufficient | 함수/클래스 이름만 있고 설명 텍스트가 빈약한 위치(예: 헬퍼 함수의 한 줄 docstring) | admissibility=ambiguous/indirect_context만 나오게 설계 |
| conflicting | 서로 다른 시점의 커밋 메시지가 같은 대상을 다르게 서술하는 경우(예: 이번 세션에서 실제로 있었던 "재해석" 전/후 커밋 메시지 쌍) | 실제로 이 세션에 존재하는 진짜 conflict 사례 — 꾸며낼 필요 없음 |

각 fixture는 `evidence_packet_schema.json`을 만족해야 하고,
`text_sha256`은 실제 소스 텍스트의 sha256이어야 한다(발췌 텍스트가
원문과 정확히 일치함을 기계적으로 보장 — 원칙 6의 "runner는
deterministic floor만" 정신을 fixture 제작에도 적용).

### Phase 1 — Deterministic floor 체크 (runner-level, 이 시점에 가능한 것만)

- 4개 evidence packet 전부 `evidence_packet_schema.json` 통과
  (`python3 -m jsonschema` 또는 동등한 검증 스크립트).
- 각 `evidence_items[].text_sha256`이 `text`의 실제 sha256과 일치.
- `extraction_policy.allowed_sources`에 없는 `source_path`가 없는지.
- `run_pipeline_input`을 `_cert_core.run_and_certify()`로 재실행했을 때
  `server_response`가 재현되는지. `candidate_concepts`는 모델-facing
  evidence packet이라 `evidence_refs`를 쓰고, `run_pipeline` 입력이
  아니므로 둘을 혼동하면 안 된다.

### Phase 2 — 독립 리뷰 (원칙 3+4+7)

fixture 제작자(이 세션)와 **다른 호출**(fresh Explore/general-purpose
subagent, 또는 사람)이 각 evidence_item의 admissibility 라벨과 class별
hidden oracle에 동의하는지 재확인. 이견이 나오면:
- 라벨 자체의 문제(사소한 판단 차이) → 재작성 후 재리뷰.
- "이게 진짜 direct_support가 맞는가"처럼 근본적 이견 → **사람 pause**
  (원칙 7) — 자동으로 어느 한쪽을 채택하지 않는다.

### Phase 3 — Freeze

기존 패턴과 동일: `README.md, evidence_packet_schema.json,
decision_schema.json, contract_prompt.md, fixture 4개, _cert_core.py
(있다면), _gen_prompts.py, evaluate.py` 전부 커밋 후 `_gen_prompts.py`가
`PREREGISTRATION_REQUIRED`로 거부하는지 먼저 확인, 그다음 설계 freeze
커밋.

### Phase 4 — 매니페스트 생성 + 3중 존재 체크리스트 (원칙 5)

| 체크 | 대상 |
|---|---|
| artifact 존재 | `_prompts.json` 파일이 생성됐는가 |
| schema gate 통과 | 각 evidence packet이 `evidence_packet_schema.json`을 통과했는가 (Phase 1 재확인) |
| 리뷰 gate 통과 | 각 evidence packet이 Phase 2 독립 리뷰를 통과했는가 |

세 값은 독립적으로 기록 — 하나라도 false면 그 cell은 매니페스트에서
제외하거나 명시적으로 "미검증"으로 표시.

### Phase 5 — 커버리지 결정 + 스크리닝 실행 (비용 고려)

전체 4 class × 3 arm = 12 cell을 전부 N=10으로 돌리면 120 trial —
이번 세션의 비용 절감 관례(E2.3의 CONTROL 축소 사례)를 따라 커버리지를
비대칭으로 둔다:

- **CONTRACT_REPO**: 4 class 전부, arm-cell당 N=10 (핵심 주장 — 전
  class 필요).
- **A_REPO**: 2 class만 (sufficient_consistent + 가장 어려운 class인
  conflicting), arm-cell당 N=10 — "A 규칙만으로 hard case에서 뭐가
  일어나는가" 비교용.
- **CONTROL_REPO**: 2 class만 (동일한 두 class), arm-cell당 N=10 —
  기저선.

합계 4+2+2=8 cell × 10 = 80 trial (Stage 1). E2.3과 동일한 threshold
0.90/escalate 7-8/10 규칙 적용 (`docs/experiment_screening_protocol.md`).

qualification(smoke test)은 실제 frozen 매니페스트 프롬프트를 그대로
써서 각 고유 `(fixture_class, arm)` 조합당 1-2회 — E2.3에서 확인된
것처럼 이 결과는 official count로 재사용 가능(smoke가 dummy 프롬프트가
아니라 실제 프롬프트일 때만).

### Phase 6 — 채점 (semantic gate, runner 밖) + selective escalate (원칙 6+9)

`evaluate.py`가 확인해야 할 것 (원칙 1의 mechanics 목록을 실제 코드로):
- 기본 provenance(`validate_trial_set`, 기존과 동일).
- `decision_schema.json`의 `semantic_constraints` 8개 전부 코드로 재검사
  (LLM self-report만 믿지 않음) — 위반 시 그 trial은 자동 FAIL, `decision`
  필드가 뭐라 자칭했든 무관.
- CONTRACT_REPO는 hidden oracle의 기대 `contract_verdict`와 실제
  `contract_verdict` 일치 여부로 채점(단순 `decision` 일치가 아니라).
- 출력에 `escalate_to_stage2` 필드로 어떤 `(fixture_class, arm)` cell이
  7-8/10 구간인지 명시 — E2.3과 동일 패턴을 cell 단위로 일반화.

### Phase 7 — 결과 커밋, push는 별도 승인

기존 관례와 동일: pathspec-scoped 커밋, 실제 관측된 수치로 커밋 메시지
작성, push는 사용자 명시 승인 후.

## 아직 결정 안 된 것 (다음 세션 시작 전에 확정 필요)

- Phase 0의 "sufficient_repairable"/"conflicting" fixture가 실제로 이
  저장소에서 자연스럽게 발견되는지, 아니면 두 실제 텍스트를 발췌·병치
  해서 구성해야 하는지 — 후자라면 "발췌·병치"도 `extraction_policy`
  위반이 아님을 README.md에 먼저 명확히 해야 한다(현재 README는 이
  구성 방식을 명시적으로 다루지 않음).
- Phase 2 독립 리뷰를 이 세션 안에서 fresh subagent로 할지, 사용자가
  직접 할지 — 원칙 4상 fixture 제작자(나)와 달라야 하므로 Agent 도구로
  fresh 세션을 쓰는 게 기본값이지만, 확정은 실행 세션에서.

## Phase 0/2/스모크 실행 결과 (2026-07-25, 후속 세션)

위 두 미결 사항은 해소됐다: 발취·병치 허용(사용자 승인), Phase 2는 fresh
general-purpose subagent(agentId `a8f54937bc27c7215`)로 실행.

**Phase 0**: 4개 fixture를 이 저장소의 실제 코드/문서/커밋 메시지에서
구성(`fixture_*.json`, 커밋 안 됨 — 아직 조사 단계 파일). `run_and_certify`로
server_response 실측, `evidence_packet_schema.json` 구조 검증 통과, 모든
`text_sha256`이 실제 발췌 텍스트와 일치.

**Phase 2 독립 리뷰**: 4개 중 2개에서 실제 결함 발견 —
1. `sufficient_consistent`: 원 evidence(`FeatureType` enum 정의 자체)가
   순환논리(vocabulary 존재 증명일 뿐, 특정 feature가 그 vocabulary에
   속한다는 근거 아님) — `SemanticTypeInference.infer()`의 실제 결정
   규칙 텍스트로 교체.
2. `conflicting`: E2.2.1/E2.2.2 커밋 메시지 충돌은 실제이지만
   **인과관계 서술의 충돌**이지 **FeatureType 온톨로지 분류의 충돌**이
   아님 — evidence는 유지하되 기대 오라클을 "abstain(사유 불문)"으로
   완화하고 이 판단을 fixture 안에 명시.

**Smoke test** (8 cell, 1 trial씩; 1차 시도에서 CONTRACT_REPO 4개 전부
`evidence_contract_v1`의 최상위 `$schema` 키 때문에 실패 → 제거 후 재실행
성공):

| fixture class | CONTRACT_REPO 결과 | 의도 | 일치 |
|---|---|---|---|
| sufficient_consistent | abstain (insufficient_evidence) | accept_report | ✗ |
| sufficient_repairable | repair (sufficient_repairable) | repair | ✓ |
| insufficient | accept_report (sufficient_consistent) | abstain | ✗ |
| conflicting | abstain (conflicting_evidence) | abstain | ✓ |

**핵심 검증 결과**: `conflicting` fixture에서 CONTROL_REPO/A_REPO(legacy
스키마)는 둘 다 abstain 없이 스스로 "ev6가 ev5를 대체"라 판단하고 조용히
repair했다. 동일 evidence에서 CONTRACT_REPO만 두 근거를 `conflict`로
명시 분류하고 정확히 abstain했다 — 계약 구조가 실제로 판단 경계를
안정화한다는 이 실험의 핵심 가설을 직접 뒷받침하는 첫 실측 증거.

> ⚠️ **정정 주석 (2026-07-27, H1)**: 위 "핵심 검증 결과"는 이 실험 전체를
> 동기부여한 관측이지만, **오라클 유출이 있던 packet에서 얻은 것**이다
> (`fixture_conflicting.json`의 `extraction_note`에 "CONTRACT_REPO's correct
> behavior is still to abstain..."이 들어 있었고, 이 필드는 모델에 전달된다 —
> `PROBLEM_2_conflicting.md` §2).
>
> 다만 유출의 방향을 따져보면 이 관측이 **유출로 설명되지는 않는다**: 유출
> 문구는 "보류가 옳다"는 쪽을 가리켰는데 legacy arm들은 그럼에도 repair를
> 강행했다. 즉 유출은 legacy의 overclaim을 만들어낸 원인이 아니라 오히려
> 그것을 억제해야 했을 텍스트였다. (legacy 스키마의 선택지는
> `report_done`/`repair`/`request_evidence`로 `abstain` 어휘 자체가 없어
> 유출 문구가 그들의 선택지에 직접 매핑되지도 않는다.)
>
> 그럼에도 이 관측은 **N=1이고, 그 fixture는 이제 커버리지에서 제외됐다**
> (§"문제 정의" 이후 절 참조 — `conflicting`은 미확보로 종결). 따라서:
> - 이 관측을 E2.4의 결론으로 인용하면 안 된다. 재현이 필요하다.
> - 재현할 fixture가 `conflicting`이 아니게 됐으므로, arm 비교를 어느 class로
>   할지가 열린 문제다(Phase 5 커버리지 재설계, `docs/HANDOFF.md` §6 H1c).

## 문제 정의 (N=10 본 실행 전 해결 필요)

**문제 1 — `sufficient_consistent`가 구조적으로 어려움 — 2026-07-27 해결됨,
아래는 당시 문제 정의 그대로 유지(이력용).** 최종 해결 경위는 위
"문제 1 해결 (2026-07-27)" 절과 `PROBLEM_1_sufficient_consistent.md`
참조. 리뷰에서 잡힌
순환논리를 고쳤는데도 CONTRACT_REPO는 여전히 insufficient로 판정했다.
이유: 텍스트가 "알고리즘이 어떻게 판단하는가"를 서술할 뿐 "이 feature는
essential이다"를 직접 선언하지 않는다. 이 저장소의 코드/주석은 대부분
**절차적**(어떻게 판단하는지)이지 **선언적**(특정 대상에 대한 직접
단언)이 아니라서, "이미 충분하고 수리 불필요"를 보여줄 진짜 근거를
코드에서 찾기 어렵다. 후보 해법: (a) `docs/`류 산문에서 더 선언적인
문장 탐색, (b) 발취·병치로 직접 단언 문장 구성, (c) 이 semantic class
자체를 이 코드베이스에 맞게 재정의.

**문제 2 — `insufficient` fixture에서 진짜 오류 발생**: 완전히 무관한
함수(JSON 추출 유틸)의 "검증 실패시 에러" 동작을, 모델이
essential_feature의 "본질적"과 혼동해 accept_report로 오판했다. 이건
fixture 결함이 아니라 **evidence가 진짜로 주제 무관(out_of_scope)한데도
모델이 오분류한 CONTRACT_REPO 메커니즘 자체의 실제 약점**이다.

**결정 필요**: 문제 2를 (a) 그대로 두고 N=10에서 측정할지(진짜 능력
한계를 재는 것 — 실패율이 유의미한 데이터), 아니면 (b)
`contract_prompt.md` 규칙 2를 강화해서("코드 동작이 기능상 필요하다는
것 자체는 essential_feature 증거가 아니다") 막고 재검증할지. (a)는 raw
baseline, (b)는 prompt-engineering 개입 후 재측정 — 둘 다 유효한
실험이지만 다른 질문에 답한다. 사용자 결정 대기.

## Phase 1 하네스 보강 (2026-07-26)

Fixture 관리 결함을 하나 발견해 먼저 닫았다. `candidate_concepts`는
`evidence_refs`를 담는 모델 입력 표면인데, 기존 문서 표현은
`server_response`가 이 객체에서 직접 관측된 것처럼 읽혔다. 실제
`run_pipeline`은 feature별 inline `evidence` 문자열을 요구하므로, 이 둘을
분리하지 않으면 `server_response` 재현 검증이 불가능하다.

조치:
- `evidence_packet_schema.json`에 `run_pipeline_input`을 필수 필드로 추가.
- 4개 `fixture_*.json`에 실제 `run_pipeline` 입력을 명시.
- `test_protocol.py` 추가. 현재 검증 항목: 필수 shape, sha256, evidence_refs,
  `candidate_concepts`와 `run_pipeline_input`의 이름/feature/type alignment,
  그리고 `_cert_core.run_and_certify(run_pipeline_input)` 기반
  `server_response` 재현.

검증 명령:

```bash
python3 -m pytest -q experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/test_protocol.py
```

현재 결과: `3 passed`.

## 문제 1(`sufficient_consistent`) 해결 (2026-07-27)

5차 시도(카페린/손잡이/`structural_composition`, evidence는 E2.3의
사전등록 fixture 텍스트 + `server.py`의 라이브 docstring 조합)로
독립 리뷰 통과 후 N=5 smoke test 실행 → 필러 essential_feature가
evidence 없이 있어 5/5 전부 abstain하는 결함 발견 → 필러 제거 +
`server_response`를 실제 `NEEDS_CORRECTION` 관측값으로 교정 → 재검증
7/7(소규모 확인 2 + 공식 재실행 5) 전부 `accept_report`/
`sufficient_consistent`. 상세 기록은
`PROBLEM_1_sufficient_consistent.md` §7.4-7.6, §11 참조. E2.4의 4개
semantic class 전부 해결·검증 완료 — Phase 3(freeze)로 넘어갈 준비가
됐다.

**부수 발견 및 정정(2026-07-27)**: `fixture_sufficient_repairable.json`의
`ev3`이 `RELATION_HINT_TYPE`을 인용하는 게 죽은 코드 근거 아니냐는
의심으로 재검토를 시작했으나, **이 "죽은 코드" 전제 자체가 틀렸다는 게
재검증에서 드러났다.** `cg_partwhole.py`의 모듈 docstring("참조용 —
직접 import 안 함")은 **stale(갱신 안 된 옛 주석)**이다 —
`concept_gate_v7.py:350`이 `hint_to_feature_type`을 실제로 import해
`relation_discrimination_gate()`에서 쓰고, 이 게이트는 `server.py`의
라이브 `run_pipeline`이 호출하는 `run()` 경로 안에 있다.
`cg_input_linter.py:15`도 별도로 import해 매 호출마다 lint에 쓴다.
`test_semantic_regressions.py`의 R6/R6b, `qa_v7.py`의 I8 테스트가 이
매핑을 검증하며 현재 통과 중이다. 즉 **오늘 `sufficient_consistent`의
3차 시도(candidate B, `RELATION_HINT_TYPE["component_of"]`)를 기각한
근거("죽은 참조용 코드")는 stale 주석을 실제 import 그래프 확인 없이
그대로 믿은 오류였다** — 상세 정정은 `PROBLEM_1_sufficient_consistent.md`
§10 참조. `sufficient_repairable` 자체는 (죽은 코드 문제는 아니지만)
`ev2`/`ev3`가 `완제품유닛B`라는 구체 concept을 언급하지 않는다는 별도
쟁점이 있어 재검증 진행 중.

**`sufficient_repairable` instance-binding 결함 → 1차 재구성(낫/칼/철,
이후 폐기) → 2차 재구성(돌체/바퀴, 최종 채택) (2026-07-27)**:

독립 리뷰(2차)가 위 별도 쟁점을 확인 — `ev2`/`ev3`는 일반 어휘 정의일
뿐 `완제품유닛B`/`재료`라는 구체 instance에 결박되지 않는다
(`sufficient_consistent`가 `ev9`만으론 부족해 `ev10`을 요구했던 것과
같은 패턴). 1차 재구성은 `완제품유닛A`/`완제품유닛B`/`재료`를 `낫`/
`칼`/`철`로 바꾸고, `test_semantic_regressions.py`의
`test_r6b_material_feature_not_in_isa_dag`(concept `칼`, feature `철`)를
`ev4`로 인용해 instance-binding을 확보했다 — 이 시도 자체는 독립
리뷰를 통과했다(자기인용 아님, 죽은 코드 아님, provenance 확인됨).

**그러나 N=5 smoke test에서 1차 재구성(낫/칼/철, MixRig 기반)은
4/4(1개는 API 세션 한도로 실패, 데이터 아님) 전부 `abstain`으로
나왔다** — 정확한 이유: `칼`의 `철`=structural_composition은 evidence로
충분히 확정됐지만, **동일 feature 이름을 공유한다는 이유만으로 `낫`의
`철`에 그 판정을 전이시키는 것은 모델이 스스로 `extraction_policy.
disallowed_sources`("심볼명만으로 하는 추론 금지")를 인용하며 거부**했다.
이는 이 실험에서 논의된 "Rule 4(전역 invariant)가 Rule 2/3(인스턴스
결박)와 같은 엄격도를 요구하는가"라는 계약 의미론 질문에 대한 실측
답(4/4, "그렇다")이었다. 이 발견 자체는 폐기하지 않고 보존됨 —
cross-concept invariant를 다시 검증하려면 이 발견을 근거로 별도
fixture/후속 실험을 설계해야 한다.

**최종 결정(외부 실험 설계 논의 경유)**: cross-concept invariant/MixRig
검증을 이 fixture에서 완전히 분리하고, "기존 instance-bound evidence가
현재 feature type과 직접 충돌하며, 지정된 단일 repair 후 clean PASS가
되는가"만 검증하는 single-concept 시나리오로 평가 목표 자체를 좁혔다.
`낫`/`칼`/`철`/MixRig 구조를 완전히 제거하고, E2.2(2026-07-23, commit
`49f030b`) → E2.2.1(2026-07-24)에서 이미 동결·재사용된 evidence를 다시
재사용 — concept `돌체`, feature `바퀴`(essential_feature로 지정돼
있지만 evidence "돌체의 바퀴는 돌체 몸체의 구성 부분이다"가 직접 반박),
feature `갑종`(essential_feature 필러, repair 후에도 essential 축 유지용).

조치:
- `fixture_sufficient_repairable.json`을 `돌체`/`바퀴`/`갑종`으로 완전히
  재작성. `run_pipeline_input`의 `바퀴` evidence는 필러 문자열로
  분리(ev1과 동일 텍스트 재사용 금지 — self-citation 방지).
- `test_protocol.py`에 `test_sufficient_repairable_single_repair_
  yields_clean_pass` 추가 — pre-repair(essential_feature)와 post-repair
  (structural_composition, 갑종 불변) 둘 다 `_cert_core.run_and_certify`로
  clean `PASS`임을 회귀 테스트로 고정.
- 별도 발견(이 재구성과 독립): `cg_input_linter.py`의 fallback dict
  (`hint_to_feature_type` import 실패 시에만 쓰이는 경로)가 `material_of`를
  `essential_feature`로 매핑해 canonical `RELATION_HINT_TYPE`과 불일치 —
  `structural_composition`으로 수정(낫/칼/철 재구성 때 발견, 돌체/바퀴
  전환 후에도 유효한 수정이라 유지).
- `contract_prompt.md` rule 5(필러가 repair 판단을 막지 않음)와 rule 7
  (server_response.status가 PASS가 아니어도 feature-type 판정과 무관하면
  accept_report 가능)에 그동안 smoke test 프롬프트에만 수동으로 추가해온
  문구를 정식 병합 — 두 rule 다 실제 smoke test에서 검증된 채로 이제
  frozen 파일 자체에 반영됨.
- 검증: `test_protocol.py`(4 passed), `test_semantic_regressions.py`
  (8 passed, R6/R6b 포함), `qa_v7.py`(101/101) 전부 통과. `test_server.py`는
  이 환경에 `fastmcp` 미설치로 실패 — 변경 전에도 동일하게 실패함을
  `git stash`로 확인(무관한 환경 이슈).
- 독립 리뷰(3차, 이 돌체/바퀴 재구성 대상): ACCEPT. provenance
  byte-identical 확인(E2.2 commit `49f030b` → E2.2.1 → 이 fixture),
  Rule 2 적합성 확인, 결정론적 pre/post 검증 확인. 잔여 리스크 2개
  지적(필러 미검증, run_pipeline_input 자기인용 외형) — 둘 다 즉시 수정.
- **N=5 smoke test(최종)**: 5/5 전부 `decision=repair`,
  `contract_verdict=sufficient_repairable`. 필러(`갑종`, evidence_refs
  없음)는 5/5 전부에서 `바퀴` repair 판단을 막지 않았다.

**결론**: `sufficient_repairable` 재검증 완료, 해결됨.

## `conflicting` 미확보로 종결 + 유효 커버리지 3 class 확정 (2026-07-27, H1)

H1(`docs/HANDOFF.md` §6)을 실행한 결과, 위 "4개 class 전부 검증 완료"라는
표현은 **틀렸다** — `conflicting`은 N=1 인증이었고 그 N=1이 오라클 유출
상태에서 얻어진 것이었다. 상세 전문은
`PROBLEM_2_conflicting.md`. 요약:

1. **오라클 유출 발견·수정**: `fixture_conflicting.json`의
   `extraction_note`(모델-facing 필드)에 기대 verdict가 그대로 적혀 있었다.
   `evidence_packet_schema.json` 자신이 금지한 것을 위반. 제거 후
   `test_protocol.py`에 **기계적 가드**(`test_model_facing_metadata_does_not_leak_the_oracle`)
   추가 — 음성 대조로 옛 유출 텍스트를 실제로 검출하는지 확인.
2. **유출 제거 후 N=5 실측**: `decision` 5/5 `abstain`(안정), 그러나
   `contract_verdict` 불안정 — `insufficient_evidence` ×4,
   `conflicting_evidence` ×1. Phase 6은 verdict 일치로 채점하므로
   **어느 쪽을 오라클로 잡아도 threshold 0.90 미달**(0.20 또는 0.80).
   원인은 fixture가 아니라 계약 문구(규칙 3이 "동등강도 direct_support"를
   `semantic_constraints`만큼 못박지 않음).
3. **결정(사용자)**: `conflicting_evidence`를 **"현 저장소의 live·동등강도
   evidence로 구성 가능한 fixture 미확보"**로 표시. **유효 커버리지 3 class**
   (`sufficient_consistent` 7/7, `sufficient_repairable` 5/5,
   `insufficient` 5/5). **Schema의 class 자체는 유지**(enum 미변경, 실제
   확인함). stale 문서 대 live 코드 충돌은 `source_authority_unresolved`
   계열 별도 실험으로 분리.

**Phase 5 커버리지 재설계 필요**: 기존 설계는 CONTROL_REPO/A_REPO에
`sufficient_consistent` + `conflicting`을 배정했다. `conflicting`이 빠지면
arm 비교의 최고 신호 셀이 사라지고, abstain-target class는 `insufficient`
하나만 남는다. 또한 위 "핵심 검증 결과" 절의 유일한 arm 비교 관측도 그
fixture에서 나온 것이라 재현 대상이 됐다(그 절의 정정 주석 참조).
**본 실행(Phase 5) 전에 이 재설계와 규칙 3 명확화가 선행돼야 한다.**
