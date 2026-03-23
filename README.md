# Proxmox MCP Server

## Overview

This is a Model Context Protocol (MCP) server that provides tools for interacting with Proxmox VE infrastructure. It enables AI assistants and other MCP clients to manage virtual machines, containers, storage, networking, firewall rules, high availability, and more through a standardized interface. The server supports both API token and password-based authentication against local and remote Proxmox instances.

## Distributions

- PyPI   - https://pypi.org/project/proxmox-mcp-server/
- Docker - https://hub.docker.com/r/mcp/proxmox

## Tools

### Node Management

- **`list_nodes`** - List all nodes in the Proxmox cluster with their status, CPU, memory, and uptime
- **`get_node_status`** - Get detailed status of a specific node including CPU, memory, disk, uptime, and kernel info
- **`get_node_config`** - Get the configuration of a node (description, wakeonlan, etc.)
- **`get_node_dns`** - Get DNS settings for a node
- **`get_node_network`** - Get network interface configuration for a node
- **`get_node_network_interface`** - Get details for a specific network interface
- **`create_node_network_interface`** - Create a network interface on a node
- **`list_node_services`** - List all system services on a node (pve, ssh, cron, etc.)
- **`manage_node_service`** - Start, stop, restart, or reload a system service on a node
- **`get_node_syslog`** - Read system log (syslog) entries from a node
- **`get_node_journal`** - Read systemd journal entries from a node
- **`list_node_tasks`** - List recent tasks on a node
- **`get_task_status`** - Get the status of a specific task by its UPID
- **`get_task_log`** - Get log output of a specific task
- **`stop_task`** - Stop (abort) a running task
- **`get_node_time`** - Get the current time and timezone of a node
- **`get_node_subscription`** - Get subscription status for a node
- **`get_node_apt_update`** - List available package updates on a node
- **`run_apt_update`** - Refresh the package index on a node (apt update)
- **`get_node_report`** - Generate a system report for a node (useful for diagnostics)
- **`get_node_disks`** - List physical disks on a node
- **`get_disk_smart`** - Get S.M.A.R.T. health data for a disk
- **`get_node_hardware_pci`** - List PCI hardware devices on a node (for passthrough)
- **`get_node_hardware_usb`** - List USB hardware devices on a node
- **`get_node_capabilities_qemu`** - Get QEMU capabilities for a node: supported CPU models, machine types, etc.
- **`get_node_storage_scan`** - Scan for available storage targets (NFS, CIFS, iSCSI, LVM, ZFS, PBS)
- **`wakeonlan_node`** - Send a Wake-on-LAN magic packet to a node
- **`startall_node`** - Start all VMs and containers on a node (respecting boot order)
- **`stopall_node`** - Stop all VMs and containers on a node
- **`get_node_hosts`** - Get the /etc/hosts file content for a node
- **`get_node_version`** - Get Proxmox VE version information for a specific node
- **`get_node_netstat`** - Get network statistics for a node (per-interface traffic)
- **`get_node_aplinfo`** - List available appliance templates (LXC templates) that can be downloaded
- **`download_appliance_template`** - Download an appliance template to local storage

### QEMU Virtual Machines

