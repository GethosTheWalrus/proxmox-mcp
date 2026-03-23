"""Cluster management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register cluster management tools."""

    # ── Cluster Info ──────────────────────────────────────────────────

    @mcp.tool()
    def get_version() -> str:
        """Get the Proxmox VE API version information."""
        return format_response(api_request("get", "/version"))

    @mcp.tool()
    def get_cluster_status() -> str:
        """Get cluster status (nodes online, quorum, HA state)."""
        return format_response(api_request("get", "/cluster/status"))

    @mcp.tool()
    def get_cluster_resources(type: str = "") -> str:
        """List all resources across the cluster (VMs, containers, storage, nodes).

        Args:
            type: Filter by type: 'vm', 'storage', 'node', 'sdn', 'pool' (empty = all).
        """
        params: dict = {}
        if type:
            params["type"] = type
        return format_response(api_request("get", "/cluster/resources", **params))

    @mcp.tool()
    def get_cluster_tasks(limit: int = 50) -> str:
        """List recent tasks across all nodes in the cluster.

        Args:
            limit: Maximum number of tasks to return.
        """
        return format_response(api_request("get", "/cluster/tasks", limit=limit))

    @mcp.tool()
    def get_cluster_log(max_entries: int = 50) -> str:
        """Get the cluster log (recent events).

        Args:
            max_entries: Max log entries.
        """
        return format_response(api_request("get", "/cluster/log", max=max_entries))

    @mcp.tool()
    def get_next_vmid(vmid: int = 0) -> str:
        """Get the next available VMID in the cluster.

        Args:
            vmid: Specific VMID to check availability for (0 = auto-assign).
        """
        params: dict = {}
        if vmid:
            params["vmid"] = vmid
        return format_response(api_request("get", "/cluster/nextid", **params))

    @mcp.tool()
    def get_cluster_options() -> str:
        """Get datacenter/cluster-wide options (keyboard layout, console, language, etc.)."""
        return format_response(api_request("get", "/cluster/options"))

    @mcp.tool()
    def update_cluster_options(
        keyboard: str = "",
        language: str = "",
        console: str = "",
        http_proxy: str = "",
        email_from: str = "",
        max_workers: int = 0,
        description: str = "",
        delete: str = "",
    ) -> str:
        """Update datacenter/cluster-wide options.

        Args:
            keyboard: Keyboard layout (e.g. 'en-us', 'de').
            language: Default language.
            console: Default console viewer: 'applet', 'vv', 'html5', 'xtermjs'.
            http_proxy: HTTP proxy URL.
            email_from: Default email sender address.
            max_workers: Max parallel workers.
            description: Datacenter description.
            delete: Comma-separated settings to delete.
        """
        params: dict = {}
        for key, val in [
            ("keyboard", keyboard), ("language", language), ("console", console),
            ("http-proxy", http_proxy), ("email-from", email_from), ("description", description),
            ("delete", delete),
        ]:
            if val:
                params[key] = val
        if max_workers:
            params["max_workers"] = max_workers
        return format_response(api_request("put", "/cluster/options", **params))

    # ── Cluster Config ────────────────────────────────────────────────

    @mcp.tool()
    def get_cluster_config() -> str:
        """Get the current cluster configuration (corosync, nodes, join info)."""
        return format_response(api_request("get", "/cluster/config"))

    @mcp.tool()
    def get_cluster_config_nodes() -> str:
        """List nodes configured in the cluster."""
        return format_response(api_request("get", "/cluster/config/nodes"))

    @mcp.tool()
    def get_cluster_join_info() -> str:
        """Get info needed to join a node to this cluster."""
        return format_response(api_request("get", "/cluster/config/join"))

    @mcp.tool()
    def join_cluster(hostname: str, fingerprint: str, password: str, nodeid: int = 0, force: bool = False) -> str:
        """Join a node to an existing cluster.

        Args:
            hostname: Hostname/IP of existing cluster node.
            fingerprint: SSL fingerprint of the cluster node.
            password: Root password of the cluster node.
            nodeid: Force specific node ID.
            force: Force join even with warnings.
        """
        params: dict = {"hostname": hostname, "fingerprint": fingerprint, "password": password}
        if nodeid:
            params["nodeid"] = nodeid
        if force:
            params["force"] = 1
        return format_response(api_request("post", "/cluster/config/join", **params))

    @mcp.tool()
    def get_cluster_totem() -> str:
        """Get the corosync totem configuration."""
        return format_response(api_request("get", "/cluster/config/totem"))

    # ── Replication ───────────────────────────────────────────────────

    @mcp.tool()
    def list_replication_jobs() -> str:
        """List all replication jobs in the cluster."""
        return format_response(api_request("get", "/cluster/replication"))

    @mcp.tool()
    def get_replication_job(id: str) -> str:
        """Get a specific replication job configuration.

        Args:
            id: Replication job ID (format: GUEST-JOBNUM, e.g. '100-0').
        """
        return format_response(api_request("get", f"/cluster/replication/{id}"))

    @mcp.tool()
    def create_replication_job(id: str, target: str, type: str = "local", schedule: str = "*/15", comment: str = "", rate: float = 0, disable: bool = False) -> str:
        """Create a storage replication job.

        Args:
            id: Job ID (format: GUEST-JOBNUM, e.g. '100-0').
            target: Target node.
            type: Replication type (currently only 'local').
            schedule: Schedule in systemd calendar format (default '*/15' = every 15 min).
            comment: Description.
            rate: Rate limit in mbps.
            disable: Create disabled.
        """
        params: dict = {"id": id, "target": target, "type": type}
        if schedule != "*/15":
            params["schedule"] = schedule
        if comment:
            params["comment"] = comment
        if rate:
            params["rate"] = rate
        if disable:
            params["disable"] = 1
        return format_response(api_request("post", "/cluster/replication", **params))

    @mcp.tool()
    def delete_replication_job(id: str, force: bool = False, keep: bool = False) -> str:
        """Delete a replication job.

        Args:
            id: Replication job ID.
            force: Force removal (skip cleanup).
            keep: Keep replicated data on target.
        """
        params: dict = {}
        if force:
            params["force"] = 1
        if keep:
            params["keep"] = 1
        return format_response(api_request("delete", f"/cluster/replication/{id}", **params))

    # ── Metrics ───────────────────────────────────────────────────────

    @mcp.tool()
    def list_metric_servers() -> str:
        """List configured metric servers (InfluxDB, Graphite)."""
        return format_response(api_request("get", "/cluster/metrics/server"))

    @mcp.tool()
    def get_metric_server(id: str) -> str:
        """Get metric server configuration.

        Args:
            id: Metric server ID.
        """
        return format_response(api_request("get", f"/cluster/metrics/server/{id}"))

    # ── Notifications ─────────────────────────────────────────────────

    @mcp.tool()
    def list_notification_endpoints() -> str:
        """List all configured notification endpoints (sendmail, gotify, smtp, webhook)."""
        return format_response(api_request("get", "/cluster/notifications/endpoints"))

    @mcp.tool()
    def list_notification_targets() -> str:
        """List all notification targets."""
        return format_response(api_request("get", "/cluster/notifications/targets"))

    @mcp.tool()
    def list_notification_matchers() -> str:
        """List all notification matchers (rules that route notifications)."""
        return format_response(api_request("get", "/cluster/notifications/matchers"))

    @mcp.tool()
    def test_notification_target(name: str) -> str:
        """Send a test notification to a target.

        Args:
            name: Target name.
        """
        return format_response(api_request("post", f"/cluster/notifications/targets/{name}/test"))

    # ── Bulk Actions ──────────────────────────────────────────────────

    @mcp.tool()
    def bulk_start_guests(vms: str = "") -> str:
        """Bulk start guests across the cluster.

        Args:
            vms: Comma-separated list of VMIDs (empty = all).
        """
        params: dict = {}
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", "/cluster/bulk-action/guest/start", **params))

    @mcp.tool()
    def bulk_shutdown_guests(vms: str = "") -> str:
        """Bulk shutdown guests across the cluster.

        Args:
            vms: Comma-separated list of VMIDs (empty = all).
        """
        params: dict = {}
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", "/cluster/bulk-action/guest/shutdown", **params))

    @mcp.tool()
    def bulk_migrate_guests(target: str, vms: str = "") -> str:
        """Bulk migrate guests to a target node.

        Args:
            target: Target node name.
            vms: Comma-separated VMIDs.
        """
        params: dict = {"target": target}
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", "/cluster/bulk-action/guest/migrate", **params))

    # ── Ceph (Cluster Level) ──────────────────────────────────────────

    @mcp.tool()
    def get_ceph_status_cluster() -> str:
        """Get Ceph cluster status (health, monitors, OSDs, PGs)."""
        return format_response(api_request("get", "/cluster/ceph/status"))

    @mcp.tool()
    def get_ceph_metadata() -> str:
        """Get Ceph metadata (versions, services across nodes)."""
        return format_response(api_request("get", "/cluster/ceph/metadata"))

    @mcp.tool()
    def get_ceph_flags() -> str:
        """Get Ceph global flags (noout, noscrub, etc.)."""
        return format_response(api_request("get", "/cluster/ceph/flags"))

    @mcp.tool()
    def set_ceph_flags(flag: str, value: bool) -> str:
        """Set a Ceph global flag.

        Args:
            flag: Flag name (noout, noscrub, nobackfill, norebalance, nodown, noup, etc.).
            value: True to set, False to unset.
        """
        return format_response(api_request("put", f"/cluster/ceph/flags/{flag}", value=int(value)))

    # ── Ceph (Node Level) ─────────────────────────────────────────────

    @mcp.tool()
    def get_ceph_status_node(node: str) -> str:
        """Get Ceph status from a specific node's perspective.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/status"))

    @mcp.tool()
    def list_ceph_osds(node: str) -> str:
        """List Ceph OSDs on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/osd"))

    @mcp.tool()
    def create_ceph_osd(node: str, dev: str, db_dev: str = "", wal_dev: str = "", encrypted: bool = False) -> str:
        """Create a new Ceph OSD on a device.

        Args:
            node: The node name.
            dev: Block device for the OSD (e.g. '/dev/sdb').
            db_dev: Separate block device for DB.
            wal_dev: Separate block device for WAL.
            encrypted: Encrypt the OSD.
        """
        params: dict = {"dev": dev}
        if db_dev:
            params["db_dev"] = db_dev
        if wal_dev:
            params["wal_dev"] = wal_dev
        if encrypted:
            params["encrypted"] = 1
        return format_response(api_request("post", f"/nodes/{node}/ceph/osd", **params))

    @mcp.tool()
    def list_ceph_pools(node: str) -> str:
        """List Ceph pools.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/pool"))

    @mcp.tool()
    def create_ceph_pool(node: str, name: str, size: int = 3, min_size: int = 2, pg_num: int = 128, application: str = "rbd") -> str:
        """Create a new Ceph pool.

        Args:
            node: The node name.
            name: Pool name.
            size: Number of replicas (default 3).
            min_size: Minimum replicas for I/O (default 2).
            pg_num: Number of placement groups (default 128).
            application: Pool application (rbd, cephfs, rgw).
        """
        return format_response(api_request(
            "post", f"/nodes/{node}/ceph/pool",
            name=name, size=size, min_size=min_size, pg_num=pg_num, application=application,
        ))

    @mcp.tool()
    def list_ceph_monitors(node: str) -> str:
        """List Ceph monitors.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/mon"))

    @mcp.tool()
    def list_ceph_managers(node: str) -> str:
        """List Ceph managers.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/mgr"))

    @mcp.tool()
    def list_ceph_mds(node: str) -> str:
        """List Ceph metadata servers (MDS, for CephFS).

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/mds"))

    @mcp.tool()
    def list_ceph_fs(node: str) -> str:
        """List CephFS filesystems.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/fs"))

    @mcp.tool()
    def get_ceph_config(node: str) -> str:
        """Get the raw Ceph configuration.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/cfg/raw"))

    @mcp.tool()
    def get_ceph_crush_rules(node: str) -> str:
        """Get Ceph CRUSH rules.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/rules"))

    # ── Jobs (Scheduled) ──────────────────────────────────────────────

    @mcp.tool()
    def list_scheduled_jobs() -> str:
        """List all scheduled cluster jobs (realm-sync, etc.)."""
        return format_response(api_request("get", "/cluster/jobs"))

    @mcp.tool()
    def list_realm_sync_jobs() -> str:
        """List realm synchronization jobs."""
        return format_response(api_request("get", "/cluster/jobs/realm-sync"))

    # ── Mappings (PCI, USB, Directory) ────────────────────────────────

    @mcp.tool()
    def list_pci_mappings() -> str:
        """List PCI device mappings for passthrough."""
        return format_response(api_request("get", "/cluster/mapping/pci"))

    @mcp.tool()
    def list_usb_mappings() -> str:
        """List USB device mappings for passthrough."""
        return format_response(api_request("get", "/cluster/mapping/usb"))

    @mcp.tool()
    def list_dir_mappings() -> str:
        """List directory mappings."""
        return format_response(api_request("get", "/cluster/mapping/dir"))
