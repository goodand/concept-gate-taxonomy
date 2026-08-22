# SBN adapter (PMB_SBN_5_1 profile) 설계 실측 기록 — 2026-08-23

D-E2E-v1-22 Q22.2가 명령한 source-결박 codec의 **계약 전 형식 실측**(M12).
wikisem 라운드의 교훈(발명 데이터는 저자의 전제를 공유한다 — P15) 때문에
RED 계약보다 실측이 먼저다. 모든 실물 인용은 공식 archive(sha256
`1533d2a5…`) 로컬 캐시에서 읽었고 repo에는 구조 기술만 남긴다.

## 1. 탐색 종결 기록 (프로토콜 1→2→3)

- **1단계 workspace**: SBN 파서 부재(쿼리 4종 기록됨). 이전 가능 기제 5종
  확정 — 예외 분류(AdapterUnsupported/SyntaxError)·산출 검증
  (validate_formula)·BOX_OPS census 상수·`%` 주석 분리·whitelist choke.
- **2단계 github**: 유일 후보(pmb-sbn-extractor, MIT)를 lead 재실측으로
  **기각** — 실체는 심리언어학 데이터 분석 repo(수십 MB TSV), sbnutils.py는
  하드코딩 홈경로+import 부작용의 연구 글루. 조사 subagent의
  "SUBTREE-WORTHY" 판정이 뒤집힌 P12 사례. 그 외 후보는 무라이선스이거나
  wrong layer(생성기/평가기).
- **결정적 발견**: 공식 archive가 **자체 파서를 동봉**한다
  (`src/sbn/sbn_spec.py` + `sbn2penman.py`, ud-boxer 계열, networkx/penman
  의존, **코드 라이선스 미명시** — PMB_LICENSE는 annotation 대상). 따라서
  **사양 정본으로만 참조**하고 코드 이식은 하지 않는다. → **3단계 TDD**.

## 2. 문법 정본 (sbn_spec.py에서 확인한 실행 가능 사양)

- `SYNSET_PATTERN = (.+)\.(n|v|a|r|x)\.(\d+)` — lemma에 `_`·특수문자 허용
- `INDEX_PATTERN = ((-|\+|\<|\>)\d)` — role 대상의 상대 참조(synset 행
  순번 기준, `target = 현재 synset idx + k`)
- `NEW_BOX_INDICATORS` 17종(NEGATION·CONJUNCTION·POSSIBILITY…) /
  `DRS_OPERATORS`(EQU·TPR·APX…) / `ROLES`(~70종) — 3계급이 상호 배타
- 상수: quoted Name, 요일·now·speaker 등 리터럴, 연도 `'NNNN'`, 수량
- 알려진 함정(스펙 주석): "-1도" 같은 상수가 인덱스로 오인될 수 있음 —
  fail-closed 사유로 채택

## 3. box 배선 규칙 (sbn2penman.from_string에서 확인)

- synset 행 → 노드 + **현재 active box**에 소속
- `NEGATION <1` 류 → **새 box를 열고 이전 box에서 op 엣지** → 이후 synset
  행은 새 box 소속. box 참조는 사슬상 직전(`<1`)만.
- **동봉 파서의 자기모순 실측**: 주석은 "전 데이터셋에 `<1`뿐"이라며 그 외를
  SBNError로 거부하는데, gold p20/d2820에 `CONJUNCTION <2`가 실재한다 —
  동봉 파서가 자기 릴리스의 gold를 못 파싱하는 코너. **우리 후보 풀(695)
  에는 box-op⊆{NEGATION} 필터 덕에 이 코너가 0건**(전수 재확인) — v0는
  `<1`만 지원, 그 외 fail-closed로 충분하다.

## 4. ∀ codec — 실물로 확정된 paired-negation 패턴

"Everyone but Jim came." (p66/d2061, 구조만):

```
b0 ─NEG→ b1 [ person(x), x NEQ jim ]   ← restriction
b1 ─NEG→ b2 [ come(e), Theme(e,x), … ] ← body
```

= ¬∃x(R(x) ∧ ¬S(x)) = ∀x(R→S). **codec 규칙**: NEG로 연 box가
(a) synset ≥1개를 담고 (b) 그 box에서 다시 NEG를 열면 → `forall`
(restriction = (a), body = (b)의 내용). 홀수 사슬 "Not everyone was
happy"(p76/d2248)는 바깥에 NEG 하나 더 = `not(forall …)` — 채점 대상인
양화↔부정 scope가 IR에 보존된다.

**음성 판별(자격 항목 9)**: 단일 NEG(단순 부정 189건)는 `not`; restriction
box가 비었거나 body-NEG가 없으면 forall로 복호하지 않는다; codec은
`PMB_SBN_5_1` profile에만 결박 — 커널·일반 canonicalizer의 ¬∃¬ 재작성은
금지 유지(D-22 §4).

## 5. IR 매핑 (v0)

- synset 행 = 담화 지시체 도입 → `exists`(box 소속 위치에서) + 단항
  `pred(lemma-정규화명, [x])` — 술어명은 O1_PMB_LEMMA_NO_SENSE_V1
  (synset→lemma·소문자)를 **adapter 산출 시점이 아니라 평가 profile에서**
  적용할지, adapter가 정규화명을 내고 원 synset을 부기할지 → **계약
  시점에 확정할 유일 미결**(D-22는 평가 profile 위치만 명령; adapter 산출
  형식은 구현 재량이나 expected_ir_sha256 고정에 영향)
- role/DRS-op 토큰 = 이항 `pred(role명, [x_src, x_tgt])`; 상수는 entity
- box 내용 = `and`; NEG box = `not`; paired 패턴 = `forall`(§4)
- constructor profile(O1-v1): `(forall, exists, and, pred, not)` — `not`은
  D-22 §16이 quantifier_negation_scope를 PMB 현상 목록에 명시함으로써
  승인된 것으로 해석(사전등록 동결 시 profile hash에 포함)

## 6. 자격 9항목 매핑

1~7은 wikisem판과 동형(입력만 SBN). 8 = §4 codec의 결정 복호. 9 = 복호
왕복(forall → 참조 SBN 재인코딩 → α-동치) + §4 음성 판별 3종.
