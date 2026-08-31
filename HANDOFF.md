# HANDOFF — codex/h1-source-authority (마일스톤: 2026-08-23 Stage 2 동결 직후 · 갱신: 2026-08-31)

프로젝트 식별자: **concept-gate-h1** (worktree `concept-gate-h1-wt`,
branch `codex/h1-source-authority`) · 실험 **E2E-v1 Stage 2** (O1 capability cohort).
이 handoff가 이 프로젝트의 현재 상태(state), 다음 행동(next action),
정지 조건(stop conditions)의 유일한 진입점이다.

이 worktree의 HANDOFF가 정본이다(main repo 것 아님). **이 문서는 포인터
중심**이다 — 상태 서술의 정본은 아래 문서들이고, 여기 중복 기재하지 않는다
(P4 예방). 이 문서에만 있는 것은 §3 "다음 실행 절차"뿐이다.

## 0. 기계 판독 상태 블록 (handoff 평가기 계약 — 코드는 아래 산문·정본과 1:1)

```yaml
updated: 2026-08-31            # 이 문서를 마지막으로 고친 날. 제목의 2026-08-23 은 **마일스톤**이지 갱신일이 아니다
state_code: D37_RECEIVED__R4_IS_DOWNSTREAM_OF_M   # D-37 도착·검증·저장 완료(`VERBATIM_SHA256: 5274ece0…`). R4는 기제 동일성이 아니라 **M 상대적 qualification 동등성**이고 **R2와 독립인 축**이다. 그리고 R4는 **M 없이 평가 불가** — M은 D-34 3항 사슬(`semantic definition → qualification evidence → measurement implementation`)의 **비어 있는 첫 항**이다. 즉 **R4를 풀어 경계로 가려던 방향은 성립하지 않는다.** 우리 상신문 §4는 **기각**됐다(금지된 다리의 역방향 반복). **코호트 dispatch 누계 0건**
next_action_code: OBLIGATION_FQN_FIELD   # A(FQN 래칫 게이트)·C(축 지도 §14.1a 18행) **완료**. 다음 = **B: ObligationResult 가 불변식 FQN 을 싣는다**(SURVEY §14.2) — 요구는 문서가 아니라 판정에 관한 것이라 목적을 직격한다. 지도가 드러낸 것: 상태 계약 축(mechspec:I1 부터 mechspec:I7 까지)은 코드가 이름으로 부르는 곳 0건(G205) — B 는 그 격차를 좁히는 첫 수단이기도 하다. 그 뒤 2-pass Verify1 승격(§8.3, 생산자 cg_obligations.py:327)
stop_condition_codes:
  - NO_COHORT_WITHOUT_USER_APPROVAL      # §1·§3 — 실행은 별도 승인
  - NO_FROZEN_SURFACE_EDITS              # §4 — V1·V2 동결 표면 수정은 D-19 §12 외부 판정 사안
authority: experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_fixture_manifest_v5.json  # V5 = 최신 동결(투영 전용 개정). 사전등록 본문은 PREREGISTRATION_STAGE2_V4.md가 여전히 정본
# 코드별 authority 근거절 — 위 코드를 주장할 때는 아래 절을 인용하라:
#   state_code             ← stage2_fixture_manifest_v5.json amendment (V5 = 투영 전용 개정, dispatch 0) + stage2_controls_results_v5_1.json (5/5)
#   next_action_code       ← docs/DESIGN_REQUEST_referential_participant_quantification.md (Q33 — 회신 전 코호트 금지)
#   NO_COHORT_WITHOUT_USER_APPROVAL ← CLAUDE.md "## 실행 승인" 절 (저장소 전역 운영 규칙 — 사전등록은 실행 허가가 아니다)
#   NO_FROZEN_SURFACE_EDITS         ← PREREGISTRATION_STAGE2_V4.md (D-19 §12; 개정은 D-24 §9 절차로만)
```

## 1. 현재 상태 한 줄

**측정 도구는 완성됐고, 그 도구가 정의할 수 없는 것 하나에 막혀 있다.**
V5 동결(투영 `O1_SCOPE_PROJECTION_V2`)과 control 재선별 **5/5**(V4 1/6 → V5 2/6
→ V5.1 5/5, 사슬 최초)는 끝났다. 남은 것은 **referential ∃ 경계**이고, 그것이
순환이다.

고리는 이렇게 닫힌다(그림: [[concept-gate-h1-wt/docs/diagrams/README_referential_circularity|Z0→Z2]]):

