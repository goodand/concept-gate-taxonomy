# 식별자 등록부 — 한 글자가 어디서 무엇을 뜻하는가

- 작성: 2026-08-31. 계기: 회고 §24(G164) — `I3` 가 두 설계 문서에서 다른 불변식이고,
  `P4` 가 회고에서는 패턴·DIRECTIVE 에서는 구현 단계다. 사용자: "분류체계를 위해서
  진짜 사전(dictionary)를 만들어야겠네."
- 게이트: [`test_identifier_register.py`](../test_identifier_register.py) — 상태 어휘
  닫힘 · 정의 위치 실재 · **발행 형식 강제** · 인벤토리 누락 · 음성 증명.
  [`test_adoption_register.py`](../test_adoption_register.py) 와 같은 골격.
- 사슬 항법: [[LEGACY_REGISTER]] · [[ADOPTION_REGISTER]] · [[RULING_CHAIN_INDEX]] ·
  회고 [[H1A_PROBLEM_ANALYSIS]] §24 · 실측 [[REFINE_VERIFY_STAGE_SURVEY_20260830]] §10~§12 ·
  상태 [[concept-gate-h1-wt/HANDOFF|HANDOFF]]

## 왜 있는가

단일 대문자+번호 식별자가 여섯 문서군에서 **독립적으로 발행**된다. A~Z 전수 조사
(2026-08-31): 17글자가 2개 이상 문서군에 걸치고, haiku 감사 2축이 문맥을 읽어 판별한
결과 **10글자는 같은 번호가 다른 것을 뜻하고**(COLLIDES — 게이트가 `V@rulings` 셋째 뜻을 추가 적발), 4글자는 한 곳이 발행하고
나머지는 인용만 한다(CITES_ONLY), 3글자는 단일 소유다.

**이 등록부는 충돌을 없애지 않는다.** 열한 계열 중 우리가 소유한 것은 넷이고 나머지는
외부 설계 원문(verbatim 보존)·다른 저장소·도구 소관이라 재번호할 수 없다. 등록부가
하는 일은 **어느 글자를 어느 문서군에서 읽고 있는지 독자가 알 수 있게** 하는 것이고,
게이트가 하는 일은 등록부가 현실과 어긋나는 것을 막는 것이다.

**인용 규약 — 완전 한정형(FQN) `<문서군>:<글자><번호>`** (2026-08-31, 검증 후 채택)

계열이 모호한 자리에서는 `retro:G164` · `directive:I3` · `mechspec:I3` · `ev-eval:I207`
처럼 **문서군 이름을 접두로** 쓴다. 문서군 이름은 아래 표의 것 그대로 — 새 어휘를
만들지 않는다. 자기 문서군 안에서 자기 계열을 쓸 때는 접두가 필요 없다.

**과거 인용은 건드리지 않는다.** 이 규약은 새 발행·새 인용부터 적용된다 — 이 저장소의
append-only 규약과 같은 형태다. 기존 문서의 `G164`·`I3` 는 그대로 두고, 필요하면
이 등록부에서 (글자, 문서군)으로 찾는다.

**왜 재번호가 아니라 FQN 인가 — 실측 (2026-08-31):**

| 방법 | 비용 | 푸는 것 |
|---|---|---|
| 재번호 `M@retro → V` | 인용 **143건·11파일**(verbatim 안 0 — 기술적으로 가능). 그중 124건이 회고이고 회고 헤더 규약은 "원문을 덮어쓰면 당시 무엇을 알았는지가 사라진다" — 재번호가 정확히 그 덮어쓰기다 | `검증` 개념 **하나**의 글자 통일. 나머지 다섯 역방향 중복은 못 푼다 |
| FQN | 이 등록부의 접두 열 **32가지 제멋대로 표기 → 7 문서군 이름**으로 고정. 원문 문서 0건 수정 | 순방향(`I3` 둘) — 접두가 이름공간이라 원리적 해소. 역방향(문제 7글자) — 개념 열이 집계 키 |

고빈도 정규화(직전 제안)는 세 개념에서 우리 소유가 고정 계열보다 커서 답을 내지
못했다(§정규화). FQN 은 크기를 비교하지 않는다 — 계열마다 접두 하나면 끝이다.

**빠지는 것**: 개념 판정은 여전히 사람이 한다. `retro:L`(drill-down 레벨)과 `mechspec:S`
(기제 슬롯)을 같은 `등급` 에 넣은 것은 판단이고 틀릴 수 있다. FQN 은 그 판단을
자동화하지 않고 **한 곳에 모아 게이트가 지키게** 할 뿐이다.

## 문서군

