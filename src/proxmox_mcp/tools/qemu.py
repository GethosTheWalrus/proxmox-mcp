"""QEMU virtual machine management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register QEMU VM management tools."""

    # ── Listing & Status ──────────────────────────────────────────────

    @mcp.tool()
    def list_vms(node: str) -> str:
        """List all QEMU virtual machines on a node with status, memory, CPU, and disk info.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu"))

    @mcp.tool()
    def get_vm_status(node: str, vmid: int) -> str:
        """Get the current runtime status of a VM (state, CPU, memory, disk, network, uptime).

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/status/current"))

    @mcp.tool()
    def get_vm_config(node: str, vmid: int, current: bool = True) -> str:
        """Get the configuration of a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            current: If True, return current (runtime) config. If False, return pending config.
        """
        params: dict = {"current": int(current)}
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/config", **params))

    @mcp.tool()
    def get_vm_pending(node: str, vmid: int) -> str:
        """Get pending configuration changes for a VM (not yet applied).

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/pending"))

    @mcp.tool()
    def get_vm_feature(node: str, vmid: int, feature: str) -> str:
        """Check if a specific feature is available/supported for a VM (e.g. snapshot, clone, copy).

        Args:
            node: The node name.
            vmid: The VM ID.
            feature: Feature to check ('snapshot', 'clone', 'copy').
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/feature", feature=feature))

    @mcp.tool()
    def get_vm_rrddata(node: str, vmid: int, timeframe: str = "hour") -> str:
        """Get RRD statistics data for a VM (CPU, memory, disk, network over time).

        Args:
            node: The node name.
            vmid: The VM ID.
            timeframe: Time range: 'hour', 'day', 'week', 'month', 'year'.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/rrddata", timeframe=timeframe))

    # ── Create / Delete ───────────────────────────────────────────────

    @mcp.tool()
    def create_vm(
        node: str,
        vmid: int,
        name: str = "",
        memory: int = 2048,
        cores: int = 1,
        sockets: int = 1,
        cpu: str = "host",
        ostype: str = "l26",
        scsihw: str = "virtio-scsi-single",
        scsi0: str = "",
        ide2: str = "",
        net0: str = "",
        boot: str = "",
        bios: str = "seabios",
        machine: str = "",
        cdrom: str = "",
        agent: str = "",
        start: bool = False,
        onboot: bool = False,
        description: str = "",
        pool: str = "",
        tags: str = "",
    ) -> str:
        """Create a new QEMU virtual machine.

        Args:
            node: The node name.
            vmid: The VM ID number.
            name: VM name.
            memory: Memory in MB (default 2048).
            cores: Number of CPU cores per socket (default 1).
            sockets: Number of CPU sockets (default 1).
            cpu: CPU type (default 'host').
            ostype: OS type: l26 (Linux 2.6+), win10, win11, wxp, other, etc.
            scsihw: SCSI controller: virtio-scsi-single, virtio-scsi-pci, lsi, megasas, pvscsi.
            scsi0: First SCSI disk (e.g. 'local-lvm:32' for 32GB on local-lvm).
            ide2: IDE device, often used for CD-ROM (e.g. 'local:iso/ubuntu.iso,media=cdrom').
            net0: Network device (e.g. 'virtio,bridge=vmbr0').
            boot: Boot order (e.g. 'order=scsi0;ide2;net0').
            bios: BIOS type: seabios, ovmf (UEFI).
            machine: Machine type (e.g. 'q35', 'i440fx').
            cdrom: CD-ROM ISO image path.
            agent: QEMU guest agent: '1' to enable, 'enabled=1,fstrim_cloned_disks=1'.
            start: Start the VM after creation.
            onboot: Start on host boot.
            description: VM description.
            pool: Resource pool to add the VM to.
            tags: Semicolon-separated tags.
        """
        params: dict = {
            "vmid": vmid,
            "memory": memory,
            "cores": cores,
            "sockets": sockets,
            "cpu": cpu,
            "ostype": ostype,
            "scsihw": scsihw,
        }
        for key, val in [
            ("name", name), ("scsi0", scsi0), ("ide2", ide2), ("net0", net0),
            ("boot", boot), ("bios", bios), ("machine", machine), ("cdrom", cdrom),
            ("agent", agent), ("description", description), ("pool", pool), ("tags", tags),
        ]:
            if val:
                params[key] = val
        if start:
            params["start"] = 1
        if onboot:
            params["onboot"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu", **params))

    @mcp.tool()
    def update_vm_config(
        node: str,
        vmid: int,
        name: str = "",
        memory: int = 0,
        cores: int = 0,
        sockets: int = 0,
        cpu: str = "",
        net0: str = "",
        description: str = "",
        onboot: bool | None = None,
        agent: str = "",
        boot: str = "",
        tags: str = "",
        hotplug: str = "",
        delete: str = "",
    ) -> str:
        """Update the configuration of an existing VM. Only provided parameters are changed.

        Args:
            node: The node name.
            vmid: The VM ID.
            name: VM name.
            memory: Memory in MB.
            cores: CPU cores per socket.
            sockets: CPU sockets.
            cpu: CPU type.
            net0: Network config.
            description: Description.
            onboot: Start on boot.
            agent: Guest agent config.
            boot: Boot order.
            tags: Semicolon-separated tags.
            hotplug: Hotplug features (disk, network, usb, memory, cpu).
            delete: Comma-separated list of settings to delete.
        """
        params: dict = {}
        for key, val in [
            ("name", name), ("cpu", cpu), ("net0", net0), ("description", description),
            ("agent", agent), ("boot", boot), ("tags", tags), ("hotplug", hotplug), ("delete", delete),
        ]:
            if val:
                params[key] = val
        if memory:
            params["memory"] = memory
        if cores:
            params["cores"] = cores
        if sockets:
            params["sockets"] = sockets
        if onboot is not None:
            params["onboot"] = int(onboot)
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/config", **params))

    @mcp.tool()
    def delete_vm(node: str, vmid: int, purge: bool = False, destroy_unreferenced_disks: bool = True) -> str:
        """Delete a VM. The VM must be stopped first.

        Args:
            node: The node name.
            vmid: The VM ID.
            purge: Remove from replication, HA, backup jobs and ACLs too.
            destroy_unreferenced_disks: Also destroy unreferenced disks owned by the VM.
        """
        params: dict = {"destroy-unreferenced-disks": int(destroy_unreferenced_disks)}
        if purge:
            params["purge"] = 1
        return format_response(api_request("delete", f"/nodes/{node}/qemu/{vmid}", **params))

    # ── Power Management ──────────────────────────────────────────────

    @mcp.tool()
    def start_vm(node: str, vmid: int, timeout: int = 0) -> str:
        """Start a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            timeout: Timeout in seconds (0 = default).
        """
        params: dict = {}
        if timeout:
            params["timeout"] = timeout
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/start", **params))

    @mcp.tool()
    def stop_vm(node: str, vmid: int, timeout: int = 0, skiplock: bool = False) -> str:
        """Hard-stop a VM (like pulling the power plug). Prefer shutdown_vm for graceful stop.

        Args:
            node: The node name.
            vmid: The VM ID.
            timeout: Wait timeout in seconds.
            skiplock: Ignore locks (requires root).
        """
        params: dict = {}
        if timeout:
            params["timeout"] = timeout
        if skiplock:
            params["skiplock"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/stop", **params))

    @mcp.tool()
    def shutdown_vm(node: str, vmid: int, timeout: int = 0, force_stop: bool = True) -> str:
        """Gracefully shut down a VM via ACPI. Falls back to hard stop after timeout if force_stop is true.

        Args:
            node: The node name.
            vmid: The VM ID.
            timeout: Timeout in seconds before force stop.
            force_stop: Force stop after timeout (default True).
        """
        params: dict = {"forceStop": int(force_stop)}
        if timeout:
            params["timeout"] = timeout
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/shutdown", **params))

    @mcp.tool()
    def reboot_vm(node: str, vmid: int, timeout: int = 0) -> str:
        """Reboot a VM via ACPI.

        Args:
            node: The node name.
            vmid: The VM ID.
            timeout: Wait timeout in seconds.
        """
        params: dict = {}
        if timeout:
            params["timeout"] = timeout
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/reboot", **params))

    @mcp.tool()
    def suspend_vm(node: str, vmid: int, todisk: bool = False) -> str:
        """Suspend a VM (pause execution or hibernate to disk).

        Args:
            node: The node name.
            vmid: The VM ID.
            todisk: If True, hibernate to disk. If False, pause in RAM.
        """
        params: dict = {}
        if todisk:
            params["todisk"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/suspend", **params))

    @mcp.tool()
    def resume_vm(node: str, vmid: int) -> str:
        """Resume a suspended/paused VM.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/resume"))

    @mcp.tool()
    def reset_vm(node: str, vmid: int) -> str:
        """Hard reset a VM (like pressing the reset button).

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/reset"))

    # ── Clone / Migrate / Template ────────────────────────────────────

    @mcp.tool()
    def clone_vm(
        node: str,
        vmid: int,
        newid: int,
        name: str = "",
        target: str = "",
        full: bool = True,
        storage: str = "",
        description: str = "",
        pool: str = "",
        snapname: str = "",
    ) -> str:
        """Clone a VM to create a new one. Can be a full copy or linked clone.

        Args:
            node: The source node name.
            vmid: The source VM ID.
            newid: The VMID for the new clone.
            name: Name for the clone.
            target: Target node for the clone (default: same node).
            full: Full clone (True) or linked clone (False).
            storage: Target storage for full clone.
            description: Description for the clone.
            pool: Resource pool.
            snapname: Snapshot name to clone from.
        """
        params: dict = {"newid": newid}
        if name:
            params["name"] = name
        if target:
            params["target"] = target
        if full:
            params["full"] = 1
        if storage:
            params["storage"] = storage
        if description:
            params["description"] = description
        if pool:
            params["pool"] = pool
        if snapname:
            params["snapname"] = snapname
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/clone", **params))

    @mcp.tool()
    def migrate_vm(
        node: str,
        vmid: int,
        target: str,
        online: bool = False,
        with_local_disks: bool = False,
        targetstorage: str = "",
    ) -> str:
        """Migrate a VM to another node in the cluster.

        Args:
            node: The source node.
            vmid: The VM ID.
            target: Target node name.
            online: Live migration (True) or offline (False).
            with_local_disks: Migrate local disks as well.
            targetstorage: Target storage mapping for migration (e.g. 'local-lvm').
        """
        params: dict = {"target": target}
        if online:
            params["online"] = 1
        if with_local_disks:
            params["with-local-disks"] = 1
        if targetstorage:
            params["targetstorage"] = targetstorage
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/migrate", **params))

    @mcp.tool()
    def convert_vm_to_template(node: str, vmid: int) -> str:
        """Convert a VM into a template (irreversible).

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/template"))

    @mcp.tool()
    def resize_vm_disk(node: str, vmid: int, disk: str, size: str) -> str:
        """Resize a VM disk. Can only grow, not shrink.

        Args:
            node: The node name.
            vmid: The VM ID.
            disk: Disk name (e.g. 'scsi0', 'virtio0', 'ide0').
            size: New size or size increment (e.g. '50G', '+10G').
        """
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/resize", disk=disk, size=size))

    @mcp.tool()
    def move_vm_disk(node: str, vmid: int, disk: str, storage: str = "", target_vmid: int = 0, target_disk: str = "", delete_original: bool = False) -> str:
        """Move a VM disk to different storage or attach to another VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            disk: Source disk name (e.g. 'scsi0').
            storage: Target storage ID (for moving to different storage).
            target_vmid: Target VM ID (for moving disk to another VM).
            target_disk: Target disk slot on the target VM.
            delete_original: Delete the original disk after moving.
        """
        params: dict = {"disk": disk}
        if storage:
            params["storage"] = storage
        if target_vmid:
            params["target-vmid"] = target_vmid
        if target_disk:
            params["target-disk"] = target_disk
        if delete_original:
            params["delete"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/move_disk", **params))

    # ── Snapshots ─────────────────────────────────────────────────────

    @mcp.tool()
    def list_vm_snapshots(node: str, vmid: int) -> str:
        """List all snapshots of a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/snapshot"))

    @mcp.tool()
    def create_vm_snapshot(node: str, vmid: int, snapname: str, description: str = "", vmstate: bool = False) -> str:
        """Create a snapshot of a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            snapname: Snapshot name.
            description: Snapshot description.
            vmstate: Include RAM state (for running VMs).
        """
        params: dict = {"snapname": snapname}
        if description:
            params["description"] = description
        if vmstate:
            params["vmstate"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/snapshot", **params))

    @mcp.tool()
    def delete_vm_snapshot(node: str, vmid: int, snapname: str, force: bool = False) -> str:
        """Delete a VM snapshot.

        Args:
            node: The node name.
            vmid: The VM ID.
            snapname: Snapshot name to delete.
            force: Force delete even if snapshot is in use.
        """
        params: dict = {}
        if force:
            params["force"] = 1
        return format_response(api_request("delete", f"/nodes/{node}/qemu/{vmid}/snapshot/{snapname}", **params))

    @mcp.tool()
    def rollback_vm_snapshot(node: str, vmid: int, snapname: str) -> str:
        """Rollback a VM to a previous snapshot (current state will be lost).

        Args:
            node: The node name.
            vmid: The VM ID.
            snapname: The snapshot name to rollback to.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/snapshot/{snapname}/rollback"))

    @mcp.tool()
    def get_vm_snapshot_config(node: str, vmid: int, snapname: str) -> str:
        """Get the configuration stored in a VM snapshot.

        Args:
            node: The node name.
            vmid: The VM ID.
            snapname: The snapshot name.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/snapshot/{snapname}/config"))

    # ── Cloud-Init ────────────────────────────────────────────────────

    @mcp.tool()
    def get_vm_cloudinit(node: str, vmid: int) -> str:
        """Get Cloud-Init configuration for a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/cloudinit"))

    @mcp.tool()
    def update_vm_cloudinit(
        node: str,
        vmid: int,
        ciuser: str = "",
        cipassword: str = "",
        sshkeys: str = "",
        ipconfig0: str = "",
        nameserver: str = "",
        searchdomain: str = "",
    ) -> str:
        """Set Cloud-Init parameters for a VM (user, password, SSH keys, network).

        Args:
            node: The node name.
            vmid: The VM ID.
            ciuser: Cloud-Init user name.
            cipassword: Cloud-Init password.
            sshkeys: SSH public keys (URL-encoded, newline delimited).
            ipconfig0: IP config for first interface (e.g. 'ip=dhcp' or 'ip=10.0.0.5/24,gw=10.0.0.1').
            nameserver: DNS nameserver IP.
            searchdomain: DNS search domain.
        """
        params: dict = {}
        for key, val in [
            ("ciuser", ciuser), ("cipassword", cipassword), ("sshkeys", sshkeys),
            ("ipconfig0", ipconfig0), ("nameserver", nameserver), ("searchdomain", searchdomain),
        ]:
            if val:
                params[key] = val
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/cloudinit", **params))

    @mcp.tool()
    def dump_vm_cloudinit(node: str, vmid: int, type: str = "user") -> str:
        """Dump the Cloud-Init generated config file (user-data, network-data, or meta-data).

        Args:
            node: The node name.
            vmid: The VM ID.
            type: Config type: 'user', 'network', or 'meta'.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/cloudinit/dump", type=type))

    # ── QEMU Guest Agent ──────────────────────────────────────────────

    @mcp.tool()
    def vm_agent_exec(node: str, vmid: int, command: str, input_data: str = "") -> str:
        """Execute a command inside a VM via the QEMU Guest Agent.

        Args:
            node: The node name.
            vmid: The VM ID.
            command: The command to execute.
            input_data: Data to pass to stdin.
        """
        params: dict = {"command": command}
        if input_data:
            params["input-data"] = input_data
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/agent/exec", **params))

    @mcp.tool()
    def vm_agent_exec_status(node: str, vmid: int, pid: int) -> str:
        """Get the status/result of a command previously executed via the guest agent.

        Args:
            node: The node name.
            vmid: The VM ID.
            pid: The PID returned by the exec call.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/agent/exec-status", pid=pid))

    @mcp.tool()
    def vm_agent_file_read(node: str, vmid: int, file: str) -> str:
        """Read a file from inside a VM via the guest agent.

        Args:
            node: The node name.
            vmid: The VM ID.
            file: Absolute file path inside the guest.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/agent/file-read", file=file))

    @mcp.tool()
    def vm_agent_file_write(node: str, vmid: int, file: str, content: str) -> str:
        """Write content to a file inside a VM via the guest agent.

        Args:
            node: The node name.
            vmid: The VM ID.
            file: Absolute file path inside the guest.
            content: File content to write.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/agent/file-write", file=file, content=content))

    @mcp.tool()
    def vm_agent_get_info(node: str, vmid: int, info_type: str = "get-osinfo") -> str:
        """Get various system information from a VM via the guest agent.

        Args:
            node: The node name.
            vmid: The VM ID.
            info_type: Info to retrieve: 'get-osinfo', 'get-host-name', 'get-time',
                       'get-timezone', 'get-users', 'get-vcpus', 'get-fsinfo',
                       'get-memory-blocks', 'get-memory-block-info', 'info',
                       'network-get-interfaces'.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/agent/{info_type}"))

    @mcp.tool()
    def vm_agent_set_password(node: str, vmid: int, username: str, password: str, crypted: bool = False) -> str:
        """Set a user password inside a VM via the guest agent.

        Args:
            node: The node name.
            vmid: The VM ID.
            username: The username.
            password: The new password.
            crypted: If True, password is already encrypted.
        """
        params: dict = {"username": username, "password": password}
        if crypted:
            params["crypted"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/agent/set-user-password", **params))

    # ── Console Access ────────────────────────────────────────────────

    @mcp.tool()
    def get_vm_vncproxy(node: str, vmid: int, websocket: bool = True) -> str:
        """Create a VNC proxy connection ticket for a VM (for console access).

        Args:
            node: The node name.
            vmid: The VM ID.
            websocket: Use WebSocket connection.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/vncproxy", websocket=int(websocket)))

    @mcp.tool()
    def get_vm_spiceproxy(node: str, vmid: int) -> str:
        """Create a SPICE proxy connection for a VM console.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/spiceproxy"))

    @mcp.tool()
    def send_vm_key(node: str, vmid: int, key: str) -> str:
        """Send a key event to a VM (e.g. ctrl-alt-del).

        Args:
            node: The node name.
            vmid: The VM ID.
            key: Key combination (e.g. 'ctrl-alt-delete').
        """
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/sendkey", key=key))

    @mcp.tool()
    def send_vm_monitor_command(node: str, vmid: int, command: str) -> str:
        """Send a QEMU monitor command to a VM (advanced/low-level).

        Args:
            node: The node name.
            vmid: The VM ID.
            command: The QEMU monitor command.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/monitor", command=command))
