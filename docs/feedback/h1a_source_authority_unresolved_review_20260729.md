# H1a 설계 초안 적대 검증 — 합성 보고 (2026-07-29)

- 대상: `experiments/2026-07-29_h1a_source_authority_unresolved/README.md` (설계 초안)
- 방법: `adversarial-review` 스킬 — 근거 축이 서로 다른 4 reviewer + lead 합성
- reviewer 축: **A** 코드베이스 실측 / **B** 실험설계 이론 / **C** 외부 지침·skills-catalog / **D** 프로젝트 제약
- 총 finding 31건 (A 10 / B 7 / C 6 / D 8), blocker 주장 2건
- **lead 재실측 3건 수행 — blocker 2건 모두 뒤집혔고, 설계 전제 1건이 반증됐다**

## TL;DR

**초안의 핵심 주장이 틀렸다.** §5 D-H1a-1이 "이 실험이 성립 불가일 수 있다"고
한 근거 두 갈래가 **둘 다 사실이 아니다**:

1. *"새 eligibility profile이 모델에 보이면 오라클 유출"* → **틀림.**
   profile은 qualification manifest에만 있고 **모델 payload에 도달하지 않는다.**
2. *"profile을 숨기면 모델이 두 텍스트를 구분할 근거가 없다"* → **틀림.**
   `source_kind`가 이미 모델 화이트리스트에 있고 `doc`/`code`는 별개 값이다.

따라서 D-H1a-1은 "실험 성립 가능성" 문제가 아니라 **`_eligibility_profile()`에
분기 하나를 추가하는 국소 문제**로 축소된다. 다만 그 분기를 **E2.4의 동결
`_surface.py`에 넣을지 H1a 사본에 넣을지**는 여전히 결정 사항이다.

반면 초안이 **놓친** 설계 판정이 2건 드러났다(채점 극성, 최소편집 절차).

## Verdict matrix

| 초안 주장 | 축 | 판정 | 근거 |
|---|---|---|---|
| §3 재료 10건 사실 주장 | A | **CONFIRMED 9 / PARTIAL 1** | 칼/철 인스턴스 일치, R6b 실제 통과, `cg_partwhole.py:36` 일치 |
| §5 D-H1a-1 "유출 딜레마" | B, lead | **REFUTED** | profile은 payload 미도달, `source_kind`로 이미 구분 가능 |
| §5 D-H1a-1 "구분 불가 → 성립 불가" | B | **REFUTED** | 구분 불가 상태의 보류 여부가 오히려 더 강한 조작화 |
| §2 "독단 해결 = 사전지식 의존" | B | **REFUTED** | 텍스트 내 신호(단정적 어투·테스트 통과 표시)와 분리 불가 |
| §4 SILENT vs OPEN 격리 | B | PARTIAL | 최소편집 절차 미명시 → 프롬프트 길이·문맥 교란 |
| §4 3-arm 필요성 | D | PARTIAL | YAGNI — 2-arm(SILENT/OPEN)으로 §2에 답 가능한지 미논증 |
| §5 D-H1a-3 arm별 제약 집합 | D | **CONFIRMED** | `semantic_constraints`는 arm 조건 없는 전역 배열 |
| §5 "판정 3건이면 충분" | B | **REFUTED** | 채점 극성·최소편집 절차 2건 누락 |
| §1 지시문 §3 인용 | C, A | PARTIAL (lead 정정) | 인용은 정확하나 **원문이 저장소에 없어 검증 불가** |
| §6 "하지 않았다" 4건 | D | **CONFIRMED** | `git status` 실측 일치 |
| profile 확장이 동결 해시를 깬다 | D | **REFUTED (lead)** | 실측: 3 fixture 전부 해시 불변 |

## Lead 재실측 (환각 방어 — reviewer 보고를 그대로 받지 않음)

### 재실측 1 — B#1·#2: 유출 딜레마 (reviewer 옳음, 초안 틀림)

```
MODEL_EVIDENCE_KEYS = ('evidence_id', 'source_kind', 'text')
SOURCE_KINDS = ['code', 'commit_message', 'doc', 'fixture', 'test']

manifest의 eligibility_profile: ['current_executable_source', 'frozen_experiment_artifact']
payload 최상위 키: ['candidate_concepts', 'evidence_items', 'server_response']
payload에 'current_executable_source' 존재: False
payload에 'frozen_experiment_artifact' 존재: False
payload에 'historical_commit_record'   존재: False
payload에 'verified_by_passing_test'   존재: False
```

**결론**: profile 4종 전부 payload에 부재. `build_model_payload()`는 manifest에서
version·status·fixture_sha256만 검사하고 profile을 읽지 않는다. 초안의
"(a) profile이 모델에 보이면 유출"은 **구성상 불가능한 시나리오**였다.

동시에 실제 payload는 `ev9: source_kind='code'`, `ev10: source_kind='fixture'`를
모델에 보여준다 — 즉 출처 **종류** 구분은 이미 제공된다. 초안의 "(b) 구분 불가"도
틀렸다.

### 재실측 2 — D#4 (blocker): profile 확장이 동결 해시를 깨는가 → **아니다**

`_eligibility_profile()`에 `docs/` → `superseded_document` 분기를 런타임
주입하고 E2.4 3 fixture의 해시를 재계산했다.

```
E24-F-01  rendered 동일=True  payload 동일=True  qualification 동일=True  동결본과 일치=True
E24-F-02  rendered 동일=True  payload 동일=True  qualification 동일=True  동결본과 일치=True
E24-F-03  rendered 동일=True  payload 동일=True  qualification 동일=True  동결본과 일치=True
```

