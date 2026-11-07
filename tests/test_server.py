"""Tests for the MCP server entry point and tool registration."""

from unittest.mock import patch


class TestServerImport:
    def test_mcp_server_loads(self):
        """Server module should import and create the FastMCP instance."""
        from proxmox_mcp.server import mcp

        assert mcp is not None
        assert mcp.name == "Proxmox MCP Server"

    def test_all_tools_registered(self):
        """All 297 tools should be registered without duplicates."""
        from proxmox_mcp.server import mcp

        tools = mcp._tool_manager._tools
        assert len(tools) == 297

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
        assert self._count_tools_from_module("nodes") == 36

    def test_qemu_module(self):
        assert self._count_tools_from_module("qemu") == 40

    def test_lxc_module(self):
        assert self._count_tools_from_module("lxc") == 25

    def test_storage_module(self):
        assert self._count_tools_from_module("storage") == 31

    def test_cluster_module(self):
        assert self._count_tools_from_module("cluster") == 49

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


class TestToolRoutingConfig:
    """Test tool routing mode environment variable parsing."""

    def test_is_routed_mode_enabled_values(self):
        from proxmox_mcp.server import _is_routed_mode
        import os

        for val in ["true", "True", "TRUE", "1", "yes", "YES"]:
            with patch.dict(os.environ, {"TOOL_ROUTING": val}):
                assert _is_routed_mode() is True

    def test_is_routed_mode_disabled_values(self):
        from proxmox_mcp.server import _is_routed_mode
        import os

        for val in ["false", "False", "FALSE", "0", "no", "NO", ""]:
            with patch.dict(os.environ, {"TOOL_ROUTING": val}):
                assert _is_routed_mode() is False

    def test_is_routed_mode_unset(self):
        from proxmox_mcp.server import _is_routed_mode
        import os

        with patch.dict(os.environ, {}, clear=True):
            assert _is_routed_mode() is False

    def test_always_visible_tools_default(self):
        from proxmox_mcp.server import _get_always_visible_tools, _DEFAULT_CORE_VISIBLE
        import os

        with patch.dict(os.environ, {}, clear=True):
            assert _get_always_visible_tools() == _DEFAULT_CORE_VISIBLE

    def test_always_visible_tools_custom(self):
        from proxmox_mcp.server import _get_always_visible_tools
        import os

        with patch.dict(os.environ, {"ALWAYS_VISIBLE_TOOLS": "get_version,list_pools"}):
            tools = _get_always_visible_tools()
            assert "get_version" in tools
            assert "list_pools" in tools
            assert "route_tools" in tools
            assert "call_routed_tool" in tools
            assert "proxmox_api_raw" in tools

