"""Storage management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register storage management tools."""

    # ── Datacenter-Level Storage Configuration ────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_storage(
        type: Annotated[
            str,
            Field(description="Filter by storage backend type (e.g., 'dir', 'lvm', 'lvmthin', 'zfspool', 'nfs', 'cifs', 'iscsi', 'rbd', 'cephfs', 'pbs')."),
        ] = "",
        enabled: Annotated[bool, Field(description="If True, return only enabled storage pools.")] = True,
    ) -> str:
        """List datacenter-level storage pool definitions configured in Proxmox cluster.

        Use when inspecting available storage backends, capacities, and content types.
        To view configuration for a specific storage pool, use get_storage_config instead.

        Args:
            type: Filter by type (dir, lvm, lvmthin, zfspool, nfs, cifs, iscsi, rbd, cephfs, pbs, glusterfs, btrfs).
            enabled: Only show enabled storage (default True).
        """
        params: dict = {}
        if type:
            params["type"] = type
        return format_response(api_request("get", "/storage", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_storage_config(
        storage: Annotated[str, Field(description="Storage identifier (e.g., 'local', 'local-lvm', 'pbs-backup').")],
    ) -> str:
        """Get configuration parameters and backend options for a specific storage pool.

        Use when checking mount points, export paths, or content settings of a storage pool.
        To list all configured storage pools, use list_storage instead.

        Args:
            storage: The storage ID.
        """
        return format_response(api_request("get", f"/storage/{storage}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def create_storage(
        storage: Annotated[str, Field(description="Unique storage pool identifier.")],
        type: Annotated[
            str,
            Field(description="Storage backend type: 'dir', 'lvm', 'lvmthin', 'zfspool', 'nfs', 'cifs', 'iscsi', 'rbd', 'cephfs', 'pbs', 'btrfs'."),
        ],
        path: Annotated[str, Field(description="Filesystem path for directory or NFS storage mounts.")] = "",
        server: Annotated[str, Field(description="NFS, CIFS, iSCSI, or PBS server IP/hostname.")] = "",
        export: Annotated[str, Field(description="NFS export share path (e.g., '/volume1/backups').")] = "",
        vgname: Annotated[str, Field(description="LVM Volume Group name.")] = "",
        thinpool: Annotated[str, Field(description="LVM thin pool name for lvmthin type.")] = "",
        pool: Annotated[str, Field(description="Pool name for ZFS or Ceph RBD/CephFS.")] = "",
        portal: Annotated[str, Field(description="iSCSI portal target address.")] = "",
        target: Annotated[str, Field(description="iSCSI target IQN string.")] = "",
        datastore: Annotated[str, Field(description="Proxmox Backup Server (PBS) datastore name.")] = "",
        content: Annotated[
            str,
            Field(description="Comma-separated content types allowed ('images', 'rootdir', 'vztmpl', 'iso', 'backup', 'snippets', 'import')."),
        ] = "",
        nodes: Annotated[str, Field(description="Comma-separated node list to restrict storage access.")] = "",
        shared: Annotated[bool, Field(description="If True, mark storage as accessible across nodes.")] = False,
        disable: Annotated[bool, Field(description="If True, create storage pool in disabled state.")] = False,
        maxfiles: Annotated[int, Field(description="Max backup files to keep (deprecated; use prune_backups).")] = 0,
        prune_backups: Annotated[str, Field(description="Backup retention spec (e.g., 'keep-daily=7,keep-weekly=4').")] = "",
    ) -> str:
        """Create a new storage pool configuration at datacenter level.

        Use when attaching NFS, LVM, ZFS, or PBS storage to Proxmox.
        To delete a storage pool, use delete_storage instead.

        Args:
            storage: Storage ID.
            type: Storage type: dir, lvm, lvmthin, zfspool, nfs, cifs, iscsi, rbd, cephfs, pbs, glusterfs, btrfs.
            path: File system path (for dir, nfs mounts).
            server: Server IP/hostname (for nfs, cifs, iscsi, pbs, glusterfs, rbd, cephfs).
            export: NFS export path.
            vgname: LVM volume group name.
            thinpool: LVM thin pool name (for lvmthin).
            pool: Pool name (for Ceph RBD/CephFS, ZFS).
            portal: iSCSI portal.
            target: iSCSI target.
            datastore: PBS datastore name.
            content: Comma-separated content types (images, rootdir, vztmpl, iso, backup, snippets, import).
            nodes: Restrict storage to these nodes (comma-separated).
            shared: Mark as shared storage.
            disable: Create disabled.
            maxfiles: Max backup files (0 = unlimited).
            prune_backups: Backup retention policy.
        """
        params: dict = {"storage": storage, "type": type}
        for key, val in [
            ("path", path),
            ("server", server),
            ("export", export),
            ("vgname", vgname),
            ("thinpool", thinpool),
            ("pool", pool),
            ("portal", portal),
            ("target", target),
            ("datastore", datastore),
            ("content", content),
            ("nodes", nodes),
            ("prune-backups", prune_backups),
        ]:
            if val:
                params[key] = val
        if shared:
            params["shared"] = 1
        if disable:
            params["disable"] = 1
        if maxfiles:
            params["maxfiles"] = maxfiles
        return format_response(api_request("post", "/storage", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_storage(
        storage: Annotated[str, Field(description="Storage ID to update.")],
        content: Annotated[str, Field(description="Comma-separated allowed content types.")] = "",
        nodes: Annotated[str, Field(description="Comma-separated allowed nodes.")] = "",
        shared: Annotated[bool | None, Field(description="Update shared status (True/False).")] = None,
        disable: Annotated[bool | None, Field(description="Update disable status (True/False).")] = None,
        prune_backups: Annotated[str, Field(description="Updated backup retention policy.")] = "",
        delete: Annotated[str, Field(description="Comma-separated list of configuration keys to delete.")] = "",
    ) -> str:
        """Update an existing storage pool's content settings, node restrictions, or retention rules.

        Use when enabling content types (e.g. adding ISO support) or altering node accessibility.

        Args:
            storage: The storage ID to update.
            content: Content types (images, rootdir, vztmpl, iso, backup, snippets, import).
            nodes: Allowed nodes (comma-separated).
            shared: Mark as shared.
            disable: Disable this storage.
            prune_backups: Backup retention policy.
            delete: Comma-separated list of settings to delete.
        """
        params: dict = {}
        for key, val in [("content", content), ("nodes", nodes), ("prune-backups", prune_backups), ("delete", delete)]:
            if val:
                params[key] = val
        if shared is not None:
            params["shared"] = int(shared)
        if disable is not None:
            params["disable"] = int(disable)
        return format_response(api_request("put", f"/storage/{storage}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_storage(
        storage: Annotated[str, Field(description="Storage ID to delete from cluster configuration.")],
    ) -> str:
        """Remove a storage pool definition from Proxmox configuration.

        Use when detaching a storage pool. Note that underlying disk files on NFS/ZFS/LVM are not destroyed.

        Args:
            storage: The storage ID.
        """
        return format_response(api_request("delete", f"/storage/{storage}"))

    # ── Node-Level Storage ────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_node_storage(
        node: Annotated[str, Field(description="PVE node name.")],
        content: Annotated[str, Field(description="Filter by content type ('images', 'iso', 'backup', etc.).")] = "",
        enabled: Annotated[bool, Field(description="Only show enabled storage pools.")] = True,
    ) -> str:
        """List active storage pools available on a specific node with runtime capacity and usage metrics.

        Use when evaluating disk space availability on a node before provisioning VMs or container disks.
        To inspect individual volumes on storage, use list_storage_content instead.

        Args:
            node: The node name.
            content: Filter by content type (images, rootdir, vztmpl, iso, backup).
            enabled: Only show enabled storage.
        """
        params: dict = {}
        if content:
            params["content"] = content
        return format_response(api_request("get", f"/nodes/{node}/storage", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_node_storage_status(
        node: Annotated[str, Field(description="PVE host node name.")],
        storage: Annotated[str, Field(description="Storage pool ID.")],
    ) -> str:
        """Get capacity usage metrics (total bytes, used, available, active status) for storage on a node.

        Use when monitoring storage utilization on a host node.

        Args:
            node: The node name.
            storage: The storage ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/status"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_storage_content(
        node: Annotated[str, Field(description="Target PVE node name.")],
        storage: Annotated[str, Field(description="Storage pool ID.")],
        content: Annotated[str, Field(description="Filter content type: 'images', 'rootdir', 'vztmpl', 'iso', 'backup', 'snippets'.")] = "",
        vmid: Annotated[int, Field(description="Filter volumes associated with a specific VM/CT ID.")] = 0,
    ) -> str:
        """List files and disk volumes stored in a storage pool (ISOs, VM disks, container templates, backups).

        Use when locating ISO images, VM disk files, or backup archives on storage.
        To view volume metadata, use get_storage_volume_info instead.

        Args:
            node: The node name.
            storage: The storage ID.
            content: Filter by type: 'images', 'rootdir', 'vztmpl', 'iso', 'backup', 'snippets'.
            vmid: Filter by VM ID.
        """
        params: dict = {}
        if content:
            params["content"] = content
        if vmid:
            params["vmid"] = vmid
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/content", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_storage_volume_info(
        node: Annotated[str, Field(description="PVE node name.")],
        storage: Annotated[str, Field(description="Storage pool ID.")],
        volume: Annotated[str, Field(description="Volume ID (e.g., 'local-lvm:vm-100-disk-0').")],
    ) -> str:
        """Get metadata, size, format, and ownership details for a specific disk volume.

        Use when inspecting volume properties before resize or migration operations.

        Args:
            node: The node name.
            storage: The storage ID.
            volume: The volume ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/content/{volume}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def allocate_storage_volume(
        node: Annotated[str, Field(description="Target PVE host node name.")],
        storage: Annotated[str, Field(description="Storage ID to allocate volume in.")],
        vmid: Annotated[int, Field(description="VM ID to associate the volume with.")],
        filename: Annotated[str, Field(description="Volume name/filename.")],
        size: Annotated[str, Field(description="Volume size specification (e.g., '10G', '500M').")],
        format: Annotated[str, Field(description="Disk format ('raw', 'qcow2', 'vmdk'). Auto-detected if empty.")] = "",
    ) -> str:
        """Allocate a raw or qcow2 virtual disk volume in storage.

        Use when manually pre-allocating virtual disk volumes.
        To delete an allocated volume, use delete_storage_volume instead.

        Args:
            node: The node name.
            storage: The storage ID.
            vmid: VM ID to associate with.
            filename: Volume name.
            size: Volume size (e.g. '10G').
            format: Disk format (raw, qcow2, vmdk). Auto-detected if empty.
        """
        params: dict = {"vmid": vmid, "filename": filename, "size": size}
        if format:
            params["format"] = format
        return format_response(api_request("post", f"/nodes/{node}/storage/{storage}/content", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_storage_volume(
        node: Annotated[str, Field(description="PVE node name.")],
        storage: Annotated[str, Field(description="Storage ID.")],
        volume: Annotated[str, Field(description="Volume ID to delete (e.g., 'local-lvm:vm-100-disk-0').")],
    ) -> str:
        """Permanently delete a disk image, ISO, or template volume from storage.

        Use when cleaning up unattached VM disks, obsolete ISOs, or old backups.

        Args:
            node: The node name.
            storage: The storage ID.
            volume: The volume ID.
        """
        return format_response(api_request("delete", f"/nodes/{node}/storage/{storage}/content/{volume}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def upload_to_storage(
        node: Annotated[str, Field(description="PVE node name.")],
        storage: Annotated[str, Field(description="Storage ID.")],
        content: Annotated[str, Field(description="Content type: 'iso', 'vztmpl', 'snippets', or 'import'.")],
        filename: Annotated[str, Field(description="Target filename on storage.")],
        tmpfilename: Annotated[str, Field(description="Temporary filename for the upload process.")] = "",
    ) -> str:
        """Register file upload metadata to storage.

        Use when initiating file upload operations to Proxmox storage.

        Args:
            node: The node name.
            storage: The storage ID.
            content: Content type: 'iso', 'vztmpl', 'snippets', 'import'.
            filename: Target filename.
            tmpfilename: Temporary filename for the upload.
        """
        params: dict = {"content": content, "filename": filename}
        if tmpfilename:
            params["tmpfilename"] = tmpfilename
        return format_response(api_request("post", f"/nodes/{node}/storage/{storage}/upload", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def download_url_to_storage(
        node: Annotated[str, Field(description="Target host node name.")],
        storage: Annotated[str, Field(description="Target storage ID.")],
        url: Annotated[str, Field(description="HTTP/HTTPS URL to download from (e.g., ISO URL).")],
        content: Annotated[str, Field(description="Content type: 'iso' or 'vztmpl'.")],
        filename: Annotated[str, Field(description="Target filename to save as (e.g., 'ubuntu-22.04.iso').")],
        checksum: Annotated[str, Field(description="Optional expected checksum hash.")] = "",
        checksum_algorithm: Annotated[str, Field(description="Checksum algorithm: 'sha256', 'sha512', or 'md5'.")] = "",
    ) -> str:
        """Download an ISO image or LXC template directly from a URL to storage.

        Use when fetching OS ISOs or container templates directly into Proxmox.

        Args:
            node: The node name.
            storage: The storage ID.
            url: URL to download from.
            content: Content type: 'iso', 'vztmpl'.
            filename: Target filename.
            checksum: Expected checksum.
            checksum_algorithm: Checksum algorithm (sha256, sha512, md5).
        """
        params: dict = {"url": url, "content": content, "filename": filename}
        if checksum:
            params["checksum"] = checksum
        if checksum_algorithm:
            params["checksum-algorithm"] = checksum_algorithm
        return format_response(api_request("post", f"/nodes/{node}/storage/{storage}/download-url", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_storage_rrddata(
        node: Annotated[str, Field(description="PVE node name.")],
        storage: Annotated[str, Field(description="Storage ID.")],
        timeframe: Annotated[str, Field(description="Time range: 'hour', 'day', 'week', 'month', or 'year'.")] = "hour",
    ) -> str:
        """Get RRD metric history for storage read/write bandwidth and IOPS over time.

        Use when analyzing historical performance metrics for storage.

        Args:
            node: The node name.
            storage: The storage ID.
            timeframe: Time range: 'hour', 'day', 'week', 'month', 'year'.
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/rrddata", timeframe=timeframe))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def prune_storage_backups(
        node: Annotated[str, Field(description="PVE host node name.")],
        storage: Annotated[str, Field(description="Storage ID containing backups.")],
        type: Annotated[str, Field(description="Guest type filter: 'qemu' or 'lxc'.")] = "",
        vmid: Annotated[int, Field(description="Filter by specific VM/CT ID.")] = 0,
        prune_backups: Annotated[str, Field(description="Retention spec (e.g., 'keep-last=3,keep-daily=7,keep-weekly=4').")] = "",
        dry_run: Annotated[bool, Field(description="If True, only simulate pruning without deleting files.")] = True,
    ) -> str:
        """Prune old vzdump backup archives according to retention policies.

        Use when executing backup retention policies to reclaim storage space.
        Note: dry_run defaults to True to prevent accidental file deletion.

        Args:
            node: The node name.
            storage: The storage ID.
            type: Guest type filter ('qemu' or 'lxc').
            vmid: Filter by VM ID.
            prune_backups: Retention spec (e.g. 'keep-last=3,keep-daily=7,keep-weekly=4').
            dry_run: If True, only simulate (default True for safety).
        """
        params: dict = {}
        if type:
            params["type"] = type
        if vmid:
            params["vmid"] = vmid
        if prune_backups:
            params["prune-backups"] = prune_backups
        if dry_run:
            return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/prunebackups", **params))
        return format_response(api_request("delete", f"/nodes/{node}/storage/{storage}/prunebackups", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_file_restore(
        node: Annotated[str, Field(description="PVE node name.")],
        storage: Annotated[str, Field(description="Storage ID (PBS or directory storage).")],
        volume: Annotated[str, Field(description="Backup volume ID.")],
        filepath: Annotated[str, Field(description="Directory path inside the backup archive.")] = "/",
    ) -> str:
        """List files inside a Proxmox Backup Server (PBS) volume for single file recovery.

        Use when browsing PBS backup volume file structures.

        Args:
            node: The node name.
            storage: The storage ID.
            volume: The backup volume ID.
            filepath: Path inside the backup to list (default '/').
        """
        return format_response(
            api_request(
                "get",
                f"/nodes/{node}/storage/{storage}/file-restore/list",
                volume=volume,
                filepath=filepath,
            )
        )

    # ── Disk Management ───────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_lvm_volumes(
        node: Annotated[str, Field(description="Target PVE host node name.")],
    ) -> str:
        """List physical LVM Volume Groups (VGs) on a host node.

        Use when auditing host node LVM disk structures.
        To view thin pool allocations, use list_lvmthin_pools instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/lvm"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_lvm(
        node: Annotated[str, Field(description="Target host node name.")],
        name: Annotated[str, Field(description="Name for the new Volume Group.")],
        device: Annotated[str, Field(description="Block device path (e.g., '/dev/sdb').")],
        add_to_storage: Annotated[bool, Field(description="If True, automatically register as Proxmox LVM storage pool.")] = True,
    ) -> str:
        """Create an LVM Volume Group on a physical block device.

        Use when initializing new raw disks as LVM storage.

        Args:
            node: The node name.
            name: VG name.
            device: Block device path (e.g. '/dev/sdb').
            add_to_storage: Auto-add as Proxmox storage.
        """
        return format_response(
            api_request(
                "post",
                f"/nodes/{node}/disks/lvm",
                name=name,
                device=device,
                add_storage=int(add_to_storage),
            )
        )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_lvm(
        node: Annotated[str, Field(description="Target host node name.")],
        name: Annotated[str, Field(description="Volume Group name to destroy.")],
        cleanup_disks: Annotated[bool, Field(description="If True, wipe partition tables on the underlying disk devices.")] = False,
    ) -> str:
        """Destroy an LVM Volume Group on a host node.

        WARNING: Destroys all logical volumes within the volume group.

        Args:
            node: The node name.
            name: Volume Group name.
            cleanup_disks: Wipe partition tables.
        """
        params: dict = {}
        if cleanup_disks:
            params["cleanup-disks"] = 1
        return format_response(api_request("delete", f"/nodes/{node}/disks/lvm/{name}", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_lvmthin_pools(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """List LVM Thin Pools configured on a host node.

        Use when checking thin-provisioned storage pools and overcommit ratios.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/lvmthin"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_lvmthin(
        node: Annotated[str, Field(description="Host node name.")],
        name: Annotated[str, Field(description="Name for the LVM thin pool.")],
        device: Annotated[str, Field(description="Block device path.")],
        add_to_storage: Annotated[bool, Field(description="Auto-add as Proxmox storage.")] = True,
    ) -> str:
        """Create an LVM Thin Pool on a block device.

        Use when initializing thin-provisioned local block storage.

        Args:
            node: The node name.
            name: Thin pool name.
            device: Block device path.
            add_to_storage: Auto-add as Proxmox storage.
        """
        return format_response(
            api_request(
                "post",
                f"/nodes/{node}/disks/lvmthin",
                name=name,
                device=device,
                add_storage=int(add_to_storage),
            )
        )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_lvmthin(
        node: Annotated[str, Field(description="Target host node name.")],
        name: Annotated[str, Field(description="LVM Thin Pool name to destroy.")],
        volume_group: Annotated[str, Field(description="Parent Volume Group name containing the thin pool.")],
    ) -> str:
        """Destroy an LVM Thin Pool on a host node.

        WARNING: Destroys all thin volumes allocated in the pool.

        Args:
            node: The node name.
            name: Thin pool name.
            volume_group: Parent Volume Group name.
        """
        return format_response(api_request("delete", f"/nodes/{node}/disks/lvmthin/{name}", volume_group=volume_group))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_zfs_pools(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """List ZFS pools (zpools) configured on a host node.

        Use when inspecting ZFS storage availability and pool states.
        To view detailed status for a specific zpool, use get_zfs_pool instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/zfs"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_zfs_pool(
        node: Annotated[str, Field(description="PVE host node name.")],
        name: Annotated[str, Field(description="ZFS pool name (e.g., 'rpool', 'tank').")],
    ) -> str:
        """Get detailed status, vdev hierarchy, and health metrics for a ZFS pool.

        Use when inspecting ZFS pool degradation, scrub state, or disk failure warnings.

        Args:
            node: The node name.
            name: ZFS pool name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/zfs/{name}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_zfs_pool(
        node: Annotated[str, Field(description="PVE host node name.")],
        name: Annotated[str, Field(description="ZFS pool name.")],
        raidlevel: Annotated[
            str,
            Field(description="ZFS RAID level: 'single', 'mirror', 'raid10', 'raidz', 'raidz2', 'raidz3', 'draid', 'draid2', 'draid3'."),
        ],
        devices: Annotated[str, Field(description="Space-separated block device paths (e.g., '/dev/sdb /dev/sdc').")],
        add_to_storage: Annotated[bool, Field(description="Auto-register as Proxmox ZFS storage pool.")] = True,
        ashift: Annotated[int, Field(description="ZFS ashift value (default 12 for 4k sector alignment).")] = 12,
        compression: Annotated[str, Field(description="ZFS dataset compression algorithm ('on', 'off', 'lz4', 'zstd').")] = "on",
    ) -> str:
        """Create a new ZFS pool on physical block devices.

        Use when initializing local ZFS storage arrays.

        Args:
            node: The node name.
            name: Pool name.
            raidlevel: RAID level: single, mirror, raid10, raidz, raidz2, raidz3, draid, draid2, draid3.
            devices: Space-separated device paths (e.g. '/dev/sdb /dev/sdc').
            add_to_storage: Auto-add as Proxmox storage.
            ashift: ashift value (default 12).
            compression: Compression (on, off, lz4, zstd, etc.).
        """
        return format_response(
            api_request(
                "post",
                f"/nodes/{node}/disks/zfs",
                name=name,
                raidlevel=raidlevel,
                devices=devices,
                add_storage=int(add_to_storage),
                ashift=ashift,
                compression=compression,
            )
        )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def destroy_zfs_pool(
        node: Annotated[str, Field(description="PVE host node name.")],
        name: Annotated[str, Field(description="ZFS pool name to destroy.")],
        cleanup_disks: Annotated[bool, Field(description="If True, wipe partition tables on constituent disks.")] = False,
    ) -> str:
        """Destroy a ZFS storage pool on a host node.

        WARNING: Destroys all datasets and volumes stored in the pool.

        Args:
            node: The node name.
            name: ZFS pool name.
            cleanup_disks: Wipe partition tables on pool drives.
        """
        params: dict = {}
        if cleanup_disks:
            params["cleanup-disks"] = 1
        return format_response(api_request("delete", f"/nodes/{node}/disks/zfs/{name}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def zfs_scrub(
        node: Annotated[str, Field(description="PVE host node name.")],
        name: Annotated[str, Field(description="ZFS pool name to scrub (e.g., 'rpool', 'tank').")],
        action: Annotated[str, Field(description="Scrub action: 'scrub' (start scrub) or 'cancel' (abort active scrub).")] = "scrub",
    ) -> str:
        """Initiate or cancel a ZFS pool data integrity scrub.

        Use when verifying data checksums and repair operations on ZFS pools.

        Args:
            node: The node name.
            name: ZFS pool name.
            action: Action to perform ('scrub' or 'cancel').
        """
        return format_response(api_request("post", f"/nodes/{node}/disks/zfs/{name}", action=action))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_directory_storage(
        node: Annotated[str, Field(description="PVE host node name.")],
    ) -> str:
        """List local directory-based storage mounts on a node.

        Use when inspecting mounted ext4/xfs storage directories.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/directory"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_directory_storage(
        node: Annotated[str, Field(description="Host node name.")],
        name: Annotated[str, Field(description="Storage mount name.")],
        device: Annotated[str, Field(description="Block device path (e.g., '/dev/sdb1').")],
        filesystem: Annotated[str, Field(description="Filesystem type: 'ext4' or 'xfs'.")] = "ext4",
        add_to_storage: Annotated[bool, Field(description="Auto-add as Proxmox storage pool.")] = True,
    ) -> str:
        """Format a device and create a directory storage mount point.

        Use when mounting dedicated local disk partitions as Proxmox directory storage.

        Args:
            node: The node name.
            name: Storage name.
            device: Block device path.
            filesystem: Filesystem type (ext4, xfs).
            add_to_storage: Auto-add as Proxmox storage.
        """
        return format_response(
            api_request(
                "post",
                f"/nodes/{node}/disks/directory",
                name=name,
                device=device,
                filesystem=filesystem,
                add_storage=int(add_to_storage),
            )
        )

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_directory_storage(
        node: Annotated[str, Field(description="Target host node name.")],
        name: Annotated[str, Field(description="Directory storage mount identifier to remove.")],
        cleanup_disks: Annotated[bool, Field(description="If True, wipe partition table on underlying device.")] = False,
    ) -> str:
        """Unmount and delete a directory storage configuration on a host node.

        Args:
            node: The node name.
            name: Storage mount identifier.
            cleanup_disks: Wipe device partition table.
        """
        params: dict = {}
        if cleanup_disks:
            params["cleanup-disks"] = 1
        return format_response(api_request("delete", f"/nodes/{node}/disks/directory/{name}", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def initialize_gpt(
        node: Annotated[str, Field(description="Target host node name.")],
        disk: Annotated[str, Field(description="Disk device path (e.g., '/dev/sdb').")],
    ) -> str:
        """Initialize a raw disk device with a clean GPT partition table.

        WARNING: Destroys all data on the specified block device.
        Use before configuring new LVM or ZFS storage on raw drives.

        Args:
            node: The node name.
            disk: Disk device path (e.g. '/dev/sdb').
        """
        return format_response(api_request("post", f"/nodes/{node}/disks/initgpt", disk=disk))