```text
순수 measurand → scope/encoding 분리 → referential ∃ 경계
      ↑                                        ↓
      └────────── 무엇이 정답인가(채점 계약) ──────┘
```

**우리가 시도한 네 가지가 전부 고리를 끊지 못했다** — synset(식별 함수 아님) ·
표면 목록(목록 자체가 부분 경계, 비율이 2~51%) · FOLIO 규약(D-34 기각) ·
`Name`/`ANA` 권위(D-35: 증거지 충분조건 아님). **내 측정이 한 일은 고리를 끊은
것이 아니라 거짓 탈출구를 제거한 것이다.**

끊는 간선은 apparatus 밖의 권위 하나이고, 그 요건 넷 중 **병목은 R2(정확성의
독립 검증 가능성)** 다 — R1은 후보 넷이 다 채우고 R2는 둘만 채운다. 그것을
Q36으로 상신했고 회신 대기다.

**코호트 dispatch 누계 0건**이며 `dispatch: blocked` ·
`immediate_projection: forbidden` · `operational_patch: forbidden`이 모두 유효하다.
**`O1_SCOPE_PROJECTION_V3`을 만들지 마라** — D-35가 금지했다.

## 2. 정본 지도 (읽는 순서)

**graph 진입점**: [[concept-gate-h1-wt/docs/RULING_CHAIN_INDEX|RULING_CHAIN_INDEX]]
— 판정 **D-19~D-36** + 조사 6왕복 전부를 **1홉으로** 도달 가능하게
묶은 색인이다. `rg`로는 판정 문서를 찾을 수 없는 경우가 실측으로 확인됐으므로
(파일명이 질문의 어휘를 포함하지 않는다), 이어받는 세션은 **grep이 아니라 이
색인에서 시작**한다. 각 판정 문서 헤더에 `이전`/`다음` 링크가 있어 색인 없이도
사슬을 걸을 수 있다.

