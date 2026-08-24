# Harness 대조 분석 + 적대 검증 — 2026-08-24

- 대상: 이 세션이 만든 게이트 2종(`test_verbatim_canon_integrity.py` ·
  `test_exclusion_rules_are_exercised.py`)
- 방식: ① Codex 라인 harness와 대조(공백 분석, lead 직접) ② Haiku red team
  2기 병렬(근거 축 분리: A=정본 게이트+docs corpus, B=공허성 게이트+대상 모듈)
  ③ lead 재실측 후 수리
- 관련: [[concept-gate-h1-wt/docs/H1A_PROBLEM_ANALYSIS|H1A_PROBLEM_ANALYSIS]] §14 · adversarial-review 스킬

## Part A-1 — Codex harness 대조 (공백 분석)

Codex worktree(`concept-gate-codex-mcp-wt`, 읽기 전용)의 harness 목록을 전수
대조했다. Codex 전용 2종 + 발산 1건:

| Codex harness | 하는 일 | 우리 쪽 대응물 | 공백 판정 |
|---|---|---|---|
| `handoff_repair_loop.py` | "검사기 통과까지 편집" 루프의 **anti-gaming 가드** G1~G5: 검사기 해시 고정 · 링크 덤프 금지(파일당 상한) · 링크마다 문맥 요구 · **입력 집합 축소 금지**(red team이 .gitignore로 orphan을 지워 metric 9→0, 실개선 0을 달성한 실측에서 나옴) · 단조 진행 | 없음 | **공백이나 당장 도입 안 함** — 우리는 도달성 검사기를 삭제했다(P21). 단 이 세션의 일괄 링크 배선(26+11건)이 정확히 이 위험 범주였고, **G2·G3 관점의 사후 점검은 통과**한다(항법 줄은 문맥 있는 산문이고 색인은 서술 있는 표다 — 맨 링크 덤프 아님). 배선을 게이트화하는 날이 오면 G1~G5를 수입해야 한다 |
| `orphan_replica_audit.py` | worktree **간** 바이트 동일 사본을 정본 1부로 접은 뒤 orphan 판정. vault-harness의 collapse 로직을 **import로 재사용**(복사 아님) | `test_handoff_single_authority.py` — 범위가 **이 worktree 내부**(rglob) | **중복 아님, 상호 보완** — 그쪽은 "논리 문서가 어디서든 링크되는가", 우리는 "이 worktree에서 current를 주장하는 사본이 하나뿐인가" |
| `test_guard_negative_coverage.py` **발산** | Codex 쪽에 `_PENDING` + `KNOWN_UNPROVEN` 3항(provider preflight 계열, 그쪽에만 있는 함수들) 추가 | 우리 판 | **G31 계열 2건째**(가드 게이트도 worktree마다 갈라짐). 그쪽 항목은 그쪽 함수에 대한 것이라 즉시 충돌은 아니나, 합류는 commit 경로로만 — 등재만 한다 |

Codex 쪽에서 **수입한 것은 코드가 아니라 규율**이다:
1. **가드의 한계를 숨기지 않고 적는다** — repair_loop이 "G1은 여전히 우회
   가능하다(bytecode), green run을 tamper-proof로 읽지 마라"를 머리에 적은 것.
   우리 두 게이트에 같은 태도로 잔여 우회를 명시했다.
2. **red team이 뚫은 경로를 도구 안에 기록한다** — 다음 저자가 같은 구멍을
   다시 열지 않게. 아래 Part B의 수리 주석이 그 형식이다.

## Part A-2 — Haiku red team 결과와 lead 재실측

### 게이트 B(배제 규칙 공허성) — **blocker 1 적중, 수리 완료**

| Finding | red team | lead 재실측 | 처분 |
|---|---|---|---|
| B-1 원장 검사가 문자열 검색 — 주석·docstring·**KNOWN_UNWITNESSED 등재**가 증인으로 세어짐 | blocker | **CONFIRMED** — lead가 red team과 독립으로 같은 결함을 먼저 발견(주석 게이밍 실측). red team이 더 넓혔다: 면제 등재만으로 원장 통과 | **수리**: AST 기반 — `test_*` 함수 **본문**(docstring 제외)의 문자열 상수만 증인. 면제는 별도 경로로 명시 집계. 수리 첫 판은 음성 테스트 자신의 단언 문자열이 수집되는 자기참조로 실패했고 **음성 테스트가 그것을 잡았다** — 프로브를 런타임 결합으로 교체. 공격 3경로 재현 검사 전부 차단 확인 |
| B-2 면제 사유의 형식 검사 게이밍("aaa…담당: x"도 통과) | major | CONFIRMED — 형식 검사로 의미를 검사할 수 없음은 원리적 | **정직한 한계로 문서화**: "tripwire이지 증명이 아니다. 막는 것은 빈 면제뿐, 의미는 사람 리뷰와 git diff의 몫" (Codex G1 태도) |
| B-3 증인 dict에 `span` 부재(실물 파서 산출과 형태 차이) | minor | CONFIRMED — 현재 미사용이나 형태 드리프트 위험 | **수리**: `_ep`에 `span` 추가 |
| (실패한 공격) 증인 오염 — 각 증인이 의도한 규칙만 발동하는가 | — | red team 전수 실행: **전부 의도 규칙만 발동** | 게이트의 핵심 주장이 공격에서 생존 |

