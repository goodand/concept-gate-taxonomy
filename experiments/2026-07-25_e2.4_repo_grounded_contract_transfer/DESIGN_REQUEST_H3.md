# 설계 판정 요청서 — H3 (E2.4 본 3-arm 실험)

- 발신: E2.4 실험 운영 세션 (worktree `concept-gate-e2.2-wt`, 브랜치 `codex/e2.4-contract-repo-design`)
- 작성: 2026-07-29
- 요청: **설계 판정 6건.** 그중 **D-H3-1이 나머지 전부의 의미를 좌우한다**
- **이 문서는 자족적이다** — 판정에 필요한 실측(M1~M9)을 전부 본문에 담았다.
  파일을 읽을 수 있는 환경이면 §부록 A로 직접 재현할 수 있으나 필수는 아니다

---

## 0. 이 요청서가 기존 인식을 하나 뒤집는다 — 먼저 읽어라

등록부와 HANDOFF는 오랫동안 H3를 막는 것을 **D3(커버리지 재설계) 하나**로
적어 왔다. 이 요청서를 쓰려고 스키마를 실측한 결과, **그보다 앞서는 문제**가
드러났다.

> **3-arm 비교가 성립하는지 자체가 불확실하다.**
>
> H3의 가설은 "CONTRACT_REPO가 legacy arm보다 evidence 불충분·충돌을 더 잘
> 잡아낸다"이고, 그 관측 지표는 **보류(abstain)** 다. 그런데 **legacy arm의
> 스키마에는 `abstain`이 없다.** 보류를 표현할 수단이 없는 arm에서 "보류하지
> 않았다"를 관측하는 것은 모델의 행동이 아니라 **스키마의 제약**을 재는 것일 수
> 있다.

이걸 D3와 함께 올리지 않으면 설계 담당은 "`conflicting` 자리에 무엇을 넣을까"만
답하게 되고, 그 답이 무의미해질 수 있다. **D-H3-1을 먼저 판정해 주시라.**

덧붙여, 같은 프로젝트가 **이 긴장을 이미 한 번 판정했다** — H1a에서 legacy
CONTROL arm은 "보류를 표현할 수 없어 **종속변수를 구조적으로 검열한다**"는
이유로 제외됐다(2-arm 축소). 그 논증이 H3에 전이되는지가 이번 판정의 핵심이다.

---

## 1. H3가 무엇인가

**E2.4의 본 목적이자 아직 한 번도 실행되지 않은 실험이다.**

### 1.1 원 가설 (`README.md` 사전등록 원문)

CONTRACT_REPO가 CONTROL_REPO/A_REPO보다 evidence 불충분·충돌을 더 잘 잡아낸다.

### 1.2 arm 구성 (사전등록)

| arm | 프롬프트 계약 | 출력 스키마 | 원 목적 |
|---|---|---|---|
| `CONTROL_REPO` | repo evidence + 평범한 클라이언트 결정 프롬프트 | legacy | repo evidence만으로 과잉주장·과잉수리가 나오는지 |
| `A_REPO` | repo evidence + E2.3 전역 feature-type invariant | legacy | A 규칙이 repo evidence 위에서도 도움이 되는지 |
| `CONTRACT_REPO` | repo evidence + sufficiency/abstain/repair 계약 | `evidence_contract_v1` | 구조화 계약이 판단 경계를 통제하는지 |

### 1.3 준비 상태

