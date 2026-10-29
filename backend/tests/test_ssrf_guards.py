"""Sprint1 SSRF guards: URL validation, DNS, redirect re-check, body cap."""

from __future__ import annotations

from types import SimpleNamespace
from urllib.parse import urlparse

import httpx
import pytest

from app.security.ssrf import assert_host_public, validate_url_for_ssrf
from app.services.monitor_service import MonitorValidationError, validate_monitor_url_host
from app.workers.tasks import checks
from app.workers.tasks.checks import _ensure_public_target, _http_get_ssrf_safe, _perform_probe


@pytest.mark.parametrize(
    "url,match",
    [
        ("http://localhost:8080", "local/internal hosts"),
        ("https://app.local/path", "local/internal hosts"),
        ("http://127.0.0.1/", "private/internal IP"),
        ("http://10.0.0.1", "private/internal IP"),
        ("http://192.168.1.1", "private/internal IP"),
        ("http://[::1]/", "private/internal IP"),
        ("ftp://example.com", "only http/https"),
        ("http://user:pass@example.com/", "embedded credentials"),
        ("https://token@evil.com/", "embedded credentials"),
    ],
)
def test_validate_url_for_ssrf_rejects_unsafe(url: str, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        validate_url_for_ssrf(url)
    with pytest.raises(MonitorValidationError, match=match):
        validate_monitor_url_host(url)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com",
        "http://example.com/path?q=1",
        "https://status.example.org:8443/health",
    ],
)
def test_validate_url_for_ssrf_allows_public_hosts(url: str) -> None:
    validate_url_for_ssrf(url)
    validate_monitor_url_host(url)


@pytest.mark.asyncio
async def test_ensure_public_target_blocks_private_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_getaddrinfo(host: str, port: int, type: int):  # noqa: A002
        return [(2, 1, 6, "", ("10.0.0.5", port))]

    loop = checks.asyncio.get_running_loop()
    monkeypatch.setattr(loop, "getaddrinfo", _fake_getaddrinfo)

    with pytest.raises(ValueError, match="private/internal"):
        await _ensure_public_target("http://example.com")


@pytest.mark.asyncio
async def test_assert_host_public_allows_public_ip(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_getaddrinfo(host: str, port: int, type: int):  # noqa: A002
        return [(2, 1, 6, "", ("93.184.216.34", port))]

    loop = checks.asyncio.get_running_loop()
    monkeypatch.setattr(loop, "getaddrinfo", _fake_getaddrinfo)
    await assert_host_public("http://example.com")


def _public_dns(monkeypatch: pytest.MonkeyPatch) -> None:
    async def _fake_getaddrinfo(host: str, port: int, type: int):  # noqa: A002
        lowered = host.lower()
        if lowered in {"localhost"} or lowered.endswith(".local"):
            return [(2, 1, 6, "", ("127.0.0.1", port))]
        try:
            from ipaddress import ip_address

            ip = ip_address(lowered)
            return [(2, 1, 6, "", (str(ip), port))]
        except ValueError:
            return [(2, 1, 6, "", ("93.184.216.34", port))]

    # Patch both the running loop (assert_host_public) and any fresh lookups.
    import app.security.ssrf as ssrf_mod

    async def _patched_assert(url: str) -> None:
        from app.security.ssrf import parse_host_and_port, validate_url_for_ssrf
        from app.security.ssrf import is_forbidden_ip_string

        validate_url_for_ssrf(url)
        host, port, _ = parse_host_and_port(url)
        infos = await _fake_getaddrinfo(host, port, 1)
        if not infos:
            raise ValueError("target host does not resolve")
        for info in infos:
            if is_forbidden_ip_string(info[4][0]):
                raise ValueError("target resolves to private/internal IP")

    monkeypatch.setattr(ssrf_mod, "assert_host_public", _patched_assert)
    monkeypatch.setattr(checks, "_ensure_public_target", _patched_assert)


@pytest.mark.asyncio
async def test_redirect_to_localhost_is_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    _public_dns(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        path = urlparse(str(request.url)).path
        if path == "/start":
            return httpx.Response(302, headers={"Location": "http://127.0.0.1/secret"})
        return httpx.Response(200, content=b"ok")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, follow_redirects=False) as client:
        with pytest.raises(ValueError, match="private/internal|local/internal|ssrf"):
            await _http_get_ssrf_safe(
                client=client,
                url="https://example.com/start",
                timeout_seconds=5,
                max_redirects=5,
                max_response_bytes=1024,
            )


@pytest.mark.asyncio
async def test_body_over_cap_is_blocked(monkeypatch: pytest.MonkeyPatch) -> None:
    _public_dns(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * 2048)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, follow_redirects=False) as client:
        with pytest.raises(ValueError, match="body exceeds limit"):
            await _http_get_ssrf_safe(
                client=client,
                url="https://example.com/big",
                timeout_seconds=5,
                max_redirects=5,
                max_response_bytes=512,
            )


@pytest.mark.asyncio
async def test_happy_path_small_body(monkeypatch: pytest.MonkeyPatch) -> None:
    _public_dns(monkeypatch)

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/plain"}, content=b"ok")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, follow_redirects=False) as client:
        response, ttfb_ms, final_url = await _http_get_ssrf_safe(
            client=client,
            url="https://example.com/ok",
            timeout_seconds=5,
            max_redirects=5,
            max_response_bytes=1024,
        )
    assert response.status_code == 200
    assert final_url.endswith("/ok")
    assert ttfb_ms is not None


@pytest.mark.asyncio
async def test_perform_probe_blocks_redirect_ssrf(monkeypatch: pytest.MonkeyPatch) -> None:
    _public_dns(monkeypatch)

    async def _no_metrics(url: str, timeout_seconds: int):
        return None, None, None

    monkeypatch.setattr(checks, "_collect_network_metrics", _no_metrics)

    def handler(request: httpx.Request) -> httpx.Response:
        if urlparse(str(request.url)).path == "/start":
            return httpx.Response(302, headers={"Location": "http://10.0.0.9/x"})
        return httpx.Response(200, content=b"ok")

    monitor = SimpleNamespace(
        url="https://example.com/start",
        timeout_seconds=5,
        slow_threshold_ms=500,
        accepted_status_codes="200-399",
        max_retries=0,
    )
    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport, follow_redirects=False) as client:
        result = await _perform_probe(client, monitor, "local", max_retries=0)  # type: ignore[arg-type]

    assert result["status"] == checks.CheckRunStatus.DOWN
    assert result["error_type"] == "blocked_target"
    assert result["error_message"]
    assert "private/internal" in str(result["error_message"]) or "ssrf" in str(result["error_message"])
