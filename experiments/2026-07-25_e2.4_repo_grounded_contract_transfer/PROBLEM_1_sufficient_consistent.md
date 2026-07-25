# 문제 정의서 — `sufficient_consistent` fixture가 이 저장소에서 구조적으로 구성되지 않음

- 상태: 미해결. 해결 요청 대상 문서.
- 관련 커밋: `a10c9ad`(1차 fixture, 리뷰 반영 후), `c2d0ce5`(문제 2 해결·무관)
- 관련 파일: `fixture_sufficient_consistent.json`, `contract_prompt.md`,
  `decision_schema.json`(`evidence_contract_v1`)

## 1. 한 줄 요약

`sufficient_consistent`(증거가 현재 상태를 충분히 지지하므로 수리 불필요,
`accept_report`가 정답인 class)를 이 저장소의 실제 코드/문서에서 구성하려는
두 차례 시도가 전부 CONTRACT_REPO에게 `abstain`(insufficient_evidence) 판정을
받았다 — fixture 결함이 반복되고 있다.

## 2. 배경

E2.4는 CONTRACT_REPO(evidence audit → sufficiency 판정 → invariant 확인 →
accept_report/repair/abstain)가 실제 repo-derived evidence 위에서 4개
semantic class(README.md 표 참조)를 올바르게 구분하는지 검증한다.

| class | 기대 판정 | 상태 |
|---|---|---|
| sufficient_consistent | accept_report | **미해결(본 문서)** |
| sufficient_repairable | repair | 해결 — smoke test에서 의도대로 동작 확인 |
| insufficient | abstain | 해결 — 규칙 2 수정 후 5/5 검증 완료(`c2d0ce5`) |
| conflicting | abstain | 해결 — smoke test에서 의도대로 동작 확인 |

4개 중 3개가 검증됐고, `sufficient_consistent` 하나만 남았다.

## 3. 문제 정의 (정확한 진술)

**"이 저장소의 실제 코드/문서/테스트/커밋 메시지 중, 어떤 후보 feature의
현재 기록된 type을 CONTRACT_REPO가 `accept_report`(= evidence가 그 type을
충분히·직접적으로 지지하며 수리 불필요)로 판정하게 만드는 real evidence
발췌를 아직 찾지 못했다."**

이건 CONTRACT_REPO 메커니즘의 버그가 아니다 — 오히려 반대로, 두 시도 모두
CONTRACT_REPO가 "불충분한 것을 충분하다고 우기지 않는다"는 바람직한 보수성을
보인 결과다. 문제는 **fixture 재료를 못 찾은 것**이다.

## 4. 현재까지 시도한 것 (전부 실패, 정확한 근거)

### 시도 1 (독립 리뷰에서 기각, 실행 전 폐기)

- Evidence: `conceptgate/concept_gate_v7.py` lines 71-81, `class
  FeatureType(Enum)` 정의 자체.
- candidate: `FeatureType_Enum` / feature `essential_marker` = essential_feature.
- 독립 리뷰(agentId `a8f54937bc27c7215`) 판정: **out_of_scope에 가까운
  순환논리**. "evidence가 essential_marker라는 특정 feature를 언급하지
  않는다 — vocabulary(enum) 정의 자체를 그 vocabulary에 속하는 근거로
  쓰는 건 순환이다." → 실행 전 폐기.

### 시도 2 (실제로 CONTRACT_REPO에 제출, abstain 받음)

- Evidence: `conceptgate/concept_gate_v7.py` lines 279-301,
  `SemanticTypeInference.infer()` classmethod 전문 — "clean fallback →
  ESSENTIAL" 결정 규칙(다른 마커에 안 걸리면 essential_feature 반환).
- candidate: `이름속성_개념` / feature `이름`(어떤 마커에도 안 걸리는
  실제 bare identifier) = essential_feature.
- server_response(실제 `run_and_certify` 실행): `{"status": "PASS", "anti_patterns": []}`.
- **CONTRACT_REPO 실제 판정(1회 실행, 스키마 버그 수정 후 재시도에서
  획득)**:
  ```
  decision: abstain
  contract_verdict: insufficient_evidence
  evidence_audit[ev1]:
    admissibility: indirect_context
    claim_strength: implicit
    rationale: "Evidence shows the general SemanticTypeInference.infer()
    method implementation for determining feature types. However, it does
    not explicitly mention concept '이름속성_개념' or feature '이름'. The
    code demonstrates the inference mechanism and logic (ESSENTIAL vs
    other types) but provides no direct textual support linking this
    specific feature to its proposed type classification."
  ```
- **판정 근거 정확한 재구성**: 모델은 "일반 알고리즘이 어떻게 판단하는지"와
  "이 특정 feature가 그 알고리즘을 통해 실제로 essential로 분류됐다는 직접
  서술" 사이에 추론적 단계(inferential step)가 있다고 보고, 그 단계를
  텍스트 자체가 수행하지 않았다는 이유로 `indirect_context`로 낮췄다.

## 5. 근본 원인 분석

이 저장소(`conceptgate/`)의 docstring·주석·코드는 압도적으로
**절차적**(procedural: "어떻게 판단하는가"를 서술하는 알고리즘/규칙
기술)이지, **선언적**(declarative: "X는 Y다"를 직접 단언하는 문장)이
아니다. 실제 예:

- `RELATION_HINT_TYPE` 딕셔너리(`cg_partwhole.py`)는 관계 어휘→type
  매핑을 선언적으로 제공한다 — 그래서 `sufficient_repairable`(문제 2와
  무관, 이미 해결됨) fixture는 성공적으로 구성됐다. **이건 예외적으로
  선언적인 코드다.**
- `SemanticTypeInference.infer()`, `_scan()`, `_has_exc()` 등은 전부
  "어떤 입력이 주어지면 어떤 규칙으로 판단하는가"를 서술하는
  **알고리즘**이다. 이건 절차적이라 direct_support가 되기 어렵다.
- 함수 docstring 대부분(`extract_json_block` 등)은 아예 설명이 없거나
  구현 세부사항만 있다(문제 2의 원인이었음).

**결론**: 이 저장소에서 "현재 상태가 이미 옳다"는 것을 직접 선언하는
텍스트는 `RELATION_HINT_TYPE`류의 명시적 매핑 딕셔너리·상수 정의 정도로
한정되고, 그마저도 이미 `sufficient_repairable` fixture가 소비했다(같은
매핑을 "불일치를 고치는 근거"로 씀). **같은 매핑을 "이미 일치함을
확인하는 근거"로 재사용하는 두 번째 fixture를 만드는 게 다음 후보다**
(섹션 7의 candidate C).

## 6. 제약 조건 (해법이 반드시 지켜야 하는 것)

1. `evidence_packet_schema.json`의 `extraction_policy` 준수 — 이
   저장소(`goodand/concept-gate-taxonomy`)의 실제 코드/문서/테스트/
   fixture/커밋 메시지만, 일반 지식·타 저장소 금지.
2. 사용자 승인된 방식(발취·병치)은 허용되나, **날조는 금지** — 실제
   존재하는 텍스트만 발췌.
3. 독립 리뷰(Phase 2, fresh subagent)를 통과해야 함 — 순환논리·주제
   무관 재현 금지.
4. `contract_prompt.md`의 최신 규칙(문제 2 수정분 포함, `c2d0ce5`)과
   모순되면 안 됨 — "알고리즘 서술은 direct_support 아님" 규칙이 이미
   있으므로, 새 evidence는 **알고리즘이 아니라 직접 단언**이어야 한다.

## 7. 후보 해법 (트레이드오프 포함)

**A. `docs/`류 산문에서 재탐색**
- 근거: 산문 문서는 코드보다 선언적 문장을 포함할 가능성이 높다
  (`docs/mechanism.md`, `docs/MCP_SERVER.md`, `docs/obligation_layer_roadmap.md` 등).
- 리스크: 이 문서들이 실제로 "X는 essential_feature다"류의 직접 단언을
  포함하는지 아직 확인 안 됨 — 확인 작업 필요(grep + 발췌 후보 스크리닝).
- 비용: 낮음(오프라인 조사).

**B. `RELATION_HINT_TYPE` 매핑을 "확인" 용도로 재사용(다른 feature)**
- 근거: 이미 검증된 유일한 선언적 소스. `component_of`/`member_of`
  등 다른 항목을 골라, 이미 올바르게 기록된 concept을 구성.
- 리스크: `sufficient_repairable`와 근거 소스가 겹쳐 "같은 텍스트
  재탕"으로 보일 수 있음 — 두 fixture가 서로 다른 dict 항목(예:
  `component_of` vs `material_of`)을 쓰면 완화 가능.
- 비용: 낮음(이미 위치 파악됨).

**C. 이 semantic class 자체를 재정의**
- 근거: 어쩌면 "완전한 declarative 직접 단언"이 이 저장소 규모에서
  드문 게 정상일 수 있다 — `sufficient_consistent`를 "direct_support가
  존재하고 conflict가 없다"가 아니라 "여러 indirect_context가
  수렴적으로(convergently) 하나의 결론을 가리키는" 더 약한 기준으로
  재정의하는 방안.
- 리스크: 이건 CONTRACT_REPO의 계약 자체(규칙 3: "direct_support만
  sufficiency를 만들 수 있다")를 바꾸는 것이라, 문제 2에서 방금 강화한
  엄격성과 철학적으로 충돌한다 — 신중해야 함.
- 비용: 설계 변경(README.md, decision_schema.json 재검토 필요).

**권장 순서**: A(빠른 재탐색) → 실패 시 B(같은 소스 다른 항목) → 그래도
안 되면 C(class 재정의를 사용자와 논의).

## 8. 완료 기준 (Definition of Done)

- 새 evidence로 재구성한 `fixture_sufficient_consistent.json`이:
  1. `evidence_packet_schema.json` 구조 검증 통과.
  2. `text_sha256`이 실제 발췌 텍스트와 일치.
  3. 독립 리뷰(fresh subagent)에서 순환논리·주제 무관 지적 없이 통과.
  4. CONTRACT_REPO 스모크 테스트(N≥3, 문제 2와 동일 검증 강도)에서
     과반수 이상 `decision=accept_report` /
     `contract_verdict=sufficient_consistent`로 판정.
- 위 4개를 만족하면 문제 1 해결로 간주하고 `OPERATIONS_PLAN.md`의
  "아직 결정 안 된 것" 목록에서 제거.

## 9. 미해결 질문 (사용자 결정 필요)

1. 후보 A(docs/ 재탐색)부터 바로 시작해도 되는가, 아니면 B/C를 먼저
   검토하고 싶은가?
2. 완료 기준의 임계치("N≥3 중 과반수")가 적절한가, 아니면 문제 2처럼
   5/5를 요구할 것인가?