| 알고 싶은 것 | 정본 |
|---|---|
| 최신 상태·패턴 원장 | [[concept-gate-h1-wt/docs/H1A_PROBLEM_ANALYSIS\|H1A_PROBLEM_ANALYSIS]] **마지막 절** — 규약상 항상 문서 끝이 최신(현재 **§21**). 이 이름은 vault에 9개 있으므로 경로로 지정한다 |
| 판정·조사 사슬 전체 | [[concept-gate-h1-wt/docs/RULING_CHAIN_INDEX\|RULING_CHAIN_INDEX]] |
| **무엇이 코호트를 막고 있나** | **순환이다.** [[DESIGN_DECISION_referential_participant_quantification\|D-33]] → [[DESIGN_DECISION_d33_claim_status\|D-33-V]] → [[DESIGN_DECISION_referential_existential_qualification\|D-34]] → [[DESIGN_DECISION_annotation_layer_admissibility\|D-35]] → [[DESIGN_DECISION_independent_verifiability_constraint\|D-36]]. 병목은 **R2(독립 검증 가능성)** 이고 D-36이 그것을 확인했으나 **R1~R4는 정리가 아니라 후보 분해**이며 삼층(L1/L2/L3)을 합치지 말라고 명했다. 구조는 구조는 [[README_referential_circularity]]가 그림으로 갖고 있다 |
| **배관이 도는가** | **돈다 — 2026-08-24 드라이런.** 오라클 20/20 해석·드리프트 0, `ingest → evaluate → score → report` 전 구간 통과, 수락 게이트가 경계에서 뒤집힌다(16→수락 / 15→거부 / 출력 누락→ERROR로 거부). **남은 미지는 모델의 답뿐이다.** 기록 [[DRYRUN_20260824]] |
| **관계 구분(is_a/has_a) 수리와 배포** | `assemble_concepts` 가 운영 어휘(`relation_hint`)·`type` 을 **조용히 무시하고 `is_a` 기본값**을 먹여 `dog --is_a--> tail` 을 냈다(부분이 하위클래스). 유도로 수리하고 배포 브랜치에 cherry-pick(`17da1da`) 후 push 완료 — **배포 반영은 Render 재배포 대기**. 전체 머지 대신 cherry-pick 을 고른 근거와 확인 방법은 [[DEPLOY_CHERRY_PICK_20260825]] |
| **드라이런이 잡은 것** | `stratum_floors`가 선택 인자여서 **생략하면 사전등록 금지 수락이 통과**했다(전체 16/20·mq 1/5 → floors 생략 시 `accepted=True`). `ingest_cohort()`로 **유도**해 그 경로를 없앴다. 그리고 이 기록을 사전등록서에 append했다가 되돌렸다 — 게이트가 13/0으로 통과했으므로 `test_frozen_surfaces.py`를 신설해 동결 표면 11개를 바이트로 고정했다 |
| **왜 우리가 경계를 정할 수 없나** | `operational_patch: forbidden`(D-31 Q31.4·D-33) + `immediate_projection: forbidden`(D-35). 실측 근거도 있다 — 표면 목록으로 유형화 비율이 **2~51%**로 움직이므로 목록 선택이 이미 부분적 경계 결정이다 |
| 무엇이 죽었고 대신 무엇을 쓰나 | [[LEGACY_REGISTER]] · 만든 것이 실제로 불리는가 [[ADOPTION_REGISTER]] — 둘 다 게이트가 거짓말을 막는다 |
| 무엇이 동결됐고 무엇이 금지인가 | 사전등록 본문은 `PREREGISTRATION_STAGE2_V4.md`가 여전히 정본이고, **동결 산출은 V5**다(`stage2_fixture_manifest_v5.json` — 투영 전용 개정). D-33이 `O1_SCOPE_PROJECTION_V3`을 예고했으므로 **V5의 measurement_contract는 잠정**이다 |
| fixture commitment | 같은 폴더 `stage2_fixture_manifest_v5.json` (**코퍼스 원문을 담지 않는다** — `text` 필드 없이 `text_sha256`·locator만. 파일 자체는 31KB다. V4에서 commitment 필드 바이트 동일, 추가된 것은 `expected_scope_signature_v2_sha256`) |
| 선별이 조작 불가능한 이유 | 같은 폴더 `freeze_stage2_v4.py`(in-N 선별) · `freeze_stage2_v5.py`(V5 = 투영 전용 개정, 재투영·서명 재생성이 전부 코드) · `freeze_controls_v5_1.py`(control 재선별, 적격 술어 2층) — seed·층 술어·투영 전부 코드가 정본이고 산출은 덮어쓰기를 거부한다 |
| 동결이 실효됐다는 선언 | 같은 폴더 `test_stage2_freeze_v4.py`의 `FREEZE_STATE`(= `V5_ACTIVE`) — SUPERSEDED 선언 하에서는 **drift가 존재해야 통과**한다(선언이 거짓일 수 없게). V5는 `test_stage2_freeze_v5.py`가 지킨다 |
| MRS 재료가 왜 아직 부적격인가 | [[RESEARCH_RESULT_mrs_redwoods_round3\|3차 조사 회신 + 우리 검증]] §B — 전수 37,066건 실측, 적격 기수 **0건**(BODY 비제약이 유일 장애 16,584건) |
| adapter 자격(코드 결박) | `experiments/2026-08-23_{o1,sbn,fol}_adapter_qualification/` — test_protocol이 코드 해시를 라이브와 대조: **커널·adapter를 고치면 자격이 자동 실효**된다(2026-08-24 실측: `cg_ir` 확장으로 3건 실효 → 재자격 9/9·9/9·7/7 재현) |
| 적대 검증 결과 | [[ADVERSARIAL_VALIDATION_20260823]] |
| 이 handoff가 실제로 복원 가능한가 | [[HANDOFF_EVALUATION_20260824]] — **9/9 복원·막힌 지점 0**, 그러나 결함 2건 적발(V5.1 운영 로그 누락 · 고아 노트 1건)과 **`vault_search`가 정본·D-33에 도달 못 함**. 1차는 [[HANDOFF_EVALUATION_20260823]](3/3) |
| 채점이 무엇을 재는가 | 같은 폴더 `_stage2_projection_pipeline_v2.py` — V1 전처리(desugar·관용구·granularity 다리) → V2 signature 합성. **이 모듈이 계약이고 V5 manifest가 해시를 pin한다**. 계약 정본은 `test_stage2_projection_pipeline_v2.py` |
| control이 무엇을 보증하고 무엇을 보증하지 않나 | [[CONTROLS_RUN_V5_20260824|V5 실행(2/6 → 정지)]] → [[CONTROLS_RUN_V5_1_20260824|V5.1 재선별(5/5)]]. D-33 §9: `control eligibility excludes X → control PASS therefore says nothing about X` — 적격 술어가 배제한 성질은 인증되지 않는다 |
| 무엇이 죽었고 대신 무엇을 쓰나 | [[LEGACY_REGISTER]] — 표기·후계자·복구 명령을 한 곳에. `test_legacy_register.py`가 등록부의 거짓말을 막는다(실재하지 않는 경로·후계자 없는 행·등록 안 된 표기). **버전 번호가 낮다고 legacy가 아니다** — `_stage2_scope_projection.py`(V2 채점의 전처리)·`freeze_stage2.py`(SEED 정본)·`.oracle_cache`·`vendor/`는 명시적 비-legacy로 적혀 있다 |
| 실행 기제 | `experiments/2026-08-23_e2e_v1_c_o1_cohort/_stage2_*.py` + `conceptgate/cg_{sbn,fol}_adapter.py`, `cg_mrs_reader.py`, `cg_fixture_resolver.py` |

