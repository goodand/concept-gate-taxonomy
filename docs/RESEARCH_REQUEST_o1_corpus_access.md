# 자료 조사 요청 — O1 oracle corpus 실물 확보 (zero-context)

- 작성: 2026-08-22. 이 문서는 **사전 맥락 없는 외부 조사 agent**를 위해
  자체 완결로 작성됐다. 아래 배경 §1만 읽으면 조사에 필요한 전부다.
- 조사 원칙: **기억으로 답하지 말고 웹 실측으로만.** "없다"는 판정은 반드시
  **어디를 어떻게 찾았는지 목록**과 함께 (부재 주장은 검색 경로 없이는
  무효). 모든 주장에 URL을 붙일 것.

## 1. 배경 (이것만 알면 됨)

한 형식의미론 평가 실험이 **외부 정본 corpus**를 필요로 한다. 사람이 주석한
logical form이 있는 문장들을 fixture로 쓰되, **corpus의 원문 표현을 그대로
보존**해야 한다(자체 저작 금지가 실험 규율). 대상 corpus:

- **논문**: "A Corpus of Encyclopedia Articles with Logical Forms",
  Nathan Rasmussen & William Schuler, LREC 2020,
  https://aclanthology.org/2020.lrec-1.132/ (PDF 공개, CC BY 4.0)
- **내용**: Simple English Wikipedia 문장 약 2,000개 + typed lambda calculus
  logical form (quantifier scope가 명시됨 — 이 실험의 관심사)
- **결정적 단서 (논문 본문에서 직접 추출, verbatim)**:
  > "This corpus is maintained at https://linguistics.osu.edu/schulerlab/dwnload"
  (PDF 합자 왜곡 — 실제 경로는 download류일 것)
- **사전 확인된 사실**: `linguistics.osu.edu/schulerlab` 페이지는 **살아
  있고 "Downloads — Files of interest from the Schuler Lab" 섹션이 있다.**
  단 `/schulerlab/download`는 404였다. 즉 정확한 하위 경로만 찾으면 된다.

## 2. 주 임무 — corpus 실물 확보 경로 확정

1. OSU Schuler Lab 사이트의 Downloads/Resources 페이지를 탐색해
   **이 corpus의 실제 다운로드 URL**을 찾아라. (사이트 내 링크 추적,
   `site:linguistics.osu.edu schulerlab` 검색, Wayback Machine
   `web.archive.org`에서 `linguistics.osu.edu/schulerlab/*` 스냅샷 확인 포함)
2. 찾으면 확인할 것:
   - **파일 형식과 규모** (압축 포맷, 파일 수, 문장 수)
   - **logical form 표기 샘플 2~3건 verbatim 인용** (typed lambda calculus
     표기가 실제로 어떤 모양인지 — 예: 변수 바인딩, quantifier 표기)
   - **multi-quantifier 문장**(한 문장에 quantifier 2개 이상, scope가
     주석된 것)이 존재하는지와 대략 몇 건인지 — 실험은 이런 문장 20개가
     필요하다
   - **라이선스 명시** (파일 내 LICENSE/README)
3. 다운로드가 계정/신청을 요구하면 그 절차를 기록하라 (신청 페이지 URL,
   요구 정보).

## 3. 부 임무 — 대안 2개의 접근성 (주 임무 성공 여부와 무관하게 수행)

**대안 A — Wang & Shi (ACL 2025)**: "Logical forms complement probability in
understanding language model (and human) performance",
https://aclanthology.org/2025.acl-long.824/ — 이 논문이 소개하는 "controlled
dataset of hypothetical and disjunctive syllogisms in propositional and
modal logic"의 **데이터 공개 위치**(GitHub/HF 등)와 라이선스, 형식 샘플.

**대안 B — QuantML worked examples**: ISO 24617-12 표준 자체는 paywall이나,
H. Bunt의 공개 논문들(LAW workshop 계열, ACL Anthology에서 "Bunt
quantification ISO 24617" 검색)에 **worked example들이 본문에 실려 있는지**,
그 예시가 quantifier scope를 형식 구조로 명시하는지, 몇 건이나 추출 가능한지.

## 4. 보고 형식

```
## 주 임무
corpus 다운로드 URL: <URL> / 상태(OK|신청 필요|불가)
형식: <표기 샘플 2~3건 verbatim>
multi-quantifier 문장: 존재 여부 + 대략 규모
라이선스: <원문 인용>
(불가 시) 시도한 경로 전체 목록 + Wayback 결과 + 저자 연락 채널(공개 이메일/페이지)

## 부 임무
대안 A: 데이터 위치 / 접근성 / 형식 샘플 / 라이선스
대안 B: worked example 소재 논문 목록 / 추출 가능 규모

## 종합 판정
fixture 20건(quantifier scope) 저작에 가장 확실한 출처 1순위와 근거 2줄
```

## 5. 하지 말 것

- 대용량 파일 전체를 출력에 붙이지 말 것 (샘플 인용만)
- corpus 내용을 요약·의역해 logical form을 "재구성"하지 말 것 — verbatim만
- 접근 불가를 확인 없이 단정하지 말 것 (경로 목록 필수)

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
