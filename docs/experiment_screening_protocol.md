# 순차 스크리닝 실험 운영 프로토콜 (2-stage adaptive N)

- **기원**: E2.2.3(OFAT ablation, 2026-07-25)이 N=20/arm으로 A_ONLY=20/20,
  B_ONLY=1/20, C_ONLY=0/20이라는 극단적으로 명확한 결과를 냈다 — 세 arm
  전부 N=10만으로도 이미 판정이 갈렸을 결과였다. `docs/obligation_layer_roadmap.md`의
  "다음 실험(E2.3, 미확정)"이 다시 OFAT/핵심 arm screening 성격을 가질
  가능성이 높으므로, 매 arm을 처음부터 N=20 confirmatory로 도는 낭비를
  구조적으로 없애는 표준 프로토콜을 여기 확정한다.
- **적용 범위**: 여러 arm/factor를 비교해 "이 중 무엇이 레버인가"를 가르는
  **screening 성격 실험**(OFAT ablation, 핵심 arm 후보 비교 등)에만 쓴다.
  E2.2처럼 단일 효과크기를 정밀 추정해야 하는 **confirmatory 주실험**에는
  쓰지 않는다(아래 "적합/부적합" 참조). 어느 쪽이든 실험 설계 시 README에
  이 문서를 참조하고 어느 쪽 프로토콜을 쓰는지 명시한다.

## 설계

### Stage 1 — Screening (모든 arm, 기본)

- **N=10/arm**, threshold **0.90**.
- 판정 규칙 (pass rate = arm의 성공 trial 수 / 10):
  | rate | 판정 | 처리 |
  |---|---|---|
  | 0.90~1.00 (9~10/10) | **screened PASS** | Stage 2로 승격하지 않음(아래 강제 승격 조건 미해당 시). 잠정 결론으로 보고 |
  | 0.70~0.80 (7~8/10) | **ambiguous** | **Stage 2로 자동 승격** |
  | 0.00~0.60 (0~6/10) | **screened FAIL** | Stage 2로 승격하지 않음. 잠정 결론으로 보고 |

  threshold를 기존 E2.x 계열의 0.80이 아니라 0.90으로 올리는 이유: N=10에서
  0.80을 기준선으로 쓰면 8/10=0.80이 정확히 경계에 걸려 판정이 모호해진다.
  0.90으로 올려 "명백한 성공"만 무증분 통과시키고, 그 아래 애매한 구간
  (7~8/10)은 전부 자동으로 증분 검증을 받게 한다.

- **강제 승격 조건**: rate와 무관하게, 그 arm의 결과가 **다음 마일스톤의
  핵심 주장에 직접 쓰이는 arm**이면 Stage 2로 승격한다. screening 목적의
  arm(비교용, 배제용)은 Stage 1로 끝나도 되지만, 그 결과 자체가 다음
  설계 결정의 근거로 인용될 arm은 N=10 표본으로 끝내지 않는다.

### Stage 2 — Confirmatory 증분 (ambiguous 또는 핵심-주장 arm만)

- Stage 1의 10개 trial을 **폐기하지 않고 그대로 유지**한 채, 같은 arm에
  **10개만 추가 실행**(누적 N=20). 처음부터 20개를 다시 도는 것이 아니라
  증분만 실행 — 이것이 이 프로토콜의 비용 절감 핵심.
- 누적 N=20에 대해 threshold **0.80**을 적용한다(기존 E2.x 계열의
  confirmatory 임계치와 정렬 — Stage 2를 거친 arm은 다른 confirmatory
  라운드 결과와 직접 비교 가능해야 하므로).
- **주의(사전 명시 필요)**: 이 2-stage 절차는 정식 group-sequential
  test(alpha-spending 등)가 아니다. Stage 1과 Stage 2를 합쳐 하나의
  유의성 검정으로 재해석하지 않는다 — 이 프로젝트의 confirmatory 라운드
  (E2.2 등)는 permutation test/bootstrap CI로 별도 수행하며, 이 프로토콜은
  거기에 들어갈 후보를 솎아내는 **descriptive escalation**일 뿐이다.
  과대해석(예: "N=20 결과이므로 p-value가 유효하다")을 방지하기 위해
  보고서에 이 문장을 그대로 인용한다.

