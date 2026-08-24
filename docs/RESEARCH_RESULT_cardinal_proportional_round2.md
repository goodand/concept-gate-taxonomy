# RESEARCH RESULT — 2차 조사 회신 (비례 source + BLOCKED 해소 + 방언 정합)

- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 수신: 2026-08-24, 사용자 경유 (조사용 agent, 다른 workspace)
- 원 요청: `RESEARCH_REQUEST_cardinal_proportional_round2.md`
  (sha256 `3319126def245b59fc2a…`)
- 성격: 사실 확인이며 적격성 판정이 아니다(조사가 명시).
- 요약: 비례 표상을 가진 후보 3계열 확인(QuantML `relativeSize`,
  Wikisem typed-lambda, ERG/MRS `_most_q`) + 1차 BLOCKED 3건은 경로 변경
  재시도 후에도 **BLOCKED 유지**(부재 판정 안 함) + C-1 답: QuantML·
  Overnight·ATIS 모두 **기수를 지우면 독립 양화 구조가 남지 않는다**,
  ERG/MRS만 `card_rel`과 quantifier EP가 분리.
- **경보**: 조사가 "1차에 없던 새 source family"로 제시한 **Wikisem은 우리가
  D-E2E-v1-21에서 이미 부적격 판정한 source**다 — 아래 수신 검증 V1 참조.

---

## 회신 전문 (verbatim — 파일명만 바꿨고 내용은 무수정)

원 파일명: `2차 조사 보고서 — 비례 양화 source + 1차 BLOCKED 해소 + 방언 정합 관점 사실 확인.md`
(공백·특수문자 파일명은 이 저장소의 `RESEARCH_RESULT_*` 규약과 어긋나 개명.
내용은 1바이트도 바꾸지 않았고 아래 sha256이 그것을 보증한다.)
- **회신 블록 자신의 `VERBATIM_SHA256`**: `ee9f325e68e5bcc4d17d957745e53db39c88e54b04f66a774e352abeae6f4bd3`
  (BEGIN 다음 개행 ~ END 직전, 개행 제외. 수신 시점에 검증한 값과 동일하다.)
- 구분자 정정 기록: `<!-- VERBATIM-END -->`가 내용 줄 끝에 붙어 있어 기계 추출이
  불가했다 — 2026-08-24에 마커만 자기 줄로 옮겼다. **내용 문자는 불변**이고,
  위 해시가 그것을 증명한다(정정 전 블록 바이트의 해시와 동일한 값이다).
  헤더 6행의 `3319126def…`는 **요청서**의 해시이고 이 회신의 것이 아니다.

<!-- VERBATIM-BEGIN -->
# 2차 조사 보고서 — 비례 양화 source + 1차 BLOCKED 해소 + 방언 정합 관점 사실 확인

## 0. 조사 범위

본 보고서는 2차 요청서가 지정한 **세 공백만** 조사했다.

- **A:** 비례 양화(proportional quantifier)를 문장과 형식 의미 표상 양쪽에서 확인할 수 있는 source
- **B:** 1차 회신에서 `BLOCKED`로 남은 Quantification Bank 2건 + Overnight 1건의 재시도
- **C:** QuantML·Overnight·ATIS에서 기수 수치 부분을 제거했을 때 독립적인 양화/scope 구조가 남는지, 그리고 1차에 없던 양화 source 계열

1차에서 이미 확정된 GeoQuery, FraCaS, AMRNews 등의 사실은 재조사하지 않았다. 또한 아래 내용은 **채택/적격성 판정이 아니라 source와 formalism에 관한 사실 확인**이다.

---

# A. 비례 양화 source

## A-1. QuantML / Quantification Bank

### 사실

Quantification Bank는 비례 양화를 단순 문자열 `most`가 아니라 **별도 의미 객체 `relativeSize`**로 표현하며, 그 객체와 참여 entity 및 scope 관계를 분리해서 기록한다.

Bank의 공식 예제 목록 자체에 **“Proportional quantifiers”** 범주가 있고 다음 문장이 들어 있다.

> `The girls have eaten most of the chocolate.`

실제 annotation에는 다음과 같은 구조가 있다.

```xml
<entity ... involvement="#q2"/>
<relativeSize xml:id="q2" pred="most"/>
<scoping arg1="#x1" arg2="#x4" scopeRel="dual"/>
```

즉 `most`가 최상급이나 `at most N`이 아니라 **집합/참여량의 상대적 크기**를 나타내는 의미 객체로 직접 표상되고, `scoping`은 별도 관계로 존재한다.

### R4 관점

QuantML 정본에서는 involvement specification이 크게 numerical specification과 relative-size specification으로 나뉘며, `relativeSize`가 후자의 표현이다. concrete syntax에서도 `entity/@involvement`, `<relativeSize>`, `<cardinality>`, `<scoping>`은 서로 구별된 구조다.

따라서 이 사례의 `most`는 사용자 정의의 **비례 양화**에 직접 해당한다. 특히 요청서에서 경고한 다음 세 종류와 구조적으로 구별된다.

- `the most beautiful` 같은 최상급
- `at most three` 같은 상한 기수
- `mostly` 같은 부사

### 확신도

**매우 높음.**

### BLOCKED

비례 양화의 **존재와 formal encoding은 미차단**.  
데이터 라이선스와 Bank item-level provenance는 B구역과 같이 계속 `BLOCKED`.

---

## A-2. Rasmussen & Schuler — Simple English Wikipedia → Typed Lambda Calculus corpus

### 사실

1차에 없던 별도 source family다.

Rasmussen & Schuler의 corpus는 약 **2,000개의 Simple English Wikipedia 문장​**에 대해 typed lambda calculus translation을 제공하며, 논문 자체가 이 자원을 quantifier와 quantifier scope를 다루는 corpus로 설명한다.

형식 의미론에는 비례 양화를 위한 generalized quantifier가 명시적으로 정의되어 있다. 예를 들어 논문에 실제로 다음 문장과 의미 표상이 제시된다.

```text
Most libraries are public.

most
  (λx. library(x))
  (λx. public(x))
```

