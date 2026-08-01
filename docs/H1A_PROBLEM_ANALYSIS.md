# H1a 문제 분석 — 패턴, 정의, 검증 근거, 해결 유무

- 작성: 2026-08-01
- 문서 종류: **운영 로그**(`WORKSPACE_NAVIGATION.md` §2). 동결 아티팩트와 같은
  커밋에 섞지 않는다
- 관계: `H1A_ISSUE_REGISTER.md`가 **시간순 기록**이라면 이 문서는 **패턴별
  단면**이다. 같은 사건을 다르게 자른 것이므로 둘 중 하나만 읽으면 안 된다
- 범위: H1a 설계·구현 전체 + 그 과정에서 드러난 워크스페이스 구조 문제
- **실행된 trial: 0건.** 아래 모든 문제는 실행 이전에 발견됐다

---

## 0. 규모

| 항목 | 수 |
|---|---|
| 외부 설계 판정 | 4회 (D-H1a-1~7 / Q1·Q2 / Q3·Q4 / Q5~Q8) |
| 독립 리뷰 | 2회 (2026-07-30 fixture, 2026-08-01 프롬프트) |
| 리뷰가 낸 blocker | 1차 1건, 2차 2건 |
| 해결된 문제 | 18 (실험 16 + 워크스페이스 2) |
| 미해결 문제 | 8 (판정 수령·미적용 4 + 그 파생 3 + 선택 1) |
| 고치지 않고 한계로 기록 | 2 |

---

## 1. 패턴 — 문제 정의

같은 형태가 반복됐다. 개별 이슈보다 이쪽이 재사용 가치가 있다.

### P1. 가드가 **참인 명제**를 검사하는데, 그것이 **필요한 명제가 아니다**

**정의**: 검사기가 정직하게 통과하고 그 판정도 옳지만, 그것이 참으로
만드는 명제와 실제로 보증되어야 할 명제가 다르다. recall/precision을 아무리
재도 잡히지 않는다 — 두 측정 모두 "가드가 올바른 것을 검사한다"를 전제하기
때문이다.

이 실험에서 **네 번** 발생했다:

