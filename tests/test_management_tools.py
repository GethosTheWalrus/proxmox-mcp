"""Tests for cluster, access, storage, and other management tools."""

import json

from proxmox_mcp.client import api_request, format_response


class TestClusterTools:
    def test_get_cluster_status(self, mock_proxmox_client):
        mock_proxmox_client.cluster.status.get.return_value = [
            {"type": "cluster", "name": "pve-cluster", "quorate": 1},
            {"type": "node", "name": "pve1", "online": 1},
        ]
        result = api_request("get", "/cluster/status")
        assert len(result) == 2
        assert result[0]["quorate"] == 1

    def test_get_cluster_resources(self, mock_proxmox_client):
        mock_proxmox_client.cluster.resources.get.return_value = [
            {"type": "qemu", "vmid": 100, "name": "web", "status": "running"},
        ]
        api_request("get", "/cluster/resources", type="vm")
        mock_proxmox_client.cluster.resources.get.assert_called_once_with(type="vm")

    def test_get_next_vmid(self, mock_proxmox_client):
        mock_proxmox_client.cluster.nextid.get.return_value = "103"
        result = api_request("get", "/cluster/nextid")
        assert result == "103"

    def test_get_version(self, mock_proxmox_client):
        mock_proxmox_client.version.get.return_value = {
            "version": "8.2.4",
            "release": "1",
        }
        result = api_request("get", "/version")
        assert result["version"] == "8.2.4"

    def test_update_replication_job(self, mock_proxmox_client):
        mock_proxmox_client.cluster.replication.__getattr__("100-0").put.return_value = None
        result = api_request("put", "/cluster/replication/100-0", schedule="daily", rate=50.0, disable=1)
        mock_proxmox_client.cluster.replication.__getattr__("100-0").put.assert_called_once_with(schedule="daily", rate=50.0, disable=1)

    def test_get_replication_log(self, mock_proxmox_client):
        mock_proxmox_client.cluster.replication.__getattr__("100-0").log.get.return_value = [
            {"t": "log line 1", "n": 1},
        ]
        result = api_request("get", "/cluster/replication/100-0/log", limit=50)
        assert len(result) == 1
        mock_proxmox_client.cluster.replication.__getattr__("100-0").log.get.assert_called_once_with(limit=50)

    def test_get_replication_status(self, mock_proxmox_client):
        mock_proxmox_client.cluster.replication.__getattr__("100-0").status.get.return_value = {
            "last_sync": 1700000000,
            "fail_count": 0,
        }
        result = api_request("get", "/cluster/replication/100-0/status")
        assert result["fail_count"] == 0


class TestAccessTools:
    def test_list_users(self, mock_proxmox_client):
        mock_proxmox_client.access.users.get.return_value = [
            {"userid": "root@pam", "enable": 1},
            {"userid": "admin@pve", "enable": 1},
        ]
        result = api_request("get", "/access/users", full=1)
        assert len(result) == 2

    def test_get_acl(self, mock_proxmox_client):
        mock_proxmox_client.access.acl.get.return_value = [
            {"path": "/", "roleid": "Administrator", "ugid": "root@pam", "type": "user"},
        ]
        result = api_request("get", "/access/acl")
        assert result[0]["roleid"] == "Administrator"

    def test_list_roles(self, mock_proxmox_client):
        mock_proxmox_client.access.roles.get.return_value = [
            {"roleid": "Administrator", "privs": "Datastore.Allocate,..."},
            {"roleid": "PVEVMAdmin", "privs": "VM.Allocate,..."},
        ]
        result = api_request("get", "/access/roles")
        assert len(result) == 2


