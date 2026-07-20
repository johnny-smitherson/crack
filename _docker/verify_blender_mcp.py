#!/usr/bin/env python3
"""Verify blender-mcp over native stateless Streamable HTTP at :9877/mcp."""
import asyncio
import os
import sys

MCP_URL = "http://localhost:9877/mcp"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/event-stream",
}


async def mcp_post(client, payload: dict) -> dict:
    resp = await client.post(MCP_URL, json=payload, headers=HEADERS, timeout=120.0)
    resp.raise_for_status()
    return resp.json()


async def main() -> int:
    import httpx

    async with httpx.AsyncClient() as client:
        init = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "verify_blender_mcp", "version": "1.0"},
            },
        }
        print("initialize...")
        result = await mcp_post(client, init)
        print(f"initialize ok: {str(result)[:200]}")

        code = """
import bpy
import os

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
bpy.context.active_object.name = "TestSphere"
output_path = "/workspace/tmp/test.blend"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"Saved to {output_path}")
"""
        call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "execute_blender_code",
                "arguments": {"code": code, "user_prompt": "verify blender mcp"},
            },
        }
        print("tools/call execute_blender_code...")
        result = await mcp_post(client, call)
        print(f"call result: {str(result)[:500]}")

    if os.path.exists("/workspace/tmp/test.blend"):
        print("SUCCESS: /workspace/tmp/test.blend created")
        return 0
    print("FAIL: test.blend not found")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