즉 `most`가 두 집합―restrictor와 nuclear scope―사이의 generalized-quantifier relation으로 직접 들어간다. 같은 의미 inventory에는 `half`도 별도 quantifier로 포함되어 있다.

더 나아가 백분율은 별도 `ratio=` 연산자로 정의된다. 논문의 실제 예는:

```text
Water covers 71% of the Earth.
```

이고 형식 표상에는 `ratio= .71 ...`이 들어간다. 정확 기수에는 별도의 `count=`가 사용되며, 논문에는 `5,500 men`을 `count= 5500 ...`으로 나타낸 실물도 있다.

따라서 이 formalism은 적어도 문법 차원에서 다음을 모두 서로 구별한다.

| 자연어 종류 | formal operator |
|---|---|
| `most R S` | `most R S` |
| `half R S` | `half R S` |
| `71% of ...` | `ratio= .71 ...` |
| 정확수 `5,500 ...` | `count= 5500 ...` |

### 현재 배포본의 실제 proportional item

현재 Ohio State Schuler Lab 배포 페이지는 논문에 적힌 특이한 철자 **`/dwnload`**를 그대로 사용해 실제 배포 중이며, `wikisemC1.logic__0.txt` 등을 목록으로 제공한다. 페이지 설명은 semantic file에 quantifier-scope annotation tag가 들어 있음을 명시한다.

해당 현재 C1 배포 파일을 직접 확인한 결과, record 85에는 다음 표면 문장이 있다.

```text
Most of the Earth's surface is covered with water.
```

대응 logic record에는 `most` operator가 실제로 존재한다. 즉 논문 속 toy example만이 아니라 **현재 배포 corpus 자체에서도 proportional `most`가 확인됐다.**

대용량 logic file은 웹 문서 renderer에서 직접 표시하지 못했지만, 배포 페이지가 가리키는 원문 locator 자체는 유효했다. 따라서 이것은 “접근 불가”나 “파일 없음”으로 처리하지 않는다. 배포 파일 이름과 현재 locator는 원 배포 페이지에서 확인된다.

### 저작/검수 방식

이 corpus는 단순 자동 parser output만 저장한 것이 아니다.

논문이 설명하는 절차는 다음과 같다.

1. Simple English Wikipedia 원문을 자동 syntactic analysis.
2. 오류나 attachment를 **사람이 수정**.
3. semantic association을 사람이 지정.
4. annotator가 anaphor antecedent와 **quantifier scope parent를 직접 표시**.
5. well-formed lambda expression이 되도록 validation 후 다시 사람 수정.
6. 첫 1,000문장 이후 일부 문서는 **second independent markup**도 수행.

다만 top-scope existential 사이처럼 의미적으로 동등하다고 취급한 일부 순서는 후처리에서 자동으로 정해진다. 논문은 evaluation에서는 hand annotation을 기준으로 사용했다고 설명한다.

따라서 사실관계는 **“자동 parse + human correction + human scope annotation + 일부 자동 tie-breaking”​**이다.

### 문장 단위

논문은 약 2,000 **sentences**의 typed-lambda translation이라고 기술하고, 배포 logic 파일 역시 sentence별 record를 제공한다. 다만 원자료는 서로 이어진 Wikipedia article의 첫 3–6문장을 사용하므로, anaphora 등 annotation 과정에는 문서 문맥이 관여할 수 있다.

따라서:

- formal output locator: sentence record
- annotation context: 일부 article-level 연결성 존재

로 구분하는 것이 정확하다.

### 라이선스

논문은 Simple English Wikipedia를 택한 이유 중 하나로 **Creative Commons license가 distribution을 용이하게 한다**고 설명한다.

그러나 이것은 **Wikipedia source text의 권리 설명**이다.

현재 Schuler Lab download page에서 별도의 annotation-corpus-specific `LICENSE`, `license`, `copyright` 조건은 이번 조사에서 찾지 못했다. 따라서 논문이나 Wikipedia의 CC 조건을 annotation corpus 전체에 자동 전이하지 않는다.

### 확신도

- 비례·기수 formalism: **매우 높음**
- corpus 실제 `most` item: **높음**
- 사람 scope annotation: **매우 높음**
- 데이터 자체 라이선스: **미확인**

### BLOCKED

**annotation corpus의 dataset-specific license = BLOCKED.**

---

## A-3. DELPH-IN ERG / MRS + LinGO Redwoods

이 경우는 **formalism과 gold treebank를 분리해서** 보는 것이 필요하다.

### Redwoods corpus 사실

Redwoods는 English Resource Grammar(ERG)로 분석한 corpus에 대해 annotator가 후보 분석들 중 **의도한 reading을 선택한 hand-annotated treebank**다. CLARINO/Språkbanken metadata는 이를 “hand-annotated corpora analysed with LinGO ERG”라고 설명하고, 각 utterance마다 candidate analyses와 annotator의 preferred reading을 기록한다고 설명한다. 해당 배포 metadata의 권리 표기는 **GNU General Public License (GPL)​**이다.

Redwoods Ninth Growth에 관한 자료는 약 **85,400 utterances**, 약 1.3M tokens의 gold-standard analyses를 보고하며, 선택된 ERG 분석에서 full logical-form meaning representation을 얻을 수 있다고 설명한다.

다만 Redwoods에는 여러 출처의 component corpora가 포함되므로, metadata의 GPL 문구와 각 underlying text component의 권리는 운영 단계에서 별도로 구분할 필요가 있다. 여기서는 component별 권리까지 확정하지 않았다.

### R4 — 기수의 MRS 구조

ERG/MRS 형식 자료의 실물 예:

```text
Three dogs bark on Tuesday in June
```

의 MRS에는 개략적으로 다음이 동시에 존재한다.

```text
bare_div_q_rel(... x7 ...)
RSTR ...
BODY ...

card_rel(... x7 ...)
CARG 3

_dog_n(... x7 ...)
```

즉:

- 개체 variable `x7`에 대한 **quantifier EP**
- 숫자 `3`을 담은 **별도 `card_rel`**
- noun predicate

가 분리되어 있다.

