# DESIGN DECISION — O1 fixture 라이선스-안전 저장 (D-E2E-v1-20)

- 사슬 항법: 이전 [[DESIGN_DECISION_e2e_v1_experiment_design|D-19]] · **D-20** · 다음 [[DESIGN_DECISION_o1_oracle_unit_and_coverage|D-21]] · 색인 [[RULING_CHAIN_INDEX]]
- 수신: **2026-08-22** (요청서: `DESIGN_REQUEST_o1_fixture_licensing.md`, Q20)
- 판정 요지: **Q20.1 = (b+)** — corpus 원문·LF·expected IR 직렬화를 저장소에
  두지 않고 sha256 commitment로 동결 + **결정론적 Oracle Adapter**(일반
  syntax-directed, fixture별 lookup 금지) + **adapter qualification 별도
  전제**. Q20.2 template 개정 승인(union-type, normative 문안 제공).
  Q20.3 hash 갈음 승인 — 단 용어를 "preregistered"가 아니라
  **"cryptographically committed"**로(공개와 고정의 분리). Q20.4 캐시 허용
  (authority 아님, hash 일치 시에만, 소진 시 execution=UNAVAILABLE).
  신설 불변식 ORACLE-08~12. **법적 판정이 아니라 재배포-최소화 아키텍처
  선택임을 판정 스스로 한정**
- 저장: 트랜스크립트 verbatim 추출(M10). 본문 sha256: `8883964418ca5d12cf58bf923d6525cecf074133d5ff949de22a9fd57baceec7`

## 운영 세션의 저장 전 검증 (2026-08-22)

| # | 판정 주장 | 검증 | 결과 |
|---|---|---|---|
| V1 | 반례 존재 3건: Frozen∧¬Available, Frozen∧¬LicenseKnown, Commitment⇏TranslatorCorrectness | **구체 반례를 코드로 구성** — hash-pinned인데 URL·캐시 모두 부재 / 라이선스 미확정 / 오역 번역기의 출력도 유효한 sha256으로 commit됨 | ✅ 3/3 성립 |
| V2 | adapter 자격의 BLOCKER 조건(∀x∃y ≠ ∃y∀x는 다른 hash, α-변이는 같은 hash) | 기존 핀 테스트 대응 열거 | ✅ **이미 양쪽에 존재** — `test_cg_ir.py:39,85` + `test_cg_evaluate.py:32,59`. adapter qualification의 절반이 선구현 상태 |
| V3 | ORACLE-08~12가 기존 07종과 정합 | 대상 직교성 검토(artifact commitment/가용성/adapter vs 흐름 격리) | ✅ 충돌 없음 |
| V4 | 용어 개정(preregistered → cryptographically committed) | P14 grep — D-E2E-v1-19 원문에 옛 용어 존재 | ✅ **원문은 수령 canon이라 편집하지 않음** — 후속 문서(사전등록·adapter)부터 새 용어 적용. 개정은 저작자 자신의 후행 판정이므로 D-19를 소급 오염시키지 않음 |

## 이 판정이 부과한 재사용 규율 (기록)

- **disclosure ≠ commitment**: hash는 사후 조작을 막지만 내용 공개도,
  번역 정확성도 아니다(ORACLE-11). "계측기의 침묵" 계열의 새 항목.
- **identity는 locator+hash가 소유, URL은 resolver**(ORACLE-09):
  URL 사망 ⇏ fixture 변경, URL 생존 ⇏ artifact 진본.
- **답 은닉 금지**(ORACLE-12): fixture별 lookup은 "expected answer를 코드에
  숨겨 커밋"하는 우회 — W5 laundering의 oracle판.
- 캐시 소진 시 `execution: UNAVAILABLE` — W2 두 축 어휘와 정합.

## 다음 단계 (판정 순서)

1. yaml fixture_template 개정 적용(승인·문안 제공됨 — 같은 커밋)
2. Oracle Adapter(`typed-lambda LF → cg_ir dict`) — TDD, 일반 syntax-directed,
   qualification 5항목(구문 파싱·α-불변·재배열 음성·binding 보존·결정성 재생)
3. fixture manifest 20건(commitment 필드만) 동결 → Stage 2 코호트

---

## 판정문 원문 (verbatim)

Wolfram MCP로 Q20을 **“재배포 최소화”와 “실험 동결력”을 동시에 만족할 수 있는가**라는 형식 문제로 검토했습니다.

결론은 **Q20.1 = (b), 단 `b+`로 보강**하는 것이 가장 적절합니다.