| 이름 | 경로 | 저장소 안 |
|---|---|---|
| `retro` | `docs/H1A_PROBLEM_ANALYSIS.md` | ✅ | `미분류` | ? (?) |
| `rulings` | `docs/DESIGN_DECISION_*.md` · `docs/DESIGN_REQUEST_*.md` | ✅ | `미분류` | ? (?) |
| `directive` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md` (+ 동반 yaml) | ✅ — **외부 설계 원문, verbatim** | `미분류` | ? (?) |
| `roadmap` | `docs/obligation_layer_roadmap.md` | ✅ | `미분류` | ? (?) |
| `h1a-scope` | `../concept-gate-h1a-scope-wt/` (md + `qa_v7.py`) | ❌ 다른 worktree |
| `mechspec` | `../notes/research/logical-revision/*.md` | ❌ vault, git 미추적 | `미분류` | ? (?) |
| `ev-eval` | `../evidence-evaluator/docs/**/*.md` | ❌ 다른 저장소 (**문서**) |
| `ev-eval-code` | `../evidence-evaluator/evidence_evaluator/*.py` | ❌ 다른 저장소 (**코드**) | `미분류` | ? (?) |
| `h1-docs-기타` | `docs/*.md` 중 위 넷이 아닌 것(SURVEY·등록부·NAVIGATION 등) | ✅ — **인용만** |
| `experiments` | `experiments/**/*.md` | ✅ — **인용만** |
| `experiments-code` | `experiments/**/*.py` | ✅ — **인용만** |
| `h1-code` | `concept-gate-h1-wt/*.py` (루트 테스트·`conceptgate/`) | ✅ — **인용만** |
| `h1a-scope-code` | `../concept-gate-h1a-scope-wt/*.py` | ❌ 다른 worktree |
| `notes` | `../notes/**/*.md` (logical-revision 제외) | ❌ vault |
| `vault-backlinks` · `vault-backlinks-code` | `../vault-backlinks-mcp/` | ❌ 다른 저장소 |
| `archive` | `../archive/**/*.md` | ❌ **읽기 전용 역사 증거** — 인벤토리에는 넣고 권위에서는 뺀다 |
| `vault-tool` | `vault_search` 가 붙이는 `authority_class` | ❌ 도구 산출 | `미분류` | ? (?) |

## 상태

| status | 뜻 |
|---|---|
| `OWNER` | 이 문서군이 이 글자의 계열을 **발행**한다. 발행 형식이 게이트로 강제된다 || `미분류` | ? (?) 
| `CITES_ONLY` | 이 문서군은 이 글자를 발행하지 않고 다른 OWNER 의 번호를 **같은 뜻으로** 인용만 한다 || `미분류` | ? (?) 
| `COLLIDES` | 이 문서군이 이 글자를 발행하는데 **다른 문서군도 같은 글자를 다른 뜻으로** 발행한다 || `미분류` | ? (?) 
| `EXTERNAL` | 저장소 밖 문서군의 발행. 게이트가 읽지 못하므로 기록만 한다 |
| `FP_DIAGRAM` | **위양성 — mermaid 노드 id** (`N1[...]` · `B -->|Yes| X1`). 그림 문법이지 식별자가 아니다 |
| `FP_SECTION` | **위양성 — 절 번호** (`§A9`) |
| `FP_EXPERIMENT` | **위양성 — 실험 이름** (`H1a` · `H3`) || `미분류` | ? (?) 

## 기호 → 영문 → 뜻 — tree 는 **일부에서만** 성립한다

사용자: "(영문)기호 → (영문)첫글자 → 뜻은 tree 로 표현할 수 있으니까." 실측: 발행 행
36개 중 **30개는 영문 첫 글자**(initial)이고 tree 가 성립한다. **6개는 아니다** —
원문이 그렇게 말한다:

| 유형 | 행 | 근거 |
|---|---:|---|
| `initial` — 글자 = 영문 뜻의 첫 글자 | 30 | P=Pattern·Phase·Priority / I=Invariant·Issue / M=Method·Milestone·Measurement / V=Version·Verification / R=Render·Reference·Requirement … |
| `arbitrary` — 영문 약자가 아니다 | 3 | `retro:G` 표 헤더가 `\| # \| 문제 정의 \|` — 한국어 "문제"에 붙인 임의 글자. **가장 큰 계열(164개)이 여기다.** `retro:D`(trial 계획)·`rulings:W` 도 |
| `ordinal` — 적대적 검증의 **축 순서** A·B·C·D… | 3 | `rulings:B`(D-35 지적)·`rulings:C`·`D`·`F`(D-36 검증·확인 표) — `## 2. 축 A의 부재 판정` 처럼 축 이름이 알파벳 순 |

initial 형만의 tree (같은 글자가 여러 영문 단어로 갈리는 것이 순방향 충돌의 실체다):

