"""SSRF guards shared by monitor create/update and HTTP probes."""

from __future__ import annotations

import asyncio
import socket
from ipaddress import IPv4Address, IPv6Address, ip_address
from urllib.parse import urlsplit

IpAddress = IPv4Address | IPv6Address


def is_blocked_ip(ip: IpAddress) -> bool:
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    )


def is_forbidden_ip_string(raw_ip: str) -> bool:
    try:
        return is_blocked_ip(ip_address(raw_ip))
    except ValueError:
        return True


def validate_url_for_ssrf(url: str) -> None:
    """Reject unsafe schemes, userinfo, and literal private/local hosts.

    Does not resolve DNS — that happens at probe time via ``assert_host_public``.
    """
    parsed = urlsplit((url or "").strip())
    scheme = (parsed.scheme or "").lower()
    if scheme not in {"http", "https"}:
        raise ValueError("only http/https URLs are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("URLs with embedded credentials are not allowed")
    host = (parsed.hostname or "").strip().lower()
    if not host:
        raise ValueError("invalid monitor url host")
    if host == "localhost" or host.endswith(".local"):
        raise ValueError("local/internal hosts are not allowed")
    try:
        ip = ip_address(host)
    except ValueError:
        return
    if is_blocked_ip(ip):
        raise ValueError("private/internal IP targets are not allowed")


def parse_host_and_port(url: str) -> tuple[str, int, bool]:
    parsed = urlsplit(url)
    host = parsed.hostname or ""
    is_https = parsed.scheme == "https"
    if not host:
        raise ValueError("invalid host")
    if parsed.port:
        return host, parsed.port, is_https
    return host, (443 if is_https else 80), is_https


async def assert_host_public(url: str) -> None:
    """Resolve hostname and reject if any address is non-public."""
    validate_url_for_ssrf(url)
    host, port, _ = parse_host_and_port(url)
    infos = await asyncio.get_running_loop().getaddrinfo(host, port, type=socket.SOCK_STREAM)
    if not infos:
        raise ValueError("target host does not resolve")
    for info in infos:
        resolved_ip = info[4][0]
        if is_forbidden_ip_string(resolved_ip):
            raise ValueError("target resolves to private/internal IP")
