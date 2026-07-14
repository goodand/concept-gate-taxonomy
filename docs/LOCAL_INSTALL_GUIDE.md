# ConceptGate MCP 로컬 설치 가이드 (Codex CLI)

각자 자기 컴퓨터에서 ConceptGate MCP 서버를 실행하는 방법입니다.
서버는 stdio로 동작하며, Render 배포나 인터넷 연결이 필요 없습니다.
LLM 호출도 하지 않습니다. 검증, 추론, 그래프화만 로컬에서 수행합니다.

## 필요한 것

- Python 3.10 이상
- uv 권장, 또는 pip
- Codex CLI

## 설치

### 1. repo에서 서버 파일 받기

전체 repo를 받아도 됩니다.

```bash
git clone https://github.com/goodand/concept-gate-taxonomy.git
cd concept-gate-taxonomy
```

서버 실행에 필요한 코드는 전부 `conceptgate/` 패키지 안에 있습니다(사본 없음).
서버는 패키지로 실행합니다 — `python -m conceptgate.server`.

`vendor/`는 `cg_gufo`(Scior 규칙 TSV)와 `cg_partwhole`(obo core.obo)이 읽습니다.
없어도 내장 fallback으로 동작하지만, 규칙이 축소되므로 함께 받는 것을 권장합니다.

전체 clone(약 40MB — 대부분 `vendor/`)이 부담되면 sparse checkout으로 줄일 수 있습니다.

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/goodand/concept-gate-taxonomy.git
cd concept-gate-taxonomy
git sparse-checkout set conceptgate vendor
```

`vendor`를 빼면 더 가볍지만 gUFO/OBO 규칙이 내장 fallback으로 축소됩니다.

### 2. 가상환경 생성 + 패키지 설치

`pip install -e .`로 설치하면 `conceptgate-mcp` 실행 파일이 함께 만들어집니다.

uv 사용:

```bash
uv venv --python 3.12
uv pip install -e .
```

uv가 없으면:

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

Windows PowerShell:

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
```

### 3. 설치 확인

macOS/Linux:

```bash
.venv/bin/python test_server.py
```

Windows:

```powershell
.venv\Scripts\python.exe test_server.py
```

`통과: 66/66`이 나오면 정상입니다.

### 4. 현재 절대 경로 확인

macOS/Linux:

```bash
pwd
```

예:

```text
/Users/name/concept-gate-taxonomy
```

Windows PowerShell:

```powershell
(Get-Location).Path
```

이 경로를 다음 단계의 `<PWD>` 자리에 넣습니다.

### 5. Codex CLI 설정에 등록

`~/.codex/config.toml` 파일을 열고, 없으면 생성한 뒤 아래 내용을 추가합니다.
`<PWD>`는 4단계에서 확인한 절대 경로로 교체하세요.

패키지를 설치하면(`pip install -e .`) `conceptgate-mcp` 실행 파일이 생깁니다.
이걸 그대로 가리키면 작업 디렉터리에 상관없이 동작합니다.

```toml
[mcp_servers.conceptgate]
command = "<PWD>/.venv/bin/conceptgate-mcp"
args = []
```

macOS 예시:

```toml
[mcp_servers.conceptgate]
command = "/Users/name/concept-gate-taxonomy/.venv/bin/conceptgate-mcp"
args = []
```

Windows 예시:

```toml
[mcp_servers.conceptgate]
command = "C:\\Users\\name\\concept-gate-taxonomy\\.venv\\Scripts\\conceptgate-mcp.exe"
args = []
```

## 사용

Codex CLI를 재시작하면 ConceptGate 도구 6개가 인식됩니다.

- `lint_concepts`
- `run_pipeline`
- `expand`
- `classify_parents`
- `export_graph`
- `analyze_expansion`

예시 프롬프트:

```text
conceptgate의 run_pipeline으로 개, 고양이, 말을 분류해줘.
각각 동물(essential_feature, evidence "살아있는 생명체")을 가진다.
PASS_WITH_WARNING이 나오면 expansion_actions를 보고 종차를 만들어
expand로 재실행해줘.
```

입력 품질까지 점검하려면 먼저 `lint_concepts`를 호출하세요.

## 자주 겪는 문제

### command not found 또는 서버가 안 뜸

`config.toml`의 `command`가 절대 경로인지 확인하세요.

```bash
ls <PWD>/.venv/bin/conceptgate-mcp
```

Windows:

```powershell
Test-Path "<PWD>\.venv\Scripts\conceptgate-mcp.exe"
```

### No module named fastmcp / conceptgate

패키지 설치가 안 된 상태입니다.

```bash
.venv/bin/pip install -e .
```

Windows:

```powershell
.venv\Scripts\python.exe -m pip install -e .
```

### classify_owl이 REASONER_UNAVAILABLE을 반환

OWL 분류기(HermiT)는 Java가 필요합니다. `java -version`으로 확인하고,
없으면 JRE를 설치하세요(macOS: `brew install openjdk`).
Java 없이도 나머지 도구는 정상 동작합니다.

### Python 3.10 미만

FastMCP는 Python 3.10 이상이 필요합니다.

```bash
python3 --version
```

## 원격 서버를 쓰고 싶다면

로컬 설치 대신 공개 Render 서버를 사용할 수도 있습니다.
이 경우 설치 없이 `config.toml`에 URL만 등록합니다.

```toml
[mcp_servers.conceptgate]
url = "https://concept-gate-taxonomy.onrender.com/mcp"
```

공개 서버는 무료 티어라 15분 이상 유휴 후 첫 요청이 지연될 수 있습니다.
자주 사용할 경우 로컬 설치가 더 빠르고 안정적입니다.

timeout이 발생하면 먼저 아래 health URL로 서버를 깨운 뒤 재시도하세요.

```text
https://concept-gate-taxonomy.onrender.com/health
```

큰 taxonomy 입력은 `lint_concepts`를 먼저 실행하고, `LARGE_PAIRWISE_INPUT` 경고가
나오면 topic/root별로 나눠 `run_pipeline`을 호출하는 것이 안전합니다.
