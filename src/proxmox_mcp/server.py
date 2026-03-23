"""Proxmox MCP Server — exposes Proxmox VE management as MCP tools."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

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
from proxmox_mcp.client import api_request, format_response

mcp = FastMCP(
    "Proxmox MCP Server",
    instructions="Manage Proxmox VE clusters, nodes, VMs, containers, storage, networking, and more.",
)

# Register all domain-specific tool modules
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
    import json as _json

    parsed: dict = {}
    if params and params != "{}":
        parsed = _json.loads(params)
    return format_response(api_request(method, path, **parsed))


def main() -> None:
    """Run the MCP server (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