이는 C-1과 관련해 특히 중요한 구조적 사실이다. `card_rel(... CARG 3)`과 `bare_div_q_rel(... RSTR/BODY ...)`가 별개이므로 **숫자/cardinality EP 자체와 restrictor/body quantifier EP가 동일한 노드는 아니다.**

### R4 — proportional `most`

ERG/MRS 자료에는 다음과 같은 직접적 generalized-quantifier EP도 있다.

```text
Most house cats are easy for dogs to chase.
```

MRS에서 `most`는 대략:

```text
_most_q(x5, h6, h7)
```

형태로 나타나며 restrictor/body handle을 가진 quantifier다. 따라서 여기의 `most` 역시 최상급 `most`가 아니라 **명사구 quantifier**다.

### 중요한 제한

이번 조사에서 위 cardinal/proportional 실물은 **ERG/MRS formalism example로 확인**했다.

반면 같은 문장이나 동형의 `most` item이 현재 재배포 가능한 특정 Redwoods profile 안에 실제 gold record로 들어 있음을 직접 locator까지 확인하지는 못했다.

따라서 다음 둘은 구분한다.

- **ERG/MRS가 cardinal과 proportional을 formal MR에서 표현한다:** 확인
- **Redwoods release 안에 실제 proportional gold item이 적어도 1건 존재한다:** 이번 조사에서는 item-level locator 미확보

### 확신도

- MRS 표현 능력/구조: **높음**
- Redwoods hand-selected gold 분석: **높음**
- Redwoods proportional 실물 item: **미확인**

### BLOCKED

**Redwoods의 proportional corpus item locator = BLOCKED.**

“없음”으로 판정하지 않는다.

---

## A-4. GQ 계열에서 확인한 near-miss

### QuRe

QuRe는 Wikipedia 문맥에서 generalized quantifier를 대상으로 **crowdsourced human annotation**을 하고 `few`, `most` 및 percentage-based interpretation을 다룬다. 따라서 비례 양화 자체를 사람이 annotation한 자원이라는 사실은 확인된다.

그러나 이번 조사에서 확인된 artifact는 **quantifier/percentage/scope annotation**이며, 문장 하나에 대해 FOL·lambda calculus·MRS·DRS 같은 완성된 full formal meaning representation을 제공한다는 근거는 찾지 못했다.

**R4 상태:** full sentence formal MR 미확인.  
**BLOCKED:** formal-MR 조건에 대해서는 예.

### GQG

GQG는 다양한 generalized quantifier가 포함된 **18,360 prompts​**를 제공하는 평가 자원으로 확인되지만, 각 자연어 문장에 대한 full formal semantic representation을 gold로 제공한다는 근거는 이번 조사에서 확인되지 않았다.

### GQNLI

GQNLI는 generalized quantifier inference를 테스트하는 사람이 만든 NLI 자료이지만, gold는 inference relation 쪽이고 full sentence MR을 제공한다는 근거는 확인되지 않았다.

따라서 이 둘도 FraCaS와 똑같다는 뜻은 아니지만, **현재 확보한 R4 근거만으로는 “문장 + 완성된 formal MR” source라고 기술할 수 없다.**

---

# B. 1차 BLOCKED 3건 재시도

## B-1. Quantification Bank 데이터 자체 라이선스

### 재시도한 경로

이번에는 1차 index 페이지 외에도 다음 계열을 다시 확인했다.

- Quantification Bank examples/index 및 background
- Quantification Bank bibliography
- QuantML concrete-syntax/specification 자료
- ISO 24617-12가 Bank를 설명하는 부분
- ISA-17 workshop 및 annotation material
- QuantML 관련 technical-report/저자 자료
- repository/README/GitHub 계열 검색
- `license`, `copyright`, `Creative Commons`, `GPL` 조합 검색

Bank 자체는 Tilburg University가 유지하는 annotated-example repository라는 설명이 재확인된다.

그러나 검색된 권리 문구들은 다음처럼 **주변 문서 자체의 저작권/라이선스**였다.

- ISO 표준 문서의 저작권
- ACL/ISA 논문의 publication license
- 저자의 technical document copyright

이 중 어느 것도 “Quantification Bank example data를 이 조건으로 배포한다”는 명시적 corpus-license statement는 아니었다.

### 결과

**BLOCKED 유지.**

정확한 표현은:

> 공개적으로 확인한 경로에서는 Quantification Bank example data 자체에 적용된 명시적 license statement를 찾지 못했다.

이지,

> Quantification Bank에는 라이선스가 없다.

가 아니다.

### 확신도

**높음** — “이번에 시도한 공개 경로에서 data-specific statement를 확보하지 못함”이라는 사실에 대한 확신도.

### BLOCKED

**예.**

---

## B-2. Quantification Bank item-level provenance

여기서는 일부 진전이 있었다.

### 새로 확인한 사실 — ISA-17 artifact attribution

ISA-17 workshop 페이지는 참가자들이 annotated examples를 제출하고 organizers가 feedback을 제공하는 구조였다고 설명하며, 특정 contribution에 대해서는 **“accompanying annotations and specification of their authors”​**라고 명시한다. Amblard et al.의 contribution과 Harry Bunt의 contribution에는 실제 accompanying annotation artifact가 연결되어 있다.

Amblard et al. accompanying annotation document에는 실제 test sentences와 QuantML annotations가 들어 있다.

Harry Bunt의 challenge-solution material에도 QuantML로 annotation된 test sentences가 있고, 그중에는:

```text
Most of the students passed the exam.
```

과 같은 proportional item도 있다.

따라서 **ISA-17 challenge artifact 자체에는 저자/제출자 귀속을 추적할 수 있다.**

### 그러나 Bank item과의 연결

현재 Quantification Bank의 개별 PDF, 예를 들어 proportional example PDF에서는 annotator/byline/provenance field가 별도로 표시되지 않는다. ISO/Bank 설명도 Bank 전체를 Tilburg가 유지한다고 할 뿐, **“Bank의 이 item은 ISA-17의 이 참가자가 작성했다”​**는 per-item mapping을 제공하는 근거는 이번 조사에서 찾지 못했다.

따라서 다음 둘을 구분한다.