> **corpus 원문과 LF는 저장소에 커밋하지 않고 hash-pinned external artifact로 유지한다. 결정론적 Oracle Adapter(LF→canonical IR)만 코드로 커밋하며, expected IR은 내용 대신 canonical hash로 사전등록한다.**
>
> 단, **번역기 자체의 정확성은 hash가 증명하지 못하므로 별도의 adapter qualification을 요구한다.**

이 방식은 기존 Oracle 격리 원칙과도 일치합니다. Oracle Adapter는 공통 IR/canonicalization primitive만 재사용할 수 있고 production Refine/Verify의 semantic judgment와 분리되어야 합니다. 

---

# DESIGN DECISION — D-E2E-v1-20

## Q20.1 — 저장 방식

### 판정: **(b) 채택, `b+`로 보강**

권장 구조:

```text
Public repository
│
├─ fixture manifest
│   ├─ corpus/version
│   ├─ locator
│   ├─ text_sha256
│   ├─ logical_form_sha256
│   ├─ expected_ir_sha256
│   ├─ oracle_adapter_version/hash
│   └─ canonicalization_profile/hash
│
├─ deterministic Oracle Adapter
│   └─ LF → canonical IR
│
└─ NO corpus text
    NO corpus LF
    NO expected IR serialization

External/local artifact
│
├─ source text
└─ source logical form
       │
       ↓ hash verification
Oracle Adapter
       │
       ↓
canonical IR
       │
       ↓
expected_ir_sha256 verification
```

O1 corpus에는 별도 LICENSE/README가 없고 논문 자체에는 CC-BY-NC 표기가 확인되어 있어 corpus 재배포 조건이 확정되지 않았다는 것이 현재 입력의 사실 상태입니다. 따라서 공개 저장소에 verbatim fixture를 넣지 않는 것이 설계상 가장 보수적입니다. 

단, 이것을 **“법적으로 안전하다”는 판정으로 읽으면 안 됩니다.** 이 판정은 법률 해석이 아니라 **저장소가 corpus 콘텐츠를 재배포하지 않도록 하는 아키텍처 선택**입니다.

---

# Wolfram 형식 검토 결과

먼저 `(a)/(b)`의 freeze와 availability를 분리했습니다.

Wolfram 결과:

```text
FreezeAContractTautology                  = True
FreezeBAddsCommitments                    = True
FrozenButUnavailableCountermodelExists    = True
FrozenButLicenseUnknownCountermodelExists = True
CacheCanSubstituteForUpstreamAvailability = True
```

핵심은 세 가지입니다.

### 1. hash pinning은 freeze를 만들 수 있다

[
locator
\land H(text)
\land H(LF)
]

가 동결되어 있으면 원문 bytes가 저장소에 없어도 **어느 artifact가 실험 대상인지**는 고정할 수 있습니다.

---

### 2. freeze와 availability는 다르다

다음 상태가 가능합니다.

[
Frozen=True
\land
Available=False
]

즉 hash가 있어도 URL도 죽고 cache도 없으면 실행할 수 없습니다.

따라서 availability는 별도 문제입니다.

---

### 3. hash pinning은 라이선스를 판정하지 않는다

또 다음 상태도 가능합니다.

[
Frozen=True
\land
LicenseKnown=False
]

따라서 `(b)`는 라이선스를 “해결”하는 게 아니라 **불확실한 재배포를 피하는 방식**입니다.

---

# 그런데 (b)에는 한 가지 중요한 공백이 있다

`expected_ir_sha256`를 고정했다고 해서 **LF→IR 번역기가 의미적으로 올바르다는 것은 증명되지 않습니다.**

이를 Wolfram으로 별도로 검증했습니다.

```text
CommitmentDoesNotImplyTranslatorCorrectness = True
TranslatorCorrectnessIsIndependentPremise    = True
```

즉:

[
H(ExpectedIR)
]

은:

> “나중에 expected IR을 바꾸지 않았다”

는 것을 강하게 고정할 수 있지만,

[
TranslatorCorrect
]

까지 함의하지 않습니다.

따라서 제가 승인하는 것은 순수 `(b)`가 아니라 다음 **`b+`**입니다.

---

# `b+` — Deterministic Adapter + Qualification

```yaml
oracle_fixture_storage:
  mode: pinned_external_artifact

  source:
    locator: ...
    text_sha256: ...
    logical_form_sha256: ...

  oracle_adapter:
    version: ...
    code_hash: ...
    deterministic: true
    qualification_status: passed

  expected:
    canonical_ir_sha256: ...

  repository_contains:
    corpus_text: false
    corpus_logical_form: false
    expected_ir_serialization: false
```

