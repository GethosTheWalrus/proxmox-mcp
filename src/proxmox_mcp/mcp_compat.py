"""Compatibility helpers for MCP SDK server APIs."""

from __future__ import annotations

import inspect
from typing import Any, cast

try:  # MCP SDK >= 2
    from mcp.server.mcpserver import Context, MCPServer
except ImportError:  # MCP SDK 1.x fallback
    from mcp.server.fastmcp import Context  # type: ignore[no-redef]
    from mcp.server.fastmcp import FastMCP as MCPServer  # type: ignore[no-redef]

FastMCP = MCPServer


def get_tool_manager(server: MCPServer) -> Any:
    """Return the MCP SDK tool manager used by both supported SDK layouts."""
    return server._tool_manager  # type: ignore[attr-defined]


def get_registered_tool_map(server: MCPServer) -> dict[str, Any]:
    """Return the registered tool map from the SDK tool manager."""
    return cast(dict[str, Any], get_tool_manager(server)._tools)  # type: ignore[attr-defined]


def list_registered_tools(server: MCPServer) -> list[Any]:
    """Return raw registered tool objects from the SDK tool manager."""
    return list(get_registered_tool_map(server).values())


async def call_registered_tool(server: MCPServer, name: str, arguments: dict[str, Any], ctx: Context | None = None) -> Any:
    """Call a registered tool across MCP SDK call signature variants."""
    manager = get_tool_manager(server)
    signature = inspect.signature(manager.call_tool)
    if "context" in signature.parameters:
        return await manager.call_tool(name, arguments, ctx)
    return await manager.call_tool(name, arguments)
