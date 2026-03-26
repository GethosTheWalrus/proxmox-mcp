"""Proxmox MCP Server — exposes Proxmox VE management as MCP tools.

When TOOL_ROUTER_MODEL is set to a path containing a fine-tuned FunctionGemma
model, the server starts in *routed* mode: only a ``route_tools`` helper and
``proxmox_api_raw`` escape-hatch are advertised initially.  Calling
``route_tools`` with a natural-language query activates the most relevant tools
and notifies the client to re-fetch the tool list.
"""

from __future__ import annotations

import json as _json
import logging
from typing import Sequence

from mcp.server.fastmcp import Context, FastMCP
from mcp.types import Tool as MCPTool

from proxmox_mcp.client import api_request, format_response
from proxmox_mcp.router import _build_tool_def, get_router
from proxmox_mcp.tools import (
    access,
    backup,
    cluster,
    firewall,
    ha,
    lxc,
    nodes,
    pools,
    qemu,
    sdn,
    storage,
)

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Proxmox MCP Server",
    instructions="Manage Proxmox VE clusters, nodes, VMs, containers, storage, networking, and more.",
)

# ── Register all domain-specific tool modules ─────────────────────────
access.register(mcp)
backup.register(mcp)
cluster.register(mcp)
firewall.register(mcp)
ha.register(mcp)
lxc.register(mcp)
nodes.register(mcp)
pools.register(mcp)
qemu.register(mcp)
sdn.register(mcp)
storage.register(mcp)


# ── Generic escape-hatch tool ────────────────────────────────────────


@mcp.tool()
def proxmox_api_raw(method: str, path: str, params: str = "{}") -> str:
    """Make an arbitrary Proxmox API call for any endpoint not covered by specific tools.

    Args:
        method: HTTP method: 'get', 'post', 'put', 'delete'.
        path: API path (e.g. '/nodes/pve1/qemu/100/status/current').
        params: JSON string of parameters (e.g. '{"memory": 4096}').
    """
    parsed: dict = {}
    if params and params != "{}":
        parsed = _json.loads(params)
    return format_response(api_request(method, path, **parsed))


# ── Tool routing (optional, enabled via TOOL_ROUTER_MODEL) ───────────

# Names of tools that are always visible regardless of routing state.
_ALWAYS_VISIBLE = {"route_tools", "proxmox_api_raw"}

# Set of currently "activated" tool names (populated by route_tools).
_active_tools: set[str] = set()


def _is_routed_mode() -> bool:
    """Return True if tool routing is configured (env var set + path exists)."""
    import os
    from pathlib import Path
    model_dir = os.environ.get("TOOL_ROUTER_MODEL", "")
    return bool(model_dir) and Path(model_dir).exists()


# Monkey-patch the tool manager's list_tools so filtering applies even
# when the MCP server has already captured a bound-method reference.
_original_tm_list_tools = mcp._tool_manager.list_tools


def _filtered_tm_list_tools():
    """Return only active tools from the manager when routing is enabled."""
    all_tools = _original_tm_list_tools()
    if not _is_routed_mode():
        return all_tools
    visible = _ALWAYS_VISIBLE | _active_tools
    return [t for t in all_tools if t.name in visible]


mcp._tool_manager.list_tools = _filtered_tm_list_tools  # type: ignore[assignment]


async def _all_tools_as_mcp() -> list[MCPTool]:
    """Return *all* tools (unfiltered) as MCPTool objects for router inference."""
    from mcp.types import Tool as MCPTool
    return [
        MCPTool(
            name=info.name,
            description=info.description,
            inputSchema=info.parameters,
        )
        for info in _original_tm_list_tools()
    ]


@mcp.tool()
async def route_tools(query: str, ctx: Context) -> str:
    """Find the most relevant Proxmox tools for a given request.

    Call this first with a description of what you want to do.  The server
    will activate the matching tools so you can call them directly.

    Args:
        query: Natural-language description of the desired operation
               (e.g. "list all VMs on node pve1").
    """
    router = get_router()
    if router is None:
        return (
            "Tool routing is not enabled (TOOL_ROUTER_MODEL not set). "
            "All tools are already available."
        )

    # Build FunctionGemma-compatible tool definitions from the full registry
    all_tools = await _all_tools_as_mcp()
    tool_defs = [
        _build_tool_def(t.name, t.description or "", t.inputSchema)
        for t in all_tools
        if t.name not in _ALWAYS_VISIBLE
    ]

    predicted = router.predict(query, tool_defs)

    global _active_tools
    _active_tools = set(predicted)

    # Notify the client that the tool list has changed
    try:
        await ctx.session.send_tool_list_changed()
    except Exception:
        logger.debug("Could not send tool_list_changed notification", exc_info=True)

    if not predicted:
        return "No matching tools found. Try rephrasing your query, or use proxmox_api_raw for direct API access."

    # Build a helpful summary of what was activated
    name_set = set(predicted)
    descriptions = {
        t.name: (t.description or "").split("\n")[0]
        for t in all_tools
        if t.name in name_set
    }
    lines = [f"Activated {len(predicted)} tools for your query:"]
    for name in predicted:
        desc = descriptions.get(name, "")
        lines.append(f"  • {name} — {desc}")
    lines.append("")
    lines.append("These tools are now available. Call the one that best fits your needs.")
    return "\n".join(lines)


def main() -> None:
    """Run the MCP server (stdio transport)."""
    if _is_routed_mode():
        logger.info("Tool routing enabled — only route_tools and proxmox_api_raw visible initially")
        logger.info("Router model will load on first route_tools call")
    else:
        logger.info("Tool routing disabled — all %d tools visible", 286)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
