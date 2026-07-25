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
