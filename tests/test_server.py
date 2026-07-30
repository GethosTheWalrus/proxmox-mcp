"""Tests for the MCP server entry point and tool registration."""

import subprocess
import sys

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

        from proxmox_mcp.mcp_compat import get_registered_tool_map

        tools = get_registered_tool_map(mcp)
        assert len(tools) == 286

    def test_no_duplicate_tool_names(self):
        """Tool names should be unique."""
        from proxmox_mcp.server import mcp

        from proxmox_mcp.mcp_compat import get_registered_tool_map

        tools = get_registered_tool_map(mcp)
        names = list(tools.keys())
        assert len(names) == len(set(names)), f"Duplicate tools found: {[n for n in names if names.count(n) > 1]}"


class TestToolModuleRegistration:
    """Verify each tool module's register() function runs without error."""

    def _count_tools_from_module(self, module_name: str) -> int:
        """Count @mcp.tool() decorators by importing and registering a single module."""
        from proxmox_mcp.mcp_compat import MCPServer, get_registered_tool_map

        test_mcp = MCPServer("test")
        mod = __import__(f"proxmox_mcp.tools.{module_name}", fromlist=["register"])
        mod.register(test_mcp)
        return len(get_registered_tool_map(test_mcp))

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


class TestToolRouting:
    def test_routed_mode_import_registers_only_facade_tools(self):
        import importlib
        import proxmox_mcp.server as mod

        try:
            with patch.dict("os.environ", {"TOOL_ROUTING": "true"}):
                mod = importlib.reload(mod)
                mod._install_routing_hooks()

            from proxmox_mcp.mcp_compat import get_registered_tool_map, list_registered_tools

            visible = {tool.name for tool in list_registered_tools(mod.mcp)}
            assert visible == {"route_tools", "call_routed_tool", "proxmox_api_raw"}
            assert set(get_registered_tool_map(mod.mcp)) == visible
        finally:
            importlib.reload(mod)

    def test_route_tools_reports_missing_router_dependency(self):
        import importlib
        import proxmox_mcp.router as router
        import proxmox_mcp.server as mod

        router._router = None
        router._router_error = None
        try:
            with patch.dict("os.environ", {"TOOL_ROUTING": "true"}):
                mod = importlib.reload(mod)
            with patch("proxmox_mcp.router.get_router", return_value=None), patch("proxmox_mcp.router.get_router_error", return_value="fastembed is not installed"):
                result = mod.route_tools("list virtual machines")

            assert "Install proxmox-mcp-server[router]" in result
        finally:
            router._router = None
            router._router_error = None
            importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_call_routed_tool_rejects_invalid_json(self):
        import importlib
        import proxmox_mcp.server as mod

        try:
            with patch.dict("os.environ", {"TOOL_ROUTING": "true"}):
                mod = importlib.reload(mod)
                mod._active_tools = {"list_vms": MagicMock()}
                result = await mod.call_routed_tool("list_vms", "{")
        finally:
            mod._active_tools = {}
            importlib.reload(mod)

        assert "Invalid JSON arguments" in result

    @pytest.mark.asyncio
    async def test_call_routed_tool_lazy_loads_only_target_module(self, mock_proxmox_client):
        import importlib
        import proxmox_mcp.server as mod
        from proxmox_mcp.tool_manifest import load_manifest

        mock_proxmox_client.nodes.pve1.qemu.get.return_value = [{"vmid": 100}]
        try:
            with patch.dict("os.environ", {"TOOL_ROUTING": "true"}):
                mod = importlib.reload(mod)
                mod._active_tools = {"list_vms": load_manifest().by_name["list_vms"]}
                from proxmox_mcp.mcp_compat import get_registered_tool_map

                assert set(get_registered_tool_map(mod.mcp)) == {"route_tools", "call_routed_tool", "proxmox_api_raw"}

                result = await mod.call_routed_tool("list_vms", '{"node": "pve1"}')

            assert "vmid" in result
            assert "qemu" in mod._registered_modules
            assert "access" not in mod._registered_modules
            assert "list_vms" in get_registered_tool_map(mod.mcp)
            visible = {tool.name for tool in await mod.mcp.list_tools()}
            assert visible == {"route_tools", "call_routed_tool", "proxmox_api_raw"}
        finally:
            importlib.reload(mod)

    @pytest.mark.asyncio
    async def test_public_mcp_list_tools_stays_filtered_in_routed_mode(self):
        import importlib
        import proxmox_mcp.server as mod

        try:
            with patch.dict("os.environ", {"TOOL_ROUTING": "true"}):
                mod = importlib.reload(mod)
                tools = await mod.mcp.list_tools()

            assert {tool.name for tool in tools} == {"route_tools", "call_routed_tool", "proxmox_api_raw"}
        finally:
            importlib.reload(mod)

    def test_raw_api_can_be_disabled(self):
        from proxmox_mcp.server import proxmox_api_raw

        with patch.dict("os.environ", {"PROXMOX_DISABLE_RAW_API": "true"}):
            result = proxmox_api_raw("get", "/nodes")

        assert "disabled" in result


class TestToolManifest:
    def test_manifest_is_current(self):
        result = subprocess.run(
            [sys.executable, "scripts/generate_tool_manifest.py", "--check"],
            cwd=".",
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr

    def test_manifest_has_expected_domain_tools(self):
        from proxmox_mcp.tool_manifest import ALWAYS_VISIBLE_TOOLS, load_manifest
        from proxmox_mcp.tool_registry import TOOL_MODULES

        manifest = load_manifest()
        names = [tool.name for tool in manifest.tools]
        assert len(manifest.tools) == 285
        assert len(names) == len(set(names))
        assert not ALWAYS_VISIBLE_TOOLS.intersection(names)
        assert {tool.module for tool in manifest.tools} == set(TOOL_MODULES)
