# RESEARCH RESULT — O1 corpus 접근 조사 (외부 조사 agent 회신)

- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 수신: **2026-08-22** (요청서: `RESEARCH_REQUEST_o1_corpus_access.md`)
- 결론: **corpus 확보 OK** — OSU Schuler Lab `wikisem` v0.3, 신청 불필요,
  직접 다운로드. multi-quantifier 공급 충분(~45%가 scope interaction).
  **단 라이선스 미확정** — corpus 자체 LICENSE 부재 + 논문 PDF는 CC-BY-NC
- 저장: 트랜스크립트 verbatim 추출(M10). 본문 sha256: `c7ead8003ef8e8c05c9eaf7711499a034edd37f5dabd94d9a550439da4a2a35f`

## 운영 세션의 저장 전 검증 (2026-08-22)

| # | 보고 주장 | 검증 | 결과 |
|---|---|---|---|
| V1 | `/schulerlab/dwnload` 살아 있음, v0.3 파일 14개(+v0.2 3개), 크기 목록 | WebFetch 재실측 | ✅ 파일명·크기 전부 일치. **주의: 경로는 정말 `dwnload`** — 이전에 내가 "합자 왜곡, 실제는 download일 것"이라 추정하고 `/download`를 404 맞았던 것은 **내 추정 오류**(조사 agent가 원문 그대로 시도해 적중) |
| V2 | C6 logic verbatim 조각 3건 | 파일 직접 다운로드(3.98MiB) 후 grep | ✅ gironde 정확 일치 1·hollywood 13·dna 5. 표기 형태 `N LOGIC: (^ (Some (\x1 …` 확인 |
| V3 | 논문 PDF에 "licensed under CC-BY-NC" | 로컬 확보 PDF의 스트림 추출 텍스트 grep | ✅ **verbatim 발견** (ELRA 행) — **내 이전 C축 감사표의 "CC BY 4.0"이 오류였음이 확정**(아래 P14 정정) |
| V4 | 저자 이메일 {rasmussen.63,schuler}@ling.osu.edu | 같은 PDF grep | ✅ |
| V5 | scope 통계 55.0/25.7/11.0/5.3/3.0% + "nearly half" | 같은 PDF grep | ✅ 5/5 + 발견 |

**조사 agent의 규율 준수 확인**: Wayback 실패를 "snapshot 없음"으로
단정하지 않고 "부재 판정은 하지 않는다"로 보고 — 요청서 §5의 부재-판정
규율이 외부 agent에게 이식돼 작동했다.

## Stage 2에 미치는 결정 사항

1. **fixture 저작 가능** — 1순위 출처 확정(wikisem v0.3), 후보 공급 충분.
2. **라이선스 관문 신설**: corpus 자체 LICENSE 부재 + 논문 CC-BY-NC.
   → **fixture의 원문 text를 저장소에 커밋하는 것은 라이선스 확인
   전까지 보류.** 내부 평가용 사용과 재배포는 다른 문제(보고서의 구분
   그대로). 잠정 방식: fixture는 **locator(파일명·행 오프셋)+원문
   sha256+우리 IR 번역**만 커밋하고 원문 text는 실행 시 fetch — 단
   fixture_template이 `source.text verbatim`을 요구하므로 이 잠정 방식과
   template의 충돌은 저자 회신 또는 설계 담당 확인으로 해소.
   저자 문의처는 위 이메일(문의 여부는 사용자 결정).
3. 대안 A(Wang&Shi)는 generator 중심이라 "고정 원문+LF" 규율에 약함,
   대안 B(QuantML)는 scope fixture 4건뿐 — **보조 참고용**. 판정
   D-E2E-v1-19의 O1-first는 자료 접근성 면에서도 유지된다.

---

## 조사 보고 원문 (verbatim)

첨부 요청서의 기준대로 **기억이 아니라 현재 웹 페이지·직접 다운로드 파일을 기준으로 확인**했다. 특히 “접근 불가”는 검색 경로 없이 단정하지 않는 조건을 적용했다. 

## 주 임무

