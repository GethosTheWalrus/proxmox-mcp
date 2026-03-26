"""Proxmox API client wrapper providing a shared connection to the Proxmox VE cluster."""

from __future__ import annotations

import json
import os

from proxmoxer import ProxmoxAPI


def _get_client() -> ProxmoxAPI:
    """Create a ProxmoxAPI client from environment variables.

    Supports two auth modes:
      1. API token: PROXMOX_TOKEN_NAME + PROXMOX_TOKEN_VALUE
      2. Password:  PROXMOX_USER + PROXMOX_PASSWORD
    """
    host = os.environ.get("PROXMOX_HOST", "")
    if not host:
        raise RuntimeError("PROXMOX_HOST environment variable is required")

    verify_ssl = os.environ.get("PROXMOX_VERIFY_SSL", "0").lower() in ("1", "true", "yes")
    port = int(os.environ.get("PROXMOX_PORT", "8006"))
    timeout = int(os.environ.get("PROXMOX_TIMEOUT", "30"))

    token_name = os.environ.get("PROXMOX_TOKEN_NAME", "")
    token_value = os.environ.get("PROXMOX_TOKEN_VALUE", "")

    if token_name and token_value:
        return ProxmoxAPI(
            host,
            port=port,
            user=os.environ.get("PROXMOX_USER", "root@pam"),
            token_name=token_name,
            token_value=token_value,
            verify_ssl=verify_ssl,
            timeout=timeout,
            service="PVE",
        )

    password = os.environ.get("PROXMOX_PASSWORD", "")
    user = os.environ.get("PROXMOX_USER", "root@pam")
    if not password:
        raise RuntimeError(
            "Either PROXMOX_TOKEN_NAME+PROXMOX_TOKEN_VALUE or "
            "PROXMOX_USER+PROXMOX_PASSWORD must be set"
        )

    return ProxmoxAPI(
        host,
        port=port,
        user=user,
        password=password,
        verify_ssl=verify_ssl,
        timeout=timeout,
        service="PVE",
    )


_client: ProxmoxAPI | None = None


def get_client() -> ProxmoxAPI:
    """Return a cached Proxmox API client, creating it on first call."""
    global _client
    if _client is None:
        _client = _get_client()
    return _client


def api_request(method: str, path: str, **params) -> dict | list | str:
    """Execute an arbitrary Proxmox API call.

    Args:
        method: HTTP method (get, post, put, delete).
        path: API path, e.g. "/nodes" or "/nodes/pve1/qemu".
        **params: Additional parameters to pass to the API.

    Returns:
        The API response data.
    """
    client = get_client()

    # Walk the path segments to build the proxmoxer resource
    segments = [s for s in path.strip("/").split("/") if s]
    resource = client
    for seg in segments:
        resource = getattr(resource, seg)

    fn = getattr(resource, method.lower())
    result: dict | list | str = fn(**params)

    # proxmoxer returns the data portion already unwrapped
    return result


def format_response(data) -> str:
    """Serialize data to a compact JSON string for MCP tool responses."""
    if isinstance(data, str):
        return data
    return json.dumps(data, indent=2, default=str)
