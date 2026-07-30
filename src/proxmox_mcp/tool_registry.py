"""Canonical registry of Proxmox MCP domain tool modules."""

from __future__ import annotations

TOOL_MODULES: tuple[str, ...] = (
    "access",
    "backup",
    "cluster",
    "firewall",
    "ha",
    "lxc",
    "nodes",
    "pools",
    "qemu",
    "sdn",
    "storage",
)