**corpus 다운로드 URL:** [OSU Schuler Lab — Downloads](https://linguistics.osu.edu/schulerlab/dwnload?utm_source=chatgpt.com)
**상태: OK — 계정·신청 불필요.**

2020 논문이 마지막에 명시한 유지 주소가 정확히 `.../schulerlab/dwnload`이며, 현재도 같은 주소가 살아 있다. 현재 페이지 제목은 “Translations of Simple English Wikipedia Articles into Typed Lambda Calculus”이고, quantifier scope가 CASP의 `-s`, `-t`, `-u` 태그로 기록된다고 명시한다. ([ACL Anthology][1])

### 형식 및 규모

현재 공개본은 **v0.3, 압축파일이 아닌 평문 `.txt` 14개**다.

* C1–C7 각각에 `*.cg*.txt` 1개와 `*.logic*.txt` 1개.
* logic 파일 크기는 C1 6.01 MB, C2 5.34 MB, C3 4.68 MB, C4 4.42 MB, C5 4.28 MB, C6 3.98 MB, C7 4.2 MB로 약 **33 MB**.
* CG 파일은 tranche당 대략 0.94–1.01 MB라 전체 약 **8 MB**다. ([Department of Linguistics][2])
* 구버전 v0.2도 남아 있지만, OSU는 이를 `modelblocks`로 수동 변환해야 하며 생성되는 lambda-calculus 파일은 각각 100 MB 이상이라고 설명한다. 따라서 fixture 제작에는 **v0.3 logic 파일을 바로 쓰는 편이 맞다.** ([Department of Linguistics][2])

문장 수는 버전을 구분해야 한다. **논문이 기술한 corpus는 2,000문장**이다. ([ACL Anthology][1]) 반면 현재 v0.3 C1–C7은 각 tranche가 128개 article의 “6-sentence beginnings”를 대상으로 하므로 2020 논문 당시 공개본보다 확장된 상태다. 실제로 제가 현재 C1–C7 CG 파일 7개를 직접 내려받아 `CG:` 레코드를 세어보면 **article title을 제외한 문장 레코드는 5,046개**였다. 따라서 “2,000”은 논문판 규모, “5,046”은 **2026-08-22 현재 다운로드본을 직접 센 값**으로 구분하는 것이 안전하다. 다운로드 페이지 자체도 C1부터 C7까지 각 tranche의 범위를 명시한다. ([Department of Linguistics][2])

### logical form 표기 샘플

아래는 현재 C6 logic 파일에서 **그대로 잘라낸 verbatim fragment**다. 전체 식을 재구성하거나 의역하지 않았다.

> `Some (\x1 Some (\e1 N-aD:gironde e1 x1)` 

> `Equal a1 (\v1 Some (\e1 N-aD:hollywood e1 v1)` 

> `Some (\x105 Some (\e105 N-aD:dna e105 x105)` 

실제 표기는 이처럼 `Some`, `Equal`, `^`, `\x1`, `\e1` 같은 lambda binder/quantificational operator를 중첩한다. 논문은 annotator가 scope-parent 관계를 표시한 뒤 이를 자동 검증·수정하여 **모든 변수가 restriction 또는 nuclear scope 등의 lambda abstraction에 바인딩된 well-formed lambda-calculus expression**이 되게 한다고 설명한다. ([ACL Anthology][1])

### multi-quantifier 문장

**존재하며, 20건 확보에는 양적으로 충분하다.**

논문의 첫 100개 article 통계는 다음과 같다.

| scopally interacting quantifiers | 문장 비율 |
| -------------------------------- | ----: |
| 없음                               | 55.0% |
| 2개                               | 25.7% |
| 3개                               | 11.0% |
| 4개                               |  5.3% |
| >4개                              |  3.0% |

즉 **45%가 적어도 한 쌍의 quantifier scope interaction을 갖고**, 약 20%는 복수 interaction을 갖는다. 논문 결론도 전체 2,000문장 corpus에 대해 “nearly half”가 multiple scopally interacting quantifiers로 주석되었다고 요약한다. ([ACL Anthology][1])

따라서 논문의 비율을 단순 규모 추정에 적용하면 후보는 **수백 건, 대략 900건 안팎의 오더**다. 이는 정확한 전수 count가 아니라 논문의 45% 표본 통계와 “nearly half” 서술에서 얻은 근사치다. fixture 20건을 고르는 데에는 여유가 크다.

### 라이선스

여기가 주의점이다. **현재 corpus 다운로드 페이지나 내려받은 v0.3 text 파일에서는 corpus 자체의 명시적 LICENSE/README를 확인하지 못했다.** 현재 landing page에서 `license`와 `README`를 검색해도 해당 항목이 없다. ([Department of Linguistics][2])

그리고 첨부 조사서의 “PDF 공개, CC BY 4.0”과 달리, **2020 LREC 논문 PDF 자체 첫 페이지에는** 다음처럼 적혀 있다.

> “licensed under CC-BY-NC” ([ACL Anthology][1])

따라서 두 가지를 분리해야 한다.

1. **논문 PDF:** PDF 원문 표시상 `CC-BY-NC`. ([ACL Anthology][1])
2. **corpus data:** 현재 OSU download page/files에서 별도 명시 라이선스를 찾지 못함.

즉 논문 라이선스를 곧바로 corpus 재배포 라이선스로 간주해서는 안 된다. fixture를 내부 평가에만 읽어 쓰는 것과, 원문 문장+LF를 제품/저장소에 함께 재배포하는 것은 구분하는 편이 안전하다.

라이선스 확인이 필요하면 논문에 공개된 저자 연락처는 **`{rasmussen.63,schuler}@ling.osu.edu`**다. ([ACL Anthology][1])

### 다운로드/신청 절차

**신청 없음.** 현재 OSU 페이지의 파일명을 클릭하면 `.txt`가 직접 반환된다. 예를 들어 C6 semantic logic은 아래 URL에서 바로 열린다. 

[C6 logic 직접 파일](https://linguistics.osu.edu/sites/default/files/2026-03/wikisemC6.logic_.txt?utm_source=chatgpt.com)

C1–C7 전체는 landing page에서 직접 연결된다. [전체 C1–C7 다운로드 목록](https://linguistics.osu.edu/schulerlab/dwnload?utm_source=chatgpt.com)

### 검색 경로 / Wayback 결과

현재 경로를 확보했기 때문에 “불가” 판정은 아니지만, 요청서가 Wayback 확인까지 명시했으므로 경로도 기록한다. 

확인한 경로는 **논문 본문의 `.../schulerlab/dwnload` → 현재 OSU Schuler Lab → Downloads → C1–C7 direct links**, 그리고 웹 검색의 `site:linguistics.osu.edu schulerlab`, exact-path 검색이었다. Wayback에 대해서는 wildcard URL과 CDX 접근을 시도했지만 이 조사 환경의 브라우징 백엔드에서 wildcard/CDX 호출이 실패했고, 검색엔진에서도 exact-path snapshot이 별도로 노출되지 않았다. 따라서 **“Wayback에 snapshot이 없다”는 부재 판정은 하지 않는다.** 현재 원주소가 정상 작동하므로 실물 확보에는 영향이 없다.

[Wayback exact-path 조회 주소](https://web.archive.org/web/*/https://linguistics.osu.edu/schulerlab/dwnload?utm_source=chatgpt.com)

---

## 부 임무

### 대안 A — Wang & Shi, ACL 2025

**데이터 위치:** 현재 확인되는 공개 위치는 저자의 GitHub 저장소다.

[Yixuan-Wang/modal-disjunction](https://github.com/Yixuan-Wang/modal-disjunction?utm_source=chatgpt.com)

논문은 이 데이터셋을 propositional/modal logic의 hypothetical·disjunctive syllogism controlled dataset이라고 설명한다. 구성은 modality 3종 × rule 4종 × theorem/fallacy 2종 = **24 logical forms**, 각 form에 1,000 interpretations를 결합하여 **24,000 questions**라고 명시한다. ([ACL Anthology][3])

형식의 대표적인 논문 원문 logic form은 다음과 같다.

> `{φ ∨ ψ, ¬φ} ⊢ ψ` 

논문 Figure 2에서는 여기에 `φ = Jane is watching a show`, `ψ = John is reading a book` 같은 interpretation을 넣어 자연어 QA로 변환한다. 

**접근성 판정은 “코드 공개 OK / 완성 dataset artifact는 미확인”이다.** 현재 `v2` branch root에는 `asset`, `code`, `.gitignore`, `.justfile`만 보이고, dataset 디렉터리나 release artifact가 노출되어 있지 않다. ([GitHub][4]) Generator는 명시적으로 “Generate data for the modal disjunction task”라고 설명된다. ([GitHub][5])

코드상 데이터는 Pandas/CSV 계열이다. 예를 들어 `make_data_wan(seed)`는 50행을 만들면서 `subject1`, `subject2`, `action1`, `action2` 열과 SHA-1을 구성하고, 주석 처리된 저장 경로는 `../data/wan/raw.2.csv`다. 동시에 코드 자체가 예전 `logicasker.csv`를 참조한다. ([GitHub][6])

더 중요한 점은 논문이 2025년 출판본에서 **dataset을 publication 시 open-source하겠다고 선언**했다는 것이다.  그러나 현재 공개 GitHub `v2` branch를 조사한 범위에서는 **완성된 24k CSV/HF dataset을 정본 파일로 식별하지 못했다.** HF도 제목/저자/repository명으로 검색했지만 해당 dataset을 확정할 결과가 나오지 않았다.

**라이선스:** repo root 파일 목록에는 `LICENSE`가 없고, `LICENSE` 검색도 일치 항목이 없다. 따라서 **코드/데이터 저장소의 명시 라이선스는 현재 확인 불가**다. ([GitHub][4]) ACL 2025 논문 자체는 ACL Anthology 정책상 CC BY 4.0이지만, 이것 역시 별도의 GitHub dataset license를 대신하지 않는다. ([ACL Anthology][3])

**판정:** 연구 재현용 대안으로는 쓸 수 있지만, “외부 정본의 고정된 원문+LF 20개를 그대로 fixture로 채택”한다는 이번 규율에는 OSU보다 약하다. 현재 확인되는 핵심 산출물이 **immutable dataset dump보다 generator/code 중심**이기 때문이다.

---

### 대안 B — QuantML worked examples

**공개 worked examples는 실제로 존재하고, scope를 형식적으로 명시한다.**

가장 직접적인 공개 자료는 Tilburg의 **Quantification Bank**다.

[Quantification Bank — Examples](https://sigsem.uvt.nl/QuantificationBank/examples.htm?utm_source=chatgpt.com)

Examples index에서 아예 `Scoping` 범주로 다음 **4개 예시**를 묶어 놓았다.

* “All the students read at least three papers twice”
* “Santa gave the children a present”
* “Three men moved both pianos.”
* “Everybody liked two of Charley’s paintings.” ([Sigsem][7])

QuantML concrete syntax에는 scope를 위한 XML element가 명시되어 있다.

`<scoping>`은 `@arg1`, `@arg2`와 함께 `@scopeRel: (wider | dual | equal)`을 사용한다. 즉 “quantifier가 있다” 수준이 아니라 **두 quantification 사이의 상대 scope relation을 데이터 구조로 직접 표현한다.** ([Sigsem][8])

공개 논문 중 확인한 핵심 자료는 다음 네 계열이다.

* Bunt 2019, *A Semantic Annotation Scheme for Quantification* — abstract syntax, compositional semantics, XML representation을 소개. ([ACL Anthology][9])
* Bunt 2020, *Annotation of Quantification: The Current State of ISO 24617-12* — QuantML의 metamodel/abstract syntax/XML/conpositional semantics를 정리. ([ACL Anthology][10])
* Bunt et al. 2022, *Quantification Annotation in ISO 24617-12, Second Draft*. ([ACL Anthology][11])
* Bunt 2023, *The compositional semantics of QuantML annotations* — 특히 scope relation의 의미론을 구체적으로 전개한다. ([ACL Anthology][12])

2023 논문은 2개 이상의 quantifier가 있는 문장의 abstract syntax를 **participation-link structures + 그 사이의 scope relations**로 정의하고, semantic interpretation이 그 scope 관계에 의해 결정된다고 명시한다. 이어 `wider`, `dual`, `equal` 세 관계에 대해 각각 자연어 worked example을 준다. ([ACL Anthology][12]) 형식 의미론도 예를 들어 다음과 같이 직접 명시한다.

> `IQ(wider) = λx.λy.x ∪* y` ([ACL Anthology][12])

**추출 가능 규모:** “scope fixture”로 보수적으로 셀 경우 Quantification Bank의 `Scoping` 섹션에서 바로 식별되는 것은 **4개**다. 다른 범주와 Bunt 논문들에도 multi-quantifier 예제가 더 있지만 중복이 있고, 모두가 독립된 완전 annotation fixture라고 볼 수 있는 것은 아니다. 따라서 **20개의 독립 scope fixture를 확실히 확보하는 주 공급원으로 보기에는 부족하다.** 대신 QuantML 구조의 의미를 검증하거나, `wider/dual/equal`이라는 다른 scope formalism을 비교하는 참고 fixture에는 매우 적합하다. ([Sigsem][7])

---

## 종합 판정

**1순위: OSU Schuler Lab `wikisem` v0.3 corpus.**

이유는 명확하다. **저자가 논문에서 직접 유지 주소를 지정했고 그 주소가 현재 살아 있으며**, C1–C7의 실제 typed-lambda-calculus logic 파일을 신청 없이 바로 받을 수 있다. 더구나 논문 실측에서 45%가 scope interaction을 가지므로 **quantifier-scope fixture 20건 확보는 데이터 양 측면에서 사실상 문제가 없다.** ([ACL Anthology][1])

단, **fixture를 외부에 재배포한다면 corpus 자체 라이선스 확인이 마지막 미해결점**이다. 현재 다운로드 페이지·파일에는 별도 LICENSE가 없고 논문 PDF는 `CC-BY-NC`라고 적혀 있으므로, 실험용 20건을 저장소에 포함시키기 전에 Schuler/Rasmussen 측에 corpus 데이터의 재배포 조건을 한 번 확인하는 것이 가장 확실하다. ([ACL Anthology][1])

[1]: https://aclanthology.org/2020.lrec-1.132.pdf "A Corpus of Encyclopedia Articles with Logical Forms"
[2]: https://linguistics.osu.edu/schulerlab/dwnload "Downloads | Department of Linguistics"
[3]: https://aclanthology.org/2025.acl-long.824/ "Logical forms complement probability in understanding language model (and human) performance - ACL Anthology"
[4]: https://github.com/Yixuan-Wang/modal-disjunction "GitHub - Yixuan-Wang/modal-disjunction · GitHub"
[5]: https://github.com/Yixuan-Wang/modal-disjunction/tree/v2/code/src/modal_disjunction/gen "modal-disjunction/code/src/modal_disjunction/gen at v2 · Yixuan-Wang/modal-disjunction · GitHub"
[6]: https://github.com/Yixuan-Wang/modal-disjunction/blob/v2/code/src/modal_disjunction/gen/data_wan.py "modal-disjunction/code/src/modal_disjunction/gen/data_wan.py at v2 · Yixuan-Wang/modal-disjunction · GitHub"
[7]: https://sigsem.uvt.nl/QuantificationBank/examples.htm "Examples"
[8]: https://sigsem.uvt.nl/QuantificationBank/concrete-syntax.htm "QuantML Bank News"
[9]: https://aclanthology.org/W19-0403/?utm_source=chatgpt.com "A Semantic Annotation Scheme for Quantification - ACL Anthology"
[10]: https://aclanthology.org/2020.isa-1.1/?utm_source=chatgpt.com "Annotation of Quantification: The Current State of ISO 24617-12 - ACL Anthology"
[11]: https://aclanthology.org/2022.lrec-1.364/?utm_source=chatgpt.com "Quantification Annotation in ISO 24617-12, Second Draft - ACL Anthology"
[12]: https://aclanthology.org/2023.isa-1.8.pdf "The compositional semantics of QuantML annotations"

---

## 부록 (2026-08-23 실측) — C1~C7 직접 파일 URL 14개

로컬 캐시는 세션별 임시 디렉터리에 있어 세션이 바뀌면 사라진다. 재취득에
필요한 것은 URL이고, **경로의 날짜 디렉터리는 파일명에서 추론할 수 없다**
(tranche마다 다르다). 그래서 landing page의 href를 그대로 기록한다 —
추측하지 않는다(G46: 원문 철자를 자동 교정하려다 부재 판정을 낸 사례).

기준: `https://linguistics.osu.edu` + 아래 경로.

| tranche | logic | cg |
|---|---|---|
| C1 | `/sites/default/files/2023-02/wikisemC1.logic__0.txt` | `/sites/default/files/2023-02/wikisemC1.cg_.txt` |
| C2 | `/sites/default/files/2023-02/wikisemC2.logic_.txt` | `/sites/default/files/2023-02/wikisemC2.cg_.txt` |
| C3 | `/sites/default/files/2024-11/wikisemC3.logic_.txt` | `/sites/default/files/2024-11/wikisemC3.cg_.txt` |
| C4 | `/sites/default/files/2024-12/wikisemC4.logic_.txt` | `/sites/default/files/2024-12/wikisemC4.cg_.txt` |
| C5 | `/sites/default/files/2026-02/wikisemC5.logic_.txt` | `/sites/default/files/2026-02/wikisemC5.cg_.txt` |
| C6 | `/sites/default/files/2026-03/wikisemC6.logic_.txt` | `/sites/default/files/2026-03/wikisemC6.cg_.txt` |
| C7 | `/sites/default/files/2026-04/wikisemC7.logic_.txt` | `/sites/default/files/2026-04/wikisemC7.cg_.txt` |

**C1의 logic 파일명이 `logic__0`(밑줄 2개 + `_0`)인 것에 주의** — 다른
tranche와 규칙이 다르므로 패턴으로 생성하면 404가 난다. `wikisema1-2` /
`wikisemc1-c2`의 `casp_.toktrees` 파일들(2021-06)도 같은 페이지에 있으나
v0.2 계열이고 O1 용도가 아니다.

받은 바이트의 동일성 확인용 해시는 `DESIGN_REQUEST_o1_oracle_unit_and_
coverage.md` §7에 있다(C6 logic·cg 2개). 저장소에는 파일을 담지 않는다
(D-E2E-v1-20 §Q20.4 — 로컬 캐시는 권위가 아니고 해시 일치 전용).