- **`list_vms`** - List all QEMU virtual machines on a node with status, memory, CPU, and disk info
- **`get_vm_status`** - Get the current runtime status of a VM (state, CPU, memory, disk, network, uptime)
- **`get_vm_config`** - Get the configuration of a VM
- **`get_vm_pending`** - Get pending configuration changes for a VM (not yet applied)
- **`get_vm_feature`** - Check if a specific feature is available/supported for a VM (e.g. snapshot, clone, copy)
- **`get_vm_rrddata`** - Get RRD statistics data for a VM (CPU, memory, disk, network over time)
- **`create_vm`** - Create a new QEMU virtual machine
- **`update_vm_config`** - Update the configuration of an existing VM
- **`delete_vm`** - Delete a VM (must be stopped first)
- **`start_vm`** - Start a VM
- **`stop_vm`** - Hard-stop a VM (like pulling the power plug)
- **`shutdown_vm`** - Gracefully shut down a VM via ACPI
- **`reboot_vm`** - Reboot a VM via ACPI
- **`suspend_vm`** - Suspend a VM (pause execution or hibernate to disk)
- **`resume_vm`** - Resume a suspended/paused VM
- **`reset_vm`** - Hard reset a VM (like pressing the reset button)
- **`clone_vm`** - Clone a VM to create a new one (full copy or linked clone)
- **`migrate_vm`** - Migrate a VM to another node in the cluster
- **`convert_vm_to_template`** - Convert a VM into a template (irreversible)
- **`resize_vm_disk`** - Resize a VM disk (can only grow, not shrink)
- **`move_vm_disk`** - Move a VM disk to different storage or attach to another VM
- **`list_vm_snapshots`** - List all snapshots of a VM
- **`create_vm_snapshot`** - Create a snapshot of a VM
- **`delete_vm_snapshot`** - Delete a VM snapshot
- **`rollback_vm_snapshot`** - Rollback a VM to a previous snapshot (current state will be lost)
- **`get_vm_snapshot_config`** - Get the configuration stored in a VM snapshot
- **`get_vm_cloudinit`** - Get Cloud-Init configuration for a VM
- **`update_vm_cloudinit`** - Set Cloud-Init parameters for a VM (user, password, SSH keys, network)
- **`dump_vm_cloudinit`** - Dump the Cloud-Init generated config file (user-data, network-data, or meta-data)
- **`vm_agent_exec`** - Execute a command inside a VM via the QEMU Guest Agent
- **`vm_agent_exec_status`** - Get the status/result of a command previously executed via the guest agent
- **`vm_agent_file_read`** - Read a file from inside a VM via the guest agent
- **`vm_agent_file_write`** - Write content to a file inside a VM via the guest agent
- **`vm_agent_get_info`** - Get various system information from a VM via the guest agent
- **`vm_agent_set_password`** - Set a user password inside a VM via the guest agent
- **`get_vm_vncproxy`** - Create a VNC proxy connection ticket for a VM (for console access)
- **`get_vm_spiceproxy`** - Create a SPICE proxy connection for a VM console
- **`send_vm_key`** - Send a key event to a VM (e.g. ctrl-alt-del)
- **`send_vm_monitor_command`** - Send a QEMU monitor command to a VM (advanced/low-level)

### LXC Containers

- **`list_containers`** - List all LXC containers on a node with status, memory, CPU, and disk info
- **`get_container_status`** - Get the current runtime status of a container
- **`get_container_config`** - Get the configuration of a container
- **`get_container_pending`** - Get pending configuration changes for a container
- **`get_container_interfaces`** - Get network interfaces and IPs of a running container
- **`get_container_rrddata`** - Get RRD statistics data for a container (CPU, memory, disk, network over time)
- **`get_container_feature`** - Check if a feature is available for a container (snapshot, clone, copy)
- **`create_container`** - Create a new LXC container
- **`update_container_config`** - Update the configuration of an existing container
- **`delete_container`** - Delete a container (must be stopped first unless force=True)
- **`start_container`** - Start a container
- **`stop_container`** - Hard-stop a container (immediate, like power off)
- **`shutdown_container`** - Gracefully shut down a container
- **`reboot_container`** - Reboot a container
- **`suspend_container`** - Suspend (freeze) a container
- **`resume_container`** - Resume a suspended container
- **`clone_container`** - Clone a container
- **`migrate_container`** - Migrate a container to another node
- **`convert_container_to_template`** - Convert a container into a template (irreversible)
- **`resize_container_disk`** - Resize a container disk/volume
- **`move_container_volume`** - Move a container volume to different storage or to another container
- **`list_container_snapshots`** - List all snapshots of a container
- **`create_container_snapshot`** - Create a snapshot of a container
- **`delete_container_snapshot`** - Delete a container snapshot
- **`rollback_container_snapshot`** - Rollback a container to a previous snapshot

### Storage

