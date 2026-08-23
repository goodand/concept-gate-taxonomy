# RESEARCH RESULT — 기수 양화 source 조사 회신 (2026-08-23)

- 수신: 2026-08-23, 사용자 경유 (조사용 agent, 다른 workspace)
- 원 요청: `RESEARCH_REQUEST_cardinal_quantifier_source.md`
  (개정 2 sha256 `e781d83de1e2861e904a…` — **회신은 개정 1 기준**, §V2 참조)
- 성격: 사실 확인 보고이며 적격성 판정이 아니다(조사가 명시). 적격성은
  운영 세션의 기계 실측 소관.
- 요약: 후보 6개 조사(QuantML/Quantification Bank·Overnight·GeoQuery·ATIS·
  AMRNews·FraCaS). 기수 실물은 여러 곳에 있으나 **전부 우리 동결 방언으로
  표현 불가**하거나 다른 조건에서 탈락한다 — §수신 검증 참조.

---

## 판정/회신 전문 (verbatim)

<!-- VERBATIM-BEGIN -->
# 기수 양화(cardinal quantifier) gold source 조사 보고서 — R1–R6

## 0. 조사 범위

이 보고서는 요청서의 정의를 그대로 따른다. 여기서 기수 양화는 명사구의 수량을 제한하는 **정확수, 하한, 상한, 단순 기수**이며, 단순 액수·나이·연도 등의 수치 언급은 제외한다.

또한 이 보고서는 **후보의 최종 적격성을 판정하지 않는다.** 서로 다른 저작 주체인지, PMB 파생인지, 사람이 작성한 gold인지, 문장–표상 대응이 실제 측정 조건을 통과하는지는 사실을 최대한 분리해서 적고, 확인할 수 없는 부분은 `BLOCKED`로 남긴다. 특히 라이선스를 주변 정책에서 추론하지 않고 배포처의 명시 문구만 사용하며, 접근 실패를 “없음”으로 바꾸지 않았다.

## 1. R1 — 후보 목록

