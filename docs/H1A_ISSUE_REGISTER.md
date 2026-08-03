# H1a 이슈 등록부

> ## 🔴 최신 상태는 §H다 (2026-08-03(2))
>
> **Q10 판정 도착(D-H1a-10, Q10=E).** 최초 40-trial 코호트는
> `completed_nonidentifying`으로 동결 보존되고, **Q7 부분 개정(R1) + 양 arm
> 재실행(R2)** 이 명령됐다. **§H.5가 현재의 게이트 목록이다.**
>
> ⚠️ **이 문서 하단의 "다음 세션 첫 행동"은 2026-08-02 텍스트다.** 거기의
> "실행된 trial 0건", "독립 리뷰 재실행이 차단선"은 **그 시점의 평가이며
> 지금은 참이 아니다.** 실제로 이 함정에 2026-08-03(2) 세션이 걸렸다 —
> 하단을 읽고 "지금 독립 리뷰를 돌려야 한다"고 판단했으나, 그때는 표면이
> 바뀌지 않아 리뷰 대상이 없는 상태였다. `WORKSPACE_NAVIGATION.md` §0 함정
> 3("해결됨/완료 표시는 과거 시점의 평가")이 **같은 문서 안에서** 재발한
> 사례다. 아래 §0 표와 §H를 먼저 읽어라.

- 갱신: **2026-08-03(2)** — **Q10 판정 도착·반입(D-H1a-10).** Q10=E /
  Q10.1=비병합 보존 / Q10.2=가드 상향 / Q10.3=L4 등록. 상세 §H.4~H.7
- 갱신: **2026-08-03** — Q9=A 반입, `PREREGISTRATION.md` §0.1 신설(L1~L3),
  4차 독립 리뷰 사용자 승인으로 생략, **동결 → 본 코호트 40 trial 실행**
  (양 arm 20/20 defer). 상세 §H
- 갱신: **2026-08-02(3)** — ev1/ev3 내용 비대칭을 **Q9 설계 판정 요청으로
  상신**(`DESIGN_REQUEST_H1a_evidence_symmetry.md`). → **판정 도착·적용 완료**
- 갱신: **2026-08-02(2)** — **3차 독립 리뷰 완료, blocker 0.** major 2 +
  minor 1 즉시 수정(§G). 게이트 그린(H1a 106 passed/1 skipped, E2.4 118
  불변).
- 갱신: **2026-08-02** — **Q5~Q8 전부 적용 완료.** 조작 span 2문장, 모델
  대면 type 앵커 제거(+구조적 no-anchor 가드), warrant 기반 select_type/defer
  규칙, fixture 진짜 1-vs-1.
- (이전) 2026-08-01 — 설계 판정 **4건**(+Q5~Q8), 독립 리뷰 **2회**,
  H 계열 worktree 분리. **패턴별 단면은 [`H1A_PROBLEM_ANALYSIS.md`](H1A_PROBLEM_ANALYSIS.md)**
  — 이 문서는 시간순 기록이고 그쪽은 패턴별 분류다. **한쪽만 읽으면 안 된다**
- (이전) 2026-07-31 — 설계 판정 3건(D-H1a-1~7, Q1·Q2, Q3·Q4) + 사전등록
  완료, 독립 리뷰에서 blocker 1 + major 5 발견 → 동결 부적합 →
  **fixture 재구성(C2~C10) + 조작 범위 재정의(Q1) + 프롬프트 표면 재정의
  (Q3=B) 전부 완료. 남은 게이트: 독립 리뷰(프롬프트) → anchor-sensitivity
  진단(Q2) 실행**
- 문서 종류: **운영 로그**(`WORKSPACE_NAVIGATION.md` §2) — 계속 갱신, 동결
  아티팩트와 같은 커밋에 섞지 않는다
- 역할 분담: 실험 폴더의 `README.md`가 설계 서술, `PREREGISTRATION.md`가
  동결된 판정 장치, **이 문서가 이슈 전체 목록과 검증 근거**
- 표기: **[DONE]** 해결(재발 감시용 보존) / **[GATE]** 이것만 풀리면 진행 /
  **[DESIGN]** 설계 판단 필요 — 운영 세션이 임의로 정하지 않는다 /
  **[FIX]** 조치 확정, 적용 대기
- 상위 맥락: E2.4/H3는 별개로 **종료**됨(존재 주장, D-H3C).
  `docs/E2.4_ISSUE_REGISTER.md` 참조

---

## 0. 상태 요약

| 항목 | 값 |
|---|---|
| 실험 | `experiments/2026-07-29_h1a_source_authority_unresolved/` |
| 설계 판정 | **6건 전부 도착·반입** — D-H1a-1~7(`DESIGN_DECISION.md`) / Q1·Q2(`_manipulation_scope`) / Q3·Q4(`_prompt_surface`) / Q5~Q8(`_review_blockers`) / Q9(`_evidence_symmetry`) / **Q10(`_residual_prohibition`, D-H1a-10)** |
| 사전등록 | `PREREGISTRATION.md` — P0.1·P1~P7 + §0.1 한계 **L1~L4**. §11은 Q6=A로 은퇴(이력) |
| 행동 코더 | **교정 통과 18/18**(실행 직전 재측정), 테스트 38 passed, 뮤테이션 3종 검증. **Q10에서 변경 대상 아님** |
| fixture | 1-vs-1(Q8=B로 ev2 제거), Q9=A로 **무변경 확정**. 비대칭은 L3로 선언 |
| 프롬프트 표면(arm) 렌더러 | `_h1a_contract.py` — Q3=B·Q5~Q7 반영. **Q10.2가 아키텍처 전환을 명령** → 어휘 tripwire에서 정책 계약으로 |
| **실행된 trial** | **40건** (2026-08-03, 40/40 성공, 전송 실패 0). ⚠️ **"trial 0건" 전제는 끝났다 — 이후 설계 변경엔 재동결 비용이 있다** |
| 최초 코호트 지위 | **`completed_nonidentifying`**(Q10.1) — 유효 관측이나 확증 부적격, 새 코호트와 **병합 금지**. `COHORT_STATUS_20260803_nonidentifying.md` |
| **진행을 막는 것** | **[GATE] §H.5의 5개** — R1(Q7 부분 개정) → Q10.2(가드 상향) → 신규 사전등록 → **독립 리뷰**(표면이 바뀌므로 3차 리뷰 무효화) → R2(양 arm 재실행) |
| [DESIGN] 미판정 | **§H.6 Q11 후보** — `removed: allowed`를 명시적 허용 문장으로 렌더링할지 침묵할지 |

**허용 결론의 상한**(결과 보기 전에 고정, `PREREGISTRATION.md` §0):
H1a는 K=1이라 `P(행동 | 고정 packet, 고정 arm, 고정 모델·파라미터)`만
추정 가능하다. **N을 늘려도 이 상한은 올라가지 않는다.**

> ⚠️ **위 문장의 "null 결론은 anchor 진단(§11) 통과 후에만"이라는 옛 단서는
> 두 번 superseded됐다.** ① Q6=A가 anchor 진단을 은퇴시켰고(대체: 구조적
> no-anchor 가드), ② **Q10이 최초 코호트의 null 자체를 비식별로 판정했다.**
> 지금 유효한 표기는 다음이다(D-H1a-10 §12):
>
> ```text
> target_effect:            insufficient_evidence
> current_bundle_contrast:  observed_zero
> ```
>
> `null_effect`가 **아니다.** "금지를 제거해도 행동은 변하지 않았다"는 보고는
> **금지**되며, 허용 문구는 `COHORT_STATUS_20260803_nonidentifying.md` §4에
> 있다. "조작이 일반적으로 효과 없다"는 금지는 물론 그대로 유효하다.

---

## A. [DONE] 설계 판정 — 외부 판정으로 해결 (2026-07-29)

