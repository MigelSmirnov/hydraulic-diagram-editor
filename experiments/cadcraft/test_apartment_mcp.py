#!/usr/bin/env python3
"""Draft apartment and terrace directly with CADCraft MCP commands."""
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
    rpc("initialize", {"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"apartment-mcp-smoke","version":"0.1"}})
    process.stdin.write(json.dumps({"jsonrpc":"2.0","method":"notifications/initialized"}) + "\n")
    process.stdin.flush()
    tool("new_drawing", {"metric": True})
    # Explicit millimetre coordinates. Unverified interior positions are estimates.
    geometry = {
        "OUTER_WALLS": [
            [[0,0],[8382,0]], [[0,0],[0,4775]],
            [[0,4775],[8382,4775]], [[8382,0],[8382,4775]],
        ],
        "PARTITIONS_ESTIMATED": [
            [[3565,0],[3565,2650]], [[3565,3350],[3565,4775]],
            [[1650,2600],[1650,4775]], [[0,2600],[1650,2600]],
            [[6500,4775],[6500,3400]], [[6500,3400],[5800,3400]],
        ],
        "TERRACE": [
            [[8382,0],[14652,0]], [[14652,0],[14652,2355]],
            [[14652,2355],[8382,2355]],
        ],
    }
    handles_by_layer = {}
    for layer, segments in geometry.items():
        execute("layer.new", {"name":layer})
        execute("layer.set", {"name":layer})
        handles_by_layer[layer] = []
        for start, end in segments:
            handles_by_layer[layer].append(handle(execute("line", {"points":[start,end]})))
    summary = tool("inspect_drawing", {"entities":False})
    tool("save", {"path":str(out / "apartment_mcp_draft.dxf")})
    tool("save", {"path":str(out / "apartment_mcp_draft.png")})
    import ezdxf
    saved = ezdxf.readfile(out / "apartment_mcp_draft.dxf")
    lines = list(saved.modelspace().query("LINE"))
    expected = sum(map(len, geometry.values()))
    assert len(lines) == expected, (len(lines), expected)
    assert (out / "apartment_mcp_draft.png").stat().st_size > 0
    for layer in geometry:
        assert layer in saved.layers
    (out / "apartment-mcp-report.json").write_text(json.dumps({
        "status":"PASS", "units":"mm", "main_size":[8382,4775],
        "terrace_size":[6270,2355], "lines":len(lines),
        "layers":list(geometry), "uncertainty":"Interior partitions are approximate",
        "handles":handles_by_layer, "inspection":summary,
    }, indent=2), encoding="utf-8")
    print(f"PASS: apartment CADCraft MCP generated {len(lines)} lines, DXF and PNG")
finally:
    if process.stdin:
        process.stdin.close()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait()
