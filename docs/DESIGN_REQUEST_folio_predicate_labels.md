# DESIGN REQUEST — FOLIO 술어 라벨 규약 미정합의 해소 (Q24)

- 상신: 2026-08-23, 운영 세션 (Stage 2 동결 후, 코호트 실행 전 smoke test가 적발)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: 이 판정 전까지 Stage 2 코호트 실행이 차단된다. 동결 표면
  (manifest·template·profile·사전등록)은 수정하지 않았다 — 해소 경로가 전부
  동결 표면이라서 D-19 §12(동결 후 변경은 외부 판정 사안)에 따라 상신한다

## 1. 배경 (필요한 최소한)

의미 컴파일 실험(E2E-v1 Stage 2)이 동결됐다: subject(무도구 LLM agent)가
영어 문장 1개를 IR(constructor 5종: forall/exists/and/pred/not)로 컴파일하고,
oracle(외부 저작 gold 논리식을 결정적 adapter로 IR화한 것)과 정규화 후
구조 비교(DirectMatch)로 채점한다. fixture 20건 = PMB 15(WordNet synset
술어) + FOLIO 5(다중 양화 전담, D-23이 제2 source로 승인) + FOLIO adapter
control 3건(N 밖, 3/3 통과가 코호트 해석 가능 조건).

**선행 판정 Q22.3(=a\*)**: PMB 술어는 synset(`happy.a.01`)이라 문자열 일치
요구가 estimand를 "scope 컴파일"에서 "scope+WSD"로 팽창시킨다 → 평가
profile `O1_PMB_LEMMA_NO_SENSE_V1`에서 **synset 패턴만** lemma·소문자로
정규화(occurrence·arity·topology 보존, 노드 병합 금지, 커널 반입 금지).

**D-23**: FOLIO의 구조 처리(∀+직속 함의의 제한식 강하, 중립 ∃, 접두 양화
순서 불변식, 함의 경계 넘는 재작성 금지 — 56/256 반례)를 확정했으나 **술어
라벨 규약은 다루지 않았다**(문서 전수 검색 0건).

**동결 template**: subject에게 "Use lowercase predicate names taken from
the sentence's content words"를 지시한다(PMB lemma 정합을 위해).

## 2. smoke test가 실측한 사실

코호트 밖 발명 재료 4건으로 동결 구성 전체(봉투 schema 5종, 실제 dispatch
경로, 실제 ingest/score)를 처음 live 관통시킨 결과:

1. **FOLIO adapter는 술어명을 원문 그대로 보존**한다(`Zorble`→`Zorble`).
   평가 profile은 synset 패턴(`^(.+)\.(n|v|a|r|x)\.(\d+)$`)만 소문자화하므로
   FOLIO형 술어는 대문자로 남는다. subject는 template 지시대로 소문자를
   낸다 → **라벨 불일치로 구조 정합과 무관하게 fail**. 최단순 대조
   실측: `∀x (Zorble(x) → Glims(x))` vs subject의 구조 동일 출력 —
   전체 소문자화하면 두 IR이 완전 동일한데 fail.
2. 동결 FOLIO 8건 전수: oracle 술어가 전부 대문자/CamelCase. 8건 중 4건은
   대소문자만 문제(`Lab`, `Eat`, `CanCatch`…), **4건은 문장에 등장하지 않는
   annotator 저작 어휘**(`SpectatorsBetOn`, `OnRoof`, `WentWrong`,
   `HoldingCompany`, `Racing`) — 소문자화로도 해소 불가.
3. 파급: control 0/3 확정(해석 가능 조건 미달), multi_quantifier floor
   0/5 확정(4/5 필요) → **PMB 성적과 무관하게 수용 불가가 사전 결정**.
4. 부수 관찰: FOLIO 표면 관행 `∀x∃y(A(x)∧B(y)→C(x,y))`(동결 FOLIO-142p1이
   이 형태)는 subject의 자연 독해 `∀x(A(x)→∃y(B(y)∧C(x,y)))`와 IR 구조가
   갈리고, D-23의 함의 경계 재작성 금지 때문에 비교층이 이어줄 수 없다 —
   smoke에서 동형 재료가 `operator_type`으로 fail했다.

