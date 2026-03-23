"""LXC container management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register LXC container management tools."""

    # ── Listing & Status ──────────────────────────────────────────────

    @mcp.tool()
    def list_containers(node: str) -> str:
        """List all LXC containers on a node with status, memory, CPU, and disk info.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc"))

    @mcp.tool()
    def get_container_status(node: str, vmid: int) -> str:
        """Get the current runtime status of a container.

        Args:
            node: The node name.
            vmid: The container ID (CTID).
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/status/current"))

    @mcp.tool()
    def get_container_config(node: str, vmid: int) -> str:
        """Get the configuration of a container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/config"))

    @mcp.tool()
    def get_container_pending(node: str, vmid: int) -> str:
        """Get pending configuration changes for a container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/pending"))

    @mcp.tool()
    def get_container_interfaces(node: str, vmid: int) -> str:
        """Get network interfaces and IPs of a running container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/interfaces"))

    @mcp.tool()
    def get_container_rrddata(node: str, vmid: int, timeframe: str = "hour") -> str:
        """Get RRD statistics data for a container (CPU, memory, disk, network over time).

        Args:
            node: The node name.
            vmid: The container ID.
            timeframe: Time range: 'hour', 'day', 'week', 'month', 'year'.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/rrddata", timeframe=timeframe))

    @mcp.tool()
    def get_container_feature(node: str, vmid: int, feature: str) -> str:
        """Check if a feature is available for a container (snapshot, clone, copy).

        Args:
            node: The node name.
            vmid: The container ID.
            feature: Feature to check ('snapshot', 'clone', 'copy').
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/feature", feature=feature))

    # ── Create / Delete ───────────────────────────────────────────────

    @mcp.tool()
    def create_container(
        node: str,
        vmid: int,
        ostemplate: str,
        hostname: str = "",
        password: str = "",
        ssh_public_keys: str = "",
        storage: str = "local",
        rootfs: str = "",
        memory: int = 512,
        swap: int = 512,
        cores: int = 1,
        cpulimit: float = 0,
        net0: str = "",
        nameserver: str = "",
        searchdomain: str = "",
        onboot: bool = False,
        start: bool = False,
        unprivileged: bool = True,
        features: str = "",
        description: str = "",
        pool: str = "",
        tags: str = "",
        mp0: str = "",
    ) -> str:
        """Create a new LXC container.

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
            ("hostname", hostname), ("password", password),
            ("ssh-public-keys", ssh_public_keys), ("rootfs", rootfs),
            ("net0", net0), ("nameserver", nameserver), ("searchdomain", searchdomain),
            ("features", features), ("description", description), ("pool", pool),
            ("tags", tags), ("mp0", mp0),
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

    @mcp.tool()
    def update_container_config(
        node: str,
        vmid: int,
        hostname: str = "",
        memory: int = 0,
        swap: int = -1,
        cores: int = 0,
        cpulimit: float = -1,
        net0: str = "",
        nameserver: str = "",
        searchdomain: str = "",
        onboot: bool | None = None,
        description: str = "",
        features: str = "",
        tags: str = "",
        delete: str = "",
    ) -> str:
        """Update the configuration of an existing container.

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
        """
        params: dict = {}
        for key, val in [
            ("hostname", hostname), ("net0", net0), ("nameserver", nameserver),
            ("searchdomain", searchdomain), ("description", description),
            ("features", features), ("tags", tags), ("delete", delete),
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
        return format_response(api_request("put", f"/nodes/{node}/lxc/{vmid}/config", **params))

    @mcp.tool()
    def delete_container(node: str, vmid: int, purge: bool = False, destroy_unreferenced_disks: bool = True, force: bool = False) -> str:
        """Delete a container. Must be stopped first unless force=True.

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

    @mcp.tool()
    def start_container(node: str, vmid: int) -> str:
        """Start a container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/start"))

    @mcp.tool()
    def stop_container(node: str, vmid: int) -> str:
        """Hard-stop a container (immediate, like power off).

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/stop"))

    @mcp.tool()
    def shutdown_container(node: str, vmid: int, timeout: int = 0, force_stop: bool = True) -> str:
        """Gracefully shut down a container.

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

    @mcp.tool()
    def reboot_container(node: str, vmid: int, timeout: int = 0) -> str:
        """Reboot a container.

        Args:
            node: The node name.
            vmid: The container ID.
            timeout: Timeout in seconds.
        """
        params: dict = {}
        if timeout:
            params["timeout"] = timeout
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/reboot", **params))

    @mcp.tool()
    def suspend_container(node: str, vmid: int) -> str:
        """Suspend (freeze) a container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/suspend"))

    @mcp.tool()
    def resume_container(node: str, vmid: int) -> str:
        """Resume a suspended container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/status/resume"))

    # ── Clone / Migrate / Template ────────────────────────────────────

    @mcp.tool()
    def clone_container(
        node: str,
        vmid: int,
        newid: int,
        hostname: str = "",
        target: str = "",
        full: bool = True,
        storage: str = "",
        description: str = "",
        pool: str = "",
        snapname: str = "",
    ) -> str:
        """Clone a container.

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
            ("hostname", hostname), ("target", target), ("storage", storage),
            ("description", description), ("pool", pool), ("snapname", snapname),
        ]:
            if val:
                params[key] = val
        if full:
            params["full"] = 1
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/clone", **params))

    @mcp.tool()
    def migrate_container(
        node: str,
        vmid: int,
        target: str,
        online: bool = False,
        restart: bool = False,
        target_storage: str = "",
    ) -> str:
        """Migrate a container to another node.

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

    @mcp.tool()
    def convert_container_to_template(node: str, vmid: int) -> str:
        """Convert a container into a template (irreversible).

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/template"))

    @mcp.tool()
    def resize_container_disk(node: str, vmid: int, disk: str, size: str) -> str:
        """Resize a container disk/volume.

        Args:
            node: The node name.
            vmid: The container ID.
            disk: Disk name (e.g. 'rootfs', 'mp0').
            size: New size or increment (e.g. '10G', '+2G').
        """
        return format_response(api_request("put", f"/nodes/{node}/lxc/{vmid}/resize", disk=disk, size=size))

    @mcp.tool()
    def move_container_volume(node: str, vmid: int, volume: str, storage: str = "", target_vmid: int = 0, target_volume: str = "", delete_original: bool = False) -> str:
        """Move a container volume to different storage or to another container.

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

    @mcp.tool()
    def list_container_snapshots(node: str, vmid: int) -> str:
        """List all snapshots of a container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/snapshot"))

    @mcp.tool()
    def create_container_snapshot(node: str, vmid: int, snapname: str, description: str = "") -> str:
        """Create a snapshot of a container.

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

    @mcp.tool()
    def delete_container_snapshot(node: str, vmid: int, snapname: str, force: bool = False) -> str:
        """Delete a container snapshot.

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

    @mcp.tool()
    def rollback_container_snapshot(node: str, vmid: int, snapname: str) -> str:
        """Rollback a container to a previous snapshot.

        Args:
            node: The node name.
            vmid: The container ID.
            snapname: Snapshot name.
        """
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/snapshot/{snapname}/rollback"))
