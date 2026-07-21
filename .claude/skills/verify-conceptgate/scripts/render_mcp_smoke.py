#!/usr/bin/env python3
"""배포된 Render MCP 서버 스모크 테스트 — verify-conceptgate 스킬 번들.

빌드 로그가 green이어도 '반영됨'의 증거가 아니다. 이 스크립트는 배포 서버에
실제 classify_owl을 호출해 응답 필드를 관측한다. Render Free의 cold start와
재배포 세션 드롭에 대비해 매 호출마다 세션 재초기화 + 재시도 + 백오프를 쓴다.

실행: venv/bin/python .claude/skills/verify-conceptgate/scripts/render_mcp_smoke.py
반환: 5시나리오 전부 PASS면 exit 0, 하나라도 실패면 exit 1.
"""
import json
import subprocess
import sys
import time

BASE = "https://concept-gate-taxonomy-docker.onrender.com/mcp"


def rpc(method, params, sid=None, mid=1, timeout=180):
    hdr = ["-H", "Content-Type: application/json",
           "-H", "Accept: application/json, text/event-stream"]
    if sid:
        hdr += ["-H", f"mcp-session-id: {sid}"]
    body = json.dumps({"jsonrpc": "2.0", "id": mid,
                       "method": method, "params": params})
    cmd = ["curl", "-sS", "-m", str(timeout), "-D", "/tmp/_vc_h.txt",
           "-X", "POST", BASE, *hdr, "-d", body]
    out = subprocess.run(cmd, capture_output=True, text=True).stdout
    sid_out = None
    try:
        for line in open("/tmp/_vc_h.txt"):
            if line.lower().startswith("mcp-session-id:"):
                sid_out = line.split(":", 1)[1].strip()
    except OSError:
        pass
    data = None
    for line in out.splitlines():
        line = line[6:] if line.startswith("data: ") else line
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue
    return data, sid_out


def new_session():
    d, sid = rpc("initialize", {"protocolVersion": "2024-11-05",
                                "capabilities": {},
                                "clientInfo": {"name": "verify-conceptgate",
                                               "version": "0.1"}})
    if sid:
        rpc("notifications/initialized", {}, sid=sid)
    return sid, (d or {}).get("result", {}).get("serverInfo")


def call_tool(name, args, mid=10, tries=4):
    """재배포로 세션이 드롭돼도 매번 새 세션 + 백오프 재시도."""
    for k in range(tries):
        sid, _ = new_session()
        if sid:
            d, _ = rpc("tools/call", {"name": name, "arguments": args},
                       sid=sid, mid=mid)
            if d and "result" in d:
                for c in d["result"].get("content", []):
                    if c.get("type") == "text":
                        return json.loads(c["text"])
        time.sleep(15 * (k + 1))
    return None


def diff(name, filler):
    return {"name": name, "definition_kind": "defined",
            "differentia": [{"property": "hasPart", "restriction": "some",
                             "filler": filler}]}


def main():
    sid, info = new_session()
    print("serverInfo:", info)
    d, _ = rpc("tools/list", {}, sid=sid, mid=2)
    tools = [t["name"] for t in (d or {}).get("result", {}).get("tools", [])]
    print(f"[T0] tools ({len(tools)}): {tools}")

    results = []

    p = call_tool("classify_owl", {"owl": {"concepts": [
        {"name": "SelfAttn", "definition_kind": "primitive"},
        diff("Encoder", "SelfAttn"), diff("Decoder", "SelfAttn"),
    ], "object_properties": ["hasPart"]}}, mid=11)
    results.append(("T1 단순 동치",
                    bool(p) and p["equivalence_groups"] == [["Decoder", "Encoder"]]
                    and p["has_nontrivial_equivalences"] is True,
                    p["equivalence_groups"] if p else "None"))

    p = call_tool("classify_owl", {"owl": {"concepts": [
        {"name": "Block", "definition_kind": "primitive", "stereotype": "category"},
        {"name": "SelfAttn", "definition_kind": "primitive", "stereotype": "kind"},
        {**diff("Encoder", "SelfAttn"), "genus": "Block", "stereotype": "subkind"},
        {**diff("Decoder", "SelfAttn"), "genus": "Block", "stereotype": "subkind"},
    ], "object_properties": ["hasPart"]}}, mid=12)
    results.append(("T2 gUFO 부모 복원",
                    bool(p) and p["hierarchy"]["Encoder"] == ["Block"]
                    and p["hierarchy"]["Decoder"] == ["Block"],
                    (f"Enc={p['hierarchy']['Encoder']} "
                     f"Dec={p['hierarchy']['Decoder']}") if p else "None"))

    p = call_tool("classify_owl", {"owl": {"concepts": [
        {"name": "SA", "definition_kind": "primitive"},
        diff("A", "SA"), diff("B", "SA"), diff("C", "SA"),
    ], "object_properties": ["hasPart"]}}, mid=13)
    results.append(("T3 전이 동치 3원소",
                    bool(p) and p["equivalence_groups"] == [["A", "B", "C"]],
                    p["equivalence_groups"] if p else "None"))

    p = call_tool("classify_owl", {"owl": {"concepts": [
        {"name": "Para", "definition_kind": "primitive"},
        {"name": "Rect", "definition_kind": "defined", "genus": "Para",
         "differentia": [{"property": "r", "restriction": "value",
                          "filler": True}]},
    ], "data_properties": [{"name": "r"}]}}, mid=14)
    results.append(("T4 동치 없음(경보등 off)",
                    bool(p) and p["equivalence_groups"] == []
                    and p["has_nontrivial_equivalences"] is False,
                    (f"groups={p['equivalence_groups']} "
                     f"flag={p['has_nontrivial_equivalences']}") if p else "None"))

    p = call_tool("classify_owl", {"owl": {"concepts": [
        {"name": "An", "definition_kind": "primitive"},
        {"name": "Ma", "definition_kind": "primitive"},
        {"name": "R1", "definition_kind": "defined", "genus": "An",
         "differentia": [{"restriction": "subClassOf", "filler": "Ma"}]},
        {"name": "R2", "definition_kind": "defined", "genus": "An",
         "differentia": [{"restriction": "subClassOf", "filler": "Ma"}]},
    ], "disjoint_groups": [["An", "Ma"]]}}, mid=15)
    results.append(("T5 unsat 격리",
                    bool(p) and set(p["unsatisfiable"]) == {"R1", "R2"}
                    and p["equivalence_groups"] == [],
                    (f"unsat={sorted(p['unsatisfiable'])} "
                     f"groups={p['equivalence_groups']}") if p else "None"))

    print("\n=== Render 기반 MCP 스모크 ===")
    allok = True
    for name, ok, detail in results:
        print(f"  [{'OK' if ok else 'FAIL'}] {name}  ->  {detail}")
        allok = allok and bool(ok)
    print(f"\n>>> {'ALL PASS' if allok else 'FAIL 있음'}")
    return 0 if allok else 1


if __name__ == "__main__":
    sys.exit(main())
