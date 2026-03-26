"""Firewall management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register firewall management tools."""

    # ── Cluster Firewall ──────────────────────────────────────────────

    @mcp.tool()
    def get_cluster_firewall_options() -> str:
        """Get cluster-wide firewall options (enable, policy_in, policy_out, etc.)."""
        return format_response(api_request("get", "/cluster/firewall/options"))

    @mcp.tool()
    def set_cluster_firewall_options(
        enable: int = -1,
        policy_in: str = "",
        policy_out: str = "",
        log_ratelimit: str = "",
        ebtables: int = -1,
        delete: str = "",
    ) -> str:
        """Set cluster-wide firewall options.

        Args:
            enable: 1 to enable, 0 to disable, -1 to not change.
            policy_in: Default input policy: 'ACCEPT', 'REJECT', 'DROP'.
            policy_out: Default output policy: 'ACCEPT', 'REJECT', 'DROP'.
            log_ratelimit: Log rate limit (e.g. 'enable=1,rate=1/second,burst=5').
            ebtables: 1 to enable ebtables rules, 0 to disable, -1 to not change.
            delete: Comma-separated options to delete.
        """
        params: dict = {}
        if enable >= 0:
            params["enable"] = enable
        if policy_in:
            params["policy_in"] = policy_in
        if policy_out:
            params["policy_out"] = policy_out
        if log_ratelimit:
            params["log_ratelimit"] = log_ratelimit
        if ebtables >= 0:
            params["ebtables"] = ebtables
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", "/cluster/firewall/options", **params))

    @mcp.tool()
    def list_cluster_firewall_rules() -> str:
        """List cluster-level firewall rules."""
        return format_response(api_request("get", "/cluster/firewall/rules"))

    @mcp.tool()
    def get_cluster_firewall_rule(pos: int) -> str:
        """Get a specific cluster firewall rule.

        Args:
            pos: Rule position number.
        """
        return format_response(api_request("get", f"/cluster/firewall/rules/{pos}"))

    @mcp.tool()
    def create_cluster_firewall_rule(
        action: str,
        type: str,
        enable: int = 1,
        source: str = "",
        dest: str = "",
        proto: str = "",
        sport: str = "",
        dport: str = "",
        iface: str = "",
        macro: str = "",
        comment: str = "",
        log: str = "",
        pos: int = -1,
    ) -> str:
        """Create a cluster-level firewall rule.

        Args:
            action: 'ACCEPT', 'DROP', 'REJECT'.
            type: 'in', 'out', 'group'.
            enable: 1 = enabled, 0 = disabled.
            source: Source address/range (CIDR or alias).
            dest: Destination address/range.
            proto: Protocol (tcp, udp, icmp, etc.).
            sport: Source port(s).
            dport: Destination port(s).
            iface: Network interface.
            macro: Use predefined macro (e.g. 'SSH', 'HTTP', 'HTTPS', 'Ping').
            comment: Description.
            log: Log level: 'emerg', 'alert', 'crit', 'err', 'warning', 'notice', 'info', 'debug', 'nolog'.
            pos: Rule position (-1 = append).
        """
        params: dict = {"action": action, "type": type, "enable": enable}
        for key, val in [("source", source), ("dest", dest), ("proto", proto), ("sport", sport),
                         ("dport", dport), ("iface", iface), ("macro", macro), ("comment", comment), ("log", log)]:
            if val:
                params[key] = val
        if pos >= 0:
            params["pos"] = pos
        return format_response(api_request("post", "/cluster/firewall/rules", **params))

    @mcp.tool()
    def update_cluster_firewall_rule(
        pos: int,
        action: str = "",
        enable: int = -1,
        source: str = "",
        dest: str = "",
        proto: str = "",
        sport: str = "",
        dport: str = "",
        macro: str = "",
        comment: str = "",
        moveto: int = -1,
        delete: str = "",
    ) -> str:
        """Update a cluster-level firewall rule.

        Args:
            pos: Rule position to update.
            action: 'ACCEPT', 'DROP', 'REJECT'.
            enable: 1 = enabled, 0 = disabled, -1 = don't change.
            source: Source address/range.
            dest: Destination address/range.
            proto: Protocol.
            sport: Source port(s).
            dport: Destination port(s).
            macro: Predefined macro.
            comment: Description.
            moveto: Move rule to this position.
            delete: Comma-separated properties to delete.
        """
        params: dict = {}
        if action:
            params["action"] = action
        if enable >= 0:
            params["enable"] = enable
        for key, val in [("source", source), ("dest", dest), ("proto", proto), ("sport", sport),
                         ("dport", dport), ("macro", macro), ("comment", comment), ("delete", delete)]:
            if val:
                params[key] = val
        if moveto >= 0:
            params["moveto"] = moveto
        return format_response(api_request("put", f"/cluster/firewall/rules/{pos}", **params))

    @mcp.tool()
    def delete_cluster_firewall_rule(pos: int) -> str:
        """Delete a cluster-level firewall rule.

        Args:
            pos: Rule position to delete.
        """
        return format_response(api_request("delete", f"/cluster/firewall/rules/{pos}"))

    # ── Cluster Firewall Groups (Security Groups) ─────────────────────

    @mcp.tool()
    def list_firewall_groups() -> str:
        """List firewall security groups (reusable sets of rules)."""
        return format_response(api_request("get", "/cluster/firewall/groups"))

    @mcp.tool()
    def get_firewall_group_rules(group: str) -> str:
        """List rules in a firewall security group.

        Args:
            group: Security group name.
        """
        return format_response(api_request("get", f"/cluster/firewall/groups/{group}"))

    @mcp.tool()
    def create_firewall_group(group: str, comment: str = "") -> str:
        """Create a new firewall security group.

        Args:
            group: Group name.
            comment: Description.
        """
        params: dict = {"group": group}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/firewall/groups", **params))

    @mcp.tool()
    def create_firewall_group_rule(
        group: str,
        action: str,
        type: str,
        enable: int = 1,
        source: str = "",
        dest: str = "",
        proto: str = "",
        sport: str = "",
        dport: str = "",
        macro: str = "",
        comment: str = "",
    ) -> str:
        """Add a rule to a firewall security group.

        Args:
            group: Security group name.
            action: 'ACCEPT', 'DROP', 'REJECT'.
            type: 'in', 'out'.
            enable: 1 = enabled, 0 = disabled.
            source: Source address/range.
            dest: Destination address/range.
            proto: Protocol.
            sport: Source port(s).
            dport: Destination port(s).
            macro: Predefined macro.
            comment: Description.
        """
        params: dict = {"action": action, "type": type, "enable": enable}
        for key, val in [("source", source), ("dest", dest), ("proto", proto), ("sport", sport),
                         ("dport", dport), ("macro", macro), ("comment", comment)]:
            if val:
                params[key] = val
        return format_response(api_request("post", f"/cluster/firewall/groups/{group}", **params))

    # ── Cluster Firewall Aliases & IPSets ─────────────────────────────

    @mcp.tool()
    def list_firewall_aliases() -> str:
        """List cluster firewall aliases (named IP addresses/ranges)."""
        return format_response(api_request("get", "/cluster/firewall/aliases"))

    @mcp.tool()
    def create_firewall_alias(name: str, cidr: str, comment: str = "") -> str:
        """Create a firewall alias (named IP address or CIDR).

        Args:
            name: Alias name.
            cidr: IP address or CIDR (e.g. '10.0.0.0/24' or '192.168.1.1').
            comment: Description.
        """
        params: dict = {"name": name, "cidr": cidr}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/firewall/aliases", **params))

    @mcp.tool()
    def delete_firewall_alias(name: str) -> str:
        """Delete a firewall alias.

        Args:
            name: Alias name.
        """
        return format_response(api_request("delete", f"/cluster/firewall/aliases/{name}"))

    @mcp.tool()
    def list_firewall_ipsets() -> str:
        """List cluster firewall IP sets (named groups of IPs)."""
        return format_response(api_request("get", "/cluster/firewall/ipset"))

    @mcp.tool()
    def create_firewall_ipset(name: str, comment: str = "") -> str:
        """Create a new firewall IP set.

        Args:
            name: IP set name.
            comment: Description.
        """
        params: dict = {"name": name}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/cluster/firewall/ipset", **params))

    @mcp.tool()
    def list_firewall_ipset_entries(name: str) -> str:
        """List entries in a firewall IP set.

        Args:
            name: IP set name.
        """
        return format_response(api_request("get", f"/cluster/firewall/ipset/{name}"))

    @mcp.tool()
    def add_firewall_ipset_entry(name: str, cidr: str, comment: str = "", nomatch: bool = False) -> str:
        """Add an IP/CIDR to an IP set.

        Args:
            name: IP set name.
            cidr: IP address or CIDR.
            comment: Description.
            nomatch: Exclude this entry (nomatch).
        """
        params: dict = {"cidr": cidr}
        if comment:
            params["comment"] = comment
        if nomatch:
            params["nomatch"] = 1
        return format_response(api_request("post", f"/cluster/firewall/ipset/{name}", **params))

    @mcp.tool()
    def delete_firewall_ipset_entry(name: str, cidr: str) -> str:
        """Remove an IP/CIDR from an IP set.

        Args:
            name: IP set name.
            cidr: IP address or CIDR to remove.
        """
        return format_response(api_request("delete", f"/cluster/firewall/ipset/{name}/{cidr}"))

    @mcp.tool()
    def list_firewall_macros() -> str:
        """List available firewall macros (predefined rule sets like SSH, HTTP, etc.)."""
        return format_response(api_request("get", "/cluster/firewall/macros"))

    @mcp.tool()
    def get_firewall_refs() -> str:
        """Get available firewall references (aliases, ipsets, names usable in rules)."""
        return format_response(api_request("get", "/cluster/firewall/refs"))

    # ── Node Firewall ─────────────────────────────────────────────────

    @mcp.tool()
    def get_node_firewall_options(node: str) -> str:
        """Get firewall options for a specific node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/firewall/options"))

    @mcp.tool()
    def set_node_firewall_options(node: str, enable: int = -1, log_level_in: str = "", log_level_out: str = "", ndp: int = -1, nf_conntrack_max: int = 0, delete: str = "") -> str:
        """Set firewall options for a node.

        Args:
            node: The node name.
            enable: 1 = enable, 0 = disable, -1 = don't change.
            log_level_in: Input log level.
            log_level_out: Output log level.
            ndp: 1 = enable NDP, 0 = disable, -1 = don't change.
            nf_conntrack_max: Max conntrack entries (0 = don't change).
            delete: Comma-separated options to delete.
        """
        params: dict = {}
        if enable >= 0:
            params["enable"] = enable
        if log_level_in:
            params["log_level_in"] = log_level_in
        if log_level_out:
            params["log_level_out"] = log_level_out
        if ndp >= 0:
            params["ndp"] = ndp
        if nf_conntrack_max:
            params["nf_conntrack_max"] = nf_conntrack_max
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/nodes/{node}/firewall/options", **params))

    @mcp.tool()
    def list_node_firewall_rules(node: str) -> str:
        """List firewall rules for a node.

        Args:
            node: The node name.
        """
        return format_response(api_request("get", f"/nodes/{node}/firewall/rules"))

    @mcp.tool()
    def get_node_firewall_log(node: str, limit: int = 50) -> str:
        """Get firewall log for a node.

        Args:
            node: The node name.
            limit: Max entries.
        """
        return format_response(api_request("get", f"/nodes/{node}/firewall/log", limit=limit))

    # ── VM/Container Firewall ─────────────────────────────────────────

    @mcp.tool()
    def get_vm_firewall_options(node: str, vmid: int) -> str:
        """Get firewall options for a QEMU VM.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/firewall/options"))

    @mcp.tool()
    def set_vm_firewall_options(node: str, vmid: int, enable: int = -1, dhcp: int = -1, ipfilter: int = -1, macfilter: int = -1, policy_in: str = "", policy_out: str = "", delete: str = "") -> str:
        """Set firewall options for a QEMU VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            enable: 1 = enable, 0 = disable.
            dhcp: 1 = enable DHCP.
            ipfilter: 1 = enable IP filter.
            macfilter: 1 = enable MAC filter.
            policy_in: Input policy.
            policy_out: Output policy.
            delete: Comma-separated options to delete.
        """
        params: dict = {}
        if enable >= 0:
            params["enable"] = enable
        if dhcp >= 0:
            params["dhcp"] = dhcp
        if ipfilter >= 0:
            params["ipfilter"] = ipfilter
        if macfilter >= 0:
            params["macfilter"] = macfilter
        if policy_in:
            params["policy_in"] = policy_in
        if policy_out:
            params["policy_out"] = policy_out
        if delete:
            params["delete"] = delete
        return format_response(api_request("put", f"/nodes/{node}/qemu/{vmid}/firewall/options", **params))

    @mcp.tool()
    def list_vm_firewall_rules(node: str, vmid: int) -> str:
        """List firewall rules for a QEMU VM.

        Args:
            node: The node name.
            vmid: The VM ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/qemu/{vmid}/firewall/rules"))

    @mcp.tool()
    def create_vm_firewall_rule(
        node: str, vmid: int, action: str, type: str, enable: int = 1,
        source: str = "", dest: str = "", proto: str = "",
        dport: str = "", macro: str = "", comment: str = "",
    ) -> str:
        """Create a firewall rule for a QEMU VM.

        Args:
            node: The node name.
            vmid: The VM ID.
            action: 'ACCEPT', 'DROP', 'REJECT'.
            type: 'in', 'out', 'group'.
            enable: 1 = enabled, 0 = disabled.
            source: Source CIDR or alias.
            dest: Destination CIDR or alias.
            proto: Protocol.
            dport: Destination port(s).
            macro: Predefined macro.
            comment: Description.
        """
        params: dict = {"action": action, "type": type, "enable": enable}
        for key, val in [("source", source), ("dest", dest), ("proto", proto),
                         ("dport", dport), ("macro", macro), ("comment", comment)]:
            if val:
                params[key] = val
        return format_response(api_request("post", f"/nodes/{node}/qemu/{vmid}/firewall/rules", **params))

    @mcp.tool()
    def get_container_firewall_options(node: str, vmid: int) -> str:
        """Get firewall options for an LXC container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/firewall/options"))

    @mcp.tool()
    def list_container_firewall_rules(node: str, vmid: int) -> str:
        """List firewall rules for an LXC container.

        Args:
            node: The node name.
            vmid: The container ID.
        """
        return format_response(api_request("get", f"/nodes/{node}/lxc/{vmid}/firewall/rules"))

    @mcp.tool()
    def create_container_firewall_rule(
        node: str, vmid: int, action: str, type: str, enable: int = 1,
        source: str = "", dest: str = "", proto: str = "",
        dport: str = "", macro: str = "", comment: str = "",
    ) -> str:
        """Create a firewall rule for an LXC container.

        Args:
            node: The node name.
            vmid: The container ID.
            action: 'ACCEPT', 'DROP', 'REJECT'.
            type: 'in', 'out', 'group'.
            enable: 1 = enabled, 0 = disabled.
            source: Source CIDR or alias.
            dest: Destination CIDR or alias.
            proto: Protocol.
            dport: Destination port(s).
            macro: Predefined macro.
            comment: Description.
        """
        params: dict = {"action": action, "type": type, "enable": enable}
        for key, val in [("source", source), ("dest", dest), ("proto", proto),
                         ("dport", dport), ("macro", macro), ("comment", comment)]:
            if val:
                params[key] = val
        return format_response(api_request("post", f"/nodes/{node}/lxc/{vmid}/firewall/rules", **params))