## 3. 다음 실행 절차 (사용자 승인 후 — 이 문서의 유일한 고유 내용)

전제: 게이트 **`../concept-gate-taxonomy/venv/bin/python scripts/run_gates.py`**
= **14 passed / 0 failed / 0 blocked**. 코호트 실험 404 passed.

**게이트 실행 방법이 바뀌었다.** `python3` 로 돌리면 owlready2 가 없어
`test_server.py` 가 BLOCKED 가 되고, 그 BLOCKED 가 실제 결함을 엿새 동안
가렸다(회고 §22 G156·G157). `CLAUDE.md` 가 명한 `venv/bin/python` 의 venv 는
**존재한 적이 없었다** — 이제 `concept-gate-taxonomy/venv` 에 만들어 두었고
SRC 는 그것을 **빌려 쓴다**(worktree 마다 133M 을 두지 않기 위해).
`conceptgate` 는 cwd 를 따르므로 각 worktree 의 것이 쓰인다(실측).

### 이미 끝난 것 (다시 하지 마라)

- **V5 재동결 완료** — 투영 V1→V2, 20건 전량 재투영(**서명 20/20 변경이 정상**,
  `expected_ir_sha256`은 전건 불변), manifest에 `measurement_contract` ·
  `supersedes` · `score_comparability` · `measurement_semantics`, 채점 배선
  V2 교체. 커밋 `1adc471`.
- **control 4라운드** — V4 1/6 → V5 2/6 → D-27 §18 재선별 → **V5.1 5/5**.
  커밋 `fe0e618`·`3125d8d`·`e5ef159`.
- **코호트 plan 20건 생성** — `stage2_cohort_plan_v5.json`. **dispatch 0건.**
- **기제 부채 상환 완료**(§19) — 인용 검사기·프롬프트 바이트 게이트·ADOPTION
  원장·문서 규약 4종. 게이트 4개 중 2개가 음성 확인에서 자기 결함을 드러냈다.
- **D-36 도착·검증·저장** — 검증 설계 → 적대검증(4축) → 검증 → 저장.
  `VERBATIM_SHA256: ee8a01b9…`. 설계가 네 곳 깨졌고 **내 §E1 제안이 실측에
  반박됐다**(`Name ?` 는 오류가 아니라 구조 표시된 하위종 394건).
- **관계 구분 수리 배포 완료** — `assemble_concepts` 가 운영 어휘를 조용히
  무시하고 `is_a` 를 먹여 **부분이 하위클래스가 됐다**(`dog --is_a--> tail`).
  유도로 수리, cherry-pick `17da1da`, **배포본에서 실측 확인**
  (`tail --component_of--> dog`).
- **배포본 인증 켜짐** — `MCP_API_TOKEN` 미설정이 원인이었다(코드는 정상).
  `~/check_conceptgate_lock.sh` 로 확인한다.
- **Java 해석 수리**(커밋 대기) — 판정 W2 §4 가 명령한 "부재 ≠ 실행 실패"
  분기가 macOS stub 에 발동하지 않았다. `cg_owl._resolve_java()` 로 exit code
  를 보게 하고 `ReasonerUnavailable(FileNotFoundError)` 로 기존 배선 재사용.
  **`server.py` 편집 0** — 그 파일 380-382행이 E2.4 fixture 에 원문 인용된다.
- **경계 실사 3라운드**(Q34·Q34-B·Q35) — PMB gold 12,053 전수, FOLIO 적격 풀
  799 전수, role 주석 층 발견. **경계는 얻지 못했고 얻을 수 없는 이유를 얻었다.**

### 1. ~~Q34~~ ~~Q34-B~~ ~~Q35~~ ~~Q36~~ **상신 완료** — 회신 대기가 다음 행동이다

