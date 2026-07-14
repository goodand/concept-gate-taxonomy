# ConceptGate MCP Server

FCA(형식개념분석) 기반 개념 계층 분류기 ConceptGate v7을 MCP 도구로 노출하는 서버.

## 핵심 원칙

이 서버는 LLM을 호출하지 않는다. MCP client(Codex CLI, Claude Desktop,
Claude Code 등)가 LLM reasoning layer 역할을 하며, `expansion_actions`를
해석하여 종차를 생성한 뒤 `expand` 도구에 제공한다.

```
client → run_pipeline → WARNING + expansion_actions
       → client가 종차 생성 → expand → PASS → export_graph
```

## 파일 구성

정본 소스는 `conceptgate/` 패키지 하나뿐이다(배포 사본 없음).

```
concept-gate-taxonomy/
├── conceptgate/
│   ├── server.py          MCP 서버 (FastMCP). `python -m conceptgate.server`
│   ├── concept_gate_v7.py ConceptGate 코어
│   ├── cg_partwhole.py    part-whole 어휘 어댑터 (vendor/obo-relations)
│   ├── cg_gufo.py         Scior/gUFO rule metadata 어댑터 (fallback 포함)
│   ├── cg_input_linter.py 입력 JSON 사전 점검 linter (stdlib)
│   ├── cg_normalizer.py   evidence-carrying 경계 어댑터
│   ├── cg_owl.py          OWL 2 DL 직렬화 + HermiT 분류 (Java 필요)
│   └── cg_graph_export.py GraphExporter
├── test_server.py         MCP 서버 테스트 (66건)
├── pyproject.toml
├── Dockerfile             배포 이미지 (JRE 포함)
└── examples/
    ├── codex_config.toml           Codex CLI MCP 설정 예시
    ├── claude_desktop_config.json  Claude Desktop MCP 설정 예시
    └── ../sample_concepts.json     도구 입력 예시
```

## 설치

Codex CLI에서 로컬 stdio MCP로 설치하려면
[`LOCAL_INSTALL_GUIDE.md`](LOCAL_INSTALL_GUIDE.md)를 먼저 보세요.
clone, 가상환경, 테스트, `config.toml` 등록까지 실패 지점 중심으로 정리되어 있습니다.

`pip install -e .`로 설치하면 `conceptgate-mcp` 실행 파일이 생기고, 작업 디렉터리와
무관하게 동작한다. 개별 파일을 옮겨 배치할 필요가 없다.

uv 사용 (권장 — 시스템 Python 충돌 회피):

```bash
cd conceptgate-mcp
uv venv --python 3.12
uv pip install fastmcp
```

또는 패키지로 설치:

```bash
uv pip install -e .
```

## 검증

```bash
.venv/bin/python test_server.py
```

47/47 통과해야 정상. PART 1은 함수 직접 호출, PART 2는 FastMCP Client
in-memory로 실제 MCP 프로토콜(tools/resources/prompts)을 검증한다.

## 도구 (Tools)

| 도구 | 역할 |
|---|---|
| `lint_concepts` | `run_pipeline` 전 입력 JSON 품질 점검. 누락 feature, placeholder, 약한 structural evidence, relation_hint/type 충돌 감지 |
| `run_pipeline` | 개념 리스트 → DAG 생성 + 검증. 핵심 엔트리포인트 |
| `expand` | 기존 개념에 종차 병합 + 재실행. client가 종차 생성 후 호출 |
| `classify_parents` | 개념별 부모 후보 multi-label 판정 (meet 지원) |
| `export_graph` | 결과를 mermaid/json/graphml/summary로 변환 |
| `analyze_expansion` | 확장 루프 history 수렴/정체/진동 판정 |

## 리소스 (Resources)

- `conceptgate://expansion-schema` — 종차 생성 시 따라야 할 JSON 스키마
- `conceptgate://pipeline-status-codes` — 5단계 status + 권장 행동
- `conceptgate://client-guide` — source-grounded feature 정규화와 FAIL 재시도 가이드

## 프롬프트 (Prompts)

- `expansion_prompt` — 종차 생성용 구조화 프롬프트 (선택적 helper)

## 입력 형식

```json
{
  "concepts": [
    {
      "name": "개",
      "features": [
        {"feature": "동물", "type": "essential_feature", "evidence": "살아있는 생명체"}
      ]
    }
  ]
}
```

type은 essential_feature / structural_composition / contextual_usage /
locational / functional / social_treatment 중 하나. evidence는 최소 4자.
입력은 반드시 ParseGate를 경유하므로 잘못된 형식은
`{"status": "FAIL", "errors": [...]}`로 거부된다.

concept에는 선택적으로 `ontoclean` 메타속성을 넣을 수 있다. 이 값이 있으면
`is-a` edge를 만들기 전에 OntoCleanMetaGate가 rigidity, identity, unity,
dependence, category 위반을 검사한다. 값이 없으면 기존 FCA feature-subsumption
동작을 유지한다.

```json
{
  "name": "트랜스포머",
  "ontoclean": {
    "category": "model_architecture",
    "rigidity": "rigid",
    "identity": "supplies_identity",
    "unity": "unified_whole",
    "dependence": "independent"
  },
  "features": [
    {"feature": "시퀀스처리", "type": "essential_feature", "evidence": "시퀀스 입력을 처리한다"}
  ]
}
```

