# 진행 보고 — Refine ↔ Verify 수정 지시의 v0 구현 (설계 담당 전달용)

- 작성: 2026-08-22, 운영 세션
- 대상 독자: **저장소 접근이 없는 설계 담당.** 판정에 필요한 사실을 이 문서가
  자체 포함하며, 인용은 전부 저장소 원문·실행 로그 대조를 거쳤다
- 범위: 지시 수령(08-22 01:42)부터 현재까지 push된 커밋 8건, +4,070행/-11행
- 묻는 것: **§4의 구현이 설계 의도와 일치하는가**, 그리고 §6의 확인 대기
  3건에 대한 회신

---

## 1. 지시 §35가 요구한 순서 그대로 진행했다

| §35 요구 | 산출물 | 상태 |
|---|---|---|
| 7항목 gap 분석을 먼저 출력 | `DESIGN_RESPONSE_refine_verify_gap_analysis.md` | ✅ 완료 — 구현 착수 전 |
| 구현 순서 제안 | 같은 문서 §7 (v0 최소 변경 + 선행 조건) | ✅ |
| "추상적으로 깨끗하다는 이유로 확대 금지" | NO CHANGE REQUIRED 8항목 명시 판정 | ✅ |
| "이미 동등한 invariant가 있으면 재사용" | 신규 subtree 0건 — 아래 §3 | ✅ |

gap 분석의 핵심 발견(구현 방향을 정한 것): **kernel은 추출 대상이 아니라
기존재였다.** `conceptgate/cg_obligations.py`(Verdict/Assurance 분리, PASS는
evidence 필수, decider별 assurance 상한, fail-closed UNKNOWN 집계)가 이미
있었고 다른 실험 라인이 이미 소비 중이었다. 따라서 v0는 재작성이 아니라
**그 위에 지시의 delta만 가산**했다.

## 2. push된 커밋 8건 (시간순)

| 커밋 | 내용 |
|---|---|
| `1c6f9a2` | 지시 원문 + oracle yaml **verbatim 저장**(트랜스크립트 추출, sha256 기록) + 저장 전 검증(전제 5건 확인·delta 8건 실측·채택 기록 공백 1건·**두 문서 간 어휘 불일치 1건**) |
| `918f0b3` | §35 7항목 gap 분석 |
| `97ef4bd` | 아키텍처 semantic-zoom 다이어그램 4단(Z0 역할→Z1 권한→Z2 기제→Z3 실체; Z3만 as-built, 나머지는 target으로 명시) |
| `1d908d2` | 운영 문제 분석 §7 (이 지시와 무관한 세션 기록) |
| `996c0f0` | **v0 primitive 구현** (아래 §4) |
| `96a3063` | 구현 기록 + **C축 출처 검증**(아래 §6-③) |
| `775c0cb` | **배선 자기감사 — 결함 4건 발견**, 1건 즉시 수정 (아래 §5) |
| `3c81a61` | **MCP 표면 배선** — 신규 tool `certify_claims` (아래 §4-마지막 행) |

## 3. 재사용 우선 원칙의 실행 (지시 §35 마지막 명령)

| 필요 | 재사용한 것 | 신규 작성 회피 근거 |
|---|---|---|
| 판정 어휘 | 기존 `Verdict`/`aggregate` — §1.1 "새로 만들지 않는다" 준수 | — |
| 외부 의무 집합 수용 | **registry seam** — 다른 라인이 이미 만들어 둔 가산 확장을 커밋 blob에서 합류(바이트 동일 검증) | 재구현 = "검증된 기제 두 벌" |
| canonical bytes/hash | 다른 라인의 검증된 구현 **verbatim 이식** + provenance 주석 | 동일 |
| 인증 순환 검출 | **stdlib graphlib** | 외부 의존 0 |
| canonical JSON 규격(RFC 8785류) | 조사 후 **불채택** — 기존 검증 구현이 충족 | 실행 중 사슬에 새 의존 금지 |

**github subtree 신규 도입: 0건.**

## 4. 구현 ↔ 지시 조항 대응표 (설계 의도 일치 검증 요청의 본론)

