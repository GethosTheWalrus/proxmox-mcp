"""Shared fixtures for the Proxmox MCP test suite."""

import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture
def mock_proxmox_client():
    """Create a mock ProxmoxAPI client that supports dynamic attribute access."""
    client = MagicMock()
    # ProxmoxAPI uses chained attribute access: client.nodes.get() -> client.nodes("pve1").qemu.get()
    # MagicMock handles this automatically since __getattr__ returns new MagicMock instances
    return client


@pytest.fixture(autouse=True)
def patch_get_client(mock_proxmox_client):
    """Patch get_client() globally so no real Proxmox connection is attempted."""
    with patch("proxmox_mcp.client.get_client", return_value=mock_proxmox_client):
        yield mock_proxmox_client
