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

**인용 규약**: 계열이 모호한 자리에서는 아래 표의 "인용 접두"를 쓴다. 자기 문서군
안에서 자기 계열을 쓸 때는 접두가 필요 없다.

## 문서군

| 이름 | 경로 | 저장소 안 |
|---|---|---|
| `retro` | `docs/H1A_PROBLEM_ANALYSIS.md` | ✅ | `미분류` |
| `rulings` | `docs/DESIGN_DECISION_*.md` · `docs/DESIGN_REQUEST_*.md` | ✅ | `미분류` |
| `directive` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md` (+ 동반 yaml) | ✅ — **외부 설계 원문, verbatim** | `미분류` |
| `roadmap` | `docs/obligation_layer_roadmap.md` | ✅ | `미분류` |
| `mechspec` | `../notes/research/logical-revision/*.md` | ❌ vault, git 미추적 | `미분류` |
| `ev-eval` | `../evidence-evaluator/docs/**/*.md` | ❌ 다른 저장소 | `미분류` |
| `vault-tool` | `vault_search` 가 붙이는 `authority_class` | ❌ 도구 산출 | `미분류` |

## 상태

| status | 뜻 |
|---|---|
| `OWNER` | 이 문서군이 이 글자의 계열을 **발행**한다. 발행 형식이 게이트로 강제된다 || `미분류` 
| `CITES_ONLY` | 이 문서군은 이 글자를 발행하지 않고 다른 OWNER 의 번호를 **같은 뜻으로** 인용만 한다 || `미분류` 
| `COLLIDES` | 이 문서군이 이 글자를 발행하는데 **다른 문서군도 같은 글자를 다른 뜻으로** 발행한다 || `미분류` 
| `EXTERNAL` | 저장소 밖 문서군의 발행. 게이트가 읽지 못하므로 기록만 한다 || `미분류` 

## 개념 — 뜻 → 글자 (역방향)

같은 것이 문서군마다 다른 글자로 불린다. 순방향 충돌(한 글자 여러 뜻)은 독자가
오독하게 하고, 역방향 중복(한 뜻 여러 글자)은 **검색·집계를 불가능하게** 한다 —
"저장소 전체 결함이 몇 개인가"에 답하려면 여덟 계열을 합쳐야 하고 합산 규칙은 없다.

| 개념 | 글자 | 뜻 |
|---|---|---|
| `문제` | **B D F G I R W** | 발견된 결함·이슈·finding·BLOCKER |
| `검증` | **B C D F M V** | 검증 항목·방법·테스트 케이스·수신 검증 |
| `등급` | **L M P S Z** | 권위 등급·레벨·줌·슬롯·능력 축 |
| `규칙` | D E | 배제 규칙·공백 항목·trial 계획 |
| `단계` | M P | 구현 단계·마일스톤 |
| `불변식` | I | 두 설계 문서의 불변식 (내용 상이) |
| `출처` | O R | 오라클 슬롯·참조 문헌 |
| `요건` | Q R | 외부 판정 질문·Q36 요건 |
| `버전` | V | 동결 버전 |
| `패턴` | P | 반복 실패 형태 — **역방향에서는 중복 없음** |
| `(인용)` | — | CITES_ONLY 행 — 개념을 새로 만들지 않는다 |

### 정규화 — 고빈도를 표준으로, 저빈도를 바꾼다 (사용자 제안, 2026-08-31)

실측(등장 횟수, 코드블록 제외):

| 개념 | 고정(외부·verbatim) 최빈 | 우리 소유 최대 | 판정 |
|---|---|---|---|
| 문제 | `I@ev-eval` 230 | **`G@retro` 547·164개** | 우리가 2.4배 크다 — 표준을 따르면 **큰 것을 작은 것에 맞춰 재번호**. 하지 않는다 |
| 검증 | `V@rulings` 287 | `M@retro` 124 | 고정이 크다 — **유일한 정당 후보.** 단 M1~M19 인용 124회 재작성 비용 |
| 등급 | `S@mechspec` 65 | `L@retro` 13 | 후보이나 L0~L2 는 drill-down 레벨, S 는 기제 슬롯 — **같은 개념이 아닐 수 있다** |
| 규칙 | `D@directive` 7 | `E@retro` 41 | 우리가 6배 크다. 하지 않는다 |
| 단계 | `P@directive` 7 | `M@roadmap` 20 | 우리가 3배 크다. 하지 않는다 |

**"상대치라 복잡하다"가 맞다.** 단순 최빈은 세 개념에서 **큰 계열을 작은 계열에 맞추라**고
한다 — 우리가 바꿀 수 있는 쪽이 대개 더 크기 때문이다. 정당한 규칙은
**고정 계열 중 최빈 ∧ 우리 계열보다 크다**이고, 그 조건에서 후보는 `검증` 하나다.
그것도 재번호 비용(124회)과 이득(집계 가능)을 비교해야 하며, 이 등록부는 결정하지
않고 기록한다. **개념 열을 통한 집계는 재번호 없이도 가능하다** — 그것이 이 표의 용도다.

## 계열

| 글자 | 문서군 | 뜻 | 개념 | 정의 위치 | 발행 형식 (표 첫 셀 내부 — 게이트가 `^\| … \|` 골격을 붙인다) | 인용 접두 | 상태 |
|---|---|---|---|---|---|---|---|
| `G` | `retro` | 이슈(발견된 결함) G1~G164. 판정문·ev-eval 은 인용만 — `G32` 를 회고가 제기하고 판정 §6 이 "통일하지 않는다"로 답한 것이 증거 | `문제` | `docs/H1A_PROBLEM_ANALYSIS.md:165` | `\*{0,2}G(\d+)(?:\s[^*]*)?\*{0,2}` | `회고 G` | `OWNER` |
| `G` | `rulings` | 회고 G 를 인용 | `(인용)` | — | — | `회고 G` | `CITES_ONLY` |
| `P` | `retro` | 패턴(반복되는 실패 형태) P1~P26. 정의는 표 첫 셀 `**P<n>**` 단독, 뒤 절 누계표는 `**P<n>**(설명)` 으로 **재기술** — 재기술만 있고 정의가 없으면 발행 아님(게이트 검사) | `패턴` | `docs/H1A_PROBLEM_ANALYSIS.md:536` | `\*{0,2}P(\d+)\*{0,2}(?:\([^)]*\))?` | `회고 P` | `COLLIDES` |
| `P` | `directive` | 구현 단계 P0~P4 (P0 architecture integrity · P4 oracle evaluation) | `단계` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:1940` | — (verbatim, 형식 미강제) | `DIRECTIVE Phase` | `COLLIDES` |
| `P` | `vault-tool` | 권위 등급 `P0-active-experiment` · `P2-path-stable-worktree` | `등급` | — | — | `vault 등급 P` | `EXTERNAL` |
| `P` | `ev-eval` | 회고 P 를 인용(`P24` 3회, 같은 뜻) + 자체 권위 등급 P0/P1/P2 | `등급` | — | — | `ev-eval P` | `EXTERNAL` |
| `I` | `directive` | 권한 경계 불변식 I1~I11 (I3 = Verify 는 graph 를 쓰지 않는다) | `불변식` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:147` | — (verbatim) | `D-I` | `COLLIDES` |
| `I` | `mechspec` | 상태·갱신 허용성 불변식 I1~I7 (I3 = verified-region protection · I7 = safe abstention) | `불변식` | — | — | `M-I` | `EXTERNAL` |
| `I` | `ev-eval` | 이슈 번호 I136~I231 (우리 `G` 와 같은 역할, append-only) | `문제` | — | — | `ev-eval I` | `EXTERNAL` |
| `M` | `retro` | 검증 방법 M1~M19 (M8 = 전문 재독) | `검증` | `docs/H1A_PROBLEM_ANALYSIS.md:222` | `\*{0,2}M(\d+)\*{0,2}` | `회고 M` | `COLLIDES` |
| `M` | `roadmap` | 마일스톤 M0~M3 | `단계` | `docs/obligation_layer_roadmap.md:28` | — | `roadmap M` | `COLLIDES` |
| `M` | `rulings` | D-19 능력 축 M1~M3 (Measurement · Semantic compilation · Certification) | `등급` | `docs/DESIGN_DECISION_e2e_v1_experiment_design.md:129` | — (verbatim) | `D-19 M` | `COLLIDES` |
| `W` | `retro` | 워크스페이스 이슈 W1~W7 (W1 = 브랜치 5/77 갈라짐) | `문제` | `docs/H1A_PROBLEM_ANALYSIS.md:188` | `\*{0,2}W(\d+)\*{0,2}` | `회고 W` | `COLLIDES` |
| `W` | `rulings` | refine_verify 리뷰 항목 W1~W5 (W1 = E2E 가 MCP 배선 미증명 · W5 = laundering BLOCKER) | `문제` | `docs/DESIGN_DECISION_refine_verify_v0_review.md:1` | — (verbatim) | `v0-review W` | `COLLIDES` |
| `R` | `retro` | 렌더·실측 이슈 R1~R4 (R1 = 동결 rendered_prompts 드리프트) | `문제` | `docs/H1A_PROBLEM_ANALYSIS.md:456` | `\*{0,2}R(\d+)\*{0,2}` | `회고 R` | `COLLIDES` |
| `R` | `directive` | 오라클 참조 문헌 R1~ (R1 = Bentzen S5) | `출처` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:79` | — (verbatim) | `oracle R` | `COLLIDES` |
| `R` | `rulings` | Q36 요건 R1~R4 (R2 = 독립 검증 가능성) | `요건` | `docs/DESIGN_REQUEST_independent_verifiability_constraint.md:46` | — | `Q36 R` | `COLLIDES` |
| `V` | `retro` | 동결 버전 V1~V5 (V5 = 투영 전용 개정) | `버전` | `docs/H1A_PROBLEM_ANALYSIS.md:1396` | — (산문·표 혼재, 형식 미고정) | `동결 V` | `COLLIDES` |
| `V` | `directive` | 저장 전 검증 항목 V1~V5 | `검증` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:36` | — | `DIRECTIVE 검증 V` | `COLLIDES` |
| `V` | `rulings` | **판정문 수신 검증 항목** V1~V6 — 판정문마다 독립 발행(15+ 문서, 87행). 회고 V(동결 버전)·DIRECTIVE V(저장 전 검증)와 셋째 뜻. **게이트 인벤토리 검사가 적발** | `검증` | `docs/DESIGN_DECISION_e2e_v1_experiment_design.md:19` | — (판정문마다 표 형식 상이) | `D-<n> 검증 V` | `COLLIDES` |
| `E` | `rulings` | 회고 E 인용 (`Q31.2 E13` 꼴) | `(인용)` | — | — | (불필요) | `CITES_ONLY` |
| `L` | `rulings` | D-36·D-37 원문의 삼층 L1/L2/L3 — verbatim 인용 | `(인용)` | — | — | `D-36 L` | `CITES_ONLY` |
| `P` | `rulings` | DIRECTIVE Phase 인용 (`P1 legacy E2E`) | `(인용)` | — | — | `DIRECTIVE Phase` | `CITES_ONLY` |
| `B` | `rulings` | D-35 적대검증 finding B1~B4 | `문제` | `docs/DESIGN_DECISION_annotation_layer_admissibility.md:528` | — | `D-35 B` | `COLLIDES` |
| `B` | `ev-eval` | MCP 테스트 케이스 B1~B7 | `검증` | — | — | `ev-eval B` | `EXTERNAL` |
| `C` | `retro` | 측정 감사 항목 C1~C7 | `검증` | `docs/H1A_PROBLEM_ANALYSIS.md:1224` | — | `회고 C` | `COLLIDES` |
| `C` | `rulings` | D-36 검증 항목 C1~C3 | `검증` | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:640` | — | `D-36 C` | `COLLIDES` |
| `C` | `ev-eval` | 회수 테스트 C1~C5 | `검증` | — | — | `ev-eval C` | `EXTERNAL` |
| `D` | `directive` | 공백 항목 D1~D8 (D2 = fingerprint primitive) | `규칙` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:46` | — | `gap D` | `COLLIDES` |
| `D` | `retro` | trial 계획 D0~D3 | `규칙` | `docs/H1A_PROBLEM_ANALYSIS.md:199` | — | `회고 D` | `COLLIDES` |
| `D` | `rulings` | D-36 검증 항목 D1~D4 · **판정 ID `D-19`~`D-37`은 하이픈이 있어 별개** | `검증` | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:727` | — | `D-36 D` | `COLLIDES` |
| `D` | `ev-eval` | 결함 D1a/D1b | `문제` | — | — | `ev-eval D` | `EXTERNAL` |
| `F` | `retro` | 레드팀 finding F1~F8 | `문제` | `docs/H1A_PROBLEM_ANALYSIS.md:1927` | — | `회고 F` | `COLLIDES` |
| `F` | `rulings` | D-36 검증 F1~F3 | `검증` | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:736` | — | `D-36 F` | `COLLIDES` |
| `F` | `ev-eval` | 결함 F1~F7 | `문제` | — | — | `ev-eval F` | `EXTERNAL` |
| `Q` | `rulings` | 외부 판정 질문 Q1~Q37 — 유일 발행자 | `요건` | `docs/RULING_CHAIN_INDEX.md:49` | — | (불필요) | `OWNER` |
| `Q` | `retro` | rulings Q 인용 | `(인용)` | — | — | (불필요) | `CITES_ONLY` |
| `O` | `directive` | 오라클 슬롯 O1~O3 (동반 yaml `semantic_oracle_set_handoff_v0.1.yaml`) | `출처` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:75` | — | (불필요) | `OWNER` |
| `O` | `rulings` | directive O 인용 | `(인용)` | — | — | (불필요) | `CITES_ONLY` |
| `E` | `retro` | 배제 규칙 E0~E15 — roadmap·rulings 는 같은 측정 영역으로 인용 | `규칙` | `docs/H1A_PROBLEM_ANALYSIS.md:1984` | — | (불필요) | `OWNER` |
| `E` | `roadmap` | 회고 E 인용 | `(인용)` | — | — | (불필요) | `CITES_ONLY` |
| `L` | `retro` | 단일 소유 (drill-down 레벨 L0~L2) | `등급` | `docs/H1A_PROBLEM_ANALYSIS.md:1423` | — | (불필요) | `OWNER` |
| `S` | `mechspec` | 기제 슬롯 S1~S14 (atp-v4) — 단일 소유 | `등급` | — | — | (불필요) | `EXTERNAL` |
| `Z` | `retro` | 다이어그램 줌 Z0~Z3 — 단일 소유 | `등급` | `docs/H1A_PROBLEM_ANALYSIS.md:2933` | — | (불필요) | `OWNER` |

