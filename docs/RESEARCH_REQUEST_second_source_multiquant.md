# RESEARCH REQUEST — 다중 양화 gold의 독립 제2 source 후보 조사

- 수신자: **조사용 agent** (다른 workspace, zero context 전제 — 이 문서가
  맥락 전부. 설계용 agent 아님)
- 발신: ConceptGate 운영 세션, 2026-08-23
- 후속: 회신을 운영 세션이 검증 후, 후보의 적격성 스캔은 별도 기계 실측.
  **조사에게 적격성 판정을 청하지 않는다** — 접근·라이선스·형식·규모의
  사실 확인만.

## 1. 배경 (필요한 최소한)

의미 컴파일 실험의 수용 오라클로 PMB(Parallel Meaning Bank) gold를 최대
15건 쓰기로 판정됐고, 나머지 **최소 5건은 독립 제2 source가 "다중 양화
scope" 문장을 공급**해야 한다. PMB gold 전수 스캔(12,053 문서) 결과 진짜
다중 양화 문장(예: "Every student read some book" 류 — 한정사 2개가 서로
scope 상호작용)이 사실상 0건이었기 때문이다.

찾는 것: **문장 단위로, 사람이 저작·검수한 형식 의미 표상(논리식류)이
붙어 있고, 한 문장에 양화사 2개 이상이 상호작용하는** 항목을 5건 이상
공급할 수 있는 공개 자원.

**독립성 조건 (외부 판정 D-E2E-v1-22 §13 verbatim — 하나라도 어기면
후보가 아니다):**

```yaml
second_source:
  different_corpus_authority: true      # PMB와 다른 기관/저작 주체
  independently_authored_gold: true     # 사람이 저작·검수한 gold
  not_derived_from_PMB: true            # PMB 재수출·변환판 금지
  not_project_generated: true           # 우리가 생성한 쌍 금지
  separate_source_locator: true
  separate_adapter_profile_if_formalism_differs: true
```

이 프로젝트가 데인 실패 2건을 피하라 (이전 요청서와 동일):
1. **라이선스를 정책으로 추정 금지** — 배포처 명시 문구 verbatim 인용.
2. **원문 철자·URL 문자 그대로 시도** — 교정은 그 다음.
그리고 **"확인 못함"(BLOCKED)과 "없음"을 구분**하라.

## 2. 조사 질문

### R1 — 후보 목록 (3~6개)
다중 양화 문장 + 형식 표상 쌍을 제공하는 공개 자원 후보. 우리가 이미 아는
계열(각각 왜 되는지/안 되는지 사실만): FraCaS test suite(양화 절 §1),
HOLLIS/GQ 데이터셋류, CCGbank 파생 논리식, Groningen 계열(단 PMB 파생이면
탈락), 논리 교과서 corpus류, GLUE/SuperGLUE류(형식 표상 없으면 탈락).
후보마다: 저작 주체·형식(논리식 문법)·규모·접근 경로.

### R2 — 각 후보의 라이선스
명시 문구 verbatim. LICENSE 파일/페이지 문구/논문 표기가 다르면 셋 다.

### R3 — 다중 양화 실재 신호
각 후보에서 한정사 2개 이상 상호작용 문장의 실물 예 1~2건(짧게, 표상 포함
가능하면 함께). 몇 건이나 있을지의 규모 신호(정확 수 불요, 출처 명시).

### R4 — 형식 문법의 정본
각 후보의 표상 문법을 정의한 문서(논문/매뉴얼) 위치 — 우리 constructor
스캐너와 adapter 계약 설계에 필요하다. **FraCaS처럼 표상이 함의 판정
(entailment label)뿐이면 "형식 표상 없음"으로 명기하라** — 함의 라벨은
우리 오라클이 될 수 없다.

### R5 — 수작업 저작 여부
gold가 사람 저작인지, 문법에서 자동 생성됐는지(생성이면 생성기 저작
주체·결정성). 자동 생성이라도 **제3자가 저작·공개한 완성 artifact**면
후보다(우리가 생성하면 탈락 — not_project_generated).

## 3. 보고 형식

R항목별: 사실 / 근거(URL·verbatim) / 확신도 / BLOCKED 여부. 시도했으나
실패한 경로 포함. 후보 순위는 매겨도 좋으나 근거를 사실로 한정하라.

---

<!-- 저장소 내부 항법 (외부 수신자에게는 무의미하다 — 그래서 본문 끝에 둔다) -->
- 사슬 색인 [[RULING_CHAIN_INDEX]] · 상태 정본 [[concept-gate-h1-wt/HANDOFF|HANDOFF (worktree 루트)]]
