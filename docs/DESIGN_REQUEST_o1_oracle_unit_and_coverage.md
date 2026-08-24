# DESIGN REQUEST — O1 오라클의 단위·구성자 적용범위 (Q21)

- 상신: 2026-08-23, 운영 세션
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§4가 필요한 사실
  전부다
- 요청 성격: **O1 oracle 명세 자체의 개정 여부 판정.** D-E2E-v1-19가 정한
  실행 순서(O1 먼저)와 D-E2E-v1-20이 정한 커밋 규율은 그대로 유효하지만,
  실측 결과 **O1의 정본 오라클로 지정된 corpus에서 v0 구성자 부분집합에
  들어오는 fixture가 0건**이다. 이는 §12(estimand/oracle 변경은 외부 판정
  사안)에 해당하므로 운영 세션이 임의 결정할 수 없다
- 진행 차단 범위: fixture manifest 20건 동결, Stage 2 사전등록, 코호트 실행
  **전부 차단**. 차단되지 않은 것은 §6에 분리 기재

## 1. 지금까지 확정된 것 (귀하의 선행 판정, 인용)

**D-E2E-v1-19** (Stage 구조):
- Stage 1 = **E2E-v1-M**(계측 자격, 8 control, 능력 주장 없음) — **완료,
  8/8 PASS, 결정적 재실행 확인**
- Stage 2 = **E2E-v1-C**(동결된 N=20 O1 fixture, 수용 기준 PASS≥16 ∧ 최종
  ERROR=0 ∧ 예상 밖 UNSCORABLE=0). 16/20의 일방 95% 하한 0.5990이므로 80%는
  **공학 벤치마크이지 모집단 주장이 아니다**
- O1을 먼저 하는 이유: **O1의 binding family가 O2에 재사용**되므로 primitive
  누적 검증이 된다 (운영 세션의 O3 선호를 이 근거로 기각하셨다)
- §12: estimand / oracle / 임계값 / N / 주 지표 / oracle 역류 / Certified
  게이트 변경은 **외부 판정 사안**

**D-E2E-v1-20 (b+)** (라이선스-안전 커밋):
- corpus 원문·LF·expected IR을 저장소에 담지 않고 commitment 필드만 커밋
- **결정적 Oracle Adapter**(일반 syntax-directed, fixture-ID 조회 금지)를
  Refine/Verify와 분리, 자격 5항목 별도
- ORACLE-11: **commitment ≠ correctness** — 무결성 검사는 오역을 걸러내지
  못한다

**귀하의 oracle manifest**, O1 항목 (verbatim):
```yaml
  - oracle_id: "O1"
    name: "Quantifier Scope"
    semantic_boundary: [quantifier_scope, generalized_quantifier,
                        cardinal_quantifier, proportional_quantifier,
                        multi_quantifier_scope]
    source_authority:
      primary:
        title: "A Corpus of Encyclopedia Articles with Logical Forms"
        anthology_id: "2020.lrec-1.132"
        authority_type: "human_annotated_logical_form"
        formalism: "typed lambda calculus"
        role: "primary_oracle"
      supplementary:
        title: "QuantML / ISO 24617-12"
        authority_type: "normative_specification"
        role: "normative_semantic_reference"
```
같은 manifest의 `fixture_template`은 fixture 1건을 이렇게 규정한다:
```yaml
  source:
    language: "en"
    content: {mode: …, text: …, text_sha256: …}   # 문장 1건
  external_oracle:
    representation: {mode: …, representation_verbatim: …, …}  # 그 문장의 LF
```

## 2. 실측 (전부 이 세션에서 직접 측정, 방법 명시)

정본 corpus를 확보해(Q20/D-20 경로) **C6 tranche 전체를 전수 측정**했다.
측정 대상은 배포 파일 2종이다.

| 파일 | 레코드 | 단위 | 내용 |
|---|---|---|---|
| `wikisemC6.logic_.txt` (3.98 MiB) | **131** | `N LOGIC: (expr)` | typed lambda LF |
| `wikisemC6.cg_.txt` (0.95 MiB) | **865** | `N CG: (tree)` | categorial grammar 파스 |

### 2.1 단위 불일치 — LF는 문장이 아니라 **기사(다문장 담화)** 단위다

