# 지시서 — 모델-facing surface 구조 재설계

- 작성: 2026-07-28
- 작성 주체: 실험 운영 세션 (구현 권한 없음 — 이 문서는 **설계 권한자용 지시서**다)
- 대상: `evidence_packet_schema.json`, payload 생성 경로, `test_protocol.py`
- 성격: **설계급 변경 요청.** 스키마 필드 구조와 계약 표면을 바꾸므로 운영
  세션이 단독 실행하지 않는다.
- 근거 문서: `PROBLEM_2_conflicting.md`(오라클 유출 발견 경위),
  독립 리뷰 3회분(§7 부록에 검증 결과 요약)

---

## 1. 무엇이 문제인가 (한 문단)

`evidence_items[].extraction_note`와 `locator`는 **fixture 제작자가 자기
판단·근거·개정 이력을 쓰는 필드**인데, 동시에 **모델 payload에 그대로
실려 나간다.** 그 결과 제작자의 결론이 모델의 판정에 직접 개입한다. 이건
가설적 위험이 아니라 **E2.4의 4개 fixture 전부에서 실측된 사실**이며, 이
때문에 지금까지 얻은 **모든 CONTRACT_REPO 결과(7/7, 5/5, 5/5, 5/5)가
인증 불가 상태**다.

## 2. 실측된 유출 사례 (전부 직접 실행/grep으로 확인)

| fixture.item | 유출 텍스트 (모델-facing) | 누출 내용 |
|---|---|---|
| `conflicting.ev5` | "CONTRACT_REPO's **correct behavior is still to abstain** … the **expected contract_verdict is loosened to** 'abstain via insufficient_evidence, conflicting_evidence, or out_of_scope'" | 최종 decision + verdict 후보 집합 |
| `insufficient.ev4` | "audit **should classify** this as **indirect_context or ambiguous, never direct_support**" | `admissibility` 판정을 지시법으로 지정 |
| `sufficient_repairable.ev1` | "the evidence **supports structural_composition, not essential_feature**" | **repair 목표 type을 이름으로 직접 지정** |
| `sufficient_consistent.ev9` | "kept as **corroborating context, not sole support**" | `admissibility` 등급 사전 지정 |
| `sufficient_consistent.ev10` | "**Combined with ev9's** general definition … **this binds** the abstract type definition to this specific feature" | sufficiency 논증을 조립해 제공 |
| `sufficient_repairable.ev1.locator` | (300자) "…frozen and reused across two prior, unrelated experiments before this E2.4 fixture was built" | evidence의 신뢰도를 모델에게 변론 |

**중요**: `repairable.ev1`의 유출은 `conflicting.ev5`보다 **강하다** —
후자는 verdict를 3지선다로 좁혔을 뿐이지만 전자는 **목표 type을 확정
지정**한다. 따라서 "`conflicting`의 N=1은 유출이라 무효, 나머지 3개는
유효"라는 구분은 성립하지 않는다. 같은 기준을 적용하면 **현재 E2.4의
인증된 class는 3개가 아니라 0개**다.

## 3. 근본 원인 3층 — 왜 블랙리스트로는 못 막는가

### 3.1 스키마의 의도는 있었으나 강제된 적이 없다

- 패킷 스키마 자기 description: *"hidden oracle fields **must not** be
  included in model prompts"*
- `extraction_note` description: *"This note is **provenance, not
  independent evidence**"*
- `locator` description: *"**used only for** provenance"*

세 문장 다 올바른 의도를 명시한다. 그리고 **셋 다 지켜지지 않았다.**
description은 강제 장치가 아니다.

### 3.2 커밋된 payload 빌더가 존재하지 않는다 ← **가장 깊은 원인**

`ls`로 확인: `_gen_prompts.py` 없음, `_prompts.json` 없음(Phase 4 미실행).
지금까지 모든 스모크 payload는 **운영 세션이 프롬프트마다 손으로 구성**했고,
그 방식이
`{k: v for k, v in fixture.items() if k != 'run_pipeline_input'}`
— 즉 **블랙리스트 projection**이었다. 제외 목록에 없는 모든 필드가 자동으로
모델에 실린다. `extraction_note`는 한 번도 제외 대상이 아니었다.

**화이트리스트 projection을 committed·tested 코드가 수행했다면 이 유출은
구조적으로 불가능했다.** 이것이 이 지시서의 핵심 요구사항이다.

