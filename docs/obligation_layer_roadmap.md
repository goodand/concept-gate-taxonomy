# Obligation Layer — 구현 로드맵과 보류 설계

- **기원**: `docs/feedback/expansion_strategy_review_20260717.md` blocker 3축 → 해소 설계 논의(2026-07-18)
- **방법론**: 큰 아키텍처는 이 문서에 보존 → 현재 실제 문제만 최소 구현 → 실측 → 트리거 충족 시 다음 계층 추가

## 목적 계층

```
L1 궁극: 인간-LLM 협업 개념 지식을 형식 추론의 보증을 받아 신뢰 가능한 온톨로지로 누적
L2 조건: "document ⊨ formal model"을 기계가 보증 (LLM 변환의 의미론적 올바름 자동 판정)
L3 기술: obligation 시스템 + (필요 시) warm reasoner + content-addressed state
```

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
| dependency invalidation 로직 (TMS식 stale 전파) | 확장 루프(제안→검증→재제안) 실구현 시 |
| L1 result cache (canonical hash → 추론 결과) | 동일 reasoning 입력 반복이 실측될 때 |
| warm JVM reasoner gateway (2-service 분리) | 세션당 reasoner 호출 > 20 또는 p95 누적 > 60초 |
| R2/S3 content-addressed state 외부화 | client payload 한도 접근 시 |
| cache_token / HMAC / auth 강화 | 외부(비신뢰) 사용자 등장 시 |
| semantic obligation 33종 확대 | 선행 4종(evidence.full_support, relation.is_a, relation.part_of, definition.sufficient)이 benchmark 개선을 보인 후 |

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