## 이 등록부가 확인하지 않은 것

- `M@mechspec` 은 **계열이 아니다** — `mechanism_spec.md:86-89` 의 `M1[Pass] M2[Syntax failure]` 는 mermaid 다이어그램 노드 ID 다. 제외했다(M 은 4중 → **3중**).
- **회고 G 의 발행 형식은 시간에 따라 바뀌었다** — G1~G8 은 `| G1 |`(굵기 없음), 이후는 `| **G9** |`, 일부는 `| **G66 BLOCKER** |`. 형식을 하나로 강제하면 초기 24개가 위반이 되므로 정규식을 관행에 맞춰 넓혔다(굵기 선택·수식어 허용). **표 첫 셀**이라는 핵심은 유지한다 — G164 산문·P25 괄호형이 그것을 벗어난 것이었다.
- **발행 형식이 적힌 계열은 다섯**(G·P·M·W·R 의 retro 행)이다. 나머지 OWNER/COLLIDES 행은
  형식이 `—` 이고 게이트의 형식 검사에서 제외된다 — verbatim 문서는 우리가 형식을
  정할 수 없고, 나머지는 발행이 표와 산문에 혼재해 아직 하나로 고정하지 못했다.
- `EXTERNAL` 행의 정의 위치는 게이트가 검증하지 않는다. 낡을 수 있다.
- A~Z 중 **A·H·T·U** 는 어느 문서군에서도 계열로 쓰이지 않아 등재하지 않았다.
  N·J·K·X·Y 도 같다. 새로 쓰기 시작하면 인벤토리 검사가 잡는다.
- haiku 감사 2축의 판정(COLLIDES/CITES_ONLY)은 lead 가 **표본만** 재실측했다
  (W1 · O 소유 · M 다섯째 계열 기각 · I 범위 136~231). 나머지는 회신 그대로다.