### 3.3 자연어 필드에 대한 금지어 목록은 열거 방어라 반드시 뚫린다

운영 세션이 유출 발견 직후 추가한 가드
(`test_model_facing_metadata_does_not_leak_the_oracle`)는 실행 검증 결과
**§2의 4개 라이브 유출을 전부 통과시키고, 작성 근거로 삼은 한 문장만
잡는다.** 원인: decision/`contract_verdict` enum만 금지하고
`admissibility` enum(`direct_support`/`indirect_context`/`ambiguous`)과
sufficiency 어휘를 빠뜨렸다.

독립 리뷰가 제안한 확장 목록(추가 enum + 지시법 modal + 실험 메타 + 상호
참조 + 길이 제한)은 실측 9개 프로브를 전부 잡지만, **여전히 블랙리스트**다.
다음번엔 다른 표현이 빠져나간다. 실제로 이 세션에서 같은 결함이
**서로 다른 위치에서 4회 재발**했다(자기인용 계열 포함).

→ **결론: 금지어를 늘리는 게 아니라, 자유서술 필드가 모델에 도달하는
경로 자체를 없애야 한다.**

## 4. 요구사항 (설계 권한자가 결정·구현할 것)

### R1. 필드를 청중(audience)으로 분리한다

`evidence_items[]`의 필드를 두 그룹으로 명확히 쪼갠다.

**(a) 모델-facing — 닫힌 집합, 기계적 값만**

| 필드 | 형태 | 비고 |
|---|---|---|
| `evidence_id` | string | 인용 식별자 |
| `source_path` | string | 저장소 상대 경로 (§5 Q1 참조) |
| `source_kind` | enum | 기존 유지 |
| `text` | string | 발췌 원문 (변경 없음) |
| `text_sha256` | string | 원문 무결성 |
| `locator` | **구조화 객체로 변경** | 자유서술 금지 — R2 |

**(b) 숨김(hidden) — 제작자용 자유서술, payload에 절대 포함되지 않음**

| 필드 | 용도 |
|---|---|
| `builder_note` (신규, `extraction_note` 대체) | 왜 이 항목을 넣었는지, C1~C4 검증 결과, 개정 이력, 리뷰 대응 — 지금 `extraction_note`에 쓰던 모든 것 |

핵심: 제작자가 쓰고 싶은 서술을 **없애는 게 아니라 옮기는 것**이다.
그 서술은 fixture 감사·재현·인수인계에 실제로 필요하다. 다만 모델이
봐서는 안 된다.

### R2. `locator`를 구조화한다

현재 자유 문자열이라 논증이 들어간다(§2 마지막 행). 판별 가능한 형태로:

```
locator: oneOf [
  { kind: "file_lines", path: str, start: int, end: int },
  { kind: "symbol",     path: str, symbol: str },
  { kind: "test",       path: str, test_id: str },
  { kind: "commit",     sha: str, part: "subject"|"body" },
  { kind: "json_path",  path: str, pointer: str }   # fixture 인용용
]
```

이렇게 하면 문장을 넣을 자리가 없다. 부수 이득: C4(precedence) 검증을
기계적으로 자동화할 수 있다.

### R3. payload 빌더를 committed·tested 화이트리스트로 만든다

- **단일 정본 함수**를 만든다 (예: `_payload.py::build_model_payload(fixture)`).
  스모크·qualification·본 실행·향후 `_gen_prompts.py`가 **전부 이 함수만**
  사용한다. 프롬프트에서 손으로 dict를 만드는 것을 금지한다.
- 구현은 **화이트리스트 projection**이어야 한다 — 허용 키를 명시 열거하고
  나머지는 전부 버린다. 새 필드가 스키마에 추가되면 **기본적으로 모델에
  보이지 않는 게 정상**이 되도록.
- 패킷 최상위도 동일 원칙 적용. 현재 `run_pipeline_input`만 제외되는데,
  `commit`·`extraction_policy`가 모델에 필요한지 재검토(§5 Q2).

### R4. 테스트를 3종으로 강제한다

1. **화이트리스트 불변식**: `build_model_payload()` 출력의 키 집합이 허용
   집합과 **정확히 일치**함을 assert. 부분집합이 아니라 동일성으로.
2. **양성 대조 코퍼스 커밋**: §2의 6개 실제 유출 문장 + 우회 프로브를
   파일로 커밋하고, "이 문장들이 `builder_note`에 있어도 payload에는
   나타나지 않는다"를 assert. 현재 가드의 음성 대조는 **손으로 한 번
   돌리고 보존하지 않았다** — 그래서 다음 편집이 조용히 약화시킬 수 있다.
