# H1a fixture — 독립 리뷰 (2026-07-30)

- 리뷰어: 별도 에이전트(general-purpose), **제작자와 분리**
- 대상: `experiments/2026-07-29_h1a_source_authority_unresolved/`의 fixture,
  surface 사본, 테스트, PREREGISTRATION, README
- 방침: 제작자의 테스트를 증거로 받지 않고 **직접 재현**하도록 지시
- **판정: 동결 부적합 (not fit to freeze and run)**
- 규모: blocker 1 / major 5 / minor 6 / confirmed-clean 6

> 1차 시도(2026-07-30 오전)는 API 세션 한도로 파일을 읽기 전에 중단됐다.
> 소견 0건이었고 전송 실패였다(P4 범주). 아래는 한도 리셋 후 재실행 결과다.

---

## 0. 운영 세션이 직접 재확인한 것

리뷰를 그대로 받지 않고 두 건을 독립 검증했다. **둘 다 사실이었다.**

### BLOCKER #16 — 금지 문장이 두 곳에 있다

```bash
sed -n '23,26p;40,43p' experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/contract_prompt.md
```

```
이 packet의 evidence item은 실행 전 provenance/eligibility 검증을
통과했다. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.      ← §4.1 삭제 대상

   - evidence_items에 없는 정보가 필요하면 abstain해야 한다.
   - 어떤 출처가 더 최신인지, 더 권위 있는지, 아직 살아있는 코드인지를
     추론하지 마라. 그 판정은 이미 끝났고 너의 범위가 아니다.          ← 그대로 남음
```

후자가 **더 명시적**이다. 서문만 지운 `PROHIBITION_REMOVED` arm은 연구 대상
행동을 여전히 금지한다 → **조작 무효**. 게다가 README §4.1이 규정한
byte-level diff 테스트는 **통과한다** — 그 테스트는 "diff가 그 한 문장인가"를
보지 "동등한 금지가 남았는가"를 보지 않는다.

**이 텍스트는 제작 세션의 컨텍스트에 이미 들어 있었다**(H3 dispatcher 작업 중
`contract_prompt.md` 전문을 읽었다). 그럼에도 못 봤다. 독립 리뷰가 존재하는
이유가 정확히 이것이다.

### #8 — 더 나은 code-side 증거가 있었다

```bash
sed -n '1190,1195p' conceptgate/concept_gate_v7.py
```

```
        "(4) 재료-대상: 철은 칼의 재료 → structural_composition "
        "(재료가 본질적이어도 관계는 has-a — 본질성은 별도 축)\n"
```

`docs/phase_a_implementation_packet.md:102`가
`(4) 재료-대상: 철은 칼의 재료 → essential_feature (재료는 본질이 될 수 있음)`
이므로, 이 둘은 **문장 줄기가 동일하고 type만 반대**다. live 패키지 코드이고
칼·철을 둘 다 명명한다. 이것이 자연스러운 ev3였다. 제작자는 대신 칼도 철도
없는 일반 dict 항목(`cg_partwhole.py:36`)을 썼다.

---

## 1. Blocker

| # | 기준 | 판정 | 심각도 |
|---|---|---|---|
| 16 | C7 | **REFUTED** | **blocker** |

**주장**: README §4.1 — 두 arm은 정확히 그 한 문장으로만 다르며 byte-level
diff 테스트가 이를 고정한다.

**근거**: `contract_prompt.md`의 서문(24-25행)과 절대 규칙 1(41-42행) 양쪽에
liveness/권위 재판정 금지가 존재한다. §4.1은 전자만 삭제한다.

**함의**: 조작이 무효화되고, 규정된 diff 테스트는 그 사실을 잡지 못한다.
추가로 41-42행 자체가 양 arm에 남는 liveness 힌트이므로, 상수로 유지하려면
그 사실이 문서에 명시돼야 하는데 어느 문서에도 없다.

---

## 2. Major

