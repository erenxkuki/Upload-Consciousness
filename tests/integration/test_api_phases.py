"""Integration tests for phases 2-7 API endpoints."""
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
async def test_phase2_memory_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        # create identity
        r = await c.post("/api/v1/identity", json={"display_name": "M", "consent_scope": "identity.create", "granted_by": "owner"})
        iid = r.json()["identity_id"]
        # store experience
        r = await c.post("/api/v1/memory/experiences", params={"identity_id": iid}, json={"content": {"text": "park"}, "source": "user"})
        assert r.status_code == 200
        # store memory
        r = await c.post("/api/v1/memory", params={"identity_id": iid}, json={
            "memory_type": "episodic", "origin_class": "actual_experience", "content": {"text": "park"}, "confidence": 0.9,
        })
        assert r.status_code == 200
        mid = r.json()["memory_id"]
        # retrieve
        r = await c.get("/api/v1/memory", params={"identity_id": iid})
        assert r.status_code == 200 and len(r.json()) == 1
        # correct
        r = await c.patch(f"/api/v1/memory/{mid}", json={"content": {"text": "park (corrected)"}, "reason": "fix", "actor": "owner"})
        assert r.status_code == 200 and r.json()["version"] == 2
        # integrity-ish: origin preserved
        r = await c.get(f"/api/v1/memory/{mid}")
        assert r.json()["origin_class"] == "actual_experience"


@pytest.mark.asyncio
async def test_phase3_emotion_personality_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/identity", json={"display_name": "E", "consent_scope": "identity.create", "granted_by": "owner"})
        iid = r.json()["identity_id"]
        r = await c.patch("/api/v1/emotions", params={"identity_id": iid}, json={"dimensions": {"valence": 0.5}, "trigger": "t"})
        assert r.status_code == 200 and r.json()["dimensions"]["valence"] == 0.5
        r = await c.get("/api/v1/emotions", params={"identity_id": iid})
        assert r.json()["dimensions"]["valence"] == 0.5
        r = await c.post("/api/v1/emotions/decay", params={"identity_id": iid, "factor": 0.5})
        assert r.status_code == 200
        r = await c.patch("/api/v1/personality", params={"identity_id": iid}, json={"preferences": {"theme": "dark"}, "actor": "owner"})
        assert r.status_code == 200
        r = await c.get("/api/v1/personality", params={"identity_id": iid})
        assert r.json()["preferences"] == {"theme": "dark"}


@pytest.mark.asyncio
async def test_phase4_cognition_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/identity", json={"display_name": "C", "consent_scope": "identity.create", "granted_by": "owner"})
        iid = r.json()["identity_id"]
        r = await c.post("/api/v1/cognition/step", params={"identity_id": iid, "input_text": "hello"})
        assert r.status_code == 200 and "output" in r.json()
        r = await c.patch("/api/v1/cognition/self-model", params={"identity_id": iid}, json={"capabilities": ["reason"]})
        assert r.status_code == 200
        r = await c.get("/api/v1/cognition/working-memory", params={"identity_id": iid})
        assert r.status_code == 200 and len(r.json()["entries"]) >= 1
        r = await c.post("/api/v1/cognition/decisions", params={"identity_id": iid}, json=None) if False else None
        r = await c.post("/api/v1/cognition/decisions", params={"identity_id": iid, "options": ["a", "b"]})
        assert r.status_code == 200
        r = await c.post("/api/v1/cognition/goals", params={"identity_id": iid, "description": "g1"})
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_phase5_continuity_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/identity", json={"display_name": "D", "consent_scope": "identity.create", "granted_by": "owner"})
        iid = r.json()["identity_id"]
        await c.post("/api/v1/continuity/nodes", params={"node_id": "n1", "role": "identity_authority"})
        await c.post("/api/v1/continuity/nodes", params={"node_id": "n2", "role": "cognitive"})
        r = await c.get("/api/v1/continuity/nodes")
        assert r.status_code == 200 and len(r.json()) == 2
        r = await c.post("/api/v1/continuity/checkpoints", params={"identity_id": iid, "node_id": "n1"})
        assert r.status_code == 200
        cp_id = r.json()["checkpoint_id"]
        r = await c.get(f"/api/v1/continuity/checkpoints/verify/{cp_id}")
        assert r.json()["verified"] is True
        r = await c.post("/api/v1/continuity/migrate", params={"identity_id": iid, "source_node": "n1", "dest_node": "n2"})
        assert r.status_code == 200 and r.json()["status"] == "completed"
        r = await c.post("/api/v1/continuity/recover", params={"identity_id": iid})
        assert r.status_code == 200 and r.json()["verified"] is True
        r = await c.get("/api/v1/continuity/conflicts", params={"identity_id": iid})
        assert r.json()["has_conflicts"] is False