3. **모델-facing 표면 해시**: `text_sha256`은 `text`만 고정한다. 화이트리스트
   전체의 정규 직렬화에 대한 해시(`model_facing_sha256` 등)를 추가해
   **모델이 실제로 본 것**을 provenance로 고정한다. 이게 있으면 결과
   재채점 시 "그때 모델이 뭘 봤는지"가 확정된다.

### R5. 기존 note를 마이그레이션한다

4개 fixture의 `extraction_note` 내용을 `builder_note`로 이동하되,
**삭제하지 말 것** — §2의 유출 문장들은 이 실험의 실패 이력 증거로서
가치가 있다. 이동 후 `PROBLEM_2` §2 표에서 참조 가능하게 유지한다.

동시에 **`conflicting.ev6.builder_note`의 사실관계 오류를 정정**할 것:
현재 "one commit later than ev5"라고 적혀 있으나 실제로는 **3커밋 뒤**다
(`ce3699a`, `d706152`가 사이에 있고, 그중 `ce3699a`는 ev5의 주장이 이미
NO_GO로 판정된 기록). 운영 세션이 넣은 오류이며, **동등강도 판단에 직접
영향을 주는 방향**이라 반드시 고쳐야 한다.

## 5. 설계 권한자가 결정해야 할 열린 질문

### Q1. 모델에게 `source_path`를 보여줄 것인가

- **보여주는 근거**: liveness/authority 판단의 재료. 경로 없이는 "이게
  라이브 코드인지 고립 문서인지" 추론 자체가 불가능하다.
- **가리는 근거**: `extraction_policy.disallowed_sources`가 이미
  "파일명/심볼명만으로 하는 추론"을 금지한다. 경로를 주면서 경로 기반
  추론을 금지하는 건 긴장 관계다. 실제로 어떤 trial이 경로를 근거의
  일부로 사용했는지 재검토 필요.

### Q2. liveness를 모델이 판단할 수 있게 할 것인가 — **가장 중요한 분기**

이게 R1을 그냥 적용하면 생기는 실질적 문제다. `sufficient_consistent.ev9`의
note는 *"Live @mcp.tool docstring (this repo's currently-registered
run_pipeline tool, re-confirmed 2026-07-27)"* 라고 알려줬다. 이걸 숨기면
**모델은 패킷만으로 liveness를 판단할 수단이 전혀 없다.**

두 갈래:

- **(i) liveness를 기계적 필드로 제공한다** — 예:
  `consulted_by: ["conceptgate/concept_gate_v7.py:350"]`,
  `verified_by_passing_test: ["test_semantic_regressions.py::test_r6"]`.
  검증 가능한 구조화 주장이므로 자유서술이 아니다. 모델이 liveness를
  판정 재료로 쓸 수 있게 된다.
- **(ii) liveness를 모델 판정 범위에서 제외한다** — fixture 제작자가
  C1(liveness)을 오프라인에서 확인하는 책임을 지고, 모델은 "주어진
  텍스트가 이 feature의 온톨로지적 성격을 서술하는가"만 판정한다.
  계약(`contract_prompt.md`)에서 liveness 관련 기대를 제거해야 한다.

**어느 쪽이든 계약 문구 수정이 따라온다.** 현재는 모델에게 liveness를
기대하면서 판단 재료를 자유서술로 주고 있어 최악의 조합이다.

### Q3. 기존 결과 17 trial을 재실행할 것인가

- 재실행 대상: `sufficient_consistent` 7, `sufficient_repairable` 5,
  `insufficient` 5.
- 독립 리뷰 예상: evidence 본문 자체는 건전하므로(인스턴스 결박된
  실제 동결 텍스트) **세 class 모두 재현될 것**. 즉 재설계가 아니라
  17 trial 재실행 비용.
- 대안: 기존 결과를 "유출 상태에서 얻음"으로 명시 보존하고 재실행하지
  않는다 → 다만 그러면 E2.4의 인증 class는 0개로 남는다.

### Q4. `conflicting` class 처리 (이미 결정됨 — 확인만)

