#!/usr/bin/env python3
"""Generate synthetic training data for fine-tuning FunctionGemma on Proxmox MCP tools.

Reads the tool catalog from the MCP server source and produces query-to-tool
mappings in the chat format expected by FunctionGemma.

Usage:
    python generate_training_data.py            # writes to data/training_data.json
    python generate_training_data.py --output custom_output.json
"""

import ast
import json
import os
import random
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Query templates per category – each list contains templates with {placeholders}
# that get filled with contextual values to create varied training examples.
# ---------------------------------------------------------------------------

CATEGORY_TEMPLATES = {
    # -- access / users / roles / tokens / permissions / ACLs / auth domains / TFA
    "access": {
        "list_users": [
            "Show me all Proxmox users",
            "List every user account",
            "Who has access to the cluster?",
            "Get the user list",
            "What users are configured?",
        ],
        "get_user": [
            "Get details for user {user}",
            "Show me info about the {user} account",
            "What permissions does {user} have?",
            "Look up user {user}",
        ],
        "create_user": [
            "Create a new user {user}",
            "Add a user account for {user}",
            "I need to create the user {user}",
            "Set up a new Proxmox user called {user}",
        ],
        "update_user": [
            "Update user {user}",
            "Change the email for user {user}",
            "Modify the {user} account settings",
        ],
        "delete_user": [
            "Delete user {user}",
            "Remove the {user} account",
            "I need to delete the user {user}",
        ],
        "list_user_tokens": [
            "List API tokens for user {user}",
            "What tokens does {user} have?",
            "Show me all tokens belonging to {user}",
        ],
        "get_user_token": [
            "Get details for token {token} of user {user}",
            "Show me the {token} API token info for {user}",
        ],
        "create_user_token": [
            "Create an API token for user {user}",
            "Generate a new token called {token} for {user}",
            "I need a new API token for {user}",
        ],
        "delete_user_token": [
            "Delete the {token} token for user {user}",
            "Remove API token {token} from {user}",
            "Revoke the {token} token belonging to {user}",
        ],
        "list_roles": [
            "List all roles",
            "What roles are available?",
            "Show me the configured roles",
        ],
        "get_role": [
            "Show me the privileges of the {role} role",
            "What does the {role} role include?",
            "Get role details for {role}",
        ],
        "create_role": [
            "Create a new role called {role}",
            "Add a custom role named {role}",
            "I need to create the {role} role",
        ],
        "update_role": [
            "Update the {role} role",
            "Change the privileges on the {role} role",
            "Modify role {role}",
        ],
        "delete_role": [
            "Delete the {role} role",
            "Remove role {role}",
        ],
        "get_acl": [
            "Show me the access control list",
            "What are the current ACL entries?",
            "List all ACL permissions",
            "Get the ACL",
        ],
        "update_acl": [
            "Update the ACL for path {path}",
            "Grant {role} to {user} on {path}",
            "Set ACL permissions",
            "Change access control for {path}",
        ],
        "list_auth_domains": [
            "List authentication domains",
            "What auth realms are configured?",
            "Show me the authentication realms",
        ],
        "get_auth_domain": [
            "Get details for the {realm} auth domain",
            "Show me the {realm} realm configuration",
        ],
        "sync_auth_domain": [
            "Sync the {realm} authentication domain",
            "Synchronize users from {realm}",
        ],
        "get_permissions": [
            "What permissions does {user} have?",
            "Check permissions for {user}",
            "Show effective permissions",
        ],
        "list_tfa": [
            "List two-factor authentication entries",
            "Show me TFA configuration",
            "What 2FA methods are configured?",
        ],
        "list_groups": [
            "List all groups",
            "Show me the user groups",
            "What groups exist?",
        ],
        "get_group": [
            "Get details for group {group}",
            "Show me the {group} group",
            "Who is in the {group} group?",
        ],
        "create_group": [
            "Create a group called {group}",
            "Add a new group named {group}",
        ],
        "update_group": [
            "Update group {group}",
            "Modify the {group} group",
            "Change the members of group {group}",
        ],
        "delete_group": [
            "Delete the {group} group",
            "Remove group {group}",
        ],
    },

    # -- backup
    "backup": {
        "list_backup_jobs": [
            "List all backup jobs",
            "Show me scheduled backups",
            "What backup jobs are configured?",
        ],
        "get_backup_job": [
            "Get details for backup job {jobid}",
            "Show me backup job {jobid}",
        ],
        "create_backup_job": [
            "Create a backup job for VM {vmid}",
            "Schedule a backup for {vmid}",
            "Set up automatic backups",
        ],
        "update_backup_job": [
            "Update backup job {jobid}",
            "Change the schedule for backup job {jobid}",
        ],
        "delete_backup_job": [
            "Delete backup job {jobid}",
            "Remove the scheduled backup {jobid}",
        ],
        "create_vzdump": [
            "Take a backup of VM {vmid} now",
            "Run an immediate backup of {vmid}",
            "Backup VM {vmid} right now",
            "Do a vzdump of {vmid}",
        ],
        "get_vzdump_defaults": [
            "Show me the default backup settings",
            "What are the vzdump defaults?",
        ],
        "get_vzdump_extractconfig": [
            "Extract the config from backup file {volume}",
            "Get the configuration from a backup archive",
        ],
        "list_backup_file_restore": [
            "List files in backup {volume}",
            "What files are in this backup?",
        ],
        "list_file_restore": [
            "Browse the contents of backup {volume}",
            "List the directory tree in backup {volume}",
        ],
        "download_file_restore": [
            "Download a file from backup {volume}",
            "Restore a specific file from backup {volume}",
        ],
    },

    # -- cluster
    "cluster": {
        "get_cluster_status": [
            "Show the cluster status",
            "Is the cluster healthy?",
            "What's the current cluster state?",
            "Get cluster status",
        ],
        "get_cluster_resources": [
            "Show all resources in the cluster",
            "List cluster resources",
            "What VMs and containers exist across the cluster?",
            "Give me a cluster resource overview",
        ],
        "get_cluster_tasks": [
            "List recent cluster tasks",
            "Show me recent operations across the cluster",
            "What tasks ran recently?",
        ],
        "get_cluster_log": [
            "Show the cluster log",
            "Get recent cluster log entries",
            "What happened in the cluster recently?",
        ],
        "get_cluster_options": [
            "Show cluster options",
            "What are the cluster-wide settings?",
            "Get cluster configuration options",
        ],
        "update_cluster_options": [
            "Update cluster options",
            "Change cluster-wide settings",
            "Set the cluster keyboard layout",
        ],
        "get_cluster_config": [
            "Show the cluster configuration",
            "Get the corosync cluster config",
        ],
        "get_cluster_config_nodes": [
            "List the nodes in the cluster configuration",
            "Show cluster config nodes",
        ],
        "get_cluster_join_info": [
            "Get cluster join information",
            "How do I join a node to this cluster?",
            "Show me the cluster join token",
        ],
        "join_cluster": [
            "Join this node to the cluster",
            "Add a node to the cluster",
        ],
        "get_cluster_totem": [
            "Show the corosync totem configuration",
            "Get the totem settings",
        ],
        "get_version": [
            "What version of Proxmox is running?",
            "Show the Proxmox VE version",
            "Get the PVE version",
        ],
        "list_scheduled_jobs": [
            "List all scheduled jobs",
            "What cron jobs are scheduled?",
            "Show scheduled tasks",
        ],
        "list_realm_sync_jobs": [
            "List realm sync jobs",
            "Show authentication realm sync schedules",
        ],
        "list_notification_endpoints": [
            "List notification endpoints",
            "What notification targets are configured?",
        ],
        "list_notification_matchers": [
            "List notification matchers",
            "Show notification filter rules",
        ],
        "list_notification_targets": [
            "List notification targets",
            "Show notification destinations",
        ],
        "test_notification_target": [
            "Test notification target {target}",
            "Send a test notification to {target}",
        ],
        "get_metric_server": [
            "Get metrics server configuration",
            "Show the metrics server settings",
        ],
        "list_metric_servers": [
            "List configured metric servers",
            "What metric servers are set up?",
        ],
        "list_acme_accounts": [
            "List ACME accounts",
            "Show Let's Encrypt accounts",
        ],
        "get_acme_account": [
            "Get ACME account details",
            "Show the Let's Encrypt account info",
        ],
        "register_acme_account": [
            "Register a new ACME account",
            "Set up Let's Encrypt",
        ],
        "get_acme_directories": [
            "List ACME directories",
            "Show available ACME CAs",
        ],
        "get_acme_tos": [
            "Get the ACME terms of service",
            "Show Let's Encrypt ToS",
        ],
        "get_acme_plugin": [
            "Get ACME plugin details",
            "Show the DNS challenge plugin configuration",
        ],
        "list_acme_plugins": [
            "List ACME plugins",
            "What DNS plugins are available for ACME?",
        ],
        "list_replication_jobs": [
            "List replication jobs",
            "Show storage replication configuration",
        ],
        "get_replication_job": [
            "Get replication job {jobid}",
            "Show details of replication job {jobid}",
        ],
        "create_replication_job": [
            "Create a replication job",
            "Set up storage replication for VM {vmid}",
        ],
        "delete_replication_job": [
            "Delete replication job {jobid}",
            "Remove the replication job {jobid}",
        ],
        "get_node_certificates": [
            "Show the SSL certificates on node {node}",
            "Get TLS certificate info for {node}",
        ],
        "order_node_certificate": [
            "Order a new certificate for node {node}",
            "Renew the Let's Encrypt certificate on {node}",
        ],
        "list_dir_mappings": [
            "List directory mappings",
            "Show mapped directories",
        ],
        "list_pci_mappings": [
            "List PCI device mappings",
            "Show PCI passthrough mappings",
        ],
        "list_usb_mappings": [
            "List USB device mappings",
            "Show USB passthrough mappings",
        ],
        "get_teams": [
            "List teams",
            "Show the available teams",
        ],
        "get_team_members": [
            "Get members of team {team}",
            "Who is on team {team}?",
        ],
        "get_me": [
            "Who am I logged in as?",
            "Show my current user info",
            "What's my username?",
        ],
        "get_latest_release": [
            "What's the latest release?",
            "Check for updates",
            "Show the newest Proxmox version available",
        ],
        "get_tag": [
            "Get tag info",
            "Show details for tag {tag}",
        ],
        "list_tags": [
            "List all tags",
            "Show available tags",
        ],
        "list_releases": [
            "List releases",
            "Show release history",
        ],
        "get_release_by_tag": [
            "Get release info for tag {tag}",
            "Show the release tagged {tag}",
        ],
    },

    # -- firewall
    "firewall": {
        "get_cluster_firewall_options": [
            "Show the cluster firewall settings",
            "Is the cluster firewall enabled?",
            "Get cluster firewall options",
        ],
        "set_cluster_firewall_options": [
            "Enable the cluster firewall",
            "Update cluster firewall settings",
            "Turn on the cluster-level firewall",
        ],
        "list_cluster_firewall_rules": [
            "List cluster firewall rules",
            "Show all cluster-level firewall rules",
            "What firewall rules are set at the cluster level?",
        ],
        "get_cluster_firewall_rule": [
            "Get cluster firewall rule {pos}",
            "Show me cluster firewall rule number {pos}",
        ],
        "create_cluster_firewall_rule": [
            "Create a cluster firewall rule",
            "Add a new firewall rule to the cluster",
            "Block port {port} at the cluster level",
        ],
        "update_cluster_firewall_rule": [
            "Update cluster firewall rule {pos}",
            "Modify cluster firewall rule {pos}",
        ],
        "delete_cluster_firewall_rule": [
            "Delete cluster firewall rule {pos}",
            "Remove cluster firewall rule number {pos}",
        ],
        "list_firewall_aliases": [
            "List firewall aliases",
            "Show all IP aliases",
            "What firewall aliases are defined?",
        ],
        "create_firewall_alias": [
            "Create a firewall alias for {cidr}",
            "Add an IP alias named {name}",
        ],
        "delete_firewall_alias": [
            "Delete firewall alias {name}",
            "Remove the {name} IP alias",
        ],
        "list_firewall_ipsets": [
            "List firewall IP sets",
            "Show all IP sets",
            "What IP sets are configured?",
        ],
        "create_firewall_ipset": [
            "Create an IP set called {name}",
            "Add a new firewall IP set named {name}",
        ],
        "list_firewall_ipset_entries": [
            "List entries in IP set {name}",
            "Show the IPs in IP set {name}",
        ],
        "add_firewall_ipset_entry": [
            "Add {cidr} to IP set {name}",
            "Add an entry to the {name} IP set",
        ],
        "delete_firewall_ipset_entry": [
            "Remove {cidr} from IP set {name}",
            "Delete an entry from IP set {name}",
        ],
        "list_firewall_groups": [
            "List firewall security groups",
            "Show all firewall groups",
        ],
        "create_firewall_group": [
            "Create a firewall security group called {name}",
            "Add a new firewall group named {name}",
        ],
        "get_firewall_group_rules": [
            "List rules in firewall group {name}",
            "Show firewall group {name} rules",
        ],
        "create_firewall_group_rule": [
            "Add a rule to firewall group {name}",
            "Create a new rule in security group {name}",
        ],
        "get_firewall_refs": [
            "List firewall references",
            "Show available firewall object references",
        ],
        "list_firewall_macros": [
            "List firewall macros",
            "What firewall macros are available?",
            "Show predefined firewall application macros",
        ],
        "get_node_firewall_options": [
            "Show firewall settings for node {node}",
            "Get firewall options on {node}",
        ],
        "set_node_firewall_options": [
            "Update firewall settings on node {node}",
            "Enable the firewall on node {node}",
        ],
        "list_node_firewall_rules": [
            "List firewall rules on node {node}",
            "Show firewall rules for {node}",
        ],
        "get_node_firewall_log": [
            "Show the firewall log for node {node}",
            "Get firewall log entries on {node}",
        ],
        "get_vm_firewall_options": [
            "Get firewall options for VM {vmid}",
            "Show firewall settings on VM {vmid}",
        ],
        "set_vm_firewall_options": [
            "Enable the firewall on VM {vmid}",
            "Update VM {vmid} firewall settings",
        ],
        "list_vm_firewall_rules": [
            "List firewall rules for VM {vmid}",
            "Show firewall rules on VM {vmid}",
        ],
        "create_vm_firewall_rule": [
            "Add a firewall rule to VM {vmid}",
            "Create a firewall rule on VM {vmid}",
            "Allow SSH to VM {vmid}",
        ],
        "list_container_firewall_rules": [
            "List firewall rules for container {vmid}",
            "Show firewall rules on LXC {vmid}",
        ],
        "create_container_firewall_rule": [
            "Add a firewall rule to container {vmid}",
            "Create a firewall rule on container {vmid}",
        ],
        "get_container_firewall_options": [
            "Get firewall options for container {vmid}",
            "Show firewall settings on container {vmid}",
        ],
    },

    # -- ha (High Availability)
    "ha": {
        "get_ha_status": [
            "Show HA status",
            "Is high availability working?",
            "Get the HA cluster status",
        ],
        "get_ha_manager_status": [
            "Show the HA manager status",
            "What's the HA manager doing?",
        ],
        "list_ha_resources": [
            "List HA resources",
            "What resources are managed by HA?",
            "Show high availability managed VMs",
        ],
        "get_ha_resource": [
            "Get details for HA resource {sid}",
            "Show HA resource {sid}",
        ],
        "create_ha_resource": [
            "Add VM {vmid} to high availability",
            "Create an HA resource for {vmid}",
            "Make VM {vmid} highly available",
        ],
        "update_ha_resource": [
            "Update HA resource {sid}",
            "Change the HA settings for {sid}",
        ],
        "delete_ha_resource": [
            "Remove {sid} from HA management",
            "Delete HA resource {sid}",
        ],
        "migrate_ha_resource": [
            "Migrate HA resource {sid} to another node",
            "Move HA resource {sid}",
        ],
        "relocate_ha_resource": [
            "Relocate HA resource {sid}",
            "Request HA to move {sid} to {node}",
        ],
        "list_ha_groups": [
            "List HA groups",
            "Show high availability groups",
        ],
        "get_ha_group": [
            "Get HA group {group}",
            "Show details of HA group {group}",
        ],
        "create_ha_group": [
            "Create an HA group called {group}",
            "Add a new high availability group",
        ],
        "update_ha_group": [
            "Update HA group {group}",
            "Change nodes in HA group {group}",
        ],
        "delete_ha_group": [
            "Delete HA group {group}",
            "Remove HA group {group}",
        ],
    },

    # -- lxc (containers)
    "lxc": {
        "list_containers": [
            "List all containers",
            "Show me all LXC containers on node {node}",
            "What containers are running?",
        ],
        "get_container_status": [
            "Get the status of container {vmid}",
            "Is container {vmid} running?",
            "Show container {vmid} status",
        ],
        "get_container_config": [
            "Show the configuration of container {vmid}",
            "Get container {vmid} config",
            "What settings does container {vmid} have?",
        ],
        "create_container": [
            "Create a new container on {node}",
            "Deploy an LXC container",
            "Spin up a new container with template {template}",
        ],
        "update_container_config": [
            "Update config for container {vmid}",
            "Change container {vmid} settings",
            "Give container {vmid} more memory",
        ],
        "delete_container": [
            "Delete container {vmid}",
            "Remove container {vmid}",
            "Destroy LXC {vmid}",
        ],
        "start_container": [
            "Start container {vmid}",
            "Boot up container {vmid}",
            "Power on container {vmid}",
        ],
        "stop_container": [
            "Stop container {vmid}",
            "Kill container {vmid}",
            "Force stop container {vmid}",
        ],
        "shutdown_container": [
            "Shut down container {vmid} gracefully",
            "Shutdown container {vmid}",
        ],
        "reboot_container": [
            "Reboot container {vmid}",
            "Restart container {vmid}",
        ],
        "suspend_container": [
            "Suspend container {vmid}",
            "Pause container {vmid}",
            "Freeze container {vmid}",
        ],
        "resume_container": [
            "Resume container {vmid}",
            "Unpause container {vmid}",
            "Unfreeze container {vmid}",
        ],
        "clone_container": [
            "Clone container {vmid}",
            "Make a copy of container {vmid}",
            "Duplicate LXC {vmid}",
        ],
        "migrate_container": [
            "Migrate container {vmid} to node {node}",
            "Move container {vmid} to {node}",
        ],
        "convert_container_to_template": [
            "Convert container {vmid} to a template",
            "Make container {vmid} a template",
        ],
        "resize_container_disk": [
            "Resize the disk on container {vmid}",
            "Increase container {vmid} disk to {size}",
            "Expand container {vmid} storage",
        ],
        "move_container_volume": [
            "Move container {vmid} volume to different storage",
            "Relocate container {vmid} disk",
        ],
        "get_container_pending": [
            "Show pending changes for container {vmid}",
            "Are there uncommitted changes on container {vmid}?",
        ],
        "get_container_interfaces": [
            "Show network interfaces for container {vmid}",
            "Get the IP addresses of container {vmid}",
            "What IPs does container {vmid} have?",
        ],
        "get_container_rrddata": [
            "Get performance data for container {vmid}",
            "Show container {vmid} resource usage history",
        ],
        "get_container_feature": [
            "Check if container {vmid} supports feature {feature}",
            "Can container {vmid} do snapshots?",
        ],
        "list_container_snapshots": [
            "List snapshots of container {vmid}",
            "Show container {vmid} snapshots",
        ],
        "create_container_snapshot": [
            "Take a snapshot of container {vmid}",
            "Create a snapshot of container {vmid} called {snapname}",
        ],
        "delete_container_snapshot": [
            "Delete snapshot {snapname} from container {vmid}",
            "Remove container {vmid} snapshot {snapname}",
        ],
        "rollback_container_snapshot": [
            "Rollback container {vmid} to snapshot {snapname}",
            "Restore container {vmid} from snapshot {snapname}",
        ],
    },

    # -- nodes
    "nodes": {
        "list_nodes": [
            "List all nodes in the cluster",
            "Show me the Proxmox nodes",
            "What nodes do I have?",
            "How many nodes are in the cluster?",
        ],
        "get_node_status": [
            "Show the status of node {node}",
            "How is node {node} doing?",
            "Get CPU and memory usage on {node}",
            "Is node {node} healthy?",
        ],
        "get_node_config": [
            "Show node {node} configuration",
            "Get the config of node {node}",
        ],
        "get_node_dns": [
            "Show DNS settings on node {node}",
            "What DNS servers does {node} use?",
        ],
        "get_node_network": [
            "Show network configuration on node {node}",
            "List network interfaces on {node}",
            "What's the network setup on {node}?",
        ],
        "get_node_network_interface": [
            "Get details of interface {iface} on node {node}",
            "Show me the {iface} network interface on {node}",
        ],
        "create_node_network_interface": [
            "Create a network interface on node {node}",
            "Add a bridge interface on {node}",
            "Set up a new VLAN interface on {node}",
        ],
        "list_node_services": [
            "List services on node {node}",
            "Show all system services on {node}",
            "What services are running on {node}?",
        ],
        "manage_node_service": [
            "Restart the {service} service on {node}",
            "Stop {service} on node {node}",
            "Start the {service} service on {node}",
        ],
        "get_node_syslog": [
            "Show the syslog from node {node}",
            "Get system logs from {node}",
            "Check the logs on {node}",
        ],
        "get_node_journal": [
            "Show the systemd journal from node {node}",
            "Get journal entries from {node}",
        ],
        "list_node_tasks": [
            "List recent tasks on node {node}",
            "What operations ran on {node}?",
            "Show the task history for {node}",
        ],
        "get_task_status": [
            "Get the status of task {upid}",
            "Is task {upid} still running?",
            "Check the progress of task {upid}",
        ],
        "get_task_log": [
            "Show the log for task {upid}",
            "Get the output of task {upid}",
        ],
        "stop_task": [
            "Stop task {upid}",
            "Abort the running task {upid}",
            "Cancel task {upid}",
        ],
        "get_node_time": [
            "What time is it on node {node}?",
            "Show the timezone on node {node}",
        ],
        "get_node_subscription": [
            "Check the subscription status of node {node}",
            "Is node {node} licensed?",
            "Show subscription info for {node}",
        ],
        "get_node_apt_update": [
            "Check for package updates on node {node}",
            "Are there updates available on {node}?",
            "List available apt updates on {node}",
        ],
        "run_apt_update": [
            "Run apt update on node {node}",
            "Refresh the package index on {node}",
            "Update the apt cache on {node}",
        ],
        "get_node_report": [
            "Generate a system report for node {node}",
            "Get diagnostics for node {node}",
        ],
        "get_node_disks": [
            "List disks on node {node}",
            "Show physical drives on {node}",
            "What disks does {node} have?",
        ],
        "get_disk_smart": [
            "Get SMART data for disk {disk} on node {node}",
            "Check the health of disk {disk} on {node}",
            "Is disk {disk} on {node} healthy?",
        ],
        "get_node_hardware_pci": [
            "List PCI devices on node {node}",
            "Show PCI hardware on {node}",
            "What GPUs does {node} have?",
        ],
        "get_node_hardware_usb": [
            "List USB devices on node {node}",
            "Show USB hardware on {node}",
        ],
        "get_node_capabilities_qemu": [
            "What CPU models can {node} emulate?",
            "Show QEMU capabilities on {node}",
            "Get QEMU machine types for {node}",
        ],
        "get_node_storage_scan": [
            "Scan for storage on node {node}",
            "Discover NFS shares on {node}",
            "Scan for iSCSI targets from {node}",
        ],
        "wakeonlan_node": [
            "Wake up node {node}",
            "Send Wake-on-LAN to {node}",
            "Power on node {node} remotely",
        ],
        "startall_node": [
            "Start all VMs on node {node}",
            "Boot everything on {node}",
            "Start all guests on {node}",
        ],
        "stopall_node": [
            "Stop all VMs on node {node}",
            "Shut down everything on {node}",
            "Stop all guests on {node}",
        ],
        "get_node_hosts": [
            "Show the hosts file on node {node}",
            "Get /etc/hosts from {node}",
        ],
        "get_node_version": [
            "What Proxmox version is node {node} running?",
            "Get the PVE version on {node}",
        ],
        "get_node_netstat": [
            "Show network statistics on {node}",
            "Get netstat for {node}",
            "Show network traffic on {node}",
        ],
        "get_node_aplinfo": [
            "List available appliance templates",
            "What LXC templates can I download on {node}?",
            "Show available container templates",
        ],
        "download_appliance_template": [
            "Download the {template} template on node {node}",
            "Get the Ubuntu LXC template on {node}",
            "Download an appliance template",
        ],
    },

    # -- pools
    "pools": {
        "list_pools": [
            "List all resource pools",
            "Show me the pools",
            "What resource pools exist?",
        ],
        "get_pool": [
            "Get details for pool {pool}",
            "Show me the {pool} pool",
            "What resources are in pool {pool}?",
        ],
        "create_pool": [
            "Create a resource pool called {pool}",
            "Add a new pool named {pool}",
        ],
        "update_pool": [
            "Update pool {pool}",
            "Add VMs to pool {pool}",
            "Change pool {pool} settings",
        ],
        "delete_pool": [
            "Delete pool {pool}",
            "Remove the {pool} resource pool",
        ],
        "list_issues": [
            "List open issues",
            "Show me any problems or issues",
        ],
        "get_label": [
            "Get label {label}",
            "Show label details for {label}",
        ],
        "list_branches": [
            "List branches",
            "Show available branches",
        ],
        "list_commits": [
            "List recent commits",
            "Show the commit history",
        ],
        "get_commit": [
            "Get commit details",
            "Show me the latest commit info",
        ],
        "list_pull_requests": [
            "List pull requests",
            "Show open PRs",
        ],
        "search_code": [
            "Search for code matching {query}",
            "Find code containing {query}",
        ],
        "search_issues": [
            "Search for issues matching {query}",
            "Find issues about {query}",
        ],
    },

    # -- qemu (VMs)
    "qemu": {
        "list_vms": [
            "List all virtual machines",
            "Show me all VMs on node {node}",
            "What VMs are running?",
            "Give me a list of all VMs",
        ],
        "get_vm_status": [
            "Get the status of VM {vmid}",
            "Is VM {vmid} running?",
            "Show VM {vmid} status",
            "Check VM {vmid}",
        ],
        "get_vm_config": [
            "Show the configuration of VM {vmid}",
            "Get VM {vmid} config",
            "How much RAM does VM {vmid} have?",
            "What settings does VM {vmid} have?",
        ],
        "create_vm": [
            "Create a new virtual machine on {node}",
            "Deploy a new VM",
            "Spin up a VM with {cores} cores and {memory} MB RAM",
        ],
        "update_vm_config": [
            "Update VM {vmid} config",
            "Give VM {vmid} more CPU cores",
            "Change VM {vmid} memory to {memory} MB",
        ],
        "delete_vm": [
            "Delete VM {vmid}",
            "Remove VM {vmid}",
            "Destroy virtual machine {vmid}",
        ],
        "start_vm": [
            "Start VM {vmid}",
            "Boot up VM {vmid}",
            "Power on VM {vmid}",
            "Turn on virtual machine {vmid}",
        ],
        "stop_vm": [
            "Stop VM {vmid}",
            "Force stop VM {vmid}",
            "Kill VM {vmid}",
        ],
        "shutdown_vm": [
            "Shut down VM {vmid} gracefully",
            "Shutdown VM {vmid}",
            "Send ACPI shutdown to VM {vmid}",
        ],
        "reboot_vm": [
            "Reboot VM {vmid}",
            "Restart VM {vmid}",
        ],
        "reset_vm": [
            "Reset VM {vmid}",
            "Hard reset virtual machine {vmid}",
        ],
        "suspend_vm": [
            "Suspend VM {vmid}",
            "Pause VM {vmid}",
        ],
        "resume_vm": [
            "Resume VM {vmid}",
            "Unpause VM {vmid}",
        ],
        "clone_vm": [
            "Clone VM {vmid}",
            "Make a copy of VM {vmid}",
            "Duplicate VM {vmid}",
            "Create a clone of virtual machine {vmid}",
        ],
        "migrate_vm": [
            "Migrate VM {vmid} to node {node}",
            "Move VM {vmid} to {node}",
            "Live migrate VM {vmid}",
        ],
        "convert_vm_to_template": [
            "Convert VM {vmid} to a template",
            "Make VM {vmid} a template",
        ],
        "resize_vm_disk": [
            "Resize the disk on VM {vmid}",
            "Increase VM {vmid} disk to {size}",
            "Expand VM {vmid} storage",
        ],
        "move_vm_disk": [
            "Move VM {vmid} disk to different storage",
            "Relocate VM {vmid} disk to {storage}",
        ],
        "get_vm_pending": [
            "Show pending changes for VM {vmid}",
            "Are there uncommitted config changes on VM {vmid}?",
        ],
        "get_vm_rrddata": [
            "Get performance data for VM {vmid}",
            "Show VM {vmid} resource usage graph data",
            "Get the CPU/memory history for VM {vmid}",
        ],
        "get_vm_feature": [
            "Check if VM {vmid} supports {feature}",
            "Can VM {vmid} be cloned?",
        ],
        "get_vm_cloudinit": [
            "Show cloud-init config for VM {vmid}",
            "Get the cloud-init settings on VM {vmid}",
        ],
        "update_vm_cloudinit": [
            "Update cloud-init for VM {vmid}",
            "Set the cloud-init IP on VM {vmid}",
        ],
        "dump_vm_cloudinit": [
            "Dump the cloud-init data for VM {vmid}",
            "Generate the cloud-init config file for VM {vmid}",
        ],
        "get_vm_vncproxy": [
            "Get a VNC console for VM {vmid}",
            "Open VNC to VM {vmid}",
        ],
        "get_vm_spiceproxy": [
            "Get a SPICE console for VM {vmid}",
            "Connect SPICE to VM {vmid}",
        ],
        "send_vm_monitor_command": [
            "Send a monitor command to VM {vmid}",
            "Run a QMP command on VM {vmid}",
        ],
        "send_vm_key": [
            "Send a key press to VM {vmid}",
            "Type a key into VM {vmid}",
        ],
        "get_next_vmid": [
            "Get the next available VMID",
            "What VMID should I use for a new VM?",
            "What's the next free VM ID?",
        ],
        "list_vm_snapshots": [
            "List snapshots of VM {vmid}",
            "Show VM {vmid} snapshots",
        ],
        "create_vm_snapshot": [
            "Take a snapshot of VM {vmid}",
            "Create a snapshot of VM {vmid} called {snapname}",
            "Snapshot VM {vmid}",
        ],
        "get_vm_snapshot_config": [
            "Get the config of snapshot {snapname} on VM {vmid}",
            "Show snapshot {snapname} details for VM {vmid}",
        ],
        "delete_vm_snapshot": [
            "Delete snapshot {snapname} from VM {vmid}",
            "Remove VM {vmid} snapshot {snapname}",
        ],
        "rollback_vm_snapshot": [
            "Rollback VM {vmid} to snapshot {snapname}",
            "Restore VM {vmid} from snapshot {snapname}",
        ],
        "vm_agent_exec": [
            "Run a command in VM {vmid} via the guest agent",
            "Execute {cmd} inside VM {vmid}",
        ],
        "vm_agent_exec_status": [
            "Check the status of command {pid} in VM {vmid}",
            "Get the result of the command I ran in VM {vmid}",
        ],
        "vm_agent_file_read": [
            "Read a file from VM {vmid} via the guest agent",
            "Get the contents of {filepath} on VM {vmid}",
        ],
        "vm_agent_file_write": [
            "Write a file to VM {vmid} via the guest agent",
            "Create {filepath} inside VM {vmid}",
        ],
        "vm_agent_get_info": [
            "Get guest agent info for VM {vmid}",
            "What OS is VM {vmid} running?",
        ],
        "vm_agent_set_password": [
            "Set the password for a user in VM {vmid}",
            "Change the root password on VM {vmid} via the guest agent",
        ],
    },

    # -- sdn (Software-Defined Networking)
    "sdn": {
        "list_sdn_zones": [
            "List SDN zones",
            "Show all SDN zones",
            "What SDN zones are configured?",
        ],
        "get_sdn_zone": [
            "Get SDN zone {zone}",
            "Show details of SDN zone {zone}",
        ],
        "create_sdn_zone": [
            "Create an SDN zone called {zone}",
            "Add a new VXLAN zone",
        ],
        "delete_sdn_zone": [
            "Delete SDN zone {zone}",
            "Remove SDN zone {zone}",
        ],
        "list_sdn_vnets": [
            "List SDN VNets",
            "Show all virtual networks",
        ],
        "get_sdn_vnet": [
            "Get VNet {vnet}",
            "Show details of virtual network {vnet}",
        ],
        "create_sdn_vnet": [
            "Create a VNet called {vnet}",
            "Add a new virtual network",
        ],
        "update_sdn_vnet": [
            "Update VNet {vnet}",
            "Change the settings on VNet {vnet}",
        ],
        "delete_sdn_vnet": [
            "Delete VNet {vnet}",
            "Remove virtual network {vnet}",
        ],
        "list_sdn_subnets": [
            "List subnets in VNet {vnet}",
            "Show subnets for {vnet}",
        ],
        "create_sdn_subnet": [
            "Create a subnet in VNet {vnet}",
            "Add a subnet {cidr} to {vnet}",
        ],
        "list_sdn_controllers": [
            "List SDN controllers",
            "Show configured SDN controllers",
        ],
        "get_sdn_controller": [
            "Get SDN controller {controller}",
            "Show SDN controller details",
        ],
        "apply_sdn_changes": [
            "Apply SDN changes",
            "Commit the pending SDN configuration",
            "Deploy SDN changes to the cluster",
        ],
        "list_sdn_ipams": [
            "List SDN IPAM configurations",
            "Show IPAM settings",
        ],
        "get_sdn_ipam": [
            "Get IPAM details",
            "Show the SDN IP address management config",
        ],
        "list_sdn_dns": [
            "List SDN DNS configurations",
            "Show SDN DNS settings",
        ],
    },

    # -- storage
    "storage": {
        "list_storage": [
            "List all storage",
            "Show me the configured storage",
            "What storage is available?",
        ],
        "get_storage_config": [
            "Get the configuration of storage {storage}",
            "Show settings for {storage}",
        ],
        "create_storage": [
            "Add a new storage",
            "Create an NFS storage",
            "Add a Ceph storage pool",
        ],
        "update_storage": [
            "Update storage {storage}",
            "Change settings on {storage}",
        ],
        "delete_storage": [
            "Delete storage {storage}",
            "Remove storage {storage}",
        ],
        "list_node_storage": [
            "List storage on node {node}",
            "What storage does {node} have?",
            "Show storage available on {node}",
        ],
        "get_node_storage_status": [
            "Get status of {storage} on node {node}",
            "How much space is left on {storage}?",
            "Show storage usage for {storage} on {node}",
        ],
        "list_storage_content": [
            "List contents of {storage} on node {node}",
            "Show files on {storage}",
            "What ISOs are on {storage}?",
        ],
        "get_storage_volume_info": [
            "Get info about volume {volume}",
            "Show details of storage volume {volume}",
        ],
        "allocate_storage_volume": [
            "Allocate a volume on {storage}",
            "Create a new disk on {storage}",
        ],
        "delete_storage_volume": [
            "Delete volume {volume}",
            "Remove the storage volume {volume}",
        ],
        "upload_to_storage": [
            "Upload a file to {storage} on node {node}",
            "Upload an ISO to {storage}",
        ],
        "download_url_to_storage": [
            "Download a URL to {storage}",
            "Fetch {url} and save it to {storage}",
        ],
        "get_storage_rrddata": [
            "Get performance data for {storage}",
            "Show usage history for {storage}",
        ],
        "prune_storage_backups": [
            "Prune old backups on {storage}",
            "Clean up old backups from {storage}",
        ],
        "list_ceph_pools": [
            "List Ceph pools",
            "Show all Ceph storage pools",
        ],
        "create_ceph_pool": [
            "Create a Ceph pool called {pool}",
            "Add a new Ceph pool",
        ],
        "list_ceph_osds": [
            "List Ceph OSDs",
            "Show all Ceph storage daemons",
        ],
        "create_ceph_osd": [
            "Create a Ceph OSD on disk {disk}",
            "Add a new OSD",
        ],
        "list_ceph_monitors": [
            "List Ceph monitors",
            "Show Ceph MONs",
        ],
        "list_ceph_managers": [
            "List Ceph managers",
            "Show Ceph MGRs",
        ],
        "list_ceph_fs": [
            "List Ceph filesystems",
            "Show CephFS instances",
        ],
        "list_ceph_mds": [
            "List Ceph MDS",
            "Show Ceph metadata servers",
        ],
        "get_ceph_status_cluster": [
            "Get Ceph cluster status",
            "Is Ceph healthy?",
            "Show the Ceph cluster health",
        ],
        "get_ceph_status_node": [
            "Get Ceph status on node {node}",
            "Show Ceph status for {node}",
        ],
        "get_ceph_config": [
            "Show the Ceph configuration",
            "Get the Ceph config",
        ],
        "get_ceph_crush_rules": [
            "Show Ceph CRUSH rules",
            "Get the CRUSH map rules",
        ],
        "get_ceph_flags": [
            "Show Ceph flags",
            "What Ceph OSD flags are set?",
        ],
        "set_ceph_flags": [
            "Set Ceph flags",
            "Enable the noout flag on Ceph",
        ],
        "get_ceph_metadata": [
            "Get Ceph metadata",
            "Show Ceph cluster metadata",
        ],
        "list_lvm_volumes": [
            "List LVM volumes on node {node}",
            "Show LVM logical volumes",
        ],
        "list_lvmthin_pools": [
            "List LVM thin pools on {node}",
            "Show thin-provisioned LVM pools",
        ],
        "list_zfs_pools": [
            "List ZFS pools on node {node}",
            "Show ZFS datasets on {node}",
        ],
        "get_zfs_pool": [
            "Get details of ZFS pool {pool}",
            "Show ZFS pool {pool} info",
        ],
        "create_zfs_pool": [
            "Create a ZFS pool on node {node}",
            "Set up a new ZFS storage pool",
        ],
        "create_lvm": [
            "Create an LVM volume group on {node}",
            "Set up LVM on {node}",
        ],
        "create_lvmthin": [
            "Create an LVM thin pool on {node}",
            "Set up thin provisioning on {node}",
        ],
        "list_directory_storage": [
            "List directory-based storage on {node}",
            "Show directory storage on {node}",
        ],
        "create_directory_storage": [
            "Create a directory-based storage on {node}",
            "Add a local directory as storage on {node}",
        ],
        "initialize_gpt": [
            "Initialize a disk with GPT on {node}",
            "Wipe and GPT format disk {disk} on {node}",
        ],
    },
}

