"""Node management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register node management tools."""

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_nodes() -> str:
        """List all PVE nodes in the Proxmox cluster with status, CPU, memory, and uptime metrics.

        Use when inspecting cluster node health and member host status.
        To view detailed status for a single host node, use get_node_status instead.
        """
        return format_response(api_request("get", "/nodes"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_status(
        node: Annotated[str, Field(description="Target PVE node name (e.g., 'pve1').")],
    ) -> str:
        """Get detailed runtime status of a specific node including CPU load, RAM usage, swap, kernel, and uptime.

        Use when monitoring host node resource utilization or kernel versions.
        To list all nodes in the cluster, use list_nodes instead.

        Args:
            node: The node name (e.g. 'pve1').
        """
        return format_response(api_request("get", f"/nodes/{node}/status"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_config(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """Get node configuration settings (description, Wake-on-LAN MAC address).

        Use when checking host node configuration parameters.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/config"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_dns(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """Get DNS resolvers and search domain settings for a node.

        Use when inspecting node network DNS parameters.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/dns"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_network(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """Get network interface configurations (bridges, bonds, physical interfaces, VLANs) for a node.

        Use when inspecting host network topology.
        To view configuration for a single interface, use get_node_network_interface instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/network"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_network_interface(
        node: Annotated[str, Field(description="PVE node name.")],
        iface: Annotated[str, Field(description="Network interface name (e.g., 'vmbr0', 'eth0').")],
    ) -> str:
        """Get configuration details for a single network interface on a node.

        Use when inspecting bridge ports, IP addresses, or VLAN tags of a network interface.

        Args:
            node: The node name.
            iface: Interface name (e.g. 'vmbr0', 'eth0').
        """
        return format_response(api_request("get", f"/nodes/{node}/network/{iface}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_node_network_interface(
        node: Annotated[str, Field(description="PVE node name.")],
        iface: Annotated[str, Field(description="Interface name to create (e.g., 'vmbr1').")],
        type: Annotated[
            str,
            Field(description="Interface type: 'bridge', 'bond', 'eth', 'alias', 'vlan', 'OVSBridge', 'OVSPort', 'OVSIntPort', 'OVSBond'."),
        ],
        address: Annotated[str, Field(description="IP address in CIDR or dot notation.")] = "",
        netmask: Annotated[str, Field(description="Subnet mask.")] = "",
        gateway: Annotated[str, Field(description="Default gateway IP address.")] = "",
        bridge_ports: Annotated[str, Field(description="Bridge ports for bridge interface (e.g., 'eth0').")] = "",
        autostart: Annotated[bool, Field(description="If True, activate interface on host boot.")] = True,
        comments: Annotated[str, Field(description="Optional comment or description.")] = "",
    ) -> str:
        """Create a new network interface (bridge, VLAN, or bond) on a node.

        Use when creating Linux bridge interfaces for virtual machine networks.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_node_services(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List all systemd services running on a host node and their active statuses.

        Use when auditing host services (pvedaemon, pveproxy, ssh, cron).
        To manage a service state, use manage_node_service instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/services"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def manage_node_service(
        node: Annotated[str, Field(description="Target PVE host node name.")],
        service: Annotated[str, Field(description="Service identifier (e.g., 'pvedaemon', 'pveproxy', 'ssh', 'cron', 'postfix').")],
        action: Annotated[str, Field(description="Lifecycle action: 'start', 'stop', 'restart', or 'reload'.")],
    ) -> str:
        """Start, stop, restart, or reload a system service on a host node.

        Use when restarting Proxmox management services or system daemons.

        Args:
            node: The node name.
            service: Service name (e.g. 'pvedaemon', 'pveproxy', 'ssh', 'cron', 'postfix').
            action: One of 'start', 'stop', 'restart', 'reload'.
        """
        if action not in ("start", "stop", "restart", "reload"):
            return "Error: action must be one of: start, stop, restart, reload"
        return format_response(api_request("post", f"/nodes/{node}/services/{service}/{action}"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_syslog(
        node: Annotated[str, Field(description="PVE node name.")],
        limit: Annotated[int, Field(description="Max log lines to return.")] = 50,
        start: Annotated[int, Field(description="Line offset.")] = 0,
        since: Annotated[str, Field(description="Filter log entries since date (YYYY-MM-DD).")] = "",
        until: Annotated[str, Field(description="Filter log entries until date (YYYY-MM-DD).")] = "",
    ) -> str:
        """Read system log (syslog) entries from a Proxmox host node.

        Use when troubleshooting system error logs and kernel messages.
        To query structured systemd journal entries, use get_node_journal instead.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_journal(
        node: Annotated[str, Field(description="PVE node name.")],
        lastentries: Annotated[int, Field(description="Max entries to return.")] = 50,
        since: Annotated[str, Field(description="Show entries since date/time.")] = "",
        until: Annotated[str, Field(description="Show entries until date/time.")] = "",
        startcursor: Annotated[str, Field(description="Start cursor for pagination.")] = "",
    ) -> str:
        """Read systemd journald log entries for a host node.

        Use when debugging systemd unit failures or service logs.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_node_tasks(
        node: Annotated[str, Field(description="PVE node name.")],
        limit: Annotated[int, Field(description="Max tasks to return.")] = 50,
        start: Annotated[int, Field(description="Offset for pagination.")] = 0,
        vmid: Annotated[int, Field(description="Filter tasks by VM/CT ID.")] = 0,
        typefilter: Annotated[str, Field(description="Filter by task type (e.g., 'qmstart', 'vzstart', 'vzcreate').")] = "",
        statusfilter: Annotated[str, Field(description="Filter by task status ('running', 'ok', 'error').")] = "",
    ) -> str:
        """List active and recent asynchronous tasks on a node.

        Use when auditing VM lifecycle operations, backup jobs, or migrations.
        To inspect status of a specific task, use get_task_status instead.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_task_status(
        node: Annotated[str, Field(description="PVE host node name.")],
        upid: Annotated[str, Field(description="Task Unique Process ID (UPID) string.")],
    ) -> str:
        """Get the execution status and exit code of an asynchronous task by UPID.

        Use when polling long-running tasks (e.g. VM creation or migration) for completion.
        To read full task log output, use get_task_log instead.

        Args:
            node: The node name.
            upid: The task UPID string.
        """
        return format_response(api_request("get", f"/nodes/{node}/tasks/{upid}/status"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_task_log(
        node: Annotated[str, Field(description="PVE node name.")],
        upid: Annotated[str, Field(description="Task UPID string.")],
        limit: Annotated[int, Field(description="Max log lines to return.")] = 50,
        start: Annotated[int, Field(description="Start line number offset.")] = 0,
    ) -> str:
        """Get log output generated during execution of an asynchronous task.

        Use when investigating task errors or progress messages.

        Args:
            node: The node name.
            upid: The task UPID string.
            limit: Max lines to return.
            start: Start line number.
        """
        return format_response(api_request("get", f"/nodes/{node}/tasks/{upid}/log", limit=limit, start=start))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def stop_task(
        node: Annotated[str, Field(description="PVE node name.")],
        upid: Annotated[str, Field(description="UPID string of the task to abort.")],
    ) -> str:
        """Stop or abort a currently running asynchronous task.

        Use when cancelling stuck background tasks or long-running operations.

        Args:
            node: The node name.
            upid: The task UPID string.
        """
        return format_response(api_request("delete", f"/nodes/{node}/tasks/{upid}"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_time(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """Get current system time, UTC offset, and timezone for a node.

        Use when verifying host clock synchronization.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/time"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_subscription(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """Get Proxmox VE subscription status and repository key info for a node.

        Use when checking enterprise repository subscription validity.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/subscription"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_apt_update(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List available software package updates for a node.

        Use when auditing pending system package upgrades.
        To refresh the APT package index, use run_apt_update instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/apt/update"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def run_apt_update(
        node: Annotated[str, Field(description="Target PVE host node name.")],
    ) -> str:
        """Refresh APT package index files on a host node (`apt update`).

        Use prior to checking available software updates.

        Args:
            node: The node name.
        """
        return format_response(api_request("post", f"/nodes/{node}/apt/update"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_report(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """Generate diagnostic system report (hardware, PVE versions, storage config) for a node.

        Use when compiling technical diagnostic reports for support.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/report"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_disks(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List physical block devices (HDDs, SSDs, NVMe drives) attached to a host node.

        Use when discovering raw unpartitioned drives for storage creation.
        To check drive health metrics, use get_disk_smart instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/list"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_disk_smart(
        node: Annotated[str, Field(description="PVE host node name.")],
        disk: Annotated[str, Field(description="Disk device path (e.g., '/dev/sda', '/dev/nvme0n1').")],
    ) -> str:
        """Get S.M.A.R.T. health data, wear level, and bad sector metrics for a physical drive.

        Use when auditing physical drive health and predicting disk failures.

        Args:
            node: The node name.
            disk: Disk device path (e.g. '/dev/sda').
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/smart", disk=disk))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_hardware_pci(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """List physical PCI/PCIe hardware devices (GPUs, NICs, HBA controllers) attached to a node.

        Use when identifying hardware devices for PCI passthrough to VMs.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/hardware/pci"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_hardware_usb(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List physical USB devices attached to a host node.

        Use when identifying USB devices for passthrough to VMs or containers.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/hardware/usb"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_capabilities_qemu(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """Get QEMU hypervisor capabilities: supported CPU models and machine types for a host.

        Use when verifying host CPU feature compatibility before VM deployment.

        Args:
            node: The node name.
        """
        cpu = api_request("get", f"/nodes/{node}/capabilities/qemu/cpu")
        machines = api_request("get", f"/nodes/{node}/capabilities/qemu/machines")
        return format_response({"cpu_models": cpu, "machine_types": machines})

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_storage_scan(
        node: Annotated[str, Field(description="PVE host node name.")],
        scan_type: Annotated[str, Field(description="Scan target type: 'nfs', 'cifs', 'iscsi', 'lvm', 'lvmthin', 'zfs', or 'pbs'.")],
        server: Annotated[str, Field(description="Target server IP or hostname (required for NFS/CIFS/iSCSI/PBS).")] = "",
    ) -> str:
        """Scan remote servers or local drives for available storage targets (NFS exports, iSCSI IQNs, ZFS pools).

        Use when discovering remote exports prior to creating storage pools.

        Args:
            node: The node name.
            scan_type: Type to scan: 'nfs', 'cifs', 'iscsi', 'lvm', 'lvmthin', 'zfs', 'pbs'.
            server: Server address (required for nfs, cifs, iscsi, pbs).
        """
        params: dict = {}
        if server:
            params["server"] = server
        return format_response(api_request("get", f"/nodes/{node}/scan/{scan_type}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def wakeonlan_node(
        node: Annotated[str, Field(description="Node name to power on.")],
    ) -> str:
        """Send a Wake-on-LAN magic packet to power on a offline node.

        Use when powering on powered-off host nodes remotely.

        Args:
            node: The node name.
        """
        return format_response(api_request("post", f"/nodes/{node}/wakeonlan"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False))
    def reboot_node(
        node: Annotated[str, Field(description="PVE host node name to reboot.")],
    ) -> str:
        """Reboot a Proxmox VE host node gracefully.

        Use when applying kernel updates or rebooting a node during maintenance.
        Ensure running VMs and containers have been migrated or cleanly stopped first.

        Args:
            node: PVE host node name.
        """
        return format_response(api_request("post", f"/nodes/{node}/status", command="reboot"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False))
    def shutdown_node(
        node: Annotated[str, Field(description="PVE host node name to power down.")],
    ) -> str:
        """Shut down and power off a Proxmox VE host node.

        Use when decommissioning a host or performing hardware maintenance.
        Ensure running workloads have been evacuated or stopped first.

        Args:
            node: PVE host node name.
        """
        return format_response(api_request("post", f"/nodes/{node}/status", command="shutdown"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def startall_node(
        node: Annotated[str, Field(description="PVE node name.")],
        force: Annotated[bool, Field(description="If True, force start guests even if running.")] = False,
        vms: Annotated[str, Field(description="Comma-separated VMIDs to start (empty string starts all).")] = "",
    ) -> str:
        """Bulk start all virtual machines and LXC containers on a host node in boot order sequence.

        Use when bringing up host workloads after host boot or maintenance.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def stopall_node(
        node: Annotated[str, Field(description="PVE host node name.")],
        vms: Annotated[str, Field(description="Comma-separated VMIDs to stop (empty string stops all).")] = "",
    ) -> str:
        """Bulk shut down all virtual machines and LXC containers on a host node.

        Use when preparing a host node for shutdown or reboot.

        Args:
            node: The node name.
            vms: Comma-separated list of VMIDs to stop (empty = all).
        """
        params: dict = {}
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", f"/nodes/{node}/stopall", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_hosts(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """Get `/etc/hosts` file content for a node.

        Use when checking local host resolution entries.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/hosts"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_version(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """Get Proxmox VE release version, repository channel, and kernel build info.

        Use when checking PVE version information.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/version"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_netstat(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """Get per-interface network traffic statistics (bytes, packets, errors) for a node.

        Use when inspecting network traffic volume across host interfaces.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/netstat"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_aplinfo(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """List available LXC appliance templates ready for download.

        Use when discovering official Linux distribution container templates.
        To download a template, use download_appliance_template instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/aplinfo"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def download_appliance_template(
        node: Annotated[str, Field(description="Target host node name.")],
        storage: Annotated[str, Field(description="Target storage ID.")],
        template: Annotated[str, Field(description="Appliance template name (e.g., 'debian-12-standard_12.2-1_amd64.tar.zst').")],
    ) -> str:
        """Download an LXC appliance template to local storage.

        Use when pulling container OS images for LXC creation.

        Args:
            node: The node name.
            storage: Target storage ID.
            template: Template name to download.
        """
        return format_response(api_request("post", f"/nodes/{node}/aplinfo", storage=storage, template=template))