| 후보                                                                          | 저작/관리 주체                                            | 형식 의미 표상                                                              | 규모 신호                                                                             | 접근                                                                                                           | 조사 상태                                                       |
| --------------------------------------------------------------------------- | --------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------- |
| **QuantML / Tilburg Quantification Bank + ISA-17 Quantification Challenge** | Tilburg University / Harry Bunt 및 QuantML·ISO 계열    | QuantML XML + abstract syntax + 조합적 DRS 계열 semantics + scope relation | Quantification Bank는 예제 모음; ISA-17 별도 test suite                                  | [Quantification Bank examples](https://sigsem.uvt.nl/QuantificationBank/examples.htm?utm_source=chatgpt.com) | R3/R4 매우 구체적; 데이터 라이선스·각 예제의 저작 provenance 일부 BLOCKED       |
| **Overnight**                                                               | Yushi Wang, Jonathan Berant, Percy Liang / Stanford | Lambda DCS 계열 executable LF; 공개 benchmark 변환본에는 SEMPRE `SW.*` 표현      | 원 논문 7개 도메인, **12.6K examples**                                                   | [원 논문](https://cs.stanford.edu/people/pliang/papers/overnight-acl2015.pdf?utm_source=chatgpt.com)            | 실제 cardinal LF 다수 확인; 원 배포처의 데이터별 라이선스 문구 BLOCKED           |
| **GeoQuery / Geo880**                                                       | UT Austin semantic parsing 연구 계열                    | Prolog 기반 logical query; FunQL 변환판 존재                                 | **880 English questions**                                                         | [UT Austin GeoQuery Data](https://www.cs.utexas.edu/~ml/nldata/geoquery.html)                                | 명시 라이선스와 수작업 gold 확인; 관찰된 cardinal 종류는 좁음                   |
| **ATIS**                                                                    | ATIS consortium sites / LDC                         | 원 corpus의 reference SQL; 후대 benchmark의 Lambda LF 등                    | 표준 semantic parsing benchmark 약 5.4K query 계열; 원 ATIS0 Complete는 여러 하위 collection | [LDC ATIS0 Complete](https://catalog.ldc.upenn.edu/LDC93S4A)                                                 | cardinal 실물 있음; 원본 라이선스 제한적이고 후대 Lambda는 변환물                |
| **AMRNews (Brazilian Portuguese AMR-BP)**                                   | NILC                                                | AMR/PENMAN graph                                                      | AMRNews 공개 corpus; 별도 문헌에서 870 annotated sentences 보고                             | [AMR-BP repository](https://github.com/nilc-nlp/AMR-BP)                                                      | 수작업·라이선스·cardinal 실물 명확; 단 AMR 정본이 quantifier scope 비표상을 명시 |
| **FraCaS test suite**                                                       | FraCaS Consortium; Bill MacCartney XML 배포판          | premise/question(or hypothesis)/answer label                          | **346 textual inference problems**                                                | [MacCartney FraCaS downloads](https://nlp.stanford.edu/~wcmac/downloads/)                                    | cardinal 예는 강함. 그러나 문장별 formal MR은 확인되지 않음                  |

## 요청서가 R4, 즉 **형식 문법의 정본과 기수 인코딩**을 R3보다 중요하게 보도록 명시했으므로, 아래에서는 각 후보를 R2–R6 관점에서 별도로 적는다.

## 2. QuantML / Quantification Bank / ISA-17

### R2 — 라이선스

**Quantification Bank 예제 데이터 자체:** `BLOCKED`.

Bank의 예제 인덱스에는 이것이 QuantML specification 및 annotation guidelines를 따르는 “collection of QuantML examples”라는 설명은 있으나, 조사한 페이지에서 `license` 또는 `copyright`에 해당하는 데이터 배포조건을 찾지 못했다. 따라서 논문이나 ISO 문서의 라이선스를 예제 데이터로 전이하지 않는다.

관련 문서의 권리 조건은 서로 다르다.

* ACL Anthology의 2021 ISA 논문은 2016년 이후 자료에 대해 **“Creative Commons Attribution 4.0 International License”**라고 명시한다. 이는 **논문**에 대한 조건이다.
* 정본 표준 ISO 24617-12:2025 PDF에는 **“© ISO 2025 – All rights reserved”**가 있고, 별도 허용·구현상 필요가 아닌 경우 서면허가 없이 복제·이용할 수 없다는 문구가 있다. 이것도 **표준 문서**의 저작권이지 Bank corpus의 데이터 라이선스는 아니다.

**확신도:** Bank 데이터 라이선스 BLOCKED = 높음.
**BLOCKED:** 예.

### R3 — 기수 양화 실재 신호

여기는 매우 직접적이다. Bank 인덱스 자체가 `Numerical quantifiers` 항목을 두고 있으며 `Three men`, `More than two thousand`, `at least three papers` 등 정확수·하한·초과수를 다룬다.

실물 예:

| 표면 문장                                                | 표상 조각                                                                |   |         |
| ---------------------------------------------------- | -------------------------------------------------------------------- | - | ------- |
| `Three men moved both pianos.`                       | `<entity ... indiv="count" involvement="3"/>`; semantics에 `          | X | = 3`    |
| `More than two thousand students protested twice.`   | `<cardinality ... numRel="greaterThan" num="2000"/>`; semantics에 `   | X | > 2000` |
| `All the students read at least three papers twice.` | `<cardinality ... numRel="greater_or_equal" num="3"/>`; semantics에 ` | Y | ≥ 3`    |

첫 예는 `Three men`에 count 3을 부여하고, `both pianos`에는 2를 부여하며 두 참여자 사이의 `scoping ... scopeRel="wider"`까지 기록한다. 의미 해석도 `|X|=3`, `|Y|=2`로 내려간다.

둘째는 cardinality 객체가 `greaterThan`, `2000`을 명시하고 의미론에서도 `|X|>2000`으로 해석된다. 셋째는 `greater_or_equal`, `3`을 명시하면서 학생과 논문의 상대 scope를 별도 `scoping` 구조로 표현하고, 의미론도 `|Y| ≥ 3`으로 계산한다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R4 — 형식 문법의 정본

정본이 가장 분명한 후보 중 하나다.

ISO 24617-12:2025는 QuantML이 **XML-based representation format, abstract syntax, semantics**로 구성된다고 정의하고, 목차에서도 §6.1 abstract syntax, §6.2 concrete syntax, §6.3 semantics 및 Annex C example annotations를 별도로 둔다. Quantification Bank는 이 표준 문서 안에서도 Tilburg University가 유지하는 annotated-example repository로 명시돼 있다.

ISA-17 설명 논문도 QuantML의 abstract/concrete syntax와 semantic interpretation을 설명하는 것이 목적이라고 명시한다.

기수는 단순 문자열이 아니라, 예컨대

`<cardinality ... numRel="greater_or_equal" num="3"/>`

처럼 **수치 관계 + 수치 상수**로 인코딩되고, entity의 `involvement`에 연결된다. scope는 별도 `scoping` relation으로 나타낼 수 있으며 조합적 의미론으로 해석된다.

**확신도:** 매우 높음.
**BLOCKED:** 아니오.

### R5 — 수작업 저작 여부

ISA-17은 사람이 QuantML annotation을 수행하는 shared annotation task로 설계되었고 논문은 test suite와 suggested markables를 설명한다.

다만 **현재 Quantification Bank에 놓인 각 PDF 예제가 구체적으로 누가 어느 단계에서 수작업 작성·검수했는지에 대한 item-level provenance 문구**는 이번 조사에서 찾지 못했다. 표준·shared task 저자들이 만든 explanatory examples라는 정황과 별개로, 요청서 기준상 이것을 자동으로 `independently_authored_gold=true`로 판정하지 않는다.

**확신도:** shared-task human annotation = 높음; Bank 각 항목 provenance = 중간 이하.
**BLOCKED:** 부분적으로 예.

### R6 — 문장 단위 1:1 여부

Bank는 한 문장을 기준으로 markables, XML, abstract syntax, semantics를 제시한다. 다만 scope가 모호한 경우 하나의 문장에 **Reading a/b/c**처럼 여러 의미 해석이 붙는다. `Three men moved both pianos` 예는 세 reading을 제시한다.

따라서 자료 구조는 **sentence-centered**이지만 엄밀한 의미에서 항상 sentence:representation = 1:1은 아니다. reading을 별도 단위로 취급해야 하는 경우가 있다.

**확신도:** 높음.
**BLOCKED:** 아니오.

---

## 3. Overnight

### R2 — 라이선스

원 저자 Stanford 배포처에서 이번 조사로 **Overnight 데이터 자체에 적용된 명시적 LICENSE 문구**를 찾지는 못했다.

후대 XSemPLR 배포판은 dataset별 라이선스를 명시하면서 verbatim으로

`Overnight, CC BY-SA 4.0`

이라고 기재한다. 같은 곳에서 GeoQuery는 GPL 2.0, ATIS는 LDC User Agreement라고 분리해 둔다. 또한 XSemPLR **code**는 별도로 MIT라고 명시한다.

따라서 현재 사실관계는:

**2차 배포처:** CC BY-SA 4.0이라고 명시.
**원 저자/원 배포처의 dataset-specific authority:** `BLOCKED`.

코드 라이선스를 데이터에 전이하지 않았다.

**확신도:** 2차 배포 문구 높음; 원 라이선스 낮음.
**BLOCKED:** 예.

### R3 — 기수 양화 실재 신호

공개 benchmark mirror에서 정확수·상한·하한이 모두 LF에 실재한다.

`player who has at least 3 assists over a season`은 `>=`와 `(number 3 assist)`로 대응한다.

`which players play no more than two positions`은 `SW.countComparative ... <= ... (number 2)`로 대응한다.

`how many blocks ... exactly 3 assists`는 `num_assists`, `=`, `(number 3 assist)`로 대응한다.

즉 이 세 예만으로도 요청 정의의 **하한 / 상한 / 정확수**가 각각 표면과 LF 양쪽에 나타난다.

다만 같은 공개 자료에는 자연언어와 LF가 어긋나는 noisy example도 있다. 예컨대 `more than 3 turnovers`인데 비교자가 반대로 `<`인 항목이 있다. 이는 별도 측정에서 검증해야 할 데이터 품질 신호이며, 원 논문 역시 crowdsourced paraphrase의 오류를 보고한다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R4 — 형식 문법의 정본

원 논문은 logical form을 **Lambda DCS**로 나타낸다고 명시하고, set 기반 composition을 설명한다.

데이터 생성 절차도 명시적이다. 간단한 grammar가 **logical forms와 canonical utterances를 함께 생성**하고, 이후 crowdsourcing으로 canonical utterance를 natural utterance로 paraphrase한다.

공개 변환판에서 cardinal은 `SW.filter`, numeric property, 비교자 `=`, `<`, `<=`, `>=`, `>`, 그리고 `(number N unit)`을 통해 나타나며 집합의 cardinality 자체를 묻는 경우 `SW.countComparative`도 사용된다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R5 — 수작업 저작 여부

여기는 순수한 “사람이 LF를 하나씩 손으로 붙인 corpus”가 아니다.

원 논문의 절차는:

1. builder가 domain seed lexicon을 만든다.
2. grammar/framework가 LF + canonical utterance를 생성한다.
3. Amazon Mechanical Turk 노동자가 canonical utterance를 자연언어로 paraphrase한다.
4. `(x, c, z)` 데이터가 만들어진다.

논문은 7개 domain에서 AMT paraphrase를 수집했고 최종적으로 **12,602 examples**를 얻었다고 보고한다.

즉 **자연언어 쪽은 인간 paraphrase**, LF는 저자가 설계한 grammar에서 생성된 것이다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R6 — 문장 단위 1:1 여부

학습 record 하나는 natural utterance와 LF를 함께 가진다. 다만 같은 canonical LF가 여러 human paraphrase를 낳을 수 있으므로 전체 corpus 수준에서는 여러 문장이 하나의 LF에 대응할 수 있다. 원 논문 자체가 데이터셋을 `(x,c,z)` triple로 정의한다.

따라서 **record-level 1:1**은 가능하지만 global bijection은 아니다.

**확신도:** 높음.
**BLOCKED:** 아니오.

---

## 4. GeoQuery / Geo880

### R2 — 라이선스

UT Austin의 공식 데이터 페이지 문구:

> “This data is made available under under GPL 2.0”

같은 페이지가 `geoqueries880`을 “sentences and their corresponding logical queries”라고 명시한다.

**확신도:** 매우 높음.
**BLOCKED:** 아니오.

### R3 — 기수 양화 실재 신호

공개 Geo880 mirror에서 다음이 실제 존재한다.

`how many states border at least one other state ?`

→ `answer(A,count(B,(state(B),next_to(B,C),state(C)),A))`

`what states contain at least one major rivers ?`

→ `answer(A,(state(A),loc(B,A),major(B),river(B)))`

여기서 `at least one`은 별도 `>= 1` 수치 연산자로 나타나는 것이 아니라 **존재 변수 C/B가 있는 conjunction**으로 의미화된다.

대조 신호도 있다:

`name the 50 capitals in the usa ?`

→ `answer(A,(capital(A),loc(A,B),const(B,countryid(usa))))`

으로 `50`은 LF에서 사라진다.

따라서 “표면에 숫자가 있다”만으로는 충분하지 않으며, 이번에 확인된 진짜 cardinal 후보는 주로 `at least one` 유형이다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R4 — 형식 문법의 정본

공식 GeoQuery FunQL 설명은 original query language를 **“basically a first-order logical form augmented with some higher-order predicates or meta-predicates”**라고 설명하며, implicit-set quantification 같은 것을 처리한다고 한다. FunQL은 variable-free이며 underlying first-order logical forms로 직접 번역되도록 설계됐다.

원 Prolog LF 자체에서 `count`, `most`, `largest`, `smallest` 같은 higher-order/meta predicate가 사용된다. 하지만 위 `at least one`의 `one`은 수치 상수 1이라기보다 existential structure로 환원된다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R5 — 수작업 저작 여부

GeoQuery dissertation은 880 English questions 중 원래 250개를 undergraduate language class에서 수집했고 **“manually translated into a logical query language based on Prolog”**했다고 명시한다. 이후 630개는 undergraduate AI class 및 CHILL web-interface 사용자 등에서 추가됐다.

따라서 적어도 original 250의 LF gold가 수작업 번역이라는 것은 명시적으로 확인된다. 880 전체의 세부 annotation workflow가 항목별로 동일했는지는 이 구절만으로 완전히 증명하지 않는다.

**확신도:** original 250 매우 높음; 전체 880 중 추가 630의 세부 provenance 중간.
**BLOCKED:** 부분적으로.

### R6 — 문장 단위 1:1 여부

공식 배포 설명부터 `sentences and their corresponding logical queries`라고 되어 있고, 실제 `geoqueries880` 파일도 `parse([tokens], answer(...)).` 형식으로 한 utterance와 한 logical query를 묶는다.

**확신도:** 높음.
**BLOCKED:** 아니오.

---

## 5. ATIS

### R2 — 라이선스

LDC 공식 catalog에서 ATIS0 Complete의 License는 명시적으로:

`LDC User Agreement for Non-Members`

이다.

실제 agreement는 데이터 사용을 **“only for non-commercial linguistic education, research and technology development”**로 제한하고, research group 밖으로 publish/retransmit/disclose/copy/reproduce/redistribute하는 것을 원칙적으로 금지한다.

따라서 일반적인 permissive open-data license가 아니다.

후대 XSemPLR도 ATIS에 대해 별도로 `ATIS, LDC User Agreement`라고 기재한다.

현재 조사한 공개 GitHub Lambda mirror 자체가 원 ATIS data를 재배포할 권한에 관한 독립적인 명시문을 갖는지는 확인하지 못했다.

**확신도:** 원 LDC 라이선스 매우 높음.
**BLOCKED:** 공개 mirror의 독립 재배포 권리 = 예.

### R3 — 기수 양화 실재 신호

후대 Lambda-LF mirror에서 다음이 확인된다.

`i want a flight ... that at least has one stop`

→ `( > ( stops $0 ) 1:i )`

`list all flight ... with at least 3 stop`

→ `( > ( stops $0 ) 3:i )`

여기에는 중요한 literal 사실이 있다. 표면은 **at least 1 / at least 3**인데 LF 비교자는 `>`이다. 통상적인 `at least N = ≥N`으로 고쳐 읽지 않았다.

또한:

`what are two ... flight ...`

에서는 LF에 2가 없고,

`list three earliest flight ...`

에서는 `argmin`만 있고 3이 사라진다.

따라서 ATIS의 표면 cardinal 표현이 항상 LF에 보존되는 것은 아니다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R4 — 형식 문법의 정본

원 ATIS Pilot corpus에서 의미 정본은 **reference SQL**이다. LDC documentation은 ANSI-standard SQL expression이 reference answer를 만든 것이며 해당 SQL이 subject query interpretation의 **“final word”**라고 명시한다.

반면 위의 Lambda 표현은 후대 semantic-parsing benchmark용 변환 표현이다. 따라서 ATIS를 사용할 경우 최소한 다음 두 층을 분리해야 한다.

**원 gold:** utterance → reference SQL.
**후대 adapter/derived representation:** SQL 또는 기존 MR → Lambda/FunQL 등.

이번 조사에서 확인한 cardinal 실물은 후자의 Lambda mirror이다. 따라서 원 reference SQL에서 같은 cardinal 항목이 어떻게 적혀 있는지까지는 **BLOCKED** 상태다.

**확신도:** 원 SQL 정본 높음; cardinal의 원 SQL 대응 미확인.
**BLOCKED:** 부분적으로 예.

### R5 — 수작업 저작 여부

ATIS 문서는 corpus에 NLParse command와 reference SQL이 들어 있으며 잘못된 answer를 사람이 NLParse command를 수정하는 방식으로 관리했다고 설명한다. reference SQL은 query interpretation의 정본이다.

다만 조사한 현대 Lambda dataset은 원 SQL gold 그 자체가 아니라 **파생 표현**이다.

**확신도:** original reference interpretation 높음; Lambda를 수작업 gold로 보는 것은 부적절.
**BLOCKED:** 아니오.

### R6 — 문장 단위 1:1 여부

표준 semantic-parsing 변환본은 TSV 한 줄에 utterance와 Lambda LF 하나가 대응한다. 실제 mirror에서 이 구조를 직접 확인했다.

원 ATIS에는 대화·context 관련 자료도 있지만, reference-SQL scoring에서는 context-dependent query를 별도 문제로 다룬다. 따라서 사용하려는 정확한 ATIS subset에 따라 sentence-level 여부를 다시 고정해야 한다.

**확신도:** 현대 benchmark record는 높음.
**BLOCKED:** 원 배포판의 사용할 subset 결정 전에는 부분적.

---

## 6. AMRNews / AMR-BP

### R2 — 라이선스

AMR-BP repository는 명시적으로 **“All corpora are distributed under the CC-BY-NC-SA license”**라고 한다.

LICENSE 파일의 정식 제목은:

`Attribution-NonCommercial-ShareAlike 4.0 International`

이며, 실제 grant에는 licensed material과 adapted material을 **“for NonCommercial purposes only”** 복제·공유할 수 있다고 적혀 있다.

즉 **CC BY-NC-SA 4.0**이며 NonCommercial과 ShareAlike 조건이 명시적이다.

AMRNews 원문은 Folha de São Paulo 신문 기사에서 왔다. repository는 corpus 전체에 위 라이선스를 선언하지만, 신문 원문에 존재할 수 있는 제3자 권리를 별도로 감사한 자료는 이번 조사에서 찾지 않았다.

**확신도:** repository license 매우 높음.
**BLOCKED:** underlying newspaper-text rights의 별도 검증은 예.

### R3 — 기수 양화 실재 신호

실제 corpus에서 단순 cardinal이 문장과 graph 양쪽에 존재한다.

`DUAS dicas para enfrentar 2019`

→ `(d / dica ... :quant 2 ...)`

여기서 `2`는 `dica`의 수량이고, 별도의 `2019`는 date entity의 year로 구분된다. 즉 요청 정의의 **NP cardinal**과 제외 대상인 연도가 한 문장 안에서도 별도 역할로 명확히 나뉜다.

`Outros dois morreram.`

→ `(p / pessoa ... :quant 2 ...)`인 annotation instance가 있다. 같은 표면 문장에 다른 annotation variant도 존재하므로 중복/버전 구분이 필요하다.

`Duas pessoas foram presas.`

→ `(p1 / pessoa :quant 2)`

따라서 최소한 단순 cardinal `2`는 corpus 실물에서 명확하다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R4 — 형식 문법의 정본

AMR guidelines는 AMR을 sentence meaning의 directed graph로 설명하며 `:quant` relation을 정식 role 목록에 포함한다. 동시에 중요한 한계를 명시한다:

**“It does not represent quantifier scope”** 그리고 Quantifiers and scope 절에서 **“AMR does not have a deep representation for quantifiers.”**라고 한다.

수치 자체는 명확히 인코딩한다. 예를 들어 guideline의

`more than four thousand boys`

는

`(b / boy :quant (m / more-than :op1 4000))`

형식이다.

따라서 AMR의 정본상 사실은 두 가지다.

**cardinality value 표현:** 가능.
**quantifier scope의 deep representation:** 하지 않음.

이는 요청서의 scope 측정 목적과 직접 관련되는 사실이지만 여기서는 적격/부적격 판정으로 확장하지 않는다.

**확신도:** 매우 높음.
**BLOCKED:** 아니오.

### R5 — 수작업 저작 여부

repository가 AMRNews를 명시적으로:

`news texts from the Folha de São Paulo newspaper manually annotated in AMR`

이라고 설명한다.

**확신도:** 매우 높음.
**BLOCKED:** 아니오.

### R6 — 문장 단위 1:1 여부

repository의 corpus notation은 `# ::snt` 등 sentence metadata 뒤에 PENMAN AMR graph가 오고 **“A blank line separates each sentence.”**라고 명시한다.

따라서 파일 구조는 명시적인 sentence-record 단위다. 다만 위 `Outros dois morreram` 사례처럼 동일한 표면 문장이 복수 record/annotation으로 존재할 수 있으므로 corpus 전체에서 surface-string uniqueness를 가정해서는 안 된다.

**확신도:** 높음.
**BLOCKED:** 아니오.

---

## 7. FraCaS — 비교용 negative control

### R2 — 라이선스

Bill MacCartney의 배포 페이지는 자신이 올린 자료에 대해:

`stuff I'm putting in the public domain`

이라고 명시하고, 그 페이지에서 FraCaS XML/DTD를 배포한다.

그러나 그는 동시에 원 test suite가 **FraCaS Consortium, 1996**에 의해 만들어졌다고 설명한다. 따라서 이 문구가 1996 원자료의 모든 저작권까지 소급해 해소하는지에 대한 별도 원 Consortium license는 이번 조사에서 찾지 못했다.

**확신도:** MacCartney 배포판의 public-domain statement 높음.
**BLOCKED:** 원 FraCaS 권리 사슬은 예.

### R3 — 기수 양화 실재 신호

기수 양화 자체는 매우 풍부하다.

문제 15:

`At least three tenors will take part in the concert.`

문제 16:

`At most two tenors will contribute their fees to charity.`

문제 85:

`Exactly two lawyers and three accountants signed the contract.`

즉 하한·상한·정확수가 모두 실물로 존재한다.

**확신도:** 매우 높음.
**BLOCKED:** 아니오.

### R4 — 형식 문법의 정본

여기가 결정적인 negative fact다.

MacCartney가 설명하는 XML 변환은 FraCaS의 **textual inference problems**를 XML로 구조화하고 questions를 declarative hypotheses로 바꾼 것이다. 각 문제의 핵심 gold는 premise/question/hypothesis에 대한 **Yes / No / Don’t know 등 inference answer**이다.

이번 조사에서는 각 문장에 대응하는 FOL/DRS/AMR 등의 **gold formal meaning representation을 제공하는 정본**을 찾지 못했다.

따라서 요청서가 지시한 표현 그대로라면:

**형식 표상 없음 — 함의/추론 answer label이 gold.**

**확신도:** 높음.
**BLOCKED:** 아니오. 현재 확인 범위에서는 label-only라는 positive negative finding.

### R5 — 수작업 저작 여부

원 suite는 FraCaS Consortium이 만든 346개의 textual inference problem이다. MacCartney는 이를 XML로 표현하고 questions를 hypotheses로 변환하고 “cleaned things up”했다고 설명한다.

문제 자체는 사람이 설계한 test suite지만, 그것이 문장별 formal-MR gold라는 뜻은 아니다.

**확신도:** 높음.
**BLOCKED:** 아니오.

### R6 — 문장 단위 1:1 여부

단위는 **inference problem**이다. 하나 이상의 premise + question/hypothesis + answer로 구성된다. 따라서 sentence → formal representation 1:1 구조가 아니다.

**확신도:** 매우 높음.
**BLOCKED:** 아니오.

---

## 8. 비교 요약

| Source           | 정확/하한/상한 cardinal 실물 | 기수가 MR에 보존됨                                              | scope 표현                                  | 사람 저작 신호                                                | 문장-record            | 데이터 라이선스 상태                                           |
| ---------------- | -------------------- | -------------------------------------------------------- | ----------------------------------------- | ------------------------------------------------------- | -------------------- | ----------------------------------------------------- |
| **QuantML Bank** | 매우 명확                | 예: `=3`, `>2000`, `>=3`                                  | **명시적 scoping relation + semantics**      | ISA annotation task는 human; Bank item provenance 일부 미확인 | 문장 중심, 복수 reading 가능 | **BLOCKED**                                           |
| **Overnight**    | 매우 명확                | 예: `=`, `<=`, `>=` + numeric constant                    | Lambda DCS; nested quantification에는 한계 명시 | LF/canonical은 grammar 생성, natural side는 AMT             | record 1:1           | 2차 배포처 CC BY-SA 4.0; **원 authority BLOCKED**          |
| **GeoQuery**     | `at least one` 확인    | existential structure로 보존; numeral `1` 자체는 없음            | FOL/Prolog/FunQL                          | original 250 수작업 LF 명시                                  | 예                    | **GPL 2.0 공식**                                        |
| **ATIS**         | `at least 1/3` 등     | 현대 Lambda에 수치 있음. 단 `at least N` → `>N` literal mismatch | 원 정본은 SQL                                 | 원 reference interpretation 관리; Lambda는 derived          | benchmark는 예         | **LDC User Agreement**                                |
| **AMRNews**      | 단순 cardinal 다수 확인    | `:quant 2` 등                                             | **정본이 quantifier scope 비표상을 명시**          | **manually annotated**                                  | 예                    | **CC BY-NC-SA 4.0 공식**                                |
| **FraCaS**       | 매우 풍부                | 해당 formal MR이 없음                                         | 없음                                        | 사람이 설계한 inference suite                                 | problem-level        | MacCartney 배포 “public domain”; 원 rights chain BLOCKED |

## 9. R4 관점에서의 조사 우선순위

이것은 **적격성 판정이 아니라**, 후속 실측 전에 adapter 문법을 얼마나 명확하게 만들 수 있는지에 따른 사실 기반 검증 순서다.

**1 — QuantML / Quantification Bank.**
기수 관계, 수치 상수, participant/entity, distributivity, scope, 조합적 semantics가 한 정본에 들어 있다. 현재 가장 큰 미확인은 Bank 데이터 자체 라이선스와 item-level provenance다.

**2 — Overnight.**
정확수/하한/상한을 LF가 실제로 인코딩하며 문장-LF record가 많다. 다만 LF가 grammar-generated이고 crowdsourced paraphrase에 noise가 있으며, 원 저자의 dataset-specific license statement를 확보하지 못했다.

**3 — GeoQuery.**
공식 GPL 2.0, 수작업 Prolog LF, 880 sentence-query pairs라는 provenance가 매우 명료하다. 현재 corpus에서 확인된 cardinal signal은 주로 `at least one`이고 그것도 explicit numeral operator가 아니라 existential structure로 의미화된다.

**4 — AMRNews.**
라이선스·수작업·sentence→graph 구조는 가장 깨끗한 편이고 `:quant 2` 실물도 있다. 반면 AMR 문법 자체가 quantifier scope를 깊게 표현하지 않는다고 명시한다.

**5 — ATIS.**
원 formal gold는 reference SQL이라는 정본이 존재하지만, 공개 Lambda cardinal 예는 파생 표현이며 `at least N`을 `>N`으로 인코딩한 literal mismatch도 보인다. 원 SQL의 해당 항목을 직접 맞춰 보는 추가 확인이 필요하다.

**6 — FraCaS.**
cardinal linguistic coverage는 좋지만 확인된 gold는 inference label이고 sentence-level formal semantics가 아니다.

## 10. BLOCKED / 실패 경로 기록

| 항목                                           | 시도 결과                                                                                                        | 판정                               |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------------------- |
| Quantification Bank 데이터 license/copyright    | 예제 index와 관련 문서 확인. 논문 CC BY 4.0 및 ISO 문서 All Rights Reserved는 찾았으나 **Bank examples 자체 적용 라이선스 문구 미발견**      | `BLOCKED`, “라이선스 없음”으로 판정하지 않음   |
| QuantML Bank item-level authoring provenance | ISA human annotation task는 확인. 현재 Bank 각 PDF에 annotator/provenance metadata는 찾지 못함                           | `BLOCKED`                        |
| Overnight 원 데이터 license                      | 후대 XSemPLR은 `Overnight, CC BY-SA 4.0`이라 명시. 원 Stanford 쪽 dataset-specific license authority를 이번 조사에서 확보하지 못함 | `BLOCKED`                        |
| GeoQuery 공식 데이터                              | 공식 UT 페이지 정상 접근, GPL 2.0 명시                                                                                  | 미차단                              |
| GeoQuery 구 논문/학위 URL 일부                      | 이전 공식 페이지에서 따라간 오래된 publication 경로 일부가 404였음; 현재 data page와 dissertation 사본은 별도 접근 가능                        | publication-link 실패일 뿐 데이터 부재 아님 |
| ATIS 원 라이선스                                  | LDC catalog 및 1-page User Agreement 직접 확인                                                                    | 미차단                              |
| ATIS 공개 Lambda mirror의 재배포 권리                | mirror 내용은 접근 가능하나 자체 데이터 권리 문구 확인 못함                                                                        | `BLOCKED`                        |
| ATIS cardinal의 원 reference SQL               | Lambda pair는 확인했으나 같은 utterance의 원 SQL까지 직접 대조하지 못함                                                          | `BLOCKED`                        |
| AMRNews                                      | repository, corpus file, LICENSE 모두 직접 확인                                                                    | 미차단                              |
| FraCaS XML                                   | MacCartney download page는 확인. 일부 XML/DTD 직접 browser fetch는 MIME 처리 문제로 막힌 적 있음; PDF/배포 설명으로 corpus 구조와 사례 확인 | fetch `BLOCKED` ≠ 자료 없음          |
| FraCaS original Consortium license           | MacCartney의 public-domain statement는 확인했으나 1996 원 Consortium의 별도 rights statement 확보 못함                      | `BLOCKED`                        |

### 최종 사실 요약

이번 조사에서 **“기수 표현이 자연어와 형식 표상 양쪽에 실제로 존재한다”**는 것을 가장 직접적으로 확인한 자원은 QuantML Bank, Overnight, AMRNews, ATIS의 후대 Lambda 표현이다. GeoQuery에서는 `at least one`이 존재하지만 수치 1이 독립 cardinal operator로 남지 않고 existential structure로 환원된다. FraCaS는 하한·상한·정확수 예가 풍부하지만 요청서가 경고한 대로 **formal sentence semantics가 아니라 inference answer가 gold**다.

반대로 현재 조사만으로 확정할 수 없는 핵심 사실은 **Quantification Bank 데이터 자체의 라이선스와 item-level human provenance**, **Overnight 원 배포처의 dataset-specific 라이선스**, 그리고 **ATIS Lambda cardinal 항목과 original reference SQL의 직접 대응**이다. 이 세 항목은 부재 판정하지 않고 `BLOCKED`로 유지한다.

이 보고서는 요청대로 후속의 ≥3건 실측, 표면 대명사·고유명 필터, subject 방언 표현 가능성, 측정 가능성 gate 등은 수행하지 않았다. 그것들은 운영 세션의 별도 기계 실측 범위다.
<!-- VERBATIM-END -->

---

## 수신 검증 기록 (2026-08-23, 운영 세션)

조사가 명시적으로 우리 범위로 남긴 것(방언 표현 가능성·적격 하한·필터)을
실측했다. 조사의 사실 보고 자체를 재조사하지는 않았다(웹 실측은 조사
채널의 소관 — 우리가 중복하면 조사의 BLOCKED 판정을 흐린다).

### V1 — 보고된 표상이 동결 방언(6종)으로 표현 가능한가 → **전부 불가**

동결 방언 = `forall/exists/and/pred/not/implies`, 항 = var|entity.
**기수 constructor가 없다.**

| source | 보고된 MR | 판정 |
|---|---|---|
| QuantML | `\|X\|=3`, `\|X\|>2000`, `\|Y\|≥3` | 집합 크기 + 부등호 — 방언 밖 |
| Overnight | `SW.filter(>=, (number 3 assist))` | 비교자 + 수치 상수 — 방언 밖 |
| ATIS | `( > ( stops $0 ) 1:i )` | 수치 비교 — 방언 밖 |
| AMRNews | `(p1 / pessoa :quant 2)` | `:quant` 수치 role — 방언 밖 |
| GeoQuery | `answer(A,(state(A),loc(B,A),major(B),river(B)))` | **방언 내 표현 가능** — 단 수치가 사라져 기수 측정이 아니다 |
| GeoQuery | `answer(A,count(B,(…),A))` | `count` meta-predicate — 방언 밖 |
| FraCaS | (형식 표상 없음) | 오라클 불가 |

**귀결**: 기수를 MR에 보존하는 4 source 전부 수치 상수·집합 크기 연산을
쓴다. 즉 **기수 층을 채우려면 subject 방언에 기수 표현을 추가해야 한다** —
D-28이 "declared boundary 확대가 아니라 coverage 복구"라고 정리한 바로 그
변경이며, 그 설계(어떤 형태로? 수치 상수? 비교자? 집합 크기?)는 아직
판정되지 않았다.

### V2 — 회신은 요청서 **개정 1** 기준이다

보고서에 R3'(비례) 절이 없고, 비례 표현(`most of` / `Most N`) 실물 예가
0건이며, 비교 요약표에 비례 열이 없다. 개정 2(비례 범주 추가)가 공유
전이었거나 반영되지 않았다. **비례 재료(적격 ≥1)는 여전히 미조사**다.

### V3 — AMRNews는 언어가 다르다

동결 template은 "the following **English** sentence"를 지시한다
(`stage2_prompt_template_v4.md:13`). AMRNews/AMR-BP는 **Brazilian
Portuguese**(Folha de São Paulo)다. 조사가 언어를 명시했고, 우리 실험에는
쓸 수 없다 — 조사 범위 밖이라 조사가 판정하지 않은 부분을 운영 세션이
판정한다. 부수로 AMR 정본이 **quantifier scope를 표상하지 않는다**고
명시하는 것도 우리 estimand와 직접 충돌한다.

### V4 — 조사가 확인한 것 중 우리 요청서의 예고가 적중한 것

- **FraCaS = 라벨 전용**: 요청서 R4가 "함의 라벨뿐이면 형식 표상 없음으로
  명기하라"고 예고했고 조사가 그대로 확인했다(346 inference problems,
  gold = Yes/No/Unknown). 후보에서 탈락.
- **URL 원문 그대로 시도**: GeoQuery 구 publication 경로 일부 404를
  "데이터 부재"로 바꾸지 않고 `publication-link 실패`로 분리해 보고했다 —
  요청서 경고 2가 작동했다.
- **BLOCKED와 없음의 구분**: Quantification Bank 데이터 라이선스, item-level
  provenance, Overnight 원 라이선스, ATIS Lambda 재배포 권리, ATIS 원 SQL
  대응 — 5건을 부재 판정 없이 BLOCKED로 유지했다.

### V5 — 각 후보의 남은 차단 요인 (운영 세션 정리)

| 후보 | 차단 요인 |
|---|---|
| QuantML Bank | **데이터 라이선스 BLOCKED** + item provenance BLOCKED + 방언 표현 불가. scope를 명시 표상하는 유일 후보라는 점은 강점 |
| Overnight | 원 라이선스 BLOCKED(2차 배포는 CC BY-SA 4.0) + LF가 grammar 생성(요청서 R5상 후보 가능) + 방언 표현 불가 + noisy example 보고 |
| GeoQuery | 라이선스 GPL 2.0 명확·수작업 LF 명확이나 **기수가 ∃로 환원돼 기수 측정이 성립하지 않는다** |
| ATIS | LDC User Agreement(비상업·재배포 금지) + 공개 mirror 재배포 권리 BLOCKED + `at least N`→`>N` literal mismatch + 방언 표현 불가 |
| AMRNews | **언어 불일치(포르투갈어)** + AMR 정본이 scope 비표상 명시 + 방언 표현 불가 |
| FraCaS | 형식 표상 없음 |

**즉 조사 결과만으로는 기수 층을 채울 수 없다.** 어느 후보를 쓰든
(i) 방언 확장 설계 + (ii) 라이선스 BLOCKED 해소 또는 GPL/CC 후보 채택 +
(iii) adapter 신설이 함께 필요하고, 그중 (i)은 판정 사안이다.

수신 텍스트의 sha256 (BEGIN 다음 개행 ~ END 직전, UTF-8):
`VERBATIM_SHA256: ebce2d7871679e615b3b5c3bb270b1a0f324cc800eb4b5b4c23e9715e67b5cbc`
