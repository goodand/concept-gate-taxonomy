# Obligation Layer — 구현 로드맵과 보류 설계

- **기원**: `docs/feedback/expansion_strategy_review_20260717.md` blocker 3축 → 해소 설계 논의(2026-07-18)
- **방법론**: 큰 아키텍처는 이 문서에 보존 → 현재 실제 문제만 최소 구현 → 실측 → 트리거 충족 시 다음 계층 추가
- **L3 의 갱신 대수 정본 (2026-08-30 연결)**: 아래 L3 "obligation 시스템" 이
  받은 obligation 을 **어떻게 갱신·롤백·기권하는가**는 이 문서가 아니라
  [[notes/research/logical-revision/mechanism_spec|Mechanism Spec]] 이 정의한다
  (feedback algebra 9종 · rollback frontier · obligation lifecycle · abstention).
  이 로드맵은 그 명세를 **알지 못한 채** 쓰였고, 이후 M1 의 `cg_obligations.py` 가
  그 명세의 obligation 층만 구현했다. 권한 경계 층은
  [[DESIGN_DIRECTIVE_refine_verify_semantic_compilation|Refine ↔ Verify DIRECTIVE]].

## 목적 계층

```
L1 궁극: 인간-LLM 협업 개념 지식을 형식 추론의 보증을 받아 신뢰 가능한 온톨로지로 누적
L2 조건: "document ⊨ formal model"을 기계가 보증 (LLM 변환의 의미론적 올바름 자동 판정)
L3 기술: obligation 시스템 + (필요 시) warm reasoner + content-addressed state
```

## 마일스톤 체인 (L1에서 역방향 도출, 2026-07-18 확정)

현 상태 진단: L3 최소핵 달성(M0), **L2는 0%** — 등록된 obligation 7종 전부가
기존 결정론 검사의 거울이라 `문서 의미 ⊨ 추출 주장`(HANDOFF §9 R5의 갭)을
판정하는 semantic obligation이 하나도 없다. E1이 이를 실증했다(아래).

