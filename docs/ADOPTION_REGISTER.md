# ADOPTION 원장 — 만든 것이 실제로 불리는가

## 왜 이 문서가 있는가

[[LEGACY_REGISTER]]는 **무엇이 죽었는지**를 적는다. 이 문서는 그 반대편이다 —
**무엇을 만들었고 그것이 실제로 불리는지**.

2026-08-24 실측: 운영 세션이 `scripts/handoff_reachability.py`를 backlink
게이트로 재사용하자고 추천했다. 그 파일은 **테스트가 있었고 아무도 부르지
않았다.** 테스트가 있으니 살아 있는 것처럼 보였고, 채택되지 않았다는 사실이
어디에도 적혀 있지 않았다(P21). 사용자가 지적해서 멈췄다.

그 실패의 구조는 이것이다: **테스트 통과는 채택의 증거가 아니다.** 계약을
지킨다는 것과 누가 쓴다는 것은 다른 사실이고, 후자가 기록되지 않으면
"테스트가 있다"가 "쓰인다"로 읽힌다.

**그리고 채택 주장 자체가 거짓일 수 있다.** 그래서 이 원장의 핵심 검사는
"적혀 있는가"가 아니라 **"인용한 호출처가 실제로 그 이름을 담고 있는가"**다
(`test_adoption_register.py`). 내가 "HANDOFF에 배선했다"고 쓰고 배선하지
않으면 게이트가 잡는다.

## status 어휘 (닫힘)

| status | 뜻 |
|---|---|
| `WIRED_GATE` | `scripts/run_gates.py`가 직접 호출한다 — 병합 게이트의 일부 |
| `WIRED_PYTEST` | 루트 pytest가 자동 수집한다(`test_*.py`) |
| `MANUAL_TOOL` | 사람·agent가 **명명된 시점**에 부른다. 호출처 문서를 반드시 인용하고, 게이트가 그 문서에 이름이 있는지 확인한다 |
| `INFRASTRUCTURE` | 러너·설정 자체. 다른 것이 그것을 통해 돌아간다 |
| `NOT_ADOPTED` | 아무도 부르지 않는다. **사유 필수**이고 [[LEGACY_REGISTER]]에 교차 등록돼야 한다 |

**게이트가 강제하는 범위**(`test_adoption_register.py`):

| status | 강제되는 것 |
|---|---|
| `MANUAL_TOOL` | 인용한 문서가 **실재**하고 그 안에 **파일 이름이 있다** — 이것이 P21 저격 검사다 |
| `WIRED_GATE` | 이름이 `scripts/run_gates.py`에 있다 |
| `NOT_ADOPTED` | 사유가 있고 이름이 [[LEGACY_REGISTER]]에 있다 |
| `INFRASTRUCTURE` · `WIRED_PYTEST` | 인용 검사 **면제** — 규약으로 자동 발견되므로 인용처가 없는 것이 정상이다. 첫 판에서 `conftest.py`의 인용처를 `pytest.ini`로 적었다가 **게이트를 쓰기 전 실측에서 거짓임을 발견**했다(그 파일은 `conftest.py`를 언급하지 않는다) |

## 원장