### is-a vs has-a

- `essential_feature` → is-a DAG 간선 (분류 계층). `dag`/`definitions`로 반환.
- `structural_composition` → has-a 구성 그래프 (부분-전체). `composition` 필드로
  별도 반환: `{"edges": [[전체, 부분], ...], "shared_parts": {부분: [전체들]}}`.

선택 필드 `relation_hint`(UFO 어휘)로 관계 맥락을 명시할 수 있다:
is_a, component_of, member_of, subcollection_of, subquantity_of,
material_of, phase_of, located_in.

`relation_hint`와 `type`이 모순되면 Relation Discrimination Gate가
DAG 생성 전에 `NEEDS_CORRECTION`으로 차단한다. 예를 들어
`type: essential_feature`와 `relation_hint: component_of` 조합은 is-a가 아니라
has-a 후보이므로 수정이 필요하다.

```json
{"feature": "엔진", "type": "structural_composition",
 "evidence": "자동차는 엔진을 동력원으로 가진다", "relation_hint": "component_of"}
```

### Source-grounded client guide

MCP client는 `conceptgate://client-guide`를 읽어 source evidence를
`run_pipeline` 입력으로 정규화하는 규칙을 확인할 수 있다.

권장 호출 순서:

```text
source evidence → atomic features → lint_concepts → run_pipeline
```

핵심 원칙:

- 개념명만으로 is-a/has-a 결론을 내리지 않는다.
- `run_pipeline` 전에 `lint_concepts`를 호출해 입력 품질을 점검한다.
- feature가 없거나 비어 있어 `Parse Gate`가 실패하면, 출처 기반 feature discovery를
  수행하고 atomic feature로 정규화한 뒤 `run_pipeline`을 재호출한다.
- `status: FAIL`이면 반환된 `dag`, `composition`, `isolated`는 진단 부산물이며
  확정 결과로 보고하지 않는다.
- `structural_composition`은 whole이 part/module/layer/component 등을 구조적으로
  포함한다고 evidence가 말할 때만 사용한다.
- `based on`, `uses`, `relies on`, `computed by`, `follows architecture` 같은 약한
  표현만으로는 has-a를 만들지 않는다.
- 상속 feature는 `"parent features"` 같은 placeholder로 쓰지 말고, parent의
  essential feature label을 자식에 명시적으로 반복한다.

### Hosted timeout / Render 운영

`run_pipeline`과 `lint_concepts` 응답에는 원인 분리용 `server_meta`가 포함된다.

```json
{
  "server_meta": {
    "timing_ms": 12.345,
    "input_stats": {
      "concept_count": 10,
      "feature_count": 42,
      "pairwise_comparisons": 45
    }
  }
}
```

운영 권장:

- Render cold start가 의심되면 먼저 `GET /health`로 깨운 뒤 재시도한다.
- 큰 taxonomy는 `lint_concepts`를 먼저 호출한다. `LARGE_PAIRWISE_INPUT` 경고가
  나오면 topic/root별 chunk로 나눠 검증한다.
- hosted client는 2-3회 retry/backoff를 둔다.
- `server_meta.timing_ms`가 낮은데 client timeout이면 cold start/네트워크 문제,
  높으면 입력 크기/서버 처리시간 문제로 본다.

### 검증 출력 (Phase C)

- `composition_issues` — mereology 공리 위반: 반대칭(antisymmetry),
  순환(cycle), is-a/has-a 혼동(isa_hasa_conflict), 자기부분(self_part)
- `anti_patterns` — UFO 안티패턴 (WARNING, 차단 안 함):
  - **MixRig**: 같은 feature가 essential과 비-essential로 혼용
  - **PartOver**: is-a 조상-자손이 같은 부분을 중복 선언
  - **WholeOver**: 한 개념이 부분과 그 특수화를 동시 보유

OntoClean rigidity 위반은 Scior/gUFO의 R22/RA02 rule reference를 함께 보존한다.
`vendor/scior` 없이 설치한 경우 `cg_gufo.py`의 내장 fallback metadata를 사용한다.

## 연결

### Codex CLI

config.toml에 등록 (`codex_config.toml` 참조):

```toml
[mcp_servers.conceptgate]
command = "/absolute/path/to/conceptgate-mcp/.venv/bin/python"
args = ["/absolute/path/to/conceptgate-mcp/server.py"]
```

### Claude Desktop

설정 파일에 등록 (`claude_desktop_config.json` 참조):

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "conceptgate": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/server.py"]
    }
  }
}
```

### Claude Code

`.claude/settings.json`:

```json
{
  "mcpServers": {
    "conceptgate": {
      "type": "stdio",
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "/path/to/conceptgate-mcp"
    }
  }
}
```

## 로컬 디버깅

MCP Inspector:

```bash
uv run fastmcp dev server.py
```

## 대화 흐름 예시

```
사용자: "개, 고양이, 말을 분류해줘"
client: [run_pipeline] → PASS_WITH_WARNING, expansion_actions=[{depth, [개,고양이,말], [동물]}]
client: (종차 생성) [expand] → PASS
client: [export_graph mermaid] → 다이어그램
```
