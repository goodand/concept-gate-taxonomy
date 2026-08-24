# DESIGN REQUEST — MRS fail-closed 조건·기수 관계 사상·재료 권리 (Q30)

- 상신: 2026-08-24, 운영 세션 (3차 조사 회신 수령·검증 완료 후)
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1~§2가 필요한 사실 전부다
- 차단 관계: full O1 재동결(V5)이 차단돼 있다. 본 코호트 dispatch는 **누계 0건**
- 선행 판정 D-E2E-v1-29가 승인한 설계를 **실물에 처음 적용한 결과**가 이 요청서다.
  판정이 틀렸다는 주장이 아니라, 판정이 정할 수 없었던 것(실물 형식)이 이제
  측정됐다는 보고다.

## 1. 배경 (필요한 최소한)

문장 단위 의미 컴파일 실험. subject(무도구 LLM)가 영어 문장을 IR로 컴파일하고,
oracle(외부 gold를 결정적 adapter로 IR화)과 비교해 채점한다.

**확정된 계약**:
- subject 방언 8종: `forall / exists / and / or / not / implies / pred` +
  **`count`**(기수)·**`prop`**(비례). 항은 변수·개체뿐이고 **수치는 연산자
  매개변수이지 항이 아니다**. `count = {kind, rel∈{eq,ge,le,gt,lt}, num:int,
  var, restriction, body}`, `prop = {kind, rel∈{most}, var, restriction, body}`.
  둘 다 **자체 결박자**다(EXISTS+주석이 아니다).
- 채점은 `O1ScopeMatch` — 양측을 투영(scope 구조만 남기고 라벨 어휘·사건
  의미론 비계 제거)한 signature 사이 exact structural match. `rel`·`num`은
  **채점 대상으로 유지**된다.
- O1의 선언된 semantic boundary(실물 인용): `[quantifier_scope,
  generalized_quantifier, cardinal_quantifier, proportional_quantifier,
  multi_quantifier_scope]`. 사용자 결정으로 **full O1 유지**(어느 층도 빼지 않는다).
- 적격 하한: **기수 ≥3건, 비례 ≥1건**.
- 기존 source 2종: PMB(CC-BY, Tatoeba 자막) · FOLIO(WikiLogic). 저장소는
  **공개 GitHub**이고, 사전등록·감사 기록이 그 저장소에 커밋된다.

**D-29가 정한 MRS 채택 조건(실물 인용)**:

```yaml
MRS_COUNT_PROJECTION_V1:
  require:
    quantifier_EP_present: true
    cardinal_EP_present: true
    same_bound_variable: true
    RSTR_resolved: true
    BODY_resolved: true
    numeric_CARG_parseable: true
    cardinal_relation_supported: true
  reject_if:
    - multiple_card_EP_candidates
    - card_and_quantifier_variable_disagree
    - unresolved_handle_constraint
    - numeric_scope_attachment_ambiguous
    - unsupported_numeric_relation
```

그리고 D-29는 Redwoods/MRS를 `APPROVED_SOURCE`가 아니라
`CONDITIONALLY_QUALIFIED_CANDIDATE`로 두고, 승격 전 (i) 비례 locator 확보
(ii) 실제 component/item 권리 확인 (iii) MRS→IR adapter 자격 (iv) card/prop
attachment fail-closed 자격, 그리고 적격 하한 충족을 요구했다.

**선행 판정들이 금지한 것**(같은 것을 다시 청하지 않기 위해): 사건 논리식→
참여자 논리식 **재작성**, 양화 경계를 넘는 함의 이동, 양화 재배열, 일반
정리-동치 정규화, 선언된 boundary의 **조용한 축소**, 실패가 예정된 계약의 실행.

## 2. 실측 사실 (전부 이 세션의 기계 실측)

### F1 — 재료를 공식 배포처에서 확보했다

3차 조사가 `BLOCKED`로 남긴 경로를 운영 세션이 뚫었다. 공식 SDP 접근 페이지가
다음을 진술한다(verbatim):

> "…can be made available for **direct download (Open SDP; version 1.2;
> January 2017)** under … Creative Commons Attribution-NonCommercial-ShareAlike
> license (CC BY-NC-SA 2.0). This package also includes some 'richer' meaning
> representations …, viz. **scope-underspecified logical forms (in the framework
> of Minimal Recursion Semantics; MRS)**"

실물: `osdp-12.tgz`, **397,685,740 bytes**, LINDAT/CLARIN 리포지터리
(handle `11234/1-1956`)에서 직접 다운로드 가능. 내려받아 확인한 내용:
`sdp/2015/eds/<item>.mrs` **37,066건** + 같은 수의 `.txt`(원문 문장).