| 질문 | 상태 |
|---|---|
| ISA-17 annotation artifact의 저자/참가자 attribution | **확인됨** |
| 현재 Quantification Bank 각 item의 annotator/author provenance | **미확인** |
| ISA-17 artifact → Bank item의 동일성/계보 | **미확인** |

### 결과

Quantification Bank **item-level provenance는 BLOCKED 유지**.

다만 1차보다 좁혀진 사실은 “관련 ISA annotation artifacts 전체가 무기명인 것은 아니다”라는 점이다.

### 확신도

**높음.**

### BLOCKED

**예 — Bank item-level mapping에 한함.**

---

## B-3. Overnight 원 배포처 dataset-specific license

### 공식 SEMPRE repository에서 확인된 것

Stanford의 공식 `percyliang/sempre` repository에는 `LICENSE.txt`가 있고 Apache License 2.0 문구가 있다. 파일은 Stanford University copyright를 명시한다.

그러나 이것을 Overnight dataset에 바로 적용하면 안 된다.

이유는 SEMPRE repository의 dependency script가 Overnight 데이터를 **repository source 자체와 별도로 Stanford NLP의 외부 data directory에서 가져오도록** 되어 있기 때문이다. 공식 README도 `overnight` package를 별도 module로 소개한다.

dependency script에서는 Stanford 내부/공개 data 경로를 조립하고 domain별 Overnight train/test paraphrase files를 가져오도록 되어 있어, 적어도 원 배포 provenance가 Stanford NLP/SEMPRE 쪽이라는 것은 확인된다.

### Apache 2.0을 dataset에 전이하지 않은 이유

SEMPRE `LICENSE.txt`는 software repository에 대한 라이선스 근거다. 조사한 자료에서는 외부 dependency로 내려받는 Overnight 데이터에 대해:

> Overnight dataset is licensed under Apache 2.0

에 해당하는 dataset-specific statement를 찾지 못했다.

Stanford의 같은 SEMPRE ecosystem에서도 WebQuestions처럼 dataset의 CC BY 조건을 **별도로 명시한 사례**가 있다. 하지만 Overnight에는 이번 검색에서 그와 동등한 원 배포처 문구를 확보하지 못했다.

이것 역시 “Overnight에는 license가 없다”는 부재 판정이 아니라 **dataset scope가 명시된 원문을 아직 확보하지 못했다**는 뜻이다.

### 시도 경로

- SEMPRE `LICENSE.txt`
- SEMPRE README
- Overnight package references
- `pull-dependencies` 및 Stanford NLP data locator
- Stanford `nlp.stanford.edu` software/data distribution 계열
- 논문/footnote license 검색
- `Overnight dataset license`, Stanford/SEMPRE 조합 검색

dependency script가 생성하는 원 public-data URL 자체는 browser inspection 과정에서 안정적으로 내용을 열지 못했기 때문에 404/부재로 판정하지 않았다.

### 결과

**BLOCKED 유지.**

1차에서 확보한 2차 배포처의 `CC BY-SA 4.0` 표기를 원 authority의 statement로 승격시키지도 않았고, SEMPRE 코드의 Apache 2.0을 dataset에 전이하지도 않았다.

### 확신도

**높음** — 현재 확보한 official sources의 scope 구분에 대해서.

### BLOCKED

**예.**

---

# C-1. 기수 수치를 제거해도 독립 양화/scope 구조가 남는가

여기서는 “그 표현이 동결 방언으로 채택 가능한가”를 판단하지 않고 **정본/formal representation의 구조만** 비교한다.

## 요약

| Source | 숫자/cardinality와 양화 구조의 관계 | 숫자 노드만 제거할 때 |
|---|---|---|
| **QuantML** | `cardinality`와 `scoping`은 별도 객체지만 entity가 `involvement`로 cardinality를 참조 | scope link 자체는 남을 수 있으나 entity의 필수 involvement reference가 깨짐. 자동 `∃`로 환원된다는 규칙은 확인되지 않음 |
| **Overnight** | cardinal restriction이 `filter/countComparative + comparator + number` 자체 | 숫자만 지우면 연산이 불완전. 전체 cardinal filter를 지우면 base entity set은 남지만 `three ...`에 해당하는 독립 quantifier는 남지 않음 |
| **ATIS 후대 Lambda** | `stops(x) > N` 같은 scalar comparison | 숫자만 지우면 비교식이 불완전. 비교 전체를 지우면 flight lambda는 남지만 stops에 대한 독립 `∃`/quantifier는 남지 않음 |
| **ERG/MRS 참고 신규계열** | quantifier EP와 `card_rel/CARG N`이 실제로 분리 | cardinal EP를 제거해도 quantifier EP의 RSTR/BODY 구조는 별도로 존재 |

---

## C-1-1. QuantML

1차에서 다룬 `All the students read at least three papers twice.` 유형에서 numerical involvement는 대략 다음처럼 분해된다.

```xml
<entity xml:id="x4" ... involvement="#n3"/>
<cardinality xml:id="n3"
             numRel="greater_or_equal"
             num="3"/>

<scoping ... arg2="#x4" .../>
```

QuantML concrete syntax상 `<cardinality>`와 `<scoping>`은 별도 구조이며, scope relation은 cardinality node `n3` 자체가 아니라 participant/entity 구조를 연결한다.

따라서 **graph/XML topology만 놓고 보면 `scoping` object는 cardinality node와 독립적으로 존재한다.**

그러나 `entity/@involvement`는 그 numerical involvement object를 참조한다. concrete syntax에서 entity의 involvement reference는 독립된 field이며, 단순히 `<cardinality id=n3>`만 삭제하면 `#n3` 참조가 dangling reference가 된다.

또한 조사한 QuantML 정본에서:

```text
at least three papers
→ cardinality를 삭제
→ 자동으로 exists(papers, ...)
```

와 같은 canonical erasure/default 규칙은 확인되지 않았다.

### 사실 결론

- **scope-relation 객체 자체:** cardinality와 별도로 존재
- **well-formed quantified participant:** cardinality를 단순 삭제해서 그대로 유지되는 구조는 아님
- **독립적인 explicit `∃`의 잔존:** 확인되지 않음

### 확신도

**높음.**

### BLOCKED

아니오 — 정본 syntax 구조에 관한 질문은 답할 수 있음.