- **`list_storage`** - List all configured storage pools at the datacenter level
- **`get_storage_config`** - Get configuration of a specific storage pool
- **`create_storage`** - Create a new storage pool configuration
- **`update_storage`** - Update an existing storage pool configuration
- **`delete_storage`** - Delete a storage pool configuration (does not delete data on the backend)
- **`list_node_storage`** - List storage pools available on a specific node with usage info
- **`get_node_storage_status`** - Get usage status of a storage pool on a node (total, used, available)
- **`list_storage_content`** - List content of a storage pool (disk images, ISOs, templates, backups)
- **`get_storage_volume_info`** - Get details about a specific volume in storage
- **`allocate_storage_volume`** - Allocate a new disk volume in storage
- **`delete_storage_volume`** - Delete a volume from storage
- **`upload_to_storage`** - Upload a file (ISO, template, etc.) to storage
- **`download_url_to_storage`** - Download a file from a URL directly to storage (ISO, template, etc.)
- **`get_storage_rrddata`** - Get RRD statistics for a storage pool (usage over time)
- **`prune_storage_backups`** - Prune (delete) old backups from storage according to retention policy
- **`list_file_restore`** - List files in a backup volume for file-level restore (PBS backups)
- **`list_lvm_volumes`** - List LVM volume groups on a node
- **`create_lvm`** - Create a new LVM volume group on a device
- **`list_lvmthin_pools`** - List LVM thin pools on a node
- **`create_lvmthin`** - Create a new LVM thin pool
- **`list_zfs_pools`** - List ZFS pools on a node
- **`get_zfs_pool`** - Get details of a ZFS pool
- **`create_zfs_pool`** - Create a new ZFS pool
- **`list_directory_storage`** - List directory-based storage mounts on a node
- **`create_directory_storage`** - Create a directory-based storage mount from a device
- **`initialize_gpt`** - Initialize a disk with GPT partition table (WARNING: destroys all data)

### Cluster

- **`get_version`** - Get the Proxmox VE API version information
- **`get_cluster_status`** - Get cluster status (nodes online, quorum, HA state)
- **`get_cluster_resources`** - List all resources across the cluster (VMs, containers, storage, nodes)
- **`get_cluster_tasks`** - List recent tasks across all nodes in the cluster
- **`get_cluster_log`** - Get the cluster log (recent events)
- **`get_next_vmid`** - Get the next available VMID in the cluster
- **`get_cluster_options`** - Get datacenter/cluster-wide options (keyboard layout, console, language, etc.)
- **`update_cluster_options`** - Update datacenter/cluster-wide options
- **`get_cluster_config`** - Get the current cluster configuration (corosync, nodes, join info)
- **`get_cluster_config_nodes`** - List nodes configured in the cluster
- **`get_cluster_join_info`** - Get info needed to join a node to this cluster
- **`join_cluster`** - Join a node to an existing cluster
- **`get_cluster_totem`** - Get the corosync totem configuration
- **`list_replication_jobs`** - List all replication jobs in the cluster
- **`get_replication_job`** - Get a specific replication job configuration
- **`create_replication_job`** - Create a storage replication job
- **`delete_replication_job`** - Delete a replication job
- **`list_metric_servers`** - List configured metric servers (InfluxDB, Graphite)
- **`get_metric_server`** - Get metric server configuration
- **`list_notification_endpoints`** - List all configured notification endpoints (sendmail, gotify, smtp, webhook)
- **`list_notification_targets`** - List all notification targets
- **`list_notification_matchers`** - List all notification matchers (rules that route notifications)
- **`test_notification_target`** - Send a test notification to a target
- **`bulk_start_guests`** - Bulk start guests across the cluster
- **`bulk_shutdown_guests`** - Bulk shutdown guests across the cluster
- **`bulk_migrate_guests`** - Bulk migrate guests to a target node
- **`get_ceph_status_cluster`** - Get Ceph cluster status (health, monitors, OSDs, PGs)
- **`get_ceph_metadata`** - Get Ceph metadata (versions, services across nodes)
- **`get_ceph_flags`** - Get Ceph global flags (noout, noscrub, etc.)
- **`set_ceph_flags`** - Set a Ceph global flag
- **`get_ceph_status_node`** - Get Ceph status from a specific node's perspective
- **`list_ceph_osds`** - List Ceph OSDs on a node
- **`create_ceph_osd`** - Create a new Ceph OSD on a device
- **`list_ceph_pools`** - List Ceph pools
- **`create_ceph_pool`** - Create a new Ceph pool
- **`list_ceph_monitors`** - List Ceph monitors
- **`list_ceph_managers`** - List Ceph managers
- **`list_ceph_mds`** - List Ceph metadata servers (MDS, for CephFS)
- **`list_ceph_fs`** - List CephFS filesystems
- **`get_ceph_config`** - Get the raw Ceph configuration
- **`get_ceph_crush_rules`** - Get Ceph CRUSH rules
- **`list_scheduled_jobs`** - List all scheduled cluster jobs
- **`list_realm_sync_jobs`** - List realm synchronization jobs
- **`list_pci_mappings`** - List PCI device mappings for passthrough
- **`list_usb_mappings`** - List USB device mappings for passthrough
- **`list_dir_mappings`** - List directory mappings

