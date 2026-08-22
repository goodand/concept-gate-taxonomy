# RESEARCH RESULT — 다중 양화 제2 source 후보 조사 (수신 verbatim)

- 수령: 2026-08-23, 사용자 경유 (조사용 agent — openai_web_gpt 환경)
- 요청 원문: `RESEARCH_REQUEST_second_source_multiquant.md`
- 검증: 수령 당일, 말미 "수신 검증 기록" — FOLIO raw를 이 환경에서 직접
  fetch해 **회신이 미측정으로 남긴 census까지 해소**. WikiSem 후보는 우리
  선행 실측(기사 단위 LF, D-21 부적격)과 충돌 — 검증 기록에 명시
- 아래 본문은 수신 그대로이며 편집하지 않는다

---

## 조사 원문 (verbatim)

요청서의 경계대로 **적격성 최종 판정은 하지 않고**, R1–R5 사실조사 결과만 정리합니다. 조사 대상은 “문장 단위 formal representation + 2개 이상 양화사의 scope 상호작용”이고, 라이선스는 추정하지 않으며 BLOCKED와 “없음”을 구분했습니다.  

## 요약

| 후보                                     | 표상                          | 다중 양화 신호                                    | 공개 artifact 상태                            | 라이선스 상태                                       | 조사 확신도           |
| -------------------------------------- | --------------------------- | ------------------------------------------- | ----------------------------------------- | --------------------------------------------- | ---------------- |
| **WikiSem / Rasmussen & Schuler 2020** | 완전한 typed λ-calculus LF     | 매우 강함: 표본 문장의 **45%**가 ≥1 scope interaction | **직접 다운로드 가능**                            | 논문 CC-BY-NC; **data artifact 자체 문구 BLOCKED**  | 매우 높음            |
| **FOLIO**                              | FOL                         | 직접 `∀∃`, `∀∀∃` 예 확인                         | **GitHub v0.0 직접 다운로드 가능**; 현 HF판 gated   | GitHub **CC-BY-SA-4.0**, 현 HF **MIT** — 서로 다름 | 매우 높음            |
| **FDA CFR AST**                        | scope를 담은 restricted LF/AST | 직접 `any ≫ some`, `R(any) ≫ a` 확인            | 논문 공개; **195문장 artifact locator BLOCKED** | 논문 CC BY-NC-SA 3.0; **data license BLOCKED**  | 논문 사실 높음         |
| **QuanText**                           | scope partial order / DAG   | 매우 강함: 500 annotated, 3.5 chunks/sentence   | 논문 공개; **corpus locator BLOCKED**         | 논문 CC BY-NC-SA 3.0; **data license BLOCKED**  | annotation 사실 높음 |
| **AnderBois et al. LSAT**              | relative-scope ordering     | 매우 강함: 680문장 모두 2–8 quantified NPs          | **permission required**                   | 원 corpus copyright restriction 명시             | 높음               |

핵심적으로 현재 조사에서 **“다운로드 가능한 문장+완전한 논리식”까지 동시에 직접 확인된 것은 WikiSem과 FOLIO**입니다. 나머지 셋은 각각 표상 완전성 또는 artifact 접근성 문제가 사실로 확인됩니다.

---

# 1. WikiSem — Rasmussen & Schuler, *A Corpus of Encyclopedia Articles with Logical Forms*

### R1 — 자원·형식·규모·접근

OSU 연구팀이 Simple English Wikipedia 약 **2,000문장**을 **typed lambda calculus**로 번역한 corpus입니다. 논문은 이 자원을 명시적으로 quantifier-scope-disambiguation용으로 제시하며 “large number of quantifiers and interesting scoping configurations”라고 기술합니다. ([ACL Anthology][1])

현재 OSU 다운로드 페이지에는 v0.3 semantic annotation이 `wikisemC1.logic...`부터 C7까지 실제 파일로 공개돼 있습니다. 또한 CASP markup에 **quantifier scope `-s, -t, -u` tags**가 포함된다고 배포처가 명시합니다. ([Department of Linguistics][2])

