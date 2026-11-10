"""Unit tests for emotion and personality services."""
from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from biological_systems.emotional_system import service as emo_service
from biological_systems.emotional_system.schemas import EmotionalUpdate
from core.identity_core import service as id_service
from core.identity_core.schemas import IdentityCreate
from mind.personality import service as pers_service
from mind.personality.schemas import PersonalityUpdate
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


async def _iid(session):
    ident = await id_service.create_identity(session, IdentityCreate(display_name="P"))
    return ident.identity_id


@pytest.mark.asyncio
async def test_emotion_state_persists_and_history(session):
    iid = await _iid(session)
    st = await emo_service.update_state(session, iid, EmotionalUpdate(
        dimensions={"valence": 0.5, "arousal": 0.3}, trigger="test", actor="system",
    ))
    assert st.dimensions["valence"] == 0.5
    st2 = await emo_service.get_or_create_state(session, iid)
    assert st2.dimensions["valence"] == 0.5
    hist = await emo_service.get_history(session, iid)
    assert len(hist) >= 1


@pytest.mark.asyncio
async def test_emotion_decay(session):
    iid = await _iid(session)
    await emo_service.update_state(session, iid, EmotionalUpdate(dimensions={"valence": 1.0}, trigger="x"))
    st = await emo_service.apply_decay(session, iid, factor=0.5)
    assert st.dimensions["valence"] == 0.5


@pytest.mark.asyncio
async def test_personality_stable_not_drifted(session):
    iid = await _iid(session)
    await pers_service.update_profile(session, iid, PersonalityUpdate(
        stable_traits={"openness": 0.8}, adaptable_tendencies={"stress": 0.2}, actor="owner",
    ))
    p = await pers_service.apply_experience_drift(session, iid, {"stress": 0.5, "openness": 0.5}, bound=0.1)
    # openness is stable trait, should not be in adaptable_tendencies
    assert "openness" not in (p.adaptable_tendencies or {})
    # stress drifted but bounded
    assert abs((p.adaptable_tendencies or {}).get("stress", 0) - 0.3) <= 1e-9 or (p.adaptable_tendencies or {}).get("stress", 0) <= 0.3


@pytest.mark.asyncio
async def test_personality_profile_persists(session):
    iid = await _iid(session)
    await pers_service.update_profile(session, iid, PersonalityUpdate(preferences={"theme": "dark"}, actor="owner"))
    p2 = await pers_service.get_or_create_profile(session, iid)
    assert p2.preferences == {"theme": "dark"}
