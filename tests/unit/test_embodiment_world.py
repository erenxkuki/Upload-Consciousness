"""Unit tests for embodiment and world."""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.identity_core import service as id_service
from core.identity_core.schemas import IdentityCreate
from digital_world.simulation import service as world_service
from embodiment.avatar import service as emb_service
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
async def test_avatar_lifecycle_independent_of_identity(session):
    ident = await id_service.create_identity(session, IdentityCreate(display_name="Emb"))
    iid = ident.identity_id
    av = await emb_service.create_avatar(session, iid, name="avatar1", capabilities=["move"])
    assert av.avatar_id
    await emb_service.record_movement(session, av.avatar_id, {"dx": 1, "dy": 0})
    await emb_service.record_perception(session, av.avatar_id, "vision", {"objects": ["cube"]}, confidence=0.9)
    await emb_service.record_expression(session, av.avatar_id, "smile", {"intensity": 0.8})
    avs = await emb_service.list_avatars(session, iid)
    assert len(avs) == 1
    # identity still intact
    ident2 = await id_service.get_identity(session, iid)
    assert ident2.identity_id == iid


@pytest.mark.asyncio
async def test_world_environment_presence_and_messaging(session):
    i1 = (await id_service.create_identity(session, IdentityCreate(display_name="A"))).identity_id
    i2 = (await id_service.create_identity(session, IdentityCreate(display_name="B"))).identity_id
    env = await world_service.create_environment(session, "Room", env_type="indoor")
    await world_service.enter_environment(session, i1, env.environment_id)
    await world_service.enter_environment(session, i2, env.environment_id)
    presences = await world_service.list_presences(session, env.environment_id)
    assert len(presences) == 2
    msg = await world_service.send_message(session, i1, {"text": "hi"}, recipient_identity_id=i2, environment_id=env.environment_id)
    assert msg.message_id
    msgs = await world_service.list_messages(session, environment_id=env.environment_id)
    assert len(msgs) == 1
    await world_service.add_governance_rule(session, env.environment_id, "no_spam", "no spamming", consent_required=True)
