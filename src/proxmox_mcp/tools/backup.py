"""Backup and vzdump tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register backup management tools."""

    @mcp.tool()
    def list_backup_jobs() -> str:
        """List all scheduled backup jobs (vzdump) in the cluster."""
        return format_response(api_request("get", "/cluster/backup"))

    @mcp.tool()
    def get_backup_job(id: str) -> str:
        """Get details of a specific backup job.

        Args:
            id: Backup job ID.
        """
        return format_response(api_request("get", f"/cluster/backup/{id}"))

    @mcp.tool()
    def get_backup_job_included_volumes(id: str) -> str:
        """Get volumes included in a backup job.

        Args:
            id: Backup job ID.
        """
        return format_response(api_request("get", f"/cluster/backup/{id}/included_volumes"))

    @mcp.tool()
    def create_backup_job(
        storage: str,
        schedule: str = "daily",
        all_guests: bool = True,
        vmid: str = "",
        node: str = "",
        mode: str = "snapshot",
        compress: str = "zstd",
        mailnotification: str = "",
        mailto: str = "",
        maxfiles: int = 0,
        prune_backups: str = "",
        notes_template: str = "",
        enabled: bool = True,
        comment: str = "",
    ) -> str:
        """Create a scheduled backup job.

        Args:
            storage: Target storage ID for backups.
            schedule: Schedule in systemd calendar format (e.g. 'daily', 'weekly', '02:00').
            all_guests: Backup all guests.
            vmid: Comma-separated VMIDs to back up (if not all_guests).
            node: Only back up guests on this node.
            mode: Backup mode: 'snapshot', 'suspend', 'stop'.
            compress: Compression: 'none', 'lzo', 'gzip', 'zstd'.
            mailnotification: 'always' or 'failure'.
            mailto: Comma-separated email addresses.
            maxfiles: Max backup files to keep (0 = unlimited, deprecated - use prune_backups).
            prune_backups: Retention schedule (e.g. 'keep-daily=7,keep-weekly=4').
            notes_template: Template for backup notes.
            enabled: Enable the job.
            comment: Description.
        """
        params: dict = {"storage": storage, "schedule": schedule, "mode": mode, "compress": compress}
        if all_guests:
            params["all"] = 1
        if vmid:
            params["vmid"] = vmid
        if node:
            params["node"] = node
        if mailnotification:
            params["mailnotification"] = mailnotification
        if mailto:
            params["mailto"] = mailto
        if maxfiles:
            params["maxfiles"] = maxfiles
        if prune_backups:
            params["prune-backups"] = prune_backups
        if notes_template:
            params["notes-template"] = notes_template
        if not enabled:
            params["enabled"] = 0
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/backup", **params))

    @mcp.tool()
    def update_backup_job(
        id: str,
        storage: str = "",
        schedule: str = "",
        all_guests: bool = False,
        vmid: str = "",
        node: str = "",
        mode: str = "",
        compress: str = "",
        enabled: bool = True,
        delete: str = "",
    ) -> str:
        """Update a scheduled backup job.

        Args:
            id: Backup job ID.
            storage: Target storage ID.
            schedule: Schedule in systemd calendar format.
            all_guests: Backup all guests.
            vmid: Comma-separated VMIDs.
            node: Node filter.
            mode: Backup mode.
            compress: Compression.
            enabled: Enable/disable.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if storage:
            params["storage"] = storage
        if schedule:
            params["schedule"] = schedule
        if all_guests:
            params["all"] = 1
        if vmid:
            params["vmid"] = vmid
        if node:
            params["node"] = node
        if mode:
            params["mode"] = mode
        if compress:
            params["compress"] = compress
        if not enabled:
            params["enabled"] = 0
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/cluster/backup/{id}", **params))

    @mcp.tool()
    def delete_backup_job(id: str) -> str:
        """Delete a scheduled backup job.

        Args:
            id: Backup job ID.
        """
        return format_response(api_request("delete", f"/cluster/backup/{id}"))

    @mcp.tool()
    def create_vzdump(
        node: str,
        vmid: str = "",
        all_guests: bool = False,
        storage: str = "",
        mode: str = "snapshot",
        compress: str = "zstd",
        stdout: bool = False,
    ) -> str:
        """Start an immediate backup (vzdump) on a node.

        Args:
            node: The node to run the backup on.
            vmid: Comma-separated VMIDs (required if not all_guests).
            all_guests: Back up all guests on the node.
            storage: Target storage (empty = default).
            mode: Backup mode: 'snapshot', 'suspend', 'stop'.
            compress: Compression: 'none', 'lzo', 'gzip', 'zstd'.
            stdout: Write to stdout instead of storage.
        """
        params: dict = {"mode": mode, "compress": compress}
        if vmid:
            params["vmid"] = vmid
        if all_guests:
            params["all"] = 1
        if storage:
            params["storage"] = storage
        if stdout:
            params["stdout"] = 1
        return format_response(api_request("post", f"/nodes/{node}/vzdump", **params))

    @mcp.tool()
    def get_vzdump_defaults(node: str) -> str:
        """Get the default vzdump configuration for a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/vzdump/defaults"))

    @mcp.tool()
    def get_vzdump_extractconfig(node: str, volume: str) -> str:
        """Extract the guest configuration from a vzdump backup archive.

        Args:
            node: The node name.
            volume: Backup volume ID (e.g. 'local:backup/vzdump-qemu-100-2024_01_01-00_00_00.vma.zst').
        """
        return format_response(api_request("get", f"/nodes/{node}/vzdump/extractconfig", volume=volume))

    # ── Backup file restore ───────────────────────────────────────────

    @mcp.tool()
    def list_backup_file_restore(node: str, storage: str, volume: str, filepath: str = "/") -> str:
        """List files in a vzdump backup for single-file restore.

        Args:
            node: The node name.
            storage: Storage ID.
            volume: Backup volume ID.
            filepath: Path within the backup (default '/').
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/file-restore/list",
                                           volume=volume, filepath=filepath))

    @mcp.tool()
    def download_file_restore(node: str, storage: str, volume: str, filepath: str) -> str:
        """Download a file from a vzdump backup.

        Args:
            node: The node name.
            storage: Storage ID.
            volume: Backup volume ID.
            filepath: Path of the file to download from the backup.
        """
        return format_response(api_request("get", f"/nodes/{node}/storage/{storage}/file-restore/download",
                                           volume=volume, filepath=filepath))
