# 설계 결정 (동결) — 세 표면 분리와 검증 경계 이동

- 결정일: 2026-07-28
- 결정 주체: 실험 설계 권한 (외부), 사용자 경유 전달
- 상태: **동결.** 이 문서는 결정 기록이다. 결과가 이 결정을 소급 수정하지
  못한다. 변경이 필요하면 새 amendment 문서로 남긴다.
- 요청 문서: [`DIRECTIVE_model_facing_surface_redesign.md`](DIRECTIVE_model_facing_surface_redesign.md) (`4a14fdd`)
- 핵심: 단순한 필드 삭제가 아니라, **제작용 fixture와 모델 입력을 서로 다른
  스키마·경로로 분리**하고, **liveness 검증 책임을 모델 경계 밖으로 이동**한다.

---

## 0. 지시서 질문에 대한 결정

| 질문 | 결정 |
|---|---|
| Q1 `source_path` 노출 | **모델에는 숨김** |
| Q2 liveness 판단 | **모델 범위에서 제외.** 실행 전 qualification gate가 검증 |
| Q3 기존 17 trials | **새 표면 동결 후 전부 clean rerun** |
| Q4 `conflicting` | schema에는 유지, E2.4에서는 **미검증 class로 표시** |
| 현재 인증 상태 | **0 class** |
| 금지어 가드 | **보조 진단으로만 유지. 보안 경계로 사용 금지** |

`source_path`·`locator`·`text_sha256`은 모델이 의미 판정에 쓸 필요가 없다.
모델은 `evidence_id`로 인용하면 되고, provenance 검증은 실행 전에 기계가 한다.

## 1. 세 개의 명시적 표면

### A. 제작용 fixture (저장소에 커밋되는 전체 기록)

```json
{
  "fixture_version": "repo_evidence_fixture_v2",
  "experiment_id": "E2.4",
  "repo": "goodand/concept-gate-taxonomy",
  "source_commit": "<full sha>",
  "run_pipeline_input": [],
  "candidate_concepts": [],
  "evidence_sources": [],
  "server_response": {},
  "builder_metadata": {}
}
```

`evidence_sources[]` 항목:

```json
{
  "evidence_id": "ev10",
  "source_kind": "fixture",
  "source_ref": {
    "kind": "json_pointer",
    "path": "experiments/.../fixture.json",
    "pointer": "/fixtures/0/input_concepts/0/features/0/evidence"
  },
  "text": "카페린의 손잡이는 카페린 몸체의 구성 부분이다",
  "text_sha256": "..."
}
```

**제작자 자유서술은 evidence item 안에 두지 않는다.** `builder_note`를
`evidence_sources[]`의 형제 필드로도 두지 않는다 — 물리적으로 떨어뜨려
잘못된 직렬화 가능성을 줄인다:

```json
{
  "builder_metadata": {
    "evidence_notes": { "ev10": "선정 이유, 독립성 검토, 리뷰 이력..." },
    "change_history": []
  }
}
```

### B. qualification manifest (실행 전 생성, 비모델 표면)

```json
{
  "qualification_version": "e2.4-source-qualification-v1",
  "fixture_sha256": "...",
  "source_commit": "...",
  "status": "passed",
  "evidence_checks": [
    {
      "evidence_id": "ev10",
      "locator_resolved": true,
      "excerpt_exact_match": true,
      "text_sha256_verified": true,
      "eligibility_profile": "frozen_experiment_artifact",
      "verification_refs": []
    }
  ]
}
```

`eligibility_profile`은 **닫힌 enum**:

- `current_executable_source`
- `verified_by_passing_test`
- `frozen_experiment_artifact`
- `historical_commit_record` — **존재와 원문만 검증하며 현재 권위를 의미하지
  않는다**

`build_model_payload()`는 fixture만 받아서는 안 된다. **fixture hash와
일치하는 `status=passed` qualification manifest가 있어야 동작한다.**

### C. 모델 payload (모델이 보는 전부)

```json
{
  "candidate_concepts": [],
  "evidence_items": [
    { "evidence_id": "ev10", "source_kind": "fixture", "text": "..." }
  ],
  "server_response": {}
}
```

**모델에게 보내지 않는 것**: `record_class`, `repo`, `source_commit`,
`run_pipeline_input`, `source_path`, `source_ref`/`locator`, `text_sha256`,
`builder_metadata`, qualification 결과, fixture class/oracle, 자유서술형
`extraction_policy`.

출처 제한 정책은 **fixture 데이터가 아니라 동결된 `contract_prompt.md`**에
둔다.

## 2. `source_ref` tagged union

`source_path + locator` 문자열 조합을 하나의 tagged union으로 교체한다.

| kind | 필드 |
|---|---|
| `file_lines` | `path`, `start_line`, `end_line` |
| `symbol` | `path`, `symbol` |
| `test` | `path`, `node_id` |
| `commit` | `sha`, `part` |
| `json_pointer` | `path`, `pointer` |

모든 variant 공통 제약:

- `additionalProperties: false`
- `path`는 저장소 상대 경로만
- commit SHA는 **40자리 full SHA**
- `start_line <= end_line`
- `pointer`는 JSON Pointer 문법
- **설명·비고·note 필드 금지** (문장이 들어갈 자리를 없앤다)

## 3. canonical builder — 유일 허용 경로

```
fixture
  → validate_fixture()
  → qualify_fixture()
  → build_model_payload()
  → render_prompt()
  → write_prompt_manifest()
  → execute_trial()
```

```python
qualify_fixture(fixture, repo_checkout) -> QualificationManifest
build_model_payload(fixture, qualification_manifest) -> ModelPayload
render_prompt(contract_prompt, model_payload) -> str
```

- `build_model_payload()`는 **명시적 화이트리스트 projection만** 수행한다.
  입력을 복사한 뒤 제거하는 blacklist 방식은 **금지**.
- 스모크·qualification·본 실행·재실행 **전부** `render_prompt()`를 거친다.
  **수동 payload 구성 불허.**

## 4. liveness — 모델에게 판단시키지 않는다

이유:

1. `consulted_by`, `verified_by_passing_test`를 모델에게 보여줘도 **모델은
   그것이 참인지 검증할 수 없다.**
2. 검증 완료된 구조화 정보를 다시 모델에게 주면 **source authority를
   암시하는 또 다른 oracle**이 된다.
3. E2.4의 평가 목표는 "주어진 텍스트가 해당 instance/type을 직접 지지하는가"
   이지 **저장소 call graph 감사가 아니다.**

→ 계약 문구를 다음으로 바꾼다:

```
이 packet의 evidence item은 실행 전 provenance/eligibility 검증을
통과했다. 모델은 출처의 liveness나 우선순위를 재판정하지 않는다.

모델의 책임은 evidence text가 해당 concept/feature의 온톨로지적
성격을 명시적으로 지지하는지, 그리고 evidence 간 의미 충돌이
있는지를 판정하는 것이다.
```

stale 문서와 live 코드의 권위 충돌은 별도 `source_authority_unresolved`
실험으로 분리한다.

## 5. `conflicting_evidence` 명확화

per-item `admissibility=conflict`는 **관계적 상태를 item 속성처럼 표현**하므로
제거한다.

`admissibility` enum (4개로 축소): `direct_support`, `indirect_context`,
`ambiguous`, `out_of_scope`

관계는 별도 필드로:

```json
{
  "evidence_id": "ev1",
  "admissibility": "direct_support",
  "supported_type": "essential_feature",
  "claim_strength": "explicit",
  "conflicts_with_evidence_ids": ["ev2"],
  "rationale": "..."
}
```

강도 순서: `explicit > implicit > weak > none`

**판정 알고리즘**:

```
1. direct_support만 후보로 취한다.
2. type별 최고 claim_strength를 계산한다.
3. 최고 강도의 type이 하나면 sufficient.
4. 양립 불가능한 둘 이상의 type이 최고 강도에서 동률이면 conflicting.
5. direct_support가 없으면 insufficient.
```

`conflicting` class는 schema에서 유지하되 E2.4에서는 **"적격 fixture
미확보"**로 기록한다. **stale-vs-live 쌍으로 대체하지 않는다.**

## 6. 해시와 실행 기록

`model_facing_sha256`을 **payload 안에 넣지 않는다.** 해시는 모델 밖
trial manifest에 기록한다.

```json
{
  "trial_id": "E24-R2-001",
  "fixture_sha256": "...",
  "qualification_sha256": "...",
  "payload_sha256": "...",
  "contract_prompt_sha256": "...",
  "rendered_prompt_sha256": "...",
  "decision_schema_sha256": "...",
  "builder_commit": "...",
  "model": "...",
  "parameters": {}
}
```

가장 중요한 값은 **`rendered_prompt_sha256`** — payload뿐 아니라 계약 문구까지
포함해 **모델이 실제로 본 전체 표면**을 고정한다.

## 7. 필수 테스트 (8종)

1. **출력 key-set 정확 일치** — 재귀적으로 모든 모델-facing 객체의 키가
   schema와 정확히 동일
2. **Hidden-field noninterference** — `builder_metadata`에 임의의 오라클
   문장을 삽입해도 **payload bytes와 hash가 완전히 동일**
3. **실제 유출 positive-control** — 발견된 6개 문장을 `builder_metadata`에
   넣고 어느 것도 rendered prompt에 나타나지 않음
4. **구조화 locator 거부** — locator 객체에 note·description 등 미허용
   필드를 넣으면 schema validation 실패
5. **Visible-field sensitivity** — `text`/`source_kind`/candidate type 중
   하나라도 바뀌면 payload hash와 rendered prompt hash가 바뀜
6. **Qualification binding** — fixture가 qualification 이후 변경되면 hash
   불일치로 payload 생성 거부
7. **Canonical-path 통합** — 스모크·본 실행·재실행 생성물이 모두 동일
   builder 함수를 사용
8. **루트 pytest 실행 보장** — 중복 `test_protocol.py` collection 문제를
   해결해 저장소 루트 게이트에서 실제로 수집됨

금지어 가드는 남겨도 되지만 **경고성 defense-in-depth일 뿐 합격의 근거가
되어서는 안 된다.**

