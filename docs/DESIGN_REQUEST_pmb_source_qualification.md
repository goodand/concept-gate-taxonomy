# DESIGN REQUEST — PMB의 O1 source 자격과 3개 판정 질문 (Q22)

- 상신: 2026-08-23, 운영 세션
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실
  전부다
- 근거 판정: D-E2E-v1-21이 O1 instance source 교체(b\*)를 명령하며 후보
  자원에 적격성 자격을 요구했고, PMB를 후보로 지정하되 자동 승격을
  금지했다. 이 문서는 그 자격 스캔의 **실측 결과 보고 + 스캔이 노출한
  판정 필요 사항 3건 + governance 1건**이다
- 차단 관계: Q22 판정 전까지 fixture manifest·constructor profile·Stage 2
  사전등록 동결이 계속 차단된다(변화 없음). 준비물 ①~⑥(subject 정의·
  스키마·cohort·채점·사전등록 초안·end-to-end 리허설)은 완료 상태다

## 1. 스캔 사실 (Path B — adapter 독립 스캐너, 재현 스크립트 포함)

대상: PMB 5.1.0 공식 archive(sha256 `1533d2a5…`, 로컬 캐시 전용)의
영어 gold 12,053 문서 전수. 스캐너와 결과는 저장소에 커밋
(`scan_pmb_eligibility.py`, `pmb_eligibility_scan_pathB.json` — corpus
텍스트 0바이트, 문서 ID·해시만).

필터 사슬(각 단계 근거는 스크립트 docstring):

| 단계 | 규칙 | 통과 |
|---|---|---|
| 양화 한정사 보유 | every/each/all/some/no/most… 어휘 | 870 |
| box/담화 연산자 ⊆ {NEGATION} | SDRT 담화 연산자(CONTINUATION 등)는 wikisem `InAnaphorSet`과 같은 지위 — 이 필터가 다문장 문제도 흡수 | ↓ |
| 내부 문장 경계 없음 + 전 층위 gold | 문장 단위 1:1 + 완전 수동 검수 | **695** |

**적격성 6조건 대조**:

| D-21 조건 | 판정 | 근거 |
|---|---|---|
| 문장 단위 1:1 쌍 | ✅ | 필터 적용 후 695건 |
| 외부 저작 오라클 | ✅ | gold = 수동 검수, `.met`로 출처 추적 |
| 양화 scope 관련성 | ⚠️ **부분** — §2.1 | 보편양화 인코딩 178+9건, 단 다중 양화 0건 |
| v0 constructor 완전 표현 | ⬜ **판정 필요** — §2.2 | ¬∃¬ 인코딩의 지위 |
| 적격 항목 ≥20 | ✅ (수량상) | 695 ≫ 20 |
| 유일 수용 source 금지 | ⬜ **governance** — §2.4 | |

라이선스: 후보 695건 중 **Tatoeba 645건** — 릴리스 동봉
`Tatoeba_LICENSE.txt`가 CC-BY(2.0-fr)를 명시(공식 archive에서 verbatim
확인 완료). 나머지 50건은 subcorpus별 개별 확인 필요(TREC/SICK/RTE 등).
fixture는 어차피 D-20 commitment 방식(원문 0바이트)이므로 라이선스는
로컬 캐시 사용 조건에만 걸린다.

## 2. 판정 질문 4건

### Q22.1 — 다중 양화 재료의 부재: fixture 구성과 estimand 경계

실측: 후보 풀에서 한정사 2개 이상 문서는 4건뿐이고 **전부 관용구
오탐**("all right", "at all", "all of a sudden")이다. 즉 O1의
`representative_distinction`(∀∃ vs ∃∀)과 `multi_quantifier_scope` 경계를
이 풀에서 인스턴스화할 수 없다.

가용한 scope 재료는: 보편양화(¬∃¬ 짝 인코딩) 178건, 부정된 보편(홀수
NEGATION) 9건, 존재·기수 양화(quantity 계열) 다수 — 즉 **양화↔부정
scope**(¬>∀ vs ∀>¬)와 **단일 양화 구조**는 풍부하다.

- (a) fixture 20건을 가용 재료(양화·부정 scope + 단일/기수 양화)로 구성
  하고, `multi_quantifier_scope`는 O1-v1의 측정 경계에서 **명시적으로
  제외**(사전등록에 기록, 향후 O1-v2 사안으로)
- (b) 다중 양화를 공급할 **제2 source**를 추가로 자격(§Q22.4의 governance
  와 결합 — 어차피 제2 source가 필요하다면 그 source가 다중 양화를 담당)
