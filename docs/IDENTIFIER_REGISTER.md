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
| `retro` | `docs/H1A_PROBLEM_ANALYSIS.md` | ✅ |
| `rulings` | `docs/DESIGN_DECISION_*.md` · `docs/DESIGN_REQUEST_*.md` | ✅ |
| `directive` | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md` (+ 동반 yaml) | ✅ — **외부 설계 원문, verbatim** |
| `roadmap` | `docs/obligation_layer_roadmap.md` | ✅ |
| `mechspec` | `../notes/research/logical-revision/*.md` | ❌ vault, git 미추적 |
| `ev-eval` | `../evidence-evaluator/docs/**/*.md` | ❌ 다른 저장소 |
| `vault-tool` | `vault_search` 가 붙이는 `authority_class` | ❌ 도구 산출 |

## 상태

| status | 뜻 |
|---|---|
| `OWNER` | 이 문서군이 이 글자의 계열을 **발행**한다. 발행 형식이 게이트로 강제된다 |
| `CITES_ONLY` | 이 문서군은 이 글자를 발행하지 않고 다른 OWNER 의 번호를 **같은 뜻으로** 인용만 한다 |
| `COLLIDES` | 이 문서군이 이 글자를 발행하는데 **다른 문서군도 같은 글자를 다른 뜻으로** 발행한다 |
| `EXTERNAL` | 저장소 밖 문서군의 발행. 게이트가 읽지 못하므로 기록만 한다 |

## 계열

| 글자 | 문서군 | 뜻 | 정의 위치 | 발행 형식 (표 첫 셀 내부 — 게이트가 `^\| … \|` 골격을 붙인다) | 인용 접두 | 상태 |
|---|---|---|---|---|---|---|
| `G` | `retro` | 이슈(발견된 결함) G1~G164. 판정문·ev-eval 은 인용만 — `G32` 를 회고가 제기하고 판정 §6 이 "통일하지 않는다"로 답한 것이 증거 | `docs/H1A_PROBLEM_ANALYSIS.md:165` | `\*{0,2}G(\d+)(?:\s[^*]*)?\*{0,2}` | `회고 G` | `OWNER` |
| `G` | `rulings` | 회고 G 를 인용 | — | — | `회고 G` | `CITES_ONLY` |
| `P` | `retro` | 패턴(반복되는 실패 형태) P1~P26. 정의는 표 첫 셀 `**P<n>**` 단독, 뒤 절 누계표는 `**P<n>**(설명)` 으로 **재기술** — 재기술만 있고 정의가 없으면 발행 아님(게이트 검사) | `docs/H1A_PROBLEM_ANALYSIS.md:536` | `\*{0,2}P(\d+)\*{0,2}(?:\([^)]*\))?` | `회고 P` | `COLLIDES` |
| `P` | `directive` | 구현 단계 P0~P4 (P0 architecture integrity · P4 oracle evaluation) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:1940` | — (verbatim, 형식 미강제) | `DIRECTIVE Phase` | `COLLIDES` |
| `P` | `vault-tool` | 권위 등급 `P0-active-experiment` · `P2-path-stable-worktree` | — | — | `vault 등급 P` | `EXTERNAL` |
| `P` | `ev-eval` | 회고 P 를 인용(`P24` 3회, 같은 뜻) + 자체 권위 등급 P0/P1/P2 | — | — | `ev-eval P` | `EXTERNAL` |
| `I` | `directive` | 권한 경계 불변식 I1~I11 (I3 = Verify 는 graph 를 쓰지 않는다) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:147` | — (verbatim) | `D-I` | `COLLIDES` |
| `I` | `mechspec` | 상태·갱신 허용성 불변식 I1~I7 (I3 = verified-region protection · I7 = safe abstention) | — | — | `M-I` | `EXTERNAL` |
| `I` | `ev-eval` | 이슈 번호 I136~I231 (우리 `G` 와 같은 역할, append-only) | — | — | `ev-eval I` | `EXTERNAL` |
| `M` | `retro` | 검증 방법 M1~M19 (M8 = 전문 재독) | `docs/H1A_PROBLEM_ANALYSIS.md:222` | `\*{0,2}M(\d+)\*{0,2}` | `회고 M` | `COLLIDES` |
| `M` | `roadmap` | 마일스톤 M0~M3 | `docs/obligation_layer_roadmap.md:28` | — | `roadmap M` | `COLLIDES` |
| `M` | `rulings` | D-19 능력 축 M1~M3 (Measurement · Semantic compilation · Certification) | `docs/DESIGN_DECISION_e2e_v1_experiment_design.md:129` | — (verbatim) | `D-19 M` | `COLLIDES` |
| `M` | `mechspec` | atp-v4 계열 M1~M4 | — | — | `mechspec M` | `EXTERNAL` |
| `W` | `retro` | 워크스페이스 이슈 W1~W7 (W1 = 브랜치 5/77 갈라짐) | `docs/H1A_PROBLEM_ANALYSIS.md:188` | `\*{0,2}W(\d+)\*{0,2}` | `회고 W` | `COLLIDES` |
| `W` | `rulings` | refine_verify 리뷰 항목 W1~W5 (W1 = E2E 가 MCP 배선 미증명 · W5 = laundering BLOCKER) | `docs/DESIGN_DECISION_refine_verify_v0_review.md:1` | — (verbatim) | `v0-review W` | `COLLIDES` |
| `R` | `retro` | 렌더·실측 이슈 R1~R4 (R1 = 동결 rendered_prompts 드리프트) | `docs/H1A_PROBLEM_ANALYSIS.md:456` | `\*{0,2}R(\d+)\*{0,2}` | `회고 R` | `COLLIDES` |
| `R` | `directive` | 오라클 참조 문헌 R1~ (R1 = Bentzen S5) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:79` | — (verbatim) | `oracle R` | `COLLIDES` |
| `R` | `rulings` | Q36 요건 R1~R4 (R2 = 독립 검증 가능성) | `docs/DESIGN_REQUEST_independent_verifiability_constraint.md:46` | — | `Q36 R` | `COLLIDES` |
| `V` | `retro` | 동결 버전 V1~V5 (V5 = 투영 전용 개정) | `docs/H1A_PROBLEM_ANALYSIS.md:1396` | — (산문·표 혼재, 형식 미고정) | `동결 V` | `COLLIDES` |
| `V` | `directive` | 저장 전 검증 항목 V1~V5 | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:36` | — | `DIRECTIVE 검증 V` | `COLLIDES` |
| `V` | `rulings` | **판정문 수신 검증 항목** V1~V6 — 판정문마다 독립 발행(15+ 문서, 87행). 회고 V(동결 버전)·DIRECTIVE V(저장 전 검증)와 셋째 뜻. **게이트 인벤토리 검사가 적발** | `docs/DESIGN_DECISION_e2e_v1_experiment_design.md:19` | — (판정문마다 표 형식 상이) | `D-<n> 검증 V` | `COLLIDES` |
| `E` | `rulings` | 회고 E 인용 (`Q31.2 E13` 꼴) | — | — | (불필요) | `CITES_ONLY` |
| `L` | `rulings` | D-36·D-37 원문의 삼층 L1/L2/L3 — verbatim 인용 | — | — | `D-36 L` | `CITES_ONLY` |
| `P` | `rulings` | DIRECTIVE Phase 인용 (`P1 legacy E2E`) | — | — | `DIRECTIVE Phase` | `CITES_ONLY` |
| `B` | `rulings` | D-35 적대검증 finding B1~B4 | `docs/DESIGN_DECISION_annotation_layer_admissibility.md:528` | — | `D-35 B` | `COLLIDES` |
| `B` | `ev-eval` | MCP 테스트 케이스 B1~B7 | — | — | `ev-eval B` | `EXTERNAL` |
| `C` | `retro` | 측정 감사 항목 C1~C7 | `docs/H1A_PROBLEM_ANALYSIS.md:1224` | — | `회고 C` | `COLLIDES` |
| `C` | `rulings` | D-36 검증 항목 C1~C3 | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:640` | — | `D-36 C` | `COLLIDES` |
| `C` | `ev-eval` | 회수 테스트 C1~C5 | — | — | `ev-eval C` | `EXTERNAL` |
| `D` | `directive` | 공백 항목 D1~D8 (D2 = fingerprint primitive) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:46` | — | `gap D` | `COLLIDES` |
| `D` | `retro` | trial 계획 D0~D3 | `docs/H1A_PROBLEM_ANALYSIS.md:199` | — | `회고 D` | `COLLIDES` |
| `D` | `rulings` | D-36 검증 항목 D1~D4 · **판정 ID `D-19`~`D-37`은 하이픈이 있어 별개** | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:727` | — | `D-36 D` | `COLLIDES` |
| `D` | `ev-eval` | 결함 D1a/D1b | — | — | `ev-eval D` | `EXTERNAL` |
| `F` | `retro` | 레드팀 finding F1~F8 | `docs/H1A_PROBLEM_ANALYSIS.md:1927` | — | `회고 F` | `COLLIDES` |
| `F` | `rulings` | D-36 검증 F1~F3 | `docs/DESIGN_DECISION_independent_verifiability_constraint.md:736` | — | `D-36 F` | `COLLIDES` |
| `F` | `ev-eval` | 결함 F1~F7 | — | — | `ev-eval F` | `EXTERNAL` |
| `Q` | `rulings` | 외부 판정 질문 Q1~Q37 — 유일 발행자 | `docs/RULING_CHAIN_INDEX.md:49` | — | (불필요) | `OWNER` |
| `Q` | `retro` | rulings Q 인용 | — | — | (불필요) | `CITES_ONLY` |
| `O` | `directive` | 오라클 슬롯 O1~O3 (동반 yaml `semantic_oracle_set_handoff_v0.1.yaml`) | `docs/DESIGN_DIRECTIVE_refine_verify_semantic_compilation.md:75` | — | (불필요) | `OWNER` |
| `O` | `rulings` | directive O 인용 | — | — | (불필요) | `CITES_ONLY` |
| `E` | `retro` | 배제 규칙 E0~E15 — roadmap·rulings 는 같은 측정 영역으로 인용 | `docs/H1A_PROBLEM_ANALYSIS.md:1984` | — | (불필요) | `OWNER` |
| `E` | `roadmap` | 회고 E 인용 | — | — | (불필요) | `CITES_ONLY` |
| `L` | `retro` | 단일 소유 (drill-down 레벨 L0~L2) | `docs/H1A_PROBLEM_ANALYSIS.md:1423` | — | (불필요) | `OWNER` |
| `S` | `mechspec` | 기제 슬롯 S1~S14 (atp-v4) — 단일 소유 | — | — | (불필요) | `EXTERNAL` |
| `Z` | `retro` | 다이어그램 줌 Z0~Z3 — 단일 소유 | `docs/H1A_PROBLEM_ANALYSIS.md:2933` | — | (불필요) | `OWNER` |