사슬은 `D-33 → D-33-V → D-34 → D-35 → D-36`이다. Q36의 축은 **R2가 실제
구속 조건인가**이고, 우리가 요건을 발명했다면 그 문서 전체가 잘못된 문제를 푼다.

**회신 없이 할 수 있는 것 둘**(둘 다 재료 문제이고 경계 결정이 아니다):

- **`sbn_spec.py` 확보.** `ANA`·`Name`의 규약상 의미가 그 사양에 있고 우리는
  **전사만** 갖고 있다(`SBN_ADAPTER_DESIGN.md` §2). Q36 (d)가 그것이 R2의
  선행 조건인지 묻는 중이지만, **취득 자체는 우리가 할 수 있다.**
- **미검토 role 198종 실사.** role 어휘는 200종이고 우리가 본 것은
  `Name`·`ANA` 둘이다. `EQU` **12,501건**은 동일성 표시라 지시성과 직접
  관계될 수 있는데 보지 않았다. **재고 목록 없이 실사를 시작한 것이 G146의
  원인**이므로 이번엔 전수 열거부터 한다.

**하지 말 것**: `O1_SCOPE_PROJECTION_V3` 제작(D-35 금지) · 경계 규칙 제안
(`operational_patch: forbidden`) · `ANA` 배제 되돌리기(D-35 §8 — 동결 모집단을
관측 결과에 맞춰 고치는 모양이 된다).

### 2. D-34 수령 후 (판정 내용에 따라 갈림)

판정이 경계를 정하면: qualification 구현(TDD → Sonnet 5 위임) →
`O1_SCOPE_PROJECTION_V3` → **V6 재동결**(20건 재투영·서명 재생성) → 채점 배선
교체 → **`stage2_cohort_plan_v5.json`을 의도적으로 삭제하고 재생성**
(`write_cohort`는 덮어쓰기를 거부한다 — 이것은 안전장치이므로 우회하지 말고
지워라) → control 재실행.

판정이 "경계를 못 정한다"고 하면 그것도 답이다 — 그때는 PMB의 지시 표현
fixture가 estimand에 포함되는지가 재료 문제로 돌아간다.

### 3. 코호트 20건 dispatch — **별도 승인 + 되돌릴 수 없다**

`export_dispatch_args(plan)`으로 인자를 내고 **Workflow 하네스**로만 돌린다
(`agentType: "o1-compiler"`, `model: haiku`, `schema`= plan의
`provenance.output_schema`). **프롬프트를 손으로 재구성하지 마라** — 실측으로
바이트 불일치 0/20이 나왔다(개행 하나 차이).

**dispatch 직전에 반드시 실행한다**(기제 — 규율만으로는 잊는다):

```text
python3 scripts/verify_dispatch_prompts.py \
    experiments/2026-08-23_e2e_v1_c_o1_cohort/stage2_cohort_plan_v5.json \
    <Workflow에 넘길 args JSON>
```

`ALL_VERBATIM`이 아니면 **dispatch하지 마라**(exit 1). 이 검사는 정규화하지
않는다 — 개행 하나가 사전등록 위반의 전부이기 때문이다. 그리고 이 게이트는
**호출을 잊는 것은 막지 못한다**. 그래서 여기 절차에 있다. mechanical retry는 dispatch층
1회만(생성 전 인프라 실패), semantic retry 금지.

채점: `ingest_outputs`에 `pass_min=16`,
`stratum_floors={"multi_quantifier": (5, 4)}`, `strata`= manifest의 stratum,
`certified=None`(dormant-by-design — 사전등록 확정).

**이 dispatch가 "관측 0건" 체제를 영구히 끝낸다.** D-24~D-33의 모든 개정이
`cohort_dispatch_count: 0`에 근거했으므로, 이후에는 사전 개정이 불가능하다.

### 4. 결과 커밋

trials_raw 보존 + 결과는 동결과 **별도 커밋**(방법론 §1). 결과 보고 표기:
`O1-v1 source = PMB-5.1.0-gold(15) + FOLIO-v0.0(5)`, wikisem 결과와 비교 서술
금지(D-21 §11).

## 4. 하지 말 것 (이미 값비싸게 배운 것의 압축)

- 동결 표면 수정(§12 사안) / adapter·비교층 코드 수정(자격 실효 — 게이트가
  잡지만 재자격 비용) / fence 관용 파서 / 원문 corpus 바이트의 repo 유입 /
  부재 판정을 재실측 없이 수용(P12) / 빗나간 뮤테이션을 검증으로 계상(P16).
