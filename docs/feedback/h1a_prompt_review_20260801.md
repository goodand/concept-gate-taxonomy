# H1a 프롬프트 표면 독립 리뷰 (2026-08-01) — **동결·실행 부적합**

- 리뷰어: 별도 에이전트. **제작자의 결론·우려를 알려주지 않았고**, 제작자
  테스트를 증거로 받지 말고 직접 재현하라고 지시함
- 대상: Q3=B 판정을 반영해 재작성한 `_h1a_contract.py`의 렌더링 결과 전체
- 판정: **blocker 2 + major 7 + minor 4 + clean 3.** "as-is로 동결·실행하지
  않겠다"
- 실행된 trial: **0건**(이 리뷰가 첫 실행 직전에 들어왔다)

---

## 0. 운영 세션이 직접 재확인한 것

리뷰 결과를 그대로 받지 않고 4건을 독립 재현했다. **전부 사실로 확인됐다.**

### B1 — "그 판정"의 선행사가 사라졌다 (blocker)

```
python3 -c "... render KEPT ..."
E2.4 antecedent sentence present in H1a template? False
```

렌더된 KEPT 문단(verbatim):

```
… codebase memory, prior conversation context, or external sources.
모델은 출처의 liveness나 우선순위를 재판정하지 않는다. 어떤 출처가 더
최신인지, 더 권위 있는지, 아직 살아있는 코드인지를 추론하지 마라.
그 판정은 이미 끝났고 너의 범위가 아니다.
```

E2.4에서 "**그 판정**"은 두 문장 앞의 `이 packet의 evidence item은 실행 전
provenance/eligibility 검증을 통과했다`를 가리켰다. **Q3=B가 그 서문을
버렸으므로 H1a에는 선행사가 없다.** 프롬프트 안에서 "이미 끝난 판정"으로
읽힐 수 있는 유일한 대상은 payload의 `"type": "structural_composition"`뿐이다.

→ **KEPT arm만 모델에게 "앵커는 이미 확정된 판정"이라고 읽히게 만든다.**
앵커는 arm-constant지만 그 **해석**은 arm-constant가 아니다. 조작 자체가
treatment×anchor 상호작용을 만들어낸 것이고, 이것은 Q2 진단이 배제하려던
바로 그 상태다.

### B2 — payload가 두 후보 type 중 하나를 건네준다 (blocker)

```
"candidate_concepts": [{"name": "칼", "features":
  [{"feature": "철", "type": "structural_composition", "evidence_refs": [...]}]
```

`builder_metadata.no_oracle`은 "Neither type is marked right"라고 적혀 있으나,
두 허용값 중 하나가 **저장소의 실제 강제 상태**로서 모델에게 전달된다.
`_h1a_diag.py` 자신이 반대 셀을 "counterfactual artifact"라고 부른다. 즉
어느 쪽이 비반사실인지 하네스가 알고 있고, 그것을 모델에게 준다.
`select_type`으로 가는 **무비용 경로**(앵커를 그대로 반복)가 생긴다.

### F7 — 잔여 금지 가드가 영어 금지문을 통과시킨다 (major, 제작자 결함)

```
injected: "Do not judge which source is more authoritative, newer, or still
           live; that judgment is already done and is outside your scope."
→ GUARD PASSED IT.  LEAKED
```

`RESIDUAL_TRIPWIRES`는 한국어 토큰 8개뿐이다. **Q3=B로 template이 영어가 된
뒤에도 가드는 한국어만 본다.** manipulation-scope 판정 요구사항 7은 영어 명제
7개를 명시적으로 나열하며 "guard must fail the removed arm if it contains a
model-facing instruction equivalent to" 라고 요구했는데, 구현하지 않았다.
template이 **수기 편집 가능한 markdown 판정문에서 로드**되므로 이 구멍은
가설이 아니라 실재한다 — 거기 추가된 금지는 **양 arm에 모두** 들어가 arm-diff
테스트로는 안 잡히고, 잡을 수 있는 유일한 장치가 이 가드였다.

### F5 — fixture가 2-vs-1인데 1-vs-1이라고 주장한다 (major)

| 측 | 주의 문장 | fixture 반영 |
|---|---|---|
| doc `phase_a_implementation_packet.md:106` | `주의: 재료-대상(4)만 essential_feature가 될 수 있습니다.` | **ev2로 실림** |
| code `concept_gate_v7.py:1196-1197` | `주의: (1)~(4)는 structural_composition, … essential_feature는 'X는 Y의 일종'(is-a)에만.` | **누락** |

ev3(`:1192-1193`)에서 **4줄 아래**에 있는, ev2의 구조적 쌍둥이다.
`builder_metadata`는 "This is a 1-vs-1 conflict"라고 적고 있으나 모델이 보는
것은 doc 2건 대 code 1건이다. 항목 수가 많은 쪽이 우세해 보이면 그 자체가
`select_type` 방향 압력이고, evidence를 고정하는 앵커 진단으로는 안 잡힌다.

### F10 — 확인 결과 **해당 없음**(리뷰어가 PARTIAL로 표시한 항목)

리뷰 시점에 agent 정의가 없어 PARTIAL이었다. 이후 만든 `h1a-decider.md`는
스키마를 **임베드하지 않고 프롬프트의 것을 가리킨다**. 실측:

```
"neither value is scored as correct"                  in prompt: False / in agent: False
"the two types the fixture's sources actually …"      in prompt: False / in agent: False
"NEVER a coding input"                                in prompt: False / in agent: False
```

