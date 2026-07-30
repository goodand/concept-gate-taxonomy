# H1a 이슈 등록부

- 갱신: **2026-07-30** — 설계 판정 7건 + 사전등록 7건 완료, **독립 리뷰에서
  blocker 1 + major 5 발견 → 동결 부적합**
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
| 설계 판정 | **완료** — 외부 판정 D-H1a-1~7 (`DESIGN_DECISION.md`) |
| 사전등록 P1~P7 | **완료** — `PREREGISTRATION.md`, trial 0건 시점에 동결 |
| 행동 코더 | **교정 통과 18/18**, 테스트 38 passed, 뮤테이션 3종 검증 |
| fixture | 제작됨(`20f7102`) — **독립 리뷰에서 동결 부적합 판정** |
| 실행된 trial | **0건** (재동결 비용 없음) |
| **진행을 막는 것** | **[GATE] G1 — 조작 무효화(blocker #16).** 설계 판정 Q1 필요 |

**허용 결론의 상한**(결과 보기 전에 고정, `PREREGISTRATION.md` §0):
H1a는 K=1이라 `P(행동 | 고정 packet, 고정 arm, 고정 모델·파라미터)`만
추정 가능하다. **N을 늘려도 이 상한은 올라가지 않는다.**

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

### [GATE] G1 — 조작이 무효화된다 (blocker #16)

**이슈**: `contract_prompt.md`에 liveness 금지가 **두 곳**에 있다.

| 위치 | 문장 | README §4.1 처리 |
|---|---|---|
| 서문 | `모델은 출처의 liveness나 우선순위를 재판정하지 않는다.` | **삭제 대상** |
| 절대 규칙 1 | `어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.` | **그대로 남음** |

**해결 근거**: 운영 세션이 `sed -n '23,26p;40,43p'`로 **직접 재확인**. 후자가
오히려 더 명시적이다. 서문만 지운 `PROHIBITION_REMOVED` arm은 연구 대상
행동을 여전히 금지한다.

**부수 발견**: README §4.1이 규정한 byte-level diff 테스트는 이 상황에서
**통과한다** — "diff가 그 한 문장인가"를 볼 뿐 "동등한 금지가 남았는가"를
보지 않는다. 즉 가드가 있어도 못 잡았을 결함이다.

**⚠️ 이 원문은 제작 세션의 컨텍스트에 이미 있었다**(H3 dispatcher 작업 중
`contract_prompt.md` 전문 판독). 그럼에도 못 봤다. **독립 리뷰를 별도
에이전트로 돌리라는 지시가 실제로 값을 낸 지점이다.**

**해결 유무**: ❌ **미해결.** A8(최소편집=한 문장)의 전제를 무너뜨린다.

**해결방법**: **[DESIGN] Q1로 상신.** 운영 세션이 정하지 않는다.

### [DESIGN] Q1 — 조작의 범위는 무엇인가

절대 규칙 1의 금지가 *조작의 일부*인가 *상수의 일부*인가?

| 안 | 귀결 |
|---|---|
| 상수로 유지 | REMOVED arm이 여전히 금지 → **실험이 아무것도 측정 못 함** |
| 조작에 포함 | 더 이상 "한 문장 제거"가 아님 → README §2의 연구 질문이 바뀜 |
| H1a 전용 계약문 신작 | 금지를 정확히 한 곳에만 배치. 단 "E2.4 서문 그대로"가 아니게 됨 |

부수 논점: 그 문장을 양 arm에 남기면 **상수 자체가 모델에게 liveness 추론을
금지**하는 것이라 Q2의 ceiling 우려와 상호작용한다.

### [DESIGN] Q2 — ceiling-null과 진짜 null을 구별할 수 있는가 (#14)

**이슈**: 앵커(기록된 type) + `server_response.status=PASS` +
`material_of → structural_composition` 폐쇄 유도가 **전부 같은 방향**을
가리킨다. 이 스택이 양 arm에서 `select_type/structural_composition`을 천장까지
밀면 관측 arm 차이는 ≈0.

**해결 근거**: `builder_metadata`의 "양 arm 동일 fixture라 교란하지 않는다"는
**교란(confounding)에 대해서만** 참이다. 상수는 covary하지 않지만 **처치와
상호작용**할 수 있다. `PREREGISTRATION` §0이 "다르지 않았다"를 허용 결론으로
명시했고 P7.2가 사후 조정을 금지하며 K=1이 고정이므로, **앵커를 뒤집은 대조
fixture가 구조적으로 불가능** → 사후 구별 불가.

**해결 유무**: ❌ **미해결.** 리뷰어 자신도 "치명적인지 문서화된 한계인지
모른다 — trial을 한 건도 안 돌렸다"고 명시.

**해결방법**: **[DESIGN] Q2로 상신.** 리뷰어 제안 동봉 — 동결 **전에** 앵커를
뒤집은 변종으로 소수 off-protocol trial을 돌려 버리고(코호트 미병합) 천장
여부만 확인하는 값싼 probe.

### [FIX] 조치 확정 — 적용 대기

| # | 이슈 | 해결 근거 | 해결방법 |
|---|---|---|---|
| C2 (#7·#8) | 충돌이 비대칭 — code측 증거가 칼·철을 명명 안 함. **더 나은 증거가 `conceptgate/concept_gate_v7.py:1192`에 있었다**: `(4) 재료-대상: 철은 칼의 재료 → structural_composition` — `docs/...:102`와 **문장 줄기 동일, type 반대**, live 패키지 코드 | 운영 세션이 `sed -n '1190,1195p'`로 원문 직접 확인 | **ev3를 그 줄로 교체** |
| C3 (#10) | ev3·ev4가 **한 커밋의 한 저작 행위**(ev4는 ev3를 pin하려고 존재) → 2-vs-2로 보이지만 1-vs-1. 게다가 code측만 `source_kind` 2종 | `git log --diff-filter=A --follow` + 커밋 메시지 + 테스트 파일 헤더 | **ev4 제거.** 1-vs-1을 1-vs-1로 제시 |
| C4 (#11) | payload가 답을 announce — `server_response.status=PASS`가 code측 답을 인증. `builder_metadata`의 "모델은 3필드만 받는다"는 주장이 **거짓**(payload에 키가 3개 더 있음) | 리뷰어가 `_cert_core.run_and_certify` **직접 실행**: 기록 type을 `essential_feature`로 뒤집으면 `NEEDS_CORRECTION` | **payload에서 `server_response` 제거.** surface 사본의 2번째 문서화된 deviation |
| C5 (#15·#17) | 어느 feature를 판정하는지 payload·스키마 어디에도 없음. `도구`(근거 0)의 type이 enum에 있어 `selected_type: essential_feature`가 **중의적**이고, 코더는 구조만 읽어 사후 해소 불가 | payload·`h1a_schema.json` 직접 대조 | **`도구` 제거** → concept 1 / feature 1 |
| C6 (#2) | drift 테스트가 **단방향** — E2.4 namespace만 순회해 H1a 쪽 **추가**를 못 잡음. `_eligibility_profile`은 통째 면제 | 테스트 코드 판독 | 양방향 + diff 기반으로 교체 |
| C7 (#3) | `docs/` profile이 **이 실험 자신의 문서**까지 `repository_prose`로 허용(`HANDOFF.md`·`E2.4_ISSUE_REGISTER.md`·H1a 리뷰 — 전부 이 충돌을 논평) | 경로 나열 | 자기언급 경로 배제 가드 |
| C8 (#6) | `source_commit`이 manifest에 복사되나 HEAD와 대조되지 않음(E2.4 상속) | 코드 판독. 오늘은 무해(두 시점 4줄 동일 확인) | HEAD 대조 테스트 |
| C9 (#12) | 유출 테스트가 어휘 substring 스캔이라 **C4를 구조적으로 탐지 불가** | 리뷰어 재실행 — 통과함에도 못 잡음 | 구조 기반 가드 추가 |
| C10 (#13) | evidence 순서(doc→code)가 **시간순과 일치**. 약하지만 무상 통제 가능 | 순서 대조 | 양 arm **동일** 고정 순서를 사전등록에 명시(교차하면 2번째 조작변수) |

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

1. **[FIX] C2~C10 적용** — 운영 세션이 처리 가능. fixture 재구성 +
   테스트 보강. 기존 `20f7102`를 되돌리지 않고 후속 커밋으로 쌓는다
   (무엇이 왜 바뀌었는지가 이력에 남아야 한다)
2. **[DESIGN] Q1·Q2 설계 요청서 발송** →
   `DESIGN_REQUEST_H1a_manipulation_scope.md`. H3 요청서와 같은 자족형
   (도메인 오리엔테이션 + 실측 embed + 비구속 권고 분리 + 회신 템플릿)
3. **동결·실행은 Q1 판정 이후.** C군 조치만으로는 G1이 풀리지 않는다.
   프롬프트 생성·해시 동결은 Q1이 정해져야 착수 가능
4. **`PREREGISTRATION.md` 갱신 시 변경 사유를 명시** — trial 0건이라
   재동결 비용은 없으나, 변경이 "결과를 봐서"가 아니라 **"실행 전 독립
   리뷰"** 때문임을 P-항목별로 기록한다