### Access Control

- **`list_users`** - List all users in Proxmox
- **`get_user`** - Get details for a specific user
- **`create_user`** - Create a new user
- **`update_user`** - Update an existing user
- **`delete_user`** - Delete a user
- **`list_user_tokens`** - List API tokens for a user
- **`get_user_token`** - Get details for a specific API token
- **`create_user_token`** - Create a new API token for a user (token value shown only once)
- **`delete_user_token`** - Delete an API token
- **`list_groups`** - List all user groups
- **`get_group`** - Get group details
- **`create_group`** - Create a new group
- **`update_group`** - Update a group
- **`delete_group`** - Delete a group
- **`list_roles`** - List all available roles
- **`get_role`** - Get role details and its privileges
- **`create_role`** - Create a new role with specific privileges
- **`update_role`** - Update role privileges
- **`delete_role`** - Delete a role
- **`get_acl`** - Get the full ACL — shows all permission assignments
- **`update_acl`** - Add or remove ACL entries (permission assignments)
- **`list_auth_domains`** - List configured authentication realms (PAM, PVE, LDAP, AD, OpenID)
- **`get_auth_domain`** - Get authentication domain configuration
- **`sync_auth_domain`** - Sync users/groups from an external auth domain (LDAP/AD)
- **`list_tfa`** - List TFA (two-factor auth) entries
- **`get_permissions`** - Check effective permissions for a user on a given path
- **`change_password`** - Change a user's password

### Backup

- **`list_backup_jobs`** - List all scheduled backup jobs (vzdump) in the cluster
- **`get_backup_job`** - Get details of a specific backup job
- **`get_backup_job_included_volumes`** - Get volumes included in a backup job
- **`create_backup_job`** - Create a scheduled backup job
- **`update_backup_job`** - Update a scheduled backup job
- **`delete_backup_job`** - Delete a scheduled backup job
- **`create_vzdump`** - Start an immediate backup (vzdump) on a node
- **`get_vzdump_defaults`** - Get the default vzdump configuration for a node
- **`get_vzdump_extractconfig`** - Extract the guest configuration from a vzdump backup archive
- **`list_backup_file_restore`** - List files in a vzdump backup for single-file restore
- **`download_file_restore`** - Download a file from a vzdump backup

### Firewall

