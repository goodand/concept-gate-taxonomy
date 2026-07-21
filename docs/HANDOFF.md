# HANDOFF — ConceptGate 세션 인수인계

- 작성: 2026-07-17 08:07 UTC
- 대상: **컨텍스트 없이 이어받는 새 세션**. 이 문서만 읽고 작업을 재개할 수 있게 쓴다.
- 다음 예정: **큰 설계 변경** (semantic fidelity 계층 — 아래 §9 R5). 그 전에 동치
  보고 체계를 완결한 상태에서 넘긴다.

> **먼저 이걸 하라**: 작업 시작 전 `verify-conceptgate` 스킬을 읽어라
> (`.claude/skills/verify-conceptgate/SKILL.md`). 이 프로젝트의 반복 함정과 검증
> 규율이 담겨 있다. 특히 "로그/기억이 아니라 실제 관측 경계에서 확인"이 핵심.

---

## 1. 지금 상태 한 문단 (TL;DR)

파생 동치(equivalence) 보고 체계가 **완결**됐다: `classify_owl`이
`equivalence_groups`·`has_nontrivial_equivalences`·`representatives`를 반환하고,
gUFO 경로에서 동치류 부모가 유실되던 결함을 그룹 부모 합집합으로 복원한다.
**로컬(pytest 93 그린) · 원격 브랜치 · Render 프로덕션 3계층 모두 라이브**로 검증됨.
작업 트리는 clean, 전부 커밋·푸시됨. 두 차례 적대적 검증(dynamic workflow) 통과.

## 2. 프로젝트 목적

**"LLM이 제안하고, 결정론이 판정한다."** 자연어를 evidence-carrying 개념으로
고정한 뒤, is-a 계층은 **풀 OWL 2 DL reasoner(HermiT)가 생성**한다. LLM의 is-a
환각을 "제안 vs 판정" 분리로 차단한다. 정본 소스는 `conceptgate/` 패키지 하나뿐.

## 3. 저장소 구조 · 핵심 파일

- `conceptgate/concept_gate_v7.py` — FCA 기반 코어(legacy DAG). `run_pipeline`의 뿌리
- `conceptgate/cg_normalizer.py` — L1: NL → evidence-carrying concepts JSON (LLM 미호출)
- `conceptgate/cg_owl.py` — **L3: OWL 2 DL 직렬화 + HermiT 분류** (이번 세션 작업 집중)
- `conceptgate/server.py` — MCP 서버(FastMCP). 11개 도구 노출. Bearer 인증 미들웨어(§7)
- `conceptgate/data/gufo.owl` — gUFO endurants-only 서브셋(owl:imports 대상)
- `test_cg_owl.py` — cg_owl 설계 증명 테스트 (P1~P10)
- `test_cg_owl_guards.py` — 입력 경계 가드 (Java 불필요)
- `docs/mechanism.md` — L1→L3 파이프라인 메커니즘 (mermaid)
- `docs/feedback/` — 설계 리뷰·적대 검증·의미충실도 비판 기록 (§9에서 참조)
- `.claude/skills/verify-conceptgate/` — 검증 규율 스킬 (§8)

## 4. 아키텍처: L1 → L3 파이프라인

```
agent(LLM 제안) → L1 cg_normalizer(결정론 경계, snapshot→lookup→selection→
  crosswalk→assemble) → concepts JSON → L3 cg_owl(map_to_owl→build_ontology→
  validate_gufo(SHACL, fail-open)→classify→HermiT) → 결과
```

핵심 설계 결정:
- **primitive(⊑) vs defined(≡)**: 자연종은 primitive(spurious is-a 차단), 형식개념은
  defined(reasoner가 다중 부모 자동 분류). "essential 집합 포함=is-a"(리뷰 발견 2)의 대체
- **stereotype punning**: gUFO IRI를 raw triple로 rdf:type 주입 → Kind⊥Phase 등 gUFO
  공리를 HermiT가 네이티브 적용
- **hierarchy는 entailed OWL** (model-theoretic 함의), run_pipeline DAG는 candidate
  feature (표면형 부분순서) — 인식론적 등급이 다름 (혼동 금지)

## 5. 이번 세션 완결 작업 — 동치 보고 체계

### classify_owl 반환 계약 (현재)

