"""Storage management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register storage management tools."""

    # ── Datacenter-Level Storage Configuration ────────────────────────

    @mcp.tool()
    def list_storage(type: str = "", enabled: bool = True) -> str:
        """List all configured storage pools at the datacenter level.

        Args:
            type: Filter by type (dir, lvm, lvmthin, zfspool, nfs, cifs, iscsi, rbd, cephfs, pbs, glusterfs, btrfs).
            enabled: Only show enabled storage (default True).
        """
        params: dict = {}
        if type:
            params["type"] = type
        return format_response(api_request("get", "/storage", **params))

    @mcp.tool()
    def get_storage_config(storage: str) -> str:
        """Get configuration of a specific storage pool.

        Args:
            storage: The storage ID.
        """
        return format_response(api_request("get", f"/storage/{storage}"))

    @mcp.tool()
    def create_storage(
        storage: str,
        type: str,
        path: str = "",
        server: str = "",
        export: str = "",
        vgname: str = "",
        thinpool: str = "",
        pool: str = "",
        portal: str = "",
        target: str = "",
        datastore: str = "",
        content: str = "",
        nodes: str = "",
        shared: bool = False,
        disable: bool = False,
        maxfiles: int = 0,
        prune_backups: str = "",
    ) -> str:
        """Create a new storage pool configuration.

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
            ("path", path), ("server", server), ("export", export),
            ("vgname", vgname), ("thinpool", thinpool), ("pool", pool),
            ("portal", portal), ("target", target), ("datastore", datastore),
            ("content", content), ("nodes", nodes), ("prune-backups", prune_backups),
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

    @mcp.tool()
    def update_storage(
        storage: str,
        content: str = "",
        nodes: str = "",
        shared: bool | None = None,
        disable: bool | None = None,
        prune_backups: str = "",
        delete: str = "",
    ) -> str:
        """Update an existing storage pool configuration.

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

    @mcp.tool()
    def delete_storage(storage: str) -> str:
        """Delete a storage pool configuration (does not delete data on the backend).

        Args:
            storage: The storage ID.
        """
        return format_response(api_request("delete", f"/storage/{storage}"))

    # ── Node-Level Storage ────────────────────────────────────────────

    @mcp.tool()
    def list_node_storage(node: str, content: str = "", enabled: bool = True) -> str:
        """List storage pools available on a specific node with usage info.

        Args:
            node: The node name.
            content: Filter by content type (images, rootdir, vztmpl, iso, backup).
            enabled: Only show enabled storage.
        """
        params: dict = {}
        if content:
            params["content"] = content
        return format_response(api_request("get", f"/nodes/{node}/storage", **params))

    @mcp.tool()
    def get_node_storage_status(node: str, storage: str) -> str:
        """Get usage status of a storage pool on a node (total, used, available).

        Args:
            node: The node name.
            storage: The storage ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/status"))

    @mcp.tool()
    def list_storage_content(node: str, storage: str, content: str = "", vmid: int = 0) -> str:
        """List content of a storage pool (disk images, ISOs, templates, backups).

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

    @mcp.tool()
    def get_storage_volume_info(node: str, storage: str, volume: str) -> str:
        """Get details about a specific volume in storage.

        Args:
            node: The node name.
            storage: The storage ID.
            volume: The volume ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/content/{volume}"))

    @mcp.tool()
    def allocate_storage_volume(node: str, storage: str, vmid: int, filename: str, size: str, format: str = "") -> str:
        """Allocate a new disk volume in storage.

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

    @mcp.tool()
    def delete_storage_volume(node: str, storage: str, volume: str) -> str:
        """Delete a volume from storage.

        Args:
            node: The node name.
            storage: The storage ID.
            volume: The volume ID.
        """
        return format_response(api_request("delete", f"/nodes/{node}/storage/{storage}/content/{volume}"))

    @mcp.tool()
    def upload_to_storage(node: str, storage: str, content: str, filename: str, tmpfilename: str = "") -> str:
        """Upload a file (ISO, template, etc.) to storage. Note: actual file upload must go through the HTTP API directly.

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

    @mcp.tool()
    def download_url_to_storage(node: str, storage: str, url: str, content: str, filename: str, checksum: str = "", checksum_algorithm: str = "") -> str:
        """Download a file from a URL directly to storage (ISO, template, etc.).

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

    @mcp.tool()
    def get_storage_rrddata(node: str, storage: str, timeframe: str = "hour") -> str:
        """Get RRD statistics for a storage pool (usage over time).

        Args:
            node: The node name.
            storage: The storage ID.
            timeframe: Time range: 'hour', 'day', 'week', 'month', 'year'.
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/rrddata", timeframe=timeframe))

    @mcp.tool()
    def prune_storage_backups(node: str, storage: str, type: str = "", vmid: int = 0, prune_backups: str = "", dry_run: bool = True) -> str:
        """Prune (delete) old backups from storage according to retention policy.

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

    @mcp.tool()
    def list_file_restore(node: str, storage: str, volume: str, filepath: str = "/") -> str:
        """List files in a backup volume for file-level restore (PBS backups).

        Args:
            node: The node name.
            storage: The storage ID.
            volume: The backup volume ID.
            filepath: Path inside the backup to list (default '/').
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/file-restore/list", volume=volume, filepath=filepath))

    # ── Disk Management ───────────────────────────────────────────────

    @mcp.tool()
    def list_lvm_volumes(node: str) -> str:
        """List LVM volume groups on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/lvm"))

    @mcp.tool()
    def create_lvm(node: str, name: str, device: str, add_to_storage: bool = True) -> str:
        """Create a new LVM volume group on a device.

        Args:
            node: The node name.
            name: VG name.
            device: Block device path (e.g. '/dev/sdb').
            add_to_storage: Auto-add as Proxmox storage.
        """
        return format_response(api_request("post", f"/nodes/{node}/disks/lvm", name=name, device=device, add_storage=int(add_to_storage)))

    @mcp.tool()
    def list_lvmthin_pools(node: str) -> str:
        """List LVM thin pools on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/lvmthin"))

    @mcp.tool()
    def create_lvmthin(node: str, name: str, device: str, add_to_storage: bool = True) -> str:
        """Create a new LVM thin pool.

        Args:
            node: The node name.
            name: Thin pool name.
            device: Block device path.
            add_to_storage: Auto-add as Proxmox storage.
        """
        return format_response(api_request("post", f"/nodes/{node}/disks/lvmthin", name=name, device=device, add_storage=int(add_to_storage)))

    @mcp.tool()
    def list_zfs_pools(node: str) -> str:
        """List ZFS pools on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/zfs"))

    @mcp.tool()
    def get_zfs_pool(node: str, name: str) -> str:
        """Get details of a ZFS pool.

        Args:
            node: The node name.
            name: ZFS pool name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/zfs/{name}"))

    @mcp.tool()
    def create_zfs_pool(node: str, name: str, raidlevel: str, devices: str, add_to_storage: bool = True, ashift: int = 12, compression: str = "on") -> str:
        """Create a new ZFS pool.

        Args:
            node: The node name.
            name: Pool name.
            raidlevel: RAID level: single, mirror, raid10, raidz, raidz2, raidz3, draid, draid2, draid3.
            devices: Space-separated device paths (e.g. '/dev/sdb /dev/sdc').
            add_to_storage: Auto-add as Proxmox storage.
            ashift: ashift value (default 12).
            compression: Compression (on, off, lz4, zstd, etc.).
        """
        return format_response(api_request(
            "post", f"/nodes/{node}/disks/zfs",
            name=name, raidlevel=raidlevel, devices=devices,
            add_storage=int(add_to_storage), ashift=ashift, compression=compression,
        ))

    @mcp.tool()
    def list_directory_storage(node: str) -> str:
        """List directory-based storage mounts on a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/disks/directory"))

    @mcp.tool()
    def create_directory_storage(node: str, name: str, device: str, filesystem: str = "ext4", add_to_storage: bool = True) -> str:
        """Create a directory-based storage mount from a device.

        Args:
            node: The node name.
            name: Storage name.
            device: Block device path.
            filesystem: Filesystem type (ext4, xfs).
            add_to_storage: Auto-add as Proxmox storage.
        """
        return format_response(api_request(
            "post", f"/nodes/{node}/disks/directory",
            name=name, device=device, filesystem=filesystem, add_storage=int(add_to_storage),
        ))

    @mcp.tool()
    def initialize_gpt(node: str, disk: str) -> str:
        """Initialize a disk with GPT partition table (WARNING: destroys all data).

        Args:
            node: The node name.
            disk: Disk device path (e.g. '/dev/sdb').
        """
        return format_response(api_request("post", f"/nodes/{node}/disks/initgpt", disk=disk))