- **`get_cluster_firewall_options`** - Get cluster-wide firewall options (enable, policy_in, policy_out, etc.)
- **`set_cluster_firewall_options`** - Set cluster-wide firewall options
- **`list_cluster_firewall_rules`** - List cluster-level firewall rules
- **`get_cluster_firewall_rule`** - Get a specific cluster firewall rule
- **`create_cluster_firewall_rule`** - Create a cluster-level firewall rule
- **`update_cluster_firewall_rule`** - Update a cluster-level firewall rule
- **`delete_cluster_firewall_rule`** - Delete a cluster-level firewall rule
- **`list_firewall_groups`** - List firewall security groups (reusable sets of rules)
- **`get_firewall_group_rules`** - List rules in a firewall security group
- **`create_firewall_group`** - Create a new firewall security group
- **`create_firewall_group_rule`** - Add a rule to a firewall security group
- **`list_firewall_aliases`** - List cluster firewall aliases (named IP addresses/ranges)
- **`create_firewall_alias`** - Create a firewall alias (named IP address or CIDR)
- **`delete_firewall_alias`** - Delete a firewall alias
- **`list_firewall_ipsets`** - List cluster firewall IP sets (named groups of IPs)
- **`create_firewall_ipset`** - Create a new firewall IP set
- **`list_firewall_ipset_entries`** - List entries in a firewall IP set
- **`add_firewall_ipset_entry`** - Add an IP/CIDR to an IP set
- **`delete_firewall_ipset_entry`** - Remove an IP/CIDR from an IP set
- **`list_firewall_macros`** - List available firewall macros (predefined rule sets like SSH, HTTP, etc.)
- **`get_firewall_refs`** - Get available firewall references (aliases, ipsets, names usable in rules)
- **`get_node_firewall_options`** - Get firewall options for a specific node
- **`set_node_firewall_options`** - Set firewall options for a node
- **`list_node_firewall_rules`** - List firewall rules for a node
- **`get_node_firewall_log`** - Get firewall log for a node
- **`get_vm_firewall_options`** - Get firewall options for a QEMU VM
- **`set_vm_firewall_options`** - Set firewall options for a QEMU VM
- **`list_vm_firewall_rules`** - List firewall rules for a QEMU VM
- **`create_vm_firewall_rule`** - Create a firewall rule for a QEMU VM
- **`get_container_firewall_options`** - Get firewall options for an LXC container
- **`list_container_firewall_rules`** - List firewall rules for an LXC container
- **`create_container_firewall_rule`** - Create a firewall rule for an LXC container

### High Availability

- **`get_ha_status`** - Get HA manager status (active, quorum, manager status)
- **`get_ha_manager_status`** - Get detailed HA manager status
- **`list_ha_resources`** - List all HA-managed resources
- **`get_ha_resource`** - Get HA resource configuration
- **`create_ha_resource`** - Add a resource to HA management
- **`update_ha_resource`** - Update an HA resource configuration
- **`delete_ha_resource`** - Remove a resource from HA management
- **`migrate_ha_resource`** - Request migration of an HA resource to a different node
- **`relocate_ha_resource`** - Request relocation of an HA resource to a different node
- **`list_ha_groups`** - List HA groups (define which nodes can run HA resources)
- **`get_ha_group`** - Get HA group configuration
- **`create_ha_group`** - Create an HA group
- **`update_ha_group`** - Update an HA group
- **`delete_ha_group`** - Delete an HA group

### SDN

- **`list_sdn_vnets`** - List SDN virtual networks (VNets)
- **`get_sdn_vnet`** - Get SDN VNet configuration
- **`create_sdn_vnet`** - Create an SDN VNet
- **`update_sdn_vnet`** - Update an SDN VNet
- **`delete_sdn_vnet`** - Delete an SDN VNet
- **`list_sdn_subnets`** - List subnets for an SDN VNet
- **`create_sdn_subnet`** - Create a subnet for an SDN VNet
- **`list_sdn_zones`** - List SDN zones
- **`get_sdn_zone`** - Get SDN zone configuration
- **`create_sdn_zone`** - Create an SDN zone
- **`delete_sdn_zone`** - Delete an SDN zone
- **`list_sdn_controllers`** - List SDN controllers (e.g. EVPN controller)
- **`get_sdn_controller`** - Get SDN controller configuration
- **`list_sdn_ipams`** - List IPAM (IP Address Management) plugins
- **`get_sdn_ipam`** - Get IPAM plugin configuration
- **`list_sdn_dns`** - List SDN DNS plugins
- **`apply_sdn_changes`** - Apply pending SDN configuration changes to all nodes