- **CONTRACT_REPO 쪽 재료는 준비됐다** — 3 semantic class가 clean rerun
  cohort(N=10/cell, 30 trial)로 인증됐고, 제약 #11 리뷰까지 끝나 인증이
  4중 논리곱(verdict + 스키마 + 계약준수 + #11) 위에 서 있다.
- **legacy arm 쪽은 아무것도 없다** — 프롬프트도, 실행 경로도, 채점 규약도.
- 원 설계 규모: 8 cell × N=10 = **80 trial** (CONTRACT_REPO 4 class +
  CONTROL_REPO/A_REPO 각 2 class). 단 `conflicting` class가 미확보로 종결돼
  이 배분 자체가 재설계 대상이다.

---

## 2. 실측 사실 (M1~M9) — 판정의 근거. 그대로 받아들여도 된다

| # | 실측 |
|---|---|
| **M1** | legacy 스키마의 `decision` 선택지는 **`report_done` / `repair` / `request_evidence` 세 개뿐**이다. **`abstain`이 없다.** CONTRACT_REPO는 `accept_report` / `repair` / `abstain` |
| **M2** | 두 스키마의 **공통 필드는 `decision`, `repaired_concepts`, `report` 3개뿐**이다. CONTRACT_REPO에만 있는 것: `contract_verdict`, `evidence_scope`, `evidence_audit`, `feature_judgments`, `invariant_checks`, `repair_plan`, `abstain` |
| **M3** | **`contract_verdict`는 CONTRACT_REPO에만 있다.** 그런데 사전등록된 채점 규약(`OPERATIONS_PLAN.md` Phase 6)은 *"`decision` 일치가 아니라 `contract_verdict` 일치로 채점한다"* 이다 → **legacy arm에 적용 불가** |
| **M4** | 스키마 파일 자신이 legacy 유지 근거를 밝힌다: *"CONTROL_REPO and A_REPO keep the legacy client decision shape used by E2.3 **so their behavior remains comparable**"* → 그 비교 가능성은 **E2.3(선행 실험)과의** 것이지 **arm 간의** 것이 아니다. **두 축이 혼동돼 있다** |
| **M5** | `arm_schema_map`이 이미 존재하고 arm별 스키마를 매핑한다(`CONTROL_REPO`→legacy, `A_REPO`→legacy, `CONTRACT_REPO`→`evidence_contract_v1`) → arm별 스키마를 바꾸는 것 자체는 **새 추상화가 아니다** |
| **M6** | **H3를 동기부여한 유일한 arm 비교 실측은 세 겹으로 무효 조건에 걸려 있다** — ① N=1 ② 오라클 유출 packet 기반 ③ 그 fixture(`conflicting`)는 이후 커버리지에서 **제외**됨 |
| **M7** | **같은 프로젝트가 이 긴장을 이미 판정했다.** H1a 외부 설계 판정: legacy CONTROL은 "보류를 표현할 수 없어 핵심 종속변수를 **구조적으로 검열**한다"며 arm에서 **제외**, 2-arm으로 축소 |
| **M8** | **E2.4의 실행 파이프라인은 `_surface.py`(빌더·qualification) + `_cohort.py`(agent/freeze/record) + `_score.py`다.** `_gen_prompts.py`는 이 실험에 **없고, 이 실험의 방식이 아니다** — 구세대 실험들이 쓰던 것이다 |
| **M9** | 코호트 인프라는 N=10/cell로 실증됐다(30 trial 실행·인증 완료). 재실행 규모 정책은 **단계적 조기중단**으로 확정됐다(smoke 먼저 → 임계점 미달 조건 확인 → 미달이면 수정, 아니면 계속) |

### 2.1 정정 — 이 저장소가 오랫동안 잘못 적어온 것

등록부와 HANDOFF는 H3의 선행 과제를 **"`_gen_prompts.py`가 존재하지 않는다,
새로 작성해야 한다"** 로 적어 왔다. **M8에 비추어 이 표현은 오도다.** E2.4는
그 방식을 쓰지 않으므로, 필요한 것은 `_gen_prompts.py` 신설이 아니라 **기존
빌더를 legacy arm까지 확장하는 것**일 가능성이 높다. D-H3-4에서 다룬다.

---

## 3. 판정 요청 6건

각 항목은 **질문 → 왜 결정 사항인가 → 선택지 → 실측 제약 → 권고 → 미판정 시
귀결** 순이다. **권고 블록은 비구속이며 앵커링을 피하려고 분리해 두었다.**

---

### D-H3-1 【최우선】 3-arm 비교가 성립하는가

#### 질문
legacy arm은 `abstain`을 표현할 수 없고(M1) `contract_verdict`가 없어 사전등록
채점 규약이 적용되지 않는다(M3). **이 상태로 arm을 비교하면 무엇을 재는 것인가?**

#### 왜 결정 사항인가
H3 가설의 관측 지표는 "불충분·충돌을 잡아내는가"이고, 그 행동적 표현이
**보류**다. legacy arm에서 관측되는 "보류 안 함"은 두 가지로 해석될 수 있다:

1. 모델이 실제로 과잉주장했다 (**측정하려는 것**)
2. 모델이 보류하려 해도 그것을 담을 선택지가 없었다 (**스키마의 제약**)

**이 둘을 분리할 수단이 현재 설계에 없다.** 분리하지 못한 채 실행하면 어떤
결과가 나오든 가설을 지지하는 것처럼 읽힌다.

M4가 문제의 뿌리를 보여준다 — legacy 유지의 명시적 근거는 **E2.3과의** 비교
가능성인데, H3가 요구하는 것은 **arm 간** 비교 가능성이다. 서로 다른 두 축이
같은 결정으로 처리돼 있다.

#### 선택지

| 안 | 내용 | 대가 |
|---|---|---|
| **A** | legacy 유지. `decision`으로 채점하고 **`request_evidence` ≈ `abstain`** 매핑을 사전등록 | 매핑의 의미론적 타당성이 미검증이다. "증거를 더 달라"와 "판단을 보류한다"는 다르다. 또 이 프로젝트는 이미 *"`decision`만 보면 불안정한 판정이 만장일치로 보인다"* 를 실측으로 기록했다(`PROBLEM_2` §5.1: `decision` 5/5 안정인데 `contract_verdict`는 4:1로 갈렸다) |
| **B** | legacy arm 스키마에 **`abstain`만 최소 추가** | 더 이상 "legacy"가 아니게 되어 **E2.3 계보와의 비교 축이 끊긴다**(M4가 지키려던 것). arm 이름과 실체가 어긋남 |
| **C** | **legacy arm 제외**, CONTRACT_REPO 내부 대조(class 간)로 축소 | H1a 판정(M7)과 일관. 단 **"계약이 legacy보다 낫다"는 원 가설 자체를 포기**하게 된다 |
| **D** | H3를 **행동 분포 비교(서술적)** 로 재정의 — 정답률·인증 없이 arm별 행동 분포만 기록 | H1a와 같은 틀. 인증 체계(임계 0.90·3구간 밴드) 사용 불가, 종료 기준을 따로 정의해야 함 |

#### 실측 제약
- **M1·M2·M3** — 비교 가능한 표면이 3개 필드뿐이고 채점 규약이 한쪽에만 적용된다.
- **M5** — arm별 스키마 변경(안 B)은 기존 구조 안에서 가능하다. 새 추상화가 아니다.
- **M7** — 동일 논증이 H1a에서 이미 "제외" 결론에 도달했다. 다만 H1a는 가설
  자체가 legacy를 필요로 하지 않았고, **H3는 가설이 legacy 대조를 명시한다**는
  차이가 있다. 그 차이가 결론을 바꾸는지가 판정 사항이다.

> **권고 (비구속 — 앵커링 주의)**
>
> **B 또는 D를 권한다.**
>
> A는 매핑의 타당성이 미검증인 채로 결론의 무게를 감당해야 한다 — 그리고 이
> 프로젝트는 `decision` 단독 채점을 이미 한 번 불신하기로 결정했다.
>
> C는 가장 안전하지만 원 가설을 버린다. 이 실험 전체가 그 가설을 위해 설계된
> 것이므로 비용이 크다.
>
> B는 "legacy"의 의미를 잃지만 **arm 간 비교를 성립시키는 최소 변경**이다. 다만
> 그 arm이 무엇의 대조군인지 이름과 문서를 다시 정의해야 한다.
>
> D는 H1a와 틀이 같아 운영 일관성이 있고, "무엇이 일어나는가"를 먼저 보는
> 탐색적 단계로 H3를 재배치한다. 인증을 포기하는 대신 해석 위험이 없다.
>
> *비구속. 반대 결론이 나와도 그대로 따른다.*

#### 미판정 시 귀결
D-H3-2(커버리지)·D-H3-3(채점 지표)·D-H3-5(규모)를 결정할 수 없다. 셋 다
"무엇을 어떻게 비교하는가"에 종속되기 때문이다.

---

### D-H3-2 `conflicting`이 빠진 자리에 무엇을 넣는가 (기존 D3 / H1c)

#### 질문
원 설계는 CONTROL_REPO/A_REPO에 `sufficient_consistent` + `conflicting` 2개를
배정했다. `conflicting`이 미확보로 종결된 지금, 그 자리를 무엇으로 채우는가?

#### 왜 결정 사항인가
`conflicting`은 **arm 비교의 최고 신호 셀**이었다. 이 실험을 동기부여한 유일한
arm 비교 관측이 바로 그 fixture에서 나왔다 — legacy 두 arm은 조용히 repair했고
CONTRACT_REPO만 정확히 보류했다. 그게 빠지면 abstain-target class 중 남는 건
`insufficient` 하나뿐이다.

#### 선택지

| 안 | 내용 |
|---|---|
| A | `conflicting` 자리에 **`insufficient`** 를 넣는다 (abstain-target 유지) |
| B | **`sufficient_repairable`** 을 넣는다 (과잉수리 관측에 초점) |
| C | `insufficient` **단독**으로 두고 N을 늘린다 (cell 수 감소, 통계력 집중) |
| D | D-H3-1의 결론에 따라 **배분 자체를 새로 설계** |

#### 실측 제약
- **M6** — 대체하려는 신호 자체가 N=1·유출·제외 삼중으로 무효다. 즉 "무엇으로
  대체할까"의 기준이 될 원 관측이 인용 불가 상태다.
- 현재 인증된 3 class는 `sufficient_consistent`(accept), `sufficient_repairable`(repair),
  `insufficient`(abstain)로 **세 가지 결정 유형을 하나씩** 덮는다.

> **권고 (비구속 — 앵커링 주의)**
>
> **D-H3-1을 먼저 판정하면 이 항목의 선택지가 줄어든다.** 특히 D-H3-1이 C(legacy
> 제외) 또는 D(서술적 재정의)로 가면 "legacy arm에 어떤 2개를 배정할까"라는
> 질문 자체가 소멸하거나 형태가 바뀐다. 순서를 지켜 주시라. *비구속.*

#### 미판정 시 귀결
H3의 cell 배분과 규모를 확정할 수 없다.

---

### D-H3-3 arm 간 채점 지표

#### 질문
사전등록 채점 규약(`contract_verdict` 일치)이 legacy arm에 적용 불가하다(M3).
arm을 가로지르는 비교 지표를 무엇으로 정의하는가?

#### 왜 결정 사항인가
지표가 정해지지 않으면 "CONTRACT_REPO가 더 낫다"를 무엇으로 판정할지가 없다.
그리고 이 프로젝트는 `decision` 단독 채점을 이미 불신하기로 했다.

#### 선택지

| 안 | 내용 |
|---|---|
| A | 공통 필드 `decision`만으로 채점 + arm별 enum 매핑을 사전등록 |
| B | **arm-agnostic 행동 코더**를 별도로 만들어 세 arm의 출력을 동일 범주(예: 확정 / 수리 / 보류 / 무효)로 분류 |
| C | arm별로 다른 지표를 쓰고 **직접 비교하지 않는다** — 각 arm을 독립적으로 서술 |

#### 실측 제약
- **M2** — 공통 필드가 3개뿐이라 A의 정보량이 매우 낮다.
- B는 H1a가 채택한 방식과 같은 구조다(행동 코더 + 후처리 분류). 다만 **코더 자체가
  검증 대상**이 된다 — 이 프로젝트는 검사기를 만들 때 recall/precision 양방향
  테스트를 요구하고(등록부 [DONE] #13·#16), 방금 D4에서 그 규율을 실제로 적용했다.

> **권고 (비구속 — 앵커링 주의)**
>
> **B.** 단 코더를 **결과 확인 전에 동결**하고 라벨 코퍼스로 recall/precision을
> 먼저 측정해야 한다. D4의 `_review_11.py`가 그 패턴의 작동 예다 — 교정 없이는
> 인증급 사용을 코드가 거부하도록 만들었다. *비구속.*

#### 미판정 시 귀결
실행해도 결과를 해석할 수 없다.

---

### D-H3-4 legacy arm 프롬프트 생성 경로

#### 질문
CONTROL_REPO/A_REPO의 프롬프트를 **기존 빌더 확장**으로 만드는가, **별도 스크립트**로 만드는가?

#### 왜 결정 사항인가
등록부·HANDOFF가 이 선행 과제를 **"`_gen_prompts.py` 부재"** 로 적어 왔으나
**그 표현이 오도다**(M8, §2.1). E2.4는 `_surface.py`+`_cohort.py`+`_score.py`
파이프라인을 쓴다. 잘못된 전제로 스코핑하면 이 실험이 쓰지 않는 방식의 스크립트를
새로 만들게 된다.

#### 선택지

| 안 | 내용 | 대가 |
|---|---|---|
| A | `_surface.render_prompt()`를 arm별 계약 텍스트를 받도록 확장 | 동결된 `_surface.py`를 수정 → 방법론의 동결 규율과 충돌 |
| B | legacy 전용 렌더 경로를 **별도 모듈**로 추가하고 payload 빌더는 공유 | payload 화이트리스트는 한 곳 유지, 계약 텍스트만 분기 |
| C | H3 전용 사본을 두고 그 안에서 확장 | E2.4 동결본 불변. 중복 |

#### 실측 제약
- **모델 입력 payload는 세 arm이 동일해야 한다** — 같은 evidence, 같은 concept.
  다른 것은 **계약 프롬프트 텍스트와 출력 스키마뿐**이어야 arm 대조가 성립한다.
- 새 파일을 만든다면 `spec_from_file_location` + **고유 `sys.modules` 키**를 써야
  한다. 이 저장소는 실험 폴더 간 모듈명 충돌로 **한 실험이 남의 코드로 조용히
  실행된 사고**를 겪었다(등록부 [DONE] #6).

> **권고 (비구속 — 앵커링 주의)**
>
> **B.** payload 빌더(화이트리스트·qualification)는 세 arm이 반드시 공유해야
> 하고 — 그게 오라클 유출을 막는 유일한 장치다 — 갈라져야 하는 것은 계약
> 텍스트와 스키마뿐이다. 그 분기점은 이미 `arm_schema_map`이 있다(M5). *비구속.*

#### 미판정 시 귀결
legacy arm을 실행할 수 없다.

---

### D-H3-5 규모와 조기중단

#### 질문
원 설계는 8 cell × N=10 = 80 trial이다. 여기에 D5로 확정된 **단계적 조기중단**
정책을 어떻게 적용하는가?

#### 실측 제약
- **M9** — 코호트 인프라는 N=10/cell로 실증됐고, 조기중단 정책이 이미 확정돼 있다
  (smoke 먼저 → 미달 조건 확인 → 미달이면 수정, 아니면 계속).
- 30 trial 실행 때 **22건이 API 세션 사용 한도로 실패**했다. 이는 전송 실패이지
  trial 데이터가 아니므로 기록하지 않고 실패분만 재실행해 병합했다. 80 trial
  규모에서는 이 패턴이 다시 나올 가능성이 높다.
- D-H3-2의 결론에 따라 cell 수가 달라지므로 총량은 그 뒤에 확정된다.

> **권고 (비구속 — 앵커링 주의)**
>
> arm 간 대조는 **같은 fixture에 대해 세 arm을 나란히** 돌려야 의미가 있으므로,
> 조기중단 단위를 "cell"이 아니라 **"fixture × 3 arm 묶음"** 으로 잡는 편이
> 낫다. 한 arm만 먼저 다 돌리면 중간 판정 시점에 비교할 짝이 없다. *비구속.*

#### 미판정 시 귀결
실행 계획을 세울 수 없다.

---

### D-H3-6 H3가 여전히 정당한가

#### 질문
이 실험을 실행할 근거가 지금도 충분한가?

#### 왜 결정 사항인가
**H3를 동기부여한 유일한 실측이 세 겹으로 무효다**(M6):

1. **N=1** — 단일 관측
2. **오라클 유출 packet 기반** — 그 실행 자체가 인증 근거에서 배제됨
3. **그 fixture는 커버리지에서 제외됨** — `conflicting`은 미확보로 종결

즉 "legacy는 조용히 repair하고 CONTRACT_REPO만 보류했다"는 관측은 **현재
인용 가능한 근거가 아니다.** 그 위에 80 trial 규모의 실험을 세우는 것이
정당한지는 별도 판단이 필요하다.

> 유출 방향을 따져보면 이 관측이 유출로 *설명되지는* 않는다 — 유출 문구는
> "보류가 옳다"는 쪽을 가리켰는데 legacy arm들은 그럼에도 repair를 강행했다.
> 게다가 legacy 스키마에는 `abstain` 어휘 자체가 없어(M1) 유출 문구가 그들의
> 선택지에 직접 매핑되지도 않았다. **다만 이는 "유출로 설명되지 않는다"이지
> "재현됐다"가 아니다.**

#### 선택지

| 안 | 내용 |
|---|---|
| A | 그대로 진행 — 가설은 사전등록됐고 재현이 곧 실험의 목적이다 |
| B | 먼저 **소규모 재현**(예: 1 fixture × 3 arm × N=5)으로 신호가 있는지 확인한 뒤 본 실행 여부를 결정 |
| C | H3를 보류하고 다른 미결(H1a, H2)을 먼저 진행 |

> **권고 (비구속 — 앵커링 주의)**
>
> **B.** D5가 확정한 조기중단 정책의 정신과 같다 — 큰 비용을 들이기 전에
> 값싼 관측으로 미달 조건을 먼저 본다. 신호가 없으면 80 trial을 아끼고, 있으면
> 그 자체가 재현이므로 M6의 세 겹 무효가 해소된다. *비구속.*

#### 미판정 시 귀결
근거가 불확실한 채로 대규모 실행에 들어간다.

---

## 4. 판정 순서

```
D-H3-1 (비교 성립 여부) ──┬──> D-H3-2 (커버리지)
                          ├──> D-H3-3 (채점 지표)
                          └──> D-H3-5 (규모)

D-H3-6 (정당성) ──────────────> 전체 실행 여부

D-H3-4 (생성 경로) : 독립
```

**D-H3-1과 D-H3-6을 먼저 판정하면 나머지 4건의 범위가 크게 줄어든다.**
특히 D-H3-6이 C(보류)로 가면 나머지는 전부 유예된다.

## 5. 넘을 수 없는 제약

1. **모델 입력 evidence 필드는 `evidence_id` / `source_kind` / `text` 3개뿐**
   이다(2026-07-29 운영 지시). 금지 필드 14종에 `liveness`·`authority`·
   `supersession`·fixture class·기대 판정이 포함된다.
2. **세 arm의 payload는 동일해야 한다.** 다른 것은 계약 텍스트와 출력 스키마뿐.
   payload 빌더는 반드시 공유한다 — 그것이 오라클 유출을 막는 장치다.
3. **동결 아티팩트는 소급 수정하지 않는다.** E2.4의 `fixture_*.json`,
   `contract_prompt.md`, `cohort_prompts.json`은 이미 인증에 쓰였다.
4. **fixture evidence는 원문과 바이트 일치해야 한다** — `qualify_fixture()`가
   강제하며 불일치 시 payload 생성을 거부한다.
5. **새 파일은 `spec_from_file_location` + 고유 `sys.modules` 키**로 로드한다
   (등록부 [DONE] #6).
6. **검사기·코더를 만들면 결과 확인 전에 동결하고 recall/precision을 양방향으로
   측정한다**(등록부 [DONE] #13·#16, D4에서 실제 적용).

## 6. 회신 형식

```text
DESIGN DECISION — H3 (E2.4 3-arm comparison)
decided_by:
date:

D-H3-1 (비교 성립 여부):   <A|B|C|D|other>   근거:
D-H3-6 (실험 정당성):      <A|B|C|other>     근거:
D-H3-2 (커버리지):         <A|B|C|D|other>   근거:
D-H3-3 (채점 지표):        <A|B|C|other>     근거:
D-H3-4 (생성 경로):        <A|B|C|other>     근거:
D-H3-5 (규모·조기중단):    <내용>            근거:

deferred:
  <항목 ID>: <사유 / 판정에 필요한 정보>

new_constraints:
  <이 판정이 새로 부과하는 제약 — 후속 세션이 지켜야 할 것>

실험 진행 여부:
  <계속 | 재정의 필요 | 보류 | 중단>   사유:
```

**정보가 부족해 판정할 수 없으면 `deferred`에 필요한 정보를 구체적으로 적어
주시라 — 추측으로 채우지 말 것.**

## 부록 A — 파일을 읽을 수 있는 환경이라면 (선택)

판정에 필수가 아니다. 실험 폴더:
`experiments/2026-07-25_e2.4_repo_grounded_contract_transfer`

```bash
# M1·M2·M3 — 두 스키마의 공통 표면과 차이
python3 -c "
import json; d=json.load(open('decision_schema.json'))
L=d['variants']['legacy_decision']['schema']; C=d['variants']['evidence_contract_v1']['schema']
print('legacy decision :', L['properties']['decision']['enum'])
print('contract decision:', C['properties']['decision']['enum'])
print('공통 필드:', sorted(set(L['properties']) & set(C['properties'])))
print('CONTRACT 전용:', sorted(set(C['properties']) - set(L['properties'])))
"

# M4 — 스키마 자신이 밝힌 legacy 유지 근거
python3 -c "
import json; d=json.load(open('decision_schema.json'))
print(d['description'][:400]); print(); print(d['variants']['legacy_decision']['description'])
"

# M5 — arm별 스키마 매핑이 이미 존재
python3 -c "import json; print(json.load(open('decision_schema.json'))['arm_schema_map'])"

# M8 — 이 실험의 파이프라인 (그리고 _gen_prompts.py 부재)
ls _*.py; ls _gen_prompts.py 2>&1 | tail -1

# M6·M7 배경
grep -n "핵심 검증 결과" -A 20 OPERATIONS_PLAN.md   # 유일한 arm 비교 관측 + 정정 주석
sed -n '/D-H1a-6/,/미판정 시/p' ../2026-07-29_h1a_source_authority_unresolved/README.md 2>/dev/null || \
  grep -n "legacy CONTROL" -B2 -A8 ../2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION.md
```

참조 문서(읽기 전용): `README.md`(사전등록 설계), `OPERATIONS_PLAN.md`(Phase 5·6),
`PROBLEM_2_conflicting.md`(§5.1 decision vs contract_verdict 실측),
`../../docs/E2.4_ISSUE_REGISTER.md`(미결 전체 + 해결 이력 25건),
`../2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION.md`(M7의 판정 원문).

## 부록 B — 용어

| 용어 | 뜻 |
|---|---|
| **arm** | 실험 조건. 같은 재료를 서로 다른 프롬프트/스키마로 처리해 비교하는 단위 |
| **cell** | (fixture class × arm) 하나. 사전등록 N은 cell당 시행 수 |
| **hidden oracle** | 기대 정답. 별도 파일에 있고 프롬프트 생성기는 접근하지 않는다 |
| **qualification** | 실행 전 검증. 모든 evidence를 원문과 바이트 대조하고 실패 시 payload 생성을 거부 |
| **동결(freeze)** | 실행 전에 프롬프트 바이트와 해시를 커밋해 고정. 결과가 설계를 소급 수정하지 못하게 한다 |
| **clean rerun cohort** | 유출 제거 후 화이트리스트 빌더를 거쳐 새로 실행한 코호트. "재채점"도 "재현"도 아니다 |
| **screened_PASS / ambiguous / screened_FAIL** | 사전등록 3구간 밴드(≥0.90 / ≥0.70 / 그 미만) |