### 게이트 A(정본 무결성) — 오발 2 수리, 과대평가 2 하향

| Finding | red team | lead 재실측 | 처분 |
|---|---|---|---|
| A-1 대문자 hex 기록을 "기록 없음"으로 오발 | major | CONFIRMED — 단 방향이 **소리 내는 실패**(조용한 통과 아님). 오발은 신뢰를 깎고 신뢰 잃은 게이트는 꺼지므로 수리 가치 있음 | **수리**: IGNORECASE + 소문자 정규화, 수리 증거 테스트 2건 |
| A-2 필드명 대소문자 변형 미인식 | minor | CONFIRMED | 같은 수리에 포함 |
| A-3 code fence 안의 해시도 "기록"으로 인정 | major | **하향(minor)** — 재실측하면 이미 알려진 잔여 우회("블록과 기록을 둘 다 고치면 통과")와 등가다. 기록이 어디 있든 고치는 행위는 같고 방어층도 같다(**git diff에 반드시 드러난다**). SHA256 preimage가 불가능하므로 "우연한 일치"는 경로가 아니다 | 게이트 머리에 **한계로 문서화**. 위치 제약은 규약 두 변종을 깨므로 도입 안 함 |
| A-4 기록 탐지 범위가 문서 전체 | major | **하향(minor)** — A-3과 같은 부류 | 같은 문서화에 포함 |
| (실패한 공격) 다중 블록 · parametrize 우회 · 해시 충돌 · 변조본 해시 삽입 | — | — | 마커 유일성 테스트·git·preimage가 방어 |

severity 하향 2건은 스킬의 "보수적 판정 채택"에 대한 예외이며 사유를 위에
적었다 — **lead 재실측이 등가성(기존 문서화된 우회와 같은 부류)을 증명한 경우**
는 과대평가를 유지하는 것이 오히려 원장을 오염시킨다(P12: 대리 산출은 재실측
전 잠정 — red team도 대리다).

## Part A-3 — 이 검증 자체가 만든 관측

1. **게이트를 잡으려고 만든 게이트가 같은 결함 부류를 저질렀다** — 원장 검사가
   "코드가 참으로 만들지 않는 명제"를 주장했다. Codex repair_loop의 red team
   기록("docstring이 가드 5개를 주장하는데 3개만 구현")과 **정확히 같은 형태**다.
   두 라인이 독립적으로 같은 실패를 저지르고 독립적으로 적대 검증으로 잡았다 —
   이 결함 부류는 저자 규율로 못 막고 **적대 검증이 표준 절차여야 한다**는
   근거가 하나 더 쌓였다.
2. **음성 테스트가 수리 자신의 결함을 잡았다** — 수리 첫 판의 자기참조(프로브
   리터럴이 자기 단언에서 수집됨)를 사람이 아니라 방금 쓴 음성 테스트가 잡았다.
3. red team의 **실패한 공격 목록**이 성공 목록만큼 값을 냈다 — "증인 오염
   없음"은 이 검증이 아니면 미검증 주장으로 남았을 것이다.

## 잔여 (수리하지 않은 것)

- A-3/A-4의 잔여 우회(블록+기록 동시 수정)는 **git이 방어층**이다. 게이트
  안에서 닫을 수 없고, 닫으려는 시도(위치 제약)가 더 큰 비용을 만든다.
- B-2의 면제 사유 의미 검증은 원리상 형식 검사 밖이다.
- guard 게이트 발산(G31 계열)은 등재만 — 합류는 commit 경로의 별도 작업.

---

# Part B — red team 원본 보고서

스킬은 Part B를 선택 사항으로 두었으나 **빠뜨린 것이 결함이었다**: 초판에는
합성(Part A)만 있었고 원문이 대화에만 있었다 — P13(적용된 정본의 원문 부재)의
형태다. 우리가 finding에 근거해 코드를 고쳤으므로 그 근거는 저장소에 있어야 한다.

**주의 — 이것은 외부 정본이 아니라 subagent 산출이다.** 그래서
`VERBATIM-BEGIN/END` 마커를 쓰지 않는다(그 규약은 외부 판정·조사 회신 전용이고,
정본 무결성 게이트의 대상이다). 대조 가능성은 아래 sha256으로 둔다.
severity는 **red team이 붙인 값 그대로**이며 lead 재실측 후의 처분은 Part A에 있다
(A-3/A-4는 minor로 하향했다 — 사유는 Part A).

