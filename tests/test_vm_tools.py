"""Tests for QEMU VM and LXC container tools."""

from unittest.mock import patch

import pytest

from proxmox_mcp.client import api_request
from proxmox_mcp.mcp_compat import MCPServer, get_registered_tool_map
from proxmox_mcp.tools import qemu


class TestQemuTools:
    def test_list_vms(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.get.return_value = [
            {"vmid": 100, "name": "webserver", "status": "running"},
            {"vmid": 101, "name": "database", "status": "stopped"},
        ]
        result = api_request("get", "/nodes/pve1/qemu")
        assert len(result) == 2
        assert result[0]["vmid"] == 100

    def test_get_vm_status(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").status.current.get.return_value = {
            "status": "running",
            "cpu": 0.12,
            "mem": 2147483648,
        }
        result = api_request("get", "/nodes/pve1/qemu/100/status/current")
        assert result is not None

    def test_create_vm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.post.return_value = "UPID:pve1:00001234"
        api_request("post", "/nodes/pve1/qemu", vmid=102, name="test-vm", memory=4096, cores=2)
        mock_proxmox_client.nodes.pve1.qemu.post.assert_called_once_with(
            vmid=102, name="test-vm", memory=4096, cores=2
        )

    def test_start_vm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").status.start.post.return_value = "UPID:..."
        result = api_request("post", "/nodes/pve1/qemu/100/status/start")
        assert result is not None

    def test_delete_vm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").delete.return_value = "UPID:..."
        result = api_request("delete", "/nodes/pve1/qemu/100")
        assert result is not None

    def test_clone_vm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").clone.post.return_value = "UPID:..."
        result = api_request("post", "/nodes/pve1/qemu/100/clone", newid=200, name="clone-vm")
        assert result is not None


class TestLxcTools:
    def test_list_containers(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.lxc.get.return_value = [
            {"vmid": 200, "name": "ct-web", "status": "running"},
        ]
        result = api_request("get", "/nodes/pve1/lxc")
        assert len(result) == 1
        assert result[0]["name"] == "ct-web"

    def test_create_container(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.lxc.post.return_value = "UPID:pve1:..."
        api_request(
            "post", "/nodes/pve1/lxc",
            vmid=201, hostname="test-ct", ostemplate="local:vztmpl/debian-12.tar.zst",
            memory=512, cores=1,
        )
        mock_proxmox_client.nodes.pve1.lxc.post.assert_called_once()

    def test_delete_container(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.lxc.__getattr__("200").delete.return_value = "UPID:..."
        result = api_request("delete", "/nodes/pve1/lxc/200")
        assert result is not None


class TestVmAgentExec:
    def _tool(self):
        server = MCPServer("test")
        qemu.register(server)
        return get_registered_tool_map(server)["vm_agent_exec"]

    def test_string_command_is_split(self):
        tool = self._tool()
        with patch.object(qemu, "api_request", return_value={}) as request:
            tool.fn(node="pve1", vmid=100, command="uname -a")

        request.assert_called_once_with(
            "post", "/nodes/pve1/qemu/100/agent/exec", command=["uname", "-a"]
        )

    def test_list_command_is_passed_through_without_mutation(self):
        tool = self._tool()
        command = ["C:\\Program Files\\App\\app.exe", "--flag"]
        original = list(command)

        with patch.object(qemu, "api_request", return_value={}) as request:
            tool.fn(node="pve1", vmid=100, command=command)

        request.assert_called_once_with(
            "post",
            "/nodes/pve1/qemu/100/agent/exec",
            command=["C:\\Program Files\\App\\app.exe", "--flag"],
        )
        assert command == original

    def test_quoted_shell_pipeline_is_split(self):
        tool = self._tool()
        with patch.object(qemu, "api_request", return_value={}) as request:
            tool.fn(node="pve1", vmid=100, command='/bin/sh -c "ls -la | wc -l"')

        request.assert_called_once_with(
            "post",
            "/nodes/pve1/qemu/100/agent/exec",
            command=["/bin/sh", "-c", "ls -la | wc -l"],
        )

    def test_quoted_windows_path_in_string_form_is_split(self):
        tool = self._tool()
        with patch.object(qemu, "api_request", return_value={}) as request:
            tool.fn(node="pve1", vmid=100, command=r'"C:\Program Files\App\app.exe" --flag')

        request.assert_called_once_with(
            "post",
            "/nodes/pve1/qemu/100/agent/exec",
            command=["C:\\Program Files\\App\\app.exe", "--flag"],
        )

    def test_input_data_is_forwarded(self):
        tool = self._tool()
        with patch.object(qemu, "api_request", return_value={}) as request:
            tool.fn(node="pve1", vmid=100, command=["echo", "hello"], input_data="hello")

        request.assert_called_once_with(
            "post",
            "/nodes/pve1/qemu/100/agent/exec",
            command=["echo", "hello"],
            **{"input-data": "hello"},
        )

    @pytest.mark.parametrize("command", ["", []])
    def test_empty_command_raises(self, command):
        tool = self._tool()
        with patch.object(qemu, "api_request", return_value={}) as request:
            with pytest.raises(ValueError, match="command must not be empty"):
                tool.fn(node="pve1", vmid=100, command=command)

        request.assert_not_called()
