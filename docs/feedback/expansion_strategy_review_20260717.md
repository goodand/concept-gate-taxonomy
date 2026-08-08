# 확장 전략 문서 타당성 검토 — 4-Agent 적대 검증 결과

- **대상**: `docs/expansion_strategy_semantic_compiler.md` (§1~§18, 1169행)
- **일시**: 2026-07-17
- **방법**: 검증 기준(ground truth)이 서로 다른 4개 독립 reviewer + lead 합성.
  persona 분할이 아니라 **근거 축 분할** — 각 agent는 다른 근거에만 대조하므로 발견이 상관되지 않는다.

| Agent | 검증 기준 | Finding 수 |
|---|---|---|
| A. Baseline Auditor (Haiku) | 현재 코드베이스 (§1 기준선 주장 16건 file:line 대조) | 16 |
| B. Formal Soundness (Fable) | OWL 2 DL 의미론, OntoClean/UFO/gUFO, mereology, vendored asset | 10 |
| C. Source Verifier (Sonnet) | 외부 논문·저장소 8건 웹 실측 | 8 |
| D. Feasibility (Fable) | CLAUDE.md Ponytail Rules, HANDOFF 로드맵, 테스트 계약, Render 배포 | 9 |

- **출력 계약**: `{section, claim, verdict, evidence, severity}` — evidence 없는 finding은 폐기(폐기 0건).
- **Lead 교차검증**: 최상위 finding 7건을 lead가 코드·자산에서 직접 재검증(본문 ✓ 표시, 기록은 말미).

---

## Part A — 종합 판정 (Lead 합성)

### TL;DR

> **방향은 타당하다. 그러나 쓰인 대로는 채택 불가 — 3개 blocker 축의 재작성이 선행 조건이다.**

43건 finding 분포: **CONFIRMED 23 / PARTIAL 11 / REFUTED 8 / UNVERIFIABLE 1** (blocker 4건, major 12건).

**살아남은 것 (검증된 강점):**
- 진단(§1 기준선 → §2 공백)은 정확하다. 기준선 주장 16건 중 14건 CONFIRMED, REFUTED 0건 — "document ⊨ formal model 미보장"이라는 중심 공백 진단은 코드 실측 위에 서 있다.
- §3.3 modality 분리(문서적 가능성 vs SAT(O∪{a}))는 형식적으로 모범적이다 — OWL consistency를 modal possibility와 혼동하지 않는 올바른 처리 (B 유일의 CONFIRMED).
- 외부 인용 8건 전수 검증에서 **반박된 것이 없다**. 핵심 인용 MEG는 수치까지 실측 일치(WiCE +18.4%p, SciFact +34.8%p), DeepOnto verbaliser의 OWLAPI 강결합(→선택 C 귀결)도 실제 아키텍처와 부합.
- 방향은 HANDOFF 로드맵 R5(semantic entailment critic) 및 저장소 철학(proposer/verifier 분리, 숫자 confidence 배제)과 정합.

**무너진 것 (3개 blocker 축):**

1. **결정론 세탁(determinism laundering)** — 문서의 핵심 서사 "LLM proposes, Typed gates decide"(§3.2)와 "신규 deterministic layer"(§13)는 지지되지 않는다. 39개 obligation 전수 분류 결과 순수 기계 판정은 **6개뿐이고 전부 기존 기능**(cycle/antisymmetry/배타성/inverse/SAT). §2의 공백을 메우는 신규 의미 obligation의 판정 주체는 **문서 전체에서 단 한 번도 지정되지 않는다**. 이 아키텍처는 미검증 LLM 판단을 제거하는 것이 아니라 한 층 아래로 이동시킨다 — 가치는 결정론이 아니라 감사 가능성(auditability)이다. [B-1, D-8: blocker]
2. **형식 코어 3개 미정의** — (i) obligation 결합 대수: sufficiency=UNKNOWN인데 decision=PRIMITIVE_SUBCLASS가 나오는 규칙이 미제시, CERTIFIED의 필요조건 미정의, counterexample=PASS는 탐색 실패를 검증 성공과 같은 토큰으로 기록하는 인식론 오류 [B-4: blocker]. (ii) §5.7 admissibility 어휘 non-MECE: ENTAILED/REDUNDANT 미구분, UNDERDETERMINED 미정의, base-inconsistent 시 ex falso로 전 후보 ENTAILED 인증되는 구멍 [B-3: major]. (iii) §5.2 selective rollback은 justification 추출(이 스택에 없음)을 전제하며 단조 논리에서 불건전 [B-7: major].
3. **실행 불가 2점** — (i) 후보별 HermiT sandbox: owlready2는 호출마다 `java -Xmx2000M` subprocess를 새로 기동(실측 0.6~1.6s/회 ✓), 후보당 4~5회 × claim×후보 조합 = certify 1회에 수백 회 JVM 기동 — Render Free(512MB)에서 시간·메모리 파산, 완화책 전무 [D-4: blocker]. (ii) 서버측 8-dict state store는 현행 완전 무상태 서버·영속 계층 없는 배포와 충돌 [D-9: major].