- (c) 그 외

### Q22.2 — ¬∃¬ → forall 복호화: syntax-directed 번역인가 금지된 재작성인가

SBN은 보편양화를 명시 토큰 없이 **부정 상자 짝**으로 인코딩한다 — 정본
(Bos, "Variable-free DRS" §4)이 "Universal quantification … analysed with
the help of negation"으로 **명시한 인코딩 규약**이다. adapter가 짝 NEGATION
패턴을 `forall`(restriction+body)로 복호화하는 것은:

- (a) **corpus가 문서화한 인코딩의 syntax-directed 복호** — wikisem의
  GQ 2-람다 → restriction 필드와 같은 지위로 허용. 복호 규칙은 adapter
  자격 항목에 "짝 패턴 인식의 결정성 + 복호 왕복 검증"을 추가해 결박
- (b) 정리-동치 재작성(¬∃¬ ≡ ∀)이므로 **금지** — 이 경우 expected IR은
  부정 상자 구조 그대로여야 하고, v0 IR에 `not` constructor를 추가해야
  하며(constructor profile 확장 = 외부 판정 사안, D-21 §16) subject의
  방언 명세도 바뀐다
- 운영 세션 권고: **(a)**. 근거: 이 인코딩은 개별 식의 우연한 형태가
  아니라 형식의 **정의 자체**다(정본이 명시). (b)를 택하면 "every"의
  기대 IR이 ¬∃¬가 되어, subject가 `forall`로 답한 정답 인스턴스가 전부
  구조 불일치 FAIL이 된다 — 측정하려는 것(scope 구조)과 무관한 표기
  차이로 estimand가 오염된다

### Q22.3 — 술어 명명: WSD 혼입을 어떻게 차단하는가

PMB의 개념 술어는 WordNet synset(`happy.a.01`, `giant_panda.n.01`)이다.
DirectMatch가 술어명 문자열 일치를 요구하면 subject는 **어의 중의성
해소(WSD)** 까지 맞혀야 하고, estimand가 "quantifier scope 컴파일"에서
"scope + WSD"로 팽창한다. end-to-end 리허설이 이 문제를 축소판으로
실측했다(어간 vs 표면형 불일치만으로 3/3 FAIL, 차원 귀속
`predicate_arguments`).

- (a) **canonicalization profile에 술어명 정규화를 추가**: 비교 전에
  synset을 lemma로 축약(`happy.a.01`→`happy`), subject 출력도 lemma
  소문자로 지시(현 template 그대로). sense 선택은 채점에서 중립화 —
  단 profile 변경은 판정 사안(D-19 §12)이므로 여기서 청함
- (b) estimand에 WSD를 포함(synset 완전 일치 요구) — 운영 세션은 반대:
  O1의 5개 semantic_boundary 어디에도 어휘 의미 선택이 없다
- (c) 그 외 (예: 술어명은 차원에서 제외하고 구조·결박만 비교 — 단
  `predicate_arguments` 차원의 정의 변경 역시 판정 사안)

### Q22.4 — governance: PMB 단독 수용 source 금지의 해소 경로

D-21 §7-8: fixture ID 분할로는 불충족("distinct fixture sets ≠ distinct
source authority"), 해소는 (허용안 1) PMB + 독립 source 병행, (허용안 2)
manifest 조항 개정 — 귀하는 2를 비권고했다. 질문: **허용안 1의 제2
source 요건이 "20건 전부를 두 source가 나눠 공급"인가, "수용 게이트에
독립 source의 fixture가 유의미 비율로 포함"인가?** Q22.1-(b)를 택하면
다중 양화 담당 source가 자연스러운 제2 source가 된다 — 후보 조사가
필요하면 조사 채널에 위임할 준비가 되어 있다.

## 3. 판정 없이 진행 가능한 것 (병행 중)

- SBN→IR adapter의 **계약 설계 준비**(Q22.2 판정에 조건부 — 두 갈래 모두
  RED 계약 초안 가능)
- 자격 7항목의 SBN판 재실행 준비(adapter 착륙 시)
- Path A 스캔(adapter 능력)은 adapter 이후 — freeze 전 Path B와 대조
  (불일치 = FREEZE_BLOCKED, D-21 §15)

## 4. 검증 재현

스캔 전체가 `scan_pmb_eligibility.py` 하나로 재현된다(입력: 공식 archive
sha256 `1533d2a5…`의 en/gold 전개본). 분류 규칙의 근거는 스크립트
docstring에, 첫 census의 오분류(비교·시제 role 연산자를 box 연산자로
합산)와 그 정정도 기록돼 있다.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