```
M0 ✅ 권한 경계 (L3 최소핵)
   verdict/assurance 분리 + Decider Registry(cg_obligations.py) +
   파이프라인 배선(run_pipeline/expand/classify_owl 응답 obligations 필드).
   E1 완료(음성): 거울 obligation은 행동 변화 한계 효과 0 (천장 효과 —
   anti_patterns/lint가 이미 시끄러운 실패 모드에선 타입 재표현일 뿐).
   reasoner 지연 실측: min 475 / median 498 / p95 539 ms.

M1 🟡 첫 semantic obligation — relation.is_a (L2 진입, 주효과 달성·directed-PC 결함 원인 규명 및 단일 레버 확정)
   HANDOFF R2(관계 반례 검사)를 obligation으로: is-a 후보에 반례 질문
   4종(instance-of/role/phase/part-of 아닌가)을 적용. 결정론 규칙로
   검사 가능한 부분은 gate(RULE_CHECKED), 나머지는 LLM 제안
   (SOURCE_ANCHORED 상한)으로 분리.
   → 최초의 certificate-only 신호: 기존 status/lint/anti_patterns가
     전부 침묵하는데 obligation만 미충족인 상태가 처음 생긴다.
   검증: E2. 완료 기준: E2에서 ARM 분기 검출.

   E2 결과(2026-07-19, 최초 A/B): 천장 효과 재현 — arm 간 행동 격차
   0(실증 불가). signal_mentioned check로 "신호 전달됨·행동 미변화" 확정.
   원인: evidence 문장 임시성 단서 잔존 → baseline 미침묵. laundering 0/13.

   E2 재설계(2026-07-19~23, 신호분해 3-arm A/C/B + truth oracle):
   - E2.1(clean baseline, 2026-07-19): B/C 내용 동등 기계 보장 확인,
     코드펜스 문제로 실측 실패 → schema-forced 출력으로 전환 필요성 확인.
   - E2.2(B-C 구조 확증, 2026-07-23, 154 trial): **주효과 달성** —
     구조화 certificate(B)가 평문 warning(C)보다 무근거 report_done을
     유의하게 더 억제 (Δ_BC=+0.32, 순열검정 p=0.00055, 부트스트랩
     CI95=[0.16, 0.48]). Go/No-go 6기준 중 5개 통과, **directed PC만
     실패**(0/10) — 사전등록 해석 규칙상 주효과 자동 무효화 아님.
   - E2.2.1(directed PC 마이크로 보정, 2026-07-24, 20 trial): directed
     PC 실패 원인을 "모델이 structural_composition 단어를 모른다"는
     가설로 보고 vocabulary를 prompt/schema에 노출 → 0/10에서 3/20(15%)로
     소폭 개선했으나 임계치(0.80) 미달, **가설 기각**. 실제 원인은
     vocabulary 부재가 아니라 **명세되지 않은 두 구조 계약**이었음이
     trial report 텍스트에서 직접 확인됨(아래).

   완료 판정: M1의 원 완료 기준(E2 ARM 분기 검출)은 E2.2로 충족. repair
   상황에서 발견된 결함(아래)은 E2.2.1~E2.2.3로 원인 규명과 요인 분해까지
   완료됐으나, 그 함의를 반영한 certificate 재설계는 아직 착수 전이라 M1은
   "핵심 실증 완료 + 재설계 대기"로 재분류.

   **발견된 hidden contract 결함 (E2.2.1 근본 원인 분석, 2026-07-24)**:
   certificate가 모델에게 전달해야 했지만 한 번도 명시하지 않은 구조적
   불변조건 2개가 있었다.
   1. 동일 feature 이름은 **모든 concept에서 type이 전역적으로 일치**해야
      한다는 불변조건 부재 → wrong_direction_repair 55%: 모델은 각
      concept의 evidence 문장을 독립적(concept-local)으로 해석해
      "다른 concept은 다른 type이어도 의미론적으로 정당하다"고 합리화함
      (trial 3 report: "a structural component in 돌체 and a functional
      role in 돌체린" — 이걸 해소로 착각).
   2. repair 출력(`repaired_concepts`)이 **partial diff가 아니라 전체
      state**여야 한다는 출력 계약 부재 → destructive_repair 30%: 모델이
      충돌을 정확히 인지하고도(trial 9) 수정한 concept만 반환하고 나머지는
      누락.
   → 결론: 실패는 모델 능력 부족도 vocabulary 미노출도 아니라, **실험
     설계가 명세하지 않은 구조 계약을 모델이 추론해주길 기대**한 누락.

   **E2.2.2(directed PC 마이크로 보정 라운드 2, 2026-07-24, 20 trial)**:
   E2.2.1의 실제 trial report에서 확인된 두 hidden contract를 (a) prompt
   규칙으로 명시하고 (b) 계약 2는 스키마 minItems로 구조적으로도 강제 →
   20/20(1.00) **완전 회복**. 단, 세 개입(A=전역 일관성 규칙, B=complete-state
   규칙, C=schema minItems)을 동시에 넣어 무엇이 필요/충분했는지 알 수 없는
   상태로 남음 — 결과 커밋이 직접 이 후속 과제를 명시.

   **E2.2.3(directed PC 3요인 OFAT ablation, 2026-07-25, 60 trial)**: A/B/C를
   각각 단독 arm(N=20)으로 분리. 결과는 비대칭적이고 결정적이었다:

   | arm | 내용 | rate | 판정 |
   |---|---|---|---|
   | A_ONLY | 전역 일관성 규칙만 | 20/20 = 1.00 | 단독으로 완전 충분 |
   | B_ONLY | complete-state 규칙만 | 1/20 = 0.05 | 기저선과 통계적으로 무차별 |
   | C_ONLY | schema minItems만 | 0/20 = 0.00 | 기저선과 통계적으로 무차별 |

   즉 E2.2.2의 "3요인 결합 수정"은 실제로는 **A 하나가 필요충분조건**이고
   B·C는 얹혀간 것이었다. 부수 발견: E2.2.1에서 30%였던 destructive_repair
   (concept 누락)가 E2.2.3 60 trial 전체에서 0건 — B_ONLY/C_ONLY도
   실패했지만 전부 wrong_direction_repair(방향 불일치)였지 concept을
   빠뜨리지는 않았다.

   **재해석(2026-07-24 초안 → 2026-07-25 E2.2.3 결과로 확정)**: certificate의
   역할을 "모델에게 더 강한 warning을 주는 신호"에서 **"모델이 유지해야 할
   전역 불변조건과 출력 상태 계약을 명시하는 reasoning contract"**로
   재정의한다. E2.2.3는 이 재정의의 핵심 함의 하나를 이미 실증했다: **불변조건을
   자연어 관계 규칙으로 명시하는 것이 스키마 구조 강제보다 강력한 레버였다**
   (C_ONLY=0.00 — cardinality 강제는 그 자체로 repair 방향을 만들지 못함).

   Before/After — certificate의 역할:

   | 축 | Before (E2.1/E2.2 단계) | After (E2.2.1~E2.2.3 이후) |
   |---|---|---|
   | 주 질문 | structured certificate가 plain warning보다 unsafe finalization을 더 줄이는가 | certificate가 reasoning state의 불변조건을 명시하고 보존시키는가 |
   | 실험 단위 | 단일 response의 decision 행동 | 판단-보류-repair의 상태 전이 |
   | certificate 역할 | 판단 보조 신호, 경고의 구조화 표현 | 경고 신호가 아니라 계약 객체 |
   | 주요 성공 신호 | request_evidence 증가, 무근거 report_done 감소 | hidden invariant가 prompt 밖에 남지 않고, 모델이 global state 기준으로 행동 |
   | 주요 실패 해석 | warning을 충분히 강하게 전달 못했거나 모델이 repair 방향을 못 고름 | 모델 능력 부족보다 계약 누락·state 범위 누락·output semantics 누락을 우선 의심 |

   **다음 마일스톤의 주 설계 원칙** (E2.2.3 결과로 뒷받침됨):
   1. **불변조건을 실험 대상으로 올린다** — "동일 feature 이름은 동일
      type이어야 한다" 같은 규칙을 채점기 내부 기대값으로 묻어두지 않고,
      certificate가 운반하는 명시적 contract 필드로 표현한다.
   2. **vocabulary/자연어 규칙/schema 강제를 층위로 분리해 실험한다** —
      E2.2.1~E2.2.3가 보여준 것처럼 이 셋은 서로 다른 층위이며, "prompt를
      더 자세히 줬더니 좋아졌다"로 뭉뚱그리면 안 된다.
   3. **repair를 local edit가 아니라 global state normalization으로
      정의한다** — repaired_concepts가 diff인지 complete state인지 모호하면
      모델은 partial diff를 낼 합리적 근거를 갖는다.
   4. **schema는 backstop이지 의미론 자체가 아니다** — C_ONLY=0/20이 실증:
      cardinality 강제(minItems)는 complete-state 누락은 막아도 repair
      *방향*(feature identity의 전역 일관성)은 만들지 못한다. 별도 계약으로
      표현해야 한다.

   다음 실험(E2.3 또는 이어지는 마일스톤)의 개념적 초점:
   - 모델이 feature-name 단위 전역 일관성을 유지하는가 (E2.2.3로 단독
     충분성 확인됨 — 이제 이 규칙을 certificate 자체에 어떻게 실어
     보낼지가 다음 질문)
   - repair를 local justification이 아니라 global state normalization으로
     수행하는가
   - repaired_concepts를 diff가 아니라 complete state로 이해하는가
   - repo/reasoner/schema를 결합할 때도 같은 전역 불변조건이 유지되는가
     (새로 추가된 질문 — repo 결합 실험의 전제조건)
   상태: 개념적 방향 확정 + 핵심 레버(자연어 관계 규칙 > schema 강제 단독)
   실증됨. 구체 설계(fixture/arm/N, repo 결합 여부)는 아직 없음.

M2 ⬜ evidence.full_support (L2 확대)
   claim의 모든 성분이 evidence span 집합으로 지지되는가 (MEG 원리).
   LLM decider — assurance 상한이 SOURCE_ANCHORED이므로 min_assurance에
   미달, aggregate는 UNKNOWN에 머문다 (세탁 불가 구조의 실전 검증).
   검증: E3. 완료 기준: false-PASS 0 + UNKNOWN 분포 실측.

M3 ⬜ 선행 4종 완성 + gold benchmark (L2 판정 품질)
   relation.part_of + definition.sufficient 추가 → 선행 4종 완성.
   검증: E4. 완료 기준: gold set에서 함정 재현율 > 오탐율.
   33종 확대는 이 결과가 트리거 (아래 보류 표와 일치).

M4 ⬜ 누적 루프 (L1 진입)
   제안→검증→재제안 확장 루프 + dependency invalidation(아래 보존 설계 —
   이 시점이 트리거 발동). client-carried state envelope 최소형.
   검증: E5 (기존 analyze_expansion 재사용). M1 이후 M2·M3과 병렬 가능.

M5 ⬜ 신뢰 소비 (L1 완성)
   인증된 온톨로지의 외부 소비(export/타 시스템 연결). 트리거 기반
   인프라(warm JVM, R2, auth)는 실측 조건 충족 시에만. M3+M4 이후.
```