**저장소 자기 규칙 위반 (major):** 신규 15모듈/2서브패키지는 CLAUDE.md Ponytail 3조항(YAGNI/Fewest files/No abstraction) 정면 위반 — 동일 기능이 신규 1~2파일 + 기존 3파일 확장으로 가능 [D-1]. tool 9→20 확대는 자체 A/B 실험 증거(description 민감도, 0/5→4/5)에 역행하며 기준선(실제 11개 ✓, `map_owl` ✓)조차 부정확 [D-5]. §16 비율형 기준 12줄은 gold relation dataset 부재로 측정 불가 [B-10, D-7].

### Verdict Matrix (문서 섹션별)

| 문서 섹션 | 판정 | 근거 요약 | 출처 |
|---|---|---|---|
| §1 기준선 | **CONFIRMED**(14/16) | 검증 사다리·span/hash·primitive/defined·punning·동치 보정·gate 전부 실재. 도구 목록만 낡음(실제 11개, `map_owl` ✓) | A |
| §2 공백 분석 | **CONFIRMED** | 기준선이 정확하므로 공백 진단 유효 | A |
| §3.1 proof obligation | **PARTIAL** | 방향 유효; 결합 대수 미정의 + counterexample PASS 인식론 오류 | B-4 |
| §3.2·§13·§17 "typed gates decide" | **REFUTED** | 결정론 세탁 — 기계 판정 6/39(전부 기존 기능), 신규 의미 obligation decider 미지정 | B-1, D-8 |
| §3.3 modality 분리 | **CONFIRMED** | 형식적으로 모범적. §5.7:454 "대체" 표현만 과장(보완이 정확) | B-8 |
| §5.1 claim 중심 전환 | **CONFIRMED** | 기준선(verbatim label 집합 포함) 정확 — concept_gate_v7.py:888 | A |
| §5.2 state store + rollback | **REFUTED** | 논리(justification 부재, 복수 justification 과잉삭제) + 인프라(무상태 서버) 이중 반박 | B-7, D-9 |
| §5.3 hierarchy 리네이밍 | **PARTIAL** | 30+ 참조/7+파일 파괴(배포 스모크 포함 ✓); additive 확장 대안 존재 | D-3 |
| §5.4 evidence group (MEG) | **CONFIRMED** | 논문·형식화·수치(18.4%/34.8%) 실측 일치. 단 full_support decider는 entailment 모델임을 명심 | C-2, B |
| §5.5 modality obligations | **PARTIAL** | 축 분해는 타당(UDS 인용 정확), decider 공백 | B, C-3 |
| §5.7 admissibility | **REFUTED**(어휘) + **blocker**(비용) | non-MECE 어휘 + 후보별 JVM 기동 ✓ + O⊨a 일반 질의 하네스 부재 | B-3, B-6, D-4 |
| §6 모듈 구조 (15개) | **REFUTED** | Ponytail 위반; 신규 1~2파일로 동일 기능 | D-1 |
| §7 tool surface (9→20) | **REFUTED** | 기준선 오류(실제 11 ✓) + tool_description A/B 실험 증거 역행 | A-8, D-5 |
| §8.1 is-a gate | **PARTIAL** | ISA-8만 기계 판정(문서 자인 doc:550), ISA-1..7 decider 공백 | B-1 |
| §8.2 part-of subtypes | **PARTIAL** | PART-7 이론(WCH·gUFO·OBO) 정합. 그러나 자산 부재: gufo.owl ObjectProperty **0개** ✓, core.obo는 7종 중 2종 ✓, member_of⊑part_of 추이 누출 ✓, portion/subquantity 미구분, feature_of는 endurants-only에서 범주 착오 | B-9 |
| §9 round-trip gate | **PARTIAL** | 결정론 구현은 IR→OWL 자기검사(컴파일 충실도)만; 원문 대조는 제2 LLM 의견(N-version) — IR이 틀리면 잘못끼리 일치해 통과 | B-5 |
| §10~§12 외부 채택 결정 | **CONFIRMED** | 인용 전수 실재·정확. GLiREL/ReLiK **CC BY-NC-SA(비영리)** 미기재만 보완 필요 | C 전체 |
| §11.4 DeepOnto 선택 C | **CONFIRMED** | verbaliser의 OWLAPI 강결합 실증 — local reimplementation 권장은 근거 탄탄 | C-4 |
| §14 Phasing | **PARTIAL** | Phase 1 가치 낮음(완료된 R1을 파괴적으로 재시행), R2 건너뜀, Phase 3~4 decider 공백(XL), Phase 5 배포 blocker | D-2, D-8 |
| §15 API 예시 | **PARTIAL** | certification=CERTIFIED 필요조건 미정의 상태에서 결과 스키마만 확정 | B-4 |
| §16 성공 기준 | **PARTIAL** | `=0` invariant 7줄은 즉시 계약화 가능; 비율형 12줄은 gold set·sampling protocol 부재로 측정 불가(저장소 최대 표본 12 trial) | B-10, D-7 |
| §17 최종 서사 | **REFUTED** | "판단 제거"가 아니라 "판단 분해·귀속·감사 가능화"가 정직한 기술 | B-1 |

