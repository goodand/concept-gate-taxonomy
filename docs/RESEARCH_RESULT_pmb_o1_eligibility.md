# RESEARCH RESULT — PMB의 O1 fixture source 적격성 사전 조사 (수신 verbatim)

- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
- 수령: 2026-08-23, 사용자 경유 (조사용 agent — openai_web_gpt 환경)
- 요청 원문: `RESEARCH_REQUEST_pmb_o1_eligibility.md`
- 검증: 수령 당일, 이 문서 말미 "수신 검증 기록" — **조사 환경이 열지 못한
  공식 1GB ZIP을 이 환경에서 완주 다운로드해 BLOCKED 항목까지 1차 해소**
- 아래 본문은 수신 그대로이며 편집하지 않는다

---

## 판정 원문 (verbatim)

# PMB O1 fixture source 적격성 사전 조사 결과

조사 범위는 요청서의 지시대로 **접근·라이선스·단위/쌍·표상 형식·규모·양화 존재 신호의 사실 확인**에 한정했습니다. 아래 내용은 **적격성 판정이 아닙니다.** 

## R1 — 접근 경로

**사실**

현재 PMB 공식 Data 페이지가 표시하는 최신 **stable Meaning Representations release는 5.1.0**이며 릴리스 날짜는 **2024-04-25**, full archive는 **1.0 GB**입니다. stable 목록은 `1.0.0 → 2.0.0 → 2.1.0 → 2.2.0 → 3.0.0 → 4.0.0 → 5.0.1 → 5.1.0`입니다. ([Parallel Meaning Bank][1])

별도의 `/releases/` 디렉터리에는 `pmb-5.0.0-prerelease.tar.gz`, `pmb-5.0.0.tar.gz`, `pmb-5.0.0.zip`도 존재합니다. 즉 **파일 디렉터리의 목록과 공식 stable-release 표는 동일하지 않습니다.** 최신 PMB 데이터 파일은 여전히 `pmb-5.1.0.zip`입니다. ([Parallel Meaning Bank][2])

다운로드는 **등록/신청/메일 요청이 아니라 직접 링크**입니다. 정확한 URL:

