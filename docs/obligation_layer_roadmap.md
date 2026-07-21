# Obligation Layer — 구현 로드맵과 보류 설계

- **기원**: `docs/feedback/expansion_strategy_review_20260717.md` blocker 3축 → 해소 설계 논의(2026-07-18)
- **방법론**: 큰 아키텍처는 이 문서에 보존 → 현재 실제 문제만 최소 구현 → 실측 → 트리거 충족 시 다음 계층 추가

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

M1 ⬜ 첫 semantic obligation — relation.is_a (L2 진입)
   HANDOFF R2(관계 반례 검사)를 obligation으로: is-a 후보에 반례 질문
   4종(instance-of/role/phase/part-of 아닌가)을 적용. 결정론 규칙로
   검사 가능한 부분은 gate(RULE_CHECKED), 나머지는 LLM 제안
   (SOURCE_ANCHORED 상한)으로 분리.
   → 최초의 certificate-only 신호: 기존 status/lint/anti_patterns가
     전부 침묵하는데 obligation만 미충족인 상태가 처음 생긴다.
   검증: E2. 완료 기준: E2에서 ARM 분기 검출.
   E2 결과(2026-07-19): 천장 효과 재현 — arm 간 행동 격차 0(실증 불가).
   signal_mentioned check로 "신호 전달됨·행동 미변화" 확정. 원인: evidence
   문장 임시성 단서 잔존 → baseline 미침묵. laundering 0/13. 다음: E3(M2)
   또는 임시성 단서 제거 fixture로 E2 재실행(baseline 침묵 전제 충족 시).

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

### E2 — certificate-only 신호 A/B (M1 검증, E1 후속)

E1이 확정한 요구: "다른 신호 침묵 + 의무만 미충족" fixture가 있어야 ARM이
갈린다. M1의 relation.is_a가 그 fixture를 처음 가능하게 한다.

- **fixture**: 표면상 유효한 is-a(status PASS, lint 0, anti_patterns 0)이지만
  반례 검사에 걸리는 입력. 예: "선장 is-a 사람" — role을 kind로 위장한
  UFO 문헌의 고전 사례.
- **ARM A**: obligations 제거 응답 / **ARM B**: 포함. E1과 동일 프로토콜
  (Haiku 5+5 trial, tool 접근 0, 결정적 채점 — evaluate.py 패턴 재사용).
- **가설**: ARM A는 report_done(=false-done), ARM B는 repair/보류.
- **판정**: B repair율 > A → M1의 행동 가치 실증. 동일 → decider 신호
  전달 설계 재검토(tool description에 certificate 읽기 지침 추가 후 재실험 —
  tool_description_ab의 교훈: 클라이언트는 description만 읽는다).

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