---

## C-1-2. Overnight

실제 Overnight LF에서 하한 기수는 다음 계열로 표현된다.

```text
player who has at least 3 assists ...
→ SW.filter(... num_assists >= (number 3 assist))
```

또는 cardinality 비교형에서는 `SW.countComparative`가 사용된다.

즉 `at least three`의 의미가 별도의 generalized-quantifier node와 숫자 node 두 개로 나뉘는 것이 아니라 **filter/comparative condition 자체에 comparator와 number가 들어간다.**

따라서:

1. `(number 3 assist)`만 지우면 `>=` 연산의 피연산자가 없어져 expression이 완전하지 않다.
2. `SW.filter(... >= 3)` 전체를 지우면 그 이전의 player/entity set이나 다른 조건은 남을 수 있다.
3. 그러나 `three assists`에 해당하는 별도의 `exists`/RSTR/BODY quantifier가 자동으로 남는 구조는 아니다.

실제 공개 LF의 comparator-number 구조가 이를 보여준다.

### 사실 결론

**base denotation은 cardinal filter 삭제 후 남을 수 있지만, cardinal NP의 독립 양화 구조가 따로 잔존하는 형식은 확인되지 않는다.**

### 확신도

**높음.**

### BLOCKED

아니오.

---

## C-1-3. ATIS

후대 Lambda benchmark에서 실제 항목은:

```text
i want a flight ... that at least has one stop
→ (> (stops $0) 1:i)
```

및

```text
list all flight ... with at least 3 stop
→ (> (stops $0) 3:i)
```

처럼 나타난다. 이 comparison은 바깥의:

```text
(lambda $0 e
  (and
    (flight $0)
    ...
    (> (stops $0) 3:i)))
```

안의 한 conjunct다.

따라서 파생 Lambda 표현에서는:

- `3:i`만 삭제하면 `>`가 불완전해진다.
- `> (stops $0) 3:i` conjunct 전체를 삭제하면 `flight($0)` 및 다른 flight 조건은 남는다.
- 그러나 stops를 별도 개체 변수로 existentially bind하는 구조는 이 LF에 없다.

### 원 reference SQL과의 구분

1차에서 확정된 정본은 **original reference SQL**이다. 이번 조사에서도 위 utterance와 정확히 같은 원 reference SQL row를 회수해 대조하지 못했다.

따라서 위 사실은 **후대 Lambda representation**에 대한 것이고,

> 원 ATIS reference SQL에서도 cardinal comparison을 삭제했을 때 무엇이 정확히 남는가

는 여전히 직접 증거가 없다.

### 확신도

- 후대 Lambda: **높음**
- 원 reference SQL 해당 row: **미확인**

### BLOCKED

**원 SQL에 한해 BLOCKED.**

---

## C-1-4. 비교를 위해 확인한 ERG/MRS

1차 대상 세 source 밖이지만, 구조적 대조가 명확하다.

```text
Three dogs bark ...
```

의 MRS에서는:

```text
bare_div_q_rel(... x ...)
  RSTR ...
  BODY ...

card_rel(... x ...)
  CARG 3
```

처럼 **quantifier EP와 cardinal-number EP가 분리**되어 있다.

따라서 적어도 이 MRS 구조에서는 `card_rel/CARG 3`과 RSTR/BODY quantifier structure가 동일 노드가 아니다.

이는 QuantML·Overnight·ATIS의 삭제 구조와 다른 실제 formalism 설계 사례다.

---

# C-2. QuantML·Overnight·ATIS가 `most`·`few` 등 비례도 다루는가

## QuantML

**예. 직접 확인됨.**

```xml
<relativeSize ... pred="most"/>
```

및 별도 `scoping`이 실제 Bank example에 존재한다.

ISA-17 material에도:

```text
Most of the students passed the exam.
```

을 QuantML로 처리한 annotation artifact가 존재한다.

---

## Overnight

이번 조사는 공개 **basketball/socialnetwork train data**에서 proportional 후보를 별도로 확인했다.

### `most`

발견된 `most`의 다수는:

- `most rebounds`
- `most assists`
- `the ... with the most ...`

처럼 `SW.superlative`, `SW.countSuperlative`, `max`에 대응하는 **최상급**이었다. 사용자 정의상 proportional에서 제외된다.

### `majority`

socialnetwork에는 `majority`가 들어간 문장이 존재한다. 그러나 실제 LF 중 하나는 다수값(mode)을 `countSuperlative ... max`로 구하고, 다른 `majority of people` 표현은 reference population의 절반을 계산하는 것이 아니라 **fixed comparison `count > 2`**로 번역되어 있다.

따라서 그 항목을:

```text
|A| > 1/2 |B|
```

와 같은 비례 formal semantics로 해석해 보고할 근거는 없다.

### `half`, `few`

검사한 socialnetwork train file에서는 `half`, `few`에 해당하는 proportional item을 찾지 못했다.

### 상태

**검사한 split에서는 faithful proportional encoding을 확인하지 못함.**

그러나 모든 Overnight domain과 모든 split을 전수 조사한 것은 아니므로:

> Overnight에 proportional item이 없다

라고 판정하지 않는다.

### BLOCKED

**corpus-wide absence/presence = BLOCKED.**

---

## ATIS

검사한 ATIS train file의 `most` 예들은 주로:

- `most expensive`
- `airline with the most arrivals`
- 기타 max/argmax 질문

으로, 요청 정의의 proportional `most of X`가 아니라 최상급/집계 최대값이다.

같은 train file에서 `half`, `majority`, proportional `few`의 실물을 확인하지 못했다.

### 상태

**검사한 train split에서는 proportional quantifier 실물 미확인.**

ATIS 전체에 대한 부재 판정은 하지 않는다.

### BLOCKED

**corpus-wide absence/presence = BLOCKED.**

---

# C-3. 1차에 없던 source/formalism 계열

## C-3-1. Ohio State Wikisem typed-lambda corpus

A-2에서 실물을 제시했다.

### R4 요약

이 formalism은 비례와 기수를 같은 typed-lambda framework 안에서 서로 다른 semantic operations로 직접 표현한다.