---

# Oracle Adapter에 추가할 강한 제한

번역기는 **corpus-specific answer table**가 되어서는 안 됩니다.

허용:

```text
parse typed-lambda-calculus syntax
map binder → Quantifier node
map variable → Variable node
map application → PredicateApplication
map nesting → scope topology
alpha-normalize
canonical serialize
```

금지:

```text
if fixture_id == O1_017:
    return expected_graph_017
```

또는:

```text
SOURCE_STRING_TO_EXPECTED_IR = {...}
```

같은 fixture별 lookup입니다.

즉 번역기는:

> **source formalism → project IR의 일반적인 syntax-directed adapter**

여야 합니다.

그래야 “expected answer 20건을 코드 안에 다른 형태로 숨겨 커밋”하는 우회를 방지할 수 있습니다.

---

# Adapter qualification도 production compiler와 분리

기존 지시의 Oracle isolation을 그대로 적용해야 합니다. 

```text
Production path

NL
↓
Refine
↓
Predicted IR


Oracle path

Published LF
↓
Oracle Adapter
↓
Expected IR
```

공유 가능:

```text
IR datatypes
canonical serializer
alpha-renaming primitive
hash primitive
```

공유 금지:

```text
semantic parse choice
scope resolution judgment
candidate ranking
Refine output
Verify verdict
```

특히:

```text
Oracle Adapter → Refine
Oracle Adapter → Verify
```

는 계속 금지입니다.

---

# Q20.2 — fixture_template 정본 개정

## 판정: **승인**

현재 template의:

```yaml
source:
  text: <verbatim>
```

과:

```yaml
external_oracle:
  representation_verbatim: ...
```

은 **inline verbatim만 허용하는 계약에서 union-type 계약으로 변경**합니다.

### BEFORE

```yaml
source:
  text: "<verbatim source sentence>"

external_oracle:
  representation_verbatim: "<verbatim source LF>"
```

### AFTER

권장 정본 문안:

```yaml
source:
  source_locator:
    corpus_id: "wikisem"
    corpus_version: "0.3"
    artifact: "<file>"
    record_locator: "<stable record/line identifier>"

  content:
    mode: "inline_verbatim | sha256_pinned_external"

    # mode=inline_verbatim일 때만 허용
    text: null

    # 항상 요구
    text_sha256: "<sha256>"

external_oracle:
  representation:
    mode: "inline_verbatim | sha256_pinned_external"

    # mode=inline_verbatim일 때만 허용
    representation_verbatim: null

    # 항상 요구
    representation_sha256: "<sha256>"

    source_locator:
      corpus_id: "wikisem"
      corpus_version: "0.3"
      artifact: "<file>"
      record_locator: "<stable record/line identifier>"
```

그리고 normative text를 다음처럼 확정하는 것이 좋습니다.

> **Oracle fixture source text and source formal representation SHOULD be stored verbatim when redistribution is authorized. When redistribution authorization is absent, unclear, or intentionally excluded by experiment policy, either field MAY instead be represented by a SHA-256-pinned external reference. A pinned external reference MUST identify the source artifact and record locator and MUST fail closed if retrieved bytes do not match the preregistered hash.**

여기서 중요한 것은:

```text
verbatim
OR
pinned external
```

이지:

```text
verbatim 없으면 아무 참조나 허용
```

이 아닙니다.

---

# Q20.3 — expected canonical IR을 hash로 갈음

## 판정: **승인, 단 “등록”의 의미를 commitment로 명확히 수정**

기존 D-E2E-v1-19의:

> `expected canonical IR`

을 반드시 저장소에 **내용 전체로 공개**해야 한다는 의미로 유지할 필요는 없습니다.

다음을 preregistration에 고정하면 충분합니다.

```yaml
expected_oracle:
  source_text_sha256: ...
  source_lf_sha256: ...

  oracle_adapter:
    version: "..."
    code_sha256: "..."

  canonicalization_profile:
    id: "semantic_ir_v1"
    profile_sha256: "..."

  expected_ir_sha256: "..."
```

이 조합이면:

[
ExpectedHash
============

H(
Canonicalize(
Adapter(
PinnedLF
)))
]

를 실행 시 재계산할 수 있습니다.

어느 하나라도 바뀌면:

* LF 변경
* translator 변경
* canonicalizer 변경
* expected hash 변경