```text
P ─┬─ Pattern       (retro)          ─→ 패턴
   ├─ Phase         (directive)      ─→ 단계
   └─ Priority      (vault-tool·ev-eval) ─→ 등급
I ─┬─ Invariant     (directive·mechspec) ─→ 불변식   ← 같은 단어, 다른 내용
   └─ Issue         (ev-eval)        ─→ 문제
M ─┬─ Method        (retro)          ─→ 검증
   ├─ Milestone     (roadmap)        ─→ 단계
   └─ Measurement   (rulings)        ─→ 등급
V ─┬─ Version       (retro)          ─→ 버전
   └─ Verification  (directive·rulings) ─→ 검증
R ─┬─ Render        (retro)          ─→ 문제
   ├─ Reference     (directive)      ─→ 출처
   └─ Requirement   (rulings)        ─→ 요건
C ─┬─ Check         (retro)          ─→ 검증
   └─ Case          (ev-eval)        ─→ 검증
D ─┬─ Delta         (directive)      ─→ 규칙
   └─ Defect        (ev-eval)        ─→ 문제
F ── Finding        (retro·ev-eval)  ─→ 문제
Q Question · O Oracle · E Exclusion · L Level · S Slot · Z Zoom · B Backlinks   (단일)
```

**tree 가 보여주는 것**: 순방향 충돌은 "같은 첫 글자를 가진 다른 영문 단어"이고(P 셋·M 셋·R 셋),
역방향 중복은 "다른 영문 단어가 같은 개념"이다(Issue·Defect·Finding·Render → 문제). 그리고
**`I → Invariant` 가지는 같은 단어인데 내용이 다르다** — 이것만은 tree 로도 갈리지 않고
문서군 접두(FQN)로만 갈린다. arbitrary·ordinal 6행은 tree 밖이고 FQN 만이 이름이다.

## 등록 범위 — **발행자와 충돌만 담는다** (2026-08-31, A~Z 전수)

워크스페이스 전체를 발행 단위(코드/문서로 갈린 13군)로 나눠 내용 SHA-256 dedup 후
전수했다. 정본 832개 · (글자,문서군) 쌍 **225개**. 그중 등록부 밖이 77쌍이었다.

**그러나 77 을 다 등재하지 않는다.** 발행(표 첫 셀·절 제목·코드의 dict 키)과 인용(산문)을
기계로 갈라 보니, 발행 10회 이상인 35쌍 중 **34쌍이 이미 소유자가 있는 글자**였다 —
`Q@experiments` 는 rulings 의 Q 를 쓰는 것이지 새 계열이 아니다. 인용처를 전부 등재하면
표가 100행을 넘으면서 **정보는 하나도 늘지 않는다.**

    등록부에 담는다   OWNER(발행) · COLLIDES(둘 이상이 발행) · EXTERNAL(밖의 발행) · 위양성
    담지 않는다       인용처. 소유자가 이미 표에 있으므로 FQN 으로 찾을 수 있다

소유자 없는 발행은 **단 하나**였고 위양성이었다 — `H@experiments` 12건은 `H1`·`H2`·`H3`
로 **가설·실험 이름**이다(`# 설계 판정 요청 — H3 확증 실험의 estimand`). 이미
`FP_EXPERIMENT` 로 등재돼 있다.

**즉 글자 차원은 닫혔다.** A~Z 중 계열로 쓰이는 것은 전부 표에 있고, 남은 것은 문서군
차원인데 그것은 인용이라 담지 않는 것이 설계다. 게이트가 이 구별을 기계로 한다
(`test_no_unregistered_issuance_by_an_unowned_letter`).

## 개념 — 뜻 → 글자 (역방향)

같은 것이 문서군마다 다른 글자로 불린다. 순방향 충돌(한 글자 여러 뜻)은 독자가
오독하게 하고, 역방향 중복(한 뜻 여러 글자)은 **검색·집계를 불가능하게** 한다 —
"저장소 전체 결함이 몇 개인가"에 답하려면 여덟 계열을 합쳐야 하고 합산 규칙은 없다.

| 개념 | 글자 | 뜻 |
|---|---|---|
| `문제` | **A B D E F G I R S T W X** | 발견된 결함·이슈·finding·BLOCKER || ? (?) 
| `검증` | **B C D F I M N V** | 검증 항목·방법·테스트 케이스·수신 검증 || ? (?) 
| `등급` | **L M P S Z** | 권위 등급·레벨·줌·슬롯·능력 축 || ? (?) 
| `규칙` | D E J K | 배제 규칙·공백 항목·trial 계획 || ? (?) 
| `단계` | M P | 구현 단계·마일스톤 || ? (?) 
| `불변식` | I | 두 설계 문서의 불변식 (내용 상이) || ? (?) 
| `출처` | O R | 오라클 슬롯·참조 문헌 || ? (?) 
| `요건` | Q R | 외부 판정 질문·Q36 요건 || ? (?) 
| `버전` | V | 동결 버전 || ? (?) 
| `패턴` | P | 반복 실패 형태 — **역방향에서는 중복 없음** || ? (?) 
| `(인용)` | — | CITES_ONLY 행 — 개념을 새로 만들지 않는다 || ? (?) 