```text
most R S
half R S

count= 5500 R S
ratio= .71 R S
```

그리고 restrictor / nuclear scope를 함수 인자로 갖는다.

현재 배포 corpus 안에서도 `Most of the Earth's surface ...` 같은 proportional item을 확인했다.

### 상태

- English: 확인
- sentence-level typed LF: 확인
- human scope annotation/correction: 확인
- proportional + cardinal formal vocabulary: 확인
- corpus data-specific license: `BLOCKED`

---

## C-3-2. DELPH-IN ERG/MRS + Redwoods

### R4 요약

ERG/MRS에서는:

**cardinal**

```text
bare_div_q_rel(... RSTR ..., BODY ...)
card_rel(... CARG 3)
```

**proportional**

```text
_most_q(x, hRestrictor, hBody)
```

처럼 표현할 수 있다.

Redwoods는 사람이 preferred ERG analysis를 선택한 English gold treebank다.

### 상태

- formalism의 cardinal 유지: 확인
- formalism의 proportional `most`: 확인
- quantifier scope handles: 확인
- Redwoods human-selected analyses: 확인
- 실제 Redwoods release 안의 proportional item locator: `BLOCKED`

---

## C-3-3. English AMR 3.0

영어 AMR 계열은 Portuguese AMRNews와 별개로 확인했다.

AMR 3.0은 English sentences와 AMR graphs를 짝지은 대규모 English release다.

정본 guideline에서 정확 기수는 예컨대:

```text
:quant 4
```

처럼 graph에 유지되고, `more than four thousand`도 `more-than`과 수치를 이용해 표현할 수 있다. 백분율 entity에도 숫자 value를 기록할 수 있다.

그러나 AMR guideline은 동시에:

> “does not represent quantifier scope”

및 quantifier에 대해 deep representation을 갖지 않는다는 취지를 명시한다.

또한 이번 공식-guideline 조사에서 확인된 `most` 관련 예 중에는 “most cars”류의 **최상급/quantity construction**이 있었지만, `Most cats sleep`, `most of the students`, `majority of X`를 generalized proportional scope relation으로 나타내는 정본 실물은 확보하지 못했다.

### 상태

| 사실 | 상태 |
|---|---|
| English sentence → AMR graph | 확인 |
| cardinal number가 graph에 남음 | 확인 |
| quantifier scope | 정본이 비표상이라고 명시 |
| proportional `most/majority`의 generalized-quantifier formalization | 미확인 |
| 백분율 numeric value 표현 | 확인, 단 이것만으로 proportional scope를 의미하지 않음 |

### BLOCKED

proportional GQ 실물에 대해서 **예**.

---

## C-3-4. Boxer / DRS / Groningen 계열

Boxer는 CCG derivation 등으로부터 DRS/semantic representation을 생성하는 **automatic semantic parser**다.

이번에 검색된 공개 English DRS corpus/gold 경로 중 주요한 것은 PMB/Boxer 계열이었다. 이들은 사용자가 명시한 `not_derived_from_PMB` 조건과 별도로 분리해야 한다.

이번 조사에서는:

> PMB에서 파생되지 않았으며, 다른 기관/저작 주체가 독립적으로 저작·검수했고, English sentence와 DRS를 gold로 짝지으며, actual proportional + cardinal item을 제공하는 Boxer-based corpus

를 item locator까지 확보하지 못했다.

이것은 **그러한 corpus가 존재하지 않는다는 판정이 아니다.**

### BLOCKED

**예 — 독립 non-PMB gold corpus locator.**

---

## C-3-5. Universal Dependencies 의미 확장 / UDepLambda

표준 UD 자체는 syntactic dependency annotation이며, generalized quantifier의 semantic class와 scope를 sentence-level gold semantics로 제공하는 layer가 아니다.

UDepLambda 등의 연구는 UD parse를 규칙 및 lexical information을 통해 logical form으로 변환한다. 일부 quantifier scope도 처리하지만, semantic representation은 **UD gold에 사람이 별도로 저작한 sentence-level formal meaning을 읽는 것이 아니라 rule-based conversion으로 생성**된다.

DRS/LF로 변환하는 후속 계열도 같은 방향이다.

### 상태

- UD syntax gold: 있음
- rule-derived logical semantics: 있음
- independent human-authored proportional sentence-MR gold라는 근거: 이번 조사에서 미확인

---

## C-3-6. QALD / TREC-style query gold

QALD류에는 natural-language question과 executable SPARQL query를 짝지은 semantic parsing gold가 존재한다.

SPARQL 자체는 `COUNT`, comparison, aggregation 등을 표현할 수 있다. 그러나 이번 조사에서는 corpus 실물 중:

```text
Most X ...
more than half of X ...
80% of X ...
```

에 대해 **reference-set proportion을 계산하는 SPARQL gold**가 붙은 item을 확보하지 못했다.

또한 “which X has the most Y?”는 대부분 최대값/superlative query가 될 수 있으므로 사용자의 proportional 정의에 자동 포함시키지 않았다.

### BLOCKED

**비례 실물 item locator = BLOCKED.**

---

# D. 이번 조사에서 새로 확정된 핵심 사실

적격성 판정 없이 사실만 압축하면 다음과 같다.

