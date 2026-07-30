"""Proxmox MCP Server — exposes Proxmox VE management as MCP tools."""

from __future__ import annotations

import importlib
import logging
import os
import threading
from typing import Any

from proxmox_mcp.client import api_request, format_response
from proxmox_mcp.mcp_compat import Context, MCPServer, call_registered_tool, get_registered_tool_map, get_tool_manager
from proxmox_mcp.tool_manifest import ALWAYS_VISIBLE_TOOLS, ManifestTool, load_manifest
from proxmox_mcp.tool_registry import TOOL_MODULES

logger = logging.getLogger(__name__)

mcp = MCPServer(
    "Proxmox MCP Server",
    instructions="Manage Proxmox VE clusters, nodes, VMs, containers, storage, networking, and more.",
)

_active_tools: dict[str, ManifestTool] = {}
_active_tools_lock = threading.Lock()
_registered_modules: set[str] = set()
_registration_lock = threading.Lock()
_router_indexed = False
_routing_hooks_installed = False
_ROUTED_MODE = os.environ.get("TOOL_ROUTING", "").lower() in ("1", "true", "yes")


def _is_routed_mode() -> bool:
    return _ROUTED_MODE


def _env_flag(name: str, default: str = "") -> bool:
    return os.environ.get(name, default).lower() in ("1", "true", "yes")


def _router_top_k() -> int:
    raw_value = os.environ.get("ROUTER_TOP_K", "10")
    try:
        return max(1, int(raw_value))
    except ValueError:
        logger.warning("Invalid ROUTER_TOP_K=%r; using 10", raw_value)
        return 10


def _register_domain_module(module_name: str) -> None:
    """Import and register one domain tool module exactly once."""
    if module_name not in TOOL_MODULES:
        raise RuntimeError(f"Unknown Proxmox tool module: {module_name}")

    with _registration_lock:
        if module_name in _registered_modules:
            return

        module = importlib.import_module(f"proxmox_mcp.tools.{module_name}")
        module.register(mcp)
        _registered_modules.add(module_name)


def _register_all_domain_tools() -> None:
    """Register every domain-specific tool module for full-tool mode."""
    for module_name in TOOL_MODULES:
        _register_domain_module(module_name)


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

    if _env_flag("PROXMOX_DISABLE_RAW_API"):
        return "Raw Proxmox API access is disabled by PROXMOX_DISABLE_RAW_API."

    parsed: dict = {}
    if params and params != "{}":
        parsed = _json.loads(params)
    return format_response(api_request(method, path, **parsed))


# ── Semantic tool routing ────────────────────────────────────────────


def _ensure_router_indexed() -> None:
    """Lazily initialise the router and build the embedding index from the manifest."""
    global _router_indexed
    if _router_indexed:
        return

    try:
        from proxmox_mcp.router import get_router
    except ImportError as exc:
        logger.warning("Tool routing unavailable: %s", exc)
        return

    router = get_router()
    if router is None:
        return

    manifest = load_manifest()
    tool_pairs = [(tool.name, (tool.description or tool.name)[:200]) for tool in manifest.tools]
    router.index(tool_pairs)
    _router_indexed = True


def _filtered_list_tools() -> list[Any]:
    """Return only the always-visible facade tools in routed mode."""
    return [tool for tool in get_registered_tool_map(mcp).values() if tool.name in ALWAYS_VISIBLE_TOOLS]


def _tool_summary(tool: ManifestTool) -> str:
    """Compact one-line summary: name(params) — description."""
    params = tool.parameters or {}
    props = params.get("properties", {})
    required = set(params.get("required", []))
    parts = []
    for pname, pinfo in props.items():
        if pname == "ctx":
            continue
        typ = pinfo.get("type", "any")
        suffix = "" if pname in required else "?"
        parts.append(f"{pname}: {typ}{suffix}")
    sig = ", ".join(parts)
    desc = (tool.description or "").split("\n")[0][:120]
    return f"{tool.name}({sig}) — {desc}"


