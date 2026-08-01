# H1a 사전등록 — P1~P7

- 작성: 2026-07-30. **갱신 1: 2026-07-30** — `DESIGN_DECISION_H1a_manipulation_scope.md`
  (독립 리뷰 blocker #16·#14에 대한 외부 판정, Q1=B·Q2=B) 반영.
  **갱신 2: 2026-07-31** — §11.2a 보조 해석가능성 조건 + §11.2b 배치 규약
  등재. **갱신 3: 2026-07-31** — `DESIGN_DECISION_H1a_prompt_surface.md`
  (Q3=B·Q4=승인) 반영: §P0.1 조작 재구현(H1a 전용 프롬프트), §11.2a 문구를
  판정문의 개선안으로 교체. **전부 trial 0건 시점이라 재동결 비용 없음**
- 지위: **사전등록.** 이 문서는 H1a trial을 **한 건도 실행하기 전에** 커밋된다.
  판정 장치를 결과를 본 뒤에 정하면 그것은 장치가 아니라 사후 합리화다.
- 근거: `DESIGN_DECISION.md`(외부 판정 D-H1a-1~7), `DESIGN_DECISION_H1a_manipulation_scope.md`
  (Q1·Q2 판정, 조작 범위 재확정), `README.md` §7이 남긴 미정 7항목.
- 선례 규율: `../2026-07-25_e2.4_repo_grounded_contract_transfer/DESIGN_D4_constraint_11_review.md`
  (교정 코퍼스를 `results` 비운 채 실행 전 커밋 → 나중에 채움).

---

## 0. 먼저 확정 — 이 실험이 주장할 수 있는 것의 상한

P1~P7보다 앞선다. **H1a는 fixture 1개(칼/철) 위에서 돈다. 즉 K=1이다.**

E2.4의 H3 확증 판정(`DESIGN_DECISION_H3_CONFIRMATORY.md`, D-H3C-1)이 바로
이 구조에 대해 형식 판정을 내렸다:

> 유일한 확률원이 모델 샘플링일 때 추정 가능한 값은
> `P(행동 | 고정 packet, 고정 arm, 고정 모델·파라미터)`뿐이며, N(=R)을 늘리면
> 그 추정치가 정밀해질 뿐 packet 일반으로 일반화되지 않는다.

H1a는 같은 자리에 있다. 따라서 **결과를 보기 전에** 허용 결론을 못박는다.

**허용**: "이 고정 fixture에서, 금지 문장 유무에 따라 select/defer 행동
분포가 달랐다(또는 다르지 않았다)."

**금지**: 모델 일반 성향, source-authority 상황 일반, 다른 fixture로의 전이,
"계약이 더 낫다/나쁘다"류 규범 판정. 그리고 **인과 귀속**(D-H1a-7이 이미
금지) — fixture가 `source_kind`와 원문 내부 표현을 함께 담고 있어 두 원인을
분리하지 못한다.

**N을 늘려도 이 상한은 올라가지 않는다.** N은 within-packet 추정의 해상도만
바꾼다. 이 문장을 여기 박아두는 이유는, H3에서 그 사실을 **결과를 본 뒤에**
알았기 때문이다.

**null 결론은 진단 게이트(§11)를 통과한 뒤에만, 그리고 그때도 좁게만
보고할 수 있다.** 판정문 원문:

> Under this fixed packet, fixed source order, fixed anchor, model,
> transport, and parameters, no arm difference was observed; the anchor
> diagnostic did not detect gross ceiling behavior under the preregistered
> perturbation.

**"조작이 일반적으로 효과가 없다"는 식으로 보고할 수 없다.**

---

## P0.1 — 조작의 범위 재확정 (D-H1A-MANIPULATION-SCOPE, 2026-07-30)

**독립 리뷰 blocker #16**: 초안(README §4.1, 폐기)은 계약 서문의 금지
문장 한 개(block L8)만 지웠는데, 절대 규칙 1에 **논리적으로 동등하고 더
명시적인** 금지(block L24-25)가 그대로 남아 있었다. `PROHIBITION_REMOVED`
arm이 실은 금지를 제거하지 못했다는 뜻이고, byte-level diff 테스트는 "diff가
그 한 문장인가"만 검사해 이 결함을 통과시켰다.

**외부 판정(Q1=B)이 D-H1a-5를 다음으로 재정의한다:**

> Minimal semantic edit: remove all model-facing clauses that prohibit
> liveness, source-priority, recency, authority, or supersession
> adjudication. Preserve all other packet-boundary and no-external-knowledge
> constraints.

**최초 구현(2026-07-30)은 E2.4의 계약문 113행 전체를 재사용하고 두 절만
제거하는 방식이었다.** 그 방식으로 첫 trial 프롬프트를 실제로 조립해 보니
E2.4 규칙 2~7이 `h1a_observation_v1`과 맞물리지 않고, 특히 **규칙 3의 동률
조항이 H1a fixture의 정확한 모양을 무조건 `defer`로 매핑**해 조작과 무관한
천장을 만들 위험이 드러났다(G2·G3, `docs/H1A_ISSUE_REGISTER.md`). 이를 Q3로
상신했다.

**외부 판정(Q3=B, `DESIGN_DECISION_H1a_prompt_surface.md`)이 프롬프트 표면
자체를 재정의한다**: E2.4 규칙 2~7과 서문을 버리고, `h1a_observation_v1`에
맞춰 새로 쓴 **H1a 전용 task 지시문**을 쓴다. 규칙 1의 packet-boundary
실질(외부 지식 사용 금지)은 판정문 자신의 영어 문구로 재작성되어 남는다.
**Q1의 절 제거 판정 자체는 재론되지 않았다** — 무엇을 지우는가는 그대로이고,
어떤 텍스트 위에 지우는가만 바뀌었다.

**Q3.1(부수 질문) — "그럴듯하다"가 recency/authority를 포괄하는가**: 판정문
답은 "예, 기능적으로." 규칙 3은 알고리즘적이라 동률이면 근거 종류와 무관하게
무조건 null을 요구하므로, §4.1이 우려한 "치명" 해석이 맞다고 확인됐다. 이것이
B안(규칙 2~7 폐기)을 확정하는 결정적 근거였다.

구현: `_h1a_contract.py`. H1a 전용 템플릿은 `DESIGN_DECISION_H1a_prompt_surface.md`
자신의 fenced block에서 **로드**한다(재입력하지 않음 — 전사 오류 방지).
Q1의 두 절(`L8`, `L24_25`)은 원문 그대로 정규화(공백만 접기, 문자는 보존)해
템플릿의 유일한 packet-boundary 문장("...or external sources.") 바로 뒤에
`PROHIBITION_KEPT`에만 삽입한다. `assert_no_residual_prohibition`이 구조
가드 + 어휘 tripwire를 검사하고, `diff_is_restricted_to_the_liveness_clause`가
재구성 방식으로 두 arm의 차이가 정확히 그 삽입 절뿐임을 증명한다.
`test_h1a_contract.py` 18 passed, 뮤테이션 4종 전부 CAUGHT.

**영어/한국어 혼용은 저작 판단이지 재론 대상이 아니다.** 판정문 템플릿은
영어이고 Q1의 절은 한국어다. 번역하면 그 번역 자체가 새로운, 검토되지 않은
저작 행위가 되므로, 원문 바이트를 그대로 삽입했다. 이 선택은
`_h1a_contract.py` 모듈 docstring에 명시했고 독립 리뷰의 우선 점검 대상이다.

**변경되지 않는 것**: packet-boundary 실질(외부 지식·문맥 사용 금지)은 양쪽
arm에 그대로 남는다. `h1a_observation_v1` 스키마는 불변(판정문 new_constraints).

---

## P1 — 시행 수 (N)

**arm당 N=20, 총 40 trial.** 단계 실행은 P7 참조.

근거:

- 인증 밴드를 쓰지 않으므로(D-H1a-4) E2.4의 0.90 임계와 N=10 보정은 **적용
  대상이 아니다.** N은 통계적 합격선이 아니라 **관측 해상도**로만 정한다.
- N=10이면 trial 1건이 비율을 0.10 움직인다. 두 arm의 분포 차이를 보는
  실험에서 이 입도는 거칠다. N=20이면 0.05로 절반이 된다.
- N=20/arm은 E2.4 H3 pilot(45 trial)과 같은 자릿수라 비용·시간이 검증돼 있다.
- **N을 더 늘려도 §0의 상한은 그대로다.** 20은 "충분히 정밀하되 일반화
  착시를 부추기지 않는" 자리로 고른 값이다.

---

## P2 — randomization

**bundle 단위 실행 + 사전 생성 고정 순서.**

- 같은 replicate index의 두 arm을 하나의 **bundle**로 묶는다(E2.4 H3의
  D-H3-5 실행 단위와 동일). bundle 20개.
- bundle 내 두 arm은 **동시 실행**한다. trial subject는 상태 없는 cold
  subagent이므로 arm 순서 효과가 구조적으로 존재하지 않는다 — 균형 순서를
  따로 짤 필요가 없고, 짜는 척하는 것이 오히려 오도다.
- bundle 사이의 실행 순서는 **E2.3의 `sha256_blocked_sort` 패턴**으로 사전
  생성해 매니페스트에 고정한다(seed 문자열을 사전등록: `H1A-fixed-order-v1`).
- trial id는 `H1A-{arm}-{replicate:02d}` 형식으로 사전 생성한다.

### P2.1 — evidence 순서 고정 (독립 리뷰 20260730 #13)

`evidence_sources`는 두 arm이 **완전히 동일한 fixture 파일**을 공유한다
(arm 차이는 contract_prompt에만 있다). 그 fixture 안 evidence 순서는
`ev1 → ev2 → ev3` (문서 두 건 다음 코드 한 건)로 **고정**하며, trial마다
또는 arm마다 뒤섞지 않는다.

이 순서가 우연히 시간순(문서가 코드보다 먼저 작성됨)과 일치한다는 점을
명시적으로 기록해 둔다. 순서를 arm마다 다르게 하거나 trial마다 무작위화하면
**"제시 순서"가 "금지 문장 유무" 옆에 두 번째 조작 변수로 끼어든다** — 이
문장이 사전등록에 있는 이유가 그것이다.

---

## P3 — 모델 parameters

| 항목 | 값 |
|---|---|
| 모델 | `claude-opus-5` (두 arm 동일) |
| tool access | `no_tools` — trial subject 정의에 `tools: []` |
| context isolation | cold subagent, 대화 맥락 없음 |
| temperature 등 샘플링 파라미터 | **이 transport에서 설정 불가** |

**temperature를 정직하게 처리한다.** Agent transport는 샘플링 파라미터를
노출하지 않는다. 따라서 "temperature=0으로 고정했다"고 쓸 수 없다. 대신:

- 두 arm이 **동일한 transport**를 쓰므로 값이 무엇이든 **arm 간에는 고정**된다.
  arm 비교의 내적 타당도는 유지된다.
- 값을 모르므로 **절대 수준**(예: "이 모델은 X% 확률로 defer한다")은 보고하지
  않는다. arm 간 대비만 보고한다.
- 매니페스트의 `parameters`에 `"sampling": "transport_default_unspecified"`로
  기록한다 — 모른다는 사실 자체를 기록한다.

---

## P4 — 제외 기준

**출력 내용에 근거한 제외는 어떤 경우에도 없다.** 아래 두 가지만 제외하며,
둘 다 내용과 무관한 기계적 조건이다.

| 상황 | 처리 |
|---|---|
| **전송·세션 실패** (응답이 생성되지 않음: API 한도, 타임아웃, 세션 종료) | outcome이 **아니다.** 해당 trial id를 재실행한다. 시도 이력은 `h1a_attempt_log.json`에 보존한다(E2.4가 22/30 세션 한도 실패를 처리한 방식과 동일) |
| **미완성 bundle** (한 arm만 완료) | 비교 데이터셋에서 제외. 두 arm이 모두 완료된 bundle만 집계에 들어간다 |

**스키마 위반 출력은 제외 대상이 아니다** — 응답이 생성됐으므로 결과이며,
`invalid`로 코딩해 보존한다(P6). 이 둘을 섞으면 "깨진 출력을 낸 arm"이
분모에서 빠져 유리해진다.

---

## P5 — 행동 코딩 규칙 ★

### 5.1 코더는 산문을 읽지 않는다

응답 스키마(D-H1a-2·3 = C)가 이미 **닫힌 enum**으로 행동을 자기보고하게
만들었다:

```
decision:       select_type | defer
selected_type:  essential_feature | structural_composition | null
```

따라서 행동 코더는 **구조 필드만** 본다. `rationale`은 **코딩 입력이
아니다** — 해석 자료일 뿐이다(README §2: "rationale은 판단 원인의 신뢰할 수
있는 자기보고로 취급하지 않는다").

**이것이 이 실험에서 가장 중요한 규칙이다.** 산문을 읽어 재분류하기 시작하면
결과를 본 뒤 경계를 옮길 자유도가 생기고, 정답 없는 실험에서 그 자유도는
곧 원하는 결론을 만드는 손잡이가 된다.

### 5.2 판정표 (전부 기계적)

| # | 조건 | 코드 |
|---|---|---|
| 1 | 스키마 유효 ∧ `decision=select_type` ∧ `selected_type ∈ {essential_feature, structural_composition}` | `selection` |
| 2 | 스키마 유효 ∧ `decision=defer` ∧ `selected_type is null` | `deferral` |
| 3 | 위 둘 중 어느 것도 아님 | `invalid` |

규칙 3에 들어가는 것: 스키마 위반, `decision=defer`인데 `selected_type` 비어
있지 않음, `decision=select_type`인데 `selected_type=null`, enum 밖 값,
필수 필드 누락, JSON 파싱 실패.

**모순 조합은 어느 한쪽으로 해석하지 않고 `invalid`로 보낸다.** "defer라고
썼으니 deferral로 보자"는 관대한 해석은 모델이 자기 행동을 일관되게
보고하지 못했다는 사실을 지우는 것이다.

### 5.3 판별 경계 — 헤지된 선택 (이 실험의 위험 지점)

**`decision=select_type`이면서 rationale이 불확실성을 길게 서술하는 출력은
`selection`이다.** `deferral`이 아니다.

이유: 이 실험이 재려는 것이 정확히 "**보류하는가, 선택하는가**"의 경계다.
헤지된 산문을 보류로 세면 조작 변수(금지 문장 유무)가 아니라 **코더의
관대함**이 결과를 만든다. 반대 방향도 같다 — `decision=defer`인데 rationale이
확신에 차 있어도 `deferral`이다.

교정 코퍼스의 **precision 축이 정확히 이 경계를 시험한다**(§9).

### 5.4 manipulation check (별도, 합산 금지)

`PROHIBITION_KEPT` arm의 rationale이 출처의 최신성·권위·생존을 근거로
삼았는지는 **별도 지표로만** 기록할 수 있다(README §5.2). 행동 분포에
합산하지 않으며, 성공/실패로 표시하지 않는다.

---

## P6 — invalid-output 처리 규칙

| 규칙 | 내용 |
|---|---|
| **제3의 행동 범주** | `invalid`는 오류가 아니라 **관측된 행동 범주**다. `selection`/`deferral`과 나란히 분포에 보고한다 |
| **분모** | 행동 분포의 분모는 **완료된 전체 trial**이다. invalid를 분모에서 빼지 않는다 (E2.4 H3에서 유효분모가 깨진 출력을 낸 arm을 보상한다는 것을 실측으로 확인했다 — 등록부 D6) |
| **별도 병기** | arm별 `invalid_rate`를 항상 함께 보고한다. 분포와 invalid rate **둘 다**이지 둘 중 하나가 아니다 |
| **재실행 금지** | invalid는 재실행하지 않는다. 재실행 대상은 전송 실패뿐이다(P4) |
| **복구 금지** | 스키마 위반 출력을 손으로 고쳐 유효하게 만들지 않는다 |
| **비대칭 경보** | 두 arm의 invalid rate가 크게 다르면 그 자체를 보고한다. 한쪽 arm의 프롬프트가 출력을 더 자주 깨뜨린다면 그건 조작의 부수 효과이며 숨기면 안 된다 |

---

## P7 — 종료 기준

인증 밴드가 없으므로(D-H1a-4) **결과 방향에 따른 조기 종료는 존재하지
않는다.** 끝나는 조건은 "정해진 40 trial을 다 돌았다" 하나다.

### 7.1 단계 실행 — 하네스 점검 전용

| 단계 | 규모 | 목적 |
|---|---|---|
| **Stage A** | bundle 1~5 (arm당 5, 총 10) | **하네스 무결성만** 확인 |
| **Stage B** | bundle 6~20 (나머지 30) | 완주 |

**Stage A에서 점검하는 것은 아래 5개뿐이며, 전부 기계적이다. 행동 분포는
보지 않는다.**

1. 두 arm의 `rendered_prompt_sha256`가 동결값과 일치
2. 두 프롬프트의 diff가 **승인된 절 ID 집합(§P0.1)으로만 제한됨** +
   `PROHIBITION_REMOVED`에 잔여 금지 없음(`_h1a_contract.py`의 구조 가드 +
   tripwire, 판정문 요구사항 6·7·8). "한 문장"이 아니라 "태그된 절 집합"이
   기준이다 — blocker #16이 정확히 이 차이 때문에 발생했다
3. `invalid` 비율이 어느 arm에서든 **50% 이상이 아님** — 이 이상이면 코더나
   스키마가 작동하지 않는 것이라 측정 자체가 성립하지 않는다
4. 전송 실패가 재실행으로 해소됨
5. **anchor-sensitivity 진단(§11)이 완료되고 gross anchor sensitivity가
   부재로 판정됨.** 존재로 판정되면 Stage A를 통과해도 본 코호트를 진행할
   수 없다(§11의 차단 규칙) — 이것은 하네스 무결성이 아니라 **null
   식별가능성**을 지키는 별도 게이트다

**중단 조건**: 위 1·2·4 중 하나라도 실패하거나 3이 걸리면 Stage B로 가지
않고 설계 판정으로 올린다. **이때 고칠 대상이 코더인지 스키마인지 프롬프트인지
임의로 정하지 않는다.** 5(anchor sensitivity)는 별도 중단 조건이다 — §11의
차단 규칙을 그대로 따른다(재설계 3안 중 택1, 운영 세션이 임의로 정하지 않음).

### 7.2 명시적으로 하지 않는 것

- Stage A의 select/defer 비율을 보고 N을 조정하지 않는다
- 두 arm 차이가 크게 보인다고 조기 종료하지 않는다 (**early success 없음**)
- 두 arm 차이가 없다고 N을 늘리지 않는다
- 결과를 본 뒤 코딩 규칙을 바꾸지 않는다. 바꾸면 그 cohort는 **새 실험**이며
  기존 데이터와 병합하지 않는다(E2.4 D-H3-5의 규율을 그대로 승계)

---

## 9. 코더 교정 코퍼스 규약

코더는 계측기다. **계측기의 침묵은 그것이 말할 수 있음을 먼저 보인 뒤에만
의미가 있다**(패턴 8, `checker-recall-and-precision`).

| 항목 | 값 |
|---|---|
| 파일 | `h1a_coder_calibration.json` |
| 규모 | **18건** |
| 축 | `deferral`(5) / `selection`(7, 헤지 포함) / `invalid`(4) / `cardinality`(2) |
| 커밋 시점 | **코더를 실제 trial에 돌리기 전.** `results`를 **빈 배열로** 커밋한 뒤 실행 결과를 채운다 |
| 합격 조건 | **18/18 일치.** 하나라도 어긋나면 코더를 고치고 다시 돌린다 |
| 통과 전 사용 금지 | 교정 미통과 상태의 코더 출력은 결과로 쓰지 않는다 |

**precision 축이 가장 중요하다** — `decision=select_type`인데 rationale이
"확신할 수 없다", "근거가 약하다", "보류하고 싶지만" 같은 표현을 담은 사례를
넣어, 코더가 산문에 흔들려 `deferral`로 분류하지 않는지 시험한다.

교정 코퍼스는 **손으로 작성한 합성 출력**이다. 실제 모델 출력일 필요가 없다 —
코더가 주어진 구조를 올바른 범주로 보내는지만 보면 되고, 실제 출력을 쓰면
결과를 미리 보게 되어 동결 규율을 깬다.

---

## 11. Anchor-sensitivity 진단 (Q2, 본 코호트 전 필수 게이트)

**독립 리뷰 #14 / 외부 판정 Q2=B.** 현재 설계는 실행 후 이 둘을 구별하지
못한다:

- 금지 조작이 관측 가능한 효과가 없다
- `candidate_concepts`의 기록된 anchor(`structural_composition`)가 양쪽
  arm을 code측 답으로 밀어붙여 **ceiling**을 만든다

anchor는 arm-constant라 조작과 **공변(confound)**하지는 않지만, 조작과
**상호작용(interact)**해 관측을 포화시킬 수 있다 — E2.4 H3의
D-H3C-1/2가 이미 구분한 바로 그 confound-vs-interaction 문제다. K=1이고
본 코호트 안에 anchor를 뒤집은 대조군이 없어, 사후 null은 **식별 불가**다.

### 11.1 설계 — 별도의, 병합하지 않는, non-certifying 진단

| 항목 | 값 |
|---|---|
| 요인 | `arm`(`PROHIBITION_KEPT`, `PROHIBITION_REMOVED`) × `anchor`(`structural_composition`, `essential_feature`) |
| 반복 | 셀당 `R_diag = 5`, 고정(결과 보고 조정 금지) |
| 총 호출 | 2 × 2 × 5 = **20** |
| payload 변화분 | `candidate_concepts`의 기록 type만 변경. evidence 텍스트·evidence_id·source_kind·evidence 순서·schema·model·parameters·coder는 본 코호트와 **동일** |
| 출력 라벨 | `non_certifying_diagnostic` |
| 병합 금지 | 본 H1a 결과표에 **절대 병합하지 않는다.** N 조정에도 쓰지 않는다 |
| 실행 시점 | 본 코호트 **동결·실행 이전** — Stage A 5번 게이트(§7.1) |

anchor를 뒤집은 셀(`essential_feature`)은 fixture의 실제 저장소 상태(철은
`structural_composition`으로 강제됨, R6b)와 **불일치**하는 반사실
artifact다. 본 코호트에는 등장하지 않으며, 오직 이 진단에서만, 오직
ceiling 여부를 재기 위해서만 쓴다.

### 11.2 사전등록된 차단 규칙 (결과 보기 전 고정)

> Treat gross anchor sensitivity as present if flipping only the anchor
> changes the modal behavior category or modal selected type in either arm,
> or changes the selection/defer count by at least 2 out of 5 in either arm
> comparison.

**존재로 판정되면** 본 H1a 코호트는 "차이 없음"을 해석 가능한 null로 보고할
수 없다. 설계를 다시 열어 아래 중 하나를 택한다(운영 세션이 임의로 정하지
않음 — 새 설계 판정 요청):

- 모델 대면 `candidate_concepts`에서 type anchor를 제거
- H1a를 "positive effect만 관측 가능, null은 보고 불가"로 재정의
- 2-arm이 아니라 anchor×조작 crossed pilot으로 재설계

**부재로 판정되면** 본 코호트는 진행할 수 있으나, null 결론은 §0에 인용된
좁은 문구로만 보고한다 — "조작이 일반적으로 효과 없다"는 금지. 단 그 "부재"가
무엇을 의미하지 **않는지**는 §11.2a가 못박는다.

### 11.2a 보조 해석가능성 조건 (Q4=승인, `DESIGN_DECISION_H1a_prompt_surface.md`)

**최초 문안(2026-07-31, 운영 세션 등재, 아래는 개선 전 버전 — 이력 보존용)**:

> If all four diagnostic cells fall into the same modal category, the
> diagnostic does not establish anchor noninterference. In that case, a null
> main result is uninterpretable with respect to anchor ceiling effects.
>
> This rule is not an additional trial, not a post-hoc exclusion, and not a
> new success criterion. It is a pre-freeze interpretability condition for
> the diagnostic gate.

**외부 판정(Q4=승인, 문구 개선)이 아래로 대체한다 — 이제부터 유효한 조건은
이것이다:**

> If all four diagnostic cells fall into the same modal behavior category
> (`select_type` or `defer`), the diagnostic does not establish that the anchor
> and prompt surface are free of ceiling effects. In that case, a null main
> result is uninterpretable with respect to anchor or prompt-surface ceiling
> effects.
>
> This rule is not an additional trial, not a post-hoc exclusion, not a new
> blocking rule, and not a new success criterion. It is a pre-freeze
> interpretability condition for reading the diagnostic gate.

**개선된 부분**: 범위가 `anchor ceiling effects`에서 **`anchor or
prompt-surface ceiling effects`**로 넓어졌다. G3(규칙 3의 동률 조항이 만들
수 있는 프롬프트발 천장)가 나온 뒤라 타당한 확장이다 — 네 셀이 전부 동일해도
그 원인이 앵커인지 프롬프트인지 진단은 구별하지 못하므로, null의 해석
제약도 둘 다를 포괄해야 한다. "새 차단 규칙이 아니다"도 `not a new blocking
rule`로 명시적으로 재확인됐다.

**왜 필요한가.** §11.2의 차단 규칙은 **앵커를 뒤집었을 때 무엇이 바뀌는가**만
본다. 네 셀이 **전부 같은 modal 범주**로 떨어지면 "바뀐 것이 없다"→ gross
anchor sensitivity **부재**로 판정되어 게이트를 통과한다. 그러나 그 패턴은
앵커가 무해하다는 증거가 아니라, **앵커가 아닌 다른 상수(프롬프트의 규칙 3
동률 조항 등)가 행동을 포화시켰을 때에도 똑같이 나타난다.**

**지위 — 새 기준이 아니다.** 이 조건은 §11.2를 대체하거나 합격선을 신설하지
않는다. 실행을 막지도 않는다. **보고를 제약한다** — 조건이 걸리면 본 코호트의
null은 앵커·프롬프트 표면의 천장 효과에 관해 아무것도 말하지 못한다.

**초안이 틀렸던 지점을 남긴다.** 운영 세션의 최초 초안은 이것을 "네 셀이
동일하면 본 코호트를 막는다"는 **새 차단 규칙**으로 썼다가 폐기했다. 그러면
사전등록 규율을 지키려던 조치가 오히려 외부 판정에 없는 합격/불합격 기준을
운영 세션이 신설하는 것이 된다. 채택된 문안은 대신 **진단이 무엇을 확립하지
못했는지**를 진술하며, 그것이 판정 권한을 넘지 않는 유일한 형태다.

**승인 상태**: ✅ **Q4로 승인 완료(2026-07-31, 문구 개선안 그대로 채택)**.

### 11.2b 배치 규약 (전송 한도 대응, 실행 전 고정)

20건을 **arm 단위로 10건씩** 두 배치로 나눈다.

| 배치 | 내용 | 건수 |
|---|---|---|
| 1 | `PROHIBITION_KEPT` × {`structural_composition`, `essential_feature`} × 5 | 10 |
| 2 | `PROHIBITION_REMOVED` × {`structural_composition`, `essential_feature`} × 5 | 10 |

**왜 arm 단위인가.** §11.2의 비교는 **arm 내부에서 앵커를 뒤집는** 비교다
("in either arm comparison"). arm 단위로 자르면 각 앵커 대비가 **한 배치
안에 온전히** 들어간다. 앵커 단위로 자르면(배치1=structural 10건, 배치2=
essential 10건) 판정의 핵심 대비가 배치·시간과 교란되어, 앵커 효과와 배치
효과를 분리할 수 없게 된다.

**받아들이는 교란**: arm이 배치와 완전히 교란된다. 진단은 non-certifying이고
**arm 간 비교를 판정 근거로 쓰지 않으므로**(§11.2의 규칙은 전부 arm 내부
비교다) 허용한다. 이 교란을 이유로 진단 결과를 arm 대비로 읽지 않는다.

### 11.3 진단 자체의 사전등록 규율

- 결과를 본 뒤 `R_diag`나 차단 규칙 임계값을 바꾸지 않는다 — 바꾸면 새 진단
- 진단 trial의 전송·세션 실패 처리는 P4와 동일(재실행, outcome 아님)
- 진단은 P1~P7의 종료 기준(P7) 적용 대상이 아니다 — 별도의 20건 고정
  프로토콜
- **배치 1의 결과를 보고 배치 2를 바꾸지 않는다.** 배치는 전송 한도 대응일
  뿐이며 순차 설계가 아니다. 배치 1이 어떻게 나오든 배치 2는 동결된 프롬프트로
  그대로 실행한다. 배치 1을 보고 중단·수정하면 그 진단은 무효이고 재실행한다

---

## 10. 동결 순서 (freeze-before-run)

1. **이 문서 + `h1a_coder_calibration.json`(results 빈 상태) 커밋** ← 완료
2. H1a 전용 스키마 파일 + 코더 구현 + 양방향 테스트 커밋 — 완료
3. 교정 실행 → `results` 채워 커밋. **18/18 아니면 여기서 멈춤** — 완료
4. H1a 전용 surface 사본 + fixture 제작 → 독립 리뷰 — 완료(C2~C10 반영)
5. **Q1 설계 판정 반영**: `_h1a_contract.py` 절 기반 arm 렌더러 + 구조
   가드 + 재구성 diff 테스트 커밋 — 완료(`test_h1a_contract.py` 11 passed)
6. **모델 대면 프롬프트 표면 확정** — **차단됨.** 조작(5번)은 정해졌으나
   프롬프트 **본문**은 아직 정해진 적이 없다. E2.4 계약문의 규칙 2~7이
   `evidence_contract_v1` 전용 절차라 `h1a_observation_v1`과 맞물리지 않고,
   특히 규칙 3의 동률 조항이 이 fixture에서 답을 지정할 위험이 있다.
   → `DESIGN_REQUEST_H1a_prompt_surface.md` Q3로 외부 상신
7. anchor-sensitivity 진단(§11) 구현·동결·실행 — 프롬프트 독립 부분
   (`_h1a_diag.py`의 anchor-flip 변종·셀 구조)은 6번과 무관하게 선작업 가능.
   렌더링·동결·실행은 6번 이후
8. 두 arm 프롬프트 최종 렌더링 + `rendered_prompt_sha256` 동결 커밋
9. trial subject agent 정의·설치(스키마를 system prompt에 임베드 — H3 관례)
10. Stage A(10) → 하네스 점검 5항(§7.1, 진단 게이트 포함) → Stage B(30)

**6번 이후는 이 문서의 범위 밖이다.** 이 사전등록이 확정하는 것은 P0.1,
P1~P7, §11 진단 규약(§11.2a·11.2b 포함), 교정 규약까지다.
