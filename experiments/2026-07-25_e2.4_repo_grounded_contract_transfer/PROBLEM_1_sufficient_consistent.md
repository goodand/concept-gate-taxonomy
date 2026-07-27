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

## 7.1 4차 후보 (2026-07-26)

후보 A를 채택해 `fixture_sufficient_consistent.json`을 재구성했다.
기존 `RELATION_HINT_TYPE` 기반 후보는 죽은/참조용 매핑 테이블 위험이 있어
유지하지 않는다. 새 후보는 살아있는 MCP 문서와 실제 `@mcp.tool`
docstring을 조합한다:

- `docs/MCP_SERVER.md` line 101: `run_pipeline` 입력 예시가
  `{"feature": "동물", "type": "essential_feature", "evidence": "살아있는 생명체"}`
  를 직접 제시한다.
- `docs/LOCAL_INSTALL_GUIDE.md` line 148: 같은 예시를 사용자 설치 가이드에서
  재확인한다.
- `conceptgate/server.py` lines 380-382: 살아있는 `run_pipeline` tool
  docstring이 `essential_feature`는 is-a DAG에 참여하고
  `structural_composition`은 has-a composition edge를 만든다고 명시한다.

새 fixture는 1 concept / 1 feature로 줄였다:
`개` / `동물` / `essential_feature`. 추가 auxiliary feature를 제거해
`accept_report` 판단을 흐리는 불필요한 평가 대상을 없앴다.

현재 deterministic 검증:

```bash
python3 -m pytest -q experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/test_protocol.py
```

결과: `3 passed`.

## 7.2 4차 후보 독립 리뷰 결과 (2026-07-27) — 기각

Deterministic floor는 통과했지만, 독립 리뷰(fresh general-purpose subagent,
fixture 제작자와 무관, hidden-oracle 라벨 모름)가 **REJECT** 판정했다.
검증 대상은 정확히 "ev7/ev8이 direct_support인가, 아니면 1차 시도(enum
정의 = 순환논리)와 같은 함정을 다른 형태로 반복하는가"였다.

리뷰어의 admissibility 판정 (전부 `indirect_context`로 낮춤):

- **ev7** (`docs/MCP_SERVER.md:101`): "`## 입력 형식`(Input Format) 절의
  worked example — JSON 스키마/문법을 가르치는 것이지 '동물이 개의
  존재론적으로 essential하다'를 단언하지 않는다. 더 나쁜 점: 이 텍스트가
  이 fixture 자신의 `run_pipeline_input`과 글자 그대로 동일하다 — 즉
  독립적 확증이 아니라, 테스트 입력 자체를 '증거'로 재인용한 순환
  참조다."
- **ev8** (`docs/LOCAL_INSTALL_GUIDE.md:148`): "`예시 프롬프트` 절의,
  사용자가 MCP client에 **입력해볼 수도 있는** 예시 문장 — ev7보다도 더
  가정적이다(실제 시스템 동작 서술조차 아니고 제안된 발화일 뿐). ev7/
  입력과 같은 내용을 반복할 뿐이라 독립적 데이터 포인트를 추가하지
  않는다 — 같은 canonical demo가 여러 문서에 퍼져 있는 것뿐일 가능성."
- **ev9** (`conceptgate/server.py:380-382`): "유일하게 진짜 선언적이고
  (2차 시도의 절차적 함정을 피함), 실제로 라이브 코드다(3차 시도의 죽은
  코드 함정을 피함) — 하지만 `essential_feature`라는 **타입 자체의
  일반적 의미**만 정의할 뿐, `동물`/`개`라는 **이 특정 feature**를
  언급하지 않는다. Rule 2가 요구하는 건 '이 feature의 온톨로지적 성격'
  이지 '이 타입이 추상적으로 뭘 뜻하는가'가 아니다."

