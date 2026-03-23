# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

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