### F2 — 라이선스 표기가 **세 곳에서 세 버전**이다

| 출처 | 표기 |
|---|---|
| 공식 SDP 접근 페이지 | `CC BY-NC-SA 2.0` |
| LINDAT 리포지터리 메타데이터 | `CC BY-NC-SA 4.0` |
| 패키지 내 `LICENSE.txt` | `Attribution-NonCommercial-ShareAlike 3.0 Unported` |

패키지 내 `2015/eds/README.txt`의 릴리스 이력은 배포 범위를 명시한다(verbatim):

> "[Version 1.0; October 11, 2015] + Initial release of DM background data,
> **including raw WSJ and Brown strings**."

즉 배포자는 **원문 문장까지 포함해** 이 묶음을 공개 배포하고 있다.

### F3 — 그러나 재료는 WSJ에 갇혀 있다

`2015/eds/`의 item id 접두는 **200~221만** 존재한다. 같은 README가 id 규약을
설명한다: `20102003` = "Section 01, 두 번째 문서, 세 번째 문장 of the WSJ
Corpus". 즉 이 디렉터리는 **WSJ section 00~21 전용**이고 Brown은 없다.

WSJ 원문의 권리는 별개로 확인된다 — LDC 카탈로그 실물:
"Wall Street Journal Materials, Copyright 1987, 1988, 1989 Dow Jones Inc."

### F4 — **판정 §11을 문자 그대로 적용하면 적격 기수가 0건이다**

계약 17건으로 결박한 MRS 파서를 37,066건에 적용: **37,060건 파싱**(거부 6건
= 0.016%, 전부 fail-closed, 예상 밖 예외 0). 그 위에 `MRS_COUNT_PROJECTION_V1`
을 적용한 결과:

| 항목 | 건수 |
|---|---|
| `card` 보유 record | **13,470** |
| **package 성공** | **0** |
| 거부: `multiple_card_EP_candidates` | 7,755 |
| 거부: `unresolved_handle_constraint` | 4,064 |
| 거부: `unsupported_numeric_relation` | 1,077 |
| 거부: `card_and_quantifier_variable_disagree` | 574 |

attachment 단위(변수별 단일 `card` + 정수 `CARG` + 그 변수를 결박하는 양화 1개)로
다시 세면:

| 상태 | 건수 |
|---|---|
| §11 조건 **전부** 충족 | **0** |
| **`BODY` 비제약만이 유일한 장애** | **16,584 (100.0%)** |
| `RSTR`·`BODY` 둘 다 비제약 | 3 |

원인은 결함 있는 record가 아니라 **MRS의 정상 형태**다. 실물 예(item
`21618050`, 표면 `Two ironies intrude.`):

```text
[ udef_q<0:3> LBL: h4 ARG0: x5 RSTR: h6 BODY: h7 ]
[ card<0:3>   LBL: h8 ARG0: e9 ARG1: x5 CARG: "2" ]
[ _irony_n_1<4:11> LBL: h8 ARG0: x5 ]
[ _intrude_v_1<12:20> LBL: h2 ARG0: e3 ARG1: x5 ]
HCONS: < h6 QEQ h8   h1 QEQ h2 >
```

`RSTR h6`은 `h6 QEQ h8`로 묶이지만 **`BODY h7`은 HCONS에 등장하지 않는다** —
최외곽 양화의 BODY는 scope resolution 단계에서 채워지도록 비워 둔다. 단
이 문장에서 남은 label은 `h2` 하나뿐이므로 **해소는 유일하게 결정된다**.

부수 구조 사실: `card`와 명사가 **LBL을 공유한다**(둘 다 `h8`). 즉 MRS에서
`card`는 quantifier의 **제한식 내부 술어**이고 독립 결박자가 아니다.
그리고 `card`의 `ARG0`은 사건 변수(`e9`)다.

### F5 — 기수 관계(`ge`/`gt`/`lt`) 재료는 **있다**. 단 사상 규칙이 없다

`card` 보유 13,470건에서 정도 수식 술어의 공기:

| 술어 | 건수 | 함의 |
|---|---:|---|
| `_at+least_x_deg` | **156** | `ge` |
| `_over_p` | 269 | `gt` (전치사 용법 혼재) |
| `_under_p` | 177 | `lt` (동일) |
| `_more+than_p` | 62 | `gt` |
| `_about_x_deg` | 948 | 근사 — v1 방언 밖 |
| `_only_x_deg` | 298 | 초점 — 기수 관계 아님 |