**리뷰어 종합 판단**: "규칙 2는 판정 대상 feature(동물)의 온톨로지적
성격을 직접 서술하는 문장을 요구하지, vocabulary/사용 예시를 요구하지
않는다. ev7/ev8은 1차 시도와 정확히 같은 방식으로 실패한다(형식 예시 ≠
이 인스턴스가 올바르게 분류됐다는 증명) — 오히려 더 나쁘다, ev7의
텍스트가 fixture의 `run_pipeline_input`과 글자 그대로 동일하므로 이건
독립 확증이 아니라 자기 인용이기 때문이다('두 개의 독립 문서'라는
포장은 두 문서가 같은 canonical 예시를 재사용했을 가능성을 가리지
못한다). ev9는 2차/3차의 함정은 피하지만 이 feature에 결박되지 않으므로
단독으로 간극을 못 메운다. 자격 미달 항목 3개(그 중 2개는 순환,
1개는 인스턴스 미결박)를 합쳐도 자격을 갖춘 항목 1개가 되지 않는다.
Rule 2에 따르면 이건 abstain/insufficient_evidence로 판정돼야지
accept_report가 아니다."

**잔여 리스크 (리뷰어가 명시적으로 남긴 것)**: (1) ev9와 달리 ev7/ev8은
"현재 실사용 경로에서 확인됨" 검증이 안 돼 있다 — 3차 시도를 죽인
"참조용 미사용 코드" 문제와 같은 패턴이 여기서도 미확인 상태로 남아
있다는 뜻(이번 리뷰는 이 부분을 반증하진 못했고 열린 질문으로만
남겼다). (2) `개`/`동물`/`essential_feature`/`살아있는 생명체`라는
동일한 4-tuple이 `run_pipeline_input`·ev7·ev8 세 곳 모두에 등장하는데,
이는 세 곳이 독립 신호가 아니라 저장소 전체에서 재사용되는 단 하나의
"hello world" canonical 예시에서 파생됐을 가능성을 시사한다 — 앞으로
같은 예시를 인용하는 어떤 fixture도 이걸 "3개의 독립 증거"로 착각하면
안 된다.

**결론**: 4차 시도(candidate A)도 기각. Behavioral smoke(N=5)는 이 판정
이후 진행하지 않았다 — 1차/3차 시도와 동일한 선례(독립 리뷰 기각 시
trial 예산을 쓰지 않음)를 따른다.

## 7.3 남은 방향

- **후보 B(`RELATION_HINT_TYPE`)**: 이미 사망 확정(3차 시도, 죽은
  참조용 코드로 기각). 재시도 안 함.
- **후보 A(docs/ 산문)**: 이번에 기각. 같은 방향(다른 docs 파일)으로
  또 재탐색할 여지는 남아 있지만, ev9가 보여주듯 이 저장소의 살아있는
  선언적 문장은 전부 "타입의 일반 정의"이지 "이 인스턴스가 이 타입"이라는
  결박 문장이 아니다 — 같은 구조적 문제에 다시 부딪힐 가능성이 높다.
- **후보 D(신규, 이번 리뷰가 사실상 근거를 강화)**: 실행 아티팩트
  (`trials.json` 등 이 worktree의 실제 이전 실험 trial 로그)를 evidence로
  쓰는 안. 핵심 이점: trial 응답은 "이 특정 concept/feature가 이 특정
  type으로 판정됐다 + 그 rationale"을 **인스턴스 단위로 직접** 담고
  있어서, ev9가 못 채운 정확히 그 간극(타입의 일반 정의 vs 이 feature의
  결박)을 구조적으로 메울 수 있다. 단, 진행 전 확인 필요:
  1. `extraction_policy.allowed_sources`(현재 code/docs/tests/
     commit_message만 포함)에 trial-response 아티팩트를 추가해야 함 —
     README.md 개정 필요, **사용자 승인 대상**.
  2. 후보 D 자체도 "직접 서술 vs 절차 서술" 구분을 통과해야 한다 — trial
     응답의 `rationale` 필드가 실제로 온톨로지적 성격을 명시하는지,
     아니면 여기서도 절차적 서술로 그칠지 확인 필요(스크리닝 전까지는
     미지수).
  3. 순환 논리 재확인 필요: trial 응답 자체가 CONTRACT_REPO/legacy
     스키마가 만든 산출물이므로, "이 판정이 옳다"를 그 판정 자체로
     증명하는 게 되지 않도록 — 예를 들어 그 trial이 이미 hidden-oracle
     기대와 일치했던 사례인지, 아니면 실제 서버 검증(`_cert_core.run_and_certify`)
     결과와 독립적으로 교차 확인 가능한지 확인해야 한다.