→ 스키마 파일의 description 유출 경로는 **닫혀 있다.** 다만 리뷰어의 권고
(테스트로 고정하라)는 유효하므로 회귀 테스트를 남길 것.

---

## 1. 분류 — 무엇이 설계 판정이고 무엇이 운영 세션 몫인가

### [DESIGN] 외부 판정 필요 — 운영 세션이 정하지 않는다

| # | 항목 | 왜 운영 세션이 못 정하나 |
|---|---|---|
| B1 | "그 판정" 선행사 소실 | 해법 두 가지가 다 상위 판정을 건드린다 — E2.4 provenance 문장을 **양 arm에** 되살리면 Q3=B가 버린 서문을 부분 복원하는 것이고, 세 번째 문장을 조작에서 빼면 **Q1이 동결한 절 바이트**를 바꾸는 것이다 |
| B2 | 앵커가 답을 건넴 | Q2 판정이 "앵커 제거"를 **진단 발동 시의 재설계안**으로 열거했다. 그것을 진단 **전에** 선취하는 것은 Q2가 정한 절차를 바꾸는 일 |
| F4 | 충돌하지만 충분한 증거에서 `defer`의 의미 미정의 | Q3=B가 규칙 3의 동률 조항을 제거하면서 **대체 규칙을 두지 않았다.** 지금 프롬프트에는 "증거가 부족하면 defer"만 있고, 이 fixture는 부족하지 않다. 무엇을 넣을지는 곧 연구 질문을 정하는 일 |
| F5 | 2-vs-1 비대칭 | code측 주의를 **추가**(2-vs-2)할지 ev2를 **제거**(1-vs-1)할지가 조작 설계 선택 |

### [FIX] 운영 세션이 처리 가능

| # | 항목 | 조치 |
|---|---|---|
| F7 | 가드가 영어 금지문 미탐지 | manipulation-scope 요구사항 7의 영어 명제 7종을 tripwire에 추가. **이미 구속력 있던 요구사항의 미구현이라 새 판단 없음** |
| F11 | `h1a_schema.json:3`이 폐기된 D-H1a-5=A를 서술 | 텍스트 정정. 이 파일은 `DESIGN_FILES`라 동결 대상 — 틀린 서술을 동결하면 기록이 자기모순 |
| F9 | 동결 산출물 부재 + 절 manifest 부재 | 커밋 승인 후 처리. 단 절 ID `L8`/`L24_25`는 **H1a가 더 이상 쓰지 않는 E2.4 행번호**라 H1a template 기준으로 재부여 필요 |
| F10 | 스키마 description 유출 | **이미 닫힘**(위 실측). 회귀 테스트만 추가 |
| F13 | 문구 비대칭(`you defer` vs 증거가 선택) | 저비용 정정, 단 template은 판정문 소유라 [DESIGN]과 함께 처리 |

### [DECLARE] 고치지 않되 사전등록에 한계로 명시

| # | 항목 |
|---|---|
| F3 | evidence-reading rule 4개 불릿이 **전부 select 쪽에만** 작용(3개는 비용 부과, 1개는 defer를 잔여값으로). arm-constant라 교란은 아니나 DV 차원의 프롬프트발 압력 |
| F8 | 조작이 **언어 전환과 분리 불가** — 영어 본문에 한국어 3문장(108자) 삽입. 길이·언어 정합 placebo arm이 없어 "절의 의미" 대 "한국어 문단 출현"을 분리할 수 없음 |

### [CLEAN] 리뷰가 문제없음으로 확인 (3건)

- 두 arm의 렌더 차이가 **바이트 수준에서 정확히 liveness 절뿐**(리뷰어가
  공통 prefix 259자·suffix 1879자를 독립 계산). 단 이것은 **중립성을
  보증하지 않는다** — B1·F3가 그 증거다
- payload whitelist가 oracle 필드를 전부 배제(`server_response`,
  `builder_metadata`, `source_ref`, `text_sha256`, eligibility profile 부재).
  field-by-field 구성이라 나중에 추가된 필드가 기본 노출되지 않음
- template을 판정문 파일에서 **로드**(재입력 안 함), drift 시 loud하게 실패

리뷰어 주석: "18개 테스트의 명제를 독립적으로 재도출했고 각각 성립한다.
**단 그중 어느 것도 finding 1~6에 닿지 않는다** — 그게 이 작업의 요점이다."

---

## 2. 이 리뷰가 드러낸 방법론적 패턴

**같은 함정에 다른 형태로 또 걸렸다.** 제 테스트는 "diff가 정확히 그 절인가"를
검사했고 그건 **참**이다(리뷰어도 독립 확인). 그러나 필요한 명제는 "그 절이
**옮겨진 자리에서도 같은 것을 의미하는가**"였다. 바이트는 정확히 이동했는데
의미는 이동하지 않았다 — 선행사를 두고 왔기 때문이다.

이것은 `adversarial-verification-probe` 패턴 10(가드가 주장하는 명제를
읽어라)의 **새 변종**이다. 기존 사례는 "diff 검사가 남은 것에 대해 말하지
않는다"였고, 이번은 **"바이트 동일성 검사가 문맥 의존 의미에 대해 말하지
않는다"**다. 텍스트를 다른 문서로 이식할 때 대명사·지시어·후방조응이
선행사를 잃는지는 바이트 비교로 원리상 검출 불가능하다.

승격 후보(1회 관측이므로 아직 승격 안 함): **이식된 절의 조응 검사** —
절을 새 문맥으로 옮길 때 그 절의 지시 표현("그 판정", "위 규칙", "this")이
새 문맥에서 무엇을 가리키는지 명시적으로 적어 원래 지시 대상과 비교하라.