## 표현 규정 (보고서/커밋 메시지 작성 시 필수)

Stage 1만 거친 결과에 **"confirmed"라는 표현을 쓰지 않는다.** 대신:

| 상태 | 용어 |
|---|---|
| Stage 1 PASS, 승격 없음 | **screened** (스크리닝 통과, 잠정) |
| Stage 1 FAIL, 승격 없음 | **screened out** (스크리닝 탈락, 잠정) |
| Stage 1 ambiguous, Stage 2 대기/진행 중 | **provisional** |
| Stage 2(N=20 누적) 완료 | **candidate gate** 통과/미통과 — "confirmatory 라운드에 들어갈 후보로서의 관문"이라는 의미. 이 자체가 최종 confirmatory 결론은 아님 |

이 표현들은 이 프로젝트의 기존 Go/No-go(0.80 confirmatory threshold, 정식
permutation/bootstrap)와 문법적으로 구분되어야 한다 — "GO"/"NO_GO"는
confirmatory 라운드 전용 용어로 남기고, screening 라운드의 판정에는 위
표의 용어만 쓴다.

## 비용 근거 (하방 없는 설계)

- E2.2.3의 실제 관측(A_ONLY=1.00, B_ONLY=0.05, C_ONLY=0.00)과 같은 극단
  분포라면 Stage 1(arm당 N=10, 총 30)만으로 세 arm 모두 screened 확정 —
  기존 방식(arm당 N=20, 총 60) 대비 50% 절감.
- ambiguous arm이 있을수록 절감폭은 줄지만, **worst case(전 arm
  ambiguous)에서도 Stage1(10)+Stage2(10)=20으로 기존 방식과 동일** — 즉
  이 프로토콜은 손해를 볼 여지가 없고 하방 리스크가 없다(scale-down이
  실패해도 최악이 현행 유지).

## 적합 / 부적합

- **적합**: OFAT 요인 분리(E2.2.3 유형), 여러 후보 factor 중 핵심 레버를
  가리는 screening, "이 중 뭘 버려도 되는가"를 정하는 비교 실험.
- **부적합**: 단일 효과크기를 정밀 추정해 사전등록된 Go/No-go 다기준
  (c1~c6 등)을 판정해야 하는 confirmatory 주실험(E2.2 유형) — 이런
  실험은 그대로 고정 N, 단일 라운드 사전등록 설계를 유지한다. 표본 크기를
  실험 도중 결과를 보고 늘리는 것 자체가 confirmatory 실험에서는 다중비교
  문제를 일으키므로, 이 프로토콜을 confirmatory 라운드에 적용하지 않는다.

## 다음 실험(E2.3 등)에 적용할 때 체크리스트

1. README에 "이 실험은 screening 프로토콜(`docs/experiment_screening_protocol.md`)을
   따른다" 명시 + 어떤 arm이 "핵심 주장 arm"(강제 승격 대상)인지 사전에
   지정.
2. `fixture.json`/`_gen_prompts.py`에 Stage 1(N=10)만 우선 생성·동결.
   Stage 2 대상이 정해지면 그 arm만 별도로 10개를 증분 생성(같은
   `ORDER_SEED` 계열 유지, `trial` 번호 11~20으로 이어 붙임 — 재현성
   위해 새 seed로 다시 섞지 않는다).
3. `evaluate.py`는 Stage 1 산출 시점에 한 번, Stage 2 완료 후 한 번,
   총 두 번 실행해 두 산출물을 모두 커밋(Stage 1 결과를 덮어쓰지 않고
   별도 기록 — 어떤 arm이 왜 승격됐는지 사후 추적 가능해야 함).