| # | 이슈 | 해결 근거 | 해결방법 | 검증 강도 |
|---|---|---|---|---|
| A1 | 3-arm 중 legacy CONTROL이 "보류"를 표현 못 함 | legacy `decision` enum에 보류 값 부재 → 종속변수를 **구조적으로 검열** | **2-arm 축소**(D-H1a-6=B), legacy 제외 | 스키마 enum 실측 |
| A2 | 정답을 둘 것인가 | 어느 type이 옳은지에 대한 규범적 ground truth 부재 | **정답·인증 밴드 폐기**, 행동 분포만(D-H1a-4=C) | 외부 판정 |
| A3 | `source_authority_unresolved`를 hidden oracle로? | correctness 프레이밍 자체가 성립 안 함 | **oracle 없음** + 중립 어휘 + 후처리 분류(D-H1a-2·3=C) | 외부 판정 |
| A4 | E2.4 스키마·채점기 확장 재사용? | 동결 아티팩트 소급 변경 금지 | **H1a 전용 사본·스키마**(D-H1a-1=B) | 외부 판정 |
| A5 | 제약 #11을 arm별 적용? | correctness 채점을 안 하므로 적용 대상 없음 | **양쪽 미적용**, 필요시 manipulation-check로만 | 외부 판정 |
| A6 | "독단 해결 = 사전지식 의존" 귀속 가능? | fixture가 `source_kind`와 원문 표현을 함께 담아 두 원인 분리 불가 | **인과 귀속 금지**(D-H1a-7) | 외부 판정 |
| A7 | **유출 딜레마 — 실험이 원리적으로 성립 불가?** | 적대 검증 4축 + **직접 실측**: eligibility profile이 payload에 도달하지 않음 | **반증됨.** 이 프레이밍으로 회귀 금지 | **실측 반증**. 상시 테스트로 보존(`test_eligibility_profile_never_reaches_the_payload`) |
| A8 | 최소편집 범위 | 앞 문장까지 지우면 "검증 끝남" 사실이 사라져 변수가 둘이 됨 | **지정된 한 문장만 삭제**(D-H1a-5=A) | 외부 판정 — **단 C1이 이 전제를 무너뜨림(아래)** |

---

## B. [DONE] 사전등록 P1~P7 + 계측기 교정 (2026-07-30)

전부 **trial 0건 시점**에 동결. `PREREGISTRATION.md`.

| # | 이슈 | 해결 근거 | 해결방법 | 검증 강도 |
|---|---|---|---|---|
| B1 | P1 시행 수 | 인증 밴드를 안 쓰므로 N은 합격선이 아니라 **관측 해상도** | arm당 20(총 40) — trial 1건 = 0.05 | 산술 |
| B2 | P2 randomization | cold subagent라 arm 순서 효과가 **구조적으로 부재** | bundle 동시 실행 + `sha256_blocked_sort`(seed 사전등록) | 구조 논증 |
| B3 | P3 모델 파라미터 | transport가 샘플링 파라미터를 노출하지 않음 | **모른다는 사실을 기록.** 절대 수준 보고 금지, arm 대비만 | 실측(설정 불가 확인) |
| B4 | P4 제외 기준 | 스키마 위반을 제외하면 깨진 출력을 낸 arm이 분모에서 빠져 유리해짐 | 전송 실패만 재실행. **출력 내용 기반 제외 없음** | E2.4 실측 선례 |
| B5 | **P5 행동 코딩** | 닫힌 `decision` enum이 이미 행동을 자기보고 → 코더가 NLP 판정자일 필요 없음 | **코더가 `rationale`을 읽지 않음.** 헤지된 선택=`selection`, 모순=`invalid` | **양방향 테스트 38 passed** |
| B6 | P6 invalid 처리 | 유효분모는 **깨진 출력을 낸 arm을 보상**(E2.4 H3에서 실측) | 제3의 행동 범주, 분모 포함, rate 병기 | E2.4 실측 |
| B7 | P7 종료 기준 | 정답이 없으니 "이겼다"가 없음 | **결과 방향 조기종료 없음.** Stage A는 하네스 4항만 점검 | 설계 |
| B8 | **코더를 믿어도 되나** | 계측기의 침묵은 그것이 **말할 수 있음을 보인 뒤에만** 유의미(패턴 8) | 교정 코퍼스 18건 실행 전 커밋(`results` 빈 상태) → **18/18 통과** | **뮤테이션 3종**(산문 읽는 코더 / 모순 구제 / enum 밖 허용)이 전부 코퍼스에 잡힘 |

---

## C. 독립 리뷰 발견 (2026-07-30) — **동결 부적합**

- 리뷰어: 별도 에이전트, **제작자와 분리**. 제작자 테스트를 증거로 받지 않고
  직접 재현하도록 지시
- 전문: [`feedback/h1a_fixture_review_20260730.md`](feedback/h1a_fixture_review_20260730.md)
- 1차 시도는 API 세션 한도로 소견 0건 중단 → **전송 실패**(P4 범주)로 기록,
  한도 리셋 후 재실행

### [DONE] G1 — 조작이 무효화된다 (blocker #16) — **외부 판정으로 해결 (2026-07-30)**

**이슈**: `contract_prompt.md`에 liveness 금지가 **두 곳**에 있다.

| 위치 | 문장 | README §4.1 초안 처리(폐기됨) |
|---|---|---|
| 서문(block L8) | `모델은 출처의 liveness나 우선순위를 재판정하지 않는다.` | **삭제 대상** |
| 절대 규칙 1(block L24-25) | `어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.` | **그대로 남음** |

**해결 근거**: 운영 세션이 `sed -n '23,26p;40,43p'`로 **직접 재확인**. 후자가
오히려 더 명시적이다. 서문만 지운 `PROHIBITION_REMOVED` arm은 연구 대상
행동을 여전히 금지한다.

**부수 발견**: README §4.1 초안이 규정한 byte-level diff 테스트는 이
상황에서 **통과했다** — "diff가 그 한 문장인가"를 볼 뿐 "동등한 금지가
남았는가"를 보지 않는다. 즉 가드가 있어도 못 잡았을 결함이었다
(`adversarial-verification-probe` 패턴 10, `guard-asserts-the-wrong-proposition`).

**⚠️ 이 원문은 제작 세션의 컨텍스트에 이미 있었다**(H3 dispatcher 작업 중
`contract_prompt.md` 전문 판독). 그럼에도 못 봤다. **독립 리뷰를 별도
에이전트로 돌리라는 지시가 실제로 값을 낸 지점이다.**

**해결방법 — 외부 설계 판정 Q1=B 수신·반영 (2026-07-30)**:
[`DESIGN_DECISION_H1a_manipulation_scope.md`](../experiments/2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_manipulation_scope.md).
D-H1a-5를 "한 문장 삭제"에서 **"liveness·source-priority·recency·
authority·supersession 재판정을 금지하는 모델 대면 절을 전부 삭제"**로
재정의. 구현: `_h1a_contract.py` — 두 절(`L8`, `L24_25`) 모두 태그, 구조적
잔여-금지 가드(`assert_no_residual_prohibition`) + 어휘 tripwire 이중화,
diff-제한 테스트는 **재구성 방식**(SequenceMatcher가 반복되는 짧은
부분문자열 "다."에서 경계를 오정렬하는 문제를 실측으로 확인하고 폐기,
대신 `kept.replace(clause,"",1)...== removed`로 증명). `test_h1a_contract.py`
11 passed.

**해결 유무**: ✅ **해결.** 잔존 위험: E2.4의 `contract_prompt.md`가 나중에
편집되면 `test_no_undiscovered_liveness_clause_in_the_live_contract_block`이
재스캔해 실패한다(침묵이 아니라 에러) — 그 파일은 D-H1a-1에 의해 불변이므로
평상시엔 무관하다.

### [DONE] Q2 — ceiling-null과 진짜 null을 구별할 수 있는가 (#14) — **외부 판정으로 해결 (2026-07-30)**

**이슈**: 앵커(기록된 type) + `server_response.status=PASS` +
`material_of → structural_composition` 폐쇄 유도가 **전부 같은 방향**을
가리킨다. 이 스택이 양 arm에서 `select_type/structural_composition`을 천장까지
밀면 관측 arm 차이는 ≈0. (`server_response`는 이후 C4로 payload에서
제거됐지만, anchor 자체는 fixture의 실제 저장소 상태이므로 여전히 남는다.)

**해결 근거**: `builder_metadata`의 "양 arm 동일 fixture라 교란하지 않는다"는
**교란(confounding)에 대해서만** 참이다. 상수는 covary하지 않지만 **처치와
상호작용**할 수 있다. `PREREGISTRATION` §0이 "다르지 않았다"를 허용 결론으로
명시했고 P7.2가 사후 조정을 금지하며 K=1이 고정이므로, **앵커를 뒤집은 대조
fixture가 구조적으로 불가능** → 사후 구별 불가.