- **프롬프트를 손으로 재구성하지 마라.** plan이 유일 출처다 — 실측으로
  재구성본이 plan과 **0/20 바이트 불일치**였다(개행 하나). `export_dispatch_args`를
  거쳐라.
- **통과한 게이트가 무엇을 배제했는지 먼저 보라.** control 5/5는 적격 술어가
  지시 표현을 배제하므로 그 성질을 인증하지 않는다(D-33 §9). 침묵을 보증으로
  읽는 것이 이 구간의 가장 비싼 오독이었다.
- **경계·정규화 규칙을 우리 손으로 만들지 마라** — `operational_patch: forbidden`
  (D-31 Q31.4 · D-33). 계측기가 두 번 이상 다르게 틀리면 만들기를 멈추고
  "재료가 그 구별을 담고 있지 않다"를 가설로 올려라(4회 실패 실측).

## 5. 열린 항목 (차단 아님)

- **행 인용 파괴에 게이트가 없다**(회고 §22 G160) — `conceptgate/server.py`
  380-382행과 `concept_gate_v7.py` 1192-1193행이 실험 fixture 에 **원문 인용**
  된다. 그 위쪽을 편집하면 행이 밀려 실험이 깨진다. 이 구간에 **3회** 깨뜨렸고
  매번 되돌렸다. 편집 전 확인이 규율로만 있다 — 다음 세션의 상환 후보.
  확인 명령은 §3 검증 절에 있다(`file_lines` locator 전수 스캔).
- **`test_guard_negative_coverage` 가 DST 에서 실패한다** — 그 브랜치에 음성
  테스트 없는 가드가 있다는 뜻이고 SRC 는 통과한다. DST 고유 부채.
- **`.vault-harness` 처분** — 색인 부분은 종결(동료 세션이 83M 회수). 그러나
  지배적 소비자는 **`.venv-neural` 853M**(가상환경)이고 **한 번도 후보로
  올라온 적이 없다**. 총 1.1G. 수정·이동·삭제 금지 대상이라 보고만 한다.

- **`concept-gate-e2.2-wt`의 h1a 구현 분기 병합 결정**(3차 정리 라운드가 발견 — `_h1a_diag*` 대 다른 4개 worktree의 `_h1a_score`/`_h1a_policy`, 정본 미결정).
- **신규 기제 부채 3건**(§21.6): 수치 민감도 필수 보고 · **적대검증 대상 동결
  기록**(대상 sha256을 회신 요구에 넣고 불일치 시 회신 무효, ~30행) · 재고 목록
  단계. 기존 부채는 §19에서 0으로 상환됐다.
- `.vault-harness` 처분 — **색인 부분은 종결, 나머지는 미제기.**
  색인: 동료 세션이 사용자 승인으로 `20260824_pre_rebuild` 83M 삭제(`e9230a0`),
  `live/` 82M은 삭제 불가 확정("쓰는 중"), `frozen/` 82M은 보존 확정
  (live와 바이트 동일 `39a75d98…`이지만 그것이 남길 이유 — 검색 결과가 싣는
  `index_sha256`의 원본).
  **그러나 지배적 소비자는 색인이 아니다(2026-08-24 실측)**:
  `.venv-neural` **853M**(가상환경, 미제기) · `live/` 82M · `frozen/` 82M ·
  `mcp-runtime/` 40M(런처가 `uv sync`로 재생성) · `.git` 50M. 총 **1.1G**.
  삭제 논의는 82M~165M 구간에서만 이뤄졌고 **853M은 한 번도 후보로 올라오지
  않았다.** (수정·이동·삭제 금지 대상이므로 보고만 한다.)
  ([[LEGACY_REGISTER]] §"동결 판본 소실"). 색인 재생성은 완료됐다.
- cert 축 활성화(의무 집합 정의 — 별도 사안), G64(PMB Δ66 모집단 정의),
  뮤테이션 하네스의 게이트화(P16), O3(재료 관문 미해결 — D-21이 조건부
  선행 허용).

## 6. 작업 대기열 (사용자 지정 — 2026-08-24, **2라운드**, 순서 그대로)

D-33 수신 처리(검증 설계 → 설계 적대검증 → 검증 → 기록)를 끝낸 뒤 **이 순서로**
진행한다. 사용자가 순서를 지정했으므로 임의로 바꾸지 않는다.