### 채택 조건 — 재작성 요구사항 12개

문서를 채택 가능하게 만드는 최소 수정 (agent들의 fix 필드 합성):

1. **Gate 2등급 분리**: deciding gate(기계 판정: cycle/antisym/배타성/SAT/hash)와 recording gate(의미 obligation — 판단자 신원·모델 버전·근거 span·threshold를 함께 기록)를 어휘 수준에서 분리. §13 "deterministic layer" 명칭과 §17 서사 수정.
2. **Decision function 명시**: CERTIFY_DEFINED ⟸ 전 obligation PASS; CERTIFY_PRIMITIVE ⟸ sufficiency∈{UNKNOWN,FAIL} 외 전부 PASS; ABSTAIN/REJECT 규칙 표로 고정. UNKNOWN·NOT_APPLICABLE 합성 규칙 정의.
3. **counterexample 상태 분리**: PASS 대신 `NOT_REFUTED(search_budget)` — 탐색 실패와 검증 성공을 같은 토큰에 두지 않는다.
4. **admissibility 어휘 재정의**: BASE_INCONSISTENT(전 후보 판정 중단), ADMISSIBLE_WITH_NEW_UNSAT 추가; REDUNDANT 폐기 또는 "구문적 기존 assert" 하위 플래그화; UNDERDETERMINED = reasoner 자원 한도/non-DL 공리로 정의. 검사 4(O∪{a}⊨⊥)는 검사 2와 동치이므로 제거.
5. **rollback 재정의**: "asserted claim 집합의 선택적 철회 + fresh World 전체 재분류로 entailed closure 재계산"(현행 build_ontology World-per-call과 정합). incremental entailment retraction은 ATMS 계열 미래 과제로 격리.
6. **admissibility 배치화**: 후보별 JVM 기동 금지 — 후보 배치를 단일 world에 태깅해 1~2회 분류, base ontology 캐시, 후보 수 상한(SizeGuard 패턴 재사용). O⊨a 일반 질의는 negation-injection 하네스 필요를 명시, value-restriction은 UNDERDETERMINED 처리.
7. **state-passing**: 서버측 store 금지. 기존 snapshot 전달 패턴대로 state JSON을 클라이언트 소유로 왕복시키는 순수 함수 설계 — rollback은 클라이언트의 부분 폐기+재호출.
8. **API additive**: `hierarchy`/`dag` 리네이밍 금지, 새 필드 추가만. (완료된 R1의 비파괴 등급 표시를 뒤집지 않는다.)
9. **모듈 절단**: 신규 1~2파일(claim IR + obligations + MEG coverage + certify) + cg_normalizer/cg_owl/server 확장. 서브패키지 금지, decider 미정 gate 파일 생성 보류.
10. **tool 표면**: `run_semantic_compiler` 단일(+검사용 1~2개), stage 결과는 응답의 구조화 필드로 노출. 기준선 정정(현행 11개, `map_owl`).
11. **§16 2층 분리**: `=0` invariant는 즉시 CI 계약으로(inverse 오류도 =0으로 강화); 비율형은 gold relation dataset 구축(수백 건 라벨링, IAA 절차)을 선행 Phase로 명시하기 전까지 "목표치"로 표기.
12. **part-of 어휘 실현**: portion_of/subquantity_of 통합, feature_of는 occurrent 지원 전 제외, full gUFO parthood property(isComponentOf 등) 재수입 또는 자체 ObjectProperty 선언 + subtype별 transitivity 표를 데이터로 고정. member_of⊑part_of 합성 누출 차단.