의존성: M1→M2→M3 순차(각 실험 결과가 다음 설계의 입력), M4는 M1 이후
병렬 가능, M5는 M3+M4 이후.

## 실험 설계 (E2~E5 — 각 마일스톤의 완료 게이트)

### E2 — certificate-only 신호 A/B → B-C 구조 확증 (M1 검증, E1 후속)

E1이 확정한 요구: "다른 신호 침묵 + 의무만 미충족" fixture가 있어야 ARM이
갈린다. M1의 relation.is_a가 그 fixture를 처음 가능하게 한다.

최초 설계(A/B, 위 문단)는 천장 효과로 실증 실패 → 신호분해 3-arm(A/C/B) +
truth oracle로 재설계. 실제 실행 체인과 결과는 위 M1 섹션 참조:
E2.1(clean baseline) → **E2.2(B-C 구조 확증, N=154): 주효과 확증
(Δ_BC=+0.32, p=0.00055) — M1 완료 기준 충족** → E2.2.1(directed PC
마이크로 보정, N=20): 가설 기각, hidden contract 결함 2건 발견 →
E2.2.2(결합 수정, N=20): 20/20 완전 회복, 요인 미분리 → **E2.2.3(OFAT
ablation, N=60): A_ONLY 단독 충분(1.00), B_ONLY/C_ONLY 기저선 수준 — 단일
필요충분요인 확정**.

