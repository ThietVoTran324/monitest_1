import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

import pytest
from fastapi import Request
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete, select

from app.api.v1 import deps_auth
from app.core import rate_limit as rate_limit_mod
from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.main import app
from app.models.monitor import Incident, IncidentStatus, Monitor
from app.models.status_page import StatusPage
from app.models.user import User
from app.workers.tasks import checks


@dataclass
class _DummyTask:
    id: str


@pytest.fixture(autouse=True)
def _reset_public_rate_limiter():
    rate_limit_mod.public_status_rate_limiter._events.clear()
    yield
    rate_limit_mod.public_status_rate_limiter._events.clear()


@pytest.mark.asyncio
async def test_status_page_create_and_public_fetch(monkeypatch) -> None:
    user_id = uuid.uuid4()
    slug = f"it-prod-status-{uuid.uuid4().hex[:8]}"

    def _fake_delay(monitor_id: str):
        return _DummyTask(id=f"task-{monitor_id}")

    monkeypatch.setattr(checks.check_http_monitor, "delay", _fake_delay)

    async with AsyncSessionLocal() as session:
        await session.execute(delete(User).where(User.email == "statuspage-user@test.local"))
        session.add(
            User(
                id=user_id,
                email="statuspage-user@test.local",
                hashed_password=None,
                is_verified=True,
            )
        )
        await session.commit()

    async def _override_current_user(_: Request) -> User:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(User).where(User.id == user_id))
            return result.scalar_one()

    app.dependency_overrides[deps_auth.get_current_user] = _override_current_user
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")

    try:
        m1 = await client.post(
            "/api/v1/monitors",
            json={
                "name": "it-status-page-1",
                "url": "https://example.com/secret-path",
                "interval_seconds": 60,
                "timeout_seconds": 10,
            },
        )
        assert m1.status_code == 201
        m2 = await client.post(
            "/api/v1/monitors",
            json={
                "name": "it-status-page-2",
                "url": "https://example.org",
                "interval_seconds": 60,
                "timeout_seconds": 10,
            },
        )
        assert m2.status_code == 201
        m1_id = m1.json()["id"]
        m2_id = m2.json()["id"]

        create_page = await client.post(
            "/api/v1/status-pages",
            json={
                "name": "Production Status",
                "slug": slug,
                "is_public": True,
                "monitor_ids": [m1_id, m2_id],
            },
        )
        assert create_page.status_code == 201
        body = create_page.json()
        assert body["slug"] == slug
        assert len(body["monitors"]) == 2
        assert all("url" in m for m in body["monitors"])

        listed = await client.get("/api/v1/status-pages")
        assert listed.status_code == 200
        assert len(listed.json()) >= 1
        assert all("url" in m for page in listed.json() for m in page["monitors"])

        async with AsyncSessionLocal() as session:
            session.add(
                Incident(
                    monitor_id=uuid.UUID(m1_id),
                    opened_at=datetime.now(UTC),
                    status=IncidentStatus.OPEN,
                    open_reason="failed https://example.com/secret-path",
                )
            )
            await session.commit()

        public_page = await client.get(f"/api/v1/public/status-pages/{slug}")
        assert public_page.status_code == 200
        public_body = public_page.json()
        assert public_body["slug"] == slug
        assert len(public_body["monitors"]) == 2
        for m in public_body["monitors"]:
            assert "url" not in m
            assert "name" in m
            assert "current_status" in m
        assert isinstance(public_body["incidents"], list)
        assert len(public_body["incidents"]) >= 1
        for inc in public_body["incidents"]:
            assert "open_reason" not in inc
            assert "close_reason" not in inc
            assert "monitor_id" in inc

        private = await client.patch(
            f"/api/v1/status-pages/{body['id']}",
            json={"is_public": False},
        )
        assert private.status_code == 200
        hidden = await client.get(f"/api/v1/public/status-pages/{slug}")
        assert hidden.status_code == 404
    finally:
        await client.aclose()
        app.dependency_overrides.clear()
        async with AsyncSessionLocal() as session:
            await session.execute(
                delete(StatusPage).where(
                    StatusPage.user_id == user_id,
                    StatusPage.slug.like("it-prod-status-%"),
                )
            )
            await session.execute(delete(Incident).where(Incident.open_reason.like("%secret-path%")))
            await session.execute(delete(Monitor).where(Monitor.name.like("it-status-page-%")))
            await session.execute(delete(User).where(User.email == "statuspage-user@test.local"))
            await session.commit()