def route_tools(query: str) -> str:
    """Find tools relevant to your task. Call this FIRST, then use call_routed_tool to invoke them.

    Returns a list of matching tool names with their parameters. Pass the
    exact tool name and a JSON arguments object to call_routed_tool.

    Args:
        query: Natural-language description of what you want to do (e.g. "list all VMs on a node").
    """
    global _active_tools

    if not _is_routed_mode():
        return "Tool routing is not enabled. All tools are already visible."

    _ensure_router_indexed()

    try:
        from proxmox_mcp.router import get_router, get_router_error
    except ImportError as exc:
        return f"Router failed to initialise. Install proxmox-mcp-server[router] to use TOOL_ROUTING. ({exc})"

    router = get_router()
    if router is None:
        detail = get_router_error()
        if detail:
            return f"Router failed to initialise. Install proxmox-mcp-server[router] to use TOOL_ROUTING. ({detail})"
        return "Router failed to initialise."

    manifest = load_manifest()
    results = router.search(query, top_k=_router_top_k())
    active_tools = {name: manifest.by_name[name] for name in results if name in manifest.by_name}
    with _active_tools_lock:
        _active_tools = active_tools

    logger.info("route_tools(%r) → %d tools activated", query, len(_active_tools))

    lines = [f"Found {len(_active_tools)} tools. Use call_routed_tool(name, arguments) to invoke one:\n"]
    for tool in _active_tools.values():
        lines.append(f"  {_tool_summary(tool)}")
    return "\n".join(lines)


async def call_routed_tool(name: str, arguments: str = "{}", ctx: Context = None) -> str:  # type: ignore[assignment]
    """Invoke a tool returned by route_tools.

    Args:
        name: Exact tool name from route_tools output (e.g. "list_vms").
        arguments: JSON object of arguments (e.g. '{"node": "proxmox1"}').
    """
    import json as _json

    if not _is_routed_mode():
        return "Tool routing is not enabled."

    if name in ALWAYS_VISIBLE_TOOLS:
        return f"Cannot call '{name}' through this tool. Call it directly."

    with _active_tools_lock:
        tool = _active_tools.get(name)

    if tool is None:
        return f"Tool '{name}' is not active. Call route_tools first to find available tools."

    try:
        parsed = _json.loads(arguments) if arguments and arguments != "{}" else {}
    except _json.JSONDecodeError as e:
        return f"Invalid JSON arguments: {e}"

    _register_domain_module(tool.module)

    if name not in get_registered_tool_map(mcp):
        return f"Tool '{name}' was not registered by module '{tool.module}'. The tool manifest may be stale."

    result = await call_registered_tool(mcp, name, parsed, ctx)
    return str(result)


def _install_routing_hooks() -> None:
    """Patch FastMCP's tool manager so only the 3 facade tools are listed."""
    global _routing_hooks_installed
    if not _is_routed_mode():
        logger.info("Tool routing disabled — all %d tools visible", len(get_registered_tool_map(mcp)))
        return
    if _routing_hooks_installed:
        logger.info("Tool routing already enabled — only 3 base tools visible")
        return

    logger.info("Tool routing enabled — only 3 base tools visible")
    registered_tools = get_registered_tool_map(mcp)
    if "route_tools" not in registered_tools:
        mcp.tool()(route_tools)
    if "call_routed_tool" not in registered_tools:
        mcp.tool()(call_routed_tool)
    tm = get_tool_manager(mcp)
    tm.list_tools = _filtered_list_tools  # type: ignore[method-assign]
    _routing_hooks_installed = True


if _is_routed_mode():
    _install_routing_hooks()
else:
    _register_all_domain_tools()


# ── Entrypoint ───────────────────────────────────────────────────────


def main() -> None:
    """Run the MCP server (stdio transport)."""
    logging.basicConfig(level=logging.INFO)
    logger.info(
        "Starting Proxmox MCP server host=%s auth=%s routing=%s read_only=%s raw_api=%s tools=%d",
        os.environ.get("PROXMOX_HOST", "<unset>"),
        "token" if os.environ.get("PROXMOX_TOKEN_NAME") and os.environ.get("PROXMOX_TOKEN_VALUE") else "password" if os.environ.get("PROXMOX_PASSWORD") else "unset",
        _is_routed_mode(),
        _env_flag("PROXMOX_READ_ONLY"),
        "disabled" if _env_flag("PROXMOX_DISABLE_RAW_API") else "enabled",
        len(get_registered_tool_map(mcp)),
    )
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