```
{ok, stage,
 hierarchy: {클래스: [유도된 직계 부모들]},        # entailed OWL, 직계만
 stereotypes: {클래스: gUFO 메타타입},
 unsatisfiable: [불충족 클래스들],
 equivalence_groups: [[동치인 클래스들], ...],      # 파생 동치 그룹(전이 폐포)
 has_nontrivial_equivalences: bool,                # 동치 존재 경보등
 representatives: {클래스: 동치류 대표(사전순 최소)}} # quotient 접기용
```

### 구현 핵심 (`cg_owl.py` `classify()`)

1. `_is_reportable_class(x)` 헬퍼 — Thing/Nothing/익명식/gUFO 제외 술어. 부모 필터와
   동치 필터가 **공유**(재사용, 중복 제거)
2. `_connected_groups(adj)` — 직접 `equivalent_to` 간선의 연결요소(전이 폐포).
   ⚠️ **주의**: owlready2 `INDIRECT_equivalent_to`는 gUFO import 시 명명 클래스를
   누락하는 버그가 있어 **쓰지 말 것**. 직접 `equivalent_to` + 자체 연결요소 사용
3. **gUFO 부모 유실 복원**: HermiT가 동치류 SubClassOf를 대표에만 부여 → 그룹 부모
   합집합해 전원에게 배포(`- set(group)`로 별칭 오염 차단). 이건 HEAD부터 있던 기존
   결함이었고, 이번에 수리
4. `representatives = {m: g[0] for g in equivalence_groups for m in g}` — 그룹이 이미
   정렬돼 g[0]이 결정적 대표
5. unsat 클래스는 동치 그룹에서 제외(축 분리) — owlready2가 불충족 클래스에 Nothing을
   불변식으로 붙여 `is_unsat` 가드가 선제 차단

### 회귀 테스트 (test_cg_owl.py)

- P8×4: 파생 동치 보고·전이 폐포·gUFO 오염 방지·unsat 격리
- P9: gUFO 경로 동치 멤버 전원 직계 부모 유지 (부모 유실 복원)
- P10×2: representatives quotient 접기 + 동치 없을 때 빈 맵 대칭

## 6. 테스트 · 실행 (전부 그린이어야 머지)

```bash
venv/bin/python -m pytest -q                    # 93 passed
venv/bin/python test_server.py                  # 73/73
venv/bin/python qa_v7.py                         # 101/101
venv/bin/python -m conceptgate.concept_gate_v7  # 60/60 (인라인)
venv/bin/python fuzz_normalizer_types.py         # total=209 CRASH=0
```

Java(HermiT) 필요: `/usr/bin/java` 있음. owlready2==0.51. pyshacl는 선택(validate_gufo용).

## 7. 배포 (Render)

**Render 서비스 2개** (둘 다 인증 없이 공개 — 아래 보안 주의):

| 서비스 | URL | 배포 브랜치 | 상태 |
|---|---|---|---|
| `concept-gate-taxonomy-docker` (srv-d9bs3s8k1i2s739kpt60) | https://concept-gate-taxonomy-docker.onrender.com | **`claude/ontoclean-gufo-handoff-7cmq0v`** | 동치 체계 라이브(11 도구) |
| `concept-gate-taxonomy` (srv-d92cu728qa3s73d6pbu0) | https://concept-gate-taxonomy.onrender.com | `main` | 구버전(6 도구) |

- **docker 서비스가 작업 브랜치를 배포**한다(main 아님). push하면 자동 재배포됨(확인됨).
- Dockerfile이 JRE+Python+의존성 전부 소유(HermiT가 Java 필요). `render.yaml`은 루트 기준.
- ⚠️ **stale 함정**: 옛 서비스는 Root Directory=`files`(삭제된 경로)로 실패했었음.
  구조 바꾸면 Render Root Directory/Branch 설정 확인.
- 배포 반영 확인은 **번들 스모크**로:
  `venv/bin/python .claude/skills/verify-conceptgate/scripts/render_mcp_smoke.py`
- **보안 주의**: `render.yaml`은 `MCP_API_TOKEN` generateValue를 의도하나 실제 두 서비스
  모두 토큰 미설정 → **인증 없이 공개**. 코드(server.py:192)는 env 설정 시 자동으로 Bearer
  강제. 원치 않으면 대시보드에서 `MCP_API_TOKEN` 설정할 것.

## 8. verify-conceptgate 스킬

`.claude/skills/verify-conceptgate/` — 이번 세션의 반복 함정을 방지하는 검증 규율.
`/verify-conceptgate`로 호출, 또는 description 조건(cg_owl/server 변경·Render 배포·로그만
green일 때) 자동 발동. 번들 스크립트로 배포 서버 5시나리오 스모크 가능.