## 3. 판정 질문

### Q24.1 — 라벨 규약 공백의 해소 방식

- (a) **평가 profile에 FOLIO 라벨 codec 추가**: FOLIO 유래 oracle에 한해
  술어명을 소문자화(예: `FOLIO_LABEL_LOWERCASE_V1`), Q22.3과 같은 지위
  (source-profile-bound, occurrence·topology 보존, 커널 밖). 대소문자만
  문제인 4건이 산다. 단 profile은 동결 표면(manifest descriptor에 hash
  포함)이라 개정·재동결 절차 판정이 §Q24.3에 필요
- (b) **subject template 개정**(대문자 허용/지시) — 운영 세션 비권고:
  PMB 15건의 lemma 정합을 깨고, template도 동결 표면이다
- (c) 비교층에서 술어명 대소문자 무시(case-insensitive compare) — 운영
  세션 비권고: source 무관 전역 규칙이 되어 Q22.3의 "profile-bound"
  원칙과 충돌
- (d) 그 외

### Q24.2 — 저작 어휘 gap 4건(문장에 없는 술어)의 처리

`SpectatorsBetOn` 류는 어떤 라벨 정규화로도 subject가 도달할 수 없다.

- (a) **해당 4건을 부적격으로 판정하고 fixture 교체**: 동결 선별 스크립트의
  seed·층 술어를 유지한 채, "oracle 술어가 전부 문장 파생 가능(대소문자
  무시 일치)"을 적격성 조건에 추가해 재선별. FOLIO 적격 풀(다중 양화 17건,
  control 후보 963건)에 여유가 있는지는 재선별 시 기계 실측 — 부족하면
  BLOCKED 보고 후 재상신
- (b) 라벨 차원을 FOLIO 트라이얼에서 채점 제외(구조·결박만 비교) — 운영
  세션 비권고: `predicate_arguments` 차원의 source별 이중 정의가 되고
  D-19 §12의 차원 정의 변경 사안
- (c) 그대로 두고 수용 기준을 완화 — 운영 세션 강력 비권고: 측정 불가능을
  알면서 실행하는 것
- (d) 그 외

### Q24.3 — 절차: 동결 후 결함 수정의 정본 경로

동결 커밋(f57ae12) 후 처음으로 동결 표면 결함이 발견됐다. 사전등록 문서에
개정 절차 조항이 없다. 이번 및 향후 재발 시의 정본 절차를 청한다 —
운영 세션 권고안: **(i)** 결함·판정·수정 diff를 사전등록서에 AMENDMENT
절로 verbatim 기록, **(ii)** manifest 재생성 시 변경된 entry만 교체하고
seed·층 술어 유지, **(iii)** 수정 전 결과가 존재하지 않음을 명기(코호트
미실행 상태의 수정임), **(iv)** 별도 커밋.

### Q24.4 — 부수 관찰(§2-4)의 지위

FOLIO 함의-양화 topology와 subject 자연 독해의 구조 갈림은:
- (a) estimand의 일부(FOLIO의 접두형 scope 구조를 재현하는 것 자체가 측정
  대상) — 그대로 두고, 예상 실패 형태로 사전등록에 기록만
- (b) 라벨과 같은 지위의 오염 — 추가 판정 필요
- 운영 세션 의견: (a) 쪽이나, D-23의 순서 불변식 판정 취지 확인을 청함

## 4. 검증 재현

- smoke 전문: `experiments/2026-08-23_e2e_v1_c_o1_cohort/SMOKE_TEST_20260823.md`
- B1 1줄 재현: `adapt_fol("∀x (Zorble(x) → Glims(x))")` 술어명 대문자 보존
  + `_stage2_eval_profile.SYNSET_PATTERN` 불일치로 정규화 미적용
- FOLIO 8건 술어 목록: SMOKE 문서 §2 표 (manifest+캐시에서 기계 재도출 가능)
