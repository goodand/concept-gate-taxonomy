# DESIGN REQUEST — E2E-v1(oracle 평가) 실험 설계 판정 (Q19) + before_P1 완료 보고

- 상신: 2026-08-22, 운영 세션
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** 필요한 사실을 이 문서가
  자체 포함하며, 인용은 §7의 감사표를 거쳤다
- 요청 성격: **실험 estimand·범위 판정** + 직전 판정(PASS_WITH_BLOCKER)의
  BLOCKER 해소 확인

---

## 0. 읽는 방법

§1은 완료 보고(확인 요청), §2는 사실(E2E-v1의 조건), §3이 판정 질문 3건,
§5는 운영 세션의 격리된 의견(읽지 않고 판정해도 정보 충분). 선택지에는
상신자가 선호하지 않는 것도 포함했다 — 요청서의 프레이밍이 판정 범위를
정한 선례(P11)의 재발 방지.

## 1. before_P1 완료 보고 — BLOCKER 해소 확인 요청

직전 판정이 명한 순서(fix_W5 → runtime-status contract → oracle titles →
P1)를 전부 실행했다.

| 판정 요구 | 실행 | 검증 |
|---|---|---|
| **W5** — prior 결과의 authenticity 결박 | 기존 receipt 선례(HMAC·host-only 키·domain 분리)를 **verbatim 재사용**해 서명 certificate 구현. 검증 순서 authenticity→subject→revision→validity 고정. raw 문자열 경로는 영구 `diagnostic_only`, certificate 전용 호출만 `certifying` | W5 재현 테스트를 판정 지시대로 **뒤집음**(두 불변식 단언). 적대 subagent가 공격 5종(응답 변조·키 없는 위조·타 claim 재사용·실패 bundle 우회·혼합 강등 우회) 실제 시도 — **5/5 차단** |
| until_fixed의 diagnostic_only | 수정 전 즉시 적용했고, 수정 후 두 경로 지위로 대체 | — |
| **W2 = (a)-refined** | `ExecutionStatus{OK,UNAVAILABLE,ERROR}` × semantic verdict 분리. reasoner 오류 코드를 의존성 부재/실행 실패로 분리. **Dockerfile이 `CONCEPTGATE_REASONER_REQUIREMENT=required` 선언**(귀하의 V2 지적 반영) | 매핑 3경로 + 정보 미소실(FAIL과 "reasoner도 죽음"을 나란히 보고) 테스트 |
| oracle title 교정 | O1/O2/O3/R1을 verbatim 서지 제목으로 + anthology/arxiv locator. name(역할)/title(서지) 분리 유지 | 웹 재확인 |
| **P1** — 실 fixture 관통 | 추가로 **서버측 발급 tool** 신설: 클라이언트는 원문 bundle+claim만 주고 모든 verdict는 서버 in-process 계산(normalizer '응답' 공급 설계는 W5 재판이라 기각). snapshot→발급→인증 전 구간 **손으로 채운 verdict 0** | 실패도 서명되나 실패 bundle엔 발급 0("실패 위에 서명하지 않는다"). 테스트 166 passed |

**확인 요청**: W5를 해소로 인정하는가? 잔여 조건이 있으면 명시해 달라.

## 2. E2E-v1(oracle 평가)의 조건 — 실측 현황

지시 §26과 oracle manifest가 규정한 다음 단계는 IR 능력을 활성화한
oracle 평가다. 조건의 현황:

| 층 | 조건 | 상태 |
|---|---|---|
| 인증 사슬 | 서명 certificate·revision 결박·execution 축·발급 orchestration | **완료** (§1) |
| IR primitive (P3) | Quantifier/Variable/Binding/Modal/Logical + nesting topology | **착수함** — 지시 §11~13이 이미 판정한 범위라 이 상신과 병행 (§5에 진행 방식) |
| 제한 정규화 v0 | α-rename·결정순서 ○ / quantifier 재배열·정리동치 ✕ | manifest의 `canonicalization_profile`이 이미 고정 — 구현만 |
| Evaluate 모듈 | canonical structural match + `PASS/FAIL/UNSCORABLE/ERROR`(Verify 어휘와 분리 — 귀하의 G32 판정) + oracle 격리를 AST 계약으로 | 미착수 |
| oracle fixture | 교정된 출처에서 fixture_template대로 저작 | 미착수. 출처 8건 중 7건 실체 웹 확인, ISO 1건 paywall |
| 시행 주체 | NL→IR을 내는 trial subject | 미착수. **H1a 하네스가 통째로 선례**(schema 강제 cold subagent·동결 manifest·provenance 계약·기계 채점) |

## 3. 판정 질문

### Q19.1 — 어느 oracle부터 시작하는가

