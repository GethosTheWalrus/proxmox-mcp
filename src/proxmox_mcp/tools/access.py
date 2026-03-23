"""Access management tools for Proxmox MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from proxmox_mcp.client import api_request, format_response


def register(mcp: FastMCP) -> None:
    """Register access/authentication management tools."""

    # ── Users ─────────────────────────────────────────────────────────

    @mcp.tool()
    def list_users(enabled: bool = False, full: bool = True) -> str:
        """List all users in Proxmox.

        Args:
            enabled: Only show enabled users.
            full: Include detailed info (groups, tokens, etc.).
        """
        params: dict = {"full": int(full)}
        if enabled:
            params["enabled"] = 1
        return format_response(api_request("get", "/access/users", **params))

    @mcp.tool()
    def get_user(userid: str) -> str:
        """Get details for a specific user.

        Args:
            userid: User ID (format: 'user@realm', e.g. 'admin@pam').
        """
        return format_response(api_request("get", f"/access/users/{userid}"))

    @mcp.tool()
    def create_user(
        userid: str,
        password: str = "",
        email: str = "",
        firstname: str = "",
        lastname: str = "",
        groups: str = "",
        comment: str = "",
        enable: bool = True,
        expire: int = 0,
    ) -> str:
        """Create a new user.

        Args:
            userid: User ID (format: 'user@realm', e.g. 'myuser@pve').
            password: Password (only for pve/pam realms).
            email: Email address.
            firstname: First name.
            lastname: Last name.
            groups: Comma-separated group list.
            comment: Description.
            enable: Enable user.
            expire: Account expiration (Unix epoch, 0 = never).
        """
        params: dict = {"userid": userid}
        if password:
            params["password"] = password
        for key, val in [("email", email), ("firstname", firstname), ("lastname", lastname),
                         ("groups", groups), ("comment", comment)]:
            if val:
                params[key] = val
        if not enable:
            params["enable"] = 0
        if expire:
            params["expire"] = expire
        return format_response(api_request("post", "/access/users", **params))

    @mcp.tool()
    def update_user(
        userid: str,
        email: str = "",
        firstname: str = "",
        lastname: str = "",
        groups: str = "",
        comment: str = "",
        enable: bool = True,
        expire: int = -1,
        append: bool = False,
    ) -> str:
        """Update an existing user.

        Args:
            userid: User ID (format: 'user@realm').
            email: Email address.
            firstname: First name.
            lastname: Last name.
            groups: Comma-separated group list.
            comment: Description.
            enable: Enable/disable user.
            expire: Account expiration (Unix epoch, 0 = never, -1 = don't change).
            append: Append groups instead of replacing.
        """
        params: dict = {}
        for key, val in [("email", email), ("firstname", firstname), ("lastname", lastname),
                         ("groups", groups), ("comment", comment)]:
            if val:
                params[key] = val
        if not enable:
            params["enable"] = 0
        if expire >= 0:
            params["expire"] = expire
        if append:
            params["append"] = 1
        return format_response(api_request("put", f"/access/users/{userid}", **params))

    @mcp.tool()
    def delete_user(userid: str) -> str:
        """Delete a user.

        Args:
            userid: User ID to delete (format: 'user@realm').
        """
        return format_response(api_request("delete", f"/access/users/{userid}"))

    # ── API Tokens ────────────────────────────────────────────────────

    @mcp.tool()
    def list_user_tokens(userid: str) -> str:
        """List API tokens for a user.

        Args:
            userid: User ID (format: 'user@realm').
        """
        return format_response(api_request("get", f"/access/users/{userid}/token"))

    @mcp.tool()
    def get_user_token(userid: str, tokenid: str) -> str:
        """Get details for a specific API token.

        Args:
            userid: User ID (format: 'user@realm').
            tokenid: Token ID.
        """
        return format_response(api_request("get", f"/access/users/{userid}/token/{tokenid}"))

    @mcp.tool()
    def create_user_token(userid: str, tokenid: str, comment: str = "", privsep: bool = True, expire: int = 0) -> str:
        """Create a new API token for a user. Returns the token value (shown only once).

        Args:
            userid: User ID (format: 'user@realm').
            tokenid: Token ID (alphanumeric).
            comment: Token description.
            privsep: Enable privilege separation (token has own permissions, not user's full permissions).
            expire: Expiration (Unix epoch, 0 = never).
        """
        params: dict = {}
        if comment:
            params["comment"] = comment
        if not privsep:
            params["privsep"] = 0
        if expire:
            params["expire"] = expire
        return format_response(api_request("post", f"/access/users/{userid}/token/{tokenid}", **params))

    @mcp.tool()
    def delete_user_token(userid: str, tokenid: str) -> str:
        """Delete an API token.

        Args:
            userid: User ID (format: 'user@realm').
            tokenid: Token ID.
        """
        return format_response(api_request("delete", f"/access/users/{userid}/token/{tokenid}"))

    # ── Groups ────────────────────────────────────────────────────────

    @mcp.tool()
    def list_groups() -> str:
        """List all user groups."""
        return format_response(api_request("get", "/access/groups"))

    @mcp.tool()
    def get_group(groupid: str) -> str:
        """Get group details.

        Args:
            groupid: Group ID.
        """
        return format_response(api_request("get", f"/access/groups/{groupid}"))

    @mcp.tool()
    def create_group(groupid: str, comment: str = "") -> str:
        """Create a new group.

        Args:
            groupid: Group ID.
            comment: Description.
        """
        params: dict = {"groupid": groupid}
        if comment:
            params["comment"] = comment
        return format_response(api_request("post", "/access/groups", **params))

    @mcp.tool()
    def update_group(groupid: str, comment: str = "") -> str:
        """Update a group.

        Args:
            groupid: Group ID.
            comment: Description.
        """
        params: dict = {}
        if comment:
            params["comment"] = comment
        return format_response(api_request("put", f"/access/groups/{groupid}", **params))

    @mcp.tool()
    def delete_group(groupid: str) -> str:
        """Delete a group.

        Args:
            groupid: Group ID.
        """
        return format_response(api_request("delete", f"/access/groups/{groupid}"))

    # ── Roles ─────────────────────────────────────────────────────────

    @mcp.tool()
    def list_roles() -> str:
        """List all available roles."""
        return format_response(api_request("get", "/access/roles"))

    @mcp.tool()
    def get_role(roleid: str) -> str:
        """Get role details and its privileges.

        Args:
            roleid: Role ID.
        """
        return format_response(api_request("get", f"/access/roles/{roleid}"))

    @mcp.tool()
    def create_role(roleid: str, privs: str) -> str:
        """Create a new role with specific privileges.

        Args:
            roleid: Role ID.
            privs: Comma-separated list of privileges (e.g. 'VM.Allocate,VM.Config.Disk,VM.PowerMgmt').
        """
        return format_response(api_request("post", "/access/roles", roleid=roleid, privs=privs))

    @mcp.tool()
    def update_role(roleid: str, privs: str, append: bool = False) -> str:
        """Update role privileges.

        Args:
            roleid: Role ID.
            privs: Comma-separated list of privileges.
            append: Append privileges instead of replacing.
        """
        params: dict = {"privs": privs}
        if append:
            params["append"] = 1
        return format_response(api_request("put", f"/access/roles/{roleid}", **params))

    @mcp.tool()
    def delete_role(roleid: str) -> str:
        """Delete a role.

        Args:
            roleid: Role ID.
        """
        return format_response(api_request("delete", f"/access/roles/{roleid}"))

    # ── ACL (Access Control Lists) ────────────────────────────────────

    @mcp.tool()
    def get_acl() -> str:
        """Get the full ACL (access control list) — shows all permission assignments."""
        return format_response(api_request("get", "/access/acl"))

    @mcp.tool()
    def update_acl(path: str, roles: str, users: str = "", groups: str = "", tokens: str = "", propagate: bool = True, delete: bool = False) -> str:
        """Add or remove ACL entries (permission assignments).

        Args:
            path: Object path (e.g. '/', '/vms/100', '/storage/local', '/pool/mypool').
            roles: Comma-separated role list.
            users: Comma-separated user list (format: 'user@realm').
            groups: Comma-separated group list.
            tokens: Comma-separated token list (format: 'user@realm!tokenid').
            propagate: Propagate permissions to child objects.
            delete: Remove the ACL entry instead of adding.
        """
        params: dict = {"path": path, "roles": roles}
        if users:
            params["users"] = users
        if groups:
            params["groups"] = groups
        if tokens:
            params["tokens"] = tokens
        if not propagate:
            params["propagate"] = 0
        if delete:
            params["delete"] = 1
        return format_response(api_request("put", "/access/acl", **params))

    # ── Auth Domains / Realms ─────────────────────────────────────────

    @mcp.tool()
    def list_auth_domains() -> str:
        """List configured authentication realms/domains (PAM, PVE, LDAP, AD, OpenID)."""
        return format_response(api_request("get", "/access/domains"))

    @mcp.tool()
    def get_auth_domain(realm: str) -> str:
        """Get authentication domain configuration.

        Args:
            realm: Realm ID (e.g. 'pam', 'pve', 'my-ldap').
        """
        return format_response(api_request("get", f"/access/domains/{realm}"))

    @mcp.tool()
    def sync_auth_domain(realm: str, dry_run: bool = False, full: bool = False, enable_new: bool = True, remove_vanished: str = "") -> str:
        """Sync users/groups from an external auth domain (LDAP/AD).

        Args:
            realm: Realm ID to sync.
            dry_run: Only show what would change.
            full: Full sync (not just incremental).
            enable_new: Enable newly synced users.
            remove_vanished: Comma-separated: 'entry' (remove users), 'properties' (clear), 'acl' (remove ACLs).
        """
        params: dict = {}
        if dry_run:
            params["dry-run"] = 1
        if full:
            params["full"] = 1
        if not enable_new:
            params["enable-new"] = 0
        if remove_vanished:
            params["remove-vanished"] = remove_vanished
        return format_response(api_request("post", f"/access/domains/{realm}/sync", **params))

    # ── TFA (Two-Factor Authentication) ───────────────────────────────

    @mcp.tool()
    def list_tfa(userid: str = "") -> str:
        """List TFA (two-factor auth) entries.

        Args:
            userid: Filter by user ID (empty = all users).
        """
        if userid:
            return format_response(api_request("get", f"/access/tfa/{userid}"))
        return format_response(api_request("get", "/access/tfa"))

    # ── Permissions ───────────────────────────────────────────────────

    @mcp.tool()
    def get_permissions(userid: str = "", path: str = "") -> str:
        """Check effective permissions for a user on a given path.

        Args:
            userid: User to check (empty = current user).
            path: Object path to check (empty = root).
        """
        params: dict = {}
        if userid:
            params["userid"] = userid
        if path:
            params["path"] = path
        return format_response(api_request("get", "/access/permissions", **params))

    # ── Password ──────────────────────────────────────────────────────

    @mcp.tool()
    def change_password(userid: str, password: str) -> str:
        """Change a user's password.

        Args:
            userid: User ID (format: 'user@realm').
            password: New password.
        """
        return format_response(api_request("put", "/access/password", userid=userid, password=password))