### Pools & ACME

- **`list_pools`** - List all resource pools
- **`get_pool`** - Get pool configuration and members
- **`create_pool`** - Create a resource pool
- **`update_pool`** - Update a resource pool (add/remove members)
- **`delete_pool`** - Delete a resource pool
- **`list_acme_accounts`** - List ACME (Let's Encrypt) accounts
- **`get_acme_account`** - Get ACME account details
- **`register_acme_account`** - Register a new ACME account
- **`list_acme_plugins`** - List ACME DNS challenge plugins
- **`get_acme_plugin`** - Get ACME plugin configuration
- **`get_acme_directories`** - List known ACME directory URLs
- **`get_acme_tos`** - Get the ACME Terms of Service URL
- **`order_node_certificate`** - Order/renew ACME certificate for a node
- **`get_node_certificates`** - Get certificate info for a node

### Generic

- **`proxmox_api_raw`** - Make an arbitrary Proxmox API call for any endpoint not covered by specific tools

## Proxmox Documentation

For more information about Proxmox VE, refer to the official documentation:

- **Proxmox VE Documentation**: https://pve.proxmox.com/pve-docs/
- **API Reference**: https://pve.proxmox.com/pve-docs/api-viewer/
- **Proxmox VE Wiki**: https://pve.proxmox.com/wiki/Main_Page
- **proxmoxer Python Library**: https://proxmoxer.github.io/docs/

## VS Code MCP Config

Add a `.vscode/mcp.json` file to your workspace. Choose the approach that fits your setup.

### Docker (environment variables)

Recommended when running via Docker. Configuration is passed through environment variables.

```json
{
  "servers": {
    "proxmox": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "PROXMOX_HOST",
        "-e", "PROXMOX_PORT",
        "-e", "PROXMOX_USER",
        "-e", "PROXMOX_TOKEN_NAME",
        "-e", "PROXMOX_TOKEN_VALUE",
        "-e", "PROXMOX_VERIFY_SSL",
        "mcp/proxmox"
      ],
      "env": {
        "PROXMOX_HOST": "192.168.1.100",
        "PROXMOX_PORT": "8006",
        "PROXMOX_USER": "root@pam",
        "PROXMOX_TOKEN_NAME": "mcp",
        "PROXMOX_TOKEN_VALUE": "your-token-here",
        "PROXMOX_VERIFY_SSL": "0"
      }
    }
  }
}
```

### Python via uvx (environment variables)

Recommended when running from PyPI via [`uvx`](https://docs.astral.sh/uv/guides/tools/). No local install required — `uvx` fetches and runs the package automatically.

```json
{
  "servers": {
    "proxmox": {
      "command": "uvx",
      "args": ["proxmox-mcp-server"],
      "env": {
        "PROXMOX_HOST": "192.168.1.100",
        "PROXMOX_PORT": "8006",
        "PROXMOX_USER": "root@pam",
        "PROXMOX_TOKEN_NAME": "mcp",
        "PROXMOX_TOKEN_VALUE": "your-token-here",
        "PROXMOX_VERIFY_SSL": "0"
      }
    }
  }
}
```

### Configuration Options

| Option | Environment Variable | Default |
|--------|---------------------|---------|
| Proxmox host | `PROXMOX_HOST` | — |
| API port | `PROXMOX_PORT` | `8006` |
| User | `PROXMOX_USER` | `root@pam` |
| API token name | `PROXMOX_TOKEN_NAME` | — |
| API token value | `PROXMOX_TOKEN_VALUE` | — |
| Password | `PROXMOX_PASSWORD` | — |
| SSL verification | `PROXMOX_VERIFY_SSL` | `0` |

Either `PROXMOX_TOKEN_NAME` + `PROXMOX_TOKEN_VALUE` or `PROXMOX_PASSWORD` is required for authentication.

## Development

### Running Tests

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest tests/ -v
```

### Building the Docker Image

```bash
docker build -t mcp/proxmox:latest .
```

## License

Apache-2.0
