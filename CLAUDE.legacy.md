> # ⚠️ LEGACY — 이 문서는 더 이상 구속력이 없다
>
> **2026-08-08 격리됨.** 파일명이 `CLAUDE.md`가 아니므로 자동 로드되지
> 않는다. 이것이 격리의 전부이자 목적이다 — 내용은 이력 증거로 보존한다.
>
> **활성본**: `concept-gate-codex-mcp-wt/CLAUDE.md`
> (11,750B, 활성 worktree 6곳에 byte-identical). 이 문서(4,849B)는 그
> 활성본의 조상이다.
>
> **격리 근거 — 이 문서는 사실과 다른 것을 말한다:**
>
> - 아래 `## Git` 절이 `claude/enable-remote-control-Lh6Di`를
>   "current working branch"라고 명시하지만 **그 브랜치는 존재하지 않는다**
>   (`git branch -a`로 확인). 이 worktree의 실제 브랜치는
>   `claude/ontoclean-gufo-handoff-7cmq0v`다.
> - "Target repo ... (will be registered separately)"도 이미 등록이 끝난
>   저장소를 미등록으로 서술한다.
>
> **이 문서에 없는 활성 규율 (활성본에만 있음):**
>
> 1. worktree 사이로 파일을 손으로 복사하지 말 것 (2026-08-05 실측 사례 포함)
> 2. 무언가를 찾을 때 grep으로 끝내지 마라 (recall 0.688→1.000 실측)
> 3. 설계 판정을 상신하기 전 "아직 안 풀렸다"고 단정하지 마라
> 4. 머지 게이트 단일 진입점(`scripts/run_gates.py`) — 이 문서의 "테스트
>    5종" 나열은 옛 방식이며, 실험 폴더 동명 모듈이 `sys.modules`를 선점해
>    **다른 실험의 evaluator로 조용히 실행되던** 실제 결함을 반영하지 않는다
>
> **이 worktree의 규칙 공백**: 격리 후 이 디렉토리에는 ConceptGate 저장소
> 규칙이 없다. 상위 `Project_in_progress/CLAUDE.md`(vault 안전 게이트·검색
> 절차)는 계속 로드된다. 활성본을 이 브랜치로 들이는 것은 정상 경로
> (commit → merge → rebase)로 처리한다 — **이 파일을 되살리거나 활성본을
> 손으로 복사하지 말 것.**
>
> 판정 근거 전문:
> `notes/audits/vault/claude-md-divergence-audit-2026-08-08.md`

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
venv/bin/python -m pytest -q                        # 86
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
