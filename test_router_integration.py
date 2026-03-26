"""Quick integration test for routed mode."""
import asyncio
from proxmox_mcp.server import (
    mcp, _filtered_list_tools, _is_routed_mode,
    _active_tools, _original_list_tools,
)
from proxmox_mcp.router import get_router, _build_tool_def


async def test():
    print(f"Routed mode: {_is_routed_mode()}")

    # Before routing: only meta-tools visible
    tools = await _filtered_list_tools()
    print(f"Tools visible (before routing): {len(tools)}")
    names = {t.name for t in tools}
    print(f"  Visible: {sorted(names)}")

    # Simulate routing
    router = get_router()
    all_tools = await _original_list_tools()
    tool_defs = [
        _build_tool_def(t.name, t.description or "", t.inputSchema)
        for t in all_tools
        if t.name not in {"route_tools", "proxmox_api_raw"}
    ]

    print(f"\nRunning inference for: 'list all VMs on node pve1'")
    predicted = router.predict("list all VMs on node pve1", tool_defs, top_k=5)
    print(f"Predicted tools: {predicted}")

    # Activate them
    _active_tools.update(predicted)
    tools = await _filtered_list_tools()
    print(f"Tools visible (after routing): {len(tools)}")
    names = {t.name for t in tools}
    print(f"  Visible: {sorted(names)}")


asyncio.run(test())
