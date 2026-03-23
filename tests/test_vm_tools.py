"""Tests for QEMU VM and LXC container tools."""

import json
import pytest
from unittest.mock import MagicMock

from proxmox_mcp.client import api_request, format_response


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
        result = api_request("post", "/nodes/pve1/qemu", vmid=102, name="test-vm", memory=4096, cores=2)
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
        result = api_request(
            "post", "/nodes/pve1/lxc",
            vmid=201, hostname="test-ct", ostemplate="local:vztmpl/debian-12.tar.zst",
            memory=512, cores=1,
        )
        mock_proxmox_client.nodes.pve1.lxc.post.assert_called_once()

    def test_delete_container(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.lxc.__getattr__("200").delete.return_value = "UPID:..."
        result = api_request("delete", "/nodes/pve1/lxc/200")
        assert result is not None
