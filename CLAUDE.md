# ConceptGate Taxonomy

Developer: 탁재현 (goodand/concept-gate-taxonomy)

## Code Philosophy: Ponytail Rules

Before writing any code, traverse this decision ladder top-down. Stop at the first rung that solves the problem.

1. **YAGNI**: Does this need to exist at all? If not, skip it.
2. **Codebase reuse**: Already in this codebase? Reuse it.
3. **Standard library**: stdlib solves it? Use stdlib.
4. **Native platform**: Native feature covers it? Use it.
5. **Installed dependency**: Already-installed dep solves it? Use it.
6. **One-liner**: Can it be one line? Make it one line.
7. **Minimum code**: Only then write the minimum code that works.

The ladder runs AFTER you understand the problem, not instead of it. Read the code fully and trace the real flow before picking a rung.

### Safety (never cut)
- Input validation at trust boundaries
- Error handling that prevents data loss
- Security
- Accessibility
- Explicit user requests

### Intentional simplifications
Mark with `ponytail:` comments that name the ceiling and upgrade path:
```python
# ponytail: O(n^2) scan; upgrade to index if n > 1000
```

### Principles
- Deletion > Addition
- Boring > Clever
- Fewest files possible
- Shortest working diff wins
- No abstraction unless explicitly requested
- Bug fixes target root cause, not symptom

## Subtree Assembly

When writing code, prefer bringing in existing code as **git subtrees** and assembling from reusable parts.

- Before creating new modules, search for existing open-source implementations that can be added as subtrees
- When a feature maps to a well-known library/repo, `git subtree add` it rather than reimplementing
- Keep subtree boundaries clean: don't modify subtree code directly, wrap/adapt in project code
- Track subtree origins in this file under "Subtree Registry" below

### Subtree Registry

| Prefix | Remote | Branch | Purpose |
|--------|--------|--------|---------|
| `vendor/obo-relations` | oborel/obo-relations | master | part_of (BFO:0000050) / has_part (BFO:0000051) 표준 공리. Phase B `relation_hint` 검증. 핵심 파일: `core.obo` |

Subtree 갱신: `git subtree pull --prefix vendor/obo-relations https://github.com/oborel/obo-relations.git master --squash`

## Project Structure

**정본 소스는 `conceptgate/` 패키지 하나뿐이다. 배포 사본을 만들지 말 것.**
예전에는 루트와 `files/`에 같은 모듈이 두 벌 있었고, 한쪽만 고치면 다른 쪽 테스트가
옛 코드로 돌아 *거짓 통과*가 났다. 그 실패 모드를 없애려고 단일 패키지로 합쳤다.
새 모듈은 `conceptgate/`에 추가하면 wheel에 자동 포함된다(수동 목록 없음).

각 모듈이 무엇인지는 그 파일의 docstring이 말한다. `Dockerfile`이 JRE를
포함하는 이유만 여기 남긴다 — HermiT가 Java를 요구해서 Docker가 선택이 아니라
필수다. `conceptgate/data/gufo.owl`은 형식 변환 사본이고 해시가
`third_party/sources.lock.json`에 고정돼 있다.

### 머지 게이트 — 단일 진입점

```bash
venv/bin/python scripts/run_gates.py     # 전부 그린이어야 머지
```

러너가 실행하는 것:

| 게이트 | 내용 |
|---|---|
| core pytest | `pytest -q` (루트, `experiments/` 제외) |
| experiment × N | `experiments/*/test_protocol.py`를 **실험마다 별도 프로세스**로 |
| test_server.py | MCP 서버 (fastmcp 필요) |
| qa_v7.py | 101/101 |
| concept_gate_v7 인라인 | 60/60 |
| fuzz_normalizer_types.py | 209, CRASH=0 |

**왜 단일 스크립트인가**: 실험 폴더들은 동결 규율상 `_cert_core.py`(6개
바이트동일)·`evaluate.py`(10개)·`_gen_prompts.py`(7개)를 같은 모듈명으로
중복 보유한다. 이걸 한 인터프리터에 모아 돌리면 먼저 로드된 쪽이
`sys.modules`를 선점해 **다른 실험이 남의 evaluator로 조용히 실행된다**
(실제로 발생했던 결함). 실험별 프로세스 분리가 유일하게 확장 가능한
해법이고, 새 실험은 아무 조치도 필요 없다. 상세 근거는
`scripts/run_gates.py` 헤더 주석.

**PASS / FAIL / BLOCKED**: 선택적 의존성(`fastmcp`, `owlready2`) 미설치로
게이트가 **시작조차 못 하면** BLOCKED로 분리 보고하고 exit code에 반영하지
않는다. 테스트가 실행된 뒤 실패한 것은 실패 메시지가 모듈 누락을 언급해도
FAIL이다 — 그러지 않으면 환경 의존 테스트 하나가 같은 suite의 실제 회귀를
가린다.

## Git

- Do NOT commit without explicit permission