### 정규화 — 고빈도를 표준으로, 저빈도를 바꾼다 (사용자 제안, 2026-08-31)

실측(등장 횟수, 코드블록 제외):

| 개념 | 고정(외부·verbatim) 최빈 | 우리 소유 최대 | 판정 |
|---|---|---|---|
| 문제 | `I@ev-eval` 230 | **`G@retro` 547** | 우리가 2.4배 크다(**언급** 기준 — 재번호 비용은 언급이 정한다). 표준을 따르면 **큰 것을 작은 것에 맞춰 재번호**. 하지 않는다 |
| 검증 | `V@rulings` 287 | `M@retro` 124 | 고정이 크다 — **유일한 정당 후보.** 단 M1~M19 인용 124회 재작성 비용 |
| 등급 | `S@mechspec` 65 | `L@retro` 13 | 후보이나 L0~L2 는 drill-down 레벨, S 는 기제 슬롯 — **같은 개념이 아닐 수 있다** |
| 규칙 | `D@directive` 7 | `E@retro` 41 | 우리가 6배 크다. 하지 않는다 |
| 단계 | `P@directive` 7 | `M@roadmap` 20 | 우리가 3배 크다. 하지 않는다 |

**"상대치라 복잡하다"가 맞다.** 단순 최빈은 세 개념에서 **큰 계열을 작은 계열에 맞추라**고
한다 — 우리가 바꿀 수 있는 쪽이 대개 더 크기 때문이다. 정당한 규칙은
**고정 계열 중 최빈 ∧ 우리 계열보다 크다**이고, 그 조건에서 후보는 `검증` 하나다.
그것도 재번호 비용(124회)과 이득(집계 가능)을 비교해야 하며, 이 등록부는 결정하지
않고 기록한다. **개념 열을 통한 집계는 재번호 없이도 가능하다** — 그것이 이 표의 용도다.

### 문서군은 저장소가 아니라 **발행 단위**다 (2026-08-31, 게이트가 잡음)

`ev-eval` 의 실패 코드 9글자를 넣으니 게이트가 `(글자, 문서군)` **중복 3건**
(`C`·`D`·`I`)을 냈다. 한 저장소가 같은 글자로 **두 계열**을 돌리기 때문이다 —
실패 코드는 `evidence_evaluator/contract.py`(코드), 이슈 번호는 `docs/feedback/*.md`(문서).

키를 늘리는 대신 **문서군을 갈랐다**: `ev-eval`(문서) / `ev-eval-code`(코드).
애초에 다른 발행 단위였고 내가 저장소 하나를 통째로 한 군으로 잡은 것이 잘못이었다.
`h1a-scope` 도 같은 형태다(`qa_v7.py` 코드 + `docs/` 문서) — 지금은 한 군이고,
그쪽에서 같은 글자 충돌이 나면 같은 방식으로 가른다.

### 상호 목격자 — 절반만 닫힌다 (2026-08-31)

`evidence-evaluator` 소관 세션이 자기 저장소에 목격자를 걸었다(커밋 `8520567`,
`tests/test_failure_code_letters_are_pinned.py`). **글자만이 아니라 코드까지** 고정한다 —
우리가 인용하는 것은 `X1` 이지 `X` 가 아니고, 글자만 보면 `R1` 을 지우고 `R9` 를 더해도
통과하기 때문이다. 독 4종(글자 추가·코드 교체·뜻 비움·글자 삭제)으로 발동을 확인했고,
**주입마다 파일 해시가 실제로 바뀌었는지도** 봤다(우리 세션의 뮤테이션 도구 결함 보고가
그쪽 검증 절차를 바꿨다).

**닫힌 절반**: `ev-eval` 의 `FAILURE_CODES` 글자·코드가 말없이 바뀌는 일은 없다.
**안 닫힌 절반**: 우리 등록부의 변경을 그쪽이 아는 길은 없다 — 한쪽이 상대를 import 해야
풀리는데 그쪽 `SEMANTIC_BOUNDARY` 가 그 방향 의존을 경계한다. **어느 절반인지 여기 적는다.**

그쪽 목격자에 가드가 하나 더 있다 — **회고 `I` 계열이 `I1` 까지 내려오면 실패**한다.
그날 아래 `I@ev-eval` 두 행을 충돌로 승격해야 한다.

## 계열

