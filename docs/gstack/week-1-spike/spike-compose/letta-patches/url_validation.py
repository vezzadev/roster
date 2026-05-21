"""Spike-only patch for letta.helpers.url_validation.

Letta's stock validator hard-rejects MCP server URLs that resolve to non-public
IP addresses or `.local`-suffixed hostnames as an SSRF defense. The spike runs
Letta + nextcloud-mcp-* in the same Docker bridge network, so the MCP hostnames
necessarily resolve to RFC-1918 addresses (172.x.x.x) — without this patch, every
`resync_tools` and `connect` call to the in-network MCP servers fails with
`Hostname resolves to non-public IP`.

This file is bind-mounted over `/app/letta/helpers/url_validation.py` inside the
Letta container via docker-compose. Drop the mount when Letta exposes a
`trusted_hosts` env var upstream (issue to file before declaring the spike
result official).

Behavior diff from upstream:
  - The empty-URL, scheme, hostname-presence, and blocked-hostname checks
    still apply.
  - The private-IP rejection is bypassed.
"""

import ipaddress
import socket
from urllib.parse import urlparse

_BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.",
    "metadata.google.internal",
    "metadata.google.internal.",
}

_BLOCKED_SUFFIXES = (
    ".localdomain",
    ".home.arpa",
    ".svc",
    ".cluster.local",
)


def _normalize_hostname(hostname: str) -> str:
    return hostname.rstrip(".").lower()


def _is_blocked_hostname(hostname: str) -> bool:
    normalized = _normalize_hostname(hostname)
    blocked_hostnames = {_normalize_hostname(value) for value in _BLOCKED_HOSTNAMES}
    return normalized in blocked_hostnames or any(normalized.endswith(suffix) for suffix in _BLOCKED_SUFFIXES)


def validate_mcp_server_url(url: str, *, resolve_hostname: bool = True) -> str:
    if not url:
        raise ValueError("server_url cannot be empty")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"server_url must start with 'http://' or 'https://', got: '{url}'")
    if not parsed.netloc:
        raise ValueError(f"server_url must have a valid host, got: '{url}'")
    if parsed.hostname is None:
        raise ValueError("Missing hostname")

    hostname = _normalize_hostname(parsed.hostname)
    if _is_blocked_hostname(hostname):
        raise ValueError(f"Blocked internal hostname: {parsed.hostname}")

    return url
