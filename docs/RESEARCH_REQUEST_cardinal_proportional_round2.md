# RESEARCH REQUEST (2차) — 비례 양화 source + 1차 회신의 BLOCKED 해소

- 수신자: **조사용 agent** (다른 workspace, zero context 전제 — 이 문서가
  맥락 전부. 설계용 agent 아님)
- 발신: ConceptGate 운영 세션, 2026-08-23
- 관계: **1차 회신("기수 양화 gold source 조사 보고서 — R1–R6")을 수령·검증
  완료했다.** 이 2차 요청은 그 회신이 확정한 사실을 **다시 조사하지 말고**,
  아래 §1의 공백 3구역만 겨냥한다.
- 후속: 회신을 운영 세션이 검증 후, 적격성은 별도 기계 실측.
  **조사에게 적격성 판정을 청하지 않는다** — 사실 확인만.

## 0. 1차 회신에서 **확정된 것** (재조사 금지)

아래는 이미 답이 나왔다. 다시 확인하지 마라.

| 사실 | 상태 |
|---|---|
| QuantML/Quantification Bank가 기수를 `numRel + num` + `scoping` relation으로 표상하고 ISO 24617-12:2025가 정본 | 확정 |
| Overnight LF가 `=`/`<=`/`>=` + `(number N unit)`로 기수를 인코딩, 2차 배포처 표기 `CC BY-SA 4.0` | 확정 |
| GeoQuery 공식 라이선스 `GPL 2.0`, original 250건 LF는 수작업 번역, 880 sentence-query pairs | 확정 |
| GeoQuery의 `at least one`이 수치 연산자가 아니라 **존재 구조로 환원**되고 `name the 50 capitals`의 `50`은 LF에서 소실 | 확정 |
| ATIS 원 정본은 reference SQL, 라이선스 `LDC User Agreement for Non-Members`, 후대 Lambda는 파생이며 `at least N`을 `>N`으로 인코딩 | 확정 |
| AMRNews/AMR-BP는 `CC BY-NC-SA 4.0`, 수작업, `:quant 2` 실물 존재, AMR 정본이 "does not represent quantifier scope" 명시 | 확정 |
| FraCaS는 gold가 **inference label**(Yes/No/Don't know)이고 문장별 형식 표상이 없다 | 확정 — 후보 탈락 |

또한 운영 세션이 자체 실측으로 판정한 것(조사 범위 밖이었던 부분):

- **AMRNews는 언어 불일치로 탈락** — 우리 subject는 영어 문장만 받는다
  (동결 프롬프트가 "the following **English** sentence"를 지시).
- **보고된 6개 표상 전부가 우리 동결 subject 방언으로 표현 불가**하다.
  방언은 `forall / exists / and / pred / not / implies`, 항은 변수·개체뿐이고
  **수치 상수·비교자·집합 크기 연산이 없다**. GeoQuery만 방언 내 표현이
  가능한데 그 경우 수치가 사라져 기수 측정이 성립하지 않는다.

## 1. 이번에 조사할 공백 3구역

### 구역 A — **비례 양화(proportional quantifier) source** ★ 최우선

1차 요청서는 기수만 물었고, 그 후 우리 쪽 판별 술어를 정정해 재census한
결과 **비례 재료도 0건**임이 확정됐다. 1차 회신에는 비례 항목이 없다.

**비례 양화의 범위 (이 조사의 정의)**: 집합의 비율을 한정하는 양화 —
`most of the students`, `Most cats sleep`, `a majority of X`,
`more than half of X`, `few of the X`(비율 해석), `80% of X`.
**제외**: 최상급(`the most beautiful`, `her most famous`), 상한 기수
(`at most N`), 부사 `mostly`, 단순 다수 형용사(`many`, `several`만 있는 것).

우리 쪽 실패 이력(같은 오류를 반복하지 않기 위해 공유): bare `most` 정규식이
"The **most** beautiful flowers…"(최상급), "He paid **at most** ten thousand
dollars"(상한 기수), "Copland's **most** famous piece"(소유격 최상급)를
비례로 잘못 잡았다. **네 번의 동결이 이 오분류를 통과했다.**

### 구역 B — 1차의 BLOCKED 3건 해소 시도

1차가 부재 판정하지 않고 BLOCKED로 남긴 것들이다. 접근 경로를 바꿔 재시도
하고, 여전히 막히면 **무엇을 어떻게 시도했는지와 함께 BLOCKED 유지**하라.

1. **Quantification Bank 데이터 자체의 라이선스** — 예제 index 페이지 밖의
   경로(repository README, 상위 sigsem 사이트 정책, ISA workshop 자료
   배포 조건, Bunt 개인 페이지, 논문 supplementary)를 시도.
2. **Quantification Bank item-level provenance** — 각 예제의 작성·검수
   주체를 밝히는 문구(annotator 명, ISA-17 참가자 귀속, "examples by …")
3. **Overnight 원 배포처의 dataset-specific 라이선스** — Stanford/SEMPRE
   저장소의 LICENSE, 데이터 릴리스 페이지, 논문 footnote, `nlp.stanford.edu`
   배포 경로. (2차 배포처 표기는 이미 확정이므로 재확인 불요.)

### 구역 C — 기수 재료의 **방언 정합 관점** 추가 사실

우리 방언에 수치가 없다는 제약 때문에, 다음 사실이 채택 판정의 핵심이 됐다.
**판정이 아니라 사실만** 보고하라.

1. 각 기수 후보(QuantML·Overnight·ATIS)의 표상에서 **기수를 제거하고도
   양화 scope 구조가 독립적으로 남는가?** 즉 `at least three papers`의
   `≥3`을 지우면 `∃`(또는 그에 상응하는 양화 구조)가 표상에 남는가, 아니면
   기수가 곧 양화자여서 지우면 구조가 무너지는가. 정본 문법 문서의 근거로
   답하라(실물 표상 조각 포함).
2. 위 세 후보 중 **`few`·`most` 같은 비례 표현도 함께 다루는 것**이 있는가.
   있으면 그 인코딩 실물 1~2건(구역 A의 후보가 될 수 있다).
3. **1차에서 언급되지 않은 후보**가 비례·기수 양쪽을 문장 단위 형식
   표상으로 공급하는 경우가 있는가. 우리가 아는 계열: GQ/generalized
   quantifier 데이터셋류, Groningen 계열(단 PMB 파생이면 탈락),
   MRS/ERG(DELPH-IN) 계열, Boxer/DRS 계열, TREC/QALD류 질의 gold,
   Abstract Meaning Representation 영어판(AMR 3.0 — **영어**임에 유의),
   Universal Dependencies의 의미 확장 계열. 각각 **비례·기수가 표상에
   남는가**를 R4 관점에서.

## 2. 독립성 조건 (변경 없음, 하나라도 어기면 후보가 아니다)

```yaml
second_source:
  different_corpus_authority: true      # PMB·FOLIO와 다른 기관/저작 주체
  independently_authored_gold: true     # 사람이 저작·검수한 gold
  not_derived_from_PMB: true            # PMB 재수출·변환판 금지
  not_project_generated: true           # 우리가 생성한 쌍 금지
  separate_source_locator: true
  separate_adapter_profile_if_formalism_differs: true
english_sentences: true                 # 2차에서 명시 — 우리 subject는 영어만 받는다
```

자동 생성 gold라도 **제3자가 저작·공개한 완성 artifact**면 후보다(우리가
생성하면 탈락). 1차의 Overnight이 이 경우에 해당한다.

## 3. 유지되는 3원칙 (1차에서 잘 작동했다)

1. **라이선스를 정책으로 추정 금지** — 배포처의 명시 문구만 verbatim.
   문서(논문·표준)의 저작권을 **데이터**에 전이하지 마라. 1차가 이 구분을
   정확히 했다.
2. **원문 철자·URL 문자 그대로 시도** — 교정은 그 다음. 1차가 GeoQuery
   404를 "데이터 부재"로 바꾸지 않고 `publication-link 실패`로 분리한 것이
   정확한 처리였다.
3. **BLOCKED와 없음을 구분** — 1차가 5건을 BLOCKED로 유지한 것이 옳다.

## 4. 보고 형식

구역별로: **사실 / 근거(URL·파일 경로·verbatim 인용) / 확신도 / BLOCKED
여부**. 시도했으나 실패한 경로 포함. 1차에서 확정된 사실은 **다시 적지
말고** 필요하면 참조만 하라.

우리가 자체 실측할 것(조사 범위 아님): 문장 단위 1:1 / 해당 양화 실재 /
**동결 방언 표현 가능성** / 표면 필터(대명사·고유명 배제) / 투영 신호 보존 /
측정 가능성. 적격 하한은 **기수 ≥3건, 비례 ≥1건**이다.
