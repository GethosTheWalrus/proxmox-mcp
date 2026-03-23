"""Node management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register node management tools."""

    @mcp.tool()
    def list_nodes() -> str:
        """List all nodes in the Proxmox cluster with their status, CPU, memory, and uptime."""
        return format_response(api_request("get", "/nodes"))

    @mcp.tool()
    def get_node_status(node: str) -> str:
        """Get detailed status of a specific node including CPU, memory, disk, uptime, and kernel info.

        Args:
            node: The node name (e.g. 'pve1').
        """
        return format_response(api_request("get", f"/nodes/{node}/status"))

    @mcp.tool()
    def get_node_config(node: str) -> str:
        """Get the configuration of a node (description, wakeonlan, etc.).

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/config"))

    @mcp.tool()
    def get_node_dns(node: str) -> str:
        """Get DNS settings for a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/dns"))

    @mcp.tool()
    def get_node_network(node: str) -> str:
        """Get network interface configuration for a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/network"))

    @mcp.tool()
    def get_node_network_interface(node: str, iface: str) -> str:
        """Get details for a specific network interface.

        Args:
            node: The node name.
            iface: Interface name (e.g. 'vmbr0', 'eth0').
        """
        return format_response(api_request("get", f"/nodes/{node}/network/{iface}"))

    @mcp.tool()
    def create_node_network_interface(
        node: str,
        iface: str,
        type: str,
        address: str = "",
        netmask: str = "",
        gateway: str = "",
        bridge_ports: str = "",
        autostart: bool = True,
        comments: str = "",
    ) -> str:
        """Create a network interface on a node.

        Args:
            node: The node name.
            iface: Interface name (e.g. 'vmbr1').
            type: Interface type (bridge, bond, eth, alias, vlan, OVSBridge, OVSPort, OVSIntPort, OVSBond).
            address: IP address (CIDR notation or IP).
            netmask: Subnet mask.
            gateway: Default gateway.
            bridge_ports: Bridge ports (for bridge type).
            autostart: Whether to start on boot.
            comments: Comments for the interface.
        """
        params: dict = {"iface": iface, "type": type, "autostart": int(autostart)}
        if address:
            params["address"] = address
        if netmask:
            params["netmask"] = netmask
        if gateway:
            params["gateway"] = gateway
        if bridge_ports:
            params["bridge_ports"] = bridge_ports
        if comments:
            params["comments"] = comments
        return format_response(api_request("post", f"/nodes/{node}/network", **params))

    @mcp.tool()
    def list_node_services(node: str) -> str:
        """List all system services on a node (pve, ssh, cron, etc.).

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/services"))

    @mcp.tool()
    def manage_node_service(node: str, service: str, action: str) -> str:
        """Start, stop, restart, or reload a system service on a node.

        Args:
            node: The node name.
            service: Service name (e.g. 'pvedaemon', 'pveproxy', 'ssh', 'cron', 'postfix').
            action: One of 'start', 'stop', 'restart', 'reload'.
        """
        if action not in ("start", "stop", "restart", "reload"):
            return "Error: action must be one of: start, stop, restart, reload"
        return format_response(api_request("post", f"/nodes/{node}/services/{service}/{action}"))

    @mcp.tool()
    def get_node_syslog(node: str, limit: int = 50, start: int = 0, since: str = "", until: str = "") -> str:
        """Read system log (syslog) entries from a node.

        Args:
            node: The node name.
            limit: Max number of log lines to return (default 50).
            start: Start line number.
            since: Only show entries since this date (YYYY-MM-DD).
            until: Only show entries until this date (YYYY-MM-DD).
        """
        params: dict = {"limit": limit, "start": start}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        return format_response(api_request("get", f"/nodes/{node}/syslog", **params))

    @mcp.tool()
    def get_node_journal(node: str, lastentries: int = 50, since: str = "", until: str = "", startcursor: str = "") -> str:
        """Read systemd journal entries from a node.

        Args:
            node: The node name.
            lastentries: Max number of entries (default 50).
            since: Show entries since date/time.
            until: Show entries until date/time.
            startcursor: Start cursor for paging.
        """
        params: dict = {"lastentries": lastentries}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if startcursor:
            params["startcursor"] = startcursor
        return format_response(api_request("get", f"/nodes/{node}/journal", **params))

    @mcp.tool()
    def list_node_tasks(node: str, limit: int = 50, start: int = 0, vmid: int = 0, typefilter: str = "", statusfilter: str = "") -> str:
        """List recent tasks on a node.

        Args:
            node: The node name.
            limit: Max tasks to return (default 50).
            start: Offset for paging.
            vmid: Filter by VM ID (0 = all).
            typefilter: Filter by task type (e.g. 'qmstart', 'vzstart', 'vzcreate').
            statusfilter: Filter by status ('running', 'ok', 'error', etc.).
        """
        params: dict = {"limit": limit, "start": start}
        if vmid:
            params["vmid"] = vmid
        if typefilter:
            params["typefilter"] = typefilter
        if statusfilter:
            params["statusfilter"] = statusfilter
        return format_response(api_request("get", f"/nodes/{node}/tasks", **params))

    @mcp.tool()
    def get_task_status(node: str, upid: str) -> str:
        """Get the status of a specific task by its UPID.

        Args:
            node: The node name.
            upid: The task UPID string.
        """
        return format_response(api_request("get", f"/nodes/{node}/tasks/{upid}/status"))

    @mcp.tool()
    def get_task_log(node: str, upid: str, limit: int = 50, start: int = 0) -> str:
        """Get log output of a specific task.

        Args:
            node: The node name.
            upid: The task UPID string.
            limit: Max lines to return.
            start: Start line number.
        """
        return format_response(api_request("get", f"/nodes/{node}/tasks/{upid}/log", limit=limit, start=start))

    @mcp.tool()
    def stop_task(node: str, upid: str) -> str:
        """Stop (abort) a running task.

        Args:
            node: The node name.
            upid: The task UPID string.
        """
        return format_response(api_request("delete", f"/nodes/{node}/tasks/{upid}"))

    @mcp.tool()
    def get_node_time(node: str) -> str:
        """Get the current time and timezone of a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/time"))

    @mcp.tool()
    def get_node_subscription(node: str) -> str:
        """Get subscription status for a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/subscription"))

    @mcp.tool()
    def get_node_apt_update(node: str) -> str:
        """List available package updates on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/apt/update"))

    @mcp.tool()
    def run_apt_update(node: str) -> str:
        """Refresh the package index on a node (apt update).

        Args:
            node: The node name.
        """
        return format_response(api_request("post", f"/nodes/{node}/apt/update"))

    @mcp.tool()
    def get_node_report(node: str) -> str:
        """Generate a system report for a node (useful for diagnostics).

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/report"))

    @mcp.tool()
    def get_node_disks(node: str) -> str:
        """List physical disks on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/list"))

    @mcp.tool()
    def get_disk_smart(node: str, disk: str) -> str:
        """Get S.M.A.R.T. health data for a disk.

        Args:
            node: The node name.
            disk: Disk device path (e.g. '/dev/sda').
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/smart", disk=disk))

    @mcp.tool()
    def get_node_hardware_pci(node: str) -> str:
        """List PCI hardware devices on a node (for passthrough).

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/hardware/pci"))

    @mcp.tool()
    def get_node_hardware_usb(node: str) -> str:
        """List USB hardware devices on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/hardware/usb"))

    @mcp.tool()
    def get_node_capabilities_qemu(node: str) -> str:
        """Get QEMU capabilities for a node: supported CPU models, machine types, etc.

        Args:
            node: The node name.
        """
        cpu = api_request("get", f"/nodes/{node}/capabilities/qemu/cpu")
        machines = api_request("get", f"/nodes/{node}/capabilities/qemu/machines")
        return format_response({"cpu_models": cpu, "machine_types": machines})

    @mcp.tool()
    def get_node_storage_scan(node: str, scan_type: str, server: str = "") -> str:
        """Scan for available storage targets (NFS, CIFS, iSCSI, LVM, ZFS, PBS).

        Args:
            node: The node name.
            scan_type: Type to scan: 'nfs', 'cifs', 'iscsi', 'lvm', 'lvmthin', 'zfs', 'pbs'.
            server: Server address (required for nfs, cifs, iscsi, pbs).
        """
        params: dict = {}
        if server:
            params["server"] = server
        return format_response(api_request("get", f"/nodes/{node}/scan/{scan_type}", **params))

    @mcp.tool()
    def wakeonlan_node(node: str) -> str:
        """Send a Wake-on-LAN magic packet to a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("post", f"/nodes/{node}/wakeonlan"))

    @mcp.tool()
    def startall_node(node: str, force: bool = False, vms: str = "") -> str:
        """Start all VMs and containers on a node (respecting boot order).

        Args:
            node: The node name.
            force: Force start even if already running.
            vms: Comma-separated list of VMIDs to start (empty = all).
        """
        params: dict = {}
        if force:
            params["force"] = 1
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", f"/nodes/{node}/startall", **params))

    @mcp.tool()
    def stopall_node(node: str, vms: str = "") -> str:
        """Stop all VMs and containers on a node.

        Args:
            node: The node name.
            vms: Comma-separated list of VMIDs to stop (empty = all).
        """
        params: dict = {}
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", f"/nodes/{node}/stopall", **params))

    @mcp.tool()
    def get_node_hosts(node: str) -> str:
        """Get the /etc/hosts file content for a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/hosts"))

    @mcp.tool()
    def get_node_version(node: str) -> str:
        """Get Proxmox VE version information for a specific node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/version"))

    @mcp.tool()
    def get_node_netstat(node: str) -> str:
        """Get network statistics for a node (per-interface traffic).

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/netstat"))

    @mcp.tool()
    def get_node_aplinfo(node: str) -> str:
        """List available appliance templates (LXC templates) that can be downloaded.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/aplinfo"))

    @mcp.tool()
    def download_appliance_template(node: str, storage: str, template: str) -> str:
        """Download an appliance template to local storage.

        Args:
            node: The node name.
            storage: Target storage ID.
            template: Template name to download.
        """
        return format_response(api_request("post", f"/nodes/{node}/aplinfo", storage=storage, template=template))
