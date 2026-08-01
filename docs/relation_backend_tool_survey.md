# 관계 의미론 백엔드 도구 조사 — 외부 분석 3건 정리 (2026-07-23)

> [!주의] 이 문서의 성격
> 사용자가 외부에서 받아온 세 건의 비평/추천을 **압축·인용**한 것이다. 이 세션이
> 직접 검증한 사실이 아니다 — 언급된 repo 존재·release 버전·라이선스 등은
> 재검증하지 않았다(참고: [[reference|Project_in_progress/benchmark-references.md]]
> 는 반대로 이 세션이 직접 grep해 만든 색인이라 성격이 다르다). 이 문서는 어떤
> 도구도 채택·기각하지 않는다.

## §1. 관계 의미론 커널 후보 비교 (외부 분석 1)

"온톨로지를 많이 만드는 것"이 아니라 "관계 의미를 분해하고 모순 없이 정의를
고정하는 것"이 목적이라는 전제 하의 비교.

| 후보 | 판정 | 근거 요약 |
|---|---|---|
| `oOo0oOo/lean-lsp-mcp` | **단일 선택 시 1순위** | Lean 정리증명기를 MCP로 연결. 관계를 타입 있는 정의로 고정하고(`member_of: Person × Group` 등), `member_of ≠ part_of` 같은 구분을 라벨링이 아니라 **정리(theorem)**로 증명 가능. 관계별 inference discipline 분리에 최적 |
| `rikarazome/prolog-reasoner` | 빠른 프로토타이핑 보조 | 규칙 실행·relation taxonomy 실험엔 좋으나 "정의 자체의 논리적 정합성"을 강하게 보장하진 않음 — 최종 기준점으로는 약함 |
| `leungBH/owl4agents` | OWL/DL 비교 참조 | is-a/object property/consistency/claim verification엔 적합하나, 목적이 "로컬 OWL 추론"보다 좁고 근본적인 "관계 의미론 해체"라 meta-level definition control이 더 중요한 이 프로젝트엔 부족 |
| `fabio-rovai/open-ontologies` | 범위 과다 | 활동은 활발하나 ontology lifecycle 전반이 관심사라 "relation semantics kernel"이라는 좁은 문제엔 과함 |

**권장 조합**(외부 분석 원문): 기준 저장소 `lean-lsp-mcp` → 정식 정의·금지 규칙,
보조 `prolog-reasoner` → 빠른 예문 실험, 필요 시만 `owl4agents`로 OWL/DL 비교.

> [!경고] 기존 계획과의 미해결 긴장
> [[prolog_relation_backend_dynamicworkflow_plan.md]]는 이미 `prolog-reasoner`를
> 실험 대상으로 Phase 0~6 실행 설계를 완성해 뒀다(cg_normalizer.claims 결합,
> 4값 verdict, Dynamic Workflows 스크립트 설계 포함). 이번 외부 분석은 "단일
> 선택이면 prolog-reasoner가 아니라 lean-lsp-mcp"라고 **정반대 결론**을 낸다.
> 이 문서에서 임의로 절충하지 않는다 — **어느 쪽을 실제로 실행할지는 아직
> 결정되지 않은 상태**로 남긴다. 결정 시 이 표와 기존 계획 문서를 나란히 놓고
> 판단할 것.

## §2. E2 실험 재설계 재사용 경계 — 완료 기록 (외부 분석 2)

**상태: 이미 커밋 `0986bc3`으로 구현 완료.** 아래는 그 설계 근거를 압축한 것 —
새로 할 일 없음, 기록용.

| 재사용(그대로 유지) | 재사용 금지(교체함) |
|---|---|
| `ParseGate`, `ConceptPipeline` | `cert["verdict"]=="pass"`를 semantic truth로 쓰는 규칙 → `mechanically_certified`/`truth_preserving`/`safe_effective` 3축 분리로 교체 |
| `results_from_pipeline()` — 필드 부재≠빈 배열 구분 유지 | `"선장"` 하드코딩 → fixture의 `oracle.parent/child/honest_categories`로 이동 |
| `results_from_isa()` | `response_full`/`response_stripped` 이중 저장(drift 위험) → 단일 canonical 응답 + `make_arm()` projection(A/C/B)으로 교체 |
| `certify()` — 단, 구조 검증용이지 semantic oracle 아님 | repair율 단독 1차 지표 → `unsafe_finalize`/`metadata_laundering`을 별도 harm 지표로 분리 |
| E1의 자기보고 배제 원칙, MixRig positive control fixture | — |