| # | 가드가 참으로 만든 것 | 필요했던 것 | 결과 |
|---|---|---|---|
| 1 | "두 프롬프트의 diff가 지정된 한 문장이다" | "어느 arm에도 동등한 금지가 남지 않았다" | 조작 무효(blocker #16) |
| 2 | "두 anchor 변종이 서로 같다" | "각 변종이 **원본 fixture와** 같다" | 대칭 오염이 통과 |
| 3 | "절의 바이트가 정확히 이동했다" | "옮겨진 자리에서도 **같은 것을 가리킨다**" | 선행사 상실(Q5) |
| 4 | 스키마 `description`이 오라클 금지를 **선언** | 그 선언을 **실행**하는 검사기 | fixture 4개가 몇 주간 유출(E2.4 선례) |

**#3이 새 변종이다.** 바이트 동일성 검사는 **문맥 의존 의미**에 대해 원리상
아무 말도 할 수 없다. 대명사·지시어("그 판정", "위 규칙", "this")를 다른
문서로 이식하면 선행사가 남겨진다.

### P2. 계측기의 **침묵이 검증되지 않았다**

**정의**: 가드가 통과했는데, 그 가드가 애초에 **실패할 수 있음을 보인 적이
없다.** 침묵은 그것이 말할 수 있음을 보인 뒤에만 의미가 있다.

| 사례 | 실태 |
|---|---|
| 잔여-금지 가드 | 한국어 tripwire 8종만. Q3=B로 template이 **영어가 된 뒤에도** 그대로. 판정 요구사항 7이 영어 명제 7종을 2026-07-30부터 명시했는데 미구현 |
| 진단 evidence 불변 검사 | 뮤테이션 4종 중 1종(대칭 오염)이 **누출** |
| 코더 교정 코퍼스 | 18/18 통과 — 단 그것만으로는 "코퍼스가 아무것도 구별 못 함"과 구별 불가 → 뮤테이션 3종 주입으로 해소 |

### P3. **상위 판정을 충실히 따른 것이 새 결함을 만든다**

**정의**: 구속력 있는 판정을 정확히 이행했는데, 제거된 것이 **다른 것을
떠받치고 있었다.** 판정 자체는 옳고, 이행도 옳고, 그래도 결함이 생긴다.

| 판정 | 이행 | 파생 결함 |
|---|---|---|
| Q3=B "E2.4 서문을 버려라" | 버림 | `그 판정은 이미 끝났고…`의 선행사가 그 서문에 있었다 → **Q5** |
| Q3=B "규칙 2~7을 버려라" | 버림 | 규칙 3의 동률 조항이 유일한 충돌 처리 규칙이었다 → 대체 없이 **공백** → **Q7** |

**이 패턴은 판정을 의심하라는 뜻이 아니다.** 판정 이행 후 "**제거한 것이
무엇을 떠받치고 있었는가**"를 별도로 확인하라는 뜻이다.

### P4. **문서가 자기 상태를 잘못 서술한다**

**정의**: 아티팩트의 자기서술이 그 아티팩트의 실제 속성과 다르다. 자기서술은
검증되지 않으므로 조용히 stale해진다.

| 아티팩트 | 주장 | 실제 |
|---|---|---|
| `builder_metadata.no_oracle` | "Neither type is marked right." | payload가 두 허용값 중 하나를 건넨다 |
| `builder_metadata.purpose` | "This is a 1-vs-1 conflict" | 모델이 보는 것은 doc 2 대 code 1 |
| `h1a_schema.json` description | 조작 = "one prohibition sentence"(D-H1a-5=A) | Q1=B와 Q3=B가 두 번 뒤집음 |
| `EXPERIMENT_METHODOLOGY.md` | "concept-gate-e2.*-wt worktree 전부 포함" | 그 worktree들에서 **열 수 없었다** |
| (E2.4 선례) `cg_partwhole.py` docstring | "참조용 — 직접 import하지 않음" | 두 모듈이 라이브 경로에서 import |

### P5. **검색 방법이 결론의 완전성을 결정한다**

**정의**: lexical 검색은 "이것이 **이미 결정됐는가**"에 답할 수 없다. 결정
문서의 제목이 질문의 어휘를 포함하지 않을 수 있기 때문이다.

실측: 활성 실험 폴더 정리를 설계하면서 `rg`로 "디렉토리 정리 / DESIGN_DECISION
/ canonical"을 훑었다. 이미 채택된 결정
(`notes/audits/vault/symlink-vs-moc-2026-07-30.md`, `status: finished`,
"Keep repository and active experiment paths unchanged")이 **걸리지 않았다** —
그 문서 제목이 "Format storage, symlink views, and MOC validation"이라
교집합이 0이기 때문이다. **backlink 1홉**으로 나왔다.

### P6. **제작자는 자기 결함을 보지 못한다**

**정의**: 결함의 원문이 제작 세션의 컨텍스트에 **이미 있었는데도** 발견되지
않는다. 자체 점검으로 닫히지 않는다 — 가드를 쓴 사람은 그 가드가 필요한
명제를 검사한다고 이미 믿고 있다.

| 리뷰 | 발견 | 비고 |
|---|---|---|
| 1차 (07-30) | blocker #16 외 major 5 | 문제의 계약문 전문이 제작 세션 컨텍스트에 있었다 |
| 2차 (08-01) | blocker 2 + major 7 | 선행사 상실·앵커 유출·영어 tripwire 공백·2-vs-1 |

두 리뷰 모두 지시에 **"제작자의 테스트를 증거로 받지 말고 직접 재현하라"**가
있었다. 1차·2차 모두 제작자 테스트는 **통과 중**이었으므로, 그것을 증거로
받았다면 둘 다 "검증됨"으로 읽혔을 것이다.

### P7. **구조가 이름과 어긋난 채 누적된다**

| 층 | 이름 | 실제 |
|---|---|---|
| 디렉토리 | `concept-gate-e2.2-wt` | E2.2 아님 |
| 브랜치 | `codex/e2.4-contract-repo-design` | E2.4 아님 |
| 실제 작업 | H1a | 둘 다 아님 |

여기에 브랜치 **5/77 갈라짐**이 겹쳐, main의 문서 개선이 실험 세션에 영영
도달하지 않았다.

---

## 2. 문제별 — 정의 / 해결 유무 / 검증 근거 / 해결 방법

### 2.1 해결됨 (17건)

| # | 문제 정의 | 검증 근거 | 해결 방법 |
|---|---|---|---|
| G1 | liveness 금지가 계약문 **두 곳**에 있는데 설계는 하나만 제거 → `PROHIBITION_REMOVED`가 여전히 연구 대상 행동을 금지 | 운영 세션이 `sed -n '23,26p;40,43p' contract_prompt.md`로 두 절 원문 직접 확인. 절대 규칙 1 쪽이 더 명시적 | **Q1=B** — 조작을 "liveness/priority/recency/authority/supersession 금지 절 **전부** 제거"로 재정의 |
| G2 | H1a 모델 대면 프롬프트 본문이 **정의된 적이 없다**. 설계 문서는 조작만 규정 | 계약문 113행을 H1a 스키마에 대조: 서문의 `server_response` 언급 거짓, 목표 문장에 repair, 규칙 2·5·6·7이 스키마에 없는 필드 요구, L109가 틀린 스키마 지시 | **Q3=B** — E2.4 규칙 2~7·서문 폐기, `h1a_observation_v1`에 맞춘 전용 프롬프트 |
| G3 | 규칙 3 4단계(동률→null)가 이 fixture 모양을 **조작과 무관하게** `defer`로 매핑 | ev1·ev3이 같은 문장 줄기로 반대 type을 명시 → 둘 다 explicit → 동률. 판정문 **Q3.1이 "예, 기능적으로"**로 확인(규칙이 알고리즘적이라 근거 종류 무관) | 규칙 2~7 전체 폐기로 소멸(G2와 동일 조치) |
| G4 | §11.2 차단 규칙이 **앵커 대비만** 보므로 균일 천장은 "부재"로 통과 | 규칙 문구 판독 — 네 셀이 전부 같으면 "바뀐 것 없음"이 되어 게이트 통과 | **Q4 승인.** 보조 해석가능성 조건 사전등록(실행 0건 시점). 판정문이 범위를 `anchor` → **`anchor or prompt-surface`**로 확장 |
| G5 | 진단 evidence 불변 검사가 **두 변종을 서로** 비교 → 대칭 오염 통과 | 뮤테이션 4종 주입 실측: MUT-1(양쪽에 동일 오염) **LEAKED**, 나머지 3종 CAUGHT | 비교 기준을 **원본 fixture**로 이동. 재주입 → CAUGHT |
| C2 | code측 증거가 칼·철을 명명 안 함(일반 매핑 행) — 충돌이 비대칭 | `concept_gate_v7.py:1192-1193`이 doc측과 **문장 줄기 동일·type만 반대**임을 원문 대조 | ev3 교체, `text_sha256` 재계산 |
| C3 | ev3·ev4가 **한 커밋의 한 저작 행위** → 2-vs-2로 보이나 1-vs-1 | `git log --diff-filter=A --follow` + 커밋 메시지 | ev4(test) 제거 |
| C4 | `server_response.status=PASS`가 code측 답을 **구조적으로 인증** | 리뷰어가 `_cert_core.run_and_certify` 직접 실행 — 기록 type을 뒤집으면 `NEEDS_CORRECTION` | payload에서 `server_response` 제거(surface 사본 2번째 문서화 deviation) |
| C5 | 어느 feature를 판정하는지 명시 없음 + 근거 0인 filler가 중의성 유발 | payload·스키마 직접 대조 | `도구` 제거 → concept 1 / feature 1 |
| C6 | drift 테스트가 **단방향**(E2.4 namespace만 순회) | 테스트 코드 판독 | 양방향 테스트 추가 |
| C7 | `docs/` profile이 **이 실험 자신의 문서**까지 허용 | 경로 나열 | 자기언급 경로 denylist |
| C8 | `source_commit`이 주장만 되고 강제 안 됨 | 코드 판독 | `git cat-file -e` 실존 확인 테스트 |
| C9 | 유출 테스트가 어휘 스캔이라 C4를 **구조적으로** 탐지 불가 | 통과함에도 못 잡음을 리뷰어가 재현 | `MODEL_PAYLOAD_KEYS` 자체를 근거로 삼는 구조 가드 |
| C10 | evidence 순서가 시간순과 일치 | 순서 대조 | P2.1로 고정 순서 사전등록 |
| F7 | 잔여-금지 가드가 **영어 금지문을 통과**시킴 | 리뷰어 injection: `"Do not judge which source is more authoritative, newer, or still live; that judgment is already done and is outside your scope."` → **GUARD PASSED**. 운영 세션이 재현 확인 | 영어 tripwire 14종 + 대소문자 무관. 판정문 7개 명제를 parametrized로 **recall 7/7**, 깨끗한 template 통과로 **precision** 확인. 재주입 → `CAUGHT: EN tripwire 'authoritative'` |
| F11 | `h1a_schema.json` description이 폐기된 D-H1a-5=A를 서술 | 판정문 원문 대조 | 무엇이 무엇을 대체했는지 명시하도록 정정 |
| W1 | `EXPERIMENT_METHODOLOGY.md`가 "e2.* worktree 전부 포함"이라면서 그 worktree에서 **열리지 않음**. 브랜치 5/77 갈라짐 | `git log --all -- docs/EXPERIMENT_METHODOLOGY.md` → `c1b6af2`, `claude/ontoclean-…` 브랜치에만. `git rev-list --left-right --count` → 5/77 | main 5커밋 병합. 충돌 2건은 근거로 해소 — `HANDOFF.md`는 **ours**(함정 #1: 의도적으로 다른 문서), 로드맵은 **파일 안에 남아 있던 2026-07-25 지침**("병합 시 그쪽이 상위 서술이다")대로 theirs 기반 + ours의 E2.4 절 보존 |
| W2 | 이름 3층 불일치(dir/branch/work) + §4 "새 계열은 새 worktree" 위반 | `git worktree list` + `EXPERIMENT_METHODOLOGY.md` §4 원문 | `concept-gate-h1-wt` / `codex/h1-source-authority` 분리. 양쪽 HANDOFF 재조준. MOC 재생성(생성기가 새 worktree 자동 탐색) |

### 2.2 미해결 (8건)

**판정을 받았으나 아직 적용하지 않은 것 — 현재 실질 차단선**

| # | 문제 정의 | 검증 근거 | 상태 |
|---|---|---|---|
| **Q5** | `그 판정은 이미 끝났고 너의 범위가 아니다.`의 **선행사가 사라졌다.** E2.4에선 두 문장 앞 provenance 문장을 가리켰는데 Q3=B가 그것을 버렸다. 프롬프트에 남은 유일한 지시 대상이 payload 앵커라, **KEPT arm만** 모델에게 "앵커는 확정된 판정"이라고 읽히게 됨 = 조작이 만든 treatment×anchor 상호작용 | 렌더 후 실측: `E2.4 antecedent sentence present in H1a template? False`. KEPT 문단 verbatim 확인 | ❌ **미적용.** 판정 = **B**(세 번째 문장 제거, 조작을 2문장으로). Q5.1이 E2.4 선행사 복원을 **명시적으로 금지** |
| **Q6** | payload가 두 허용값 중 하나(`structural_composition`)를 **기록된 현재 상태로** 건네줌. 저장소의 실제 강제 상태이고, 하네스 자신이 반대 셀을 "counterfactual artifact"라 부름. `select_type`으로 가는 **무비용 경로** | 렌더된 payload에 `"type": "structural_composition"` 존재 확인. `no_oracle` 주장과 대조 | ❌ **미적용.** 판정 = **A**(앵커 제거). 파생: 20건 앵커 진단이 잴 대상 상실 |
| **Q7** | 충돌하지만 **충분한** 증거에서 `defer`의 의미가 정의돼 있지 않다. 프롬프트의 유일한 defer 경로가 "증거 부족"인데 이 fixture는 부족하지 않음 | 프롬프트 4불릿과 ev1·ev3 원문 대조 — 둘 다 지지 기준 충족 | ❌ **미적용.** 판정 = **E**(warrant 기반 정의. 충돌이라고 defer 강요 안 함, 직접증거 있다고 select 강요 안 함, tie-breaker 금지 목록 명시) |
| **Q8** | fixture가 **doc 2 대 code 1**인데 metadata는 1-vs-1 주장. code측 `주의:` 문장이 ev3에서 4줄 아래 존재하나 미포함 | `sed -n '1192,1198p' concept_gate_v7.py`로 누락 문장 확인, `phase_a_implementation_packet.md:106`(=ev2)과 구조 대조 | ❌ **미적용.** 판정 = **B**(ev2 제거해 진짜 1-vs-1). Q8.1: enum 밖 type 이름 노출 **불가** |

**위의 파생 — 적용 후에야 착수 가능**

| # | 내용 | 상태 |
|---|---|---|
| D1 | `_h1a_diag*` 4파일·47테스트 **은퇴**(Q6=A로 잴 대상 소멸) → 구조적 no-anchor 가드로 대체 | ❌ |
| D2 | **독립 리뷰 재실행** — 프롬프트·payload·fixture가 전부 바뀌므로 2차 리뷰는 무효가 됨 | ❌ |
| D3 | 동결 → 본 코호트 40 trial | ❌ (D2 통과 후) |

**선택 사항**

| # | 내용 | 상태 |
|---|---|---|
| O1 | E2.4 브랜치에서 H1a 파일 제거(현재 25파일 양쪽 중복) | ⬜ **선택.** vault `duplicate-register.md`가 "Exact-content duplicates are preserved for Git and worktree provenance. The first link in each group is the navigation canonical" — **예상된 상태로 이미 처리 중**(214 groups) |

### 2.3 고치지 않고 **한계로 기록**하기로 한 것 (2건)

2차 리뷰가 major로 지적했으나 blocker로 보지 않았고, 사전등록에 declared
limitation으로 남길 항목.

| # | 내용 | 왜 안 고치나 |
|---|---|---|
| L1 | evidence-reading rule 4불릿이 **전부 select 쪽에만** 작용 — 3개는 select에 비용 부과, 1개는 defer를 잔여값으로. defer엔 어떤 조건·임계·출력 의무도 없음 | arm-constant라 교란은 아님. 고치려면 프롬프트를 다시 저작해야 하고 그 자체가 새 조작 |
| L2 | 조작이 **언어 전환과 분리 불가** — 영어 본문에 한국어 3문장(108자) 삽입. 길이·언어 정합 placebo arm 없음 | 번역하면 그 번역 자체가 검토되지 않은 저작 행위. 원문 바이트 삽입이 덜 나쁜 선택 |

---

## 3. 이 분석의 한계

- **trial 0건 상태의 분석이다.** 실행 후 드러날 문제(코더 실패율, 전송 실패
  패턴, 응답 형식 붕괴)는 여기 없다
- **P1의 네 사례는 사후 재구성이다.** 발견 당시엔 각각 다른 문제로 보였고,
  같은 패턴이라는 인식은 세 번째(#3, 선행사) 이후에 생겼다
- **미해결 8건의 "해결 방법" 칸은 비어 있다** — 판정문이 지시한 방향은
  적었으나 구현되지 않았으므로, 그것이 실제로 문제를 푸는지는 **아직
  검증되지 않았다.** Q5~Q8 적용 후 독립 리뷰가 그것을 판정한다
- 워크스페이스 문제(W1·W2)는 오늘 해결됐으나 **다른 worktree·다른 실험
  계열에서 같은 형태가 재발할 수 있다.** §4 규약이 문서화돼 있어도 위반이
  누적됐던 것이 그 증거다