불일치가 발생합니다.

---

## 다만 terminology를 바꿔야 한다

기존:

```text
expected canonical IR preregistered
```

보다 다음이 더 정확합니다.

```text
expected canonical IR cryptographically committed
```

즉:

> **내용 공개(disclosure)**와 **사전 고정(commitment)**을 분리합니다.

hash만 있는 경우 repository 독자는 expected IR을 읽을 수 없습니다.

따라서:

```text
preregistered expected IR
```

이라고만 쓰면 사람이 IR 내용을 미리 리뷰한 것처럼 오해할 수 있습니다.

권장 구분:

```yaml
expected_ir:
  disclosure: external_only
  commitment: sha256
```

---

# adapter correctness에 대한 별도 qualification

이게 `b+`의 핵심입니다.

최소:

```yaml
oracle_adapter_qualification:
  syntax_parse_tests: PASS
  alpha_rename_invariance: PASS
  quantifier_reordering_negative_test: PASS
  binding_preservation: PASS
  deterministic_replay: PASS
```

O1에서는 특히 다음 negative pair가 중요합니다.

```text
∀x ∃y R(x,y)
```

vs

```text
∃y ∀x R(x,y)
```

adapter가 이 둘에 같은 canonical hash를 내면 **BLOCKER**입니다.

반대로:

```text
∀x ∃y R(x,y)
```

vs

```text
∀a ∃b R(a,b)
```

는 같은 canonical representation으로 normalize되어야 합니다.

이는 기존 canonicalization 원칙과도 직접 일치합니다. 

---

# Q20.4 — 로컬 cache

## 판정: **허용**

오히려 권장합니다.

단:

> **cache는 authority가 아니라 retrieval optimization**

이어야 합니다.

### 권장 resolver

```text
1. local external cache
       ↓
   hash match?
   ├─ YES → 사용
   └─ NO  → 거부

2. upstream source
       ↓
   hash match?
   ├─ YES → 사용 + optional local cache
   └─ NO  → 거부

3. optionally user-supplied local artifact
       ↓
   hash match?
   ├─ YES → 사용
   └─ NO  → 거부
```

identity는 항상:

```text
locator + preregistered hash
```

가 소유합니다.

cache path는 identity가 아닙니다.

---

# cache 계약

```yaml
artifact_cache:
  allowed: true

  repository_tracked: false
  gitignored: true

  identity_authority: false

  required_validation:
    algorithm: sha256
    expected: preregistered_artifact_hash

  on_hash_mismatch: FAIL_CLOSED

  on_cache_absent:
    try_upstream: true

  on_cache_absent_and_upstream_unavailable:
    result: ARTIFACT_UNAVAILABLE
```

`ARTIFACT_UNAVAILABLE`을 semantic FAIL로 읽으면 안 됩니다.

이것은 앞서 정한 execution state와 동일하게:

```text
semantic result: none
execution: UNAVAILABLE
```

에 가깝습니다.

---

# URL 소멸을 fixture invalidation으로 읽지 않는다

예를 들어:

```text
OSU URL = dead
cache = exact hash match
```

라면 fixture는 여전히 동일합니다.

왜냐하면 fixture identity는 URL의 현재 생존성이 아니라 bytes hash에 있기 때문입니다.

따라서:

[
URLDead
\not\Rightarrow
FixtureChanged
]

입니다.

반대로:

```text
URL alive
but bytes hash changed
```

라면 실행을 거부해야 합니다.

[
URLAlive
\not\Rightarrow
ArtifactAuthentic
]

입니다.

---

# source locator도 한 단계 수정 권고

locator를:

```yaml
url: ...
line: ...
```

만 두기보다는:

```yaml
source_locator:
  corpus: wikisem
  version: "0.3"
  artifact: "<file-name>"
  record_id: "<stable record id if available>"
  retrieval_urls:
    - ...
```

로 두십시오.

즉 URL은 **resolver**이고 corpus/version/artifact/record가 논리적 locator입니다.

URL이 바뀌어도 fixture identity가 불필요하게 바뀌지 않습니다.

---

# (a)는 왜 차선인가

`(a)`도 기본 freeze는 성립합니다.

하지만:

```text
LF
↓
?
↓
expected project IR
```

의 변환 과정을 실행자가 매번 별도로 결정해야 합니다.

그러면 결국 운영자가 수동으로 IR을 만들거나 별도의 미동결 translation rule이 개입할 수 있습니다.

따라서:

```text
source fixed
but expected interpretation construction not fully fixed
```