### 부수 발견 — 문서와 무관한 저장소 이슈 (수리 가치)

| 이슈 | 위치 | 내용 |
|---|---|---|
| 유령 이름 | `conceptgate/cg_partwhole.py:56` ✓ | `"constituted of"`는 core.obo에 존재하지 않는 이름 — 파싱 대상이 영원히 매칭되지 않음 |
| stale 문서 | `docs/MCP_SERVER.md` | 6도구 시대 기술, examples/ 경로도 stale — 계약 변경과 무관하게 동기화 부채 |
| 라이선스 리스크 | (도입 시) | GLiREL·ReLiK 모두 CC BY-NC-SA 4.0(비영리) — 상업 배포 고려 시 §12.1에 명시 필요 |

### Lead 교차검증 기록

subagent 환각 방어를 위해 lead가 직접 재실측한 항목:

1. `server.py` @mcp.tool **11개**, `map_owl`(server.py:700) — A-8, D-5 확인 ✓
2. `owlready2/reasoning.py:192` `subprocess.check_output(command)` — 호출당 java 기동 — D-4 확인 ✓
3. `hierarchy`/`dag` 참조가 venv 제외 **14개 파일**(배포 스모크 `render_mcp_smoke.py` 포함) — D-3 방향 확인 ✓
4. `conceptgate/data/gufo.owl`에 "ObjectProperty" 문자열 **0건** — B-9 확인 ✓
5. `core.obo`에 7 subtype 중 `part of`·`member of`만 존재 — B-9 확인 ✓
6. `core.obo:428` `member of is_a part of` + `part of is_transitive: true` — 혼합 추이 누출 — B-9 확인 ✓
7. `cg_partwhole.py:56` "constituted of" — B 보고의 :54는 2행 오프셋, 내용 정확 ✓

**충돌 해소 2건**: (i) §16 severity — B(minor) vs D(major) → **major** 채택: 문서 스스로 "테스트 계약"을 핵심 성취로 내세우는데 측정 전제가 부재하므로. (ii) stdlib-only — A(id 15)와 D(line 6) 통합: "게이트/노멀라이저 코어 6모듈 층위에서 참, 패키지·배포(owlready2+fastmcp+JRE) 층위에서 거짓; §11.1의 subflow 결론은 프로세스 분리·provider 격리 논거만으로 유지된다."

**한계 고지**: C의 MEG 수치는 1차 소스(arXiv/ACL PDF)가 403이라 복수 독립 2차 출처 교차 확인이다. MEG 공개 reference repo 존재는 미확인 — §11.2 "repo: 참고용 clone 가능"은 낙관적일 수 있음.

---

---

## 부록 — 검토 방법 재현

4개 reviewer agent는 각자 `{section, claim, verdict, evidence, severity}` JSON 계약으로
독립 보고서를 산출했고, 위 Part A는 lead가 이를 교차검증·합성한 결과다. Part A의
Verdict Matrix와 채택 조건 12개가 각 agent finding을 출처 표기(A-n/B-n/C-n/D-n)와 함께
반영한다. (agent 원본 보고서 전문은 이 커밋에 포함하지 않는다.)
