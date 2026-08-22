# Stage 2 end-to-end 리허설 기록 — 2026-08-23 (준비물 ⑥)

목적: 진짜 fixture 없이(발명 3건, corpus 0바이트) **본 실험과 동일한 경로**를
관통 — manifest→resolver 캐시→dispatch plan(③)→레지스트리 agentType+스키마
강제(①②)→cg_evaluate→_stage2_score(④). 결론: **배선 관통 성공, 그리고
dispatch 시도 4회 중 3회가 실패하며 API 계약 3건을 실측**했다 — 리허설이
없었다면 전부 본 코호트에서 났을 실패다.

## 실측된 dispatch 계약 3건 (각각 시도 1회 소모)

| # | 400/거부 | 원인 | 반영 |
|---|---|---|---|
| 1 | `no schema with key or ref "…draft/2020-12…"` | 하네스 검증기가 `$schema` 메타 참조 미해석 | 생성기가 메타 키 자체를 방출하지 않음 (단일 아티팩트 유지 — dispatch용 사본을 벗기면 그게 드리프트) |
| 2 | `input_schema.type: Field required` | API가 tool 스키마 root의 `type` 요구 — bare `$ref` root 불가 | root에 type:object |
| 3 | `input_schema does not support oneOf/allOf/anyOf at the top level` | formula는 본질상 oneOf라 root에 못 옴 | **봉투 패턴**: `{"formula": <$ref>}` — `dispatch_envelope_schema()` 신설, 실행기가 벗김 |

## 4차 시도: 3/3 성공 (전부 StructuredOutput 경유)

- REH-01 (`Every zorble glims.`) → `∀x zorble(x)[glims(x)]`
- REH-02 (`Every quux mels some florp.`) → `∀x quux(x)[∃y florp(y)[mels(x,y)]]`
- REH-03 (`Some tikk praxes every zorble.`) → `∃x tikk(x)[∀y zorble(y)[praxes(x,y)]]`

셋 다 커널 유효·닫힘·표면 어순 scope. trial당 ~2,960토큰, 도구 호출 1회.
**fence는 구조적으로 불가능해졌다** — 프로브 A/B에서 2회 재현된 위반이 이
경로에서 소멸(D-19의 schema-forced 명령이 세 번째로 실증).

## 채점 관통과 의도적으로 유익한 FAIL

evaluate: 3건 전부 `fail`, 차원 귀속 `predicate_arguments` — 원인은 발명
oracle이 어간(`glim`)을, 프롬프트 규약("content words as they appear")이
표면형(`glims`)을 쓰게 한 **어휘화 불일치**다. 양성 대조 2건(oracle 자기
자신 → pass, 표면형 정렬 oracle vs 실제 출력 → pass)으로 평가기 건전성
확정. score: UCR 0.0, 2×2 {A:0,B:0,C:0,D:3}, acceptance 하위 플래그 정확
(`no_final_error` true, `pass_min_met` false).

## 리허설이 노출한 사전등록 요건 (신규)

**술어 명명 규약이 template과 expected-IR adapter 사이에 고정되어야 한다.**
지금 template은 표면형을 지시하는데, 실제 oracle의 술어명은 corpus 관행을
따른다 — PMB라면 WordNet synset(`happy.a.01`)이다. 규약이 안 맞으면
DirectMatch는 **구조적으로 0**이 된다. 따라서 source 자격 스캔 항목에
"술어 명명 규약의 template↔adapter 정합"을 추가해야 하며, 이는 template
동결 전에 반드시 해소할 [TBD] 항목이다 (PREREGISTRATION_STAGE2_DRAFT §B에
반영할 것 — 다음 개정 시).

## 남는 한계

- 리허설 모델은 haiku, 코호트 모델은 [TBD-MODEL].
- certification 축은 certified=False 고정으로 2×2의 C/D열만 관통 — A/B열은
  Verify 파이프라인 연결 시점에 별도 리허설 필요.
- 재료는 발명 3건 — 20건 규모·실 corpus 어휘에서의 거동은 미측정.
