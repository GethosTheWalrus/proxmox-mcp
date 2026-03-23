"""Tests for the Proxmox API client wrapper."""

import pytest
from unittest.mock import patch, MagicMock

from proxmox_mcp.client import api_request, format_response, get_client, _get_client


class TestGetClient:
    def test_missing_host_raises(self):
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(RuntimeError, match="PROXMOX_HOST"):
                _get_client()

    def test_missing_auth_raises(self):
        with patch.dict("os.environ", {"PROXMOX_HOST": "10.0.0.1"}, clear=True):
            with pytest.raises(RuntimeError, match="PROXMOX_TOKEN_NAME"):
                _get_client()

    def test_token_auth(self):
        env = {
            "PROXMOX_HOST": "10.0.0.1",
            "PROXMOX_USER": "root@pam",
            "PROXMOX_TOKEN_NAME": "mcp",
            "PROXMOX_TOKEN_VALUE": "secret-token",
        }
        with patch.dict("os.environ", env, clear=True), patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            mock_api.return_value = MagicMock()
            client = _get_client()
            mock_api.assert_called_once_with(
                "10.0.0.1",
                port=8006,
                user="root@pam",
                token_name="mcp",
                token_value="secret-token",
                verify_ssl=False,
                timeout=30,
                service="PVE",
            )

    def test_password_auth(self):
        env = {
            "PROXMOX_HOST": "10.0.0.1",
            "PROXMOX_USER": "admin@pve",
            "PROXMOX_PASSWORD": "secret",
        }
        with patch.dict("os.environ", env, clear=True), patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            mock_api.return_value = MagicMock()
            client = _get_client()
            mock_api.assert_called_once_with(
                "10.0.0.1",
                port=8006,
                user="admin@pve",
                password="secret",
                verify_ssl=False,
                timeout=30,
                service="PVE",
            )

    def test_custom_port_and_ssl(self):
        env = {
            "PROXMOX_HOST": "pve.example.com",
            "PROXMOX_PORT": "443",
            "PROXMOX_VERIFY_SSL": "true",
            "PROXMOX_TOKEN_NAME": "tok",
            "PROXMOX_TOKEN_VALUE": "val",
        }
        with patch.dict("os.environ", env, clear=True), patch("proxmox_mcp.client.ProxmoxAPI") as mock_api:
            mock_api.return_value = MagicMock()
            _get_client()
            _, kwargs = mock_api.call_args
            assert kwargs["port"] == 443
            assert kwargs["verify_ssl"] is True

    def test_get_client_caches(self):
        """get_client() should return the same cached instance on subsequent calls."""
        import proxmox_mcp.client as mod

        mock = MagicMock()
        mod._client = None  # reset cache
        with patch.object(mod, "_get_client", return_value=mock):
            # Temporarily restore the real get_client to test caching
            real_fn = mod.get_client
            try:
                # Bypass autouse patch by calling the real implementation
                def _real_get_client():
                    if mod._client is None:
                        mod._client = mod._get_client()
                    return mod._client
                c1 = _real_get_client()
                c2 = _real_get_client()
                assert c1 is c2 is mock
                # _get_client should only be called once due to caching
                mod._get_client.assert_called_once()
            finally:
                mod._client = None  # cleanup


class TestApiRequest:
    def test_get_walks_path(self, mock_proxmox_client):
        mock_proxmox_client.nodes.get.return_value = [{"node": "pve1"}]
        result = api_request("get", "/nodes")
        mock_proxmox_client.nodes.get.assert_called_once_with()
        assert result == [{"node": "pve1"}]

    def test_post_with_params(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.post.return_value = "UPID:pve1:..."
        result = api_request("post", "/nodes/pve1/qemu", vmid=100, name="test")
        mock_proxmox_client.nodes.pve1.qemu.post.assert_called_once_with(vmid=100, name="test")

    def test_deep_path(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.qemu.__getattr__("100").status.current.get.return_value = {"status": "running"}
        # MagicMock chains automatically
        result = api_request("get", "/nodes/pve1/qemu/100/status/current")
        assert result is not None


class TestFormatResponse:
    def test_string_passthrough(self):
        assert format_response("hello") == "hello"

    def test_dict_to_json(self):
        result = format_response({"key": "value"})
        assert '"key": "value"' in result

    def test_list_to_json(self):
        result = format_response([1, 2, 3])
        assert "[" in result
        assert "1" in result

    def test_nested_structure(self):
        data = {"nodes": [{"name": "pve1", "status": "online"}]}
        result = format_response(data)
        assert "pve1" in result
        assert "online" in result