D-29는 `card` 단독의 사상만 정했고, **정도 수식이 `card` 위에 얹힌 MRS를
`count(rel=ge)`로 사상하는 규칙은 없다.** 현재 구현은 그런 record를
`unsupported_numeric_relation`(1,077건)으로 거부한다.

### F6 — 비례 재료는 형식상 하한을 넘지만 **실질 1건**이다

- `_most_q` 보유 record: **443건**
- 그중 양화 EP가 **1개뿐**(= BODY가 유일 해소되는 경우): **3건**
- 그 3건의 실물 표면:

| item | 표면 | 그 밖의 술어 |
|---|---|---|
| `20214052` | `Most are trim.` | `generic_entity`, `_trim_a_1` |
| `21306015` | `But so far, most potential participants haven't decided.` | `_but_c`, `focus_d`, `comp_so`, `neg`, … |
| `21569067` | `Most other bonds, however, would probably not have fared much better.` | `neg`, `comp`, `subord`, `_would_v_modal`, … |

뒤 2건은 `neg`·`comp`·`subord`·modal을 실어 방언을 넘거나 압박한다.
남는 1건(`20214052`)의 제한식은 **`generic_entity`** — ERG의 무어휘 자리표이며
어휘 술어가 아니다. 표면 `Most are trim.`에는 명사가 없으므로 **subject는
제한식에 무엇을 쓸지 문장에서 알 수 없다.**

나머지 440건은 다중 양화이므로 `multi_quantifier_scope` 층의 성질이 섞인다.

### F7 — 운영 세션이 계약에서 **선택한 독법 1건**을 드러내 둔다

`multiple_card_EP_candidates`를 "문장 내 `card` EP가 둘 이상이면 거부"로
구현했다(v1 최소주의). 더 좁은 독법 — "**같은 결박 변수**에 대한 후보가 둘
이상일 때만 거부" — 도 문면에 부합한다. 이 선택이 **7,755건**을 좌우한다.
조용히 좁은 쪽을 택하지 않기 위해 여기 적는다.

### F8 — 우리 쪽 표면 필터가 아직 방언 확장을 반영하지 않았다

control 적격 술어(D-27이 정한 측정 계약)의 어휘가 그대로다:
`SUPPORTED_QUANTIFIER_LEXICON = (all, every, each, some, no)`,
`UNSUPPORTED_QUANTIFIER_LEXICON = (few, fewer, several, **most**, many, both,
either, neither)`. 기수어(`two/three/five`)는 어느 목록에도 없다.
결과: 위 4건 전부가 `unsupported_quantifier` 또는 `quantifier_count`로 거부된다.
**운영 세션이 임의로 고치지 않았다** — 이것은 D-27이 정한 계약이다.

## 3. 판정 질문

### Q30.1 — `BODY_resolved`의 정의 ★최우선

F4가 확정한 것: "HCONS에 제약됨"으로 읽으면 **0건**, "유일 해소 가능"으로
읽으면 **16,584건**. 전자를 유지하면 MRS source는 원리상 채택 불가이고,
그것은 D-25가 금지한 "실패가 예정된 계약"에 해당하는지가 문제가 된다.

- (a) **`BODY_resolved`를 "유일 해소 가능"으로 정의**한다 — 남은 label이
  하나뿐이어서 scope 해소가 결정적일 때 통과. 다중 양화로 해소가 여럿이면
  여전히 거부(그때가 진짜 scope 미명세다). 운영 세션 관측이 지지하나
  **권고하지 않는다**(범위 확장 방향의 제안은 3연속 기각된 이력이 있다)
- (b) "HCONS에 제약됨"을 유지하고 **MRS source를 부적격으로 종결**한다 —
  기수·비례 재료를 다시 0으로 되돌리고 다른 source를 찾는다
- (c) `RSTR_resolved`만 요구하고 `BODY`는 요구에서 제거 — 우려: 다중 양화의
  진짜 미명세까지 통과한다
- (d) 그 외

부수 질문: (a)를 택하면 **해소의 유일성을 무엇으로 판정하는가** — "남은
label 수 1"인가, 외부 scope solver의 해집합 크기 1인가. 후자는 우리 계약에
새 의존성을 들인다.

### Q30.2 — `multiple_card_EP_candidates`의 독법 (F7, 7,755건)

- (a) 같은 결박 변수에 대한 후보가 둘 이상일 때만 거부(넓은 쪽)
- (b) 문장 내 `card` EP가 둘 이상이면 거부(현재 구현, 좁은 쪽)
- (c) 그 외

### Q30.3 — 정도 수식을 `count.rel`로 사상하는 규칙 (F5)

`at least three papers` 류가 MRS에서 `card(CARG "3")` + `_at+least_x_deg`로
나타난다(156건). D-29는 이 조합을 다루지 않았다.