## B-1 — 정본 무결성 게이트 공격 (Haiku)

`report_sha256: 423e3f20a21f850b7609fa592e811d2d4f45eaeaa15e81c1b1e68c96d428cb06`

```text
## 적대 검증 보고서: test_verbatim_canon_integrity.py

### Finding 1: False Positive – 대문자 해시는 정규식이 인식 불가
- 종류: false-positive / 심각도: major / 근거 행: test_verbatim_canon_integrity.py:43
재현: 기록 해시를 대문자로 바꾼 사본에 `_HASH.findall`을 적용 → `set()`(빈 집합).
정규식 `[0-9a-f]{64}`는 소문자만 매칭한다. hexdigest는 소문자를 내지만 사람이
대문자로 옮겨 적으면 게이트가 "기록 없음"으로 실패한다. body 자체는 유효하다.

### Finding 2: False Positive – 필드명 대소문자 문제
- 종류: false-positive / 심각도: minor / 근거 행: :43
`VERBATIM_Sha256:`처럼 쓰면 `(?:sha256|SHA256)`가 매칭하지 않는다.

### Finding 3: Vacuity – 해시가 Code Fence 안에 있어도 게이트 통과
- 종류: vacuity / 심각도: major / 근거 행: :43(regex scope)
재현: 해시 필드를 ```yaml 코드펜스로 옮긴 사본 → `got & recorded` 가 True.
정규식이 문서 전체를 검색하므로 코드블록·표·산문 어디에 있어도 "기록"으로
인정된다. 게이트는 "메타데이터에 기록"을 의도하지만 위치를 보장하지 않는다.

### Finding 4: Vacuity – 문서 전체에서 해시를 찾아 의도하지 않은 값 매칭 가능
- 종류: vacuity / 심각도: major / 근거 행: :75
verbatim 블록 내부나 다른 섹션의 `sha256: xxx`도 캡처될 수 있다.

## 시도했으나 실패한 공격
1. 내용 수정 후 수정본 해시를 body 안에 포함 — body가 바뀌면 해시도 바뀌어 불가
2. 여러 VERBATIM 블록 — 마커 유일성 테스트가 방어
3. Parametrize 우회 — git이 파일 버전을 추적하므로 수집 후 수정도 혼입 불가
4. Hash collision — SHA256 collision은 현실적으로 불가능

## 총평
정규식의 캐릭터 클래스(소문자 전용)·검색 범위(문서 전체)·필드명 대소문자를
재검토해야 한다. 정규식 대신 구조적 파싱(헤더 영역만, YAML 필드 검증) 권장.
```

## B-2 — 배제 규칙 공허성 게이트 공격 (Haiku)

`report_sha256: 3c3cd5ad5f0a82021906fed1572da49b5977f83599e0210a0b42dda118f77648`

```text
## 적대 검증 보고서: test_exclusion_rules_are_exercised.py

### Finding 1: 원장 대조의 문자열 검사 우회
- 종류: ledger-bypass / 심각도: blocker / 근거 행: :145
`missing = [c for c in mcp.REJECT_CODES if f'"{c}"' not in src]` 는 "증인
테스트의 존재"가 아니라 **"소스에 코드 문자열의 존재"**만 확인한다.
시연: REJECT_CODES에 `new_code_without_witness` 추가 + KNOWN_UNWITNESSED에 같은
이름 등재 → 증인 테스트 없이 통과. 출력: `Missing codes: []` / `검사 통과!`

### Finding 2: KNOWN_UNWITNESSED 등재 조건의 형식 검사 우회
- 종류: gaming / 심각도: major / 근거 행: :151-154
`len(reason) > 60` 과 `"담당" in reason` 은 길이와 단어 존재만 본다.
시연 3케이스 전부 통과: "aaa…담당: someone"(74자) · "---…담당: nobody"(70자) ·
"xxx…담당: test"(88자).

### Finding 3: 증인의 구조 부족
- 종류: shape-mismatch / 심각도: minor(현재) → blocker(미래)
- 근거 행: witness :39-44 / reader conceptgate/cg_mrs_reader.py:68-74
witness `_ep()`는 `{"pred","lbl","args"}`, 실물 파서는 `{"pred","span","lbl","args"}`.
현재 package_count는 span 미사용이라 영향 없으나, span을 쓰는 게이트가 추가되면
증인이 오염될 수 있다.

## 시도했으나 실패한 공격
witness-contamination: 모든 증인이 의도한 규칙만 발동함(전수 실행 확인).
type_mismatch · unsupported_compound_cardinal_mapping_v1 · DESIGNATOR 등 전부 일치.

## 총평
Finding 1+2를 합치면, 새 reject 코드를 추가할 때 증인을 쓰지 않고
KNOWN_UNWITNESSED에 코드명과 무의미한 이유만 넣으면 모든 자동 검사를 통과한다.
게이트가 보호하려던 상황(공허한 배제 규칙)이 정확히 이것이다.
```