@pytest.mark.asyncio
async def test_status_page_ownership_cross_user(monkeypatch) -> None:
    user_a = uuid.uuid4()
    user_b = uuid.uuid4()
    slug = f"it-own-{uuid.uuid4().hex[:8]}"

    monkeypatch.setattr(checks.check_http_monitor, "delay", lambda mid: _DummyTask(id=f"t-{mid}"))

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(User).where(User.email.in_(["sp-owner-a@test.local", "sp-owner-b@test.local"]))
        )
        session.add(User(id=user_a, email="sp-owner-a@test.local", hashed_password=None, is_verified=True))
        session.add(User(id=user_b, email="sp-owner-b@test.local", hashed_password=None, is_verified=True))
        await session.commit()

    current = {"id": user_a}

    async def _override(_: Request) -> User:
        async with AsyncSessionLocal() as session:
            return (
                await session.execute(select(User).where(User.id == current["id"]))
            ).scalar_one()

    app.dependency_overrides[deps_auth.get_current_user] = _override
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    try:
        m_a = await client.post(
            "/api/v1/monitors",
            json={"name": "it-sp-own-a", "url": "https://example.com", "interval_seconds": 60, "timeout_seconds": 10},
        )
        assert m_a.status_code == 201
        page = await client.post(
            "/api/v1/status-pages",
            json={
                "name": "A page",
                "slug": slug,
                "is_public": True,
                "monitor_ids": [m_a.json()["id"]],
            },
        )
        assert page.status_code == 201
        page_id = page.json()["id"]

        current["id"] = user_b
        m_b = await client.post(
            "/api/v1/monitors",
            json={"name": "it-sp-own-b", "url": "https://example.org", "interval_seconds": 60, "timeout_seconds": 10},
        )
        assert m_b.status_code == 201

        steal = await client.patch(
            f"/api/v1/status-pages/{page_id}",
            json={"name": "stolen"},
        )
        assert steal.status_code == 404

        attach = await client.patch(
            f"/api/v1/status-pages/{page_id}",
            json={"monitor_ids": [m_b.json()["id"]]},
        )
        assert attach.status_code == 404

        current["id"] = user_a
        bad_attach = await client.patch(
            f"/api/v1/status-pages/{page_id}",
            json={"monitor_ids": [m_b.json()["id"]]},
        )
        assert bad_attach.status_code == 400
    finally:
        await client.aclose()
        app.dependency_overrides.clear()
        async with AsyncSessionLocal() as session:
            await session.execute(delete(StatusPage).where(StatusPage.slug == slug))
            await session.execute(delete(Monitor).where(Monitor.name.like("it-sp-own-%")))
            await session.execute(
                delete(User).where(User.email.in_(["sp-owner-a@test.local", "sp-owner-b@test.local"]))
            )
            await session.commit()


@pytest.mark.asyncio
async def test_public_status_rate_limit(monkeypatch) -> None:
    user_id = uuid.uuid4()
    slug = f"it-rl-{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(checks.check_http_monitor, "delay", lambda mid: _DummyTask(id=f"t-{mid}"))
    monkeypatch.setattr(settings, "public_status_rate_limit_max_attempts", 3)
    monkeypatch.setattr(settings, "public_status_rate_limit_window_seconds", 60)

    async with AsyncSessionLocal() as session:
        await session.execute(delete(User).where(User.email == "sp-rl@test.local"))
        session.add(User(id=user_id, email="sp-rl@test.local", hashed_password=None, is_verified=True))
        await session.commit()

    async def _override(_: Request) -> User:
        async with AsyncSessionLocal() as session:
            return (await session.execute(select(User).where(User.id == user_id))).scalar_one()

    app.dependency_overrides[deps_auth.get_current_user] = _override
    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    try:
        m = await client.post(
            "/api/v1/monitors",
            json={"name": "it-sp-rl", "url": "https://example.com", "interval_seconds": 60, "timeout_seconds": 10},
        )
        assert m.status_code == 201
        page = await client.post(
            "/api/v1/status-pages",
            json={
                "name": "RL",
                "slug": slug,
                "is_public": True,
                "monitor_ids": [m.json()["id"]],
            },
        )
        assert page.status_code == 201

        statuses = []
        for _ in range(4):
            res = await client.get(f"/api/v1/public/status-pages/{slug}")
            statuses.append(res.status_code)
        assert statuses[:3] == [200, 200, 200]
        assert statuses[3] == 429
        limited = await client.get(f"/api/v1/public/status-pages/{slug}")
        assert limited.status_code == 429
        assert limited.headers.get("Retry-After")
    finally:
        await client.aclose()
        app.dependency_overrides.clear()
        async with AsyncSessionLocal() as session:
            await session.execute(delete(StatusPage).where(StatusPage.slug == slug))
            await session.execute(delete(Monitor).where(Monitor.name == "it-sp-rl"))
            await session.execute(delete(User).where(User.email == "sp-rl@test.local"))
            await session.commit()
