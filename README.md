# Proxmox MCP Server

A comprehensive [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for managing Proxmox VE infrastructure. Exposes **286 tools** covering the full Proxmox API surface — VMs, containers, storage, networking, firewall, HA, Ceph, backups, SDN, and more.

## Features

| Domain | Tools | Capabilities |
|--------|-------|-------------|
| **Nodes** | 34 | Status, config, networking, services, tasks, logs, disks, hardware, APT |
| **QEMU VMs** | 39 | Full lifecycle, snapshots, cloning, migration, cloud-init, QEMU agent, VNC/SPICE |
| **LXC Containers** | 25 | Full lifecycle, snapshots, cloning, migration, templates |
| **Storage** | 26 | Datacenter config, node storage, volumes, upload, LVM/ZFS/directory management |
| **Cluster** | 46 | Status, resources, config, Ceph, replication, metrics, notifications, bulk actions, jobs, mappings |
| **Access** | 27 | Users, groups, roles, ACL, API tokens, auth domains, TFA, permissions |
| **Backup** | 11 | Scheduled jobs, vzdump, file restore |
| **Firewall** | 32 | Cluster/node/VM/container rules, security groups, aliases, IP sets |
| **HA** | 14 | Resources, groups, status, migration, relocation |
| **SDN** | 17 | VNets, subnets, zones, controllers, IPAM, DNS |
| **Pools & ACME** | 14 | Resource pools, Let's Encrypt certificates |
| **Generic** | 1 | `proxmox_api_raw` — arbitrary API calls for anything not covered above |

## Quick Start

### 1. Create an API token in Proxmox

```
Datacenter → Permissions → API Tokens → Add
```

Uncheck "Privilege Separation" to inherit the user's full permissions, or assign specific roles via ACL.

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your Proxmox host/credentials
```

### 3. Run with Docker

```bash
docker compose build
docker compose up -d
```

### 4. Run without Docker

```bash
pip install .
proxmox-mcp-server
```

## Configuration

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PROXMOX_HOST` | **Yes** | — | Proxmox host IP or hostname |
| `PROXMOX_PORT` | No | `8006` | API port |
| `PROXMOX_USER` | No | `root@pam` | User for auth |
| `PROXMOX_TOKEN_NAME` | Auth* | — | API token name |
| `PROXMOX_TOKEN_VALUE` | Auth* | — | API token value |
| `PROXMOX_PASSWORD` | Auth* | — | Password (alternative to token) |
| `PROXMOX_VERIFY_SSL` | No | `0` | SSL verification (`1`/`true` to enable) |

*Either `PROXMOX_TOKEN_NAME` + `PROXMOX_TOKEN_VALUE` or `PROXMOX_PASSWORD` is required.

## MCP Client Integration

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "proxmox": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--env-file", "/path/to/.env", "proxmox-mcp-server"],
      "transportType": "stdio"
    }
  }
}
```

Or without Docker:

```json
{
  "mcpServers": {
    "proxmox": {
      "command": "proxmox-mcp-server",
      "env": {
        "PROXMOX_HOST": "192.168.1.100",
        "PROXMOX_TOKEN_NAME": "mcp",
        "PROXMOX_TOKEN_VALUE": "your-token-here"
      },
      "transportType": "stdio"
    }
  }
}
```

### VS Code (GitHub Copilot)

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "proxmox": {
      "command": "proxmox-mcp-server",
      "env": {
        "PROXMOX_HOST": "192.168.1.100",
        "PROXMOX_TOKEN_NAME": "mcp",
        "PROXMOX_TOKEN_VALUE": "your-token-here"
      }
    }
  }
}
```

## Architecture

```
src/proxmox_mcp/
├── server.py          # FastMCP server entry point
├── client.py          # Proxmox API client wrapper (proxmoxer)
└── tools/
    ├── access.py      # Users, groups, roles, ACL, tokens, auth domains
    ├── backup.py      # Vzdump, scheduled backup jobs, file restore
    ├── cluster.py     # Cluster status, config, Ceph, replication, notifications
    ├── firewall.py    # Rules, security groups, aliases, IP sets (cluster/node/VM/CT)
    ├── ha.py          # HA resources, groups, migration
    ├── lxc.py         # LXC container lifecycle and management
    ├── nodes.py       # Node status, services, tasks, disks, hardware
    ├── pools.py       # Resource pools, ACME/Let's Encrypt certificates
    ├── qemu.py        # QEMU VM lifecycle, snapshots, cloud-init, agent
    ├── sdn.py         # VNets, zones, controllers, IPAM
    └── storage.py     # Storage config, volumes, LVM/ZFS management
```

Each tool module exposes a `register(mcp)` function that registers domain-specific tools. The `proxmox_api_raw` escape-hatch tool in `server.py` handles any API endpoint not covered by specific tools.

## License

MIT