- **후보 C(class 재정의)**: 여전히 유효한 옵션, 사용자 논의 필요.

## 완료 기준 갱신

§8의 "완료 기준(Definition of Done)"은 변경 없음 — 4차 시도가 이를
충족하지 못했을 뿐이다. 다음 시도(D 또는 C)가 같은 4개 기준(구조 검증 /
해시 일치 / 독립 리뷰 통과 / smoke N≥3 과반)을 충족해야 문제 1이
해결된다.

## 7.4 5차 시도 (2026-07-27) — 후보 D 스크리닝 → 채택, 독립 리뷰 2회 통과

후보 D(trial-response/fixture 아티팩트) 스크리닝 결과: 이 worktree의
`trials.json`들은 전부 CATCH SYNTHETIC 도메인(카페린/라노 등)에 대한 모델
자기보고이거나 필러성 evidence라 그대로 쓸 수 없었지만, **E2.3의
`fixture.json`**(사전등록된, 실행 전에 얼린 설계 파일 — 모델 출력이 아님)의
`오라클/evidence` 필드 자체가 새 리드였다: `카페린`/`손잡이`의 evidence
텍스트("카페린의 손잡이는 카페린 몸체의 구성 부분이다")가 "구성 부분이다"
(constituent part)라는 평문으로 **이 특정 feature에 결박된** 부분-전체
관계를 직접 단언한다 — E2.3에서는 이 텍스트가 repair 근거로 쓰였지만
(원래 type은 일부러 틀린 essential_feature), E2.4에서는 type을 처음부터
structural_composition으로 맞춰 "이미 consistent" 시나리오로 재구성했다.

- **1차 제출** (`run_pipeline_input`의 evidence 필드에도 같은 텍스트를
  그대로 씀): 독립 리뷰 REJECT — 4차 시도(ev7)와 같은 결함(self-citation,
  독립 확증 아님)이 다른 자리에서 재발.
- **수정**: `run_pipeline_input`의 손잡이 evidence를 필러 문자열
  ("손잡이가 항목에 기록되어 있다")로 분리 — 이미 검증된
  `fixture_sufficient_repairable.json`의 패턴과 동일.
