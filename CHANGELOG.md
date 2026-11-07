# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [1.0.8] - 2026-11-06

### Added
- **Node Power Lifecycle**: Added `reboot_node` and `shutdown_node` tools in `nodes.py` (`POST /nodes/{node}/status` with `command: reboot|shutdown`).
- **Storage Replication CRUD**: Added `update_replication_job` (`PUT /cluster/replication/{id}`), `get_replication_log` (`GET /cluster/replication/{id}/log`), and `get_replication_status` (`GET /cluster/replication/{id}/status`) in `cluster.py`.
- **ZFS & Disk Management**: Added `destroy_zfs_pool` (`DELETE /nodes/{node}/disks/zfs/{name}`), `zfs_scrub` (`POST /nodes/{node}/disks/zfs/{name}`), `delete_lvm`, `delete_lvmthin`, and `delete_directory_storage` in `storage.py`.
- **QEMU Unlink**: Added `unlink_vm_disk` (`PUT /nodes/{node}/qemu/{vmid}/unlink`) to safely detach virtual disk images without volume deletion in `qemu.py`.
- **Dynamic Config & Extra Options**: Added `extra_config` parameter to `update_vm_config` and `update_container_config` allowing dynamic key-value / JSON updates for virtual disks, I/O limits (`mbps_wr`, `iops_wr`), secondary network interfaces (`net1`, `net2`), and mount points (`mp0`).
- **VM Recovery & Lifecycle Enhancements**: Added `overrule_shutdown` flag to `stop_vm` and `start` flag to `rollback_vm_snapshot`.
- **Router Ergonomics**: Supported exposing a curated set of 19 core operational tools directly alongside the router in routed mode, configurable via `ALWAYS_VISIBLE_TOOLS`.

## [1.0.4] - 2026-07-27

### Refactored
- **Tool Definition Quality Score (TDQS) Optimization**: Achieved **Tier A+ (5.00 / 5.0)** across all 285 registered tool definitions in 11 modules (`access`, `backup`, `cluster`, `firewall`, `ha`, `lxc`, `nodes`, `pools`, `qemu`, `sdn`, `storage`).
- **Behavioral Metadata**: Added FastMCP `ToolAnnotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`) to all `@mcp.tool()` decorators for enhanced safety awareness in AI client environments.
- **Schema Parameter Documentation**: Upgraded 100% of function parameters to Pydantic `Annotated[T, Field(description=...)]` types to guarantee comprehensive metadata generation.
- **Operational Guidelines**: Standardized tool docstrings with explicit "Use when..." context to improve LLM tool selection and prevent ambiguity.

## [1.0.3] - 2026-07-26

### Fixed
- Redirected container entrypoint `echo` startup messages to `stderr` (`>&2`). Prevents non-JSON-RPC output on `stdout` which caused stdio MCP clients (such as Antigravity) to fail initialization with `invalid character 'S' looking for beginning of value`.

## [1.0.2] - 2026-07-24

### Added
- Integrated ContextForge Gateway natively into the Docker image.
- Added `ENABLE_CONTEXTFORGE_GATEWAY` environment variable to conditionally run the gateway.
- Made the Gateway port configurable via `GATEWAY_PORT` (defaults to 8000).

## [1.0.1] - 2026-07-24

### Fixed
- Fixed an import error in IBM ContextForge by removing a semicolon from the `create_vm` tool docstring.
- Added GitHub Actions workflow to publish the Docker image to GitHub Container Registry (GHCR).

## [0.1.0] - 2026-03-23

### Added

- Initial release with 286 MCP tools covering the full Proxmox VE API
- Node management (status, config, networking, services, tasks, disks, hardware)
- QEMU VM lifecycle (create, clone, migrate, snapshots, cloud-init, QEMU agent)
- LXC container management (create, clone, migrate, snapshots, templates)
- Storage management (datacenter config, volumes, LVM/ZFS/directory)
- Cluster operations (status, config, Ceph, replication, metrics, notifications)
- Access control (users, groups, roles, ACL, API tokens, auth domains)
- Backup management (vzdump, scheduled jobs, file restore)
- Firewall rules (cluster, node, VM, and container level)
- High Availability (resources, groups, migration)
- SDN (VNets, zones, controllers, IPAM)
- Resource pools and ACME certificate management
- Generic `proxmox_api_raw` escape-hatch tool for arbitrary API calls
- Docker support with docker-compose
- API token and password authentication
