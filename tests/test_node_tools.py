"""Tests for node management tools."""

import json
import pytest
from unittest.mock import MagicMock

from proxmox_mcp.client import api_request, format_response


class TestNodeTools:
    def test_list_nodes(self, mock_proxmox_client):
        mock_proxmox_client.nodes.get.return_value = [
            {"node": "pve1", "status": "online", "cpu": 0.15},
            {"node": "pve2", "status": "online", "cpu": 0.30},
        ]
        result = api_request("get", "/nodes")
        assert len(result) == 2
        assert result[0]["node"] == "pve1"

    def test_get_node_status(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.status.get.return_value = {
            "uptime": 86400,
            "cpu": 0.05,
            "memory": {"total": 16 * 1024**3, "used": 4 * 1024**3},
        }
        result = api_request("get", "/nodes/pve1/status")
        assert result["uptime"] == 86400

    def test_get_node_network(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.network.get.return_value = [
            {"iface": "vmbr0", "type": "bridge", "address": "10.0.0.1"},
        ]
        result = api_request("get", "/nodes/pve1/network")
        assert result[0]["iface"] == "vmbr0"

    def test_list_node_tasks(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.tasks.get.return_value = [
            {"upid": "UPID:pve1:00001234:...", "type": "qmstart", "status": "OK"},
        ]
        result = api_request("get", "/nodes/pve1/tasks")
        assert result[0]["type"] == "qmstart"

    def test_get_node_dns(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.dns.get.return_value = {
            "dns1": "8.8.8.8",
            "dns2": "8.8.4.4",
            "search": "example.com",
        }
        result = api_request("get", "/nodes/pve1/dns")
        assert result["dns1"] == "8.8.8.8"
