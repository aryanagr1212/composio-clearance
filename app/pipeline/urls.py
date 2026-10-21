"""URL checks for the fetcher.

The live pipeline opens URLs that come from a search API and from the
developer who typed a website. That is a server-side request, so we refuse
non-public hosts before connecting. This is a basic guard, not a full SSRF
suite: it does not defend against a public host that redirects after we have
already connected, beyond checking each hop.
"""

from __future__ import annotations

import ipaddress
import os
import socket
from urllib.parse import urljoin, urlparse, urlunparse

from app.pipeline.errors import ResearchError


class UnsafeURL(ResearchError):
    """The URL is not something this app should open."""


_BLOCKED_HOSTS = {"localhost", "metadata.google.internal"}

# Some sandboxes and corporate proxies answer every DNS lookup with a
# "fake IP" from 198.18.0.0/15 and route the real connection themselves.
# Off by default. Set ALLOW_FAKE_IP_DNS=1 only on such a network.
_FAKE_IP_NET = ipaddress.ip_network("198.18.0.0/15")


def _fake_ip_allowed(address: str) -> bool:
    if os.getenv("ALLOW_FAKE_IP_DNS", "").strip().lower() not in {"1", "true", "yes"}:
        return False
    try:
        return ipaddress.ip_address(address) in _FAKE_IP_NET
    except ValueError:
        return False


def canonicalize(url: str) -> str:
    """Drop the fragment and trailing slash so source matching is stable."""
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, "", parsed.query, ""))


def _host_is_blocked(host: str) -> bool:
    host = host.lower().rstrip(".")
    if host in _BLOCKED_HOSTS or host.endswith(".local") or host.endswith(".internal"):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    # ip.is_global is false for loopback, private, link-local, and reserved ranges.
    return not ip.is_global


def ensure_public_http_url(url: str) -> str:
    """Return the URL if it is http(s) and does not point at a non-public host.

    Hostnames are resolved. If any address is non-public, the URL is rejected.
    """
    parsed = urlparse(url.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise UnsafeURL(f"Only public http(s) URLs can be opened (got {url!r}).")
    host = parsed.hostname
    if _host_is_blocked(host):
        raise UnsafeURL(f"Refusing to open a non-public address ({host}).")
    # IP literals are decided above. Hostnames still need a DNS check.
    if _is_ip_literal(host):
        return url
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise UnsafeURL(f"Could not resolve {host}.") from exc
    for info in infos:
        address = info[4][0]
        if _host_is_blocked(address) and not _fake_ip_allowed(address):
            raise UnsafeURL(f"Refusing to open {host}; it resolves to a non-public address.")
    return url


def _is_ip_literal(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def join_redirect(current: str, location: str) -> str:
    return urljoin(current, location)
