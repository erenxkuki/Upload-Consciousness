"""Integration tests for identity API."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from interfaces.api.main import app
from storage.database import Base, engine


@pytest.fixture(autouse=True)
async def reset_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_identity_crud_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        payload = {"display_name": "Zed", "initial_profile": {"display_name": "Zed", "bio": "hi"}, "consent_scope": "identity.create", "granted_by": "owner"}
        r = await client.post("/api/v1/identity", json=payload)
        assert r.status_code == 201 or r.status_code == 200, r.text
        iid = r.json()["identity_id"]
        r2 = await client.get(f"/api/v1/identity/{iid}")
        assert r2.status_code == 200
        r3 = await client.get(f"/api/v1/identity/{iid}/integrity")
        assert r3.json()["intact"] is True
        r4 = await client.patch(f"/api/v1/identity/{iid}", json={"profile": {"display_name": "Zed", "bio": "updated"}, "reason": "edit", "actor": "owner"})
        assert r4.status_code == 200
        assert r4.json()["version"] == 2
        r5 = await client.post(f"/api/v1/identity/{iid}/lifecycle", params={"new_state": "active", "actor": "owner"})
        assert r5.status_code == 200
        assert r5.json()["status"] == "active"
