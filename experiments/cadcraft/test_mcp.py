#!/usr/bin/env python3
"""End-to-end CADCraft MCP test: geometry -> BLOCK -> INSERT -> DXF/PNG."""
import json
import subprocess
from pathlib import Path

out = Path("cadcraft-test-output")
out.mkdir(exist_ok=True)
process = subprocess.Popen(
    ["_cadcraft/target/release/cadcraft-cli", "mcp"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    text=True, bufsize=1,
)
seq = 0
def rpc(method, params=None):
    global seq
    seq += 1
    request = {"jsonrpc": "2.0", "id": seq, "method": method, "params": params or {}}
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    line = process.stdout.readline()
    if not line:
        raise RuntimeError("MCP server ended without a response")
    response = json.loads(line)
    if "error" in response:
        raise RuntimeError(str(response["error"]))
    return response["result"]

def tool(name, args=None):
    result = rpc("tools/call", {"name": name, "arguments": args or {}})
    if result.get("isError"):
        raise RuntimeError(f"{name}: {result}")
    texts = [item["text"] for item in result.get("content", []) if item.get("type") == "text"]
    if not texts:
        raise RuntimeError(f"{name}: missing text response")
    return json.loads(texts[0])

def execute(command, params):
    return tool("execute", {"command": command, "params": params})

def handle(result):
    if isinstance(result, dict):
        if isinstance(result.get("handle"), str):
            return result["handle"]
        handles = result.get("handles")
        if isinstance(handles, list) and len(handles) == 1 and isinstance(handles[0], str):
            return handles[0]
    raise RuntimeError(f"Expected exactly one entity handle: {result}")

try:
    rpc("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"hydraulic-cadcraft-smoke","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    process.stdin.flush()
    available = rpc("tools/list")["tools"]
    assert {"execute", "inspect_drawing", "save"} <= {t["name"] for t in available}
    tool("new_drawing", {"metric": True})
    handles = [handle(execute("circle", {"center":[37,37],"radius":23}))]
    for a,b in [
        ([0,37],[14,37]),([60,37],[74,37]),
        ([37,37],[52,27]),([37,37],[37,20]),([37,37],[23,47])
    ]:
        handles.append(handle(execute("line", {"points":[a,b]})))
    created = execute("block", {"name":"HYD_CIRCULATION_PUMP","base":[0,0],"handles":handles,"keep":"convert"})
    assert created.get("block") == "HYD_CIRCULATION_PUMP", created
    second = execute("insert", {"name":"HYD_CIRCULATION_PUMP","at":[200,0],"scale":1,"rotation":0})
    assert second.get("handle"), second
    pipe = execute("line", {"points":[[74,37],[200,37]]})
    assert pipe.get("handle"), pipe
    summary = tool("inspect_drawing", {"entities":True})
    assert "HYD_CIRCULATION_PUMP" in json.dumps(summary), summary
    blocks = execute("blocks.list", {})
    assert "HYD_CIRCULATION_PUMP" in json.dumps(blocks), blocks
    tool("save", {"path":str(out / "pump_mcp.dxf")})
    tool("save", {"path":str(out / "pump_mcp.png")})
    assert (out / "pump_mcp.dxf").stat().st_size > 0
    assert (out / "pump_mcp.png").stat().st_size > 0
    (out / "mcp-report.json").write_text(json.dumps({
        "result":"PASS", "block":created, "second_insert":second,
        "pipe":pipe, "blocks":blocks, "drawing":summary,
    },indent=2),encoding="utf-8")
    print("PASS: CADCraft MCP created block, two inserts, pipe, DXF and PNG")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
