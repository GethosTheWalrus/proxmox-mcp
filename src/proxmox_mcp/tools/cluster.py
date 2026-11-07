"""Cluster management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register cluster management tools."""

    # ── Cluster Info ──────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_version() -> str:
        """Get Proxmox VE API release version, repository channel, and build info.

        Use when checking cluster API capabilities or PVE version information.
        """
        return format_response(api_request("get", "/version"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_status() -> str:
        """Get cluster health, quorum status, voting membership, and node online states.

        Use when verifying cluster quorum and node availability.
        To view specific node details, use get_node_status in nodes module.
        """
        return format_response(api_request("get", "/cluster/status"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_resources(
        type: Annotated[
            str,
            Field(description="Filter resource type: 'vm', 'storage', 'node', 'sdn', or 'pool'. Empty string returns all resources."),
        ] = "",
    ) -> str:
        """List all virtual machines, LXC containers, storage backends, and host nodes across the cluster.

        Use when discovering resources or searching for VMIDs across nodes.

        Args:
            type: Filter by type: 'vm', 'storage', 'node', 'sdn', 'pool' (empty = all).
        """
        params: dict = {}
        if type:
            params["type"] = type
        return format_response(api_request("get", "/cluster/resources", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_tasks(
        limit: Annotated[int, Field(description="Max task records to return.")] = 50,
    ) -> str:
        """List recent asynchronous task history across all nodes in the cluster.

        Use when auditing cluster-wide operations and long-running tasks.
        To list tasks on a specific host node, use list_node_tasks instead.

        Args:
            limit: Maximum number of tasks to return.
        """
        return format_response(api_request("get", "/cluster/tasks", limit=limit))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_log(
        max_entries: Annotated[int, Field(description="Max log entries to return.")] = 50,
    ) -> str:
        """Get cluster-wide log events (corosync, node joins, HA state changes).

        Use when inspecting cluster audit logs and state changes.

        Args:
            max_entries: Max log entries.
        """
        return format_response(api_request("get", "/cluster/log", max=max_entries))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_next_vmid(
        vmid: Annotated[int, Field(description="Optional specific VMID to test availability for (0 = auto-assign next ID).")] = 0,
    ) -> str:
        """Get the next unused VMID in the cluster for provisioning new guests.

        Use when allocating a free VMID prior to VM or LXC container creation.

        Args:
            vmid: Specific VMID to check availability for (0 = auto-assign).
        """
        params: dict = {}
        if vmid:
            params["vmid"] = vmid
        return format_response(api_request("get", "/cluster/nextid", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_options() -> str:
        """Get datacenter options (keyboard layout, HTML5 console preferences, HTTP proxy, notification defaults).

        Use when checking cluster-wide defaults.
        To modify datacenter settings, use update_cluster_options.
        """
        return format_response(api_request("get", "/cluster/options"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_cluster_options(
        keyboard: Annotated[str, Field(description="Default keyboard layout (e.g., 'en-us', 'de').")] = "",
        language: Annotated[str, Field(description="Default UI language code.")] = "",
        console: Annotated[str, Field(description="Default console viewer: 'applet', 'vv', 'html5', 'xtermjs'.")] = "",
        http_proxy: Annotated[str, Field(description="HTTP proxy URL.")] = "",
        email_from: Annotated[str, Field(description="Default sender email address.")] = "",
        max_workers: Annotated[int, Field(description="Max parallel workers.")] = 0,
        description: Annotated[str, Field(description="Datacenter description.")] = "",
        delete: Annotated[str, Field(description="Comma-separated settings to remove.")] = "",
    ) -> str:
        """Update datacenter/cluster-wide configuration options.

        Use when configuring console viewers, HTTP proxies, or notification email senders.

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
            ("keyboard", keyboard),
            ("language", language),
            ("console", console),
            ("http-proxy", http_proxy),
            ("email-from", email_from),
            ("description", description),
            ("delete", delete),
        ]:
            if val:
                params[key] = val
        if max_workers:
            params["max_workers"] = max_workers
        return format_response(api_request("put", "/cluster/options", **params))

    # ── Cluster Config ────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_config() -> str:
        """Get corosync cluster membership and network ring configuration.

        Use when reviewing cluster corosync topology.
        """
        return format_response(api_request("get", "/cluster/config"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_config_nodes() -> str:
        """List member nodes configured in corosync cluster config.

        Use when checking registered corosync node IDs and addresses.
        """
        return format_response(api_request("get", "/cluster/config/nodes"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_join_info() -> str:
        """Get encoded cluster join parameters and SSL fingerprints.

        Use when preparing a standalone PVE node to join this cluster.
        To execute the join, use join_cluster.
        """
        return format_response(api_request("get", "/cluster/config/join"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def join_cluster(
        hostname: Annotated[str, Field(description="Hostname or IP of existing cluster node.")],
        fingerprint: Annotated[str, Field(description="SSL certificate fingerprint of the target cluster node.")],
        password: Annotated[str, Field(description="Root password of the target cluster node.")],
        nodeid: Annotated[int, Field(description="Specific node ID to request (0 = auto-assign).")] = 0,
        force: Annotated[bool, Field(description="If True, force join even with configuration warnings.")] = False,
    ) -> str:
        """Join local PVE host to an existing Proxmox VE cluster.

        Use when expanding cluster node membership.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_cluster_totem() -> str:
        """Get corosync totem protocol options (crypto cipher, hash algorithm, retransmit limits).

        Use when auditing low-level cluster communications.
        """
        return format_response(api_request("get", "/cluster/config/totem"))

    # ── Replication ───────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_replication_jobs() -> str:
        """List storage replication jobs configured across cluster nodes.

        Use when auditing storage replication schedules for guests.
        To view specific job settings, use get_replication_job.
        """
        return format_response(api_request("get", "/cluster/replication"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_replication_job(
        id: Annotated[str, Field(description="Replication job ID formatted as 'GUEST-JOBNUM' (e.g., '100-0').")],
    ) -> str:
        """Get target node, schedule, and state for a storage replication job.

        Use when inspecting guest storage replication configurations.

        Args:
            id: Replication job ID (format: GUEST-JOBNUM, e.g. '100-0').
        """
        return format_response(api_request("get", f"/cluster/replication/{id}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_replication_job(
        id: Annotated[str, Field(description="Job ID formatted as 'GUEST-JOBNUM' (e.g., '100-0').")],
        target: Annotated[str, Field(description="Target PVE host node name for replication.")],
        type: Annotated[str, Field(description="Replication type (currently 'local').")] = "local",
        schedule: Annotated[str, Field(description="Systemd calendar format schedule (default '*/15' = every 15 mins).")] = "*/15",
        comment: Annotated[str, Field(description="Optional job description.")] = "",
        rate: Annotated[float, Field(description="Bandwidth rate limit in MB/s (0 = unlimited).")] = 0,
        disable: Annotated[bool, Field(description="If True, create job in disabled state.")] = False,
    ) -> str:
        """Create a new storage replication job for a ZFS-backed guest.

        Use when setting up high-frequency ZFS storage replication between nodes.
        To delete a job, use delete_replication_job.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_replication_job(
        id: Annotated[str, Field(description="Replication job ID to delete.")],
        force: Annotated[bool, Field(description="If True, force removal without target cleanup.")] = False,
        keep: Annotated[bool, Field(description="If True, retain replicated dataset snapshots on target node.")] = False,
    ) -> str:
        """Delete a storage replication job.

        Use when stopping automated guest storage replication.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_replication_job(
        id: Annotated[str, Field(description="Replication job ID formatted as 'GUEST-JOBNUM' (e.g., '100-0').")],
        schedule: Annotated[str, Field(description="Systemd calendar format schedule (e.g., '*/15', 'daily', '22:00').")] = "",
        rate: Annotated[float, Field(description="Bandwidth rate limit in MB/s (0 = leave unchanged or unlimited).")] = 0,
        comment: Annotated[str, Field(description="Updated job description.")] = "",
        disable: Annotated[bool | None, Field(description="Set True to disable job, False to enable.")] = None,
        delete: Annotated[str, Field(description="Comma-separated properties to delete from config (e.g., 'rate,comment').")] = "",
    ) -> str:
        """Update schedule, bandwidth rate limit, or enabled state for a storage replication job.

        Use when tuning ZFS replication frequency or disabling replication during maintenance.

        Args:
            id: Replication job ID (format: GUEST-JOBNUM, e.g. '100-0').
            schedule: Schedule in systemd calendar format.
            rate: Rate limit in MB/s.
            comment: Description.
            disable: True to disable, False to enable.
            delete: Comma-separated list of properties to remove.
        """
        params: dict = {}
        if schedule:
            params["schedule"] = schedule
        if rate > 0:
            params["rate"] = rate
        if comment:
            params["comment"] = comment
        if disable is not None:
            params["disable"] = 1 if disable else 0
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/replication/{id}", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_replication_log(
        id: Annotated[str, Field(description="Replication job ID formatted as 'GUEST-JOBNUM' (e.g., '100-0').")],
        start: Annotated[int, Field(description="Line number to start reading logs from.")] = 0,
        limit: Annotated[int, Field(description="Maximum number of log lines to retrieve (default 50).")] = 50,
    ) -> str:
        """Get execution logs for a storage replication job.

        Use when diagnosing ZFS replication errors, snapshot sync failures, or transfer delays.

        Args:
            id: Replication job ID (format: GUEST-JOBNUM, e.g. '100-0').
            start: Starting log line offset.
            limit: Maximum log lines to return.
        """
        params: dict = {}
        if start > 0:
            params["start"] = start
        if limit > 0:
            params["limit"] = limit
        return format_response(api_request("get", f"/cluster/replication/{id}/log", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_replication_status(
        id: Annotated[str, Field(description="Replication job ID formatted as 'GUEST-JOBNUM' (e.g., '100-0').")],
    ) -> str:
        """Get real-time operational status for a storage replication job.

        Use when inspecting replication run state, last sync timestamp, and failure counters.

        Args:
            id: Replication job ID (format: GUEST-JOBNUM, e.g. '100-0').
        """
        return format_response(api_request("get", f"/cluster/replication/{id}/status"))

    # ── Metrics ───────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_metric_servers() -> str:
        """List metric exporter backends (InfluxDB, Graphite) configured in cluster.

        Use when reviewing external metric stream targets.
        """
        return format_response(api_request("get", "/cluster/metrics/server"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_metric_server(
        id: Annotated[str, Field(description="Metric server ID.")],
    ) -> str:
        """Get configuration properties for a metric exporter server.

        Use when inspecting metric target URLs and protocols.

        Args:
            id: Metric server ID.
        """
        return format_response(api_request("get", f"/cluster/metrics/server/{id}"))

    # ── Notifications ─────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_notification_endpoints() -> str:
        """List configured notification endpoints (Sendmail, Gotify, SMTP, Webhook).

        Use when reviewing notification delivery channels.
        """
        return format_response(api_request("get", "/cluster/notifications/endpoints"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_notification_targets() -> str:
        """List notification target destinations.

        Use when inspecting notification channels.
        To send a test alert, use test_notification_target.
        """
        return format_response(api_request("get", "/cluster/notifications/targets"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_notification_matchers() -> str:
        """List notification matchers (routing rules based on severity, domain, or event type).

        Use when reviewing alert routing rules.
        """
        return format_response(api_request("get", "/cluster/notifications/matchers"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def test_notification_target(
        name: Annotated[str, Field(description="Notification target name.")],
    ) -> str:
        """Send a test notification message to a target endpoint.

        Use when verifying alert delivery.

        Args:
            name: Target name.
        """
        return format_response(api_request("post", f"/cluster/notifications/targets/{name}/test"))

    # ── Bulk Actions ──────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def bulk_start_guests(
        vms: Annotated[str, Field(description="Comma-separated VMIDs to start (empty string starts all cluster guests).")] = "",
    ) -> str:
        """Bulk start virtual machines and LXC containers across the cluster respecting boot order.

        Use when restoring cluster workload operations after maintenance.

        Args:
            vms: Comma-separated list of VMIDs (empty = all).
        """
        params: dict = {}
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", "/cluster/bulk-action/guest/start", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def bulk_shutdown_guests(
        vms: Annotated[str, Field(description="Comma-separated VMIDs to shut down (empty string shuts down all guests).")] = "",
    ) -> str:
        """Bulk shut down virtual machines and LXC containers across the cluster.

        Use when executing orderly datacenter power-down procedures.

        Args:
            vms: Comma-separated list of VMIDs (empty = all).
        """
        params: dict = {}
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", "/cluster/bulk-action/guest/shutdown", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def bulk_migrate_guests(
        target: Annotated[str, Field(description="Target PVE host node name.")],
        vms: Annotated[str, Field(description="Comma-separated VMIDs to migrate.")],
    ) -> str:
        """Bulk migrate guests to a target node.

        Use when evacuating a node or rebalancing cluster workloads.

        Args:
            target: Target node name.
            vms: Comma-separated VMIDs.
        """
        params: dict = {"target": target}
        if vms:
            params["vms"] = vms
        return format_response(api_request("post", "/cluster/bulk-action/guest/migrate", **params))

    # ── Ceph (Cluster Level) ──────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ceph_status_cluster() -> str:
        """Get overall Ceph storage health, monitor status, OSD counts, and Placement Group (PG) states.

        Use when monitoring hyperconverged Ceph cluster health.
        """
        return format_response(api_request("get", "/cluster/ceph/status"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ceph_metadata() -> str:
        """Get Ceph service metadata and daemon versions across all nodes.

        Use when verifying Ceph daemon versions across host nodes.
        """
        return format_response(api_request("get", "/cluster/ceph/metadata"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ceph_flags() -> str:
        """Get Ceph global cluster flags (noout, noscrub, nobackfill, norebalance).

        Use when checking Ceph maintenance flags.
        To modify Ceph flags, use set_ceph_flags.
        """
        return format_response(api_request("get", "/cluster/ceph/flags"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def set_ceph_flags(
        flag: Annotated[str, Field(description="Flag identifier ('noout', 'noscrub', 'nobackfill', 'norebalance', 'nodown', 'noup').")],
        value: Annotated[bool, Field(description="True to set flag, False to clear flag.")],
    ) -> str:
        """Set or clear Ceph cluster maintenance flags.

        Use when pausing Ceph scrubbing or rebalancing during node maintenance.

        Args:
            flag: Flag name (noout, noscrub, nobackfill, norebalance, nodown, noup, etc.).
            value: True to set, False to unset.
        """
        return format_response(api_request("put", f"/cluster/ceph/flags/{flag}", value=int(value)))

    # ── Ceph (Node Level) ─────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ceph_status_node(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """Get Ceph status from a specific node perspective.

        Use when troubleshooting node-local Ceph daemons.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/status"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_ceph_osds(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List Ceph Object Storage Daemons (OSDs) running on a node.

        Use when inspecting OSD drive statuses and utilization on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/osd"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_ceph_osd(
        node: Annotated[str, Field(description="Target PVE host node name.")],
        dev: Annotated[str, Field(description="Primary block device for OSD (e.g., '/dev/sdb').")],
        db_dev: Annotated[str, Field(description="Separate fast block device for RocksDB (e.g., '/dev/nvme0n1p1').")] = "",
        wal_dev: Annotated[str, Field(description="Separate block device for Write-Ahead Log (WAL).")] = "",
        encrypted: Annotated[bool, Field(description="If True, encrypt OSD storage disk.")] = False,
    ) -> str:
        """Create a new Ceph OSD on a physical disk drive.

        Use when expanding Ceph storage capacity on a node.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_ceph_pools(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List Ceph pools configured on the cluster.

        Use when auditing Ceph storage pools and replication sizes.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/pool"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_ceph_pool(
        node: Annotated[str, Field(description="PVE host node name.")],
        name: Annotated[str, Field(description="Ceph pool name.")],
        size: Annotated[int, Field(description="Replication factor (default 3).")] = 3,
        min_size: Annotated[int, Field(description="Minimum required replicas for I/O (default 2).")] = 2,
        pg_num: Annotated[int, Field(description="Placement group count (default 128).")] = 128,
        application: Annotated[str, Field(description="Pool application tag ('rbd', 'cephfs', 'rgw').")] = "rbd",
    ) -> str:
        """Create a new Ceph storage pool.

        Use when creating storage pools for VM disk images (RBD) or CephFS.

        Args:
            node: The node name.
            name: Pool name.
            size: Number of replicas (default 3).
            min_size: Minimum replicas for I/O (default 2).
            pg_num: Number of placement groups (default 128).
            application: Pool application (rbd, cephfs, rgw).
        """
        return format_response(
            api_request(
                "post",
                f"/nodes/{node}/ceph/pool",
                name=name,
                size=size,
                min_size=min_size,
                pg_num=pg_num,
                application=application,
            )
        )

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_ceph_monitors(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List Ceph Monitor (MON) daemons across nodes.

        Use when verifying Ceph monitor quorum.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/mon"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_ceph_managers(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List Ceph Manager (MGR) daemons.

        Use when checking active Ceph manager services.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/mgr"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_ceph_mds(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List Ceph Metadata Server (MDS) daemons for CephFS.

        Use when checking CephFS metadata daemon states.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/mds"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_ceph_fs(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """List CephFS filesystems configured on the cluster.

        Use when auditing CephFS shared filesystem mounts.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/fs"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ceph_config(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """Get raw `ceph.conf` configuration file contents.

        Use when reviewing low-level Ceph cluster options.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/cfg/raw"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_ceph_crush_rules(
        node: Annotated[str, Field(description="PVE node name.")],
    ) -> str:
        """Get Ceph CRUSH map placement rules.

        Use when inspecting failure domains and disk tiering rules in Ceph.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/ceph/rules"))

    # ── Jobs (Scheduled) ──────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_scheduled_jobs() -> str:
        """List all scheduled background cluster jobs.

        Use when reviewing scheduled datacenter tasks.
        """
        return format_response(api_request("get", "/cluster/jobs"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_realm_sync_jobs() -> str:
        """List scheduled LDAP/Active Directory user synchronization jobs.

        Use when inspecting scheduled authentication realm syncs.
        """
        return format_response(api_request("get", "/cluster/jobs/realm-sync"))

    # ── Mappings (PCI, USB, Directory) ────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_pci_mappings() -> str:
        """List cluster PCI hardware device mappings for hardware passthrough.

        Use when reviewing hardware passthrough aliases (e.g. GPU mappings).
        """
        return format_response(api_request("get", "/cluster/mapping/pci"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_usb_mappings() -> str:
        """List cluster USB hardware device mappings for hardware passthrough.

        Use when inspecting shared USB device aliases.
        """
        return format_response(api_request("get", "/cluster/mapping/usb"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_dir_mappings() -> str:
        """List cluster directory mappings for shared storage/container mounts.

        Use when reviewing cluster-wide directory mount mappings.
        """
        return format_response(api_request("get", "/cluster/mapping/dir"))