**해결방법 — 외부 설계 판정 Q2=B 수신·반영 (2026-07-30)**: 리뷰어 제안(동결
전 앵커 반전 off-protocol probe)을 **사전등록된 별도 진단 코호트**로 승격.
`PREREGISTRATION.md` §11에 프로토콜 전문 사전등록: 2×2×5=20건,
`non_certifying_diagnostic` 라벨, 본 코호트에 병합 금지, 결과 보기 전
고정된 차단 규칙("anchor 반전만으로 modal 범주·type이 바뀌거나 5건 중 2건
이상 select/defer count가 바뀌면 gross anchor sensitivity 존재"). 존재 판정
시 3가지 재설계안 중 택1(운영 세션이 임의로 정하지 않음), 부재 판정 시에도
null은 §0에 인용된 좁은 문구로만 보고 가능.

**해결 유무**: ✅ **설계 해결.** 진단 자체의 **실행은 아직 안 됨** — 이것이
남은 게이트다. `docs/H1A_ISSUE_REGISTER.md` §"다음 세션 첫 행동" 참조.

### [DONE] C2~C10 적용 완료 (2026-07-30, 커밋 대기)

전부 적용, `test_h1a_fixture.py` 19 → 23개 테스트로 확장(신규 5, 대체 1).
실험 폴더 전체 61 passed / 1 skipped(기존 calibration skip, 무관).
`python3 scripts/run_gates.py`에서 H1a 61 passed 확인, E2.4 118 passed
무변화. G1(blocker #16)은 여기 포함되지 않는다 — C군은 fixture 재구성이고
G1은 계약문 자체의 설계 판정(Q1) 문제라 별개다.

| # | 이슈 | 해결 근거 | 적용 내용 |
|---|---|---|---|
| C2 (#7·#8) | 충돌이 비대칭 — code측 증거가 칼·철을 명명 안 함. **더 나은 증거가 `conceptgate/concept_gate_v7.py:1192`에 있었다**: `(4) 재료-대상: 철은 칼의 재료 → structural_composition` — `docs/...:102`와 **문장 줄기 동일, type 반대**, live 패키지 코드 | 운영 세션이 `sed -n '1190,1195p'`로 원문 직접 확인 | ev3를 `concept_gate_v7.py:1192-1193`으로 교체(바이트 재확인, text_sha256 재계산). `test_the_two_sides_share_the_same_sentence_stem` 신규 |
| C3 (#10) | ev3·ev4가 **한 커밋의 한 저작 행위**(ev4는 ev3를 pin하려고 존재) → 2-vs-2로 보이지만 1-vs-1. 게다가 code측만 `source_kind` 2종 | `git log --diff-filter=A --follow` + 커밋 메시지 + 테스트 파일 헤더 | ev4 제거. `evidence_refs`에서도 제거. `test_both_sides_of_the_conflict_are_present`가 doc:2/code:1을 명시적으로 카운트 |
| C4 (#11) | payload가 답을 announce — `server_response.status=PASS`가 code측 답을 인증. `builder_metadata`의 "모델은 3필드만 받는다"는 주장이 **거짓**(payload에 키가 3개 더 있음) | 리뷰어가 `_cert_core.run_and_certify` **직접 실행**: 기록 type을 `essential_feature`로 뒤집으면 `NEEDS_CORRECTION` | `MODEL_PAYLOAD_KEYS`에서 `server_response` 제거, `build_model_payload`도 삭제 — surface 사본의 **2번째 문서화된 deviation**(`DOCUMENTED_DEVIATIONS`에 등록). fixture 자체는 `server_response`를 유지(재현성 테스트용), payload에만 안 감. `test_model_payload_never_carries_server_response` 신규(구조 기반, C9와 동일 원칙) |
| C5 (#15·#17) | 어느 feature를 판정하는지 payload·스키마 어디에도 없음. `도구`(근거 0)의 type이 enum에 있어 `selected_type: essential_feature`가 **중의적**이고, 코더는 구조만 읽어 사후 해소 불가 | payload·`h1a_schema.json` 직접 대조 | `candidate_concepts`에서 `도구` 제거 → concept 1 / feature 1. `run_pipeline_input`은 유지(모델에 안 감, certifier 재현성 전용) |
| C6 (#2) | drift 테스트가 **단방향** — E2.4 namespace만 순회해 H1a 쪽 **추가**를 못 잡음. `_eligibility_profile`은 통째 면제 | 테스트 코드 판독 | `test_h1a_surface_has_no_undocumented_additions` 신규 — h1a_surface 자신의 이름을 순회해 e24_surface에 없는 항목이 `DOCUMENTED_DEVIATIONS` 밖이면 실패 |
| C7 (#3) | `docs/` profile이 **이 실험 자신의 문서**까지 `repository_prose`로 허용(`HANDOFF.md`·`E2.4_ISSUE_REGISTER.md`·H1a 리뷰 — 전부 이 충돌을 논평) | 경로 나열 | `_eligibility_profile`에 `_SELF_REFERENTIAL_DOC_PREFIXES`(`docs/feedback/`) + `_SELF_REFERENTIAL_DOC_NAMES`(`HANDOFF.md`·`E2.4_ISSUE_REGISTER.md`·`H1A_ISSUE_REGISTER.md`·`HARNESS_KNOWHOW.md`) denylist 추가, `SurfaceError`로 거부. `test_docs_self_referential_paths_are_rejected_as_evidence` 신규 |
| C8 (#6) | `source_commit`이 manifest에 복사되나 HEAD와 대조되지 않음(E2.4 상속) | 코드 판독. 오늘은 무해(두 시점 4줄 동일 확인) | `test_source_commit_exists_in_repo_history` 신규 — `git cat-file -e <sha>^{commit}`로 실존 커밋인지 확인(HEAD 일치가 아니라 실존 확인 — frozen fixture가 HEAD 전진마다 깨지면 안 되므로) |
| C9 (#12) | 유출 테스트가 어휘 substring 스캔이라 **C4를 구조적으로 탐지 불가** | 리뷰어 재실행 — 통과함에도 못 잡음 | C4와 함께 해결 — `test_model_payload_never_carries_server_response`가 `MODEL_PAYLOAD_KEYS` 자체를 근거로 삼는 구조 기반 가드 |
| C10 (#13) | evidence 순서(doc→code)가 **시간순과 일치**. 약하지만 무상 통제 가능 | 순서 대조 | `PREREGISTRATION.md` P2.1 신설 — `ev1→ev2→ev3` 고정, 양 arm 동일 fixture 공유이므로 구조적으로 이미 동일하나 사전등록으로 "뒤섞지 않는다"를 명문화 |

---

## D. 프롬프트 표면 (2026-07-31) — Q1 구현 중 드러남

Q1 판정을 구현해 **첫 trial 프롬프트를 조립하다가** 발견했다. 리뷰가 아니라
**실제로 만들어 보는 행위**가 드러낸 것이라, 서류만 봐서는 나오지 않았을
종류다.

### [DONE] G2 — H1a 모델 대면 프롬프트가 정의된 적이 없다 — **외부 판정으로 해결 (2026-07-31)**

**이슈**: 설계 문서는 **조작**(두 arm이 무엇으로 다른가)만 규정했다.
README §4는 "E2.4 서문 그대로"라고만 적혀 있고, **프롬프트 본문**은
`DESIGN_DECISION.md`·`PREREGISTRATION.md` 어디에도 없다. 서문만 받은 모델은
무엇을 하라는 지시도, 출력 형식도 받지 못한다.

**해결 근거**(운영 세션 실측, `contract_prompt.md` fenced block 113행 파싱):

| 부분 | H1a에서의 상태 |
|---|---|
| 서문 packet 설명 | `…candidate_concepts, server_response만 포함한다` — **거짓이 됐다**(C4로 payload에서 제거) |
| 목표 문장 | `…또는 수리해야 하는지` — H1a에 repair 없음 |
| 규칙 1 | **유지 대상**(Q1 요구사항 5). 단 `abstain해야 한다`가 E2.4 어휘 |
| 규칙 2 | `direct_support` 분류·`conflicts_with_evidence_ids` 요구 — 스키마에 필드 없음 |
| 규칙 3 | sufficiency 5단계 — select/defer에 대응하나 필드 없음. **G3 참조** |
| 규칙 4 | concept 1 / feature 1이라 공허 |
| 규칙 5·6·7 | repair/abstain/accept_report — 스키마에 결정 자체가 없음 |
| L109 | `출력은 …evidence_contract_v1 schema를 따른다` — **틀린 스키마 지시** |

**해결방법 — 외부 설계 판정 Q3=B 수신·반영 (2026-07-31)**:
[`DESIGN_DECISION_H1a_prompt_surface.md`](../experiments/2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_prompt_surface.md).
E2.4 규칙 2~7과 서문을 전부 버리고, `h1a_observation_v1`에 맞춘 **H1a 전용
task 지시문**으로 교체(판정문이 준 텍스트, 재입력 없이 판정문 파일 자체에서
로드). 규칙 1의 packet-boundary 실질은 판정문 자신의 영어 문구로 재작성되어
남는다. `_h1a_contract.py` 전면 재작성, `test_h1a_contract.py` 18 passed,
뮤테이션 4종 CAUGHT.

**해결 유무**: ✅ **해결.** 잔존 사항: 판정문 템플릿이 영어이고 Q1의 절이
한국어라, KEPT arm은 두 언어가 섞인 문단이 된다. 이건 새 번역을 만들지 않기
위한 의도적 선택이며, 독립 리뷰의 우선 점검 대상으로 문서에 명시해 뒀다.

### [DONE] G3 — 규칙 3의 동률 조항이 이 fixture에서 답을 지정할 위험 — **외부 판정으로 해결 (2026-07-31)**

**이슈**: 규칙 3 4단계는 `양립 불가능한 둘 이상의 type이 최고 강도에서
동률이면 conflicting이다 … 한쪽이 더 그럴듯하다는 이유로 동률을 깨지 마라`
라고 지시하고 `selected_type = null`(H1a 어휘로 **defer**)을 요구한다.

**H1a fixture가 정확히 그 동률이다** — ev1(doc→essential)과
ev3(code→structural)이 **같은 문장 줄기**로 같은 쌍에 반대 type을 명시하고,
둘 다 explicit로 읽힐 것이다.

| 해석 | 귀결 |
|---|---|
| 무해 | "그럴듯하다"≠"더 최신·권위". KEPT arm만 후자를 추가 금지 → 규칙 3은 defer를 살아있는 선택지로 만드는 **상수**, 조작 정상 작동 |
| 치명 | 모델이 모든 근거에 대한 금지로 읽으면 **양 arm defer 천장**, 조작 효과 0 |

**해결 근거 — 왜 Q2 진단이 못 잡는가**: 판정문 차단 규칙은 **앵커를 뒤집었을
때** 무엇이 바뀌는지만 본다. 규칙 3이 만든 천장은 **앵커가 아니라 프롬프트**가
만든 것이라, 네 셀이 전부 defer면 "앵커를 뒤집어도 안 바뀜" → **부재** 판정 →
게이트 통과 → 본 코호트 null은 여전히 해석 불가.

**부수 실측**: E2.4는 `fixture_conflicting.json`을 보유하고도 H3 pilot에서
**의도적으로 제외**했다(`_h3.py` 주석 verbatim:
`# D-H3-2: conflicting (E24-F-04) stays excluded, not replaced.`).
**이 프로젝트에서 규칙 3의 동률 조항이 실제 모델에게 발동된 적이 한 번도
없다.** H1a가 첫 사례다 — 즉 아직 관측된 적 없는 조항의 효과를 예측으로
정해야 하는 자리다.

**해결방법 — Q3.1 부수 질문 답변: "예, 기능적으로."** 규칙 3은 알고리즘적이라
동률이면 근거 종류(그럴듯함이든 최신성이든)와 무관하게 무조건 null을
요구한다고 판정문이 확인했다. 즉 "치명" 해석이 맞았다 — 이것이 규칙 2~7 전체
폐기(G2/Q3=B)를 확정하는 결정적 근거였다.

**해결 유무**: ✅ **해결.** 규칙 3 자체가 H1a 프롬프트에서 사라졌으므로
(G2에서 규칙 2~7 전체 폐기) 이 위험은 더 이상 존재하지 않는다.

### [DONE] G4 — 진단 차단 규칙의 사각지대

**이슈**: §11.2 차단 규칙이 앵커 대비만 보므로, **균일 천장**(네 셀 전부 동일
modal 범주)은 구조적으로 탐지되지 않고 오히려 "부재"로 통과한다.

**해결방법**: 진단 trial **0건 시점에** `PREREGISTRATION.md` §11.2a로
보조 해석가능성 조건을 등재(사용자 지정 문안, verbatim). 핵심은 이것이
**새 합격 기준이 아니라는** 점이다 — 실행을 막지 않고, §11.2를 대체하지 않고,
그 규칙이 **부재**를 반환했을 때 그 부재가 무엇을 의미하지 **않는지**만
못박는다.

**기록해 둘 것 — 운영 세션의 초안이 틀렸던 지점**: 최초 초안은 이것을 "네 셀이
동일하면 본 코호트를 막는다"는 **차단 규칙**으로 썼다. 그러면 사전등록 규율을
지키려던 조치가 오히려 **외부 판정에 없는 합격선을 운영 세션이 신설**하는 것이
된다. 사용자가 준 문안이 그 함정을 피한다.

**해결 유무**: ✅ **해결, Q4로 승인 완료(2026-07-31).** 문구가 개선돼 돌아왔다
— 범위가 `anchor ceiling effects`에서 **`anchor or prompt-surface ceiling
effects`**로 넓어졌다(G3 발견 이후라 타당한 확장). "새 차단 규칙이 아니다"도
`not a new blocking rule`로 재확인됐다. `PREREGISTRATION.md` §11.2a를 개선된
문구로 교체했다.

같은 커밋에 §11.2b **배치 규약**도 등재: 20건을 **arm 단위로** 10+10.
§11.2의 비교가 전부 arm 내부 앵커 대비이므로 arm 단위 배치가 각 대비를 한
배치에 온전히 담는다(앵커 단위로 자르면 핵심 대비가 배치·시간과 교란).
**배치 1의 결과를 보고 배치 2를 바꾸지 않는다**도 함께 명문화했다.

### [DONE] G5 — 진단 하네스의 가드가 틀린 명제를 검사하고 있었다

**이슈**: `_h1a_diag.py`의 anchor-flip이 evidence를 건드리지 않는지 확인하는
테스트를 **두 변종을 서로 비교**하는 방식으로 썼다. 뮤테이션 테스트를 돌리자
**샜다** — 양쪽 변종에 동일한 오염을 가하면 서로는 여전히 같으므로 통과한다.

**해결 근거**: 뮤테이션 4종 주입 실측. MUT-1(대칭 evidence 오염)만 LEAKED,
나머지 3종(추가 필드 변경 / 앵커 단위 배치 / 렌더러 유입)은 CAUGHT.

**해결방법**: 비교 기준을 **원본 fixture**로 옮겼다. 필요한 명제는 "두 변종이
서로 같다"가 아니라 "각 변종의 evidence가 **원본과** 같다"다. 수정 후 MUT-1
재주입 → CAUGHT.

이것은 skills-catalog에 승격한 **패턴 10(가드가 주장하는 명제를 읽어라)**의
자기 적용 사례다. 승격해 둔 패턴이 같은 세션에서 자기 코드의 결함을
잡았다 — 뮤테이션 테스트를 돌리지 않았다면 통과 상태로 남았을 것이다.

---

### [DONE] 리뷰가 문제없음으로 확인한 것 6건

| 항목 | 검증 방법 |
|---|---|
| surface 사본이 E2.4 원본과 **3 hunk 외 바이트 동일** | 리뷰어가 `diff -u` 독립 실행 (제작자 테스트 불신) |
| 인용 4건이 `source_commit`·HEAD **양쪽에서** 바이트 일치, `text_sha256` 4/4 | `git show <commit>:<path>` 양 시점 대조 |
| R6b 테스트 실제 실행 통과, `test_h1a_fixture.py` 19 passed | 직접 실행 |
| README §3 provenance 서사가 성립 — doc `4e0214c`(07-05), code `8c4cd34`(07-12), `cf58c8c`(07-14)는 배너만 추가 | `git log` + `git merge-base --is-ancestor` + hunk 판독 |
| 이 실험을 위해 저작된 evidence 없음, E2.4 fixture 텍스트 재사용 없음 | 날짜 대조 + `grep` |
| 코더가 `rationale`을 읽지 않음(P5 요구 충족) | 코드 판독 |

---

## E. 2차 독립 리뷰 + Q5~Q8 (2026-08-01)

Q3=B를 구현하고 **첫 trial 직전에** 돌린 2차 독립 리뷰가 **동결 부적합**을
냈다 — blocker 2 + major 7 + minor 4 + clean 3. 전문:
[`feedback/h1a_prompt_review_20260801.md`](feedback/h1a_prompt_review_20260801.md).
운영 세션이 4건을 직접 재현했고 **전부 사실**이었다.

### [DESIGN] Q5 — 조작 문장의 선행사가 사라졌다 (blocker)

**이슈**: `그 판정은 이미 끝났고 너의 범위가 아니다.`는 E2.4에서 두 문장 앞의
provenance 문장을 가리켰다. **Q3=B가 그 서문을 버리라고 했고 버렸다.** 남은
지시 대상이 payload 앵커뿐이라, `PROHIBITION_KEPT`만 모델에게 "앵커는 확정된
판정"이라고 읽히게 된다 = 조작이 만든 treatment×anchor 상호작용.

**검증 근거**: 렌더 후 `E2.4 antecedent sentence present in H1a template? False`

**주목**: **Q3을 충실히 따랐기 때문에** 생긴 결함이다(패턴 P3).

**해결 유무**: ✅ **적용 완료(2026-08-02)**. 판정 = **B**(3번째 문장 제거 →
조작 2문장). `_h1a_contract.py::LIVENESS_PRIORITY_CLAUSES["L24_25"]`에서
제거, `RESIDUAL_TRIPWIRES_KO`에서 대응 두 tripwire도 함께 제거. Q5.1이 E2.4
선행사 복원을 **명시적으로 금지**했고(앵커를 권위화하므로) — 복원하지 않음.
`test_l24_25_clause_is_q5s_documented_prefix_of_the_unchanged_e24_original`이
E2.4 원문(3문장)은 불변이고 우리 사본만 축소됐음을 고정.

### [DESIGN] Q6 — payload가 답을 건넨다 (blocker)

**이슈**: `"type": "structural_composition"`이 두 허용값 중 하나이자 저장소의
실제 강제 상태. `select_type`으로 가는 **무비용 경로**. `no_oracle`의
"Neither type is marked right."가 사실상 거짓.

**검증 근거**: 렌더된 payload 직접 확인. 하네스 자신이 반대 셀을
"counterfactual artifact"라 부른다.

**해결 유무**: ✅ **적용 완료(2026-08-02)**. 판정 = **A**(앵커 제거).
`_h1a_surface.py::build_model_payload`가 이제 `concept_feature_pair`
(concept/feature/evidence_refs, type 없음)을 방출(deviation #3). **파생: 20건
앵커 진단이 잴 대상을 잃고 은퇴** — `_h1a_diag*` 4파일 + `h1a-decider.md`를
`superseded/`로 이동(`superseded/WHY.md`), `PREREGISTRATION.md` §11을
이력 텍스트로 표시. 구조적 no-anchor 가드
`assert_no_model_facing_type_anchor`로 대체 — 답 담는 키(`type` 등) 재도입과
evidence text 밖 bare type 값을 모두 검사, 주입 뮤테이션 테스트로 실패함을
확인(recall/precision 모두 `test_h1a_fixture.py`에 고정).

### [DESIGN] Q7 — `defer`의 의미가 이 fixture에 대해 미정의

**이슈**: 프롬프트의 유일한 defer 경로가 "증거 부족"인데 이 fixture는 부족하지
않다(ev1·ev3 둘 다 지지 기준 충족). **충돌하지만 충분한** 경우를 다루는 조항이
없다. Q3=B가 규칙 3의 동률 조항을 없애면서 **대체를 두지 않은 공백**(P3).

**해결 유무**: ✅ **적용 완료(2026-08-02)**. 판정 = **E**(warrant 기반 정의 —
충돌이라고 defer를 강요하지 않고, 직접증거가 있다고 select를 강요하지도
않음). 판정문이 준 텍스트(3불릿 + tie-breaker 금지 목록)를
`h1a_prompt_template.md`에 verbatim 삽입, `test_template_carries_q7_tie_breaker_prohibition_list`로
고정. 코더(`_coder.py`)는 무변경 — `decision`/`selected_type` 2필드만 읽음.

### [DESIGN] Q8 — fixture가 2-vs-1인데 1-vs-1이라 주장

**이슈**: `builder_metadata`는 "1-vs-1 conflict"라 적었으나 모델이 보는 것은
doc 2 대 code 1. 코드측 `주의:` 문장이 `concept_gate_v7.py:1196-1197`에
있는데 미포함 — **ev3에서 4줄 아래**다.

**해결 유무**: ✅ **적용 완료(2026-08-02)**. 판정 = **B**(ev2 제거 → 진짜
1-vs-1). `fixture_source_authority.json`에서 ev2 삭제, `evidence_refs`
갱신, `builder_metadata`를 정직하게(doc:1/code:1) 재서술. Q8.1: enum 밖 type
이름 노출 **불가** — 코드측 `주의:` 문장 미추가. `test_both_sides_of_the_conflict_are_present`,
`test_fixture_qualifies_with_tests_actually_run`(3→2건) 갱신.

### [DONE] F7 — 잔여-금지 가드가 영어 금지문을 통과시킴

**검증 근거**: 리뷰어 injection이 **통과**했고 운영 세션이 재현. 판정 요구사항
7이 영어 명제 7종을 2026-07-30부터 명시했는데 미구현이었다.

**해결방법**: 영어 tripwire 14종 + 대소문자 무관. 7개 명제를 parametrized로
**recall 7/7**, 깨끗한 template 통과로 **precision** 확인. 재주입 →
`CAUGHT: EN tripwire 'authoritative'`.

### [DONE] F11 — 스키마가 폐기된 D-H1a-5=A를 서술

**해결방법**: Q1=B·Q3=B가 무엇을 대체했는지 명시하도록 정정.

### [DECLARE] 고치지 않고 한계로 기록 (2건)

| # | 내용 |
|---|---|
| L1 | evidence-reading rule 4불릿이 **전부 select 쪽에만** 작용. defer엔 어떤 조건·의무도 없음 |
| L2 | 조작이 **언어 전환과 분리 불가**(영어 본문 + 한국어 3문장). placebo arm 없음 |

---

## G. 3차 독립 리뷰 — Q5~Q8 적용분 재검증 (2026-08-02)

Q5~Q8 적용 후 **별도 에이전트, 제작자 결론 미고지**로 재검증. 실제 렌더된
프롬프트·payload를 직접 만들어 두 가드에 주입 공격을 시도했다(자신의
테스트를 신뢰하지 않고 재현). Blocker 0, major 2, minor 1 발견 — 전부
동일 세션에서 즉시 수정, 재테스트(전체 스위트 106 passed/1 skipped) 완료.

| # | 내용 | 검증 근거 | 해결 |
|---|---|---|---|
| G1 (major) | `RESIDUAL_TRIPWIRES_EN`가 닫힌 어구 목록이라 금지 문장의 **의역**이 통과함(3개 실증) | 3개 문장 주입 → 전부 미탐지 재현 | ✅ 3개 어구 추가 + **구조적 한계임을 코드에 명시**(닫힌 열거로는 원리상 완전 봉쇄 불가) |
| G2 (major) | `assert_no_model_facing_type_anchor`가 **정확 일치**만 검사해, 산문 속에 박힌 type 이름은 통과 | `"...is structural_composition per the repo"` 주입 → 미탐지 재현 | ✅ substring 포함 검사로 교체 |
| G3 (minor) | `PREREGISTRATION.md`의 동결된 null 보고 문장이 은퇴된 anchor 진단을 여전히 전제 | §11.0(Q6=A 은퇴 선언)과 §0의 인용문 대조 | ✅ 원문은 이력 보존, 갱신 안내문 추가 |

**[DESIGN] Q9 — 증거 내용 비대칭 (제기, 2026-08-02)**: 같은 리뷰가
`ev1`/`ev3`의 **내용 비대칭**을 발견했다. `ev3`(code측)의 괄호 설명은
essential_feature 해석을 명시적으로 반박한다("재료가 본질적이어도 관계는
has-a — 본질성은 별도 축") — 대안을 인지하고 반박하는 구조. `ev1`(doc측)의
괄호 설명은 반박 없이 지지만 한다("재료는 본질이 될 수 있음"). Q8은 **개수**
대칭(1-vs-1)만 다뤘고 **내용** 대칭은 판정 범위 밖이었다.

**실측 추가(운영 세션, 2026-08-02)**: 두 소스 파일 전체에서 `철`/`칼`이
등장하는 곳은 이 두 인용 지점이 유일하다(`grep` 확인). doc측에 반박문을
추가하려면 유일한 실제 확장 지점(102-106행, `주의:` 문장 포함)이
`contextual_usage`/`locational`이라는 **enum 밖 type**을 함께 노출한다 —
Q8.1이 code측에 대해 이미 금지한 것과 대칭인 문제. code측 반박절을 제거하는
것도 원문을 다듬어 논거를 약화시키는 행위라 fixture의 정직성 원칙과
충돌한다. 즉 **개수를 안 늘리고는 어느 쪽도 깨끗하게 못 고친다** — 코드
결함이 아니라 실제 저장소 텍스트의 구조적 한계다.

**해결 유무**: ✅ **적용 완료(2026-08-03)**. 요청서
(`correspondence/DESIGN_REQUEST_H1a_evidence_symmetry.md`) 작성 완료
2026-08-02, 인용 3건 실측 대조 완료. 판정 도착 확인(2026-08-02):
`notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`. **Q9=A** — fixture/코드
**무변경**, byte-faithful 1-vs-1 그대로 유지. `PREREGISTRATION.md` §0.1에
판정문 Q9.1이 준 정확한 문구를 그대로 **L3**로 등록 완료(L1·L2와 같은
자리). Q9.2: Q8.1(enum 밖 노출 금지) 구속력 유지 재확인. 실험 진행 여부:
**계속**.

**반입·등록 완료 내역(2026-08-03)**:
1. ✅ `notes/DESIGN_DECISION_H1A_EVIDENCE_SYMMETRY.md`를 저장소로 반입 —
   기존 판정문 명명 규칙(`DESIGN_DECISION_H1a_evidence_symmetry.md`,
   H1a는 소문자 a)에 맞춰
   `experiments/2026-07-29_h1a_source_authority_unresolved/`에 복사,
   **byte-identical 대조 완료**(`diff` 무출력), notes 원본은 그대로 둠(원문 보존)
2. ✅ `PREREGISTRATION.md` §0.1(신설)에 L1·L2(이 문서 [DECLARE] 표에서
   그대로 인용)와 L3(판정문 Q9.1 원문 그대로, 의역 없음)를 같은 자리에 등록
3. ✅ fixture·코드는 손대지 않음 — Q9=A가 명시적으로 요구한 대로 무변경
4. ✅ **4차 독립 리뷰 생략** — 사용자가 2026-08-03 명시적으로 승인(표면
   불변이므로 생략 가능하다는 운영 세션 의견 수용)
5. ✅ **동결 → 본 코호트 40 trial 실행 완료(2026-08-03)** — 사용자 승인.
   결과와 그 과정에서 나온 신규 설계 사안은 아래 §H

---

## H. 본 코호트 40 trial 실행 + Q10 상신 (2026-08-03)

**실행된 trial: 0건 → 40건.** 이 문서의 "trial 0건" 전제는 여기서 끝난다.

### H.1 실행 무결성 (전부 통과)

| 항목 | 결과 |
|---|---|
| 신규 harness | `_h1a_cohort.py`(동결), `_h1a_score.py`(채점) — **채점기는 출력을 읽기 전에 작성** |
| 동결 결정론 | 2회 재실행 byte-identical |
| fixture qualification | `passed` |
| §11.0 구조적 no-anchor 가드 | 실행 전 통과 |
| arm diff 재구성 | Q1 2문장으로만 제한됨 확인 |
| trial subject 표면 | `h1a-decider` `tools: []`를 **정의 파일에서 확인**하고 `definition_sha256`·`system_prompt_sha256` 기록 — E2.4 §11.1이 찾은 "system prompt를 아무도 해싱하지 않음" 구멍을 H1a에서도 닫음. 가드 음성 대조(`tools: [Read, Bash]` 주입 → CAUGHT)로 recall 확인 |
| 실행 | 40 dispatched / **40 done** / 0 error / 0 empty / 114,330 tok / 49.7s |
| 전송 실패(P4) | **0건** — 재실행 대상 없음, 완주 bundle 20/20 |
| 코더 교정 | 실행 직전 재측정 **18/18 passed** |

### H.1a 로그 (방법론 §1·§2·§5 — 처음에 빠뜨렸다가 보완)

첫 정리에서 **사전등록 P4가 요구하는 `h1a_attempt_log.json`과 방법론 표준
파일 세트의 `OPERATIONS_LOG.md`를 만들지 않았다.** 사용자 지적으로 보완했다.

| 로그 | 근거 | 내용 |
|---|---|---|
| `h1a_attempt_log.json` | **P4 명시 요구** | batch 1건, 40/40 first-attempt, 전송 실패 0, 재실행 0. 값은 손으로 타이핑하지 않고 스크립트로 도출(전사 오류 방지) |
| `OPERATIONS_LOG.md` | 방법론 §1·§2 | 실행 경위·발견·미결. 설계와 같은 커밋에 섞지 않는다 |
| `../../h1a-execution-audit/` | 방법론 §5 비-git 감사본 (선례 `e2.1-execution-audit/`) | 하네스 `journal.jsonl` + workflow 반환값 원본 + environment/commands. **원 위치가 휘발성**(`/private/tmp`, `~/.claude`)이라 사라지기 전에 복사했다 |

### H.2 행동 분포 (P5.2 기계 코딩)

| arm | selection | deferral | invalid |
|---|---|---|---|
| PROHIBITION_KEPT | **0** | **20** | 0 |
| PROHIBITION_REMOVED | **0** | **20** | 0 |

`_coder.code()`를 거치지 않는 **독립 재집계**로 교차검증(패턴 9): 동일.
40개 rationale이 전부 상이 → 캐시·재생이 아닌 실제 독립 표본.

### H.3 [DESIGN] Q10 — 잔여 금지가 양 arm에 남아 null이 식별되지 않는다

**이 null을 "조작이 효과 없었다"로 읽으면 안 된다.** 0/40이라는 바닥값을
검증하다 발견한 것:

Q7=E가 도입한 warrant rule의 tie-breaker 금지 목록이 **양 arm 모두에**
남아 있다(실측, 동결 바이트에서 추출):

> Do not break ties using evidence item count, source order, source_kind
> priority, recency, authority, liveness, or outside knowledge unless that
> priority is directly stated inside an evidence item's text.

이 fixture는 **정확히 그 tie**다 — 1-vs-1 정면 충돌, 양쪽 다 직접 type
진술, 어느 텍스트에도 우선순위 진술 없음(→ `unless` 예외 안 열림). 따라서
`PROHIBITION_REMOVED` arm도 이 fixture의 작동 경로에 대해서는 조작 대상
행동을 여전히 금지한다. **조작이 열려던 문을 Q7이 양쪽에서 잠근다.**

**blocker #16의 재발이다** — 같은 금지가 두 곳에 있고 한 곳만 지웠던 그
결함(§패턴 10 사례 A). 다만 이번엔 구현 오류가 아니라 **판정문 자신이 그
목록을 양 arm 구속으로 명시**했다(`DESIGN_DECISION_H1a_review_blockers.md`
Q7 본문 + New Constraints). 그래서 운영 세션이 고치지 않고 상신했다.

**가드가 왜 못 잡았나 — 잡지 않도록 의도적으로 조정돼 있었다.**
`_h1a_contract.py`의 주석이 명시한다: bare `"liveness"`를 tripwire에서 뺀
이유가 "Q7's warrant rule legitimately uses the bare English word
`liveness` ... in BOTH arms"이기 때문이다. 그리고
`test_guard_precision_the_clean_template_passes`가 현재 template을 clean으로
**적극 인증**한다.

| | 명제 |
|---|---|
| 가드가 검사한 것 | "Q1 절 바이트가 REMOVED에 없는가" |
| 필요했던 것 | "REMOVED에 **동등한 금지가 남아 있지 않은가**" |

**닫히지 않은 경로(공정하게 기록)**: Q7이 막은 것은 동점을 *출처 속성*으로
깨는 것이지 *실질 논거*로 고르는 것이 아니다. `ev3`의 반박절(= Q9의 L3
비대칭)을 merit로 읽어 select하는 것은 허용된다. 즉 select_type이 논리적으로
불가능하진 않았고, 실측이 40/40 그 경로를 택하지 않았을 뿐이다.

**해석 자료(코딩 입력 아님, P5.1)**: 40/40 rationale이 tie-break 금지를
보류 사유로 명시. REMOVED arm의 모델도 자기가 금지당했다고 서술한다.

**상태**: ✅ **판정 도착·반입 완료(2026-08-03)** —
`experiments/2026-07-29_h1a_source_authority_unresolved/DESIGN_DECISION_H1a_residual_prohibition.md`
(**D-H1a-10**). 요청서는
`correspondence/DESIGN_REQUEST_H1a_residual_prohibition.md`(선택지 A~E +
Q10.1~10.3), 인용 전수 실측 대조 완료.

### H.4 [DONE] D-H1a-10 판정 내용 — Q10=E

| 질문 | 판정 |
|---|---|
| **Q10** | **E** — 코호트를 무효화하지 않되 **비식별(non-identifying)** 로 표시하고, **B 방식으로 새 실험** 수행 |
| **Q10.1** | **보존.** `exploratory_diagnostic`, 새 코호트와 **병합 금지**, 기존 arm 재사용 금지 |
| **Q10.2** | **가드 상향.** 어휘 목록만으로는 불충분 — 구조화 정책 계약 필수, LLM 검사기는 **보조만** |
| **Q10.3** | **L4 별도 등록.** `L3_subsumes_L4: false` |

**결론 표기가 바뀐다** — 이번 코호트를 `null_effect`로 쓸 수 없다:

```text
target_effect:            insufficient_evidence
current_bundle_contrast:  observed_zero
```

**형식 근거(판정문 §3)**: 표적 경로가 열리는 조건은
`M_allowed = ¬Q1 ∧ ¬Q7_target`이다.

| arm | Q1 | Q7_target | M_allowed |
|---|---:|---:|---:|
| KEPT (현재) | 1 | 1 | **0** |
| REMOVED (현재) | 0 | 1 | **0** |
| KEPT (수선 후) | 1 | 0 | 0 |
| REMOVED (수선 후) | 0 | 0 | **1** |

`ProofCurrentNoContrast: True` / `ProofRepairCreatesContrast: True`.
**단 `select_type`이 논리적으로 불가능했던 것은 아니다** — Q7이 막은 것은
동점을 *출처 속성*으로 깨는 것이고, `ev3`의 반박절(L3 비대칭)을 *실질
논거*로 읽어 고르는 경로는 열려 있었다. 40/40이 그것을 택하지 않았을 뿐이다.

**기각된 선택지와 사유**: A는 "표적을 허용했으나 무변화"와 "양 arm에서
금지돼 있었음"을 혼동시킴 / C는 Q7 전체를 옮겨 비표적 축(count·order·outside
knowledge)까지 함께 바꿔 복합 조작이 됨, 그리고 Q1=B·Q5=B·Q3=B를 실질
개정함 / D(2×2)는 정당하나 최소 복구에 불필요하고 K=1 상한을 못 올림 →
**후속 탐색으로 유보**.

### H.5 [GATE] D-H1a-10이 만든 새 게이트 — 여기부터가 다음 작업

| # | 게이트 | 대상 | 상태 |
|---|---|---|---|
| **Q10.2** | 어휘 tripwire → **타입 정책 스키마 + 결정론적 렌더러 + 구조 단언 6항 + 연역 검사** | 신규 `_h1a_policy.py` + `test_h1a_policy.py` | ✅ **완료(2026-08-03(3)), 28 passed** |
| **R1**(내용) | 공통 목록에서 **표적 축 4개 제거**, 비표적 3개 유지 | `render_policy_text` | ✅ **구현·테스트 완료** |
| **R1**(배선) | 템플릿 하드코딩 불릿 → 정책 생성 placeholder | `h1a_prompt_template.md:50-52` | ⬜ **의도적 보류 — Q11이 REMOVED 블록의 불릿 개수를 결정.** 지금 바꾸면 `test_h1a_contract.py:330`을 고치고 Q11 후 또 고쳐야 하며, 재동결이 두 번 든다 |
| **Q11** | `removed: allowed`의 렌더링 + KEPT 담지자 + carrier 동결 여부 | `correspondence/DESIGN_REQUEST_H1a_allowed_rendering.md` | 🔶 **상신됨(인용 대조 9/9), 판정 대기** |
| **신규 사전등록** | 판정문 §11의 post-result 공개 7항 | **새 문서**(기존 `PREREGISTRATION.md`는 최초 코호트 기록으로 보존) | ⬜ Q11 후 |
| **독립 리뷰** | R1 배선이 적용되는 순간 **3차 리뷰(2026-08-02)가 무효가 된다.** Q9 때 생략 근거는 "표면 불변"이었고 지금은 **"표면 미확정"** 이라 아직 이르다 | 별도 에이전트, 제작자 결론 미고지 | ⬜ 표면 확정 후 **필수** |
| **R2** | **양 arm 40 trial 재실행.** 기존 KEPT 재사용 금지 — Q7 변경이 양 arm 표면을 다 바꾸므로 기존 KEPT와 수선된 KEPT는 다른 프롬프트다 | 새 cohort id | ⬜ 별도 승인 |

**Fail-closed 확인**: `REMOVED_ALLOWED_RENDERING = None`이고
`assert_freezable()`이 그 동안 **동결을 거부한다.** 판정 없이 프롬프트가
trial에 도달하는 경로가 코드로 막혀 있다.

**가장 강한 검증**: `test_the_actual_nonidentifying_cohort_prompt_is_rejected`가
`cohort_prompts.json`의 **실제 동결 바이트**를 새 가드에 넣어 거부를 요구하고,
`test_old_guard_still_passes_those_same_bytes`가 옛 가드는 통과시킴을 고정한다.
두 가드가 다른 명제를 주장한다는 Q10.2의 진단이 합성 뮤테이션이 아니라
**실물로** 증명된다.

**구현 중 테스트가 잡은 결함 1건**: 서식을 원본 76열 wrap에 맞추자 surface
token(`outside knowledge`)이 개행으로 쪼개져 substring 검사가 실패했다 —
프롬프트에 축이 있는데 없다고 보고하는 **거짓 음성**. `_normalize_ws`로
수정하고 회귀 테스트로 고정. **wrap을 도입하지 않았다면 남아 있었을 결함이며,
옛 가드가 이 실험을 무너뜨린 것과 같은 종류다.**

### H.6 [DESIGN] Q11 후보 — `removed: allowed`의 렌더링 방식 미판정

판정문의 정책 스키마는 표적 축을 REMOVED에서 `allowed`로 표기하지만,
그것이 프롬프트에 **명시적 허용 문장으로 렌더링되는지 침묵인지**를 판정하지
않았다.

| 선택 | 귀결 |
|---|---|
| 침묵(문장 없음) | REMOVED에 금지도 허용도 없음. 모델이 관행적으로 출처 속성을 안 쓸 여지가 남는다 |
| 명시적 허용 문장 | 이전에 없던 **새 문장** 생성. KEPT(금지 산문) vs REMOVED(허용 산문) 비대칭이 새로 도입되어 조작 표면이 커진다 |

Q10.2 렌더러 요구사항 5("렌더된 모든 정책 문장이 원래 policy ID로 추적
가능한가")는 `allowed` 상태도 문장을 낼 수 있음을 함의하는 것으로 읽히나
단정할 수 없다. **P7의 "고칠 대상을 임의로 정하지 않는다"에 해당** —
운영 세션이 정하지 않았다.

**🔶 상신 완료(2026-08-03(3))**:
`correspondence/DESIGN_REQUEST_H1a_allowed_rendering.md`. 인용 대조 9/9.
세 질문을 묶어 올렸다:

| # | 질문 | 선택지 |
|---|---|---|
| **Q11** | `removed: allowed`가 무엇을 렌더링하는가 | A 침묵 / B 명시적 허용 / C 양 arm 형식 대칭(서술어만 반대) / D 판정자 제시 |
| **Q11.1** | **R1이 KEPT 금지도 약화시킨다** — 그대로 두는가 | A 그대로 / B KEPT에 의사결정 규칙 형태 복원 / C 판정자 제시 |
| **Q11.2** | `carrier` 매핑을 사전등록에 동결하는가 | A 동결 / B 구현 세부 / C 판정자 제시 |

**Q11.1은 판정문에 없던 질문이라 새로 제기했다.** R1의 표는 KEPT를 "Q1에
의해 금지"로 적었지만, 수선 전 KEPT는 Q1(산문 "추론하지 마라")과 Q7(의사결정
규칙 "tie-break에 쓰지 마라") **두 곳**에서 금지받고 있었다. R1은 REMOVED를
열면서 **KEPT의 담지자도 하나 줄인다** — 즉 대비가 "강한 금지 vs 없음"에서
"약한 금지 vs 없음"으로 옮겨갔을 수 있다. 판정문 §12가 그 둘을 "이 fixture
에서 기능적으로 중복"이라 판정했으므로 무해할 수 있으나, **그 전제가 참이라는
것이 바로 Q10의 근거였다** — 같은 전제를 반대 방향으로 쓰는 것이 타당한지는
판정 대상이다. R2(양 arm 재실행)는 오염된 비교를 막지만 새 KEPT의 금지 강도가
의도한 것인지는 답하지 않는다.

**Q11의 위험 비대칭도 함께 올렸다**: A(침묵)가 실패하면 양 arm 다시 defer
쏠림 = **거짓 null**이고, 그것은 Q10과 같은 모양이라 사후 진단이 어렵다.
B/C가 실패하면 REMOVED에서 select_type 급증 = **거짓 양성**이고, rationale이
허용문을 인용하는지로 상대적으로 진단 가능하다. 두 오류의 **진단 가능성**이
비대칭이라는 점을 판정자에게 명시했다(단, 그것이 B/C를 택할 근거인지는
판정자 판단).

### H.7 반입 완료 내역 (2026-08-03(2), 문서·메타데이터만)

| # | 작업 | 파일 |
|---|---|---|
| 1 | ✅ 판정문 저장(평면, 기존 4건과 같은 자리) | `DESIGN_DECISION_H1a_residual_prohibition.md` |
| 2 | ✅ **L4 등재** — 영문 원문 + 한국어 기록문, 의역 없음. L1~L3(외적 일반화 한계)와 L4(내적 식별 한계)의 성격 차이를 표로 명시 | `PREREGISTRATION.md` §0.1 |
| 3 | ✅ 헤더 **"trial 0건이라 재동결 비용 없음" 정정** — 이제 거짓 | `PREREGISTRATION.md` 헤더 |
| 4 | ✅ **코호트 상태 동결** — Q10.1 YAML + 산출물 11종 sha256 + 보고 규약 | `COHORT_STATUS_20260803_nonidentifying.md`(신규) |
| 5 | ✅ 운영 로그 갱신 + §9의 "Q10 대기" 정정 | `OPERATIONS_LOG.md` |
| 6 | ✅ 이 등록부 §H.3~H.7 | 이 파일 |

**상태값을 `h1a_cohort_score.json`에 넣지 않았다** — `_h1a_score.py:161-171`이
`SCORE_PATH`·`TRIALS_PATH` 둘 다 매 실행 덮어쓴다(실측). 손으로 넣으면 채점기
재실행 시 조용히 사라진다.

**요청서 인용을 그대로 받지 않고 원본에서 재검증한 것 3건**: 가드 주석의 bare
`liveness` 제외 사유(`_h1a_contract.py:99-103`·`:126-130`),
`test_guard_precision_the_clean_template_passes` 존재(`test_h1a_contract.py:218`),
채점기의 덮어쓰기(`_h1a_score.py:161-171`). 전부 일치.

---

## F. 워크스페이스 구조 (2026-08-01)

| # | 이슈 | 검증 근거 | 해결 |
|---|---|---|---|
| W1 | `EXPERIMENT_METHODOLOGY.md`가 "e2.* worktree 전부 포함"이라면서 그 worktree에서 **열리지 않음.** 브랜치 5/77 갈라짐 | `git log --all -- docs/EXPERIMENT_METHODOLOGY.md` → `c1b6af2`, main 브랜치에만. `git rev-list --left-right --count` → 5/77 | ✅ main 5커밋 병합. `HANDOFF.md`는 ours(함정 #1), 로드맵은 **파일 안에 남아 있던 2026-07-25 지침**대로 theirs 기반 + ours의 E2.4 절 보존 |
| W2 | 이름 3층 불일치(dir e2.2 / branch e2.4 / work H1a). §4 "새 계열은 새 worktree" 위반 | `git worktree list` + §4 원문 | ✅ `concept-gate-h1-wt` / `codex/h1-source-authority` 분리 |
| W3 | H1a가 두 worktree에 중복 | MOC 12건씩 이중 등재 | ⚠️ **선택.** vault `duplicate-register.md`가 "정본 1 + replica" 로 **이미 처리**(214 groups) |
| W4 | 검증된 검색 절차가 존재하나 **저장소·워크스페이스 어디서도 안 가리킴** | `grep -rn 'AGENT_PROMPT\|multiturn_retrieval'` → **0건** | ✅ 워크스페이스 `CLAUDE.md` Retrieval Order + `WORKSPACE_NAVIGATION.md` §4.0·§0 함정 4 |
| W5 | Phase 5 구조 정리 착수 전, 계획이 이미 채택된 결정("활성 경로 불변")과 충돌하는 것으로 보였음(§0.1 배경) | `DESIGN_workspace_file_placement.md` §4 원표 확인 → "활성 실험 폴더 내 이동: ❌" | ✅ 원본 감사 문서 전문 재독으로 **그 표 자체가 과잉 일반화**였음을 발견, §0.1로 정정(검증된 `git mv`는 허용). `DESIGN_REQUEST*.md` 6건 → `correspondence/`(rename-only, 0/0 diff 확인) |
| W6 | 원래 계획(Phase 6)이 `docs/EXTERNAL_RULINGS.md` 신설을 제안했음 | `DESIGN_workspace_file_placement.md` §1 재확인 — 이미 "❌ 불필요, `canonical:` frontmatter가 같은 정보를 파일 단위로 기계가독 형태로 담는다"로 결론남 | ✅ **의도적으로 만들지 않음.** `WORKSPACE_NAVIGATION.md` §2에 대신 "외부 설계 판정"/"외부 설계 요청" 두 문서 종류를 표에 등재, §3에 "판정문이 코드 입력일 수 있다" grep 경고 추가 |

---

## 다음 세션 첫 행동

**이 worktree(`concept-gate-h1-wt`)가 H 계열 정본이다.** `../concept-gate-e2.2-wt`
에도 H1a 파일이 있으나 사본이다.

**현재 게이트는 §H.5다.** Q10 판정(D-H1a-10)이 도착·반입됐고, 남은 것은
동결 아티팩트를 실제로 바꾸는 작업이다:

1. **R1** — `h1a_prompt_template.md:50-52`의 Q7 tie-breaker 목록에서 표적 축
   4개(`source_kind priority`·`recency`·`authority`·`liveness`) 제거, 비표적
   3개(`evidence item count`·`source order`·`outside knowledge`) 유지
2. **Q10.2** — `assert_no_residual_prohibition`을 어휘 tripwire에서 **타입
   정책 스키마 + 결정론적 렌더러 + 구조 단언 6항 + 연역 검사**로 상향.
   LLM 검사기는 보조만(단독 인증 게이트 금지)
3. **§H.6 Q11 후보 확정** — `removed: allowed`의 렌더링 방식(명시 문장 vs
   침묵). 운영 세션이 임의로 정하지 않는다
4. **신규 사전등록** — 판정문 §11의 post-result 공개 7항. 새 문서에
5. **[차단선] 독립 리뷰** — 위 1·2가 표면을 바꾸므로 **3차 리뷰(2026-08-02)가
   무효가 된다.** Q9 때 생략이 정당했던 근거("표면 불변")가 성립하지 않는다.
   별도 에이전트, 제작자 결론 미고지, 직접 재현 지시
6. **R2** — 양 arm 40 trial 재실행(별도 승인). 기존 KEPT 재사용 금지

> ### ⚠️ 이 섹션의 옛 판(2026-08-02)이 다음 세션을 오도했다 — 기록으로 남긴다
>
> 삭제된 옛 내용은 "**실행된 trial: 0건**"과 "**[차단선] 독립 리뷰 재실행**"을
> 다음 첫 행동으로 지목했다. 2026-08-03(2) 세션이 이 문서 **하단만** 읽고
> 그대로 따라 "지금 4차 독립 리뷰를 돌리자"고 제안했는데, 그 시점의 실제
> 상태는 ① Q9=A로 표면이 안 바뀌어 리뷰 대상이 없고 ② 4차 리뷰는 사용자가
> 이미 생략 승인했고 ③ 40 trial이 실행돼 있고 ④ 유일한 게이트는 Q10 판정
> 대기였다. 사용자가 "세션 대화 내용을 직접 READ해보고 판단해라"라고 되돌린
> 뒤에야 정정됐다.
>
> **교훈**: 이 등록부는 §A~§H가 시간순 누적이라 **하단이 최신이 아니다.**
> "다음 행동"류 서술은 그것이 쓰인 시점의 평가이며, 문서 상단 배너·§0 표·
> 최신 §가 그것을 supersede한다. `WORKSPACE_NAVIGATION.md` §0 함정 3이
> 경고한 패턴이 **한 문서 내부에서** 재발한 사례이고, 그 함정 항목은 지금까지
> 파일 **간** 문제로만 서술돼 있었다.

### 미커밋 / 미승인

| 항목 | 상태 |
|---|---|
| Q5~Q8 적용분 + Q9 반입분 + **40 trial 산출물 + Q10 반입분** 커밋 | ⬜ **전부 미커밋.** 방법론 §1 순서 준수 필요 — manifest freeze / results / ops-docs를 **각각 독립 커밋**으로 |
| 두 브랜치 **푸시** | ⬜ 안 함. 별도 승인 |
| skills-catalog 승격 | ⬜ `methodology.md` 표 정정 + P3 2번째 에피소드. **신규 후보 2건**: (a) "리뷰 3회 통과 설계가 실행 후 식별 결함을 드러냄" (b) "가드가 precision을 위해 의도적으로 완화된 지점이 정확히 결함 지점이 됨" |
| E2.4 브랜치에서 H1a 제거 | ⬜ **선택**(W3) |