# Values for placeholder substitution
SAMPLE_VALUES = {
    "node": ["pve1", "pve2", "pve-node1", "proxmox1", "node1"],
    "vmid": ["100", "101", "102", "200", "201", "300", "1001"],
    "user": ["admin@pam", "root@pam", "deploy@pve", "mike@pam", "user1@pam"],
    "token": ["mcp-token", "automation", "api-key", "deploy-token"],
    "role": ["PVEAdmin", "PVEAuditor", "Operator", "ReadOnly", "VMAdmin"],
    "group": ["admins", "developers", "operators", "monitoring"],
    "path": ["/vms", "/storage", "/", "/pool/production"],
    "realm": ["pam", "pve", "ldap", "ad"],
    "storage": ["local", "local-lvm", "nfs-backup", "ceph-pool", "zfs-data"],
    "volume": ["local:backup/vzdump-qemu-100-2024_01_01.vma.zst", "local:iso/ubuntu.iso"],
    "disk": ["/dev/sda", "/dev/sdb", "/dev/nvme0n1"],
    "iface": ["vmbr0", "eth0", "ens18", "bond0"],
    "service": ["pvedaemon", "pveproxy", "ssh", "cron", "corosync"],
    "upid": ["UPID:pve1:00001234:AABBCCDD:12345678:vzdump:100:root@pam:"],
    "snapname": ["clean-state", "pre-upgrade", "backup", "snap1"],
    "template": ["local:vztmpl/ubuntu-22.04-standard.tar.zst", "debian-12-standard"],
    "feature": ["snapshot", "clone", "copy"],
    "pool": ["production", "development", "testing"],
    "cidr": ["10.0.0.0/24", "192.168.1.0/24", "172.16.0.0/16"],
    "name": ["trusted", "blocked", "internal", "web-servers"],
    "pos": ["0", "1", "2", "3"],
    "port": ["22", "80", "443", "8006"],
    "zone": ["myzone", "vxlan-zone", "evpn-zone"],
    "vnet": ["vnet1", "myvnet", "prod-net"],
    "controller": ["evpn1", "controller1"],
    "sid": ["vm:100", "vm:101", "ct:200"],
    "jobid": ["backup-abcd1234", "job1"],
    "target": ["mail-target", "smtp-alerts"],
    "tag": ["v1.0", "latest", "production"],
    "team": ["devops", "platform", "infra"],
    "label": ["bug", "feature", "critical"],
    "query": ["network config", "storage usage", "backup failure"],
    "cmd": ["ls -la", "hostname", "ip addr"],
    "filepath": ["/etc/hostname", "/var/log/syslog", "/root/.bashrc"],
    "pid": ["12345", "6789"],
    "size": ["50G", "100G", "200G"],
    "memory": ["2048", "4096", "8192"],
    "cores": ["2", "4", "8"],
    "url": ["https://releases.ubuntu.com/22.04/ubuntu.iso"],
}


