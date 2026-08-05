# H1a 이슈 등록부 (2026-07-31 스냅샷 — 더 이상 갱신 안 됨)

> ## 🔴 정본은 여기가 아니다 (2026-08-05 확인)
>
> **H1a는 2026-08-01 `concept-gate-h1-wt`(브랜치 `codex/h1-source-authority`)로
> 분리됐다.** 이 파일은 그 분리 직전(2026-07-31)의 스냅샷이고, 이후의
> Q5~Q12(D-H1a-5~12 전부), 가드 음성-테스트 게이트, 40 trial 실행 결과가
> 전혀 없다. **`../concept-gate-h1-wt/docs/H1A_ISSUE_REGISTER.md`를 읽어라.**
> 아래 본문은 그 시점까지의 이력으로만 보존한다 — "이 문서가 이슈 전체
> 목록"이라는 옛 서술은 더 이상 참이 아니다.

---

## 0. 상태 요약

| 항목 | 값 |
|---|---|
| 실험 | `experiments/2026-07-29_h1a_source_authority_unresolved/` |
| 설계 판정 | **완료 (3건)** — D-H1a-1~7 (`DESIGN_DECISION.md`) +
  조작 범위 Q1·Q2 (`DESIGN_DECISION_H1a_manipulation_scope.md`) +
  프롬프트 표면 Q3·Q4 (`DESIGN_DECISION_H1a_prompt_surface.md`) |
| 사전등록 P0.1 + P1~P7 + §11(11.2a·11.2b) | **완료** — `PREREGISTRATION.md`, trial 0건 시점에 갱신 |
| 행동 코더 | **교정 통과 18/18**, 테스트 38 passed, 뮤테이션 3종 검증 |
| fixture | `20f7102` → **C2~C10 재구성 적용(2026-07-30), 커밋 대기** |
| 프롬프트 표면(arm) 렌더러 | **G1·G2·G3 해결.** `_h1a_contract.py` — Q3=B 반영, H1a 전용 template + Q1 절 삽입, `test_h1a_contract.py` 18 passed, 뮤테이션 4종 CAUGHT |
| 진단 하네스 | 프롬프트 독립 부분 완성 — `_h1a_diag.py`, `test_h1a_diag.py` 20 passed |
| 실행된 trial | **0건** (재동결 비용 없음) |
| **진행을 막는 것** | **[GATE] G2 — 모델 대면 프롬프트 표면 미정의.** 진단조차 렌더링할 수 없다. `DESIGN_REQUEST_H1a_prompt_surface.md` Q3 판정 필요 |

**허용 결론의 상한**(결과 보기 전에 고정, `PREREGISTRATION.md` §0):
H1a는 K=1이라 `P(행동 | 고정 packet, 고정 arm, 고정 모델·파라미터)`만
추정 가능하다. **N을 늘려도 이 상한은 올라가지 않는다.** null 결론은
anchor 진단(§11) 통과 후에만, 그것도 "이 고정 packet 하에서"로 좁게만
보고 가능 — "조작이 일반적으로 효과 없다"는 금지.

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

## 다음 세션 첫 행동

1. ~~**[FIX] C2~C10 적용**~~ — 완료(2026-07-30), 61 passed
2. ~~**Q1·Q2 설계 요청서 발송·회신·반영**~~ — 완료. `_h1a_contract.py`
   11 passed
3. ~~**Q4 보조 조건 + 배치 규약 사전등록**~~ — 완료(2026-07-31),
   `PREREGISTRATION.md` §11.2a·§11.2b. **진단 0건 시점에 등재됨**
4. ~~**진단 하네스 프롬프트 독립 부분**~~ — 완료. `_h1a_diag.py`,
   `test_h1a_diag.py` 20 passed, 뮤테이션 4종 확인(G5)
5. ~~**`DESIGN_REQUEST_H1a_prompt_surface.md` 발송 → Q3·Q4 판정**~~ —
   완료(2026-07-31). `DESIGN_DECISION_H1a_prompt_surface.md` 도착.
   Q3=B(H1a 전용 프롬프트) · Q3.1=예 · Q4=승인(문구 개선) 반영 완료
6. ~~**Q3 반영 — 프롬프트 재구현**~~ — 완료. `_h1a_contract.py` 전면
   재작성, `test_h1a_contract.py` 18 passed, 뮤테이션 4종 CAUGHT
7. **[다음 단계] 독립 리뷰(별도 에이전트, 제작자 결론 미고지).** 최우선
   공격 대상: 새 프롬프트가 select/defer 한쪽으로 기울었는가. 특히
   `_h1a_contract.py`가 스스로 표시해 둔 판단(영어 템플릿에 한국어 liveness
   절을 그대로 삽입, 번역하지 않음)을 검토
8. **[리뷰 통과 후] agent 정의 설치 → 동결 → 진단 실행**
   - agent 정의는 스키마를 별도 임베드할 필요 없음 — Q3 템플릿 자체가
     `h1a_observation_v1`을 프롬프트 안에 인라인으로 보여준다(H3와 다른
     선택, 판정문이 그렇게 줌)
   - 진단 20건은 **arm 단위 10+10**(§11.2b). Agent/Workflow 호출이므로
     **사용자 명시 허가 별도 필요**
9. **본 코호트 동결·실행은 진단 게이트 통과 후.**

**커밋 미완 목록**(전부 사용자 명시 승인 필요, CLAUDE.md). `20f7102`를
되돌리지 않고 후속 커밋으로 쌓는다:

| 구분 | 파일 |
|---|---|
| fixture 재구성 | `fixture_source_authority.json`, `_h1a_surface.py`, `test_h1a_fixture.py` |
| 프롬프트 표면(Q1+Q3) | `_h1a_contract.py`, `test_h1a_contract.py` |
| 진단 하네스 | `_h1a_diag.py`, `test_h1a_diag.py` |
| 사전등록·설계 | `PREREGISTRATION.md`, `DESIGN_DECISION_H1a_manipulation_scope.md`, `DESIGN_REQUEST_H1a_prompt_surface.md`, `DESIGN_DECISION_H1a_prompt_surface.md` |
| 문서 | `README.md`, `docs/H1A_ISSUE_REGISTER.md` |
