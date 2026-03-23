"""Tests for the MCP server entry point and tool registration."""

import pytest
from unittest.mock import patch, MagicMock


class TestServerImport:
    def test_mcp_server_loads(self):
        """Server module should import and create the FastMCP instance."""
        from proxmox_mcp.server import mcp

        assert mcp is not None
        assert mcp.name == "Proxmox MCP Server"

    def test_all_tools_registered(self):
        """All 286 tools should be registered without duplicates."""
        from proxmox_mcp.server import mcp

        tools = mcp._tool_manager._tools
        assert len(tools) == 286

    def test_no_duplicate_tool_names(self):
        """Tool names should be unique."""
        from proxmox_mcp.server import mcp

        tools = mcp._tool_manager._tools
        names = list(tools.keys())
        assert len(names) == len(set(names)), f"Duplicate tools found: {[n for n in names if names.count(n) > 1]}"


class TestToolModuleRegistration:
    """Verify each tool module's register() function runs without error."""

    def _count_tools_from_module(self, module_name: str) -> int:
        """Count @mcp.tool() decorators by importing and registering a single module."""
        from mcp.server.fastmcp import FastMCP

        test_mcp = FastMCP("test")
        mod = __import__(f"proxmox_mcp.tools.{module_name}", fromlist=["register"])
        mod.register(test_mcp)
        return len(test_mcp._tool_manager._tools)

    def test_nodes_module(self):
        assert self._count_tools_from_module("nodes") == 34

    def test_qemu_module(self):
        assert self._count_tools_from_module("qemu") == 39

    def test_lxc_module(self):
        assert self._count_tools_from_module("lxc") == 25

    def test_storage_module(self):
        assert self._count_tools_from_module("storage") == 26

    def test_cluster_module(self):
        assert self._count_tools_from_module("cluster") == 46

    def test_access_module(self):
        assert self._count_tools_from_module("access") == 27

    def test_backup_module(self):
        assert self._count_tools_from_module("backup") == 11

    def test_firewall_module(self):
        assert self._count_tools_from_module("firewall") == 32

    def test_ha_module(self):
        assert self._count_tools_from_module("ha") == 14

    def test_sdn_module(self):
        assert self._count_tools_from_module("sdn") == 17

    def test_pools_module(self):
        assert self._count_tools_from_module("pools") == 14


class TestMainEntryPoint:
    def test_main_calls_mcp_run(self):
        from proxmox_mcp.server import mcp

        with patch.object(mcp, "run") as mock_run:
            from proxmox_mcp.server import main

            main()
            mock_run.assert_called_once_with(transport="stdio")
