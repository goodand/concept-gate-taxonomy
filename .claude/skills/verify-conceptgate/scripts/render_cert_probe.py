"""배포 표면의 인증 사슬 probe — verify-conceptgate 사다리 (c) 전용.

실행:  MCP_TOK=<Render MCP_API_TOKEN> venv/bin/python \
           .claude/skills/verify-conceptgate/scripts/render_cert_probe.py

관측하는 것: 도구 목록의 인증 계열 · certify_claims 응답의
profile/profile_required(D-38 관측점 — 옛 코드에는 이 필드 자체가 없다) ·
anchoring verdict. 토큰은 **환경변수로만** 받는다 — 하드코딩 금지.

함정 기록(2026-09-01, 첫 폴링이 이것으로 6라운드를 태웠다):
`render_mcp_smoke.new_session()` 은 **튜플** `(sid, serverInfo)` 를 반환한다.
통째로 세션 헤더에 넣으면 서버가 "Session not found" 를 낸다 — 재배포 증상과
구별 불가한 오진을 만든다. 이 스크립트는 자체 rpc 를 쓴다.
"""
import json, os, subprocess
B = "https://concept-gate-taxonomy-docker.onrender.com/mcp"
TOK = os.environ["MCP_TOK"]
H = ["-H","Content-Type: application/json","-H","Accept: application/json, text/event-stream",
     "-H", f"Authorization: Bearer {TOK}"]
def rpc(method, params, sid=None, mid=1):
    hdr = H + (["-H", f"mcp-session-id: {sid}"] if sid else [])
    out = subprocess.run(["curl","-sS","-m","120","-D","/tmp/_h.txt","-X","POST",B,*hdr,
        "-d", json.dumps({"jsonrpc":"2.0","id":mid,"method":method,"params":params})],
        capture_output=True, text=True).stdout
    sid2 = None
    try:
        sid2 = next((l.split(":",1)[1].strip() for l in open("/tmp/_h.txt")
                     if l.lower().startswith("mcp-session-id:")), None)
    except OSError: pass
    data = None
    for line in out.splitlines():
        line = line[6:] if line.startswith("data: ") else line
        try: data = json.loads(line.strip())
        except Exception: pass
    return data, sid2
d, sid = rpc("initialize", {"protocolVersion":"2024-11-05","capabilities":{},
                            "clientInfo":{"name":"d38-probe","version":"0"}})
print("서버:", (d or {}).get("result", {}).get("serverInfo"))
rpc("notifications/initialized", {}, sid=sid)
d, _ = rpc("tools/list", {}, sid=sid, mid=2)
tools = [t["name"] for t in d["result"]["tools"]]
print("도구:", len(tools), "| 인증 계열:", sorted(t for t in tools if "certif" in t))
claim = {"claim_id":"c1","id":"c1","concept":"돌체","feature":"액체금속",
         "cited_evidence_ids":["ev1"],"graph_revision":1}
d, _ = rpc("tools/call", {"name":"certify_claims",
    "arguments":{"claims":[claim],"evidence_texts":{"ev1":"돌체 는 액체금속 을 포함한다"}}}, sid=sid, mid=3)
r = d.get("result", d)
try:
    body = json.loads(r["content"][0]["text"])
except Exception:
    body = r.get("structuredContent", r)
print("profile:", body.get("profile"))
print("profile_required:", body.get("profile_required"))
print("authority:", body.get("authority"), "| certified:", body.get("certified_claim_ids"))
print("anchoring verdict:", (body.get("verdicts_by_claim") or {}).get("c1"))