| 항목 | 새로 확인된 사실 |
|---|---|
| **QuantML proportional** | `most`가 `<relativeSize pred="most">`로 직접 표상되고 별도 `scoping` relation이 존재 |
| **새 source: Wikisem** | 약 2,000 English Simple-Wikipedia sentences → typed lambda calculus. `most`, `half`, `count=`, `ratio=`를 정식 operator로 사용하며 현재 corpus에서 실제 `Most of ...` item 확인 |
| **새 family: ERG/MRS** | cardinal `card_rel/CARG N`과 quantifier RSTR/BODY가 분리되고, proportional `_most_q`도 직접 존재 |
| **QuantML cardinal 삭제 구조** | `scoping`은 cardinality와 별도이지만 entity가 cardinality를 `involvement`로 참조하므로 단순 숫자-node 삭제가 well-formed existential projection을 자동 생성하지 않음 |
| **Overnight cardinal 삭제 구조** | comparator+number가 filter/comparative condition 자체. 조건 전체 삭제 후 base set은 남아도 cardinal NP의 별도 binder는 남지 않음 |
| **ATIS Lambda cardinal 삭제 구조** | `stops(x)>N` comparison 자체가 cardinal restriction. 삭제 후 flight 조건은 남지만 stop existential은 별도 존재하지 않음 |
| **Overnight proportional 검사** | 조사한 basketball/socialnetwork train에서 `most`는 주로 superlative. `majority of people` 한 사례도 reference-set ratio가 아니라 fixed `count > 2` |
| **ATIS proportional 검사** | 조사한 train의 `most`는 superlative/max 계열; proportional item 미확인 |
| **English AMR 3.0** | cardinal numeric representation은 존재하지만 정본이 quantifier scope 비표상을 명시 |
| **Quantification Bank license** | 대체 경로까지 확인했지만 data-specific license 문구 확보 실패 → BLOCKED 유지 |
| **Quantification Bank provenance** | ISA-17 annotation artifacts에는 authorship attribution이 있지만 현재 Bank item과의 per-item mapping 미확보 → BLOCKED 유지 |
| **Overnight original license** | SEMPRE는 Apache 2.0이지만 Overnight data는 외부 dependency. dataset-specific 원 배포 license 문구 미확보 → BLOCKED 유지 |

---

# E. BLOCKED ledger 및 실패 경로

| 조사 대상 | 시도 | 결과 |
|---|---|---|
| Quantification Bank data license | Bank index/background/bibliography, concrete syntax, ISO, ISA-17, 저자/technical material, repository/README/GitHub 및 license 키워드 | 문서 저작권만 확인. Bank data-specific license 없음을 **확정한 것이 아니라 미발견** → `BLOCKED` |
| Quantification Bank item provenance | Bank PDFs + ISA-17 participant/contribution pages + accompanying annotations | ISA artifacts의 author attribution은 확인. Bank 각 PDF와 author의 mapping 없음 → `BLOCKED` |
| Overnight original data license | SEMPRE LICENSE/README/package, dependency script, Stanford NLP distribution paths, 논문·footnote 검색 | SEMPRE code Apache 2.0과 외부 Overnight data를 구분. dataset-specific statement 미확보 → `BLOCKED` |
| Overnight original dependency file URL | dependency script의 literal Stanford path를 따라감 | browser에서 원 data payload를 안정적으로 inspection하지 못함. 404/부재로 판정하지 않음 |
| Wikisem current large logic file | 원 저자 `/dwnload` 페이지와 listed filename을 문자 그대로 사용 | locator 및 파일 배포는 유효. 웹 renderer가 대용량 파일을 직접 표시하지 못한 것은 자료 부재로 처리하지 않음 |
| Redwoods proportional gold item | Redwoods metadata/논문 + ERG/MRS formal examples | formalism의 `_most_q` 확인. 특정 Redwoods release item locator 미확보 → `BLOCKED` |
| Boxer non-PMB independent corpus | Boxer/DRS 및 Groningen 계열 검색 | 확인된 주요 gold 경로가 PMB 계열. 별도 독립 corpus를 찾지 못했으나 부재 판정하지 않음 → `BLOCKED` |
| QALD proportional item | question↔SPARQL 자료 계열 조사 | full SPARQL gold 자원은 확인, proportional reference-set ratio 실물 미확보 → `BLOCKED` |

---

## F. 운영 세션에 넘길 때 유의할 사실

이번 조사 결과 중 기계 실측으로 넘길 가치가 있는 **locator/구조적 사실**만 열거하면 다음과 같다. 이는 적격성 순위가 아니다.

1. **QuantML Bank proportional example**  
   `The girls have eaten most of the chocolate.`  
   → `relativeSize(pred="most")` + 별도 `scoping`.

2. **Ohio State Wikisem**  
   현재 `/dwnload` 배포의 `wikisemC*.logic__0.txt` 계열. Formal vocabulary에 `most`, `half`, `count=`, `ratio=`가 있고 현재 C1에서도 `Most of the Earth's surface ...` 실물 확인. Scope annotation에는 사람 표시·수정이 관여한다.

3. **ERG/MRS + Redwoods**  
   formalism에서 `card_rel(CARG N)`과 quantifier RSTR/BODY가 분리되며 `_most_q`가 존재한다. Redwoods는 hand-selected ERG analyses를 갖지만, proportional record의 release-level locator는 아직 `BLOCKED`.

여기까지가 2차 요청서에서 요구한 **사실 확인 범위**다. 동결 방언으로의 투영 가능성, 실제 표면 필터 통과 여부, `기수 ≥3 / 비례 ≥1` 충족 여부는 요청서가 별도 운영 실측으로 남겨 둔 사항이므로 이 보고서에서는 판정하지 않았다.
<!-- VERBATIM-END -->

`VERBATIM_SHA256: ee9f325e68e5bcc4d17d957745e53db39c88e54b04f66a774e352abeae6f4bd3`

---

## 수신 검증 기록 (2026-08-24, 운영 세션)

### V1 (최중대) — Wikisem은 **이미 배제된 source**다. 조사 서술은 우리 실측과 배치된다

조사는 A-2/C-3-1에서 Ohio State Wikisem typed-lambda corpus를 "1차에 없던
별도 source family"로 제시하고 "약 2,000 English **sentences**", "배포 logic
파일 역시 **sentence별 record** 제공"이라고 적었다. 우리 판정·실측은 다르다.

**우리 선행 판정**: `DESIGN_DECISION_o1_oracle_unit_and_coverage.md`(D-21)가
wikisem을 **O1-v0의 단위·표현 경계에 부적합한 oracle source**로 분류하고
O1 instance source 교체(b\*)를 명령했다. 근거로 기록된 실측:
`Coverage(v0, wikisem-article-LF) = 0` / `0/121` / "wikisem article-level LF와
O1-v0 acceptance-fixture contract의 교집합이 비어 있다".

**이번 재실측** (로컬 캐시 `wikisemC6.logic.txt`, 992KB):