| 글자 | 문서군 | 뜻 | 개념 | 영문 (유형) | 정의 위치 | 발행 형식 (표 첫 셀 내부 — 게이트가 `^\| … \|` 골격을 붙인다) | FQN (인용 접두) | 상태 |
|---|---|---|---|---|---|---|---|---|
| `G` | `retro` | 이슈(발견된 결함) G1~G170(**정의** 수; 언급은 548건 — 두 숫자를 섞지 마라). 판정문·ev-eval 은 인용만 — `G32` 를 회고가 제기하고 판정 §6 이 "통일하지 않는다"로 답한 것이 증거 | `문제` | — (arbitrary) | `docs/H1A_PROBLEM_ANALYSIS.md:165` | `\*{0,2}G(\d+)(?:\s[^*]*)?\*{0,2}` | `retro:G` | `OWNER` |
| `G` | `rulings` | 회고 G 를 인용 | `(인용)` | (인용) | — | — | `retro:G` | `CITES_ONLY` |
| `P` | `retro` | 패턴(반복되는 실패 형태) P1~P26. 정의는 표 첫 셀 `**P<n>**` 단독, 뒤 절 누계표는 `**P<n>**(설명)` 으로 **재기술** — 재기술만 있고 정의가 없으면 발행 아님(게이트 검사) | `패턴` | Pattern (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:536` | `\*{0,2}P(\d+)\*{0,2}(?:\([^)]*\))?` | `retro:P` | `COLLIDES` |
| `P` | `directive` | 구현 단계 P0~P4 (P0 architecture integrity · P4 oracle evaluation) | `단계` | Phase (initial) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:1940` | — (verbatim, 형식 미강제) | `directive:P` | `COLLIDES` |
| `P` | `vault-tool` | 권위 등급 `P0-active-experiment` · `P2-path-stable-worktree` | `등급` | Priority (initial) | — | — | `vault-tool:P` | `EXTERNAL` |
| `P` | `ev-eval` | 회고 P 를 인용(`P24` 3회, 같은 뜻) + 자체 권위 등급 P0/P1/P2 | `등급` | Priority (initial) | — | — | `ev-eval:P` | `EXTERNAL` |
| `I` | `directive` | 권한 경계 불변식 I1~I11 (I3 = Verify 는 graph 를 쓰지 않는다) | `불변식` | Invariant (initial) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:147` | — (verbatim) | `directive:I` | `COLLIDES` |
| `I` | `mechspec` | 상태·갱신 허용성 불변식 I1~I7 (I3 = verified-region protection · I7 = safe abstention) | `불변식` | Invariant (initial) | — | — | `mechspec:I` | `EXTERNAL` |
| `I` | `ev-eval` | 이슈 번호 **I136~I231**(86개, 우리 `G` 와 같은 역할·append-only). **같은 저장소 안에서 `I1` 실패 코드와 공존** — 번호대가 안 겹쳐 아직 사고가 없을 뿐이다 | `문제` | Issue (initial) | — | — | `ev-eval:I` | `EXTERNAL` |
| `M` | `retro` | 검증 방법 M1~M19 (M8 = 전문 재독) | `검증` | Method (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:222` | `\*{0,2}M(\d+)\*{0,2}` | `retro:M` | `COLLIDES` |
| `M` | `roadmap` | 마일스톤 M0~M3 | `단계` | Milestone (initial) | `docs/obligation_layer_roadmap.md:28` | — | `roadmap:M` | `COLLIDES` |
| `M` | `rulings` | D-19 능력 축 M1~M3 (Measurement · Semantic compilation · Certification) | `등급` | Measurement axis (initial) | `docs/DESIGN_DECISION_e2e_v1_experiment_design.md:129` | — (verbatim) | `rulings:M` | `COLLIDES` |
| `W` | `retro` | 워크스페이스 이슈 W1~W7 (W1 = 브랜치 5/77 갈라짐) | `문제` | Workspace (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:188` | `\*{0,2}W(\d+)\*{0,2}` | `retro:W` | `COLLIDES` |
| `W` | `rulings` | refine_verify 리뷰 항목 W1~W5 (W1 = E2E 가 MCP 배선 미증명 · W5 = laundering BLOCKER) | `문제` | — (arbitrary) | `docs/DESIGN_DECISION_refine_verify_v0_review.md:1` | — (verbatim) | `rulings:W` | `COLLIDES` |
| `R` | `retro` | 렌더·실측 이슈 R1~R4 (R1 = 동결 rendered_prompts 드리프트) | `문제` | Render (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:456` | `\*{0,2}R(\d+)\*{0,2}` | `retro:R` | `COLLIDES` |
| `R` | `directive` | 오라클 참조 문헌 R1~ (R1 = Bentzen S5) | `출처` | Reference (initial) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:79` | — (verbatim) | `directive:R` | `COLLIDES` |
| `R` | `rulings` | Q36 요건 R1~R4 (R2 = 독립 검증 가능성) | `요건` | Requirement (initial) | `docs/DESIGN_REQUEST_independent_verifiability_constraint.md:46` | — | `rulings:R` | `COLLIDES` |
| `V` | `retro` | 동결 버전 V1~V5 (V5 = 투영 전용 개정) | `버전` | Version (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:1396` | — (산문·표 혼재, 형식 미고정) | `retro:V` | `COLLIDES` |
| `V` | `directive` | 저장 전 검증 항목 V1~V5 | `검증` | Verification (initial) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:36` | — | `directive:V` | `COLLIDES` |
| `V` | `rulings` | **판정문 수신 검증 항목** V1~V6 — 판정문마다 독립 발행(15+ 문서, 87행). 회고 V(동결 버전)·DIRECTIVE V(저장 전 검증)와 셋째 뜻. **게이트 인벤토리 검사가 적발** | `검증` | Verification (initial) | `docs/DESIGN_DECISION_e2e_v1_experiment_design.md:19` | — (판정문마다 표 형식 상이) | `rulings:V` | `COLLIDES` |
| `E` | `rulings` | 회고 E 인용 (`Q31.2 E13` 꼴) | `(인용)` | (인용) | — | — | `retro:E` | `CITES_ONLY` |
| `L` | `rulings` | D-36·D-37 원문의 삼층 L1/L2/L3 — verbatim 인용 | `(인용)` | (인용) | — | — | `retro:L` | `CITES_ONLY` |
| `P` | `rulings` | DIRECTIVE Phase 인용 (`P1 legacy E2E`) | `(인용)` | (인용) | — | — | `directive:P` | `CITES_ONLY` |
| `B` | `rulings` | D-35 적대검증 finding B1~B4 | `문제` | — (ordinal) | `docs/DESIGN_DECISION_annotation_layer_admissibility.md:528` | — | `rulings:B` | `COLLIDES` |
| `B` | `ev-eval` | MCP 테스트 케이스 B1~B7 | `검증` | Backlinks (initial) | — | — | `ev-eval:B` | `EXTERNAL` |
| `C` | `retro` | 측정 감사 항목 C1~C7 | `검증` | Check (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:1224` | — | `retro:C` | `COLLIDES` |
| `C` | `rulings` | D-36 검증 항목 C1~C3 | `검증` | — (ordinal) | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:640` | — | `rulings:C` | `COLLIDES` |
| `C` | `ev-eval` | 회수 테스트 C1~C5 | `검증` | Case (initial) | — | — | `ev-eval:C` | `EXTERNAL` |
| `D` | `directive` | 공백 항목 D1~D8 (D2 = fingerprint primitive) | `규칙` | Delta (initial) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:46` | — | `directive:D` | `COLLIDES` |
| `D` | `retro` | trial 계획 D0~D3 | `규칙` | — (arbitrary) | `docs/H1A_PROBLEM_ANALYSIS.md:199` | — | `retro:D` | `COLLIDES` |
| `D` | `rulings` | D-36 검증 항목 D1~D4 · **판정 ID `D-19`~`D-37`은 하이픈이 있어 별개** | `검증` | — (ordinal) | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:727` | — | `rulings:D` | `COLLIDES` |
| `D` | `ev-eval` | 결함 D1a/D1b | `문제` | Defect (initial) | — | — | `ev-eval:D` | `EXTERNAL` |
| `F` | `retro` | 레드팀 finding F1~F8 | `문제` | Finding (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:1927` | — | `retro:F` | `COLLIDES` |
| `F` | `rulings` | D-36 검증 F1~F3 | `검증` | — (ordinal) | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:736` | — | `rulings:F` | `COLLIDES` |
| `F` | `ev-eval` | 결함 F1~F7 | `문제` | Finding (initial) | — | — | `ev-eval:F` | `EXTERNAL` |
| `Q` | `rulings` | 외부 판정 질문 Q1~Q37 — 유일 발행자 | `요건` | Question (initial) | `docs/RULING_CHAIN_INDEX.md:49` | — | `rulings:Q` | `OWNER` |
| `Q` | `retro` | rulings Q 인용 | `(인용)` | (인용) | — | — | `rulings:Q` | `CITES_ONLY` |
| `O` | `directive` | 오라클 슬롯 O1~O3 (동반 yaml `semantic_oracle_set_handoff_v0.1.yaml`) | `출처` | Oracle (initial) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:75` | — | `directive:O` | `OWNER` |
| `O` | `rulings` | directive O 인용 | `(인용)` | (인용) | — | — | `directive:O` | `CITES_ONLY` |
| `E` | `retro` | 배제 규칙 E0~E15 — roadmap·rulings 는 같은 측정 영역으로 인용 | `규칙` | Exclusion (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:1984` | — | `retro:E` | `OWNER` |
| `E` | `roadmap` | 회고 E 인용 | `(인용)` | (인용) | — | — | `retro:E` | `CITES_ONLY` |
| `L` | `retro` | 단일 소유 (drill-down 레벨 L0~L2) | `등급` | Level (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:1423` | — | `retro:L` | `OWNER` |
| `S` | `mechspec` | 기제 슬롯 S1~S14 (atp-v4) — 단일 소유 | `등급` | Slot (initial) | — | — | `mechspec:S` | `EXTERNAL` |
| `I` | `ev-eval-code` | `FAILURE_CODES` I1 — 해석 주장 미근거 — **회고 I136~I231 과 같은 저장소 안 순방향 충돌** | `문제` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:I` | `EXTERNAL` |
| `D` | `ev-eval-code` | `FAILURE_CODES` D0 — 실패 코드 (동료 세션이 내 삼중항 누락을 정정, 2026-08-31) | `문제` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:D` | `EXTERNAL` |
| `R` | `ev-eval-code` | `FAILURE_CODES` R1 R2 — 실패 코드 | `문제` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:R` | `EXTERNAL` |
| `A` | `ev-eval-code` | `FAILURE_CODES` A1 — 실패 코드 | `문제` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:A` | `EXTERNAL` |
| `S` | `ev-eval-code` | `FAILURE_CODES` S1 — 실패 코드 | `문제` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:S` | `EXTERNAL` |
| `T` | `ev-eval-code` | `FAILURE_CODES` T1 — 실패 코드 | `문제` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:T` | `EXTERNAL` |
| `E` | `ev-eval-code` | `FAILURE_CODES` E0 E1 — 실패 코드 | `문제` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:E` | `EXTERNAL` |
| `V` | `ev-eval-code` | `FAILURE_CODES` V1 — 실패 코드 | `검증` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:V` | `EXTERNAL` |
| `C` | `ev-eval-code` | `FAILURE_CODES` C1~C4 — 실패 코드 | `검증` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval-code:C` | `EXTERNAL` |
| `X` | `ev-eval` | 실패 코드 `X1: citation outside exposed context` | `문제` | — (arbitrary) | `evidence_evaluator/contract.py` | — | `ev-eval:X` | `EXTERNAL` |
| `H` | `experiments` | **가설·실험 이름** `H1`·`H2`·`H3`(`# 설계 판정 요청 — H3 확증 실험의 estimand`)·`H1a`. 계열이 아니다 | `(인용)` | — (arbitrary) | `experiments/2026-07-25_e2.4_repo_grounded_contract_transfer/DESIGN_REQUEST_H3.md` | — | — | `FP_EXPERIMENT` |
| `X` | `h1a-scope` | mermaid 노드 id (`X1["버림"]`) — 그림 문법 | `(인용)` | — (arbitrary) | `docs/feedback/design_review_*_round2.md` | — | `h1a-scope:X` | `FP_DIAGRAM` |
| `N` | `h1a-scope` | 검사 항목 `N1 Scior TSV에서 RA02 로드` | `검증` | — (arbitrary) | `qa_v7.py` | — | `h1a-scope:N` | `EXTERNAL` |
| `I` | `h1a-scope` | 검사 항목 `I1. STRUCTURAL은 비-essential`… I1~I7, `R.check` 이름으로 발행 — **directive I1~I11·mechspec I1~I7 과 교집합 구간(I1~I7) 순방향 충돌, 발행자 셋째** | `검증` | — (arbitrary) | `qa_v7.py:495` | — | `h1a-scope:I` | `EXTERNAL` |
| `K` | `h1a-scope` | 규칙 `K1. STRUCTURAL 부분이 개념으로 존재 → ∃has_part ESSENTIAL 파생` | `규칙` | — (arbitrary) | `qa_v7.py` | — | `h1a-scope:K` | `EXTERNAL` |
| `J` | `h1a-scope` | 규칙 `J1. 반대칭: A has B + B has A → ERROR` | `규칙` | — (arbitrary) | `qa_v7.py` | — | `h1a-scope:J` | `EXTERNAL` |
| `Z` | `retro` | 다이어그램 줌 Z0~Z3 — 단일 소유 | `등급` | Zoom (initial) | `docs/H1A_PROBLEM_ANALYSIS.md:2933` | — | `retro:Z` | `OWNER` |

## 이 등록부가 확인하지 않은 것

- `M@mechspec` 은 **계열이 아니다** — `mechanism_spec.md:86-89` 의 `M1[Pass] M2[Syntax failure]` 는 mermaid 다이어그램 노드 ID 다. 제외했다(M 은 4중 → **3중**).
- **회고 G 의 발행 형식은 시간에 따라 바뀌었다** — G1~G8 은 `| G1 |`(굵기 없음), 이후는 `| **G9** |`, 일부는 `| **G66 BLOCKER** |`. 형식을 하나로 강제하면 초기 24개가 위반이 되므로 정규식을 관행에 맞춰 넓혔다(굵기 선택·수식어 허용). **표 첫 셀**이라는 핵심은 유지한다 — G164 산문·P25 괄호형이 그것을 벗어난 것이었다.
- **발행 형식이 적힌 계열은 다섯**(G·P·M·W·R 의 retro 행)이다. 나머지 OWNER/COLLIDES 행은
  형식이 `—` 이고 게이트의 형식 검사에서 제외된다 — verbatim 문서는 우리가 형식을
  정할 수 없고, 나머지는 발행이 표와 산문에 혼재해 아직 하나로 고정하지 못했다.
- `EXTERNAL` 행의 정의 위치는 게이트가 검증하지 않는다. 낡을 수 있다.
- **범위 정정 (2026-08-31)**: 위 A~Z 전수는 **`concept-gate-h1-wt/docs` 의 6 문서군에만**
  돌린 것이다. 넓힌 실측에서 이 문서가 "쓰이지 않는다"고 적었던 넷 중 셋이 실재했다:

  | 글자 | 넓힌 범위 실측 | 정체 |
  |---|---:|---|
  | `H` | **354** (notes 261 · experiments 90) | H1a·H3 — **실험 이름**, 계열 아님(위양성) |
  | `T` | **346** (ev-eval 230 · vault-backlinks 102) | `contract.py:60` 의 `"T1": "answer without a reproducible authority-read…"` — **실재 계열**(코드 안 dict 키) |
  | `A` | 29 | `§A9`·`A2. 의미보존 압축` — 문서 절 번호. 계열 경계 |
  | `U` | 2 | `FOLIO U2+E1` — 산발 |

  즉 **`T` 는 진짜 누락**이고 나머지 셋은 위양성이었다. `T` 는 `ev-eval`·`vault-backlinks-mcp`
  소관이라 이 등록부에는 `EXTERNAL` 로만 들어갈 수 있다.
- **아직 등재되지 않은 문서군이 둘 있다** — `h1-wt/experiments`(md 1,932 식별자·19글자,
  `Q785 L216 M204 R130 V120`)와 `h1-wt/experiments` 코드(809·15글자). 이 등록부의
  문서군 표에 없으므로 게이트의 인벤토리 검사도 그곳을 보지 않는다.
- **동료 세션(`evidence-evaluator` 소관)이 내 계수를 반박했고 절반 맞았다** — 그쪽 214 대
  내 652. 반증 가능한 예측("사본이 원인이면 T 126→약 44")으로 검정: 워크트리 사본 제외 시
  **652→330 · T 126→63**. 사본은 원인의 **절반**이고, 나머지는 **이중 계수**였다 —
  `evidence-evaluator/vault-backlinks-mcp`(150건)를 최상위에서 **또 한 번**(137건) 셌다.
- **정의 수와 언급 수는 다른 숫자다.** `FAILURE_CODES` 의 `T` 는 **정의 1개·언급 62건**이고,
  `retro:G` 는 **정의 170개·언급 548건**이다. 이 등록부의 "G1~G164" 는 정의였고 광역 측정의
  "639" 는 언급이었는데 **라벨이 없어 같은 표에서 섞였다.** 재번호 비용은 언급이, 계열 크기는
  정의가 정한다.
- **동료 세션이 등록부 밖 계열 넷을 찾았고 독립 재현됐다** (2026-08-31). 방법이 핵심이다 —
  **내용 SHA-256 dedup 먼저**(문서 사본이 3배 부풀린다), 그 다음 등록부 글자 집합과 **차집합**,
  마지막에 **사람이 실물 확인**(이 단계를 빼면 `H` 같은 위양성이 그대로 들어간다).
  정본 4,377개에서: **X 64 · N 50 · K 37 · J 35.**
  X 는 **저장소를 가로지르는 순방향 충돌** — `ev-eval:X1`(실패 코드) 대 `h1a-scope:X1`(mermaid
  노드). 후자는 그림 문법이라 사람은 식별자로 안 읽지만 **인벤토리는 구별하지 못한다.**
  N·K·J 는 `concept-gate-h1a-scope-wt/qa_v7.py` — **세 번째 미등재 문서군**이고 코드와 문서가
  같은 계열을 양쪽에서 발행한다.
- **위양성 유형을 상태 어휘에 넣었다** (`FP_DIAGRAM`·`FP_SECTION`·`FP_EXPERIMENT`). 전에는
  그 판단이 내 머릿속에만 있어 다음 전수 조사가 같은 판정을 다시 해야 했다.
- **코드도 계열을 쓴다.** `evidence-evaluator` 코드 652건(T126 C116 E116 Z102),
  `vault-backlinks-mcp` 137건(Z51 T50). "코드는 점 이름공간이라 이 문제가 없다"는
  `cg_obligations.py` 한 파일에서만 참이다 — `conceptgate/` 의 P72 는 주석 안
  **회고 패턴 인용**이고 발행은 아니다.
- haiku 감사 2축의 판정(COLLIDES/CITES_ONLY)은 lead 가 **표본만** 재실측했다
  (W1 · O 소유 · M 다섯째 계열 기각 · I 범위 136~231). 나머지는 회신 그대로다.