## 9. 열린 로드맵 (docs/feedback/semantic_fidelity_critique_20260716_160758.md)

외부 의미충실도 비판이 정리한 우선순위. **다음 큰 설계 변경은 R5**:

| # | 항목 | 상태 |
|---|---|---|
| R1 | hierarchy 등급 표시(entailed vs candidate) | ✅ 완료(docstring/mechanism.md) |
| R3 | representatives / quotient graph | ✅ 완료(이번 세션) |
| R2 | 관계 반례 검사 질문(is-a/part-of/role/phase)을 client-guide·feedback에 | ⬜ 중간 비용, 미착수 |
| R4 | SHACL fail-open 정책 옵션(심각 위반 error 승격) | ⬜ 중간 비용, 미착수 |
| **R5** | **semantic entailment critic / claim-evidence adjudicator** | ⬜ **대형. 다음 설계 변경 후보** |

### R5 배경 (큰 설계 변경의 핵심)

비판의 요지: 시스템은 `형식 공리 ⊨ 분류 결과`는 강하게 검증하나 `문서의 실제 의미
⊨ 추출된 주장`은 약하다. 즉 span/hash/quote 일치(=evidence-linked)는 "그 문장이
feature/관계를 실제로 *의미*하는가"(=proof-carrying)를 검증 안 함. 상류 변환
(`자연어 → claim → primitive/defined → OWL 공리`)의 의미 충실도를 검증하는 독립
계층이 없다. 관계 확정 절차(관계 후보→argument type→철학적 조건→반례 검사→확정/보류)와
반례 질문을 입력 계약·feedback으로 강제하는 방향이 제안됨. **양상논리는 별도 계층**
(OWL 2는 SROIQ DL이라 □/◇/K/O/반사실 연산자 없음 — modal theorem prover 아님).
정량 평가: is-a 8/10, part-of 8/10, raw 자동분류 5/10, 양상논리 단독 3/10.

## 10. 반복 이슈 패턴 (교훈 — 스킬에도 있음)

1. **성공 신호 ≠ 실측**: 배포 로그 green ≠ 반영. git 기억 ≠ 실제. → 관측 경계에서 확인
2. **같은 트리거(gUFO)가 특수경로에서만 버그**: base case 통과는 미완. 대조군 필수
3. **stale 참조**: 계약 바꾸면 docstring·mechanism.md·MCP_SERVER.md·Render 설정 동기화
4. **인프라 간헐 실패**: MCP disconnect, AskUserQuestion 실패, 서브에이전트 세션 한도,
   git checkout -B 분류기 차단, 네트워크 403 → 재시도·우회
5. **컨텍스트 단절 후 상태 오인**: "Continue" 뒤엔 git/서버로 ground truth 재확립

## 11. Git 상태 (정확)

- 브랜치: `claude/ontoclean-gufo-handoff-7cmq0v` (로컬 == origin, clean)
- 최신 커밋:
  - `75d16d4` docs(feedback): 의미충실도 비판 정리
  - `30406d2` chore(skills): verify-conceptgate 스킬
  - `54b6c72` feat(cg_owl): representatives + 등급 표시 (R3+R1)
  - `f510f7f` docs(cg_owl): equivalence_groups·has_nontrivial 계약 반영
  - `d1a2ba7` feat(cg_owl): 파생 동치 보고 + gUFO 부모 유실 복원
  - `4d2c110` Merge PR #2 (main 머지 — 이 브랜치는 그 위에 rebase됨)
- ⚠️ **PR #2는 이미 머지됨**. 이 브랜치에 쌓인 커밋(dffe462~75d16d4)은 후속 작업.
  새 PR을 열거나, main으로 정리하는 결정은 사용자 몫. `settings.local.json`은 gitignored.
- **커밋 규칙**(사용자 강조): 매우 상세한 멀티라인. 사용자 명시 없이 커밋 금지.
  트레일러: `Co-Authored-By: Claude Opus 4.8 ...` + `Claude-Session: ...`

## 12. 작업 스타일 (사용자 선호 — 중요)

- **매 결정마다 사용자에게 질문**(닫힌 선택지). 실행 전 설명, "실행 후 보고" 금지
- 사용자가 개념을 이해 못 하면 상위 개념·장단점 설명
- **step-by-step**: 구현→실험→구현→실험 반복
- **원본 수정 최소화 + 재사용성**(기존/타인 코드 재사용). 단 프로그램 가치·기능 범위 우선
- 커밋은 명시적 승인 후에만