| # | 할 일 | 완료 판정 |
|---|---|---|
| 1 | ~~**회고**~~ **2라운드 완료** — §21 append(G140~G148, P24가 11회로 지배). 1라운드는 §18
| 2 | ~~**handoff 갱신**~~ **2라운드 완료** — §1 전면 재작성(고리 구조·병목 R2)·§2 낡은 행 3건+신설 3행·§3 재작성. 1라운드는 §0 코드·§1 재작성
| 3 | ~~**handoff test**~~ **2라운드 완료** — **10/10 복원·막힌 지점 0·낡은 것 0**, 중의성 1건 적발·수리("원문 0바이트"를 파일 크기로 오독). 신규 8건 고아 0. 1라운드는 9/9·결함 3건
| 4 | ~~**삭제 후보 탐색 — 현재 작업 범위**~~ **2라운드 완료** — 신규 24파일 재계수: 후보 0건, **거짓 포인터 3건 적발·수리**(`.dot`이 없는 소스를 가리켰다). 1라운드는 문서 공백 1건 | ✅ |
| 5 | ~~**탐색 범위 분할**~~ **2라운드 완료** — **분할 축을 크기에서 권위로 바꿨다**(같은 크기라도 다른 시험을 받으면 다른 범위). A(git 밖 최상위)·B(archive)·C(trunk 미커밋)·D(형제 worktree)·E(vault+MCP 저장소). 제외 목록(vendor 140M·`.git`·등록 worktree 46M = 220M)을 브리프에 먼저 명시 | ✅ |
| 6 | ~~**탐색 subagent(haiku) 위임**~~ **2라운드 완료** — 4건 위임 전부 0건. lead 재실측이 **1건 확증(음성 대조)·1건 정정**(MCP 등재를 설정 파일 하나만 보고 오판). 후보 1건은 lead 범위에서 나왔고 **삭제 완료**(전문 보존 후 sha256 왕복 대조). 누계 삭제 7건 | ✅ [[WORKSPACE_CLEANUP_20260824_ROUND4]] |

### 이 대기열에 이미 적용되는 규율

- 3항의 zero-context 시험은 **5/5를 목표로 하지 않는다** — 복원 실패가 나오면
  그것이 handoff의 결함이고 고칠 대상이다. 통과율을 좋게 만들려고 시험을
  약화시키면 시험이 무의미해진다.
- 4~6항: **날짜는 근거가 아니다.** `SAFE_TO_REMOVE`는 근거 3항이 필요하고,
  0건이 정당한 답이다(2차 라운드 실측: worktree 0 · vault 0 · 파일 1). 선행
  결정을 재제안하지 않기 위해 [[WORKSPACE_CLEANUP_20260823|1차 라운드]]와
  [[WORKSPACE_CLEANUP_20260824|2차 라운드]]를 **먼저 읽는다**.
- 4~6항의 함정 3개(2차 라운드에서 실측된 것): worktree 삭제 안전성의 기준은
  병합이 아니라 **push**다 · **상호 참조는 참조가 아니다**(닫힌 고리는 둘 다
  후보) · **캐시라도 테스트가 읽으면 하중 자산**이다.

## 7. 편집 구간 경계 (compaction ledger — 2026-08-29 신설)

**왜 있는가.** 삭제·병합 후보의 범위는 "이 작업 구간이 무엇을 건드렸나"로
좁혀진다. 그런데 그 구간을 아는 주체는 main agent 하나뿐이고, main agent 는
**가장 최근에 고친 파일은 기억하지만 구간의 시작점은 compaction 에서 잃는다.**
사용자도 최신 것은 기억하지만 시작점은 마찬가지다. 그래서 경계를 파일에 남긴다.

**규약.** compaction 이 일어날 때마다 아래 표에 한 행을 더한다. 기록할 것은
**그 compaction 이후 처음 수정한 파일**과 시각이다. 되돌아볼 때 이 표의 두 행
사이가 곧 한 구간이고, 그 구간의 편집 집합이 후보군의 상한이다.
세션 ID·세션 이름·cwd 는 적지 않는다(워크스페이스 규칙).