## 이 등록부가 확인하지 않은 것

- **회고 G 의 발행 형식은 시간에 따라 바뀌었다** — G1~G8 은 `| G1 |`(굵기 없음), 이후는 `| **G9** |`, 일부는 `| **G66 BLOCKER** |`. 형식을 하나로 강제하면 초기 24개가 위반이 되므로 정규식을 관행에 맞춰 넓혔다(굵기 선택·수식어 허용). **표 첫 셀**이라는 핵심은 유지한다 — G164 산문·P25 괄호형이 그것을 벗어난 것이었다.
- **발행 형식이 적힌 계열은 다섯**(G·P·M·W·R 의 retro 행)이다. 나머지 OWNER/COLLIDES 행은
  형식이 `—` 이고 게이트의 형식 검사에서 제외된다 — verbatim 문서는 우리가 형식을
  정할 수 없고, 나머지는 발행이 표와 산문에 혼재해 아직 하나로 고정하지 못했다.
- `EXTERNAL` 행의 정의 위치는 게이트가 검증하지 않는다. 낡을 수 있다.
- A~Z 중 **A·H·T·U** 는 어느 문서군에서도 계열로 쓰이지 않아 등재하지 않았다.
  N·J·K·X·Y 도 같다. 새로 쓰기 시작하면 인벤토리 검사가 잡는다.
- haiku 감사 2축의 판정(COLLIDES/CITES_ONLY)은 lead 가 **표본만** 재실측했다
  (W1 · O 소유 · M 다섯째 계열 기각 · I 범위 136~231). 나머지는 회신 그대로다.