manifest의 권장 순서는 **O1(quantifier scope) → O2 → O3**다. 한편 운영
세션의 난이도×확실성 분석은 **O3(modal scope)**를 최상으로 봤다 — 근거:
O3의 authority_type이 `formula_generated`(형식 구조를 먼저 고정하고 NL을
생성)라 gold가 **구성상 정확**하고(주석자 노이즈 0), 요구 IR이 가장
넓다(Modal+Logical 결합자까지).

- (a) **O1 먼저** — manifest 권장 그대로. quantifier/binding primitive가
  O2의 전제라는 순서 논리
- (b) **O3 먼저** — gold 확실성 최상 + IR 최대 절단면을 먼저 검증
- (c) **O1과 O3 병행** — 요구 primitive가 겹치지 않는 부분이 큼
- (d) 그 외

### Q19.2 — "E2E-v1 달성"의 정의

manifest는 의도적으로 N·임계값을 두지 않았다. 다음을 정해 달라:

- fixture 규모 (예: oracle당 N건, 최소 얼마)
- acceptance: 무엇이면 "E2E가 성립했다"인가 — (i) 파이프라인이 전 구간
  오류 없이 관통하고 결과가 4치(PASS/FAIL/UNSCORABLE/ERROR)로 분류되면
  성립(계측 검증), (ii) 특정 PASS율 이상(능력 검증), (iii) 2단계(먼저 i,
  별도 판정 후 ii)
- UNSCORABLE·ERROR의 보고 규약 (H1a의 교훈: 실패 게이트를 null 증거로
  보고 금지 — 여기서 대응물은 무엇인가)

### Q19.3 — 시행 주체와 평가 대상

- 시행 주체: (a) H1a 방식 그대로 — schema 강제 cold subagent(LLM), 동결
  manifest, provenance 계약 (b) 그 외
- 평가 대상: manifest는 evaluator 입력으로 "certified semantic graph"와
  "predicted canonical IR" **둘 다** 허용한다. E2E-v1은 — (a) predicted
  IR을 직접 평가(컴파일 능력 측정, 인증 사슬은 우회) (b) 인증 통과분만
  평가(사슬 전체 관통, 단 미인증 다수면 표본 소실) (c) 둘 다 보고하되
  구별 유지
- 이 실험도 H1a처럼 **사전등록 + 동결 + 외부 판정** 규율을 따르는가
  (상신자는 따른다고 가정하고 준비 중)

## 4. 상위 목적 정렬

사용자의 방향(재현성/생성 제어보다 **피드백과 출력 기반 인과 추론**)에서,
E2E-v1은 "LLM 출력(IR)을 형식 oracle과 대조해 구조화 피드백을 만드는"
첫 실증이다 — D-H1a-18의 next_program 2번 항목의 착지점.

## 5. 운영 세션의 격리된 의견 (판정 자료 아님)

Q19.1은 (b) 또는 (c) — O3의 구성상 정확한 gold가 계측 논쟁을 원천 차단한다.
Q19.2는 (iii) 2단계 — H1a에서 계측 검증과 능력 검증을 섞었을 때의 비용을
지불한 경험. Q19.3은 시행 주체 (a) + 평가 대상 (c). **상신자가 틀릴 수
있는 지점**: O1-먼저의 순서 논리(O2 전제)는 manifest 저작자의 설계 의도라
상신자가 그 무게를 과소평가했을 수 있다.

T2(IR primitive)는 이 상신과 **병행 착수**했다 — §11~13이 이미 판정한
범위이고, Q19의 어떤 답도 IR 자체는 요구하기 때문. 단 Evaluate 모듈과
fixture 저작은 Q19 회신까지 착수하지 않는다.

## 6. 이 상신이 정하지 않는 것

Certified-gate authority 전환(Reason/Derive 입력을 Certified로 좁히기)은
여전히 별도 판정 대상으로 남아 있다 — 이번 질문에 섞지 않았다.

## 7. 인용 감사

| 인용 | 출처 | 확인 |
|---|---|---|
| W5 해소 세부·공격 5종 차단 | 커밋 `b8a53a3`·`741413d`, 적대 검증 스크립트 재실행 | lead가 최종 스크립트 직접 재실행 5/5 |
| Dockerfile required 선언 | Dockerfile | 직접 판독 |
| title 교정 4건 | yaml + ACL/arXiv 페이지 | 웹 실측 2계통 |
| manifest 권장 순서·canonicalization_profile·evaluator 입력 허용 목록 | `semantic_oracle_set_handoff_v0.1.yaml` | 직접 판독 |
| O3 = formula_generated | 같은 파일 + ACL 2025 초록("controlled dataset of ... syllogisms in propositional and modal logic") | 웹 실측 |
| H1a 하네스 선례 | `experiments/2026-07-29_.../_h1a_cohort_run.py` 등 | 이 세션에서 구현·실행 |
| 166 passed / 게이트 8-0-1 | 로컬 실행 | CI 부재 — 자기보고임을 명시 (귀하의 V5 지적 수용) |

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