@pytest.mark.asyncio
async def test_phase6_embodiment_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/identity", json={"display_name": "B", "consent_scope": "identity.create", "granted_by": "owner"})
        iid = r.json()["identity_id"]
        r = await c.post("/api/v1/embodiment/avatars", params={"identity_id": iid, "name": "av1"})
        assert r.status_code == 200
        aid = r.json()["avatar_id"]
        r = await c.post(f"/api/v1/embodiment/avatars/{aid}/movement", json={"dx": 1})
        assert r.status_code == 200
        r = await c.post(f"/api/v1/embodiment/avatars/{aid}/perception", params={"modality": "vision"}, json={"objects": ["cube"]})
        assert r.status_code == 200
        r = await c.post(f"/api/v1/embodiment/avatars/{aid}/expressions", params={"expression_type": "smile"}, json={"intensity": 0.8})
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_phase7_world_api():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r1 = await c.post("/api/v1/identity", json={"display_name": "W1", "consent_scope": "identity.create", "granted_by": "owner"})
        r2 = await c.post("/api/v1/identity", json={"display_name": "W2", "consent_scope": "identity.create", "granted_by": "owner"})
        i1, i2 = r1.json()["identity_id"], r2.json()["identity_id"]
        r = await c.post("/api/v1/world/environments", params={"name": "Room", "env_type": "indoor"})
        assert r.status_code == 200
        eid = r.json()["environment_id"]
        r = await c.post("/api/v1/world/enter", params={"identity_id": i1, "environment_id": eid})
        assert r.status_code == 200
        r = await c.post("/api/v1/world/enter", params={"identity_id": i2, "environment_id": eid})
        assert r.status_code == 200
        r = await c.get("/api/v1/world/presences", params={"environment_id": eid})
        assert r.status_code == 200 and len(r.json()) == 2
        r = await c.post("/api/v1/world/messages", params={"sender_identity_id": i1, "environment_id": eid}, json={"text": "hi"})
        assert r.status_code == 200
        r = await c.get("/api/v1/world/messages", params={"environment_id": eid})
        assert r.status_code == 200 and len(r.json()) == 1
        r = await c.post("/api/v1/world/governance/rules", params={"rule_type": "no_spam"}, json=None) if False else await c.post("/api/v1/world/governance/rules", params={"rule_type": "no_spam", "description": "no spam"})
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_idempotency_replay():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.post("/api/v1/identity", json={"display_name": "Idem", "consent_scope": "identity.create", "granted_by": "owner"},
                         headers={"Idempotency-Key": "k-123"})
        assert r.status_code == 200
        iid1 = r.json()["identity_id"]
        r2 = await c.post("/api/v1/identity", json={"display_name": "Idem", "consent_scope": "identity.create", "granted_by": "owner"},
                          headers={"Idempotency-Key": "k-123"})
        assert r2.status_code == 200
        assert r2.headers.get("idempotent-replayed") == "true"
        assert r2.json()["identity_id"] == iid1