가 됩니다.

`(b+)`는 이 경로까지 고정합니다.

---

# (c)를 채택하지 않는 이유

현재 입력 상태에서는 corpus 자체의 redistribution 조건이 확정되지 않았습니다. 

따라서 외부 설계자가:

> “20건 정도는 인용이므로 괜찮다”

라는 법률적 판단을 대신해서는 안 됩니다.

특히 실험 fixture는 일반적인 논문 인용보다:

* 기계적으로 수집된 corpus 문장
* 원문 LF
* 반복 가능한 benchmark material

이라는 성격이 강합니다.

따라서 **불필요하게 이 논쟁을 만들 이유가 없습니다.**

---

# (d)를 채택하지 않는 이유

현재 자료에서는 O1이 목적에 가장 잘 맞는 corpus이고, 대체 후보들은:

* 충분한 고정 sentence+LF pairing 부족
* fixture 수 부족

문제가 있다고 보고되어 있습니다. 

라이선스 불확실성은 **source substitution 없이 storage architecture로 격리 가능**하므로 oracle 자체를 교체할 이유가 없습니다.

---

# 추가 invariant

이번 Q20으로 아래를 canonical invariant에 추가하는 것을 권합니다.

### ORACLE-08 — Artifact commitment

> External oracle artifacts need not be stored in the repository when redistribution is not authorized or is unclear, but their exact bytes MUST be cryptographically committed before execution.

### ORACLE-09 — Availability is not identity

> Failure to retrieve an artifact does not change fixture identity. A retrieved or cached artifact may be used only if its bytes match the preregistered hash.

### ORACLE-10 — Adapter separation

> A deterministic Oracle Adapter may translate published formal representations into project canonical IR, but it MUST NOT be imported by or provide semantic judgments to Refine or Verify.

### ORACLE-11 — Commitment is not correctness

> A matching expected-IR hash proves consistency with the preregistered oracle transformation, not the semantic correctness of that transformation. Oracle Adapter qualification is a separate prerequisite.

### ORACLE-12 — No embedded oracle corpus

> Oracle Adapter source code, tests, and fixtures MUST NOT embed corpus sentences, logical forms, or fixture-ID-to-answer lookup tables except where redistribution is separately authorized.

---

# 최종 판정

```yaml
D_E2E_v1_20:

  Q20_1:
    decision: B_PLUS

    storage:
      corpus_text_in_repo: false
      corpus_lf_in_repo: false
      expected_ir_serialization_in_repo: false

    commit:
      - source_locator
      - corpus_version
      - text_sha256
      - lf_sha256
      - oracle_adapter_version
      - oracle_adapter_code_sha256
      - canonicalization_profile_sha256
      - expected_ir_sha256

    oracle_adapter:
      deterministic: true
      generic_syntax_directed: true
      fixture_specific_lookup: forbidden
      production_refine_import: forbidden
      production_verify_import: forbidden
      qualification_required: true

  Q20_2:
    fixture_template_amendment: APPROVED

    source_representation:
      allowed_modes:
        - inline_verbatim
        - sha256_pinned_external

    pinned_external:
      fail_closed_on_hash_mismatch: true

  Q20_3:
    expected_IR_hash_substitution: APPROVED

    interpretation:
      hash_is_commitment: true
      hash_is_disclosure: false
      hash_proves_translator_correctness: false

    preregistration_term:
      preferred: expected_IR_cryptographic_commitment

  Q20_4:
    local_cache:
      allowed: true
      repository_tracked: false
      authority: false
      use_only_after_hash_match: true

    upstream_unavailable_and_no_cache:
      execution: UNAVAILABLE
      semantic_FAIL: false

  legal_scope:
    ruling_is_redistribution_minimizing_design: true
    ruling_is_legal_license_clearance: false
```

## 핵심

이번 변경은 재현성을 약화시키는 것이 아닙니다.

오히려 정본을:

```text
“저장소에 원문이 있어야 frozen”
```

에서

```text
“실험에 사용되는 exact bytes와 변환 규칙이 사전에 cryptographically committed되어야 frozen”
```

으로 일반화하는 것입니다.

그리고 가장 중요한 제한은 하나입니다.

> **hash는 사후 조작을 막지만 의미적으로 잘못 만든 Oracle을 올바르게 만들지는 않는다.**

따라서 `(b+) = external hash commitment + deterministic isolated Oracle Adapter + adapter qualification`까지를 하나의 설계 단위로 채택하는 것이 맞습니다.
