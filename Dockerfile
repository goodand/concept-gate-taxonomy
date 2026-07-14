# ConceptGate MCP 서버.
#
# Docker를 쓰는 이유는 단 하나 — HermiT(OWL DL reasoner)가 Java 프로그램이라
# JRE가 필요하기 때문이다. Render의 네이티브 python 런타임은 빌드 단계에 root가
# 없어 apt-get을 못 쓴다(공식 문서: 필요한 도구가 없으면 Docker로 배포하라).
# JRE가 없으면 classify_owl 등 OWL 경로 전체가 REASONER_UNAVAILABLE로 죽는다.
FROM python:3.12-slim

# default-jre-headless: owlready2가 HermiT를 subprocess로 실행할 때 쓰는 `java`.
RUN apt-get update \
    && apt-get install -y --no-install-recommends default-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 의존성 레이어를 소스와 분리해 캐시가 소스 변경에 무효화되지 않게 한다.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 정본 소스는 conceptgate/ 하나뿐이다. vendor/는 cg_gufo(scior 규칙 TSV)와
# cg_partwhole(obo core.obo)이 런타임에 읽는다 — 없으면 내장 fallback으로
# 조용히 degrade하므로 반드시 함께 넣는다.
COPY conceptgate/ ./conceptgate/
COPY vendor/ ./vendor/

# 이미지도 배포물이다. vendor subtree의 Apache-2.0/CC0 고지를 보존한다.
COPY THIRD_PARTY_NOTICES.md ./
COPY licenses/ ./licenses/

ENV PYTHONUNBUFFERED=1 \
    MCP_TRANSPORT=http \
    PORT=8000

EXPOSE 8000

# 패키지이므로 -m 으로 실행한다(상대 import가 성립하려면 패키지 컨텍스트 필요).
CMD ["python", "-m", "conceptgate.server"]