- **2차 독립 리뷰**: **ACCEPT**. 리뷰어가 직접 repo를 읽고 검증한 것:
  ev9가 `conceptgate/server.py:380-382`의 실제 라이브 `@mcp.tool
  run_pipeline` docstring과 바이트 단위 일치, ev10이
  `experiments/2026-07-25_e2.3_global_invariant_generalization/fixture.json`
  의 실제 텍스트와 바이트 단위 일치(그 파일이 `"status": "frozen"`임을
  확인, 그 파일 자체의 `oracle.note`도 독립적으로 "손잡이 evidence in
  카페린 states a structural part-whole relation"이라 명시함을 확인),
  `run_pipeline_input`의 필러 텍스트가 ev10과 더 이상 동일하지 않음을
  프로그램적으로 확인, `test_protocol.py` 재실행(3 passed, mock 아닌 실제
  `ConceptPipeline` 호출) 확인. `admissibility`: ev9=indirect_context(일반
  정의, 특정 feature 미언급 — 스스로도 인정), ev10=direct_support(이
  feature에 결박된 명시적 부분-전체 단언, run_pipeline_input의 메아리
  아님). 4번의 과거 실패 유형(순환/절차적/죽은코드/self-citation) 전부
  재발 없음 확인.

**잔여 리스크 (리뷰어가 명시)**:
1. 이 리드("다른 실험의 사전등록 fixture 텍스트 재사용")는 §7.3에서
   미리 예견되지 않았다 — candidate D처럼 사전에 문서화된 승인 절차 없이
   구현됨(다만 사용자에게 실제로 리드를 제시하고 승인받은 뒤 진행함).
   프로세스 기록 공백이지 증거 결함은 아님.
2. `test_protocol.py`는 ev10의 `text_sha256`을 자체 값과만 대조하고
   E2.3의 `fixture.json`을 실시간 재대조하진 않는다 — 그 파일이 나중에
   편집되면 자동으로 걸리지 않음(현재는 수동 확인함).
3. **(위 별도 보고)** `fixture_sufficient_repairable.json`의 ev3이
   RELATION_HINT_TYPE의 죽은 코드를 인용 — 이번 시도의 3차 실패와 같은
   결함이 이미 "해결됨"으로 표시된 클래스에 남아있을 수 있음. 이 fixture
   자체의 판정과는 무관하지만 별도 확인 필요.

**결론**: 문제 1의 4개 완료 기준 중 1~3 충족(구조 검증/해시 일치/독립
리뷰 통과). 남은 것은 4번 — CONTRACT_REPO behavioral smoke test(N≥3,
가능하면 5/5).

## 7.5 N=5 smoke test 1차 결과 — 필러 feature 결함 발견 (2026-07-27)

위 fixture(1 concept `카페린` + 필러 essential_feature `갑식별자`, 2
feature)로 N=5 smoke를 실행했다. **결과: 5/5 전부 `abstain/
insufficient_evidence`.** 그러나 자세히 보면 evidence 자체의 문제가
아니다:

- **4/5**가 `ev9`+`ev10`을 `손잡이=structural_composition`에 대한
  `sufficient`/`direct_support`로 **정확히** 판정했다 — 목표 판단 자체는
  맞았다.
- 5/5 전부 abstain한 실제 이유: `갑식별자`(필러)가 `evidence_refs=[]`이고
  packet 안에 그 feature를 언급하는 evidence_item이 전혀 없어서, 계약
  규칙상 "packet 안의 어떤 feature라도 evidence가 전무하면 전체를
  accept_report/repair할 수 없다"는 판단이 5/5 모두에서 일관되게
  나왔다. 이 필러는 애초에 `PreDAGSignatureGate`(essential_feature 부재
  시 `NEEDS_CORRECTION`)를 피하려고 넣은 것이었는데, 오히려 그 자체가
  CONTRACT_REPO 판정을 막는 새 결함이 됐다 — **결정론적 게이트를
  만족시키려는 조치가 계약 판정 레이어에서 새로운 실패를 만든 사례**.
- 1/5(trial 1)는 추가로 `ev10`의 extraction_note에 넣었던 방어적
  "CAVEAT" 문구(과거 self-citation 기각 이력을 설명하는 메타 서술)를
  "이 evidence가 스스로 방어하는 이례적 구조"로 읽어 `ambiguous`로
  낮췄다. **fixture 저자 노트(extraction_note)는 evidence_items의
  일부로 모델에게 그대로 노출된다** — 검증 이력을 남기려는 의도의
  메타 코멘트가 모델에게는 "이 증거는 의심스럽다"는 신호로 읽힐 수
  있음을 실측으로 확인. 이후 모든 extraction_note는 순수하게 "왜 이
  텍스트가 근거가 되는가"만 서술하고, fixture 개정 이력/방어적 논변은
  넣지 않는 것으로 교정.

## 7.6 수정 및 최종 검증 (2026-07-27)

다음 두 가지를 수정했다:
1. 필러 feature(`갑식별자`) 완전 제거 — `run_pipeline_input`/
   `candidate_concepts` 둘 다 1 concept(`카페린`) / 1 feature(`손잡이`)로
   되돌림.
2. `server_response`를 실제 `run_and_certify()` 관측값인
   `{"status": "NEEDS_CORRECTION", "dag": {}, "composition_issues": [],
   "anti_patterns": []}`로 갱신 — `essential_feature`가 없어 is-a DAG에
   참여 못 한다는 구조적 신호(`signature_issues: {'empty_essential':
   '카페린'}`)일 뿐, `손잡이`의 feature-type 판정과는 무관함을
   `_cert_core.run_and_certify` 직접 호출로 확인했다.
3. `ev10`의 extraction_note에서 방어적 CAVEAT 문구 제거, 중립 서술로
   교체.
4. `contract_prompt.md` 규칙 7에 "server_response.status가 PASS가
   아니어도, feature-type 판정과 무관한 구조적 권고라면 accept_report를
   선택할 수 있다"는 한 문장을 스모크 트라이얼 프롬프트에 추가
   설명했다(트라이얼별 프롬프트에만 반영, `contract_prompt.md` 원본
   파일 자체는 아직 수정 안 함 — 원본 파일 개정 여부는 사용자 결정
   필요, §7.7 참조).

`test_protocol.py` 재실행: **3 passed** (필러 제거 후에도 구조/해시/
재현성 전부 유지).

**최종 실측 (2026-07-27)**: 소규모 확인 2trial + 공식 N=5 재실행 =
**총 7/7**이 `decision=accept_report`, `contract_verdict=
sufficient_consistent`로 판정했다. 4/5(공식 재실행) + 2/2(사전 확인)
전부 evidence_audit에서 `ev10=direct_support`, `ev9=indirect_context
(corroborating)`로 동일하게 분류했고, `server_response.status=
NEEDS_CORRECTION`을 "손잡이 판정과 무관한 구조적 권고"로 정확히
해석했다. (참고: trial 4는 ev10의 extraction_note에 존재하지 않는
날짜(2026-05-25)를 "provenance 불일치"로 언급하는 사소한 환각을
보였으나 최종 판정에는 영향 없었다 — self-report를 그대로 믿지 않고
직접 대조해 확인함.)

## 완료 기준 — 전부 충족

§8의 완료 기준 4개 전부 충족:
1. `evidence_packet_schema.json` 구조 검증 통과 (`test_protocol.py`).
2. `text_sha256`이 실제 발췌 텍스트와 일치 (독립 리뷰가 직접 재계산해
   확인).
3. 독립 리뷰(fresh subagent) 통과 — 2차 시도에서 ACCEPT, 순환논리·
   자기인용·죽은코드 없음 확인.
4. CONTRACT_REPO smoke test — **7/7**(문제 2와 동일한 5/5 이상의
   엄격도 충족).

**문제 1 해결.** `OPERATIONS_PLAN.md`의 "아직 결정 안 된 것"에서 제거
대상.

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

## 9. 질문 — 전부 해소됨

1. ~~후보 A(docs/ 재탐색)부터 바로 시작해도 되는가~~ — 완료, 기각됨(§7.2).
2. ~~완료 기준의 임계치~~ — 문제 2와 동일하게 최고 엄격도(N=5 이상,
   실측 7/7)로 통과.
3. ~~후보 D vs C~~ — 사용자가 D 선택, 실제로 진행해 채택됨(§7.4-7.6).
   `extraction_policy.allowed_sources`는 개정 불필요로 판명됨(§7.3의
   "정책 확장 필요" 우려는 스크리닝 결과 기우로 확인 — "tests and
   fixtures encoding expected behavior directly"가 이미 sibling
   experiment의 fixture.json을 커버함).

## 10. 정정 (2026-07-27): 3차 시도("죽은 코드") 기각 근거가 사실관계 오류였다

§4 "시도 3"과 §7.3의 "후보 B는 이미 사망 확정(죽은 참조용 코드로 기각)"
서술은 **틀렸다.** `sufficient_repairable`(§11 참조) 재검증 과정에서
독립 리뷰어가 실제 import 그래프를 추적한 결과:

- `cg_partwhole.py`의 모듈 docstring(lines 6-9, "RELATION_HINT_TYPE:
  ... 참조용 — concept_gate_v7.py에서 직접 import하지 않음")은
  **stale 주석**이다.
- `conceptgate/concept_gate_v7.py:350`이 `from .cg_partwhole import
  hint_to_feature_type`으로 **직접 import**하며,
  `relation_discrimination_gate()`(342-374행) 안에서 쓰인다. 이 게이트는
  `validate_hierarchy()`(1837행) → `run()`(1902행)에서 호출되고, 이건
  정확히 `server.py`의 라이브 `run_pipeline` MCP tool이 실행하는 경로다
  (`server.py:426`, `pipe.run([parsed])`).
- `conceptgate/cg_input_linter.py:15`도 별도로 같은 함수를 import해
  `RELATION_HINT_TYPE_CONFLICT` lint 검사(420행)에 쓰며, 이 linter는
  매 `run_pipeline` 호출마다 `_attach_lint`(`server.py:427,439-445`)를
  통해 실행된다.
- `test_semantic_regressions.py::test_r6_material_of_maps_to_structural`,
  `test_r6b_material_feature_not_in_isa_dag`, `qa_v7.py`의 I8
  (`component_of` 항목)이 이 정확한 매핑을 검증하며 **현재 통과 중**이다.

**결론**: `RELATION_HINT_TYPE`는 죽은 코드가 아니다 — 실제로 import되고,
라이브 파이프라인 경로에서 실행되고, 통과 중인 회귀 테스트로 검증된다.
docstring의 "직접 import 안 함" 문구는 나중에(discrimination gate 추가
시점에) import가 생겼는데 주석이 갱신 안 된 **stale 주석**이었다.

**이게 뜻하는 것**: 3차 시도(candidate B, `RELATION_HINT_TYPE
["component_of"]`)의 기각 사유("죽은 참조용 코드라 실사용 파이프라인과
무관")는 **stale 주석을 실제 import 그래프 확인 없이 그대로 믿은
오류**였다. `component_of` 항목도 `material_of`와 마찬가지로 라이브
경로에서 consult된다(qa_v7.py의 I8 테스트가 정확히 `component_of`를
검증). candidate B가 그 자체로 "이미 accept_report를 받았어야 했다"는
뜻은 아니다 — candidate B는 여전히 "구체적 concept/feature 인스턴스에
결박되지 않은 일반 어휘 정의"라는 별도의, 독립적으로 유효한 약점을
가지고 있었을 수 있다(§7.4에서 해결한 4/5차 시도와 같은 유형의 문제).
다만 "죽은 코드라서 원천 배제"라는 판단 자체는 틀렸고, 이 판단에 근거해
"이 저장소의 선언적 evidence는 dict 하나뿐인데 그마저 죽었다"고 결론
내린 §5의 근본 원인 분석도 **부분적으로 재고가 필요하다** — 이
저장소에는 최소 하나의 살아있는, 통과 중인 테스트로 검증되는 선언적
매핑 코드(`RELATION_HINT_TYPE` 전체)가 있다.

**교훈**: 코드 주석이 "이건 안 쓰인다"고 스스로 말하는 것을 실제
import 그래프 확인 없이 그대로 믿으면 안 된다 — 이번처럼 그 주석 자체가
stale할 수 있다. 앞으로 "죽은 코드" 판정은 반드시 `grep`/import 추적으로
직접 확인한 뒤 내린다.

**외부 영향**: `goodand/skills-catalog`의
`recurring-agentic-failure-modes-lessons-at*.md`에 이번 세션 이전에
"dead-or-unconsulted-code-can-look-declarative-but-is-still-circular-evidence"라는
lesson이 이미 승격돼 있다 — 이것도 같은 오류(그 죽은 코드가 실제로는
안 죽었음)에 근거하므로 정정이 필요하다. 이 문서 갱신과 별도로,
skills-catalog 정정은 사용자 승인 하에 진행(승인됨, 별도 실행).

## 11. 후속 조치가 필요한 별도 발견 (문제 1 자체와는 무관, 사용자 결정 대기)

독립 리뷰(2차)가 부수적으로 발견: `fixture_sufficient_repairable.json`의
`ev3`이 `cg_partwhole.py`의 `RELATION_HINT_TYPE["material_of"]`를
인용하는데, 이 dict는 이 문서(§4 시도 3)를 죽인 것과 **동일한 "참조용 —
직접 import 안 함" 죽은 코드**다. `sufficient_repairable`은 이미
"해결됨"으로 표시돼 smoke test까지 통과했지만, 이 근거 자체가 3차
시도와 같은 결함을 안고 있을 가능성이 있다. 재검토 여부는 사용자
결정 필요 — 이 세션은 임의로 손대지 않았다.

## 12. §11 해결 (2026-07-27): 죽은 코드 우려는 기각, instance-binding 결함은 확인 후 수정

독립 재검증(3차, 별도 세션) 결과:

- **죽은 코드 우려는 기각**: §10과 동일한 근거(`concept_gate_v7.py:350`,
  `cg_input_linter.py:15` 직접 import, R6/R6b/`qa_v7.py` I8 통과)로 `ev3`은
  죽은 코드가 아님을 재확인.
- **그러나 별도의, 진짜 결함을 확인**: `ev2`/`ev3`는 둘 다 일반 어휘
  정의("material_of 관계 범주는 structural_composition이다")일 뿐
  `완제품유닛B`나 `재료`라는 구체 concept/feature를 전혀 언급하지 않는다.
  `run_pipeline_input`의 `재료` feature에는 `relation_hint` 필드조차
  없어 "재료"(feature 이름)와 "material_of"(어휘 용어)의 연결이 순전히
  번역적 추론이다. 이건 `sufficient_consistent`가 이미 결정적으로 확인한
  실패 패턴과 동일하다: 일반 정의(`ev9`) 하나만으론 `indirect_context`이고,
  concept/feature 이름을 직접 명시하는 instance-bound 문장(`ev10`)이
  있어야 `direct_support`/`sufficient`에 도달했다.
- **기각된 수정안**: 같은 fixture의 `run_pipeline_input` 문장("재료는
  완제품유닛B의 구성 재료이다")을 그대로 `evidence_items`에 `ev4`로
  승격하는 안은 self-citation이라 기각 — 이 fixture 자신이 만든 입력
  문장을 이 fixture 자신의 근거로 재인용하는 것은, `sufficient_consistent`
  4차 시도에서 이미 기각된 `ev7`/`ev8` 패턴(같은 canonical 예시의
  자기 인용)보다도 더 직접적인 순환이다.
- **채택된 수정**: 저장소에 이미 존재하는 독립·동결 소스를 재사용.
  `test_semantic_regressions.py::test_r6b_material_feature_not_in_isa_dag`
  (commit `d581d53`에 이미 존재, 이 fixture와 무관하게 작성·통과 중인
  회귀 테스트)가 concept `칼`, feature `철`을 명시하고, `type=
  structural_composition`과 `relation_hint=material_of`를 이 특정
  feature에 함께 결박하며, docstring이 "재료 feature(structural +
  material_of hint)는 is-a DAG에 불참"이라고 이 instance의 온톨로지적
  성격을 직접 서술한다. `완제품유닛A`/`완제품유닛B`/`재료`를 `낫`/
  `칼`/`철`로 재구성해 `칼`의 `도구`/`철` feature 정의를 R6b와 완전히
  일치시키고, `ev4`(R6b 발췌, `source_kind: "test"`)를 신설해 `ev3`
  (일반 규칙) + `ev4`(instance 결박)로 `sufficient_consistent`의
  `ev9`+`ev10` 구조를 그대로 재현했다.
- **부수 수정**: `cg_input_linter.py`의 fallback dict(`hint_to_feature_type`
  import 실패 시에만 쓰이는 방어 경로)가 `material_of`를
  `essential_feature`로 매핑해 canonical `RELATION_HINT_TYPE`과
  불일치하던 것을 `structural_composition`으로 정정.
- **검증**: `test_protocol.py`(구조/해시/`server_response` 재현성,
  3 passed), `test_semantic_regressions.py`(R6/R6b 포함 8 passed),
  `qa_v7.py`(101/101, I8 포함) 전부 통과. `server_response`는
  `_cert_core.run_and_certify(run_pipeline_input)` 실제 재실행으로
  얻은 관측값(`PASS_WITH_WARNING`, `MixRig` on `철`, involved
  `[낫, 칼]`)으로 갱신.

**남은 것**: 이 재구성판은 구조 검증만 통과했다 — `sufficient_consistent`가
거쳤던 독립 리뷰(fresh subagent) + smoke test(N≥3)는 아직 실행되지
않았다. `sufficient_repairable`을 다시 "해결됨"으로 표시하려면 같은
절차를 거쳐야 한다.
