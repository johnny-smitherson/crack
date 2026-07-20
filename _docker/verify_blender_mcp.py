#!/usr/bin/env python3
"""Verify blender-mcp works: replace default cube with sphere, save /workspace/tmp/test.blend"""
import asyncio
import json
import sys
import os

# Use the MCP client to call execute_blender_code via HTTP endpoint
async def main():
    import httpx
    
    base_url = "http://localhost:9877"
    sse_url = f"{base_url}/sse"
    msg_url = f"{base_url}/message"
    headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Connect to SSE to get session ID
        print("Connecting to SSE endpoint...")
        async with client.stream("GET", sse_url, headers=headers) as resp:
            print(f"SSE status: {resp.status_code}")
            # Read the first event to get session ID
            async for line in resp.aiter_lines():
                print(f"SSE line: {line}")
                if line.startswith("data: /message?sessionId="):
                    session_id = line.split("sessionId=")[1].strip()
                    print(f"Got session ID: {session_id}")
                    break
        
        # Step 2: Initialize via message endpoint
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "verify", "version": "1.0"}
            }
        }
        print(f"Initializing with session {session_id}...")
        resp = await client.post(f"{msg_url}?sessionId={session_id}", json=init_msg, headers=headers)
        print(f"Initialize: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
        
        # Step 3: List tools
        list_tools = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        print("Listing tools...")
        resp = await client.post(f"{msg_url}?sessionId={session_id}", json=list_tools, headers=headers)
        print(f"Tools: {resp.status_code}")
        print(f"Response: {resp.text[:1000]}")
        
        # Step 4: Call execute_blender_code to replace cube with sphere
        code = """
import bpy
import os

# Delete default cube
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

# Create sphere
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, location=(0, 0, 0))
sphere = bpy.context.active_object
sphere.name = "TestSphere"

# Save
output_path = "/workspace/tmp/test.blend"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
bpy.ops.wm.save_as_mainfile(filepath=output_path)
print(f"Saved to {output_path}")
"""
        call_tool = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "execute_blender_code",
                "arguments": {"code": code, "user_prompt": "verify blender mcp"}
            }
        }
        print("Executing blender code...")
        resp = await client.post(f"{msg_url}?sessionId={session_id}", json=call_tool, headers=headers, timeout=120.0)
        print(f"Execute result: {resp.status_code}")
        print(f"Response: {resp.text[:2000]}")
        
        # Verify file exists
        if os.path.exists("/workspace/tmp/test.blend"):
            print("SUCCESS: /workspace/tmp/test.blend created")
            return 0
        else:
            print("FAIL: test.blend not found")
            return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))