| path | 무엇인가 | status | 호출처 (게이트가 이 문서에서 이름을 찾는다) |
|---|---|---|---|
| `scripts/run_gates.py` | 병합 게이트 단일 진입점 | INFRASTRUCTURE | `CLAUDE.md` |
| `scripts/verify_finding_citations.py` | 적대검증 finding의 인용 실재 확인 → 없으면 자동 폐기 | MANUAL_TOOL | `.claude/skills/adversarial-review/SKILL.md` |
| `scripts/verify_dispatch_prompts.py` | dispatch 인자 프롬프트가 plan과 바이트 동일한지 | MANUAL_TOOL | `HANDOFF.md` |
| `scripts/wikilink_graph.py` | 저장소 안 `[[wikilink]]` 해소 — 죽은 링크·모호한 basename·범위 밖(EXTERNAL)을 가른다 | WIRED_PYTEST | `test_wikilink_graph.py` |
| `qa_v7.py` | v7 QA 스위트 | WIRED_GATE | `scripts/run_gates.py` |
| `fuzz_normalizer_types.py` | 정규화기 타입 fuzz | WIRED_GATE | `scripts/run_gates.py` |
| `test_server.py` | MCP 서버 표면 검사(스크립트로 실행) | WIRED_GATE | `scripts/run_gates.py` |
| `conftest.py` | pytest 설정 | INFRASTRUCTURE | (인용처 없음 — pytest가 **규약으로 자동 발견**한다) |
| `concept_gate_v6_3.py` | v6.3 추론기 본체 | NOT_ADOPTED | 사유: 회귀 참고용. `README.md`가 그렇게 지목하고 게이트는 v7만 돈다. [[LEGACY_REGISTER]] 등록 |
| `qa_v6_3.py` | v6.3 QA 33건 | NOT_ADOPTED | 사유: 위와 짝. `run_gates.py`는 이 파일을 돌지 않는다. [[LEGACY_REGISTER]] 등록 |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/test_stage2_cohort_acceptance.py` | `WIRED_GATE` | `run_gates.py:134`가 `experiments/*/test_*.py` 보유 디렉터리를 별도 프로세스로 돈다 — 루트 pytest는 `pytest.ini` `norecursedirs`로 실험을 제외하므로 **루트 수집 0건이 정상**이다 | 층 하한 생략 회피를 막는다. 음성 대조 쌍(`test_the_evasion_*`)이 같은 입력에서 판정이 뒤집히는 것을 보인다 |
| `experiments/2026-08-23_e2e_v1_c_o1_cohort/test_frozen_surfaces.py` | `WIRED_GATE` | `run_gates.py:134`의 실험 디렉터리 순회 | 동결 표면 11개(사전등록 3·manifest 4·freeze 4)를 바이트로 고정. **이 세션이 사전등록서에 부록을 append했는데 게이트가 13/0으로 통과한 것**이 생긴 이유다. 완전성 검사가 고정 없는 새 동결 표면을 잡고, 러너를 고정하지 **않는다는 결정**도 테스트로 고정한다 |
| `conceptgate/server_o1_scope.py` + `scripts/run_o1_scope_mcp.sh` | `MANUAL_TOOL` | `docs/O1_SCOPE_TOOL.md` — Claude Desktop `mcpServers.o1-scope` 등재(2026-08-24) 및 CLI `--cli` | 코호트 채점 사슬을 MCP·CLI로 노출. 모델 호출 경로 없음(게이트가 소스 검사). 동반 게이트 `test_server_o1_scope.py` 19건 — 계약 해시 드리프트 거부와 **실패 형태 균일성**에 음성 테스트 |

루트 `test_*.py` 28개는 `WIRED_PYTEST`다 — `pytest.ini`가 `norecursedirs`로
`experiments/`만 제외하므로 루트 테스트는 **자동 수집**된다. 개별 행으로 적지
않는 이유: 채택이 파일 존재만으로 성립하므로 기록이 정보를 더하지 않는다.
실험 폴더의 테스트는 `run_gates.py`가 폴더별 프로세스로 돌린다.

## 이 원장이 하지 않는 것

- **호출처가 그 도구를 쓰는지 확인하지 않는다.** 이름이 문서에 있는지만 본다.
  문서가 "이 도구는 쓰지 마라"라고 적어도 게이트는 통과한다 — 그것까지
  판정하려면 문서를 읽어야 하고, 그것은 기제가 아니라 사람의 일이다.
- **`MANUAL_TOOL`이 실제로 불렸는지 세지 않는다.** 호출 횟수를 기록하려면
  도구가 로그를 남겨야 하고, 그것은 별개 설계다. 지금 막는 것은 "채택된 적
  없는 것을 채택된 것으로 오인하는 것"뿐이다.
