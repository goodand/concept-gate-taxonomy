# DESIGN REQUEST — O1 fixture의 라이선스-안전 저장 방식 (Q20)

- 상신: 2026-08-22, 운영 세션
- 판정자 전제: **저장소 접근 없음, 사전 맥락 없음.** §1이 필요한 사실 전부다
- 요청 성격: fixture_template(귀하의 oracle manifest)와 사전등록 목록
  (귀하의 D-E2E-v1-19 §11)의 **개정 여부 판정** — 두 문서 다 귀하의
  정본이라 운영 세션이 임의 개정할 수 없다
- 선행: 저자 문의 경로는 사용자가 기각(회신 기대 난망) — 설계 판정으로 해소

## 1. 사실 (전부 실측·검증됨)

O1(quantifier scope) oracle의 정본 corpus를 확보했다:

- **출처**: OSU Schuler Lab `wikisem` v0.3 — 논문("A Corpus of Encyclopedia
  Articles with Logical Forms", Rasmussen & Schuler, LREC 2020)이 본문에
  명시한 유지 주소(`linguistics.osu.edu/schulerlab/dwnload`)가 살아 있고,
  신청 없이 직접 다운로드된다. typed lambda calculus logical form 파일
  7개(~33MB) + CG 파일 7개. multi-quantifier 문장 공급 충분(논문 실측:
  문장의 ~45%가 scope interaction, "nearly half").
- **형식 실증**: 파일에서 verbatim 확인 —
  `1 LOGIC: (^ (Some (\x1 Some (\e1 N-aD:gironde e1 x1) …`
- **라이선스 문제**: corpus 파일·페이지에 **LICENSE/README 부재**. 논문
  PDF 원문은 **"licensed under CC-BY-NC"**(ELRA) — PDF에서 직접 추출해
  확인. 즉 **재배포 조건 미확정**이며, 이 저장소는 공개 원격(github)에
  push되므로 fixture에 원문을 담아 커밋하면 재배포가 된다.

## 2. 충돌하는 두 정본 조항

| 조항 | 요구 | 충돌 |
|---|---|---|
| oracle manifest `fixture_template.source.text` | 원문 문장 **verbatim** 포함 | 재배포 위험 |
| 같은 template `external_oracle.representation_verbatim` | 원문 LF **verbatim** 보존 ("우리 표기로 덮어쓰지 않는다") | LF도 corpus 콘텐츠 — 같은 위험 |
| D-E2E-v1-19 §11 사전등록 목록 | "fixture IDs + hashes, **expected canonical IR**" 등록 | expected IR이 원문 LF의 번역물이면 파생물 커밋 여부도 같은 질문 |

## 3. 판정 질문

### Q20.1 — 저장 방식

- **(a) hash-pinned 참조 + 실행 시 fetch**: 저장소에는 fixture당
  {locator(파일·행), 원문 text의 sha256, 원문 LF의 sha256}만 커밋.
  실행기가 corpus를 fetch해 sha256 대조 후 메모리에서만 사용. 동결의
  불변성은 hash가 담보(원문이 바뀌면 sha256 불일치로 실행 거부).
- **(b) 번역기 커밋 방식**: (a) + **결정론적 번역기**(원문 LF → 우리
  canonical IR)를 커밋하고, expected IR도 실행 시 계산하되 그
  **canonical hash를 사전등록**에 고정. 저장소에는 corpus 파생물이 한
  글자도 없고, 동결은 {locator, text_sha256, lf_sha256,
  expected_ir_sha256, 번역기 코드}로 성립.
- **(c) verbatim 커밋 강행**: 짧은 발췌 20건 + 출처 표기는 인용 범위라는
  판단 하에 template대로 커밋. (운영 세션은 권하지 않음 — NC 조건과
  corpus 자체 라이선스 부재에서 "인용"의 성립을 우리가 판정할 자격 없음)
- **(d) 출처 교체**: 대안 조사 결과 Wang&Shi는 generator 중심(고정
  원문+LF 규율에 약함), QuantML 공개 worked example은 scoping 4건뿐 —
  둘 다 주 공급원 부적합으로 실측됨. 완결성 위해 포함.

### Q20.2 — (a)/(b) 채택 시 정본 개정

fixture_template의 `source.text`/`representation_verbatim`을
"verbatim **또는** sha256-pinned 참조(라이선스 미확정 출처)"로 개정하는
문안을 귀하가 확정해 달라 — manifest는 귀하의 정본이다.

### Q20.3 — expected IR의 지위

(b)에서 expected IR은 저장소에 **hash로만** 존재한다. D-E2E-v1-19 §11의
"expected canonical IR" 등록을 hash 등록으로 갈음하는 것을 승인하는가?
(사후 조작은 hash가 차단 — 번역기·corpus·hash 셋 중 무엇이 바뀌어도
불일치가 드러난다)

### Q20.4 — URL 소멸 위험의 처리

(a)/(b)는 OSU URL 생존에 의존한다. 로컬 캐시(저장소 밖, gitignore)를
허용하는가? 캐시 파일의 sha256이 사전등록 hash와 일치할 때만 사용.

## 4. 운영 세션의 격리된 의견 (판정 자료 아님)

**(b)를 권한다.** (a)보다 나은 점: 우리 IR 번역까지 파생물 커밋을 피하면서
expected IR의 동결력은 hash로 유지된다. 번역기가 결정론이므로 재현성도
보존된다. 틀릴 수 있는 지점: 번역기 자체가 "LF의 구조를 옮긴 코드"라
파생물 경계가 완전히 깨끗하지는 않다 — 다만 코드는 표현이 아니라 규칙의
구현이라는 관행적 구분에 기댄다. 이 구분의 타당성 판단은 귀하 몫.

## 5. 인용 감사

| 주장 | 확인 방법 |
|---|---|
| corpus 직접 다운로드 가능·파일 목록·크기 | 운영 세션이 페이지 재실측 + C6 파일(3.98MiB) 실제 다운로드 |
| LF 표기 verbatim | 다운로드 파일 grep — 조사 보고의 조각 3건 전부 일치 |
| "licensed under CC-BY-NC" | 논문 PDF 스트림 직접 추출 텍스트에서 발견 (당초 "CC BY 4.0" 표기는 미실측 가정이었음이 확정, 정정됨) |
| ~45% scope interaction | 같은 PDF에서 통계 5종+"nearly half" 확인 |
| 대안 A/B 부적합 | 외부 조사 agent 보고 + 운영 세션 재실측 (RESEARCH_RESULT_o1_corpus_access.md) |