사용자 결정 기록: "현 저장소의 live·동등강도 evidence로 구성 가능한
fixture 미확보"로 표시, 유효 커버리지 3 class 보고, **schema class는
유지**, stale 문서 대 live 코드는 `source_authority_unresolved` 계열
별도 실험으로 분리. → 이 지시서는 그 결정을 변경하지 않는다. 다만 Q3의
결과에 따라 "유효 커버리지 3"이 "0"이 될 수 있으므로 **표기가 Q3에
종속**된다는 점만 명시한다.

## 6. 범위 밖 (별도로 처리)

1. **`contract_prompt.md` 규칙 3의 `conflicting` 정의 명확화** —
   `semantic_constraints`는 "conflicting direct evidence **of equal
   strength**"를 요구하나 규칙 3 본문은 그만큼 못박지 않아 N=5에서 1/5가
   "사실 충돌"로 읽었다. 별도 설계 사안(단, Q2의 계약 수정과 같은
   커밋에서 처리하면 효율적).
2. **Phase 5 커버리지 재설계** — `conflicting` 제외로 arm 비교의 최고 신호
   셀이 사라졌고, 그 셀에서 나온 유일한 arm 비교 관측도 유출 packet에서
   얻은 것이라 재현 대상이다.
3. **`conceptgate/` 라이브 버그 2건** — 이 실험은 `conceptgate/`를
   read-only로 취급하므로 별도 이슈로 제기:
   - `has_part`/`part_of`가 `RELATION_HINT_TYPE`에 없어
     `relation_discrimination_gate`가 `essential_feature`+`has_part`를
     is-a DAG에 통과시킨다(리뷰가 실행 증거 제시). 반면
     `docs/MCP_SERVER.md`와 `server.py`의 클라이언트 가이드는 반대로 안내.
   - `cg_partwhole.py:7-8`의 stale docstring("참조용 — 직접 import하지
     않음")이 아직 그대로다. 이 문장이 이번 세션에 잘못된 "죽은 코드"
     판정을 만들었고 lesson은 정정됐으나 **코드 주석은 안 고쳐졌다** —
     다음 fixture 제작자에게 같은 함정이 장전된 상태.
4. **프로세스 결함 2건** (운영 세션이 수정 가능하나 이 지시서와 별개):
   - 루트 `python3 -m pytest -q`(CLAUDE.md 게이트 1번)가 **collection에서
     중단**된다(3 errors) — `test_protocol.py`가 여러 실험 폴더에 동명으로
     있는데 `pytest.ini`에 `--import-mode=importlib`도 `norecursedirs`도
     없다. 즉 R4의 테스트를 추가해도 **디렉터리로 `cd`해야만 실행된다.**
   - E2.4에만 `trials.json`이 없다. 모든 결과가 산문 표로만 존재해
     오라클 변경 시 재채점이 불가능하다 — **이번에 실제로 그 상황이
     발생했다.** R4-3의 표면 해시와 함께 정비 필요.

## 7. 부록 — 이 지시서의 사실 근거 검증 상태

이 문서의 모든 주장은 운영 세션이 **직접 실행/grep으로 확인**했다. 독립
리뷰가 제기한 주장을 액면 그대로 인용하지 않고 재검증한 결과:

| 주장 | 검증 방법 | 결과 |
|---|---|---|
| 나머지 3개 fixture도 유출 | 4개 fixture note를 문구별 grep | **참** (§2 표) |
| 현재 가드가 그 유출을 못 잡음 | 가드 로직을 4개 문장에 직접 실행 | **참** — 4/4 통과(evade), 제거된 문장만 검출 |
| `ev6` note의 "one commit later"가 거짓 | `git log 4017aff..559f61f` | **참** — 3커밋(`ce3699a`, `d706152`, `559f61f`) |
| 문서-코드 후보가 "수정된 채로 라이브에 존재" | `concept_gate_v7.py:1188-1196` 직접 확인 | **참** — `:1192`가 "철은 칼의 재료 → **structural_composition** (재료가 본질적이어도 관계는 has-a)" |
| 루트 pytest가 collection 중단 | `python3 -m pytest -q` 실행 | **참** — 3 errors, Interrupted |
| 커밋된 payload 빌더 없음 | 실험 폴더 `ls` | **참** — `_gen_prompts.py`/`_prompts.json` 부재 |

미검증으로 남긴 것: 리뷰가 제시한 `has_part` 관련 실행 증거와
`relational_scaling`/`locational`/`contextual_usage` 긴장 사례들은 §6-3의
별도 이슈로 넘겼고 이 지시서의 논거로 사용하지 않았다.