**다음 실험(E2.3, 미확정)의 방향**: 위 M1 섹션의 Before/After 프레이밍과
4가지 설계 원칙 참조. 핵심 전환은 Δ_BC 반복이 아니라 certificate가
"전역 불변조건과 출력 상태 계약을 명시하는 reasoning contract" 역할을
안정적으로 수행하는지 검증하는 것. 구체 fixture/arm 설계는 아직 없으나,
**운영 프로토콜(N/threshold)은 확정**: `docs/experiment_screening_protocol.md`의
2-stage 순차 스크리닝(N=10·threshold=0.90 우선 실행 → 7~8/10이거나 핵심
주장에 직접 쓰이는 arm만 N=20으로 증분) 적용. 보고 시 "confirmed" 대신
screened/provisional/candidate gate 용어 사용.

> **병합 기록 (2026-08-01)**: 이 문서의 두 브랜치 판을 병합했다. E2/E2.1~E2.3
> 서술은 `claude/ontoclean-gufo-handoff-7cmq0v`(메인) 판을 채택했다 — 2026-07-25에
> 이 브랜치가 스스로 "병합 시 그쪽이 상위 서술이다"라고 남긴 지침에 따른 것이다.
> 아래 E2.4 절은 이 브랜치에만 있던 내용이라 그대로 보존했다.