### #7 (C2, REFUTED) — 충돌이 비대칭이다
model-facing 텍스트 기준: ev3(`cg_partwhole.py:36`)는 칼도 철도 포함하지
않는 일반 dict 항목. ev4는 철만 포함하고 칼이 없다. doc측 ev1만 둘 다
명명한다. **code측의 칼 결박은 출처가 아니라 하네스(`candidate_concepts`)가
공급한 것.** 제작자 테스트도 이 비대칭을 스스로 인정한다
(`test_h1a_fixture.py:148-149` — ev1에는 CONCEPT·FEATURE 둘 다,
ev4에는 FEATURE만 단언).

### #8 (C2, REFUTED) — 더 나은 증거가 있었다
위 §0 참조. 부재 사유가 README·PREREGISTRATION·builder_metadata 어디에도
설명돼 있지 않다.

### #10 (C3, PARTIAL) — 2-vs-2가 아니라 1-vs-1이다
`git log --diff-filter=A --follow -- test_semantic_regressions.py` → ev3를
바꾼 것과 **같은 커밋**. 커밋 메시지가 "material_of remapped ... 8 golden
tests pin all of the above"라 밝히고, 테스트 파일 헤더도 목적이 그 수정을
고정하는 것이라 명시한다. **ev4는 ev3를 pin하려고 존재한다 — 두 파일에
걸친 하나의 저작 행위.** ev1/ev2도 같은 fenced block 4줄 간격의 한 저작
행위다. 그런데 code측만 `source_kind` 2종(code, test)을 갖고 doc측은 1종이다.

### #11 (C1, REFUTED) — payload가 답을 announce한다
`builder_metadata.liveness_is_harness_only`는 "모델은 evidence_id /
source_kind / text만 받는다"고 주장하나, payload에는 다른 두 키가 더 있다.

- `candidate_concepts[0].features[1].type = "structural_composition"` (code측 답)
- `server_response.status = "PASS"` (그 기록을 인증)

**실행 반사실**(리뷰어가 `_cert_core.run_and_certify`로 직접 실행):

| 기록된 type | relation_hint | 결과 |
|---|---|---|
| `structural_composition` | material_of | **PASS** |
| `essential_feature` | material_of | **NEEDS_CORRECTION** |
| `essential_feature` | 없음 | PASS |

즉 payload는 기계 목소리로 "code측 답이 현재 기록돼 있고, 그 기록이 깨끗하게
인증된다"고 말한다 — doc측 답으로는 나올 수 없었던 판정이다. "stale"이라는
단어는 없지만 **어느 출처가 유효한지**라는 같은 정보다.

### #14 (C5, REFUTED) — 앵커 방어 논증이 불완전하다
`builder_metadata.recorded_type_rationale`의 "양 arm이 동일 fixture를 받으므로
교란하지 않는다"는 **교란(confounding)에 대해서만** 참이다. 상수는 covary하지
않지만 **처치와 상호작용**할 수 있다. 앵커 + `PASS` + `material_of →
structural_composition` 폐쇄 유도가 전부 같은 방향을 가리키므로, 이 스택이 양
arm에서 `select_type/structural_composition`을 천장까지 밀면 관측되는 arm
차이는 ≈0이 된다.

`PREREGISTRATION` §0은 "다르지 않았다"를 허용 결론으로 명시했고, P7.2는 사후
조정을 금지하며, K=1 고정이라 **앵커를 뒤집은 대조 fixture가 구조적으로
불가능**하다 → **ceiling-null과 진짜 null이 사후 구별 불가.**

### #15 (C7, REFUTED) — 어느 feature를 판정하는지 명시가 없다
`candidate_concepts[0]`에 feature가 둘이다: `도구`(essential_feature, 근거 0)와
`철`(structural_composition, 근거 4). `h1a_schema.json`의 `selected_type`은
`[essential_feature, structural_composition]`인데 **`도구`의 type이 그중
하나**다. 따라서 `select_type/essential_feature` 응답은 "철에 대해 doc측이
이겼다"인지 "도구를 보고했다"인지 **판별 불가**다. 코더는 설계상 구조만 읽고
(P5.1) rationale을 볼 수 없어 사후 해소도 금지돼 있다.

---

## 3. Minor

