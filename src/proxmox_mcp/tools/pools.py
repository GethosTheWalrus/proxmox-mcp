"""Pool management and ACME certificate tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register pool and ACME tools."""

    # ── Pools ─────────────────────────────────────────────────────────

    @mcp.tool()
    def list_pools() -> str:
        """List all resource pools."""
        return format_response(api_request("get", "/pools"))

    @mcp.tool()
    def get_pool(poolid: str) -> str:
        """Get pool configuration and members.

        Args:
            poolid: Pool ID.
        """
        return format_response(api_request("get", f"/pools/{poolid}"))

    @mcp.tool()
    def create_pool(poolid: str, comment: str = "") -> str:
        """Create a resource pool.

        Args:
            poolid: Pool ID.
            comment: Description.
        """
        params: dict = {"poolid": poolid}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/pools", **params))

    @mcp.tool()
    def update_pool(poolid: str, comment: str = "", vms: str = "", storage: str = "", delete: bool = False) -> str:
        """Update a resource pool (add/remove members).

        Args:
            poolid: Pool ID.
            comment: Description.
            vms: Comma-separated VMIDs to add/remove.
            storage: Comma-separated storage IDs to add/remove.
            delete: If true, remove the specified vms/storage from the pool instead of adding.
        """
        params: dict = {}
        if comment:
            params["comment"] = comment
        if vms:
            params["vms"] = vms
        if storage:
            params["storage"] = storage
        if delete:
            params["delete"] = 1
        return format_response(api_request("put", f"/pools/{poolid}", **params))

    @mcp.tool()
    def delete_pool(poolid: str) -> str:
        """Delete a resource pool.

        Args:
            poolid: Pool ID.
        """
        return format_response(api_request("delete", f"/pools/{poolid}"))

    # ── ACME (Let's Encrypt Certificates) ─────────────────────────────

    @mcp.tool()
    def list_acme_accounts() -> str:
        """List ACME (Let's Encrypt) accounts."""
        return format_response(api_request("get", "/cluster/acme/account"))

    @mcp.tool()
    def get_acme_account(name: str = "default") -> str:
        """Get ACME account details.

        Args:
            name: Account name (default: 'default').
        """
        return format_response(api_request("get", f"/cluster/acme/account/{name}"))

    @mcp.tool()
    def register_acme_account(contact: str, directory: str = "", name: str = "default", tos_url: str = "") -> str:
        """Register a new ACME account.

        Args:
            contact: Contact email address.
            directory: ACME directory URL (empty = Let's Encrypt production).
            name: Account name.
            tos_url: Terms of service URL to accept.
        """
        params: dict = {"contact": contact, "name": name}
        if directory:
            params["directory"] = directory
        if tos_url:
            params["tos_url"] = tos_url
        return format_response(api_request("post", "/cluster/acme/account", **params))

    @mcp.tool()
    def list_acme_plugins() -> str:
        """List ACME DNS challenge plugins."""
        return format_response(api_request("get", "/cluster/acme/plugins"))

    @mcp.tool()
    def get_acme_plugin(id: str) -> str:
        """Get ACME plugin configuration.

        Args:
            id: Plugin ID.
        """
        return format_response(api_request("get", f"/cluster/acme/plugins/{id}"))

    @mcp.tool()
    def get_acme_directories() -> str:
        """List known ACME directory URLs."""
        return format_response(api_request("get", "/cluster/acme/directories"))

    @mcp.tool()
    def get_acme_tos() -> str:
        """Get the ACME Terms of Service URL."""
        return format_response(api_request("get", "/cluster/acme/tos"))

    @mcp.tool()
    def order_node_certificate(node: str, force: bool = False) -> str:
        """Order/renew ACME certificate for a node.

        Args:
            node: The node name.
            force: Force renewal even if not due.
        """
        params: dict = {}
        if force:
            params["force"] = 1
        return format_response(api_request("post", f"/nodes/{node}/certificates/acme/certificate", **params))

    @mcp.tool()
    def get_node_certificates(node: str) -> str:
        """Get certificate info for a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/certificates/info"))
