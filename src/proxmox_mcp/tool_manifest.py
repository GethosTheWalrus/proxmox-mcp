"""Runtime loader for the generated Proxmox MCP tool manifest."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib.resources import files  # nosemgrep: python.lang.compatibility.python37.python37-compatibility-importlib2
from typing import Any

from proxmox_mcp.tool_registry import TOOL_MODULES

MANIFEST_VERSION = 1
ALWAYS_VISIBLE_TOOLS = {"route_tools", "call_routed_tool", "proxmox_api_raw"}


@dataclass(frozen=True)
class ManifestTool:
    """Static metadata for a lazily registered MCP tool."""

    name: str
    module: str
    description: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class ToolManifest:
    """Validated tool manifest with fast name lookup."""

    version: int
    tools: tuple[ManifestTool, ...]
    by_name: dict[str, ManifestTool]


@lru_cache(maxsize=1)
def load_manifest() -> ToolManifest:
    """Load and validate the generated tool manifest bundled with the package."""
    manifest_path = files("proxmox_mcp").joinpath("tools_manifest.json")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    version = data.get("version")
    if version != MANIFEST_VERSION:
        raise RuntimeError(f"Unsupported tool manifest version: {version}")

    tools: list[ManifestTool] = []
    by_name: dict[str, ManifestTool] = {}
    allowed_modules = set(TOOL_MODULES)

    for raw_tool in data.get("tools", []):
        name = raw_tool.get("name")
        module = raw_tool.get("module")
        description = raw_tool.get("description", "")
        parameters = raw_tool.get("parameters", {})

        if not isinstance(name, str) or not name:
            raise RuntimeError("Tool manifest contains a tool without a valid name")
        if name in ALWAYS_VISIBLE_TOOLS:
            raise RuntimeError(f"Tool manifest must not include always-visible tool: {name}")
        if name in by_name:
            raise RuntimeError(f"Tool manifest contains duplicate tool name: {name}")
        if module not in allowed_modules:
            raise RuntimeError(f"Tool manifest contains unknown module for {name}: {module}")
        if not isinstance(description, str):
            raise RuntimeError(f"Tool manifest contains invalid description for {name}")
        if not isinstance(parameters, dict):
            raise RuntimeError(f"Tool manifest contains invalid parameters for {name}")

        tool = ManifestTool(
            name=name,
            module=module,
            description=description,
            parameters=parameters,
        )
        tools.append(tool)
        by_name[name] = tool

    if not tools:
        raise RuntimeError("Tool manifest contains no tools")

    return ToolManifest(version=version, tools=tuple(tools), by_name=by_name)
