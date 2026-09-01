# 배포 동기화 — 인증 사슬 v0 최초 배포 + 브랜치 통합 (2026-09-01)

- 성격: **운영 로그.** 측정 계약을 바꾸지 않는다. 선례 문서
  [[concept-gate-h1-wt/docs/DEPLOY_CHERRY_PICK_20260825|DEPLOY_CHERRY_PICK_20260825]]의 후속.
- 결과 커밋: `80c8b34` — `origin/main` 과
  `origin/claude/ontoclean-gufo-handoff-7cmq0v` **양쪽**이 이 커밋을 가리킨다
  (`4d2c110..80c8b34` / `eef02b8..80c8b34`, push 는 사용자 직접 실행).

## 1. 무엇이 배포되나 — 계약 변경이 아니라 최초 배포

배포 표면에 인증 도구가 **0건**이었다(실측: 배포 브랜치 `server.py` 에
`certify_claims`·`issue_claim_certificates` grep 0건, `origin/main` 도 0건).
따라서 D-38 처분(schema v2·profile commitment·검증부 대조)을 실은 이 배포는
기존 클라이언트 계약을 바꾸는 것이 아니라 **인증 사슬의 최초 공개**다 —
하위호환 우려가 원천적으로 없고, D-38 수신 검증 V8 의 "배포된 계약의 역사적
의미" 조건도 이 층에서는 공집합 위에 선다.

## 2. 방식 — cherry-pick 이 아니라 폐포 동기화, 그 이유

08-25 선례는 cherry-pick 이었다(수리 4파일이 양 트리 바이트 동일 → 충돌 0).
이번엔 인증 사슬 커밋이 **14개**이고 시험 cherry-pick 이 `docs/` 파일에서
DU 충돌했다 — 충돌 원인이 **이미지에 들어가지도 않는 파일**(Dockerfile COPY 는
`conceptgate/`·`vendor/` 등만)이었다. 그래서 import 폐포를 실측해 폐포
파일만 동기화했다:

```text
server.py 의 로컬 import: concept_gate_v7 · cg_graph_export · cg_input_linter
                          · cg_obligations · cg_normalizer
cg_obligations 의 import:  cg_identity · _identifier_groups
차이가 있던 나머지:        cg_owl (+84, W2 수리)  ← 포함
바이트 동일이던 것:        concept_gate_v7 · cg_graph_export · cg_input_linter
                          · requirements.txt · vendor/               ← 불필요
```

동기화 7파일(전부 `625f00b` 와 바이트 동일, push 후 재실측 확인):
`server.py` · `cg_obligations.py` · `cg_identity.py`(신규) ·
`cg_normalizer.py` · `_identifier_groups.py`(신규) · `cg_owl.py` ·
`test_server.py`(이미지 밖, 브랜치 위생).

**08-25 의 근거는 계승했다**: 검증된 적 없는 어댑터 10파일(`cg_sbn_adapter`
등 +3,300행)은 이미지에 넣지 않는다. cherry-pick 이라는 *방식*이 아니라
"검증 안 된 코드를 배포하지 않는다"는 *근거*가 선례의 본체다.

## 3. 브랜치 통합 — "어느 브랜치가 맞나"의 해소

사용자 질문("`-docker` 가 그 브랜치 쓰는 것 맞아? main 을 써도 되는데")에서
출발한 실측: 배포 브랜치는 main 보다 **170커밋 앞서고 뒤처짐 0** — 즉 fork 가
아니라 한 줄이었고, main 을 fast-forward 시키는 것으로 질문 자체가 사라진다.
push 가 양쪽 ref 를 같은 커밋(`80c8b34`)으로 만들었으므로 이제 Render 가
어느 브랜치를 빌드하든 같은 내용이다.

문서 불일치도 이것으로 해소된다: verify 스킬은 `-docker` 를, `LOCAL_INSTALL_GUIDE`
는 비-docker 를 MCP 엔드포인트로 안내하고 있었다 — 내용이 같아졌으니 남는
확인은 **각 Render 서비스의 런타임**뿐이다(`render.yaml` 주석: HermiT 가 JRE 를
요구하므로 docker 런타임이 아니면 OWL 경로가 전부 `REASONER_UNAVAILABLE`).

## 4. push 전 감사 (사용자 지시로 수행)

public 저장소이므로 "이미 공개 vs 신규 공개"를 축으로 감사했다.
**신규 공개분은 커밋 2개**(`784e897` 다른 세션의 음성 가드 테스트 +185행 ·
`80c8b34` 동기화 7파일)뿐 — 나머지 170커밋은 이미 public 인 claude 브랜치에
있었다.

| 검사 | 결과 |
|---|---|
| 동기화 커밋 파일 혼입 | 없음 — 정확히 7파일, 전부 바이트 동일 |
| 신규 공개분의 secret·개인 경로·이메일 | **0건** |
| 위험 파일명(.env/.pem/key) 전 범위 | 0건 |
| 대형 파일 3개(0.5~0.8MB) | 실험 trial 산출물, 이미 공개 범위 |
| 개인 경로 31행 | 전부 기존 공개 범위 — 이번 push 의 신규 노출 아님 |

## 5. 검증 사슬 (verify-conceptgate 스킬 사다리)

- (a) 로컬: 동기화 트리에서 `test_server.py` **전체 통과**(사용자 실행).
  동기화 전 71/73 이었고 실패 2는 옛 테스트가 W2 판정이 복원시킨
  `REASONER_DEPENDENCY_UNAVAILABLE` 코드를 모르던 것.
- (b) 로컬 MCP 표면: h1-wt 게이트의 `test_server.py` 가 커버.
- (c) 배포 표면: **완결 (2026-09-01).** 2단 관측 —
  1. 무토큰: `-docker` 가 `Unauthorized: missing Bearer token` — 이 문구는
     이번 배포에 실린 fail-closed 인증(`b8156d8`)의 것이다(배포 전에는
     도구 0개 무응답이었다). **오류의 종류가 바뀐 것이 반영의 첫 신호.**
  2. 인증 probe(`render_cert_probe.py`, 토큰은 사용자 제공): 도구 **13개**,
     인증 계열 `certify_claims`·`issue_claim_certificates` 존재,
     `profile: legacy_relation_claim_v0`(D-38 — 기본값 `_v0` 유지 계약 그대로),
     `profile_required` 6종 일치, anchoring verdict 계산 `pass`,
     `authority: diagnostic_only`(전제 충족 전 인증 없음 — 정상).
- 비-docker 서비스는 **구버전**(도구 6개, 3.4.3, 인증 계열 0) — auto-deploy
  미설정으로 보인다. 정식 표면은 `-docker` 로 확정.
- probe 하네스 승격: `.claude/skills/verify-conceptgate/scripts/render_cert_probe.py`.
  함정 기록 포함 — 첫 폴링이 `new_session()` 튜플 반환을 세션 헤더에 통째로
  넣어 "Session not found" 6라운드를 태웠다(P25 형태: 재배포 증상과 구별
  불가한 오진).
- **토큰 처리**: 사용자가 토큰을 채팅에 공유했고(두 번째 — 이전 세션도
  받았으나 세션 간 기억이 없어 재요구했던 것), **재발급 안 함으로 결정**.
  세션 memory 에 SECRET 표시로 보관해 재요구를 없앴다. 저장소 실측:
  `.env` 추적 0건, git 이력에 토큰 0건 — 커밋 노출은 없다.
