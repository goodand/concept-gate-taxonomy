# 적대 검증 기록 — D-22/D-23 구현 사슬 (2026-08-23)

방식: adversarial-review 규율 — **근거 축 분리** 4공격자(Haiku xhigh):
판정 원문 대조 / 구성·실행 반례 / 회계 수학 / 스캔 무결성. evidence 없는
finding 폐기, severity 상위는 lead 전량 재실측(P12).

## 확정 발견과 수리 (전부 이번 커밋에 봉합)

| # | 발견 (공격자) | lead 재실측 | 수리 |
|---|---|---|---|
| F1 **BLOCKER** | 무괄호 `∀x P(x) → Q(x)`가 `(∀xP)→Q`로 파싱되고 RHS의 x가 **entity로 조용히 강등** — "구성상 닫힘"이 공허(2공격자 수렴) | **확정** + 반경 실측: 실데이터 6,323 중 무괄호 39건(배포 밖 아님), 비결박 단일 소문자 40건은 전부 실제 열린 식 | 항 규칙 강화: **비결박 단일 소문자 = 거부**(scope 이탈 신호), 다중문자 상수는 유지. 계약 3건 추가 |
| F2 MAJOR | FOL 자격 spec에 Mutation B(임의 ∃ 분할) 직접 검사 부재 | 확정 — 계약에는 있었으나 자격 기록층이 약함 | spec **v2**: `neutral_exists` 검사 신설(restriction=True 단언) |
| F3 MINOR | D-23 §13 "item 9 반드시 포함" 문언 대비 Mutation A가 item 3에만 | 확정(문언) | item 9에 복제 + F1 음성 2건 추가 — v2 23검사, **재자격 9/9** |
| F4 | desugar가 비-dict 조용 통과 | 확정(맥락상 상류 차단이 있으나 자기 계약 위반) | TypeError 가드 + 계약 |
| F5 | 유령 trial_id의 certified/기타 map 묵살(오탈자→조용한 미인증) | 확정 | 3개 map(certified·expected_unscorable·strata) 전부 유령 거부 |
| F6 | expected-unscorable 지정 경로 부재(D-21 §14 도달 불가) + stratum 미전파 | 확정 — 실배선 공백 | `expected_unscorable`·`strata` 파라미터 신설(유령 거부 포함), floor까지 관통 계약 |
| F7 **BLOCKER→정렬** | BOX_OPS 두 목록 발산(scanner: ANA 포함·ELABORATION 누락 vs 스펙) | 확정 — 단 현행 후보 내 두 토큰 0건(영향 잠재적) | 스펙 권위로 정렬(ANA=DRS op) → 재스캔: **후보 695→709(+14, 이탈 0)**, Path A 683 OK, fixture 17 불변 |

## 반박·기각된 주장 (P12 — 재실측이 뒤집음)

- "`∀x Loves(x, alice)`에서 alice가 free로 잡혀야" — **반박**: alice는 항
  규칙상 정당한 상수(entity). 진짜 문제는 F1의 단일 소문자 케이스뿐.
- "Path A/B 불일치 15건 = MAJOR 신규" — **기지 사실 재발견**: fc2e0aa에서
  이미 전량 귀속(hyphen 술어명)·기록됨.
- fingerprint 충돌·OracleDrift α-변형 공격·결정성·중복 trial 거부·stratum
  가드·UNSCORABLE 회계 — **전부 공격 실패**(공격자 자신이 확인).

## 문서화로 수용한 것 (수리 아닌 명시)

- **FOL dedup**: 동일 FOL·상이 NL 16건 — 스캔은 첫 출현의 (example_id,
  premise_index, text_sha256)를 기록하므로 fixture 정체는 결정적. 선별은
  기록된 튜플 기준(문자열 아님)임을 선별 규칙이 전제.
- **PMB 문장 경계 regex의 보수 편향**: 약어(Mr. 류) 오탐은 후보를
  *제외*하는 방향(오염 없음, 손실만). 풀 709 ≫ 15라 수용.
- **ANA 보유 신규 14건**: 문장 내 조응 연산자 — 선별 시 ANA-무 문서 우선
  고려(선별 규칙에 주기).

## 수리 후 상태

FOL adapter 21계약(+3) · 자격 v2 9/9(23검사) · FOLIO 스캔 17 fixture
**불변**/control 963 · PMB 709 · 실행기 58계약 스위트 green.
