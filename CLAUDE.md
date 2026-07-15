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

- `conceptgate/concept_gate_v7.py` -- Core FCA-based concept lattice reasoner
- `conceptgate/cg_partwhole.py` -- Part-whole adapter assembling vocabulary from vendor/obo-relations subtree
- `conceptgate/cg_owl.py` -- OWL 2 DL serializer + HermiT classification (Java 필요)
- `conceptgate/cg_normalizer.py` -- evidence-carrying 경계 어댑터 (단계 파이프라인)
- `conceptgate/server.py` -- MCP server (FastMCP adapter). 실행: `python -m conceptgate.server`
- `conceptgate/data/gufo.owl` -- gUFO endurants-only 서브셋 (형식 변환 사본, third_party/sources.lock.json에 해시 고정)
- `qa_v7.py`, `test_*.py`, `fuzz_normalizer_types.py` -- 테스트 (repo 루트에서 실행)
- `Dockerfile` -- 배포. JRE 포함 (HermiT가 Java를 요구하므로 Docker가 필수)
- `vendor/` -- git subtrees (see Subtree Registry)
- `docs/` -- Implementation packets and documentation

### 테스트 5종 (전부 그린이어야 머지)

```bash
venv/bin/python -m pytest -q                        # 78
venv/bin/python test_server.py                      # 73/73
venv/bin/python qa_v7.py                            # 101/101
venv/bin/python -m conceptgate.concept_gate_v7      # 60/60 (인라인)
venv/bin/python fuzz_normalizer_types.py            # 209, CRASH=0
```

## Key Architecture

- `FeatureType`: ESSENTIAL, CONTEXTUAL, LOCATIONAL, FUNCTIONAL, SOCIAL, STRUCTURAL(has-a)
- `ISA_ALLOWED_TYPES = {FeatureType.ESSENTIAL}` -- only ESSENTIAL creates DAG edges
- `DAGReasoner.composition_view()` -- separate has-a graph (STRUCTURAL edges + UFO shareable detection)
- `relation_hint` (LLM output) -- UFO vocabulary corrected via `cg_partwhole.hint_to_feature_type()`
- `SemanticTypeInference` -- Korean-language keyword heuristic for feature type classification
- `build_expansion_prompt()` -- LLM prompt generator for concept expansion
- `parse_expansion_response()` -- LLM response parser
- `DAGReasoner` -- builds DAG from essential_attrs subset inclusion

## Git

- Do NOT commit without explicit permission
- Branch: `claude/enable-remote-control-Lh6Di` (current working branch)
- Target repo: `goodand/concept-gate-taxonomy` (will be registered separately)
