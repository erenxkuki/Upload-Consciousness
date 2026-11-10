"""Unit tests for distributed continuity."""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.identity_core import service as id_service
from core.identity_core.schemas import IdentityCreate
from distributed.nodes import service as dist_service
from storage.database import Base


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as s:
        yield s
    await engine.dispose()


@pytest.mark.asyncio
async def test_multi_node_checkpoint_migrate_recover(session):
    ident = await id_service.create_identity(session, IdentityCreate(display_name="Dist"))
    iid = ident.identity_id
    await dist_service.register_node(session, "node-a", role="identity_authority")
    await dist_service.register_node(session, "node-b", role="cognitive")
    nodes = await dist_service.list_nodes(session)
    assert len(nodes) == 2

    # checkpoint on node-a
    cp = await dist_service.create_checkpoint(session, iid, "node-a")
    assert cp.verified is True
    vcp = await dist_service.verify_checkpoint(session, cp.checkpoint_id)
    assert vcp.verified is True

    # migrate a->b
    mr = await dist_service.migrate_identity(session, iid, "node-a", "node-b")
    assert mr.status == "completed"
    assert mr.integrity_verified is True

    # recover
    rec = await dist_service.recover_identity_state(session, iid)
    assert rec["verified"] is True
    assert rec["identity_version"] == ident.version

    # conflict detection (none)
    c = await dist_service.detect_conflicts(session, iid)
    assert c["has_conflicts"] is False

    # idempotent task scheduling
    t1 = await dist_service.schedule_task(session, iid, "cognitive_step", {}, idempotency_key="k1")
    t2 = await dist_service.schedule_task(session, iid, "cognitive_step", {}, idempotency_key="k1")
    assert t1.task_id == t2.task_id


@pytest.mark.asyncio
async def test_node_down_and_task_queued(session):
    await dist_service.register_node(session, "node-x", role="cognitive")
    await dist_service.mark_node_down(session, "node-x")
    task = await dist_service.schedule_task(session, None, "maintenance", {}, preferred_role="cognitive")
    # all cognitive nodes down -> queued
    assert task.status == "queued"
    assert task.node_id is None