def fill_template(template: str) -> str:
    """Replace {placeholder} tokens in a template with random sample values."""
    import re
    def replacer(match):
        key = match.group(1)
        if key in SAMPLE_VALUES:
            return random.choice(SAMPLE_VALUES[key])
        return match.group(0)
    return re.sub(r"\{(\w+)\}", replacer, template)


def build_function_schema(tool: dict) -> dict:
    """Build a JSON schema function definition from a tool dict."""
    properties = {}
    required = []
    for arg in tool["arguments"]:
        prop = {"type": arg["type"]}
        properties[arg["name"]] = prop
        # First arg is typically required
        if len(required) == 0:
            required.append(arg["name"])

    schema = {
        "type": "function",
        "function": {
            "name": tool["name"],
            "description": tool["description"],
            "parameters": {
                "type": "object",
                "properties": properties,
            },
        },
    }
    if required:
        schema["function"]["parameters"]["required"] = required
    return schema


def generate_training_examples(tools: list[dict], examples_per_tool: int = 4) -> list[dict]:
    """Generate training data in FunctionGemma chat format.
    
    Each example is a dict with:
      - messages: list of {role, content} dicts  
      - tools: list of function schemas (a random subset including the target tool)
      - expected_tool: the name of the correct tool
    """
    examples = []
    tool_by_name = {t["name"]: t for t in tools}
    tools_by_category = {}
    for t in tools:
        tools_by_category.setdefault(t["category"], []).append(t)

    for tool in tools:
        name = tool["name"]
        cat = tool["category"]

        # Get query templates for this tool
        templates = CATEGORY_TEMPLATES.get(cat, {}).get(name, [])
        if not templates:
            # Fallback: generate from tool description
            desc = tool["description"]
            templates = [
                desc,
                f"I need to {desc.lower().rstrip('.')}",
                f"Can you {desc.lower().rstrip('.')}?",
                f"Please {desc.lower().rstrip('.')}",
            ]

        # Generate examples_per_tool examples for this tool
        for i in range(examples_per_tool):
            template = templates[i % len(templates)]
            query = fill_template(template)

            # Build a context window of tools: the target + random others
            # Include all tools from the same category + a random sample from others
            same_cat_tools = tools_by_category[cat]
            other_tools = [t for t in tools if t["category"] != cat]
            # Sample 10-15 other tools from different categories
            n_other = min(random.randint(10, 15), len(other_tools))
            context_tools = same_cat_tools + random.sample(other_tools, n_other)
            # Deduplicate and shuffle
            seen = set()
            unique_tools = []
            for t in context_tools:
                if t["name"] not in seen:
                    seen.add(t["name"])
                    unique_tools.append(t)
            random.shuffle(unique_tools)

            tool_schemas = [build_function_schema(t) for t in unique_tools]

            example = {
                "messages": [
                    {
                        "role": "developer",
                        "content": "You are a model that can do function calling with the following functions",
                    },
                    {
                        "role": "user",
                        "content": query,
                    },
                ],
                "tools": tool_schemas,
                "expected_tool": name,
            }
            examples.append(example)

    random.shuffle(examples)
    return examples


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate FunctionGemma training data")
    parser.add_argument("--output", "-o", default="data/training_data.json",
                        help="Output path for training data (default: data/training_data.json)")
    parser.add_argument("--examples-per-tool", "-n", type=int, default=4,
                        help="Number of examples per tool (default: 4)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    parser.add_argument("--tools-dir", default=None,
                        help="Path to tools source directory (auto-detected if not set)")
    args = parser.parse_args()

    random.seed(args.seed)

    # Auto-detect tools directory
    if args.tools_dir:
        tools_dir = args.tools_dir
    else:
        script_dir = Path(__file__).resolve().parent
        tools_dir = script_dir.parent / "src" / "proxmox_mcp" / "tools"

    if not tools_dir.exists():
        print(f"Error: tools directory not found at {tools_dir}", file=sys.stderr)
        sys.exit(1)

    # Extract tools from source
    tools = []
    for filename in sorted(os.listdir(tools_dir)):
        if not filename.endswith(".py") or filename == "__init__.py":
            continue
        category = filename.replace(".py", "")
        filepath = os.path.join(tools_dir, filename)
        with open(filepath) as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    is_mcp_tool = False
                    if isinstance(dec, ast.Call):
                        if isinstance(dec.func, ast.Attribute) and dec.func.attr == "tool":
                            is_mcp_tool = True
                    elif isinstance(dec, ast.Attribute) and dec.attr == "tool":
                        is_mcp_tool = True

                    if is_mcp_tool:
                        name = node.name
                        desc = ast.get_docstring(node) or ""

                        arguments = []
                        for arg in node.args.args:
                            if arg.arg in ("ctx", "self"):
                                continue
                            arg_type = "string"
                            if arg.annotation and isinstance(arg.annotation, ast.Name):
                                t = arg.annotation.id.lower()
                                if t in ("int", "float"):
                                    arg_type = "number"
                                elif t == "bool":
                                    arg_type = "boolean"
                            arguments.append({"name": arg.arg, "type": arg_type})

                        tools.append({
                            "name": name,
                            "category": category,
                            "description": desc.split("\n")[0].strip(),
                            "arguments": arguments,
                        })
                        break

    print(f"Found {len(tools)} tools across {len(set(t['category'] for t in tools))} categories")

    # Generate training data
    examples = generate_training_examples(tools, args.examples_per_tool)
    print(f"Generated {len(examples)} training examples ({args.examples_per_tool} per tool)")

    # Split into train/val (90/10)
    split_idx = int(len(examples) * 0.9)
    train_examples = examples[:split_idx]
    val_examples = examples[split_idx:]

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write full dataset
    with open(output_path, "w") as f:
        json.dump(examples, f, indent=2)
    print(f"Wrote full dataset to {output_path}")

    # Write train split
    train_path = output_path.with_name("train.json")
    with open(train_path, "w") as f:
        json.dump(train_examples, f, indent=2)
    print(f"Wrote {len(train_examples)} training examples to {train_path}")

    # Write val split
    val_path = output_path.with_name("val.json")
    with open(val_path, "w") as f:
        json.dump(val_examples, f, indent=2)
    print(f"Wrote {len(val_examples)} validation examples to {val_path}")


if __name__ == "__main__":
    main()
