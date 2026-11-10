"""Unit tests for memory service."""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.identity_core import service as id_service
from core.identity_core.schemas import IdentityCreate
from mind.memories import service
from mind.memories.schemas import (
    ConsolidationProposalCreate,
    MemoryCorrect,
    MemoryCreate,
)
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


async def _make_identity(session):
    ident = await id_service.create_identity(session, IdentityCreate(display_name="MemTest"))
    return ident.identity_id


@pytest.mark.asyncio
async def test_store_and_retrieve_memory(session):
    iid = await _make_identity(session)
    mem = await service.store_memory(session, iid, MemoryCreate(
        memory_type="episodic", origin_class="actual_experience",
        content={"text": "went to park"}, tags=["outdoor"], confidence=0.9,
    ))
    assert mem.memory_id
    items = await service.retrieve_memories(session, iid, memory_type="episodic")
    assert len(items) == 1
    assert items[0].origin_class == "actual_experience"


@pytest.mark.asyncio
async def test_correction_preserves_history(session):
    iid = await _make_identity(session)
    mem = await service.store_memory(session, iid, MemoryCreate(
        memory_type="semantic", origin_class="imported", content={"fact": "sky is blue"}, confidence=1.0,
    ))
    corrected = await service.correct_memory(session, mem.memory_id, MemoryCorrect(
        content={"fact": "sky is blue (corrected)"}, confidence=0.95, reason="fix", actor="owner",
    ))
    assert corrected.version == 2
    assert corrected.content["fact"].endswith("corrected)")
    # original content retained in version diff
    from sqlalchemy import select

    from mind.memories.models import MemoryVersion
    res = await session.execute(select(MemoryVersion).where(MemoryVersion.memory_id == mem.memory_id))
    versions = list(res.scalars().all())
    assert len(versions) == 2


@pytest.mark.asyncio
async def test_origin_class_filter_and_no_auto_promotion(session):
    iid = await _make_identity(session)
    await service.store_memory(session, iid, MemoryCreate(
        memory_type="semantic", origin_class="generated", content={"text": "maybe"}, confidence=0.5,
    ))
    # generated should not appear in actual_experience filter
    actual = await service.retrieve_memories(session, iid, origin_class="actual_experience")
    assert len(actual) == 0
    all_items = await service.retrieve_memories(session, iid)
    assert len(all_items) == 1
    assert all_items[0].origin_class == "generated"


@pytest.mark.asyncio
async def test_soft_delete(session):
    iid = await _make_identity(session)
    mem = await service.store_memory(session, iid, MemoryCreate(
        memory_type="episodic", origin_class="actual_experience", content={"text": "x"},
    ))
    await service.soft_delete_memory(session, mem.memory_id, actor="owner")
    visible = await service.retrieve_memories(session, iid)
    assert len(visible) == 0
    all_items = await service.retrieve_memories(session, iid, include_deleted=True)
    assert len(all_items) == 1
    assert all_items[0].is_deleted is True


@pytest.mark.asyncio
async def test_consolidation_proposal_and_approval_creates_generated_memory(session):
    iid = await _make_identity(session)
    m1 = await service.store_memory(session, iid, MemoryCreate(
        memory_type="episodic", origin_class="actual_experience", content={"text": "a"},
    ))
    m2 = await service.store_memory(session, iid, MemoryCreate(
        memory_type="episodic", origin_class="actual_experience", content={"text": "b"},
    ))
    cp = await service.propose_consolidation(session, iid, ConsolidationProposalCreate(
        source_memory_ids=[m1.memory_id, m2.memory_id],
        proposed_memory={"summary": "a and b"},
    ), actor="system")
    assert cp.status == "pending"
    decided = await service.decide_consolidation(session, cp.proposal_id, True, "owner", "ok")
    assert decided.status == "approved"
    # a generated consolidated memory now exists
    gen = await service.retrieve_memories(session, iid, origin_class="generated")
    assert len(gen) == 1
    assert gen[0].content.get("summary") == "a and b"
    assert gen[0].origin_class == "generated"