- (a) 닫힌 열거 표를 신설한다 — `_at+least_x_deg → ge`, `_more+than_p → gt`
  등만 사상하고 나머지(`_about_x_deg` 근사, `_only_x_deg` 초점)는 거부 유지.
  표에 없는 것은 fail-closed
- (b) v1은 `card` 단독(`rel=eq`)만 다루고 정도 수식 record는 전부 거부 유지 —
  그러면 `rel`의 4/5 값이 실물에서 한 번도 운동하지 않는다. `rel`을 채점
  차원으로 유지하는 것이 정당한가가 따라 나온다
- (c) 그 외

### Q30.4 — WSJ 문장 원문을 공개 저장소에 커밋할 수 있는가 (F2·F3)

배포자는 원문 문장을 포함해 CC BY-NC-SA로 공개 배포한다. 그러나 원문의
저작권은 Dow Jones에 있고, 우리 저장소는 공개 GitHub이며 D-29 §17이 Gate C
대조표에 `surface reading` 열을 요구한다.

- (a) fixture manifest는 이미 `text_sha256`만 저장하므로 무해하고, **Gate C
  대조표에서도 표면형을 해시로 대체**한다(사람 감사자는 로컬에서 원문을
  볼 수 있다). 저장소에는 문장이 커밋되지 않는다
- (b) 표면형을 커밋한다 — 배포자의 CC BY-NC-SA 배포와 인용 규모(문장 20건)를
  근거로
- (c) 그 외

구현 상태: `surface_display`에 **기본값을 두지 않았다**(`full` | `sha256`을
호출자가 매번 명시). 이 판정이 그 기본값을 정한다.

### Q30.5 — Open SDP 1.2를 배포처로 채택할 수 있는가 (F1·F2)

- 세 버전 표기(2.0 / 3.0 / 4.0) 중 무엇을 정본으로 기록하는가. 조용히 하나로
  통일하는 것은 라이선스 추정 금지 원칙에 저촉된다
- **NC(비상업)** 가 우리 사용과 양립하는가
- **SA(동일조건변경허락)** 가 우리 파생물(adapter 산출 IR·manifest)에
  전이되는가. 전이되면 저장소 전체 라이선스와 충돌 가능성이 있다

### Q30.6 — 무어휘 제한식(`generic_entity`) fixture의 지위 (F6)

비례 층의 실질 재료가 1건이고 그것이 `generic_entity`다. subject가 제한식
내용을 문장에서 추론할 근거가 없다.

- (a) 적격으로 인정한다 — 투영이 라벨을 익명화하므로 signature 비교는 성립하고,
  측정 대상은 "제한식 **노드를 두었는가**"이지 그 어휘가 아니다
- (b) 부적격 — 그러면 비례 층 재료가 실질 0건이 되고 하한 미달로 freeze 계속 차단
- (c) 다중 양화 `_most_q` 440건에서 적격을 찾도록 범위를 넓힌다(그 경우
  `proportional`과 `multi_quantifier_scope` 층이 겹치는 회계를 정해야 한다)
- (d) 그 외

### Q30.7 — control 표면 어휘 갱신 절차 (F8)

방언이 8종이 되었으므로 `most`가 `UNSUPPORTED`에 남아 있는 것은 사실과
어긋난다. 그러나 control 적격 의미론은 D-27이 정한 측정 계약이므로 운영
세션이 고치지 않았다. 갱신을 승인하는가, 그리고 기수어를 `SUPPORTED`에
넣는가(넣지 않으면 적격성 스캔이 기수 층을 영원히 선별하지 못한다).

## 4. 검증 재현

- F1·F2·F3·F4·F5·F6: `docs/RESEARCH_RESULT_mrs_redwoods_round3.md`
  §A(회신 verbatim + sha256) / §B(우리 실측, 검증 설계 §B.0 포함)
- F4의 계약: `experiments/…/test_stage2_mrs_count_projection.py` 14건 —
  실물 거부를 **회귀 테스트로 보존**했고, "BODY에 제약을 넣으면 통과한다"는
  대조 시험으로 막히는 유일한 이유가 BODY 비제약임을 증명
- 파서: `conceptgate/cg_mrs_reader.py` + 계약 17건(실물 2변종 바이트를 시험
  입력으로). 37,066건 적합성 실측 포함
- 게이트 전체: 13 passed / 0 failed / 1 blocked(선택 의존성 부재)
- 이 세션이 정정한 자기 오류 2건도 같은 문서에 남겼다(§B.11.0, §B.5) —
  깨진 임시 도구가 낸 `6,154`(정본 13,470)와 "`rel` 재료 부재" 주장

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
