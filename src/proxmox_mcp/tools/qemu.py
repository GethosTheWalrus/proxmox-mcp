"""QEMU virtual machine management tools for Proxmox MCP server."""

from __future__ import annotations

from typing import Annotated

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from pydantic import Field

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register QEMU VM management tools."""

    # ── Listing & Status ──────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_vms(
        node: Annotated[str, Field(description="PVE host node name (e.g., 'pve1').")],
    ) -> str:
        """List all QEMU virtual machines on a node with status, memory, CPU, and disk metrics.

        Use when inspecting active or stopped VMs on a host.
        To view detailed configuration for a specific VM, use get_vm_config instead.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_status(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID (e.g., 100).")],
    ) -> str:
        """Get current runtime status (state, CPU utilization, RAM usage, disk I/O, network stats, uptime) of a VM.

        Use when checking live operational metrics of a VM.
        To list all VMs on a node, use list_vms instead.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/status/current"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_config(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        current: Annotated[bool, Field(description="If True, return runtime active config. If False, return pending config.")] = True,
    ) -> str:
        """Get hardware resources, network devices, disk attachments, and settings of a VM.

        Use when reviewing VM hardware, ISO images, or network settings.

        Args:
            node: The node name.
            vmid: The VM ID.
            current: If True, return current (runtime) config. If False, return pending config.
        """
        params: dict = {"current": int(current)}
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/config", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_pending(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
    ) -> str:
        """Get pending configuration changes for a VM (not yet applied).

        Use when checking staged hardware or resource modifications requiring VM reboot.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/pending"))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_feature(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        feature: Annotated[str, Field(description="Feature to query ('snapshot', 'clone', 'copy').")],
    ) -> str:
        """Check feature availability (snapshots, cloning) for a QEMU VM.

        Use when testing if storage backends support snapshotting or cloning operations for a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            feature: Feature to check ('snapshot', 'clone', 'copy').
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/feature", feature=feature))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_rrddata(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        timeframe: Annotated[str, Field(description="Time range: 'hour', 'day', 'week', 'month', or 'year'.")] = "hour",
    ) -> str:
        """Get RRD metrics history (CPU, memory, disk throughput, network I/O) for a VM.

        Use when inspecting historical performance trends of a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            timeframe: Time range: 'hour', 'day', 'week', 'month', 'year'.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/rrddata", timeframe=timeframe))

    # ── Create / Delete ───────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_vm(
        node: Annotated[str, Field(description="Target PVE host node name.")],
        vmid: Annotated[int, Field(description="Unique VM ID (e.g., 100).")],
        name: Annotated[str, Field(description="VM name.")] = "",
        memory: Annotated[int, Field(description="RAM allocation in MB (default 2048).")] = 2048,
        cores: Annotated[int, Field(description="CPU core count per socket (default 1).")] = 1,
        sockets: Annotated[int, Field(description="CPU socket count (default 1).")] = 1,
        cpu: Annotated[str, Field(description="CPU architecture/emulation type (default 'host').")] = "host",
        ostype: Annotated[str, Field(description="OS type ('l26' for Linux 2.6+, 'win10', 'win11', 'other').")] = "l26",
        scsihw: Annotated[str, Field(description="SCSI controller hardware ('virtio-scsi-single', 'virtio-scsi-pci', 'lsi').")] = "virtio-scsi-single",
        scsi0: Annotated[str, Field(description="First SCSI disk allocation spec (e.g., 'local-lvm:32' for 32GB).")] = "",
        ide2: Annotated[str, Field(description="IDE device spec, often CD-ROM (e.g., 'local:iso/ubuntu.iso,media=cdrom').")] = "",
        net0: Annotated[str, Field(description="Network device spec (e.g., 'virtio,bridge=vmbr0').")] = "",
        boot: Annotated[str, Field(description="Boot order specification (e.g., 'order=scsi0;ide2').")] = "",
        bios: Annotated[str, Field(description="BIOS type ('seabios' or 'ovmf' for UEFI).")] = "seabios",
        machine: Annotated[str, Field(description="QEMU machine model (e.g., 'q35', 'i440fx').")] = "",
        cdrom: Annotated[str, Field(description="CD-ROM ISO file path.")] = "",
        agent: Annotated[str, Field(description="QEMU guest agent enable string (e.g., 'enabled=1').")] = "",
        start: Annotated[bool, Field(description="If True, boot VM immediately after creation.")] = False,
        onboot: Annotated[bool, Field(description="If True, start VM on host system boot.")] = False,
        description: Annotated[str, Field(description="VM description or notes.")] = "",
        pool: Annotated[str, Field(description="Resource pool to assign VM to.")] = "",
        tags: Annotated[str, Field(description="Semicolon-separated tag strings.")] = "",
    ) -> str:
        """Create a new QEMU virtual machine instance.

        Use when deploying new virtual machine workloads.
        To delete a VM, use delete_vm instead.

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
            boot: Boot order (e.g. 'order=scsi0').
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
            ("name", name),
            ("scsi0", scsi0),
            ("ide2", ide2),
            ("net0", net0),
            ("boot", boot),
            ("bios", bios),
            ("machine", machine),
            ("cdrom", cdrom),
            ("agent", agent),
            ("description", description),
            ("pool", pool),
            ("tags", tags),
        ]:
            if val:
                params[key] = val
        if start:
            params["start"] = 1
        if onboot:
            params["onboot"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_vm_config(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        name: Annotated[str, Field(description="Updated VM name.")] = "",
        memory: Annotated[int, Field(description="RAM allocation in MB.")] = 0,
        cores: Annotated[int, Field(description="CPU core count per socket.")] = 0,
        sockets: Annotated[int, Field(description="CPU socket count.")] = 0,
        cpu: Annotated[str, Field(description="CPU type.")] = "",
        net0: Annotated[str, Field(description="Network device spec.")] = "",
        description: Annotated[str, Field(description="Updated description.")] = "",
        onboot: Annotated[bool | None, Field(description="Set start on host boot.")] = None,
        agent: Annotated[str, Field(description="Guest agent config.")] = "",
        boot: Annotated[str, Field(description="Boot order spec.")] = "",
        tags: Annotated[str, Field(description="Semicolon-separated tags.")] = "",
        hotplug: Annotated[str, Field(description="Hotplug features ('disk,network,usb,memory,cpu').")] = "",
        delete: Annotated[str, Field(description="Comma-separated settings to delete.")] = "",
        extra_config: Annotated[str, Field(description="JSON string or comma-separated key=value pairs for any additional Proxmox QEMU parameters, such as virtual disks (e.g. '{\"scsi0\": \"local-zfs:vm-100-disk-0,mbps_wr=250,discard=on\"}'), secondary network devices, or custom hardware flags.")] = "",
    ) -> str:
        """Update hardware resources, network interfaces, or boot order for an existing VM.

        Use when adjusting VM memory, CPU allocation, network settings, disk throttles, or tags.

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
            extra_config: JSON string or key=value pairs for extra QEMU options (e.g. disk configs/throttles, net1).
        """
        params: dict = {}
        for key, val in [
            ("name", name),
            ("cpu", cpu),
            ("net0", net0),
            ("description", description),
            ("agent", agent),
            ("boot", boot),
            ("tags", tags),
            ("hotplug", hotplug),
            ("delete", delete),
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
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/config", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_vm(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID to destroy.")],
        purge: Annotated[bool, Field(description="If True, remove from HA, backup jobs, and ACLs.")] = False,
        destroy_unreferenced_disks: Annotated[bool, Field(description="If True, destroy unreferenced disks.")] = True,
    ) -> str:
        """Permanently delete a QEMU virtual machine and destroy associated virtual disk images.

        Use when decommissioning a virtual machine. VM must be stopped prior to deletion.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def start_vm(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        timeout: Annotated[int, Field(description="Timeout in seconds (0 = default).")] = 0,
    ) -> str:
        """Power on a stopped QEMU virtual machine.

        Use when booting a VM.
        To gracefully stop a VM, use shutdown_vm instead.

        Args:
            node: The node name.
            vmid: The VM ID.
            timeout: Timeout in seconds (0 = default).
        """
        params: dict = {}
        if timeout:
            params["timeout"] = timeout
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/start", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False))
    def stop_vm(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        timeout: Annotated[int, Field(description="Wait timeout in seconds.")] = 0,
        skiplock: Annotated[bool, Field(description="If True, ignore locks (requires root).")] = False,
        overrule_shutdown: Annotated[bool, Field(description="If True, overrule/cancel any pending or active shutdown task.")] = False,
    ) -> str:
        """Forcefully stop a QEMU VM immediately (hard power kill).

        Use when a VM is unresponsive to shutdown signals. Prefer shutdown_vm for clean OS shutdown.

        Args:
            node: The node name.
            vmid: The VM ID.
            timeout: Wait timeout in seconds.
            skiplock: Ignore locks (requires root).
            overrule_shutdown: Cancel active shutdown task and force hard stop.
        """
        params: dict = {}
        if timeout:
            params["timeout"] = timeout
        if skiplock:
            params["skiplock"] = 1
        if overrule_shutdown:
            params["overrule-shutdown"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/stop", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def shutdown_vm(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        timeout: Annotated[int, Field(description="Timeout in seconds before force stop.")] = 0,
        force_stop: Annotated[bool, Field(description="If True, force stop after timeout expires.")] = True,
    ) -> str:
        """Gracefully shut down a QEMU VM via ACPI signal or QEMU Guest Agent.

        Use for clean VM OS shutdowns.
        To force immediate power-off, use stop_vm instead.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def reboot_vm(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        timeout: Annotated[int, Field(description="Wait timeout in seconds.")] = 0,
    ) -> str:
        """Reboot a QEMU VM gracefully via ACPI.

        Use when restarting a VM OS.

        Args:
            node: The node name.
            vmid: The VM ID.
            timeout: Wait timeout in seconds.
        """
        params: dict = {}
        if timeout:
            params["timeout"] = timeout
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/reboot", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def suspend_vm(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        todisk: Annotated[bool, Field(description="If True, hibernate RAM to disk; if False, pause execution in RAM.")] = False,
    ) -> str:
        """Pause VM execution in RAM or save state to disk (hibernate).

        Use when pausing VM workloads.
        To resume execution, use resume_vm.

        Args:
            node: The node name.
            vmid: The VM ID.
            todisk: If True, hibernate to disk. If False, pause in RAM.
        """
        params: dict = {}
        if todisk:
            params["todisk"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/suspend", **params))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def resume_vm(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
    ) -> str:
        """Resume execution of a suspended or paused QEMU VM.

        Use when restoring execution of a paused VM.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/resume"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False))
    def reset_vm(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
    ) -> str:
        """Hard reset a QEMU VM (equivalent to physical hardware reset button).

        Use when a VM guest kernel is hard locked.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/status/reset"))

    # ── Clone / Migrate / Template ────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def clone_vm(
        node: Annotated[str, Field(description="Source PVE host node name.")],
        vmid: Annotated[int, Field(description="Source QEMU VM ID.")],
        newid: Annotated[int, Field(description="Target VM ID for the clone.")],
        name: Annotated[str, Field(description="Name for the cloned VM.")] = "",
        target: Annotated[str, Field(description="Target node for clone (defaults to same node).")] = "",
        full: Annotated[bool, Field(description="If True, full standalone copy; if False, linked clone.")] = True,
        storage: Annotated[str, Field(description="Target storage pool for full clone.")] = "",
        description: Annotated[str, Field(description="Description for clone.")] = "",
        pool: Annotated[str, Field(description="Resource pool.")] = "",
        snapname: Annotated[str, Field(description="Snapshot name to clone from.")] = "",
    ) -> str:
        """Clone a QEMU virtual machine to create a new VM instance.

        Use when duplicating VM configurations or instantiating from golden templates.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def migrate_vm(
        node: Annotated[str, Field(description="Source PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID to migrate.")],
        target: Annotated[str, Field(description="Target PVE host node name.")],
        online: Annotated[bool, Field(description="If True, perform live VM migration without downtime.")] = False,
        with_local_disks: Annotated[bool, Field(description="If True, migrate local non-shared disk storage.")] = False,
        targetstorage: Annotated[str, Field(description="Target storage ID mapping.")] = "",
    ) -> str:
        """Migrate a QEMU VM to another host node in the cluster.

        Use when rebalancing cluster compute load or clearing a host node for maintenance.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def convert_vm_to_template(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID to convert.")],
    ) -> str:
        """Convert a QEMU VM into a read-only golden template (irreversible).

        Use when creating custom base VM templates for linked/full cloning.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/template"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def resize_vm_disk(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        disk: Annotated[str, Field(description="Disk drive identifier (e.g., 'scsi0', 'virtio0').")],
        size: Annotated[str, Field(description="New size or increment (e.g., '50G', '+10G').")],
    ) -> str:
        """Expand disk capacity for a QEMU VM disk drive.

        Use when increasing VM storage capacity. Note that shrinking disks is not supported by QEMU.

        Args:
            node: The node name.
            vmid: The VM ID.
            disk: Disk name (e.g. 'scsi0', 'virtio0', 'ide0').
            size: New size or size increment (e.g. '50G', '+10G').
        """
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/resize", disk=disk, size=size))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def move_vm_disk(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="Source QEMU VM ID.")],
        disk: Annotated[str, Field(description="Disk identifier (e.g., 'scsi0').")],
        storage: Annotated[str, Field(description="Target storage ID for relocation.")] = "",
        target_vmid: Annotated[int, Field(description="Target VM ID (to reattach disk to another VM).")] = 0,
        target_disk: Annotated[str, Field(description="Target disk drive slot on destination VM.")] = "",
        delete_original: Annotated[bool, Field(description="If True, remove original disk image after copy.")] = False,
    ) -> str:
        """Move a VM virtual disk to different storage or attach it to another VM.

        Use when migrating VM disks between storage pools.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False))
    def unlink_vm_disk(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        idlist: Annotated[str, Field(description="Comma-separated disk keys to detach (e.g., 'scsi0', 'scsi1,virtio0').")],
        force: Annotated[bool, Field(description="If True, force detachment even if guest is running or locked.")] = False,
    ) -> str:
        """Unlink and detach a virtual disk from a VM without deleting the underlying storage volume.

        Use when safely disconnecting a disk image from a VM so it moves to 'unused[n]' status.

        Args:
            node: The node name.
            vmid: The VM ID.
            idlist: Comma-separated disk keys (e.g. 'scsi0,scsi1').
            force: Force detachment.
        """
        params: dict = {"idlist": idlist}
        if force:
            params["force"] = 1
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/unlink", **params))

    # ── Snapshots ─────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def list_vm_snapshots(
        node: Annotated[str, Field(description="PVE node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
    ) -> str:
        """List snapshots created for a QEMU VM.

        Use when inspecting VM restore points and snapshot trees.
        To create a snapshot, use create_vm_snapshot.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/snapshot"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def create_vm_snapshot(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        snapname: Annotated[str, Field(description="Snapshot identifier name.")],
        description: Annotated[str, Field(description="Snapshot description or notes.")] = "",
        vmstate: Annotated[bool, Field(description="If True, include active RAM state for running VMs.")] = False,
    ) -> str:
        """Create a point-in-time snapshot of a QEMU virtual machine.

        Use prior to OS or application upgrades to enable quick recovery.
        To revert to a snapshot, use rollback_vm_snapshot.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=True))
    def delete_vm_snapshot(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        snapname: Annotated[str, Field(description="Snapshot name to delete.")],
        force: Annotated[bool, Field(description="If True, force delete snapshot.")] = False,
    ) -> str:
        """Delete a VM snapshot.

        Use when deleting obsolete restore points.

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

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=True, idempotentHint=False))
    def rollback_vm_snapshot(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        snapname: Annotated[str, Field(description="Snapshot name to revert VM state to.")],
        start: Annotated[bool, Field(description="If True, automatically start the VM after rollback completes.")] = False,
    ) -> str:
        """Revert QEMU VM hardware configuration and disk contents to a previous snapshot state.

        Use when restoring VM virtual disk and configuration state to a saved point in time.

        WARNING: Unsaved changes made after the snapshot will be lost.

        Args:
            node: The node name.
            vmid: The VM ID.
            snapname: The snapshot name to rollback to.
            start: Start the VM after restoring snapshot.
        """
        params: dict = {}
        if start:
            params["start"] = 1
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/snapshot/{snapname}/rollback", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_snapshot_config(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        snapname: Annotated[str, Field(description="Snapshot name.")],
    ) -> str:
        """Get the stored VM hardware configuration associated with a snapshot.

        Use when reviewing hardware settings saved in a historical snapshot.

        Args:
            node: The node name.
            vmid: The VM ID.
            snapname: The snapshot name.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/snapshot/{snapname}/config"))

    # ── Cloud-Init ────────────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_cloudinit(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
    ) -> str:
        """Get Cloud-Init settings (user, SSH keys, IP config) configured on a VM.

        Use when auditing Cloud-Init provisioning settings.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/cloudinit"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def update_vm_cloudinit(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        ciuser: Annotated[str, Field(description="Cloud-Init username.")] = "",
        cipassword: Annotated[str, Field(description="Cloud-Init password.")] = "",
        sshkeys: Annotated[str, Field(description="Newline-delimited SSH public keys.")] = "",
        ipconfig0: Annotated[str, Field(description="IP config for net0 (e.g., 'ip=dhcp' or 'ip=10.0.0.5/24,gw=10.0.0.1').")] = "",
        nameserver: Annotated[str, Field(description="DNS nameserver IP.")] = "",
        searchdomain: Annotated[str, Field(description="DNS search domain.")] = "",
    ) -> str:
        """Configure Cloud-Init automation parameters (default user, SSH keys, static IP addresses, DNS).

        Use when customizing automated cloud image initialization.

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
            ("ciuser", ciuser),
            ("cipassword", cipassword),
            ("sshkeys", sshkeys),
            ("ipconfig0", ipconfig0),
            ("nameserver", nameserver),
            ("searchdomain", searchdomain),
        ]:
            if val:
                params[key] = val
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/cloudinit", **params))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def dump_vm_cloudinit(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        type: Annotated[str, Field(description="Cloud-Init payload section to inspect ('user', 'network', 'meta').")] = "user",
    ) -> str:
        """Dump generated Cloud-Init ISO metadata (user-data, network-data, or meta-data).

        Use when inspecting rendered Cloud-Init configuration files.

        Args:
            node: The node name.
            vmid: The VM ID.
            type: Config type: 'user', 'network', or 'meta'.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/cloudinit/dump", type=type))

    # ── QEMU Guest Agent ──────────────────────────────────────────────

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def vm_agent_exec(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        command: Annotated[str, Field(description="Command binary path or executable command line string.")],
        input_data: Annotated[str, Field(description="Data string to pass to command stdin.")] = "",
    ) -> str:
        """Execute an arbitrary command inside a running VM via QEMU Guest Agent.

        Use when running guest OS commands without SSH connection.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def vm_agent_exec_status(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        pid: Annotated[int, Field(description="PID integer returned from vm_agent_exec.")],
    ) -> str:
        """Get exit status, stdout, and stderr for a command previously executed via QEMU Guest Agent.

        Use when polling completion status of guest agent commands.

        Args:
            node: The node name.
            vmid: The VM ID.
            pid: The PID returned by the exec call.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/agent/exec-status", pid=pid))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def vm_agent_file_read(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        file: Annotated[str, Field(description="Absolute file path inside guest VM.")],
    ) -> str:
        """Read text contents of a file inside a VM via QEMU Guest Agent.

        Use when inspecting configuration or log files inside guest VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            file: Absolute file path inside the guest.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/agent/file-read", file=file))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def vm_agent_file_write(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        file: Annotated[str, Field(description="Absolute destination file path inside guest VM.")],
        content: Annotated[str, Field(description="Text content to write to file.")],
    ) -> str:
        """Write content to a file inside a VM via QEMU Guest Agent.

        Use when injecting configuration files into running VMs.

        Args:
            node: The node name.
            vmid: The VM ID.
            file: Absolute file path inside the guest.
            content: File content to write.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/agent/file-write", file=file, content=content))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def vm_agent_get_info(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        info_type: Annotated[
            str,
            Field(description="Information metric to retrieve ('get-osinfo', 'get-host-name', 'get-time', 'get-timezone', 'get-users', 'get-vcpus', 'get-fsinfo', 'network-get-interfaces')."),
        ] = "get-osinfo",
    ) -> str:
        """Get guest OS information (network interfaces, IP addresses, OS version, mounted filesystems) via QEMU Agent.

        Use when inspecting operational details inside guest VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            info_type: Info to retrieve: 'get-osinfo', 'get-host-name', 'get-time', 'get-timezone', 'get-users', 'get-vcpus', 'get-fsinfo', 'network-get-interfaces'.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/agent/{info_type}"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=True))
    def vm_agent_set_password(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        username: Annotated[str, Field(description="Target user account inside guest OS.")],
        password: Annotated[str, Field(description="New password string.")],
        crypted: Annotated[bool, Field(description="If True, password string is already crypted.")] = False,
    ) -> str:
        """Reset user account password inside a VM via QEMU Guest Agent.

        Use when setting or resetting user passwords in VM guest OS.

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

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_vncproxy(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        websocket: Annotated[bool, Field(description="If True, prepare WebSocket proxy connection.")] = True,
    ) -> str:
        """Create a VNC proxy connection ticket and port for remote graphical console access.

        Use when establishing web VNC sessions to a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            websocket: Use WebSocket connection.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/vncproxy", websocket=int(websocket)))

    @mcp.tool(annotations=ToolAnnotations(readOnlyHint=True))
    def get_vm_spiceproxy(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
    ) -> str:
        """Create a SPICE proxy connection configuration for high-performance remote desktop access.

        Use when opening SPICE console sessions to a VM.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/spiceproxy"))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def send_vm_key(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        key: Annotated[str, Field(description="Key event sequence string (e.g., 'ctrl-alt-delete').")],
    ) -> str:
        """Send virtual key stroke events (e.g., Ctrl+Alt+Del) directly to a VM console.

        Use when sending key events to guest virtual machine input console.

        Args:
            node: The node name.
            vmid: The VM ID.
            key: Key combination (e.g. 'ctrl-alt-delete').
        """
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/sendkey", key=key))

    @mcp.tool(annotations=ToolAnnotations(destructiveHint=False, idempotentHint=False))
    def send_vm_monitor_command(
        node: Annotated[str, Field(description="PVE host node name.")],
        vmid: Annotated[int, Field(description="QEMU VM ID.")],
        command: Annotated[str, Field(description="QEMU monitor command string (e.g., 'info block').")],
    ) -> str:
        """Send raw QEMU HMP/QMP monitor command string directly to hypervisor instance.

        Use for low-level QEMU hypervisor debugging and inspection.

        Args:
            node: The node name.
            vmid: The VM ID.
            command: The QEMU monitor command.
        """
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/monitor", command=command))