## 8. 마이그레이션과 재실행

- `extraction_note` → `builder_metadata.evidence_notes`로 이동
- 모든 locator → tagged union 변환
- **`conflicting.ev6`의 "one commit later"를 "three commits later"로 정정**하고
  `ce3699a`, `d706152`를 기록
- fixture class/oracle → 별도 `oracle_manifest.json`으로 이동
- 실행 시 **class 이름 대신 불투명 fixture ID** 사용
- 기존 결과는 **`legacy_leaky`로 보존**하고 인증·통계에서 제외
- `_prompts.json` 또는 동등한 manifest **반드시 커밋**
- `trials.json`에 raw output과 전체 표면 hash 기록
- 새 표면 동결 후 **17 trials clean rerun**

**용어 규율**: 정확한 동일 prompt가 보존되지 않았으므로 기존 실행의
"재채점"이나 "정밀 재현"이라고 부르면 **안 된다**. 새로운
**`clean rerun cohort`**다.

**인증 상태**: 재실행 전 **0 class**. 재실행을 통과한 class만 다시 인증하며
**최대 유효 커버리지는 3 class**.

## 9. 이 결정의 논리적 핵심

지시서가 제기한 Q2의 두 갈래 중, "liveness를 구조화 필드로 모델에게
제공"하는 쪽을 **기각**했다. 근거는 §4의 세 가지이고, 그 중 결정적인 것은
**검증 불가능성**이다 — 모델은 `consulted_by` 같은 주장의 진위를 확인할
수단이 없으므로, 그것을 주는 것은 결국 또 하나의 신뢰 요구(=oracle)를
추가하는 것이다.

따라서 이 설계는 **오라클 유출**과 **검증 불가능한 authority 추론**을
동시에 막는다: 전자는 표면 분리(§1)와 화이트리스트 builder(§3)로, 후자는
검증 책임을 모델 경계 밖으로 이동(§4)해서.

---

## Amendment 1 (2026-07-28) — 요구사항 8번의 이행 방식

**동결 문서이므로 위 본문을 수정하지 않고 여기에 추가한다.**

§7-8은 "중복 `test_protocol.py` collection 문제를 해결해 **저장소 루트
게이트**에서 이 테스트들이 실제 수집되어야 한다"고 요구했다. 이행 과정에서
루트 단일 pytest로는 이 요구를 만족시킬 수 없음이 드러나, **게이트의 정의
자체를 바꾸는 방식**으로 이행했다(사용자 승인).

**왜 단일 pytest로 안 되는가**: `--import-mode=importlib`로 수집은 복구됐으나
(0개 → 89개), 그 즉시 두 번째 결함이 드러났다 — 실험 폴더들이 동결 규율상
`_cert_core.py`(6개 바이트동일)·`evaluate.py`(10개)·`_gen_prompts.py`(7개)를
같은 모듈명으로 중복 보유하는데, 두 실험의 test가 이를 plain import 하므로
한 인터프리터에서 먼저 로드된 쪽이 `sys.modules`를 선점한다. 결과적으로
2026-07-23 실험이 2026-07-19의 evaluator로 실행돼 `KeyError: 'role'`이 났다.
`_cert_core.py`의 헤더가 밝히듯 **이 중복은 preregistration 동결 규칙이
요구하는 것**이라 제거할 수 없고, 새 실험마다 하나씩 늘어난다.

**이행 방식**: `scripts/run_gates.py`를 유일 진입점으로 두고, 실험 self-check를
**실험마다 별도 프로세스**로 실행한다. 충돌이 구조적으로 불가능해지고 새
실험은 아무 조치도 필요 없다. `pytest.ini`는 `experiments/`를 제외해 맨손
pytest가 코어만 돌게 한다. `CLAUDE.md`의 게이트 절을 5개 명령 나열에서 단일
러너로 갱신했다(게이트가 원래도 단일 명령이 아니었으므로 사용성은 개선).

**요구사항 8번 충족 상태**: E2.4의 테스트가 게이트에서 실제로 실행된다는
취지는 달성. 다만 "루트 단일 pytest 명령"이라는 형식은 의도적으로 포기했다.

**러너의 PASS/FAIL/BLOCKED 규약**: 선택적 의존성 미설치로 게이트가 **시작조차
못 하면** BLOCKED(exit code 미반영), 테스트가 실행된 뒤 실패한 것은 실패
메시지가 모듈 누락을 언급해도 FAIL이다 — 그러지 않으면 환경 의존 테스트
하나가 같은 suite의 실제 회귀를 가린다.

**남은 red 1건 (승인 대기)**: `test_cg_obligations.py::test_registered_handlers_resolve`가
`owlready2` 부재로 스킵이 아니라 실패한다. 이 저장소는 이미 3곳에서
`pytest.importorskip("owlready2", ...)` 관례를 쓰는데 이 테스트만 따르지
않는다. **기존 결함**(변경 전에도 동일, `git stash`로 확인)이고 core 테스트
파일이라 승인 없이 수정하지 않았다. 제안 패치는 `docs/HANDOFF.md` §10.1.