| 항목 | 실측값 | 조사 서술 |
|---|---|---|
| record 수 | **131** (id 1~131, 각 1행) | "약 2,000 sentences" |
| record 내용 | 한 record가 여러 문장을 담은 **거대 단일 LOGIC 식** (첫 record가 Gironde 기사 도입부 3~4문장) | "sentence별 record" |
| 담화 구성자 | `InAnaphorSet` **1690회**, `Equal` **1297회** | (언급 없음) |
| `ratio=` | **0회** | "논문의 실제 예 … `ratio= .71`" |
| `count=` | **0회** | "`count= 5500`으로 나타낸 실물" |
| `Most` (대문자 GQ) | **0회** | "`most R S` generalized-quantifier relation" |
| `most` | 54회 — 그중 **48회가 `A-aN:most`(형용사=최상급)**, 나머지 9회는 `N-b{N-aD}:most`/`N-bO:most` | "proportional `most` 확인" |

즉 (i) 단위는 **기사**이며 조사 자신도 "원자료는 이어진 Wikipedia article의
첫 3–6문장"이라 적어 서술 내부에 모순이 있다 — 우리 실측이 그것을 해소한다.
(ii) 조사가 인용한 비례·기수 연산자(`most R S`, `half R S`, `ratio=`,
`count=`)는 **논문의 예시**이고 적어도 C6 배포본에는 **존재하지 않는다**.
(iii) `most` 54회는 대부분 최상급 형용사로, 요청서가 제외 목록에 명시한 바로
그 부류다.

**P12 overturn** (위임 산출의 재실측 원칙)이며, 같은 오류의 **2회째**다 —
이전 라운드에서도 "WikiSem 제2 source 제안 → 선행 기사 단위 실측과 충돌
(선행 실측이 이긴다)"이 기록됐다.

**원인은 우리 요청서에 있다.** CLAUDE.md는 "외부 판정자에게 미리 알려진 것을
다시 청하지 않는다"를 규율로 두고 선행 판정을 요청서에 embed하도록 한다.
2차 요청서 §0에 1차 확정 사실은 넣었으나 **D-21의 wikisem 배제는 넣지
않았다**(1차 회신에 없던 항목이라 누락). 조사 채널에도 **우리 선행 판정
목록을 함께 전달**해야 한다 — 3차 요청 시 반영한다.

### V2 — C-1의 답은 기수 층의 구조적 제약을 확정한다

조사가 준 답: QuantML은 `scoping`이 `cardinality`와 별도 객체지만
`entity/@involvement`가 cardinality를 참조하므로 숫자 노드만 지우면
dangling reference가 되고, **자동 `∃` 환원 규칙은 정본에 없다**.
Overnight·ATIS는 comparator+number가 filter/비교식 자체여서 지우면 식이
불완전하고, 조건 전체를 지우면 base set은 남아도 **기수 NP의 독립 binder가
남지 않는다**. ERG/MRS만 `card_rel(CARG N)`과 quantifier EP(RSTR/BODY)가
분리된다.

**우리 방언 관점 귀결**(운영 세션 판정): 우리 방언에는 수치가 없으므로
QuantML·Overnight·ATIS 재료는 **기수를 버리고 쓸 수도 없다**(버리면 양화
구조 자체가 무너지므로). 즉 기수 층을 채우는 경로는 두 가지로 좁혀진다 —
(a) 방언에 기수 표현을 추가하고 그 source를 adapter로 받는다,
(b) **ERG/MRS 계열**처럼 기수 EP와 양화 EP가 분리된 formalism을 써서 기수
EP만 비계로 제거하고 양화 구조를 측정한다. (b)는 D-25 projection의 논리를
그대로 재사용할 수 있다는 점에서 구조적으로 유망하나, 조사가 **Redwoods
release 안의 실제 proportional item locator는 BLOCKED**로 남겼다.

### V3 — 1차 BLOCKED 3건은 정당하게 유지됐다

경로를 바꿔 재시도한 기록이 구체적이고(§B-1의 8경로, §B-3의 7경로),
"라이선스 없음"으로 바꾸지 않았다. SEMPRE의 Apache 2.0을 **데이터에 전이하지
않은 판단**과 WebQuestions가 별도로 CC BY를 명시한 대조 사례를 든 것은
1차의 원칙(문서 저작권 ≠ 데이터 라이선스)을 정확히 적용한 것이다.
부수 진전: ISA-17 artifact에는 저자 귀속이 있고 그중
`Most of the students passed the exam.`이 QuantML로 annotation돼 있다 —
Bank item과의 per-item mapping만 미확보.

### V4 — 비례 후보의 현재 상태 (운영 세션 정리)

| 후보 | 비례 표상 | 남은 차단 |
|---|---|---|
| QuantML Bank | `<relativeSize pred="most">` + 별도 `scoping` — 요청 정의에 정확히 부합 | 데이터 라이선스·item provenance **BLOCKED**, 방언 표현 불가 |
| Wikisem | 논문 문법에는 `most R S`·`half R S` | **D-21 배제 + C6 실물에 연산자 0회 + 단위=기사** → 후보 아님 |
| ERG/MRS + Redwoods | `_most_q(x, h, h)` 확인, Redwoods는 GPL 표기·사람 선택 gold | **release 내 proportional item locator BLOCKED**, 방언 표현 여부 미판정 |
| Overnight | 검사 split에서 `most`는 최상급, `majority`는 `count > 2` | 비례 부재는 BLOCKED(전수 아님) |
| ATIS | 검사 split에서 최상급/max | 동일 |
| English AMR 3.0 | 기수는 `:quant`, **비례 GQ 정본 실물 미확인** | AMR 정본이 scope 비표상 명시 |
| QuRe / GQG / GQNLI / UDepLambda / QALD | 양화 annotation은 있으나 **문장 단위 full formal MR 근거 미확보** | 오라클 불가 또는 BLOCKED |

**적격 하한(기수 ≥3, 비례 ≥1)을 충족하는 후보는 아직 없다.** 가장 가까운
것은 ERG/MRS + Redwoods이며, 그 진로는 (i) proportional item locator 확보
(3차 조사) + (ii) MRS→우리 IR adapter 설계 + (iii) 기수 EP를 비계로 다루는
projection 확장 — 모두 판정 사안이거나 조사 사안이다.