| # | 기록(UTC) | 로컬 | 유발 | 직전 토큰 |
|---:|---|---|---|---:|
| 1 | `2026-07-29T11:32:22` | `2026-07-29 20:32:22` | manual | 712,094 |
| 2 | `2026-07-30T11:16:37` | `2026-07-30 20:16:37` | manual | 781,511 |
| 3 | `2026-08-01T15:23:10` | `2026-08-02 00:23:10` | manual | 858,789 |
| 4 | `2026-08-15T12:08:24` | `2026-08-15 21:08:24` | auto | 934,331 |
| 5 | `2026-08-17T14:32:37` | `2026-08-17 23:32:37` | manual | 881,098 |
| 6 | `2026-08-22T12:43:38` | `2026-08-22 21:43:38` | auto | 1,001,383 |
| 7 | `2026-08-23T02:24:57` | `2026-08-23 11:24:57` | auto | 1,000,496 |
| 8 | `2026-08-23T15:23:47` | `2026-08-24 00:23:47` | auto | 1,001,674 |
| 9 | `2026-08-24T06:46:23` | `2026-08-24 15:46:23` | auto | 1,003,675 |
| 10 | `2026-08-24T12:56:06` | `2026-08-24 21:56:06` | auto | 1,000,740 |
| 11 | `2026-08-29T09:18:40` | `2026-08-29 18:18:40` | auto | 1,000,270 |
| 12 | `2026-08-30T16:49:09` | `2026-08-31 01:49:09` | auto | 1,007,652 |

**이 표는 손으로 적지 않는다** — `scripts/compaction_ledger.py` 가 세션 기록의
`subtype: compact_boundary` 를 뽑는다. 갱신:

```bash
python3 scripts/compaction_ledger.py ~/.claude/projects/<프로젝트>/<세션>.jsonl
```

**손으로 적었을 때 틀렸다(2026-08-31 실측).** 시각 열에 compaction 시각이 아니라
**첫 편집 파일의 mtime** 을 적었고, 08-30 을 "여러 회"라 지어냈으나 **1회**였고,
12건 중 **3건**만 적혀 있었다. 시점은 기억할 것이 아니라 **잴 것**이다.

**그 지적 자체도 한 번 틀렸다** — 기록은 UTC 이고 mtime 은 로컬(KST)이라 처음엔
"9시간 뒤"라고 결론냈으나 실제 차이는 **7분**이었다. 그래서 표가 UTC·로컬을
**둘 다** 낸다.

**compaction 이 잃는 나머지 절반**(진행 중인 미커밋 작업)은 `scripts/session_snapshot.py`
가 낸다 — 손으로 유지하지 않고 `git`·이 문서에서 **생성**하며, 그 산출물은
**advisory** 다(정본과 어긋나면 이 문서가 이긴다):

```bash
python3 scripts/session_snapshot.py .
```

**구간의 편집 집합**은 여전히 사람이 잰다 — 경계 두 개 사이를
`find <범위> -newermt '<앞 경계>' ! -newermt '<뒤 경계>'` 로 좁힌다.

**이 세션의 실측 구간** (미커밋 파일 mtime, 1회차 compaction 이전 구간 포함):

```text
2026-08-29 17:59  test_cg_owl.py · test_server.py
2026-08-29 18:05  conceptgate/cg_owl.py · test_java_resolution.py
2026-08-29 18:08  docs/H1A_PROBLEM_ANALYSIS.md
2026-08-29 18:09  HANDOFF.md
2026-08-29 18:14  docs/WORKSPACE_CLEANUP_20260829_ROUND5.md
```

**규약이 지켜지지 않은 사례가 이미 있다(2026-08-31).** 08-30 하루치가 통째로
비어 있다 — 규약은 08-29 에 만들었고 그날 이후 여러 번 compaction 이 있었으나
아무도 행을 더하지 않았다. 즉 **이 표는 "빈 구간이 없다"를 보장하지 않는다.**
표를 읽는 쪽은 인접한 두 행 사이를 한 구간으로 믿기 전에 **행 번호가 연속인지**
먼저 보아야 한다(`—` 행은 누락 표시다). 기록은 compaction 직후 **첫 편집과 같은
turn 에** 하는 것이 유일하게 지켜지는 방법이다 — 나중에 하면 시작점을 이미 잃는다.

**한계 — 이 표가 답하지 못하는 것.** 1회차 compaction 의 경계는 이 규약이
생기기 전에 지나가서 기록이 없다. 그리고 위 mtime 은 **미커밋 파일만** 보여준다
— 이 구간에 커밋까지 마친 편집(예: `cg_normalizer.py`, `server_o1_scope.py`)은
`git log` 로 따로 찾아야 한다. 다음 구간부터는 표의 행이 그 일을 대신한다.
