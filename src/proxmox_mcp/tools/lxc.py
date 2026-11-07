"""LXC container management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register LXC container management tools."""

    # ── Listing & Status ──────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_containers(
        node: Annotated[str, Field(description="PVE host node name (e.g., 'pve1').")],
    ) -> str:
        """List all LXC containers on a node with status, memory, CPU, and disk metrics.

        Use when inspecting active or stopped containers on a host.
        To view detailed configuration for a specific container, use get_container_config instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_container_status(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID (CTID, e.g., 101).")],
    ) -> str:
        """Get current runtime status (state, CPU utilization, RAM usage, swap, uptime) of a container.

        Use when checking live operational metrics of a container.
        To list all containers on a node, use list_containers instead.

        Args:
            node: The node name.
            vmid: The container ID (CTID).
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/status/current"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_container_config(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
    ) -> str:
        """Get hardware resources, network interfaces, and settings of an LXC container.

        Use when reviewing container resources, OS templates, or network settings.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/config"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_container_pending(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
    ) -> str:
        """Get pending configuration changes for an LXC container (not yet applied).

        Use when checking staged configuration modifications requiring container restart.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/pending"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_container_interfaces(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
    ) -> str:
        """Get assigned IP addresses (IPv4/IPv6) and MAC addresses for a running LXC container.

        Use when discovering container network addresses.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/interfaces"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_container_rrddata(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
        timeframe: Annotated[str, Field(description="Time range: 'hour', 'day', 'week', 'month', or 'year'.")] = "hour",
    ) -> str:
        """Get RRD metrics history (CPU, memory, network I/O, disk throughput) for a container.

        Use when inspecting historical performance trends of an LXC container.

        Args:
            node: The node name.
            vmid: The container ID.
            timeframe: Time range: 'hour', 'day', 'week', 'month', 'year'.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/rrddata", timeframe=timeframe))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_container_feature(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
        feature: Annotated[str, Field(description="Feature to query ('snapshot', 'clone', 'copy').")],
    ) -> str:
        """Check feature availability (snapshots, cloning) for an LXC container.

        Use when testing if a container storage backend supports snapshot or clone operations.

        Args:
            node: The node name.
            vmid: The container ID.
            feature: Feature to check ('snapshot', 'clone', 'copy').
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/feature", feature=feature))

    # ── Create / Delete ───────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_container(
        node: Annotated[str, Field(description="Target PVE host node name.")],
        vmid: Annotated[int, Field(description="Unique Container ID (CTID, e.g., 101).")],
        ostemplate: Annotated[
            str,
            Field(description="Template volume path (e.g., 'local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst')."),
        ],
        hostname: Annotated[str, Field(description="Container hostname.")] = "",
        password: Annotated[str, Field(description="Root user password.")] = "",
        ssh_public_keys: Annotated[str, Field(description="Newline-delimited SSH public keys.")] = "",
        storage: Annotated[str, Field(description="Target storage pool for rootfs (defaults to 'local').")] = "local",
        rootfs: Annotated[str, Field(description="Rootfs allocation spec (e.g., 'local-lvm:8' for 8GB).")] = "",
        memory: Annotated[int, Field(description="RAM allocation in MB (default 512).")] = 512,
        swap: Annotated[int, Field(description="Swap space in MB (default 512).")] = 512,
        cores: Annotated[int, Field(description="CPU core count (default 1).")] = 1,
        cpulimit: Annotated[float, Field(description="CPU quota limit (0 = unlimited).")] = 0,
        net0: Annotated[str, Field(description="Network interface spec (e.g., 'name=eth0,bridge=vmbr0,ip=dhcp').")] = "",
        nameserver: Annotated[str, Field(description="DNS nameserver IP.")] = "",
        searchdomain: Annotated[str, Field(description="DNS search domain.")] = "",
        onboot: Annotated[bool, Field(description="If True, start container on host boot.")] = False,
        start: Annotated[bool, Field(description="If True, boot container immediately after creation.")] = False,
        unprivileged: Annotated[bool, Field(description="If True, create unprivileged container (recommended for security).")] = True,
        features: Annotated[str, Field(description="Comma-separated feature flags (e.g., 'nesting=1,keyctl=1').")] = "",
        description: Annotated[str, Field(description="Container description or notes.")] = "",
        pool: Annotated[str, Field(description="Resource pool to assign container to.")] = "",
        tags: Annotated[str, Field(description="Semicolon-separated tag strings.")] = "",
        mp0: Annotated[str, Field(description="Additional mount point spec (e.g., 'local-lvm:4,mp=/mnt/data').")] = "",
    ) -> str:
        """Create a new LXC container from an OS template.

        Use when deploying Linux container instances.
        To delete a container, use delete_container instead.

        Args:
            node: The node name.
            vmid: The container ID.
            ostemplate: Template volume (e.g. 'local:vztmpl/debian-12-standard_12.2-1_amd64.tar.zst').
            hostname: Container hostname.
            password: Root password.
            ssh_public_keys: SSH public keys (newline delimited).
            storage: Storage for rootfs (default 'local').
            rootfs: Root filesystem spec (e.g. 'local-lvm:8' for 8GB).
            memory: Memory in MB (default 512).
            swap: Swap in MB (default 512).
            cores: CPU cores (default 1).
            cpulimit: CPU limit (0 = unlimited).
            net0: Network config (e.g. 'name=eth0,bridge=vmbr0,ip=dhcp').
            nameserver: DNS nameserver.
            searchdomain: DNS search domain.
            onboot: Start on host boot.
            start: Start after creation.
            unprivileged: Create an unprivileged container (default True, recommended).
            features: Comma-separated features (e.g. 'nesting=1,keyctl=1').
            description: Container description.
            pool: Resource pool.
            tags: Semicolon-separated tags.
            mp0: Mount point (e.g. 'local-lvm:4,mp=/mnt/data').
        """
        params: dict = {
            "vmid": vmid,
            "ostemplate": ostemplate,
            "memory": memory,
            "swap": swap,
            "cores": cores,
            "unprivileged": int(unprivileged),
        }
        if storage and not rootfs:
            params["storage"] = storage
        for key, val in [
            ("hostname", hostname),
            ("password", password),
            ("ssh-public-keys", ssh_public_keys),
            ("rootfs", rootfs),
            ("net0", net0),
            ("nameserver", nameserver),
            ("searchdomain", searchdomain),
            ("features", features),
            ("description", description),
            ("pool", pool),
            ("tags", tags),
            ("mp0", mp0),
        ]:
            if val:
                params[key] = val
        if cpulimit:
            params["cpulimit"] = cpulimit
        if onboot:
            params["onboot"] = 1
        if start:
            params["start"] = 1
        return format_response(api_request("post", f"/nodes/{node}/lxc", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_container_config(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID.")],
        hostname: Annotated[str, Field(description="Updated hostname.")] = "",
        memory: Annotated[int, Field(description="RAM allocation in MB.")] = 0,
        swap: Annotated[int, Field(description="Swap allocation in MB (-1 to leave unchanged).")] = -1,
        cores: Annotated[int, Field(description="CPU core count.")] = 0,
        cpulimit: Annotated[float, Field(description="CPU quota limit (-1 to leave unchanged).")] = -1,
        net0: Annotated[str, Field(description="Network interface config.")] = "",
        nameserver: Annotated[str, Field(description="DNS nameserver IP.")] = "",
        searchdomain: Annotated[str, Field(description="DNS search domain.")] = "",
        onboot: Annotated[bool | None, Field(description="Set start on host boot.")] = None,
        description: Annotated[str, Field(description="Updated description.")] = "",
        features: Annotated[str, Field(description="Comma-separated feature flags (e.g., 'nesting=1').")] = "",
        tags: Annotated[str, Field(description="Semicolon-separated tags.")] = "",
        delete: Annotated[str, Field(description="Comma-separated keys to remove from config.")] = "",
        extra_config: Annotated[str, Field(description="JSON string or comma-separated key=value pairs for extra LXC config options, such as mount points (e.g. '{\"mp0\": \"local-lvm:8,mp=/data\"}'), secondary network devices, or custom limits.")] = "",
    ) -> str:
        """Update hardware resources, network interface options, or settings of an existing container.

        Use when scaling container RAM/CPU, modifying network options, mount points, or toggling nesting.

        Args:
            node: The node name.
            vmid: The container ID.
            hostname: Container hostname.
            memory: Memory in MB.
            swap: Swap in MB.
            cores: CPU cores.
            cpulimit: CPU limit (0 = unlimited).
            net0: Network config.
            nameserver: DNS nameserver.
            searchdomain: DNS search domain.
            onboot: Start on boot.
            description: Description.
            features: Comma-separated features.
            tags: Semicolon-separated tags.
            delete: Comma-separated list of settings to delete.
            extra_config: JSON string or key=value pairs for extra LXC config (e.g. mount points, net1).
        """
        params: dict = {}
        for key, val in [
            ("hostname", hostname),
            ("net0", net0),
            ("nameserver", nameserver),
            ("searchdomain", searchdomain),
            ("description", description),
            ("features", features),
            ("tags", tags),
            ("delete", delete),
        ]:
            if val:
                params[key] = val
        if memory:
            params["memory"] = memory
        if swap >= 0:
            params["swap"] = swap
        if cores:
            params["cores"] = cores
        if cpulimit >= 0:
            params["cpulimit"] = cpulimit
        if onboot is not None:
            params["onboot"] = int(onboot)
        if extra_config:
            import json as _json
            try:
                parsed_extra = _json.loads(extra_config)
                if isinstance(parsed_extra, dict):
                    params.update(parsed_extra)
            except _json.JSONDecodeError:
                # Support key=value,key2=value2 format fallback
                for item in extra_config.split(","):
                    if "=" in item:
                        k, v = item.split("=", 1)
                        params[k.strip()] = v.strip()
        return format_response(api_request("put", f"/nodes/{node}/lxc/{vmid}/config", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_container(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="LXC container ID to destroy.")],
        purge: Annotated[bool, Field(description="If True, remove from HA, backup schedules, and ACLs.")] = False,
        destroy_unreferenced_disks: Annotated[bool, Field(description="If True, destroy unreferenced disks.")] = True,
        force: Annotated[bool, Field(description="If True, force destroy even if container is running.")] = False,
    ) -> str:
        """Permanently delete an LXC container and purge its rootfs disk volumes.

        Use when decommissioning a container instance.

        Args:
            node: The node name.
            vmid: The container ID.
            purge: Remove from replication, HA, backup and ACLs too.
            destroy_unreferenced_disks: Destroy unreferenced disks.
            force: Force destroy even if running.
        """
        params: dict = {"destroy-unreferenced-disks": int(destroy_unreferenced_disks)}
        if purge:
            params["purge"] = 1
        if force:
            params["force"] = 1
        return format_response(api_request("delete", f"/nodes/{node}/lxc/{vmid}", **params))

    # ── Power Management ──────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def start_container(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
    ) -> str:
        """Power on a stopped LXC container.

        Use when starting a container workload.
        To gracefully stop a container, use shutdown_container instead.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/start"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False))
    def stop_container(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
    ) -> str:
        """Forcefully stop an LXC container immediately (hard kill process).

        Use when a container is un-responsive. Prefer shutdown_container for clean shutdown.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/stop"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def shutdown_container(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
        timeout: Annotated[int, Field(description="Timeout in seconds before force stopping (0 = default).")] = 0,
        force_stop: Annotated[bool, Field(description="If True, force stop after timeout expires.")] = True,
    ) -> str:
        """Gracefully shut down an LXC container via init system.

        Use for clean container shutdowns.
        To force immediate stop, use stop_container instead.

        Args:
            node: The node name.
            vmid: The container ID.
            timeout: Timeout in seconds before force stop.
            force_stop: Force stop after timeout.
        """
        params: dict = {"forceStop": int(force_stop)}
        if timeout:
            params["timeout"] = timeout
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/shutdown", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def reboot_container(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
        timeout: Annotated[int, Field(description="Timeout in seconds for reboot process.")] = 0,
    ) -> str:
        """Reboot an LXC container gracefully.

        Use when applying system package updates inside container.

        Args:
            node: The node name.
            vmid: The container ID.
            timeout: Timeout in seconds.
        """
        params: dict = {}
        if timeout:
            params["timeout"] = timeout
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/reboot", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def suspend_container(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
    ) -> str:
        """Freeze execution of a running LXC container.

        Use when temporarily pausing container processes.
        To unfreeze, use resume_container instead.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/suspend"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def resume_container(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
    ) -> str:
        """Unfreeze execution of a suspended LXC container.

        Use when resuming a paused container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/resume"))

    # ── Clone / Migrate / Template ────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def clone_container(
        node: Annotated[str, Field(description="Source PVE host node name.")],
        vmid: Annotated[int, Field(description="Source LXC container ID.")],
        newid: Annotated[int, Field(description="Target Container ID for the clone.")],
        hostname: Annotated[str, Field(description="Hostname for cloned container.")] = "",
        target: Annotated[str, Field(description="Target node for clone (defaults to same node).")] = "",
        full: Annotated[bool, Field(description="If True, full standalone copy; if False, linked clone.")] = True,
        storage: Annotated[str, Field(description="Target storage pool for full clone.")] = "",
        description: Annotated[str, Field(description="Description for clone.")] = "",
        pool: Annotated[str, Field(description="Resource pool.")] = "",
        snapname: Annotated[str, Field(description="Snapshot name to clone from.")] = "",
    ) -> str:
        """Clone an existing LXC container to create a new instance.

        Use when duplicating container configurations or instantiating from container templates.

        Args:
            node: The source node name.
            vmid: The source container ID.
            newid: ID for the new container.
            hostname: Hostname for the clone.
            target: Target node (default: same node).
            full: Full clone (True) or linked clone (False).
            storage: Target storage for full clone.
            description: Description.
            pool: Resource pool.
            snapname: Snapshot to clone from.
        """
        params: dict = {"newid": newid}
        for key, val in [
            ("hostname", hostname),
            ("target", target),
            ("storage", storage),
            ("description", description),
            ("pool", pool),
            ("snapname", snapname),
        ]:
            if val:
                params[key] = val
        if full:
            params["full"] = 1
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/clone", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def migrate_container(
        node: Annotated[str, Field(description="Source PVE host node name.")],
        vmid: Annotated[int, Field(description="Container ID to migrate.")],
        target: Annotated[str, Field(description="Target PVE host node name.")],
        online: Annotated[bool, Field(description="If True, perform live container migration.")] = False,
        restart: Annotated[bool, Field(description="If True, restart container on target after offline migration.")] = False,
        target_storage: Annotated[str, Field(description="Target storage ID mapping.")] = "",
    ) -> str:
        """Migrate an LXC container to another host node in the cluster.

        Use when rebalancing cluster workloads or evacuating a node for maintenance.

        Args:
            node: The source node.
            vmid: The container ID.
            target: Target node name.
            online: Live migration.
            restart: Restart container after migration (for non-live).
            target_storage: Target storage mapping.
        """
        params: dict = {"target": target}
        if online:
            params["online"] = 1
        if restart:
            params["restart"] = 1
        if target_storage:
            params["target-storage"] = target_storage
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/migrate", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def convert_container_to_template(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="Container ID to convert.")],
    ) -> str:
        """Convert a container into a read-only golden template (irreversible).

        Use when creating custom base container templates for cloning.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/template"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def resize_container_disk(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
        disk: Annotated[str, Field(description="Disk name (e.g., 'rootfs', 'mp0').")],
        size: Annotated[str, Field(description="New size or increment (e.g., '10G', '+2G').")],
    ) -> str:
        """Expand rootfs or mount point volume capacity for an LXC container.

        Use when expanding container disk space. Note that disk shrinking is not supported by LXC.

        Args:
            node: The node name.
            vmid: The container ID.
            disk: Disk name (e.g. 'rootfs', 'mp0').
            size: New size or increment (e.g. '10G', '+2G').
        """
        return format_response(api_request("put", f"/nodes/{node}/lxc/{vmid}/resize", disk=disk, size=size))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def move_container_volume(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="Source container ID.")],
        volume: Annotated[str, Field(description="Volume name (e.g., 'rootfs', 'mp0').")],
        storage: Annotated[str, Field(description="Target storage ID.")] = "",
        target_vmid: Annotated[int, Field(description="Target container ID (to attach volume to another container).")] = 0,
        target_volume: Annotated[str, Field(description="Target volume slot on destination container.")] = "",
        delete_original: Annotated[bool, Field(description="If True, delete original volume after moving.")] = False,
    ) -> str:
        """Move a container disk volume to different storage or attach to another container.

        Use when relocating container rootfs to faster storage pools.

        Args:
            node: The node name.
            vmid: The container ID.
            volume: Volume name (e.g. 'rootfs', 'mp0').
            storage: Target storage.
            target_vmid: Target container ID.
            target_volume: Target volume slot.
            delete_original: Delete original after move.
        """
        params: dict = {"volume": volume}
        if storage:
            params["storage"] = storage
        if target_vmid:
            params["target-vmid"] = target_vmid
        if target_volume:
            params["target-volume"] = target_volume
        if delete_original:
            params["delete"] = 1
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/move_volume", **params))

    # ── Snapshots ─────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_container_snapshots(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
    ) -> str:
        """List snapshots created for an LXC container.

        Use when inspecting container snapshot trees and restore points.
        To create a snapshot, use create_container_snapshot instead.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/snapshot"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_container_snapshot(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
        snapname: Annotated[str, Field(description="Snapshot name (alphanumeric).")],
        description: Annotated[str, Field(description="Snapshot notes or description.")] = "",
    ) -> str:
        """Create a point-in-time snapshot of an LXC container.

        Use before making software changes inside container to allow rollback.
        To revert to a snapshot, use rollback_container_snapshot.

        Args:
            node: The node name.
            vmid: The container ID.
            snapname: Snapshot name.
            description: Snapshot description.
        """
        params: dict = {"snapname": snapname}
        if description:
            params["description"] = description
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/snapshot", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_container_snapshot(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
        snapname: Annotated[str, Field(description="Snapshot name to delete.")],
        force: Annotated[bool, Field(description="If True, force delete snapshot.")] = False,
    ) -> str:
        """Delete a container snapshot file.

        Use when deleting obsolete snapshot restore points.

        Args:
            node: The node name.
            vmid: The container ID.
            snapname: Snapshot name.
            force: Force delete.
        """
        params: dict = {}
        if force:
            params["force"] = 1
        return format_response(api_request("delete", f"/nodes/{node}/lxc/{vmid}/snapshot/{snapname}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False))
    def rollback_container_snapshot(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="Container ID.")],
        snapname: Annotated[str, Field(description="Snapshot name to revert container state to.")],
    ) -> str:
        """Revert LXC container state and rootfs content to a previous snapshot.

        Use when restoring container filesystem state to a previously saved point in time.

        WARNING: Current container state modifications made after the snapshot will be lost.

        Args:
            node: The node name.
            vmid: The container ID.
            snapname: Snapshot name.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/snapshot/{snapname}/rollback"))
