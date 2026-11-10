"""Unit tests for identity service."""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from autonomy.lifecycle.states import LifecycleState
from core.identity_core import service
from core.identity_core.schemas import IdentityCreate, IdentityUpdate, ProfileData
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
async def test_create_and_retrieve(session):
    data = IdentityCreate(display_name="Alice", initial_profile=ProfileData(display_name="Alice", bio="hi"))
    ident = await service.create_identity(session, data)
    assert ident.identity_id
    assert ident.version == 1
    assert ident.status == LifecycleState.CREATED.value

    fetched = await service.get_identity(session, ident.identity_id)
    assert fetched is not None
    assert fetched.identity_id == ident.identity_id
    assert fetched.profile.data["bio"] == "hi"


@pytest.mark.asyncio
async def test_update_preserves_history(session):
    data = IdentityCreate(display_name="Bob")
    ident = await service.create_identity(session, data)
    iid = ident.identity_id
    upd = IdentityUpdate(profile=ProfileData(display_name="Bob", bio="changed"), reason="edit", actor="owner")
    await service.update_identity(session, iid, upd, actor="owner")
    versions = await service.list_versions(session, iid)
    assert len(versions) == 2
    integrity = await service.verify_integrity(session, iid)
    assert integrity.intact is True


@pytest.mark.asyncio
async def test_lifecycle_transitions(session):
    data = IdentityCreate(display_name="Carol")
    ident = await service.create_identity(session, data)
    iid = ident.identity_id
    await service.transition_lifecycle(session, iid, LifecycleState.ACTIVE, actor="owner")
    i2 = await service.get_identity(session, iid)
    assert i2.status == "active"
    # illegal transition
    with pytest.raises(ValueError):
        await service.transition_lifecycle(session, iid, LifecycleState.DELETED, actor="owner")


@pytest.mark.asyncio
async def test_integrity_detects_tampering(session):
    data = IdentityCreate(display_name="Dave")
    ident = await service.create_identity(session, data)
    iid = ident.identity_id
    # tamper manifest_hash
    ident2 = await service.get_identity(session, iid)
    ident2.manifest_hash = "deadbeef"
    await session.commit()
    res = await service.verify_integrity(session, iid)
    assert res.intact is False


@pytest.mark.asyncio
async def test_consent_grant_revoke(session):
    data = IdentityCreate(display_name="Eve")
    ident = await service.create_identity(session, data)
    iid = ident.identity_id
    from core.identity_core.schemas import ConsentCreate
    cr = await service.create_consent(session, iid, ConsentCreate(scope="data.read", granted_by="owner"))
    assert cr.revoked_at is None
    revoked = await service.revoke_consent(session, cr.id, actor="owner")
    assert revoked.revoked_at is not None