### E2.4 — Repo-Grounded Evidence Sufficiency + Abstain/Repair Contract (design, 미실행)

E2.3이 synthetic fixture 위에서 A(전역 feature-type 일관성 규칙)의 일반화를
확인했다면, E2.4는 그 규칙이 **실제 repo-derived evidence** 위에서도
판단/보류/수리 경계를 안정적으로 유지하는지 검증한다. 설계 상세는
`experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/README.md`
참조 — evidence 출처는 `goodand/concept-gate-taxonomy` 자체 코드/문서/테스트/
커밋 메시지로 한정(외부 지식·타 저장소 금지), arm은 CONTROL_REPO/A_REPO/
CONTRACT_REPO 3개, CONTRACT_REPO는 evidence audit → sufficiency 판정 →
invariant 확인 → accept_report/repair/abstain 선택의 새 계약 스키마
(`evidence_contract_v1`)를 쓴다. **이 커밋 시점엔 설계 패킷(README +
스키마 2개 + prompt 블록)만 존재 — fixture 구성·매니페스트 생성·실행은
아직 없음.**


### E3 — UNKNOWN 정직성 실측 (M2 검증)

- 지지 완전/부분/무관 evidence 3계열 × N trial에서 LLM decider가 제안만
  하고 aggregate가 UNKNOWN에 머무는지 관측.
- **측정**: false-PASS 발생 건수(불변조건의 실전판 — 목표 0), UNKNOWN 비율,
  human_or_abstain 경로 노출 빈도.
- **판정**: false-PASS 1건이라도 나오면 M2 재설계 (세탁 구멍).

### E4 — 반례 검사 gold set (M3 검증)

- gold 10~20건: 유효 is-a/part-of 절반 + 함정 절반(instance-of, role,
  phase, member_of, 재질-객체 혼동).
- **측정**: 함정 검출 재현율 / 유효 관계 오탐율 (결정적 채점).
- **판정**: 함정 재현율이 오탐율을 의미 있게 상회해야 33종 확대 트리거.

### E5 — 누적 수렴 (M4 검증)

- 확장 루프 N회에서 invalidation 후 재수렴 여부 — 기존
  analyze_expansion(converged/stalled/oscillating) 재사용.

## 지금 구현 (blocker 1만 — 결정론 세탁 차단)

`conceptgate/cg_obligations.py` 한 파일, stdlib only, 배포 불변:

- `Verdict {PASS, FAIL, UNKNOWN}` × `Assurance {PROPOSED < SOURCE_ANCHORED < RULE_CHECKED < REASONER_PROVED < HUMAN_APPROVED}` 2축 분리
- `MAX_ASSURANCE[decider]` — **LLM 상한 = SOURCE_ANCHORED** (RULE_CHECKED 이상은 결정론 검사기·reasoner·사람만)
- `OBLIGATION_REGISTRY` — 현재 코드베이스에 decider가 실존하는 obligation만 등록
- `ObligationResult.depends_on` — provenance 필드만 (invalidation 로직은 트리거 대기)
- CI 불변조건: registry 완결성 / LLM 상한 / PASS 최소 assurance / decider cap

## 보류 계층과 도입 트리거

