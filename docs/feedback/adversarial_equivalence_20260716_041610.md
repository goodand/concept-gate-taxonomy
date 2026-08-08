# 적대적 검증 종합 보고 — 파생 동치 보고 구현

- 일시: 2026-07-16 04:16 UTC
- 대상: `conceptgate/cg_owl.py` `classify()`의 `equivalence_groups` +
  `has_nontrivial_equivalences` 신규 필드 (+ 헬퍼 `_is_reportable_class`,
  `_connected_groups`)
- 방식: 서브에이전트 2개 병렬 (화이트박스 A / 블랙박스 B), 시점 분리
- 발견 처리: **보고만** — 수정은 별도 승인 (사용자 확정)
- 메인 세션이 CONFIRMED 발견을 **직접 재현·검증**함 (에이전트 주장 그대로 신뢰 안 함)

## 요약

신규 필드의 **핵심 로직(직렬화·타입·결정성·전이 폐포·unsat 제외·경보등)은
계약을 정확히 준수**한다. 두 에이전트 합쳐 13+ 시나리오 중 **신규 코드의 결함은
0건**. 다만 검증이 **기존 결함 1건**과 **문서 부채 1건**을 드러냈다.

| 발견 | 등급 | 원인 | 이번 변경이 유발? |
|---|---|---|---|
| #1 gUFO 경로에서 동치 그룹 비대표 멤버의 hierarchy 부모 유실 | CONFIRMED | HermiT가 동치류를 접어 SubClassOf를 대표에만 부여 | **아니오 (기존)** — 변경 전 HEAD에서 동일 재현 |
| #2 `OWL_NOT_OBJECT` 가드가 MCP 경로에서 사문화 | CONFIRMED, 저 | `classify_owl(owl: dict)` 시그니처를 pydantic이 먼저 거부 | 아니오 (기존, 무관) |
| #3 docstring·mechanism.md·MCP_SERVER.md가 신규 필드 누락 | CONFIRMED, 문서 | 필드 추가 시 문서 미갱신 | **예** — 이번 변경의 후속 |

## 신규 코드 자체는 견고 (화이트박스 A + 블랙박스 B 공통)

방어 확인된 각도:
- **다중 독립 그룹·긴 전이 체인(5원소)** — 정확 분리·병합
- **결정성** — 입력 셔플 10회 + `PYTHONHASHSEED` 6종에서 바이트 동일
  (`_connected_groups`의 이중 `sorted()`가 set 순회 비결정성을 완전 정규화)
- **unsat 격리 (유력 후보였음)** — owlready2가 모든 불충족 클래스에 `Nothing`을
  불변식으로 덧붙이므로 `is_unsat` 가드가 항상 선제 차단. "non-unsat인데
  unsat과 동치"는 논리적으로 성립 불가라 누출 재현 불가
- **익명식/구성자 배제** — `_is_reportable_class`가 And/Or/Not/Restriction/
  Thing/Nothing/gUFO를 전부 배제. 실제 `equivalent_to`에 익명식이 섞여도 안 샘
- **MCP 직렬화** — `list[list[str]]`·bool이 raw·wire(JSON) 양쪽에서 온전,
  frozenset/set 누수 0. 한글 클래스명 연쇄(make_snapshot→map_owl→classify_owl)도 정상
- **기존 도구 회귀 없음** — run_pipeline 등 무관 도구에 부수효과 0
- **P1~P7 계약 불변** — 동치 없는 입력에서 새 필드 항상 `[]`/`False`

## 발견 상세

### #1 — gUFO 경로 hierarchy 부모 유실 (CONFIRMED, 기존 결함)

**증상**: stereotype(gUFO)이 로드된 상태에서 nontrivial 동치가 있으면, 동치
그룹의 **대표 1명만** 직계부모를 유지하고 나머지 멤버의 `hierarchy`는 `[]`가 된다.

