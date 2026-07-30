#!/usr/bin/env python3
"""Generate or check the bundled Proxmox MCP tool manifest."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any

from proxmox_mcp.mcp_compat import MCPServer, get_registered_tool_map
from proxmox_mcp.tool_manifest import ALWAYS_VISIBLE_TOOLS, MANIFEST_VERSION
from proxmox_mcp.tool_registry import TOOL_MODULES

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "src" / "proxmox_mcp" / "tools_manifest.json"


def build_manifest() -> dict[str, Any]:
    """Build manifest data by registering each domain module on an isolated FastMCP instance."""
    # Domain modules must register deterministically; routed mode relies on this
    # manifest matching the tools registered later by the same module.
    tools: list[dict[str, Any]] = []
    seen: set[str] = set()

    for module_name in TOOL_MODULES:
        test_mcp = MCPServer(f"manifest-{module_name}")
        module = importlib.import_module(f"proxmox_mcp.tools.{module_name}")
        module.register(test_mcp)

        for tool in get_registered_tool_map(test_mcp).values():
            if tool.name in ALWAYS_VISIBLE_TOOLS:
                continue
            if tool.name in seen:
                raise RuntimeError(f"Duplicate tool name in manifest generation: {tool.name}")
            seen.add(tool.name)
            tools.append(
                {
                    "name": tool.name,
                    "module": module_name,
                    "description": tool.description or "",
                    "parameters": tool.parameters or {},
                }
            )

    tools.sort(key=lambda item: (item["module"], item["name"]))
    return {
        "version": MANIFEST_VERSION,
        "generated_by": "scripts/generate_tool_manifest.py",
        "tools": tools,
    }


def render_manifest(data: dict[str, Any]) -> str:
    """Return deterministic manifest JSON."""
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if the committed manifest is stale")
    args = parser.parse_args()

    rendered = render_manifest(build_manifest())
    if args.check:
        current = MANIFEST_PATH.read_text(encoding="utf-8") if MANIFEST_PATH.exists() else ""
        if current != rendered:
            print("tools_manifest.json is stale; run scripts/generate_tool_manifest.py", file=sys.stderr)
            return 1
        return 0

    MANIFEST_PATH.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