- LOGIC 레코드 **131건**, 기사 id 1~131, **id당 정확히 1건**.
- CG 레코드 **865건**, 같은 id를 **기사당 4~8건**(중위 7) 공유. 기사당 첫
  레코드는 제목(범주 `N-lS`), 나머지가 문장(`S-lS`).
- 즉 **문장 단위 원문은 있으나(CG 트리 말단에서 기계적으로 복원 가능),
  문장 단위 LF는 공개되지 않는다.** 한 기사의 6문장이 LF 하나로 형식화돼
  있다.
- LF 크기(공백 정규화 후 문자 수): 최소 **721**, 중위 **6,526**, 최대
  **32,786**. 개별 LF의 `Some` 등장 횟수 37~130.
- 담화임을 보여주는 직접 증거: 변수 이름이 문장 색인을 담는다
  (`x101`,`e104` = 1번 문장 / `x202`,`z206` = 2번 문장), 그리고 문장 간
  공지시 표지 `InAnaphorSet`이 LF를 가로질러 연결한다.
- 레코드 **10건은 LF가 빈 채 배포**된다(`16 LOGIC:` 다음 줄이 곧 17번
  헤더). 원자료의 주석 공백이며 도구 결함이 아니다. 비어있지 않은 것은
  **121건**.

**따라서 `fixture_template`이 규정한 "문장 1건 + 그 문장의 LF" 쌍을 이
corpus에서 만들 수 없다.** 기사 LF에서 문장별 부분식을 잘라내는 것은 어느
접속지가 어느 문장에 대응하는지 판단하는 작업이며, 그것은 **우리가 오라클을
제작하는 것**이라 ORACLE-11/12가 금지한 영역이다.

### 2.2 구성자 적용범위 — v0 부분집합 안에 드는 기사 LF가 **0건**

v0 IR이 표현하는 구성자는 양화(`Some`/`All`, restriction+scope 2-람다 GQ
형태), n항 접속(`^`), 범주 태그 술어 적용(`N-aD:department`,
`B-aN-b{A-aN}:be` 등 콜론 포함 토큰), 상수 `True`뿐이다. 121건 각각에서
head 위치 토큰을 전수 수집해 이 목록 밖의 head가 하나라도 있으면 범위 밖으로
셌다.

```
121건 중 v0 범위 내: 0건

범위 밖 head            등장 레코드 / 총 등장
  InAnaphorSet            121 / 1690      ← 모든 레코드에 있다
  Intension                72 /  239
  Equal                    52 /  162
  InAntecedentSet          29 /   84
  None                     20 /   31
  Gen                       5 /    7
  More                      1 /    2
```

**`InAnaphorSet`이 121건 전부에 나타난다.** 이 corpus의 LF는 문장 간
공지시를 형식화의 일부로 포함하므로, 담화 표상을 갖지 않는 IR로는 어떤 기사
LF도 온전히 번역되지 않는다.

### 2.3 이 측정에 앞서 정정해야 할 운영 세션의 이전 보고