**메인 세션 직접 재현** (동일 입력, stereotype 유/무 대조):
```
대조군(gUFO 없음):  Encoder=['Block']  Decoder=['Block']   ← 둘 다 정상
실험군(gUFO 있음):  Encoder=[]         Decoder=['Block']   ← Encoder 부모 유실
```
**근본 원인** (raw is_a 관찰):
```
Encoder.is_a = ['gufo.SubKind']              ← Block 없음
Decoder.is_a = ['gufo.SubKind', 'onto.Block'] ← Block은 대표에만
```
HermiT가 `Encoder≡Decoder`를 하나의 동치류로 접으면서 `SubClassOf Block` 간선을
대표(Decoder)에만 assert한다. gUFO import가 이 재조직을 촉발한다.

**이번 변경이 유발한 것이 아님 (검증됨)**: 변경 전 HEAD 코드로 같은 입력 실행 →
`Encoder=[] Decoder=['Block']` 동일. `classify()`의 parents 필터는 의미가 완전히
같고(`_is_reportable_class`는 기존 인라인 술어와 동치), hierarchy 값은 불변.

**역설적 완화**: 이번에 추가한 `equivalence_groups=[['Decoder','Encoder']]`가
바로 이 정보를 복구하는 수단이다 — 클라이언트가 그룹을 교차참조하면 "Encoder의
부모 = Decoder의 부모 = Block"을 재구성할 수 있다. 다만 `hierarchy`만 읽는
클라이언트는 여전히 Encoder를 고아로 오판한다.

**연결**: Round 2 리뷰어의 "representatives / quotient mapping" 제안이 겨냥한
바로 그 축이다. representatives를 내보내면 어느 멤버가 대표인지 명시해 이
비대칭을 계약으로 흡수할 수 있다.

### #2 — `OWL_NOT_OBJECT` 가드 사문화 (CONFIRMED, 저severity, 기존·무관)

`classify_owl(owl: dict)` 시그니처 때문에 `owl`이 dict가 아니면 FastMCP/pydantic이
본문 진입 전 `ToolError`를 던진다. `server.py:728-733`의 `if not isinstance(owl,
dict): return {...OWL_NOT_OBJECT...}`는 MCP 경로로 도달 불가(함수 직접호출로만
도달). crash는 아니나, 형제 가드(`data_properties=[7]`→구조화 오류)와 오류 표면이
비일관. **이번 변경과 무관** — 시그니처는 기존.

### #3 — 문서·docstring 신규 필드 누락 (CONFIRMED, 문서)

이번 변경이 필드를 추가했으나 문서 미갱신:
- `server.py:716` `classify_owl` docstring: "반환: {ok, hierarchy,
  unsatisfiable}" — stereotypes(기존)·equivalence_groups·has_nontrivial 전부 누락
- `docs/mechanism.md:34, 83` — 출력을 3축(hierarchy·stereotypes·unsatisfiable)만 서술
- `docs/MCP_SERVER.md:72-81` — 도구 표가 구 6-tool 상태(classify_owl/map_owl/
  normalizer 도구 자체 부재), 검증 카운트 stale

## 참고 관찰 (결함 아님)

- **primitive가 동치 그룹에 포함**: 정의 클래스가 primitive를 유일 genus로 `≡`
  선언하면(`Alias≡Base`) 그 primitive가 그룹에 들어간다. 외연이 실제 동일하므로
  **의미상 정확**. 자연종 노출을 운영상 원치 않으면 리뷰 포인트.
- **`sync_reasoner` try/except 부재**: 전역 inconsistent면
  `OwlReadyInconsistentOntologyError`가 전파되나, 현재 API(개체 멤버십 주입 불가,
  개념당 stereotype 1개)로는 해당 크래시 도달 불가.

## 제안 (수정은 사용자 승인 후)

1. **#3 문서 갱신** — 가장 명확한 후속. docstring + mechanism.md에 신규 2필드 반영
   (저비용, 이번 변경의 마무리)
2. **#1 representatives 추가 재검토** — hierarchy 부모 유실의 계약적 흡수 수단.
   Round 2에서 "선택"으로 보류했으나, 이 검증이 실효성을 뒷받침함. 넣을지는 결정 필요
3. **#2** — 기존·무관·저severity. 이번 스코프 밖 (별도 정리 항목)