실제 구현은 [[isa_certificate_only_ab README|experiments/2026-07-18_isa_certificate_only_ab/README.md]]
(E2)와 커밋 `0986bc3`, 그리고 read-only 감사 결과(mixrig 안전판정 가드 일부
누락 — 별도 패치 후보로 이미 기록됨)를 참고.

## §3. Ontology-learning / extraction 도구 비교 (외부 분석 3)

"OntoGPT보다 나은 대안"을 묻는 질문에 대한 답 — 단일 대체재가 아니라 **역할
분담**이 결론.

| Repo | 강점 | ConceptGate 적합성 |
|---|---|---|
| `monarch-initiative/ontogpt`(SPIRES) | schema-constrained extraction, 여러 provider 지원 | atomic claim proposer로 계속 유효 — 폐기 대상 아님 |
| `sciknoworg/OntoLearner` | term typing/taxonomy discovery/non-taxonomic RE/Text2Onto를 명시적 task로 분리, 150+ ontology·20+ domain 벤치마크, MIT | **단일 대안 선택 시 1순위** — proposer가 아니라 candidate 생성·평가 계층 |
| `andylolu2/ollm` | taxonomy 부분그래프 전체를 fine-tuning으로 생성(개별 relation 예측이 아니라 backbone 전체) | evaluation-only clone — 검증기 대체 부적절(source span/provenance/OWL round-trip 없음) |
| RELATE(2025 biomedical RE) | LLM 추출 → ontology predicate embedding(SapBERT) → retrieval/rerank로 표준 predicate 정규화 | 메커니즘만 일반화해 재구현(SapBERT→domain-neutral embedding, Biolink→OBO+gUFO+ConceptGate registry) |
| RIGOR | RDB schema → iterative delta ontology, provenance-tagged, judge LLM 병합 | 아키텍처 아이디어 참조(state update/rollback 설계에 참고) — 입력이 RDB라 직접 재사용은 아님 |
| `HamedBabaei/LLMs4OL` | Task A/B/C(Term Typing/Taxonomy/Non-Taxonomic RE) 벤치마크 데이터셋 | dataset/benchmark clone — OntoLearner의 원천에 가까움 |
| DeepOnto | OWL 처리·verbalization | compiler 후단 참조 |

**권장 파이프라인**(외부 분석 원문 압축):

```text
Document
  → OntoGPT/SPIRES (atomic claim 후보)
  → OntoLearner (term type / taxonomy / non-taxonomic relation 경쟁 후보)
  → RELATE-style predicate retrieval (OBO/gUFO/ConceptGate registry로 정규화)
  → ConceptGate proof obligations (evidence/relation type/necessity/sufficiency/counterexample)
  → OWL compiler → verbalizer → HermiT sandbox → 인증된 온톨로지
```

도입 방식: OntoLearner·LLMs4OL·OLLM은 **optional import/별도 subflow/evaluation
clone**(코어 대체 아님), RELATE는 **메커니즘만 로컬 재구현**, OntoGPT는 proposer
역할 유지.

## §4. 상호 참조

- [[prolog_relation_backend_dynamicworkflow_plan.md]] — prolog-reasoner 결합
  실행 설계(§1의 미해결 긴장 대상)
- [[scior_reuse_audit.md]] — Scior(OntoClean 자동 분류기) 재사용 감사, 같은
  성격의 선행 문서
- [[ontoclean_research_context_packet.md]] — OntoClean 이론적 배경
- `Project_in_progress/benchmark-references.md` — 이 프로젝트가 조사한 논문·repo
  통합 색인(git 미적용 디렉터리에 위치, 별도 관리)

## §5. Out of Scope

이 문서는 어떤 도구도 채택/기각하지 않는다. subtree 추가, `CLAUDE.md` Subtree
Registry 갱신, 코드 변경 전부 없음 — §1의 긴장과 §3의 파이프라인은 향후 결정
시 참고할 입력일 뿐이다.