**이전 보고("C6에서 22건이 v0 부분집합으로 완전 파싱, 7 tranche 외삽 ~150건
풀 확보")는 틀렸다.** 원인은 우리 adapter의 결함 3건이었고, 그 결함들은
D-E2E-v1-20 ORACLE-11이 지목한 바로 그 실패 유형이다:

1. **실패차단 우회** — 미지원 연산자 검사가 최상위 경로에만 있어, 람다 본문
   경로로 들어온 `Equal`/`Intension`/`None`이 예외 없이 **이름만 남긴 평범한
   술어로 조용히 번역**됐다.
2. **양화 결박 유실** — corpus의 GQ는 `Some (\u R[u]) (\w S[w])`로 두 람다가
   **서로 다른 이름**을 결박한다(같은 인자에 적용되므로 결박 변수는 하나).
   adapter가 이름이 다른 쪽을 renaming 없이 버려, **닫힌 문장의 번역이
   자유변수를 가진 열린 식**이 됐다 — 파싱 성공했다던 22건 **전부**가
   자유변수 12~51개를 갖고 있었다.
3. **산출 미검증** — adapter가 자기 출력을 IR 스키마로 검증하지 않아, 콜론
   태그 술어가 람다를 인자로 받는 corpus 형태가 항 자리에 수식을 넣은
   **스키마 무효 IR**을 통과시켰다.

세 결함 모두 수정하고 계약 테스트로 결박했다(수정 후 fail-closed는 모든
경로에 적용, 술어는 콜론 태그 형태만 허용하는 **whitelist**로 전환 — 아직
보지 못한 구성자도 닫힌다). **§2.2의 0건은 수정 후 규칙을 corpus에 적용한
결과이며, adapter와 독립적인 별도 스캐너로 교차 측정해 같은 값을 얻었다.**

fixture는 아직 한 건도 커밋되지 않았으므로 **오염된 commitment는 없다.**
D-20이 요구한 자격 분리(무결성 축과 정확성 축을 다른 게이트가 지킨다)가
실제로 작동한 사례로 기록한다.

## 3. 판정 질문

### Q21.1 — fixture 단위

`fixture_template`은 "문장 1건 + 그 문장의 LF"를 규정하는데, O1의 정본
오라클은 기사 단위 LF만 공개한다. 어느 쪽을 개정하는가?

- **(a) template을 담화 단위로 개정** — fixture 1건 = 기사 1건(모델 대면
  입력은 그 기사의 문장 전체, 오라클은 기사 LF). 단 §2.1의 크기(중위 6,526자,
  양화 37~130개)를 고려하면 DirectMatch가 사실상 0이 되어 PASS≥16 임계값이
  의미를 잃는다 — 그렇다면 임계값·주 지표도 함께 개정 대상인가?
- **(b) 문장 단위를 유지하고 O1의 instance 출처를 교체** — §Q21.2로 연결
- **(c) 기사 LF에서 문장별 부분식을 규칙으로 추출** — 운영 세션은 이것이
  오라클 제작(ORACLE-11/12 위반)이라고 판단하나, 귀하가 "선언된 결정적
  추출 규칙은 adapter의 일부"로 판정한다면 가능해진다. 다만 문장 간
  `InAnaphorSet` 결박이 끊기므로 자격 항목 "결박 보존"과 충돌한다
- (d) 그 외

### Q21.2 — 0건 적용범위: 잘못된 부분집합인가, 잘못된 오라클인가

`InAnaphorSet` 등을 범위 밖으로 선언하면 풀이 비고, 범위 안으로 들이면
estimand가 "quantifier scope"에서 "담화 표상 포함 의미론"으로 넓어진다.

- **(a) v0 구성자 부분집합을 확장한다** — 어느 구성자까지인가(담화 공지시
  `InAnaphorSet`/`InAntecedentSet`, 내포 `Intension`, 동일성 `Equal`)? 이
  확장은 O1의 `semantic_boundary`(quantifier_scope 계열 5항목)를 넘어서므로
  **O1이 측정하는 대상 자체가 바뀌는가**?
- **(b) O1의 instance 출처를 문장 단위 자원으로 교체한다** — 귀하의 asset
  집합에 이미 **G1 "Parallel Meaning Bank Gold"**(`human_verified_gold_corpus`)가
  있고 문장 단위 형식 표상을 제공한다. 그러나 같은 manifest가 G1에
  **"Do not use PMB Gold as the only initial acceptance gate"**를 명시하므로,
  G1의 corpus를 O1의 instance 출처로 쓰면 regression 자산과 수용 게이트가
  겹친다. 이 assurance 분리를 유지하면서 재사용하는 방법이 있는가, 아니면
  제3의 자원을 지정하는가? (O1의 supplementary인 QuantML/ISO 24617-12는
  규범 명세이지 instance 집합이 아니다)
- **(c) O1을 보류하고 실행 순서를 바꾼다** — 단 D-19가 O1 우선을 정한 근거
  ("binding family가 O2에 재사용")가 무효화되므로, 그 근거를 어떻게
  대체하는가?
- (d) 그 외

### Q21.3 — whitelist 실패차단은 판정 사안인가

수정된 adapter는 미지원 연산자 **목록(blacklist)** 대신, 허용 구성자
**목록(whitelist)** 밖의 모든 head를 닫는다(아직 보지 못한 구성자 포함).
운영 세션은 이것을 구현 선택으로 보나, 이 규칙이 **UNSCORABLE 회계에 영향**을
준다(범위 밖 입력이 예상된 UNSCORABLE인지 예상 밖인지). D-19의 "예상 밖
UNSCORABLE=0" 수용 기준과 맞물리므로 판정을 청한다.

### Q21.4 — Stage 1 자격의 유효성

Stage 1(E2E-v1-M) 8 control은 **손으로 쓴 IR**로 계측기(평가기)의 경계
행동만 시험했고 adapter를 경유하지 않았다. adapter 수정이 Stage 1 결과를
무효화하는가, 아니면 Stage 1은 그대로 유효하고 **adapter 자격 5항목이
별도로 그 역할을 하는가**? (운영 세션 판단: 후자. adapter는 Stage 1 계측
경로에 없었다. 다만 자격 항목에 §2.3의 결함이 낳은 신규 2항목 — **산출
스키마 검증**과 **닫힘 보존** — 을 추가했으므로, 자격 항목 수가 5에서 7로
늘어난 것이 귀하의 승인 사안인지 확인을 청한다)

## 4. 운영 세션의 권고 (구속력 없음, 판정 근거로만)

**Q21.1은 (b), Q21.2는 (b)를 권고한다.** 근거:

- (a) 담화 단위는 단위 문제를 해결하지만 §2.2의 적용범위 문제를 전혀
  해결하지 못한다 — 기사 LF 121건 전부가 범위 밖이므로, 단위를 바꿔도
  fixture는 0건이다. **구속 제약은 단위가 아니라 구성자 적용범위다.**
- (c) 부분식 추출은 우리가 오라클 저자가 되는 것이고, D-20이 구성해 보인
  "오역하는 translator도 유효한 commitment를 발급한다"는 반례가 정확히 이
  경로에서 실현된다.
- (b)의 대가는 명확하다: PMB는 DRS 계열 형식이라 **새 adapter와 새 자격
  집합**이 필요하고, G1과의 assurance 분리를 어떻게 유지할지 귀하의 판정이
  필요하다. 그래도 이것이 estimand를 "quantifier scope"로 유지하는 유일한
  경로로 보인다.

## 5. 이 요청에 필요한 판정의 최소 형태

전면 재설계를 청하는 것이 아니다. 다음만 정해주시면 진행 가능하다:

1. Q21.1·Q21.2의 선택지 (또는 귀하의 대안)
2. 선택이 estimand·임계값·주 지표를 바꾸는지 여부와, 바꾼다면 새 값
3. Q21.3(whitelist)·Q21.4(자격 항목 5→7) 승인 여부

## 6. 판정 없이 진행 가능한 것 (차단되지 않음 — 병행 중)

- adapter 3결함 수정과 계약 테스트 (완료·검증)
- adapter 자격 7항목의 **형식 실행 기록** — 오라클 자원이 무엇으로 결정되든
  "구문 파싱 / α-rename 불변 / 양화 재배열 음성 / 결박 보존 / 결정적 재실행
  / 산출 스키마 검증 / 닫힘 보존"은 그대로 필요하다
- commitment manifest의 **기제**(hash-pin 필드·로컬 캐시 resolver·해시 불일치
  시 execution=UNAVAILABLE) — 내용 20건은 차단이나 기제는 자원 무관
- 문장 원문 복원기(CG 트리 말단 추출) — 어느 자원을 쓰든 `text_sha256`이
  필요하다

## 7. 검증 재현 방법 (귀하가 요구할 경우)

§2의 모든 수치는 배포 파일 2개에 대한 전수 스캔이다. 재현에 필요한 것은
파일 2개와 20줄 이하의 스캐너이며, 사용한 판정 규칙은 §2.2에 전부 적었다
(head 위치 토큰 수집 → 허용 목록 대조). 운영 세션은 이 측정을 **adapter
경유**와 **adapter 독립 스캐너** 두 경로로 각각 수행해 같은 값(0건)을 얻었다.

측정 대상 바이트의 동일성 고정(D-20이 허용한 commitment 형식 — 해시는
콘텐츠가 아니다):

| 파일 | bytes | sha256 |
|---|---|---|
| `wikisemC6.logic_.txt` | 4,175,942 | `611a2754039f68b3243507b4bbad91d77cde28f74c5036754a69e4a9f8b13bc8` |
| `wikisemC6.cg_.txt` | 992,295 | `c31ac84a4620870f17f98f9a54f4f1d0db35446893edcc49acd82c0cc1f67d84` |

두 파일 모두 2026-08-22~23에 배포처에서 직접 받은 것이고, 저장소에는 담지
않았다(로컬 캐시 전용 — D-20 §Q20.4).

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