| # | 기준 | 내용 |
|---|---|---|
| 2 | C6 | 제작자의 drift 테스트가 **단방향** — E2.4 namespace만 순회해 H1a 쪽 **추가**를 못 잡음. `_eligibility_profile`은 통째로 면제라 그 안의 추가 편집도 미검사 |
| 3 | C6 | `docs/` profile이 이 실험 자신의 문서까지 `repository_prose`로 허용 (`docs/HANDOFF.md`, `docs/E2.4_ISSUE_REGISTER.md`, `docs/feedback/h1a_*` — 전부 이 충돌을 논평하는 문서). E2.4의 docs/ 거부가 우연히 제공하던 C3 가드가 사라짐 |
| 6 | C4 | `source_commit`이 manifest에 복사되지만 HEAD와 대조되지 않음(E2.4에서 상속). 오늘은 무해(639c991과 HEAD에서 4줄 동일 확인) |
| 9 | C2 | ev2도 인스턴스 주장이 아닌 일반 규칙 — README가 "보강"이라 표기해 은폐는 아님 |
| 12 | C1 | 유출 테스트가 어휘 substring 스캔이라 #11을 **구조적으로** 탐지 불가. 가드 자체는 정상 작동하나 "봉쇄 증명"으로 과대 해석됨 |
| 13 | C1 | evidence 순서(doc→code)가 시간순과 일치. 약하지만 무상으로 통제 가능한 자유변수 |
| 17 | C7 | `도구`는 근거 0인 typed feature — arm 무관하게 `defer`할 독립적 이유를 제공해 종속변수에 잡음 추가, #15를 가중 |

---

## 4. CONFIRMED — 문제없음으로 확인된 것

| # | 내용 |
|---|---|
| 1 | surface 사본이 E2.4 원본과 **3개 hunk 외 바이트 동일**(docstring + 프로파일 1줄 + 분기 2줄). 리뷰어가 `diff -u`로 독립 확인 |
| 4 | 인용 4건 전부 `source_commit`과 HEAD **양쪽에서** 바이트 일치, `text_sha256` 4/4 검증, R6b 실제 실행 통과, `test_h1a_fixture.py` 19 passed |
| 5 | README §3의 provenance 서사가 `git log`로 성립 — doc 본문 `4e0214c`(07-05), code 수정 `8c4cd34`(07-12), `cf58c8c`(07-14)는 배너만 추가하고 102·106행 미변경 |
| 10(전반) | 이 실험을 위해 저작된 evidence 없음(4건 전부 H1a 시작 전), E2.4 fixture 텍스트 재사용 없음 |
| 18 | 교차측 비순환성 성립 — ev1과 ev3/ev4가 표현을 공유하지 않음 |
| — | 코더가 `rationale`을 읽지 않음(P5 요구 충족) |

---

## 5. 리뷰어가 가장 확신하지 못한다고 밝힌 것

> #11/#14가 치명적인지 문서화된 한계에 불과한지. 앵커가 권위 신호이고
> arm 무관임은 증명했으나 **trial을 한 건도 돌리지 않았으므로** 실제로
> 천장을 치는지는 모른다. 문제는 위험이 입증됐다는 것이 아니라, 동결된
> 설계에 **사후에 두 경우를 구별할 계측기가 없다**는 것이다(K=1, 대조
> 앵커 없음, P7이 사후 조정 금지).
>
> 제안: 동결 **전에** 앵커를 뒤집은 변종으로 소수 off-protocol trial을
> 돌려 버리고(코호트 미병합) 천장 여부만 확인하는 값싼 probe.

---

## 6. 대응

- **A군(기계적)** — 운영 세션이 처리: ev3 교체, ev4·`도구` 제거,
  payload에서 `server_response` 제거, drift 테스트 양방향화, `docs/`
  자기언급 가드, `source_commit` 강제
- **B군(설계 판정)** — 외부 설계 담당: Q1 조작 범위(blocker #16),
  Q2 ceiling-null 식별가능성(#14) → `DESIGN_REQUEST_H1a_manipulation_scope.md`
- **동결·실행은 Q1 판정 이후.** A군만으로는 blocker가 풀리지 않는다