| 지시 조항 | 구현 | 의도 준수의 증거 |
|---|---|---|
| §3.1 Stable Identity / §7 fingerprint | 신규 잎 모듈 `cg_identity.py` (의존 {hashlib, json}, import 3.2ms) — node/claim/graph/obligation_target 4종, **kind를 도메인 분리자로** (node fingerprint가 claim으로 검증 불가) | "same canonical fingerprint → same normalized representation, NOT same truth"를 docstring에 명시(I9) |
| **§29 negative contract** | 산문이 아니라 **AST 테스트로 집행** — kernel에 판정형 함수명(select/judge/certify/repair/infer/score…)이나 판정 모듈 import가 생기면 스위트가 실패 | 규율→기제 전환 |
| I8 FAIL/UNKNOWN/ERROR | `Verdict.ERROR` 추가. 집계 우선순위 **FAIL > ERROR > 전부PASS > UNKNOWN** (확정 위반 > 도구 고장 > 통과; ERROR는 PASS 차단). ERROR는 reason 필수 | 음성 테스트 3건 |
| I10/§24 인증 의존 순환 | `certification_cycle()` → `certify()`에 배선, `CERTIFICATION_CYCLE`로 FAIL. semantic graph 순환과 구별(R7) | 순환/무순환/집합밖참조 3방향 테스트 |
| §4.2/§16 revision 결박 | `ObligationResult.graph_revision`(가산 필드) + `stale_obligations()` — **None은 stale 아님**(revision 개념 없는 기존 경로를 거짓 stale로 만들지 않음) | R8 충족 |
| §15 CertificationProfile | dataclass + `LEGACY_RELATION_PROFILE`(§31-E 요구) — required/allowed_na 중복은 생성 시 거부, **없는 검사 = UNKNOWN ≠ PASS** | — |
| §6/I6/I3 Certified Projection | `certified_projection()` = **view** — 입력 claim을 변경하지 않음. lifecycle 갱신은 Refine의 쓰기로 남김 | I3 (Verify쪽 코드가 graph writer가 되지 않음) |
| §10 semantic support 경계 | `claim.evidence_anchoring` — **결정론적 어휘 결박**이며 semantic support가 **아님을 이름·docstring이 명시.** 어휘 부재 = UNKNOWN(FAIL 아님 — 부재가 비지지를 증명하지 않음). LLM decider는 실물 구현 시에만 registry 등록(YAGNI) | I9/laundering 방지 |
| §25 E2E-v0 | 9단계 관통 테스트: snapshot → candidate(origin/lifecycle) → Verify(무수정) → revision 결박 obligation → 수리 1회(**구 revision fingerprint 불변을 단언**) → stale 거부 → projection → derived는 origin 구별. §31-F의 who-wrote/authority를 전이마다 단언 | I1/I2/I3/I6 |
| **MCP 표면** | 신규 tool `certify_claims` — anchoring 계산 + 호출자 지참 prior verdict 병합 + profile 인증. **게이트 재실행 안 함**(이전 응답의 certificate를 호출자가 지참). prior 없이 호출 = 인증 0건이 정상 | "검사 안 됨 ≠ 통과" |

테스트: 신규 40건 포함 전체 135 passed, 루트 게이트 8 passed / 0 failed / 1 blocked.

## 5. 자기감사가 찾은 결함 4건 (은폐하지 않고 보고)

구현 직후 "테스트 통과 ≠ 실배선"을 적대 점검해 4건을 찾았다:

- **W1** 신규 기능 4종이 실제 MCP 경로에 미배선 → **`certify_claims` tool로 해소** (`3c81a61`)
- **W2** `Verdict.ERROR`를 내는 프로덕션 생산자가 없음 → **의도적 미결** (§6-①)
- **W3** `depends_on`을 채우는 생산자가 없어 순환 검출이 실전에서 미발동 → **의도적 미결** — 검출기를 발동시키려고 장식용 의존을 만드는 것 자체가 공허한 검사의 제조라 판단. Refine 수리 루프가 실제 의존을 나를 때 함께
- **W4** 신규 가드 2개가 이 저장소의 뮤테이션 강제 게이트 **스캔 표면 밖**(명명 규약 불일치) → 즉시 수정. 부수 발견: `conceptgate/` 패키지 전체가 그 게이트의 역사적 사각지대였음(이번 이전 해당 규약 함수 0개)

W4 수정의 효과는 즉시 실증됐다: 다음 날 쓴 신규 가드(prior verdict 형 검증)의
음성 테스트 부재를 게이트가 **몇 초 안에 거부**했다.

## 6. 설계 담당 확인 대기 3건

① **W2 — ERROR의 프로덕션 도입 방식.** 현행 reasoner 실패 처리는 진짜
crash와 "Java 없음(기본 Render 배포)"을 같은 예외 절, 같은 오류 코드로 잡고,
도구 docstring이 "미가용이면 unknown"을 호스팅 계약으로 문서화하고 있다.
I8대로 crash→ERROR로 바꾸면 **운영 중인 배포의 기존 응답이 바뀐다.**
가산이 아니라 계약 변경이므로 회신 후 별도 diff로 진행하겠다.
질문: (a) crash와 dep-부재를 오류 코드부터 분리한 뒤 crash만 ERROR로,
(b) 둘 다 ERROR로(호스팅 계약 개정), (c) 현행 유지 중 택일.

② **G32 — 어휘 불일치.** 지시 I8은 `FAIL/UNKNOWN/ERROR`, 동반 yaml의
평가 프로토콜 v1 enum은 `PASS/FAIL/UNSCORABLE/ERROR`. **UNKNOWN과
UNSCORABLE이 같은 상태인가?** 같다면 한 어휘로 통일 대상, 다르다면 그
구별의 정의가 필요하다. 운영 세션이 조용히 통일하지 않았다.

③ **oracle yaml의 출처 title 필드.** 8건 전부 웹 실측했다(1건은 ISO
paywall로 접근 불가). **실체는 전부 확인** — 단 O1·O2·O3·R1의 `title`이
논문의 verbatim 제목이 아니라 설명어다. 예: O1의 실제 제목은 "A Corpus of
Encyclopedia Articles with Logical Forms"(초록이 quantifier scope 코퍼스임을
확인). yaml 자신의 `fixture_template.source_locator`가 source-faithful 표기를
요구하므로, fixture 저작 전에 **verbatim 제목으로 교정된 yaml 개정판**을
요청한다.

## 7. 다음 순서 (지시 §33 기준)

P0 완료. P1(legacy E2E의 실 fixture 관통)은 `certify_claims`가 표면을 열어
착수 가능. P2(capability registry)·P3(Quantifier/Modal IR)·oscillation은
지시대로 후순위 유지. **Certified-gate 전환(Reason/Derive 입력을 Certified로
좁히기)은 authority 변경이라 착수하지 않았고 상신 대상으로 유지한다.**