class TestStorageTools:
    def test_list_storage(self, mock_proxmox_client):
        mock_proxmox_client.storage.get.return_value = [
            {"storage": "local", "type": "dir", "content": "images,rootdir,iso"},
            {"storage": "ceph-pool", "type": "rbd", "content": "images"},
        ]
        result = api_request("get", "/storage")
        assert len(result) == 2
        assert result[0]["storage"] == "local"

    def test_list_node_storage(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.storage.get.return_value = [
            {"storage": "local", "avail": 100 * 1024**3, "used": 20 * 1024**3},
        ]
        result = api_request("get", "/nodes/pve1/storage")
        assert result[0]["storage"] == "local"

    def test_destroy_zfs_pool(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.disks.zfs.__getattr__("tank").delete.return_value = "UPID:pve1:..."
        result = api_request("delete", "/nodes/pve1/disks/zfs/tank")
        assert result is not None

    def test_zfs_scrub(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.disks.zfs.__getattr__("tank").post.return_value = "UPID:pve1:..."
        result = api_request("post", "/nodes/pve1/disks/zfs/tank", action="scrub")
        assert result is not None
        mock_proxmox_client.nodes.pve1.disks.zfs.__getattr__("tank").post.assert_called_once_with(action="scrub")

    def test_delete_lvm(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.disks.lvm.__getattr__("vg0").delete.return_value = "UPID:pve1:..."
        result = api_request("delete", "/nodes/pve1/disks/lvm/vg0")
        assert result is not None

    def test_delete_lvmthin(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.disks.lvmthin.__getattr__("thinpool").delete.return_value = "UPID:pve1:..."
        result = api_request("delete", "/nodes/pve1/disks/lvmthin/thinpool", volume_group="vg0")
        assert result is not None
        mock_proxmox_client.nodes.pve1.disks.lvmthin.__getattr__("thinpool").delete.assert_called_once_with(volume_group="vg0")

    def test_delete_directory_storage(self, mock_proxmox_client):
        mock_proxmox_client.nodes.pve1.disks.directory.__getattr__("data").delete.return_value = "UPID:pve1:..."
        result = api_request("delete", "/nodes/pve1/disks/directory/data")
        assert result is not None


class TestFirewallTools:
    def test_list_cluster_firewall_rules(self, mock_proxmox_client):
        mock_proxmox_client.cluster.firewall.rules.get.return_value = [
            {"pos": 0, "type": "in", "action": "ACCEPT", "macro": "SSH"},
        ]
        result = api_request("get", "/cluster/firewall/rules")
        assert result[0]["macro"] == "SSH"

    def test_get_firewall_options(self, mock_proxmox_client):
        mock_proxmox_client.cluster.firewall.options.get.return_value = {
            "enable": 1,
            "policy_in": "DROP",
            "policy_out": "ACCEPT",
        }
        result = api_request("get", "/cluster/firewall/options")
        assert result["enable"] == 1


class TestHATools:
    def test_list_ha_resources(self, mock_proxmox_client):
        mock_proxmox_client.cluster.ha.resources.get.return_value = [
            {"sid": "vm:100", "state": "started", "group": "prefer-pve1"},
        ]
        result = api_request("get", "/cluster/ha/resources")
        assert result[0]["sid"] == "vm:100"

    def test_list_ha_groups(self, mock_proxmox_client):
        mock_proxmox_client.cluster.ha.groups.get.return_value = [
            {"group": "prefer-pve1", "nodes": "pve1:2,pve2:1"},
        ]
        result = api_request("get", "/cluster/ha/groups")
        assert result[0]["group"] == "prefer-pve1"


class TestPoolTools:
    def test_list_pools(self, mock_proxmox_client):
        mock_proxmox_client.pools.get.return_value = [
            {"poolid": "production", "comment": "Production VMs"},
        ]
        result = api_request("get", "/pools")
        assert result[0]["poolid"] == "production"


class TestGenericRawTool:
    def test_proxmox_api_raw(self, mock_proxmox_client):
        """The escape-hatch tool should parse JSON params and call api_request."""
        mock_proxmox_client.cluster.resources.get.return_value = [{"vmid": 100}]
        result = api_request("get", "/cluster/resources", type="vm")
        parsed = json.loads(format_response(result))
        assert parsed[0]["vmid"] == 100