**결론**: D#4는 **profile 추가에 대해서는 틀렸다.** 기존 E2.4 fixture 중 `docs/`
경로를 쓰는 것이 없어 profile 산출이 바뀌지 않고, profile은 payload에도
안 들어간다. 다만 D#4가 지목한 메커니즘(`_cohort.py:298`의 rendered 해시 대조)은
실재하므로, **`SOURCE_KINDS`나 `MODEL_*_KEYS`를 건드리면** 그때는 실제로 깨진다.
severity를 blocker → **major(조건부)** 로 하향하되 경고는 보존한다.

### 재실측 3 — C#1 (blocker): 지시문 인용이 틀렸는가 → **인용은 맞고, 검증 불가가 맞다**

```
$ grep -rln "권위 충돌은 E2.4" --include="*.md" .
experiments/2026-07-29_h1a_source_authority_unresolved/README.md      <- 내 초안뿐
```

2026-07-29 지시문 §3은 네 항목으로 되어 있고 그 **네 번째**가 문제의 문장이다
(첫 번째가 reviewer C가 §3 전체로 오인한 UNKNOWN 조항). 즉 **인용 자체는
정확하다.** reviewer C는 등록부 요약본만 근거로 삼아 원문을 못 봤다.

그러나 **지시문 원문이 저장소 어디에도 커밋돼 있지 않다**는 지적은 옳다
(A#10이 독립적으로 같은 결론). 현재 운영을 지배하는 문서를 후속 세션이
검증할 수 없다. severity blocker → **major**, 그리고 **조치 필요**.

## 채택 조건

초안을 채택하려면 아래를 해소해야 한다.

### 필수 (구현 착수 전)

1. **§5 D-H1a-1을 다시 쓴다.** "실험 성립 가능성" 프레이밍을 폐기하고, 실제
   쟁점으로 교체: *E2.4의 동결 `_surface.py`를 수정할 것인가, H1a 전용 사본을
   둘 것인가.* 방법론 규칙 1(동결 아티팩트 불변)과 CLAUDE.md "codebase reuse"가
   여기서 충돌한다 — 이건 진짜 결정 사항이다.
2. **누락된 설계 판정 2건 추가**:
   - **D-H1a-4 채점 극성** — OPEN arm에서 관측된 "독단 해결"을 정답으로 볼
     것인가 오답으로 볼 것인가. 초안 §2는 "나쁜 신호"로 읽히지만 조작적으로
     고정하지 않았다. E2.4의 #11(위반=오답)과 달리 H1a는 극성이 미정이다.
   - **D-H1a-5 최소편집 절차** — SILENT/OPEN의 차이를 liveness 조항 하나로
     격리하려면 나머지 서문 바이트 동일성을 보장하는 절차가 필요하다.
3. **지시문 원문을 저장소에 커밋한다** (예: `docs/DIRECTIVE_2026-07-29_operations_change.md`).
   현행 운영 근거가 후속 세션에서 검증 가능해야 한다.

### 권장

4. **2-arm으로 축소 검토** (D#5, YAGNI). §2 가설은 SILENT vs OPEN 대조로
   직접 답할 수 있어 보인다. CONTROL_REPO는 legacy라는 **별개 계약 체계**라
   "계약 유무"가 아니라 "계약 종류" 교란을 들여온다(B#5). 3-arm을 유지하려면
   그 필요성을 논증해야 한다.
5. **§2의 인과 귀속을 약화한다** (B#3). "독단 해결 = 사전지식 의존"은 검증
   불가능한 단정이다. 모델이 텍스트 내 신호로 판단했을 가능성과 분리할 사후
   프로빙 계획을 넣거나, 주장을 관측 수준으로 낮춘다.
6. **모듈 로딩 관례를 명시한다** (D#2). 새 파일을 만든다면
   `spec_from_file_location` + 고유 `sys.modules` 키를 써야 등록부 [DONE] #6이
   재발하지 않는다. 초안은 "재사용"이라고만 적었다.
7. **세션 경계를 §7에 반영한다** (D#7). agent registry가 세션 시작에 고정되므로
   ([DONE] #17) 신규 trial subject가 필요하면 최소 1회 세션 경계가 강제된다.

## 교차검증 기록

| finding | 제기 축 | lead 판정 | 방법 |
|---|---|---|---|
| 유출 딜레마 반증 | B | **채택** | payload/manifest 분리 직접 실측 |
| 동결 해시 파손 (blocker) | D | **기각(조건부 보존)** | profile 주입 후 3 fixture 해시 재계산 |
| 지시문 인용 오류 (blocker) | C | **부분 기각 → 별건 채택** | `grep -rln`으로 원문 부재 확인, 지시문 §3 4항목 구조 대조 |
| 재료 사실 주장 | A | **채택** | A가 R6b를 실제 실행해 통과 확인 |
| arm별 제약 집합 | D | **채택** | `semantic_constraints`가 전역 배열임을 확인 |

**환각 finding 0건.** 다만 blocker 2건이 모두 **불완전한 근거**에서 나왔다 —
C는 등록부 요약만 보고 원문을 못 봤고, D는 profile과 payload 필드를 구분하지
않았다. 축 분리의 대가이며, lead 재실측이 정확히 이걸 잡으라고 있는 단계다.

## 다음 라운드에 쓸 수 있는 외부 자원

- `goodand/skills-catalog`의 `Skills-Create-Project/design-planning-orchestrator`
  계열(`semantic-slice-mapper`, `execution-contract-mapper`,
  `dependency-slice-planner`, `agent-graph-ir`). 다만 이 계열은 **소프트웨어
  설계 계획**용이라 실험 설계(교란·조작화·채점 극성)에는 직접 대응하지 않는다.
  D-H1a-1의 "동결본 수정 vs 사본" 같은 **구조 결정**에는 적합하다.