[https://pmb.let.rug.nl/releases/pmb-5.1.0.zip](https://pmb.let.rug.nl/releases/pmb-5.1.0.zip?utm_source=chatgpt.com)

**근거**

공식 Data 페이지는 “Stable versions of the PMB are provided…”라고 명시하고 5.1.0을 최상단에 둡니다. 공식 releases index에는 `pmb-5.1.0.zip`이 실제 파일 항목으로 노출됩니다. ([Parallel Meaning Bank][1])

**확신도:** **높음**

**BLOCKED:** **부분적 YES.** 공식 ZIP 링크까지는 확인됐으나 이 조사 환경의 웹 리더가 `application/zip` 본문을 직접 열지 못했습니다. 인증 페이지로 리디렉션된 것이 아니라 ZIP MIME 처리 제약이므로 **접근 경로 자체는 확인**, ZIP 내부의 직접 검사는 BLOCKED입니다.

---

## R2 — 라이선스

### 사실 1: annotation과 raw text의 라이선스가 분리되어 있다

5.1.0 릴리스의 `licenses/PMB_LICENSE.txt` 사본에서 핵심 문구는 다음과 같습니다.

> “The PMB annotations are made available under the Open Data Commons Attribution License (ODC-BY)”

그리고 raw text에 대해서는 별도로:

> “The raw texts included in the PMB are published under their respective license terms, as noted in their accompanying .met files.”

즉 **ODC-BY는 PMB annotation에 대한 blanket license이고, raw sentence 자체에는 blanket ODC-BY가 적용된다고 적혀 있지 않습니다.**

릴리스의 `licenses/`에는 실제로 `PMB_LICENSE.txt`, `ODC-BY.txt`, `Tatoeba_LICENSE.txt`, `SICK-README.txt`, 여러 RTE 관련 라이선스/README 등이 따로 존재합니다.

### 사실 2: ODC-BY는 상업 이용 자체를 금지하지 않는다

동봉된 `ODC-BY.txt`에는:

> “These rights explicitly include commercial use, and do not exclude any field of endeavour.”

라고 되어 있습니다. 반면 같은 문서는 개별 Contents에 대해:

> “this license only governs the rights over the Database, and not the contents of the Database individually.”

라고 명시합니다. 따라서 **annotation/database 권리와 개별 raw text 저작권을 구분해야 합니다.**

### 사실 3: 가장 큰 Gold subcorpus인 Tatoeba에는 별도 CC-BY가 명시되어 있다

릴리스의 `Tatoeba_LICENSE.txt`는 verbatim으로:

> “The Tatoeba corpus is released under CC-BY”

라고 하며 `https://creativecommons.org/licenses/by/2.0/fr/`를 지정합니다. 또한 원문은 변경하지 않고 annotation layers를 추가했다고 적습니다.

5.1.0 README 통계상 영어 Gold 11,987 documents 중 **10,983 documents가 Tatoeba**입니다. 그러나 나머지 subcorpora까지 이 라이선스로 일반화할 수는 없습니다.

### 배포 페이지 / README / 논문의 차이

* **공식 Data 페이지:** 다운로드와 인용 논문은 제시하지만, 조회된 페이지 본문에는 데이터 라이선스 문구가 없습니다. ([Parallel Meaning Bank][1])
* **release README:** `licenses/`가 “license statements for subcorpora used”를 담는다고 설명하지만 raw 전체에 대한 단일 라이선스를 부여하지 않습니다.
* **`PMB_LICENSE.txt`:** annotation=ODC-BY, raw text=각 `.met`에 지정된 source license라고 명시합니다.
* **2017 PMB 논문:** PDF에서 `license` 문자열을 찾았으나 데이터 라이선스 조항은 발견되지 않았습니다. 논문은 다만 “freely distributable texts are preferable”이라고 corpus 선정 원칙을 설명합니다. 이는 **라이선스 부여 문구가 아닙니다.** ([ACL Anthology][3])

**공개 GitHub에 원문 문장을 넣을 수 있는가?**

조사 단계에서 확인 가능한 정확한 결론은:

> **PMB annotation의 ODC-BY만으로 모든 raw Gold sentence의 공개 재배포를 정당화할 수 없다. 각 후보 문장의 `.met` source/license를 확인해야 한다.**

Tatoeba처럼 별도 CC-BY가 명시된 source는 그 라이선스 조건 아래에서 별도 검토할 수 있지만, 이를 다른 subcorpus에 전파해서는 안 됩니다.

**확신도:**

* annotation=ODC-BY / raw=text-specific: **높음**
* 개별 Gold sentence 전체에 대한 공개-repo 허용 여부: **미판정**

**BLOCKED:** **부분적 YES.** `PMB_LICENSE.txt` 등은 5.1.0 릴리스 구조를 복제한 공개 파일에서 확인했습니다. 공식 1 GB ZIP을 이 환경에서 직접 풀어 `.met` 전수를 검사하지는 못했습니다. 따라서 **개별 문장별 raw-text license 확인은 BLOCKED**입니다.

---

## R3 — 단위와 쌍

**사실**

원본 5.1.0 release 구조의 기본 단위는 **sentence directory가 아니라 document directory**입니다.

README 예시는:

```text
data/
    gold/
        p00/
            d0030/
```

이고 각 document directory에는 적어도 다음이 있습니다.

```text
*.met
*.raw
*.status
*.drs.sbn
```

`*.raw`는 raw document text이고 `*.drs.sbn`은 해당 DRS의 SBN 표현입니다.

중요하게도 영어 Gold 규모는:

* **11,987 documents**
* **12,117 sentences**

입니다. 따라서 **Gold 전체가 “directory 하나 = sentence 하나”인 것은 아닙니다.** multi-sentence documents가 섞여 있음을 숫자 자체가 보여줍니다.

반면 release의 semantic-parsing split은 README가 명시적으로:

> “a *.sbn file containing the ID, raw sentences and corresponding sbn”

이라고 설명합니다.

PMB 5.1.0 seq2seq 데이터를 제공하는 저자측 GitHub 사본에서도 실제 `en/train/gold.sbn`이 **raw text + TAB + SBN** 형식으로 확인됩니다. 짧은 실물 예:

```text
We exaggerated.    person.n.01 Sub speaker exaggerate.v.01 Agent -1 Time +1 time.n.08 TPR now
```

또 release README의 split 구조에서 영어 test에는 별도로:

```text
standard.sbn    gold-sbn
long.sbn        gold/silver-long-text-sbn
```

이 존재합니다. 즉 long-text challenge가 명시적으로 분리되어 있습니다.

**판정하지 않고 사실만 요약하면:** 원본 Gold 저장 구조는 document-level이며 일부 multi-sentence이고, parsing용 split에는 raw sentence/text와 SBN을 한 레코드에 묶는 형태가 실제 존재합니다. 따라서 운영 세션에서 “문장 단위 1:1”을 요구한다면 **Gold 전체를 그대로 간주할 것이 아니라 sentence-only 레코드를 실측 선별해야 합니다.**

**확신도:** **높음**

**BLOCKED:** **부분적 YES.** document별 정확한 sentence count를 나타내는 별도 metadata field는 확보한 README에서 확인되지 않았습니다. 공식 ZIP의 전체 Gold document를 직접 순회하지 못했으므로 “multi-sentence를 기계적으로 식별하는 정확한 필드/규칙”은 아직 실물 확인이 필요합니다.

---

## R4 — 표상 형식과 양화

**사실**

`DRS인가 SBN인가`는 양자택일이 아닙니다.

* 의미표상 자체: **Discourse Representation Structure (DRS)**, DRT 기반.
* 릴리스 직렬화: **Simplified Box Notation (SBN)**.
* README에는 평가 용도로 **flat clause format**도 사용한다고 설명되어 있습니다.

릴리스 README의 표현은:

> “The DRSs are provided in simplified box notation (SBN).”

입니다.

### SBN 정본

Johan Bos, **“Variable-free Discourse Representation Structures”**, Section 4가 직접 “Simplified Box Notation”을 정의합니다. SBN을 concepts, relations, structural constraints의 sequence로 정의하고 Section 5에서 ordinary DRS로의 해석/변환을 형식적으로 제시합니다. ([세멘틱스 아카이브][4])

[Variable-free Discourse Representation Structures PDF](https://semanticsarchive.net/Archive/jQzMzJlY/compact.pdf?utm_source=chatgpt.com)

양화에서 특히 중요한 정본 문구는:

> “Universal quantification and disjunction is also analysed with the help of negation in SBN.”

이며 universal implication에

`(p → q) ↔ ¬(p ∧ ¬q)`

를 사용한다고 정의합니다. ([세멘틱스 아카이브][4])

### flat clause 정본

van Noord et al. (2018), **“Exploring Neural Methods for Parsing Discourse Representation Structures”**는 DRS를 “a sequence of flat clauses”로 표현하고 well-formedness/interpretablity 검증을 설명합니다. ([ACL Anthology][5])

[ACL Anthology — van Noord et al. 2018](https://aclanthology.org/Q18-1043/?utm_source=chatgpt.com)

### 5.1.0 Gold의 양화 실물

실제 `data/pmb-5.1.0/seq2seq/en/train/gold.sbn`에 다음 Gold record가 있습니다.

```text
Not everyone was happy.    NEGATION <1 NEGATION <1 person.n.01 NEGATION <1 time.n.08 TPR now happy.a.01 Experiencer -2 Time -1
```

즉 universal quantification과 scope가 **명시적 `FORALL` 토큰이 아니라 SBN의 negation/box 구조로 구현되는 경우**가 실제 release Gold에 존재합니다. 이는 Bos의 SBN 정의와 일치합니다. ([세멘틱스 아카이브][4])

**확신도:** **높음**

**BLOCKED:** **NO** — constructor scanner를 설계하는 데 필요한 SBN의 정본 정의와 release-side 표상 예는 확보했습니다. 단, 정본 PDF screenshot 렌더링은 조사 도구의 cache-miss로 실패했고 PDF text layer는 정상적으로 읽혔습니다.

---

## R5 — 규모

**사실**

5.1.0 release README가 제시하는 영어 규모:

| Quality  |  Documents |  Sentences |     Tokens |
| -------- | ---------: | ---------: | ---------: |
| **Gold** | **11,987** | **12,117** | **79,863** |
| Silver   |    147,511 |    164,575 |  1,818,047 |
| Bronze   |    142,138 |    146,670 |  1,262,659 |

이 숫자는 **제가 센 값이 아니라 release README의 통계**입니다.

공식 Data 페이지도 5.1.0 영어 Gold를 **11,987**로 표시하고, 페이지 상단에서 표시 숫자는 Gold instances라고 명시하므로 독립적으로 일치합니다. ([Parallel Meaning Bank][1])

구분 방식도 명시적입니다.

* `data/gold/` — fully manually checked
* `data/silver/` — partially manually checked
* `data/bronze/` — no manual annotations
* 각 document의 `*.status`에서도 annotation layer별 Gold/Silver/Bronze 상태 기록

**확신도:** **높음**

**BLOCKED:** **NO** — 요청된 영어 Gold 문서/문장 규모 및 quality-tier 구분 방식은 release README에서 직접 확인됐습니다.

---

## R6 — 양화 관련 부분집합 존재 신호

**사실**

5.1.0 **English Gold train**의 실제 `gold.sbn`에서 universal-quantifier 계열 문장을 검색할 수 있었습니다. 짧은 예 3건:

```text
Everyone but Jim came.
Tom is liked by everyone.
Not everyone was happy.
```

세 문장 모두 같은 5.1.0 Gold train 파일에서 확인됩니다.

따라서 적어도 **`everyone`/`not everyone`을 포함하는 Gold 양화 사례의 실재 여부는 YES**입니다. 또한 release README 자체도 현재 release가 포함하는 semantic phenomena로 `quantification`과 `scope`를 명시합니다.

이번 검색에서는 `Each ...`, `Some ...`, `Most ...`를 별도로 확정할 만한 Gold-train match를 추가 확보하지 못했습니다. 이것을 **“없음”으로 판정하지 않습니다.** 검색 인터페이스가 1.4 MB 파일 전체에 대한 임의 substring 검색을 안정적으로 제공하지 않았기 때문입니다.

**확신도:**

* universal quantifier 사례의 존재: **높음**
* `each/some/most` 각각의 존재 여부: **미확인**

**BLOCKED:** **부분적 YES** — 3개의 확정 사례는 확보했지만 전체 Gold 양화 inventory 검색은 공식 archive 직접 순회가 필요합니다.

---

## 실패·차단 경로 기록

1. 공식 `pmb-5.1.0.zip` URL을 **문자 그대로** 열었습니다. 링크는 존재하지만 조사 웹 리더가 `application/zip`을 지원하지 않아 ZIP 내부 열기가 실패했습니다. **BLOCKED이지 부재가 아닙니다.** ([Parallel Meaning Bank][2])
2. release README에는 `https://pmb.let.rug.nl/releases/split-5.1.0.zip`가 verbatim으로 적혀 있습니다.  이 파일은 현재 공식 directory index에는 노출되지 않아 이번 환경에서 실재 여부를 독립적으로 확인하지 못했습니다. **미확인이지 404/부재 판정이 아닙니다.**
3. 5.1.0 release README/license 파일을 보유한 공개 GitHub copy는 전체 `data/gold/`를 포함하지 않아 해당 경로 조회가 404였습니다. 이는 **그 mirror가 불완전하다는 의미이지 공식 PMB Gold의 부재를 뜻하지 않습니다.**
4. 대신 PMB5 저자측 seq2seq repository의 `data/pmb-5.1.0/seq2seq/en/train/gold.sbn` blob은 실제 읽기에 성공해 R3/R4/R6의 실물 레코드를 확인했습니다.

## 운영 세션으로 넘길 핵심 사실

가장 중요한 제약은 **R2와 R3**입니다. PMB 5.1.0은 Gold 규모와 SBN 양화 자료 면에서는 충분한 실측 후보를 제공하지만, **원본 Gold는 document-level이고 일부 multi-sentence이며, raw text의 라이선스는 문서별 source license**입니다. 따라서 후속 기계 실측에서는 `sentence-only` 선별과 함께 **각 선택 항목의 `.met` license/source 확인을 같은 단계에 묶는 것**이 필요합니다. 이것은 적격성 판정이 아니라, 이번 조사에서 확인된 release 구조가 요구하는 전처리 조건입니다.

[1]: https://pmb.let.rug.nl/data.php "Data - Parallel Meaning Bank"
[2]: https://pmb.let.rug.nl/releases/ "Index of /releases"
[3]: https://aclanthology.org/E17-2039.pdf "The Parallel Meaning Bank: Towards a Multilingual Corpus of Translations Annotated with Compositional Meaning Representations"
[4]: https://semanticsarchive.net/Archive/jQzMzJlY/compact.pdf "Variable-free Discourse Representation Structures"
[5]: https://aclanthology.org/Q18-1043/ "Exploring Neural Methods for Parsing Discourse Representation Structures - ACL Anthology"

---

## 수신 검증 기록 (2026-08-23, 운영 세션 — 본문 밖)

수신 본문 sha256 (이 절 추가 전 파일):
`7f8f138d72761879a0cc0be9a951b17740a53c5437e873bd09a73681032f452c`

조사 환경(openai_web_gpt)이 열지 못한 **공식 1GB ZIP을 이 환경에서 완주
다운로드**(이어받기 3회, `pmb-5.1.0.zip` 1,030,132,135바이트, sha256
`1533d2a5f3198988069ac45821bf3a9a1cde9db0c28f6a371f933880e4de0f64`, 로컬
캐시 전용 — repo 밖)해 mirror 경유였던 주장을 정본에서 재검증했다.

| # | 회신 주장 | 정본 검증 | 결과 |
|---|---|---|---|
| V1 | releases index에 5.1.0 zip + 5.0.0 변종들 | 공식 index fetch — pmb-* 13항목 | **일치** |
| V2 | `split-5.1.0.zip` 미확인(부재 판정 유보) | HEAD 요청 → **404 확정**, 단 archive README에는 그 URL이 실재 | 유보가 옳았음 + **README의 낡은 URL**이라는 신규 사실 확정 |
| V3 | 라이선스 3문구 (annotation=ODC-BY / raw=.met별 / Tatoeba=CC-BY) | 공식 archive의 `licenses/` 3파일 직접 해제 | **3/3 verbatim 일치** (CC-BY 2.0-fr URL까지) |
| V4 | "Not everyone… " = NEGATION 구조, seq2seq 평탄 레코드 | 공식 gold 문서 `data/en/gold/p76/d2248/en.drs.sbn` 직접 해제 | **일치** — 보편양화=negation이 정본 실물로 확인 |
| V5 | SBN 정본 논문 인용문 | PDF가 subset-font라 이 환경에서 텍스트 대조 **BLOCKED** — 대신 V4의 실물이 같은 명제를 기능적으로 입증 | 기능 검증으로 대체 |
| R6 | 양화 문장 3건 실재 | 공식 gold en.raw 전수 스캔 | **3/3 HIT** (p76/d2248, p66/d2061, p20/d2820) |

조사가 BLOCKED로 남긴 것 중 이번에 해소된 것: ZIP 내부 검사 전반,
`.met` 실물 확인(예: p76/d2248 = `subcorpus: Tatoeba` — 문서별 라이선스
확인이 기계 가능함을 실증), 공식 archive의 실제 경로 형태
**`data/<lang>/<quality>/pXX/dXXXX`** (README 예시의 `data/gold/…`보다
언어 층위가 하나 위).

신규 실측 2건 (회신에 없던 것):

1. **en gold `en.raw` 파일 수 = 12,053** — README의 11,987 documents와
   **66 차이**. 미해석(층위별 status와 디렉터리 배치의 정의 차이 추정).
   적격성 스캔 때 정확한 모집단 정의가 필요하다.
2. **`en.status`에 `scp`(scope) 층위가 별도 존재하며 해당 문서에서 gold** —
   O1(quantifier scope) 적격성에 유리한 신호. 스캔 설계에 반영할 것.

권한 축 기록: 조사 환경은 `application/zip` 본문을 열 수 없고 이 환경은
열 수 있다 — 두 환경이 상보적이며, BLOCKED 어휘 규율 덕에 그 경계가
회신에 정확히 표시되어 이 환경이 이어받을 지점이 명확했다.
