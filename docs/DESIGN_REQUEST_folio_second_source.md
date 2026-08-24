# DESIGN REQUEST — FOLIO 제2 source 승인과 FOL encoding profile (Q23)

- 상신: 2026-08-23, 운영 세션
- 판정자 전제: 저장소 접근 없음, 사전 맥락 없음. §1이 사실 전부
- 근거: D-E2E-v1-22 Q22.4 — 독립 제2 source ≥5건(다중 양화 전담), §13
  독립성 6조건. 조사 회신(`RESEARCH_RESULT_second_source_multiquant.md`)
  수령·검증 완료
- 차단 관계: Q23 판정이 fixture 동결의 마지막 선행 판정이다(PMB 측 준비물
  전부 완료: SBN adapter 자격 9/9, 평가 profile, 선별 규칙 초안)

## 1. 사실 (전부 이 세션에서 원본 재실측)

**후보: FOLIO GitHub v0.0** (Yale-LILY, NL↔FOL 전문가 저작 dataset)

| D-22 §13 조건 | 판정 근거 (실측) |
|---|---|
| different_corpus_authority | Yale (PMB=Groningen) |
| independently_authored_gold | 논문: "All stories and FOL annotations … written and reviewed by expert annotators", 980 man-hours |
| not_derived_from_PMB | FOL 직접 저작. (GMB 계보는 PMB 쪽 사실) |
| not_project_generated | 제3자 공개 artifact |
| separate_source_locator | GitHub v0.0 `data/v0.0/folio-train.jsonl`(787,496B) + validation — 직접 fetch 확인 |
| separate_adapter_profile | **FOL adapter 필요** — 본 상신의 §2 |

- 라이선스: repo LICENSE 첫 행 verbatim **"Attribution-ShareAlike 4.0
  International"** (CC-BY-SA-4.0). 참고: 현행 HF 배포본은 MIT 표기+gated —
  우리는 GitHub v0.0만 locator로 쓴다(배포판 계보 분리). fixture는 D-20
  commitment 방식(원문 0바이트)이므로 repo 재배포 문제 없음.
- **규모 실측**(train 전수): 고유 premise-FOL 1,649 / 양화≥2 **86** /
  혼합 ∀·∃ **19** / 그중 ∨·=·⊕ 없는 것 **16** — 요건 ≥5의 3배.
- 조사 회신의 차순위 후보 처리: WikiSem은 우리 선행 실측(기사 단위 LF,
  0/121)과 충돌해 제외(Q21.1(c)가 부분식 추출을 금지). FDA/QuanText는
  artifact locator BLOCKED, LSAT는 명시적 permission 제한, FraCaS는 형식
  표상 없음.
- 유의 사실 고지: FOLIO의 HybLogic 부분집합은 반-template 구성(순수
  자유작문 아님). WikiLogic 부분집합은 from-scratch 저작. 선별 시
  부분집합 필드로 구분 가능.

## 2. 판정 질문

### Q23.1 — FOLIO를 제2 source로 승인하는가

§1의 6조건 대조가 근거의 전부다. 승인 시 cohort 구성은 D-22 §16 그대로
(PMB ≤15 + FOLIO ≥5 = 다중 양화 전담, source-adapter 자격용 단순 양화
control 2~4건은 N 밖).

### Q23.2 — FOL encoding profile (FOLIO_FOL_V0)

D-22 Q22.2는 codec을 "source 명세가 정의한 encoding"으로 좁혔다. FOLIO의
명세는 논문 Appendix E(Russell & Norvig 기반 FOL: ¬∧∨→∀∃=)다. SBN과 달리
FOL은 **제한 양화를 표기하지 않으므로** 복호 규칙 2개가 판정 대상이다:

- **(a) 보편**: `∀x (P → Q)` → `forall(x, restriction=P, body=Q)` —
  제한 양화의 교과서 대응. 이것을 Appendix E 기반 source encoding으로
  인정하는가? (인정하지 않으면 IR에 `implies`가 필요해 profile이 넓어짐)
- **(b) 존재**: `∃y (A₁ ∧ … ∧ Aₙ)`의 restriction/body 분할. 제안 규칙:
  **결박 변수의 단항 술어로 이뤄진 최좌 연쇄 = restriction, 잔여 =
  body; 그런 연쇄가 없으면 restriction = True**. 실물 예
  `∃y (Company(y) ∧ Holds(x, y))` → restriction=Company(y),
  body=Holds(x,y). 이 규칙은 (a)보다 관례적이다 — 승인/수정/기각을 청함.
- **(c) 표기 관례 처리**: 실물에 `∀x ∃y (P(x) → Q(x,y))`처럼 ∃가 →
  왼쪽에 prefix로 걸친 형태가 흔하다(예: "Cats are pets" =
  `∀x ∃y (Cat(x) → Pet(x, y))`). 문자 그대로 읽으면 ∃y가 조건문 전체를
  지배한다 — **prefix 양화열은 표기 순서 그대로 중첩**으로 복호하고 (a)는
  →가 양화 body의 최상위일 때 적용하는 규칙을 제안한다. 승인 여부.
- **(d) fail-closed 경계**: ∨·=·⊕·biconditional 포함 식, (a)~(c) 패턴
  밖의 → 은 전부 INELIGIBLE(선별 전) / UNEXPECTED_UNSCORABLE(동결 후) —
  D-21 §14 회계 그대로.

### Q23.3 — 자격 항목

FOL adapter의 자격은 SBN판 9항목 구조를 따르되 항목 8·9를 (a)~(c) 복호와
그 음성 판별(∨ 포함 식 비복호 등)로 치환한 **9항목 동형**을 제안한다.
승인 여부.

## 3. 판정 없이 진행 가능한 것 (병행 예정)

FOL adapter의 RED 계약 초안(두 갈래 모두 대비 가능), FOLIO v0.0 파일의
로컬 캐시 고정(sha256), 선별 규칙 초안의 FOLIO 층 추가.

## 4. 재현

census 스크립트는 20줄 이하(§1 수치 전부), 원본은 GitHub raw v0.0.
검증 기록은 조사 결과 문서 말미.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
