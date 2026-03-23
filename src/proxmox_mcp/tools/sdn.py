"""SDN (Software-Defined Networking) management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register SDN management tools."""

    # ── VNets ─────────────────────────────────────────────────────────

    @mcp.tool()
    def list_sdn_vnets() -> str:
        """List SDN virtual networks (VNets)."""
        return format_response(api_request("get", "/cluster/sdn/vnets"))

    @mcp.tool()
    def get_sdn_vnet(vnet: str) -> str:
        """Get SDN VNet configuration.

        Args:
            vnet: VNet ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/vnets/{vnet}"))

    @mcp.tool()
    def create_sdn_vnet(vnet: str, zone: str, tag: int = 0, alias: str = "", vlanaware: bool = False) -> str:
        """Create an SDN VNet.

        Args:
            vnet: VNet ID.
            zone: Zone ID.
            tag: VLAN tag.
            alias: Display alias.
            vlanaware: Enable VLAN-aware bridge.
        """
        params: dict = {"vnet": vnet, "zone": zone}
        if tag:
            params["tag"] = tag
        if alias:
            params["alias"] = alias
        if vlanaware:
            params["vlanaware"] = 1
        return format_response(api_request("post", "/cluster/sdn/vnets", **params))

    @mcp.tool()
    def update_sdn_vnet(vnet: str, zone: str = "", tag: int = -1, alias: str = "", delete: str = "") -> str:
        """Update an SDN VNet.

        Args:
            vnet: VNet ID.
            zone: Zone ID.
            tag: VLAN tag (-1 = don't change).
            alias: Display alias.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if zone:
            params["zone"] = zone
        if tag >= 0:
            params["tag"] = tag
        if alias:
            params["alias"] = alias
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/sdn/vnets/{vnet}", **params))

    @mcp.tool()
    def delete_sdn_vnet(vnet: str) -> str:
        """Delete an SDN VNet.

        Args:
            vnet: VNet ID.
        """
        return format_response(api_request("delete", f"/cluster/sdn/vnets/{vnet}"))

    # ── VNet Subnets ──────────────────────────────────────────────────

    @mcp.tool()
    def list_sdn_subnets(vnet: str) -> str:
        """List subnets for an SDN VNet.

        Args:
            vnet: VNet ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/vnets/{vnet}/subnets"))

    @mcp.tool()
    def create_sdn_subnet(vnet: str, subnet: str, gateway: str = "", snat: bool = False, dnszoneprefix: str = "") -> str:
        """Create a subnet for an SDN VNet.

        Args:
            vnet: VNet ID.
            subnet: Subnet CIDR (e.g. '10.0.0.0/24').
            gateway: Gateway IP.
            snat: Enable SNAT.
            dnszoneprefix: DNS zone prefix.
        """
        params: dict = {"subnet": subnet, "type": "subnet"}
        if gateway:
            params["gateway"] = gateway
        if snat:
            params["snat"] = 1
        if dnszoneprefix:
            params["dnszoneprefix"] = dnszoneprefix
        return format_response(api_request("post", f"/cluster/sdn/vnets/{vnet}/subnets", **params))

    # ── Zones ─────────────────────────────────────────────────────────

    @mcp.tool()
    def list_sdn_zones() -> str:
        """List SDN zones."""
        return format_response(api_request("get", "/cluster/sdn/zones"))

    @mcp.tool()
    def get_sdn_zone(zone: str) -> str:
        """Get SDN zone configuration.

        Args:
            zone: Zone ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/zones/{zone}"))

    @mcp.tool()
    def create_sdn_zone(zone: str, type: str, nodes: str = "", ipam: str = "", dns: str = "", bridge: str = "", mtu: int = 0) -> str:
        """Create an SDN zone.

        Args:
            zone: Zone ID.
            type: Zone type: 'simple', 'vlan', 'qinq', 'vxlan', 'evpn'.
            nodes: Comma-separated node list.
            ipam: IPAM plugin name.
            dns: DNS plugin name.
            bridge: Bridge name.
            mtu: MTU.
        """
        params: dict = {"zone": zone, "type": type}
        for key, val in [("nodes", nodes), ("ipam", ipam), ("dns", dns), ("bridge", bridge)]:
            if val:
                params[key] = val
        if mtu:
            params["mtu"] = mtu
        return format_response(api_request("post", "/cluster/sdn/zones", **params))

    @mcp.tool()
    def delete_sdn_zone(zone: str) -> str:
        """Delete an SDN zone.

        Args:
            zone: Zone ID.
        """
        return format_response(api_request("delete", f"/cluster/sdn/zones/{zone}"))

    # ── Controllers ───────────────────────────────────────────────────

    @mcp.tool()
    def list_sdn_controllers() -> str:
        """List SDN controllers (e.g. EVPN controller)."""
        return format_response(api_request("get", "/cluster/sdn/controllers"))

    @mcp.tool()
    def get_sdn_controller(controller: str) -> str:
        """Get SDN controller configuration.

        Args:
            controller: Controller ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/controllers/{controller}"))

    # ── IPAM ──────────────────────────────────────────────────────────

    @mcp.tool()
    def list_sdn_ipams() -> str:
        """List IPAM (IP Address Management) plugins."""
        return format_response(api_request("get", "/cluster/sdn/ipams"))

    @mcp.tool()
    def get_sdn_ipam(ipam: str) -> str:
        """Get IPAM plugin configuration.

        Args:
            ipam: IPAM ID.
        """
        return format_response(api_request("get", f"/cluster/sdn/ipams/{ipam}"))

    # ── DNS ───────────────────────────────────────────────────────────

    @mcp.tool()
    def list_sdn_dns() -> str:
        """List SDN DNS plugins."""
        return format_response(api_request("get", "/cluster/sdn/dns"))

    # ── Apply SDN Changes ─────────────────────────────────────────────

    @mcp.tool()
    def apply_sdn_changes() -> str:
        """Apply pending SDN configuration changes to all nodes."""
        return format_response(api_request("put", "/cluster/sdn"))
