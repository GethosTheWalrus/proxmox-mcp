"""High Availability (HA) management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register HA management tools."""

    @mcp.tool()
    def get_ha_status() -> str:
        """Get HA manager status (active, quorum, manager status)."""
        return format_response(api_request("get", "/cluster/ha/status"))

    @mcp.tool()
    def get_ha_manager_status() -> str:
        """Get detailed HA manager status."""
        return format_response(api_request("get", "/cluster/ha/status/manager_status"))

    # ── HA Resources ──────────────────────────────────────────────────

    @mcp.tool()
    def list_ha_resources() -> str:
        """List all HA-managed resources."""
        return format_response(api_request("get", "/cluster/ha/resources"))

    @mcp.tool()
    def get_ha_resource(sid: str) -> str:
        """Get HA resource configuration.

        Args:
            sid: HA resource ID (format: 'type:vmid', e.g. 'vm:100' or 'ct:101').
        """
        return format_response(api_request("get", f"/cluster/ha/resources/{sid}"))

    @mcp.tool()
    def create_ha_resource(
        sid: str,
        group: str = "",
        max_relocate: int = 1,
        max_restart: int = 1,
        state: str = "started",
        comment: str = "",
    ) -> str:
        """Add a resource to HA management.

        Args:
            sid: Resource ID (format: 'type:vmid', e.g. 'vm:100' or 'ct:101').
            group: HA group name.
            max_relocate: Max relocations on failure.
            max_restart: Max restarts on failure.
            state: Desired state: 'started', 'stopped', 'enabled', 'disabled', 'ignored'.
            comment: Description.
        """
        params: dict = {"sid": sid, "max_relocate": max_relocate, "max_restart": max_restart, "state": state}
        if group:
            params["group"] = group
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/ha/resources", **params))

    @mcp.tool()
    def update_ha_resource(
        sid: str,
        group: str = "",
        max_relocate: int = -1,
        max_restart: int = -1,
        state: str = "",
        comment: str = "",
        delete: str = "",
    ) -> str:
        """Update an HA resource configuration.

        Args:
            sid: Resource ID.
            group: HA group name.
            max_relocate: Max relocations (-1 = don't change).
            max_restart: Max restarts (-1 = don't change).
            state: Desired state.
            comment: Description.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if group:
            params["group"] = group
        if max_relocate >= 0:
            params["max_relocate"] = max_relocate
        if max_restart >= 0:
            params["max_restart"] = max_restart
        if state:
            params["state"] = state
        if comment:
            params["comment"] = comment
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/ha/resources/{sid}", **params))

    @mcp.tool()
    def delete_ha_resource(sid: str) -> str:
        """Remove a resource from HA management.

        Args:
            sid: Resource ID (format: 'type:vmid').
        """
        return format_response(api_request("delete", f"/cluster/ha/resources/{sid}"))

    @mcp.tool()
    def migrate_ha_resource(sid: str, node: str) -> str:
        """Request migration of an HA resource to a different node.

        Args:
            sid: Resource ID.
            node: Target node.
        """
        return format_response(api_request("post", f"/cluster/ha/resources/{sid}/migrate", node=node))

    @mcp.tool()
    def relocate_ha_resource(sid: str, node: str) -> str:
        """Request relocation of an HA resource to a different node.

        Args:
            sid: Resource ID.
            node: Target node.
        """
        return format_response(api_request("post", f"/cluster/ha/resources/{sid}/relocate", node=node))

    # ── HA Groups ─────────────────────────────────────────────────────

    @mcp.tool()
    def list_ha_groups() -> str:
        """List HA groups (define which nodes can run HA resources)."""
        return format_response(api_request("get", "/cluster/ha/groups"))

    @mcp.tool()
    def get_ha_group(group: str) -> str:
        """Get HA group configuration.

        Args:
            group: Group ID.
        """
        return format_response(api_request("get", f"/cluster/ha/groups/{group}"))

    @mcp.tool()
    def create_ha_group(
        group: str,
        nodes: str,
        nofailback: bool = False,
        restricted: bool = False,
        comment: str = "",
    ) -> str:
        """Create an HA group.

        Args:
            group: Group ID.
            nodes: Node list with optional priority (e.g. 'node1:2,node2:1' — higher = preferred).
            nofailback: If true, don't fail back to higher-priority nodes once recovered.
            restricted: Only run on nodes in this group (otherwise runs anywhere but prefers group nodes).
            comment: Description.
        """
        params: dict = {"group": group, "nodes": nodes}
        if nofailback:
            params["nofailback"] = 1
        if restricted:
            params["restricted"] = 1
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/ha/groups", **params))

    @mcp.tool()
    def update_ha_group(group: str, nodes: str = "", nofailback: bool = False, restricted: bool = False, comment: str = "", delete: str = "") -> str:
        """Update an HA group.

        Args:
            group: Group ID.
            nodes: Node list with optional priority.
            nofailback: Don't fail back.
            restricted: Only run on group nodes.
            comment: Description.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if nodes:
            params["nodes"] = nodes
        if nofailback:
            params["nofailback"] = 1
        if restricted:
            params["restricted"] = 1
        if comment:
            params["comment"] = comment
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/ha/groups/{group}", **params))

    @mcp.tool()
    def delete_ha_group(group: str) -> str:
        """Delete an HA group.

        Args:
            group: Group ID.
        """
        return format_response(api_request("delete", f"/cluster/ha/groups/{group}"))
