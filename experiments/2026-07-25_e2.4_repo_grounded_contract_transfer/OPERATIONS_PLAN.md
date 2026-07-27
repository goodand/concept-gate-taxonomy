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