| 보류 항목 | 도입 트리거 |
|---|---|
| dependency invalidation 로직 (TMS식 stale 전파) | 확장 루프(제안→검증→재제안) 실구현 시 (= M4) |
| L1 result cache (canonical hash → 추론 결과) | 동일 reasoning 입력 반복이 실측될 때 |
| warm JVM reasoner gateway (2-service 분리) | 세션당 reasoner 호출 > 20 또는 p95 누적 > 60초. E1 실측: median 498ms/호출 → 60s 예산 ≈ 120회/세션. 기존 ">20회" 트리거는 실측 대비 6배 보수적 — 유지하되 근거 병기 |
| R2/S3 content-addressed state 외부화 | client payload 한도 접근 시 |
| cache_token / HMAC / auth 강화 | 외부(비신뢰) 사용자 등장 시 |
| semantic obligation 33종 확대 | 선행 4종(evidence.full_support, relation.is_a, relation.part_of, definition.sufficient)이 benchmark 개선을 보인 후 — 실험 게이트: E2(행동 분기) → E3(false-PASS 0) → E4(gold set 재현율 > 오탐율) |

## 보존 설계 결정 (트리거 발동 시 이 사양대로)

### Canonical reasoning hash
```
reasoning_input_hash = SHA-256(
  "cg-canonicalizer@1" || base_artifact_id || base_artifact_sha256
  || canonical_axiom_set || reasoner_name || reasoner_version || reasoning_options)
```
- `canonical_axiom_set`: 지원 공리 범위의 **typed structural serialization** (toString() 정렬 금지 — 전체 IRI, axiom/operand type 명시, 무순서 operand는 자식 encoding 정렬, 길이-prefix 결합)
- 클라이언트 `input_sha256`은 non-authoritative hint(L0). 권위 키는 서버 canonicalizer 산출물
- 목표는 structural equivalence — 논리적 동치까지 같은 hash를 보장하지 않음 (그것 자체가 reasoning 문제)
- RDF blank node는 OWL structural parse 이후 canonicalize하므로 캐시 키에 들어오지 않음 (gufo.owl의 DisjointUnion RDF list 포함). anonymous individual 지원 시 별도 처리

### 캐시 계층
```
L2 base cache: base_artifact_sha256 + parser/canonicalizer version → parsed base ontology 재사용
              (classified reasoner 재사용은 backend capability에 따름 — per-call HermiT면 parse 절약뿐)
L1 result:    reasoning_input_hash → consistency/hierarchy/equivalence/unsat + reasoner metadata
L0 hint:      정확성에 영향 없어야 함. hint만으로 cache hit 금지
```
재시작 시 L1/L2 소실은 정상 (단일 사용자·소형 ontology 전제).

### 배포 (트리거 발동 시)
```
concept-gate-taxonomy.onrender.com        → Python MCP (control plane, stateless)
concept-gate-taxonomy-docker.onrender.com → reasoning plane (POST /reason/check|classify, /warm-session?level=)
```
- 무료 tier: keep-alive 금지 (750h/workspace 공유). cold start chain은 `/warm-session` 병렬 wake로 해소
- artifact 계약: `artifact_id + artifact_sha256` fail-closed 검증. gufo.owl은 body 전송 금지(이미지 내장)
- 상태 기계: `AVAILABLE → LOADED → CLASSIFIED`
- ELK fast path 제약: gufo.owl 전체는 OWL 2 EL 불가(`owl:disjointUnionOf` covering axioms). 후보 공리 단위 OWL2ELProfile 검사로만 라우팅. ELK FAIL은 신뢰(EL⊂DL monotone), PASS 인증은 HermiT/Openllet
- verdict `CONFLICT`와 admissibility 직교 축(consistency/entailment/novelty/impact)은 다중 decider 상황이 실재할 때

### Rollback 의미론 (확장 루프 도입 시)
- "undo"가 아니라 **dependency invalidation**: append-only event + `depends_on` 그래프의 후손을 stale 표시
- reasoner justification 불요. 복합 inconsistency 원인 분석에만 locality module + explanation