[WikiSem OSU downloads](https://linguistics.osu.edu/schulerlab/dwnload?utm_source=chatgpt.com)
[Rasmussen & Schuler 2020 paper](https://aclanthology.org/2020.lrec-1.132/?utm_source=chatgpt.com)

**BLOCKED:** 없음 — locator와 logic 파일 존재 자체는 확인됨. 다만 대용량 logic 파일의 본 조사 브라우저 직접 fetch에는 크기 제한이 있었음. 이것은 원 자원 접근 불능이 아니라 조사 도구 제한입니다.

**확신도:** 높음.

### R2 — 라이선스

논문 PDF 상단의 verbatim 표기는:

> “licensed under CC-BY-NC”

입니다. ([ACL Anthology][1])

그러나 **OSU의 corpus download 페이지 자체에서는 annotation artifact에 적용되는 별도 LICENSE 문구를 찾지 못했습니다.** 논문은 Simple English Wikipedia의 Creative Commons license가 corpus distribution에 유리하다고만 설명합니다. 이를 annotation artifact의 라이선스로 자동 전이하면 요청서의 “라이선스 추정 금지”에 걸리므로:

* 논문 라이선스: **CC-BY-NC — 확인**
* 원문 Wikipedia licensing 관련 언급: **확인**
* `wikisem*.logic` artifact 자체의 명시 라이선스: **BLOCKED**

로 분리합니다. ([ACL Anthology][1])

### R3 — 다중 양화 실재

논문에 실제 LF가 붙은 예가 있습니다.

문장:

> “The number of bytes in each memory is a whole power of two.”

표상에는 `all` 아래에 여러 `some`이 중첩됩니다:

```text
all (λx prop memory x)
  (λx some (λn prop number n, ... )
    (λn some (λm prop number m, ... )))
```

즉 실제 sentence/LF pair에서 복수의 양화가 구조적으로 중첩됩니다. ([ACL Anthology][1])

규모 신호는 더 강합니다. 첫 100개 article에서 **전체 문장의 45%가 적어도 한 쌍의 quantifier interaction**, 거의 **20%가 multiple interactions**을 갖습니다. 첫 1,000문장 뒤에는 33×3문장을 독립적으로 두 번째 markup하여 IAA도 측정했습니다. ([ACL Anthology][1])

논문 결론도 거의 절반이 multiple scopally interacting quantifiers로 annotated됐다고 재확인합니다. ([ACL Anthology][1])

**확신도:** 매우 높음. “5건 이상 공급 가능성”에 대해서는 corpus 자체의 보고 수치가 매우 강한 규모 신호를 제공합니다. 최종 5건 추출은 요청서가 예정한 별도 기계 실측 사항입니다.

### R4 — 형식 문법 정본

논문 §3이 typed λ-calculus의 타입과 생성 규칙을 명시합니다.

* entity `e`
* truth value `t`
* function `α → β`
* constants
* variables
* λ-abstraction
* application

으로 구성됩니다. ([ACL Anthology][1])

또 OSU Resources 페이지가 별도의 **“Cued Association Sentence Processing Markup [pdf]” annotation guidelines**를 정식 documentation으로 링크합니다. ([Department of Linguistics][3])

따라서 constructor/adapter 측 정본 후보는 **Rasmussen & Schuler 2020 §3–5 + CASP annotation guidelines**로 특정 가능합니다.

### R5 — 수작업 저작·검수

자동 parse 뒤 corpus를 **hand corrected**하고, annotator가 직접 anaphor antecedent와 **scope parent**를 지정합니다. 자동 well-formedness validation 이후에도 hand correction을 수행합니다. ([ACL Anthology][1])

오류 분석 뒤에는 annotators가 서로의 작업을 정기적으로 review하도록 workflow를 바꾸고 guideline도 재작성했습니다. ([ACL Anthology][1])

**독립성 관련 확인된 사실:** OSU 연구팀 제작이며 Simple English Wikipedia를 source text로 삼습니다. 조사한 논문·배포 페이지에는 PMB에서 변환했다는 기술이 발견되지 않았습니다. 단, **“PMB-derived가 아니라는 명시 선언” 자체를 발견한 것은 아니므로 그 부정명제까지 확정하지 않습니다.**

---

# 2. FOLIO

### R1 — 자원·형식·규모·접근

FOLIO는 natural language와 **First-Order Logic annotation**을 나란히 갖습니다. 논문 abstract 기준 **1,430 examples / 487 premise sets**이며, NL–FOL pair 자체를 translation dataset으로 설명합니다. 

구 GitHub v0.0은 공개 repository이고 `folio-train.jsonl`, validation 파일 등이 존재합니다. 각 record에는 명시적으로:

* `premises`
* `premises-FOL`
* `conclusion`
* `conclusion-FOL`

필드가 있습니다. ([GitHub][4])

[FOLIO GitHub v0.0](https://github.com/Yale-LILY/FOLIO?utm_source=chatgpt.com)
[current Yale NLP FOLIO distribution](https://huggingface.co/datasets/yale-nlp/FOLIO?utm_source=chatgpt.com)

참고로 논문 abstract는 1,430이라고 하지만 paper의 다른 표에서는 1,435라는 버전/집계 차이가 있어, 규모는 **1.43k급**으로 기록하는 것이 안전합니다.

### R2 — 라이선스

구 GitHub LICENSE의 verbatim heading:

> “Attribution-ShareAlike 4.0 International”

및

> “Creative Commons Attribution-ShareAlike 4.0 International Public License”

가 확인됩니다. ([GitHub][5])

반면 **현재 Hugging Face 배포본은 `License: mit`**라고 표시되며 동시에:

> “You need to agree to share your contact information to access this dataset”

라고 되어 있습니다. 즉 repository는 공개적으로 보이지만 파일 접근 조건 수락이 필요합니다. ([Hugging Face][6])

따라서 사실관계는:

**GitHub v0.0 = CC-BY-SA-4.0 / 공개 파일**,
**현 HF판 = MIT metadata / gated access**

입니다. 두 배포본의 라이선스 차이를 제가 임의로 조정·해석하지 않습니다.

### R3 — 다중 양화 실재

이번 조사에서는 **원 GitHub raw v0.0에서 직접** 확인했습니다.

예 1:

> “Holding companies hold several companies.”

Gold FOL:

```text
∀x ∃y (HoldingCompany(x) → Company(y) ∧ Holds(x, y))
```

즉 `∀x`와 `∃y`가 한 formula 안에 있습니다. 

예 2는 더 강합니다.

> “If a universal language exists, then for every two people …”

Gold:

```text
∀x ∀y (
  ∃z (Know(x,z) ∧ Know(y,z) ∧ UniversalLanguage(z))
  → Communicate(x,y)
)
```

`∀x ∀y ∃z`가 한 식에 직접 중첩돼 있습니다. 

또 raw train에는 예컨대 werewolf 문장에 `∀x ∃y (...)`가 직접 존재합니다. 따라서 **mixed-quantification 실재 자체는 BLOCKED가 아닙니다.** 

다만 이번 단계에서는 전체 train/validation에 대해 “사용 가능한 mixed-scope 항목이 정확히 몇 건인가”를 census하지 않았으므로 그 **정확 수는 미측정**, 요청서 표현대로 별도 기계 실측 영역입니다.

### R4 — 형식 문법 정본

논문 Appendix E가 FOL definition을 직접 제시합니다. 포함 operator는:

`¬, ∧, ∨, →, ∀, ∃, =`

이며 Russell & Norvig를 기준으로 삼고, n-place predicate 사용 및 Davidsonian/neo-Davidsonian semantics를 사용하지 않는다는 modeling convention도 명시합니다. 

따라서 adapter 계약의 정본 위치는 **FOLIO paper Appendix E, 특히 E.2–E.3**입니다.

### R5 — 수작업 저작 여부

여기는 증거가 매우 명확합니다. 논문은:

> “All stories and FOL annotations in FOLIO are written and reviewed by expert annotators”

라고 합니다. 총 6단계 workflow와 **980 man-hours**도 보고합니다. WikiLogic은 Wikipedia를 seed로 하되 **새 story를 template 없이 from scratch** 쓰고, parallel FOL도 annotator가 작성합니다. 

HybLogic은 논리적으로 유효한 template을 먼저 조합하는 hybrid construction을 쓰므로 **전체가 순수 자유작문인 것은 아닙니다**. 하지만 최종 artifact는 FOLIO 연구팀이 설계·작성·검수해 공개한 제3자 dataset이라는 사실까지 확인됩니다.

---

# 3. Dinesh, Joshi & Lee 2011 — FDA CFR AST corpus

### R1 / R4 — 자원과 표상

FDA Code of Federal Regulations Section 610에서 **195문장**을 Abstract Syntax Tree(AST)라는 logical-form variant로 annotation했습니다. determiner, modal, negation, VP modifier 등이 scope-taking operator입니다. ([ACL Anthology][7])

중요한 제한도 저자들이 직접 밝힙니다. AST는 logic으로 가기 전 intermediate representation이며, 결론에서:

> “we do not attempt to translate all the way to logic.”

이라고 명시합니다. ([ACL Anthology][7])

즉 **scope-resolved restricted LF는 존재하지만 FOL/λ-calculus와 같은 완전한 sentence logic은 아닙니다.** 이것은 BLOCKED가 아니라 형식 자체의 확인된 특성입니다.

정본은 논문 §1–4이며, 더 자세한 annotation guideline/IAA는 저자가 **Dinesh 2010**을 가리킵니다. ([ACL Anthology][7])

### R2 — 라이선스와 접근

ACL Anthology상의 **논문**은 pre-2016 material이므로:

> “Creative Commons Attribution-NonCommercial-ShareAlike 3.0 International License”

로 배포됩니다. ([ACL Anthology][8])

하지만 별도의 **195문장 AST annotation artifact 다운로드 위치 및 artifact LICENSE는 이번 조사에서 발견하지 못했습니다.**

따라서:

* 논문: 공개, license 확인
* corpus artifact locator: **BLOCKED**
* corpus artifact license: **BLOCKED**

입니다. “없음”으로 판정하지 않습니다.

### R3 — 다중 양화 실재

논문 실물 example에:

> “Samples of any lot of a licensed product …”

가 나오며, AST에서 implicit determiner가 `some`으로 해석됩니다. 저자 설명대로:

```text
any ≫ some
R(any) ≫ a
```

입니다. 즉 최소 `any / some / a` 사이의 구조적 scope 관계를 직접 확인할 수 있습니다. ([ACL Anthology][7])

또 corpus에는 **277 determiner instances**가 있고, universal 74, existential 12 등으로 보고되어 scope material 규모 자체는 충분히 큽니다. ([ACL Anthology][9])

### R5 — 수작업 여부

195문장 대부분은 **한 annotator가 annotation**, 그중 32문장은 두 번째 annotator가 별도로 annotation했습니다. ([ACL Anthology][7])

**확신도:** 내용/형식/수작업은 높음. 독립 corpus artifact 접근·license는 BLOCKED.

---

# 4. QuanText

### R1 / R3 — 규모와 실제 scope gold

University of Rochester 계열입니다. 원 논문은 core corpus 약 **500문장**, crowdsourcing으로 추가 약 2,000문장을 수집했으며, core 500이 annotation됐다고 보고합니다. 문장당 평균 **3.9 scopal terms**입니다. 100문장은 3명의 linguistics-background annotator가 annotation했습니다. ([ACL Anthology][10])

2013 실험판 QuanText는 **500 sentences / 1,750 chunks / 평균 3.5 chunks per sentence**, 그중 1,700이 NP chunks이고 plural 320개가 implicit universal을 추가합니다. ([ACL Anthology][11])

실제 예:

> “Replace every line in the file ending in punctuation with a blank line.”

Gold scoping:

```text
(2 > 1 > 4; 1 > 3)
```

처럼 주어집니다. `i > j`는 i가 j보다 wide scope라는 뜻이고, gold는 **annotators’ preferred scoping을 partial order/DAG**로 나타냅니다. ([ACL Anthology][11])

### R4 — 형식 문법의 성격

QuanText가 말하는 “full scope information”은 **모든 scopal-element pair의 scope interaction을 labeling**한다는 뜻입니다. predicate-argument semantics 전체를 λ-term이나 FOL로 쓰는 것이 아닙니다. ([ACL Anthology][10])

따라서 정본은:

* Manshadi, Allen & Swift 2011 §4: annotation relation 정의
* Manshadi, Gildea & Allen 2013 §2: partial-order/DAG formalization

입니다. ([ACL Anthology][11])

이 사실은 constructor 관점에서 중요합니다. **scope gold는 매우 풍부하지만 full sentence LF는 아닙니다.**

### R2 — 라이선스·접근

2011/2013 **논문**은 ACL 배포 정책상 CC BY-NC-SA 3.0입니다. ([ACL Anthology][12])

그러나 이번 조사에서 original QuanText corpus의 살아 있는 공식 download locator와 별도 artifact license를 찾지 못했습니다.

* corpus locator: **BLOCKED**
* corpus license: **BLOCKED**
* 논문 license: 확인됨

동명의 현대 GitHub 프로젝트가 검색되지만 이 corpus와 무관하므로 locator로 사용하지 않았습니다.

### R5 — 수작업 여부

Mechanical Turk에서 얻은 문장은 **모두 manual review**를 거쳤고, 자동 NP chunking 뒤에도 사람이 chunking 오류를 수정합니다. 그 후 chunked sentences를 annotator에게 넘겨 scope를 annotation합니다. ([ACL Anthology][10])

즉 gold scope는 human annotation입니다.

---

# 5. AnderBois–Brasoveanu–Henderson LSAT scope corpus

### R1 / R3 — 규모

후속 정밀 분석 논문이 원 2012 corpus를 **680 LSAT logic-puzzle sentences with multiple quantified NPs**라고 명시합니다. 모든 문장에 2–8개의 quantified NP가 있습니다. ([OUP Academic][13])

분포는:

| Quantifier 수 | 문장 수 |
| -----------: | ---: |
|            2 |  450 |
|            3 |  168 |
|            4 |   47 |
|            5 |    7 |
|            6 |    5 |
|            7 |    2 |
|            8 |    1 |

입니다. ([OUP Academic][13])

실제 예:

> “Hannah visits at least one city in each of the three countries.”

에 대해 세 quantified NP가 numerical scope tag를 가지며 최종 관계는:

```text
q3 > q2 > q1
```

로 분석됩니다. ([OUP Academic][13])

따라서 다중 양화의 **실재·밀도는 매우 명백**합니다.

### R4 — 표상의 성격

각 sentence는 quantified NP들 사이의 **relative scope**로 annotation됩니다. 후속 formalization은 pair마다:

```text
q1 > q2
q2 > q1
q1 ; q2      # incomparable
```

세 관계를 사용합니다. ([OUP Academic][13])

그러므로 QuanText와 마찬가지로 **scope ordering gold이지 full sentence predicate-logic LF는 아닙니다.**

### R2 — 접근·라이선스

이 후보는 BLOCKED와 구분할 수 있습니다. 현대 재사용 repository가 원 2012 dataset에 대해 명시적으로:

> “requires permission from copyright holders”

라고 밝히며 copyright holder로 **Law School Admission Council와 Adrian Brasoveanu**를 지목하고, permission을 얻은 뒤 저자에게 연락하여 data를 받을 수 있다고 설명합니다. ([GitHub][14])

따라서:

* 접근: **restricted / permission route known**
* BLOCKED: **아님**
* open artifact: **아님**

후속 2024 논문 자체는 CC BY-NC 4.0이지만 이것은 원 LSAT corpus의 라이선스가 아닙니다. ([OUP Academic][13])

### R5 — human annotation

Rasmussen & Schuler의 survey는 AnderBois et al.이 **multiple annotators가 각 item을 code**하도록 하여 품질을 높였다고 명시합니다. ([ACL Anthology][1])

원 annotation workflow의 세부 guideline 전체는 이번 조사에서 직접 회수하지 못했으므로 **세부 R5는 partial BLOCKED**로 둡니다.

---

# 요청서에 명시된 두 계열 추가 확인

### FraCaS

MacCartney 배포본은 **346 textual inference problems**이며 XML로 변환된 test suite입니다. 배포 페이지는 자신의 공개 material을 “public domain”이라고 표현합니다. ([스탠포드 자연어 처리 그룹][15])

하지만 이 자원의 gold는 premise/question에 대한 **yes/no/unknown entailment judgment** 중심입니다. 요청서가 명시한 대로 entailment label은 sentence formal representation으로 간주하지 않으므로, 여기서는 **“형식 표상 없음(요청서가 요구하는 의미에서)”**입니다. 이는 BLOCKED가 아닙니다. 

### Groningen / GMB 계열

GMB는 public-domain English text에 syntactic/semantic representations를 제공하고 quantifier scope도 대상으로 삼습니다. 다만 GMB 자체가 NLP tools/Boxer를 사용한 **bootstrapping approach**로 approximate gold를 만든다고 설명합니다. ([Rug Let][16])

더 중요한 lineage 사실은 PMB 공식 페이지가 자신을:

> “building upon the Groningen Meaning Bank”

라고 명시한다는 점입니다. ([Parallel Meaning Bank][17])

또 Evang & Bos의 GMB scope subset은 456개 example이지만 해당 연구 자체가 **narrowly selected syntax + purely binary annotation**이라고 기술됩니다. ([ACL Anthology][1])

여기서도 제가 독립성 판정을 내리지는 않습니다. 다만 요청서의 `not_derived_from_PMB` / `different_corpus_authority` 검증에 필요한 **직접적인 계보 사실**은 이것입니다.

---

## 운영 세션으로 넘길 수 있는 현재 상태

현재 **바로 별도 기계 실측을 걸 수 있는 locator**는 두 개가 가장 명확합니다.

1. **WikiSem v0.3 `*.logic` files** — full typed λ-calculus, human scope annotation, multi-scope density 수치까지 이미 논문에 있음. 단 **artifact 자체 license wording은 BLOCKED**. ([Department of Linguistics][2])
2. **FOLIO GitHub v0.0 JSONL** — NL과 FOL이 같은 record에 있고, raw artifact에서 `∀∃`/`∀∀∃` 실물을 직접 확인함. GitHub v0.0 license도 명시되어 있음. 다만 현재 HF판은 **MIT + gated**라 배포 버전별 provenance를 분리해야 합니다. ([GitHub][4])

FDA AST와 QuanText는 **논문에서 다중 scope gold의 실재는 확인되지만 corpus artifact locator/license가 BLOCKED**, LSAT는 locator 문제가 아니라 **명시적 permission restriction**입니다. 따라서 이 단계에서 “없음”으로 처리할 후보는 없습니다. FraCaS만 요청서 정의상 **formal sentence representation이 없는 것이 확인된 경우**입니다.

[1]: https://aclanthology.org/2020.lrec-1.132.pdf "A Corpus of Encyclopedia Articles with Logical Forms"
[2]: https://linguistics.osu.edu/schulerlab/dwnload "Downloads | Department of Linguistics"
[3]: https://linguistics.osu.edu/schulerlab/resources "Resources | Department of Linguistics"
[4]: https://github.com/Yale-LILY/FOLIO "GitHub - Yale-LILY/FOLIO · GitHub"
[5]: https://github.com/Yale-LILY/FOLIO/blob/main/LICENSE "FOLIO/LICENSE at main · Yale-LILY/FOLIO · GitHub"
[6]: https://huggingface.co/datasets/yale-nlp/FOLIO "yale-nlp/FOLIO · Datasets at Hugging Face"
[7]: https://aclanthology.org/D11-1111.pdf "Computing Logical Form on Regulatory Texts"
[8]: https://aclanthology.org/D11-1111/ "Computing Logical Form on Regulatory Texts - ACL Anthology"
[9]: https://aclanthology.org/D11-1111.pdf?utm_source=chatgpt.com "Computing Logical Form on Regulatory Texts"
[10]: https://aclanthology.org/P11-2025.pdf "A Corpus of Scope-disambiguated English Text"
[11]: https://aclanthology.org/P13-1007.pdf "Plurality, Negation, and Quantification:Towards Comprehensive Quantifier Scope Disambiguation"
[12]: https://aclanthology.org/P13-1007/ "Plurality, Negation, and Quantification:Towards Comprehensive Quantifier Scope Disambiguation - ACL Anthology"
[13]: https://academic.oup.com/jos/article/40/4/621/7590887 "oup.silverchair-cdn.com"
[14]: https://github.com/McGill-NLP/scope-ambiguity "GitHub - McGill-NLP/scope-ambiguity: Code and data for the paper 'Scope Ambiguities in Large Language Models'. · GitHub"
[15]: https://www-nlp.stanford.edu/~wcmac/downloads/ "Downloads from Bill MacCartney"
[16]: https://www.let.rug.nl/bjerva/gmb/about.php "About - Groningen Meaning Bank - Parallel Meaning Bank"
[17]: https://pmb.let.rug.nl/ "PMB - Parallel Meaning Bank"

---

## 수신 검증 기록 (2026-08-23, 운영 세션 — 본문 밖)

수신 본문 sha256 (이 절 추가 전):
`eb9a89485f0e54ab7160b94e2b905e975a70486ecad25759405f7fdd17847a30`

| # | 회신 주장 | 검증 | 결과 |
|---|---|---|---|
| V1 | FOLIO GitHub v0.0 공개 + LICENSE=CC-BY-SA-4.0 | repo tree·LICENSE 직접 fetch — `data/v0.0/folio-train.jsonl`(787KB) 실재, LICENSE 첫 행 "Attribution-ShareAlike 4.0 International" verbatim | **일치** |
| V2 | raw에 `∀x ∃y`·`∀x ∀y (∃z …)` 실물 | train 전량 파싱 — HoldingCompany·UniversalLanguage 예 **둘 다 발견** | **일치** |
| V3 | 다중 양화 정확 수 **미측정**(회신이 명시한 공백) | **이 환경에서 전수 census 해소**: 고유 premise-FOL 1,649 / 양화≥2 **86** / 혼합 ∀·∃ **19** (train만; validation 별도) — D-22 요건 ≥5 충족 | **해소** |
| V4 | WikiSem을 후보 1순위로 제시 | **우리 선행 실측과 충돌**: v0.3 artifact의 LOGIC은 기사 단위(131 레코드=기사, v0 범위 0/121)라 D-21이 문장 fixture 부적격으로 판정했고, 문장별 부분식 추출은 Q21.1(c)로 **금지**됐다. 회신은 논문의 "2,000문장" 서술 기준이라 zero-context에서 알 수 없던 사실. **후보에서 제외**(단 회신의 신규 사실 — CASP markup의 scope 태그 `-s,-t,-u`, v0.2 계열 별도 artifact — 는 장래 참고로 유효) | **기각(선행 실측 우선)** |
| V5 | FraCaS = 형식 표상 없음(BLOCKED 아님) | 요청서 함정 경고의 정확한 준수 확인 | **정합** |

판정(운영 세션): **FOLIO GitHub v0.0을 유일한 즉시 실측 가능 후보로 채택
추진.** D-22 §13 독립성 6조건 대조 — different_corpus_authority(Yale vs
Groningen) ✓ / independently_authored_gold("written and reviewed by expert
annotators", 980 man-hours) ✓ / not_derived_from_PMB(FOL 직접 저작, PMB
계보 무관 — GMB 계보는 PMB 쪽) ✓ / not_project_generated ✓ /
separate_source_locator(GitHub v0.0 고정) ✓ /
separate_adapter_profile_if_formalism_differs → **FOL adapter 필요**(예견된
조건). 라이선스 CC-BY-SA-4.0: D-20 commitment 방식(원문 0바이트)이라 repo
재배포 문제 없음, 로컬 캐시 사용은 명시 라이선스 하에서 무리 없음.

남는 판정 사안(Q23 상신): FOL→IR 복호의 encoding profile —
① `∀x(P → Q)` → forall(restriction=P, body=Q): 제한 양화의 표준 대응이나
D-22가 codec을 "source 명세가 정의한 encoding"으로 좁혔으므로 FOLIO
Appendix E(Russell&Norvig 기반)를 그 명세로 인정할지 판정 필요.
② `∃y(A ∧ B)`의 restriction/body 분할 경계(어느 conjunct가 제한부인가)는
①보다 더 관례적이라 반드시 판정 필요. HybLogic(반-template 구성)의 R5
성격도 판정자에게 고지.
