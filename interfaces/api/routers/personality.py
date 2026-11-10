"""Personality router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mind.personality import service as pers_service
from mind.personality.schemas import PersonalityUpdate
from storage.database import get_session

router = APIRouter(prefix="/personality", tags=["personality"])


@router.get("")
async def get_profile(identity_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    p = await pers_service.get_or_create_profile(session, identity_id)
    return {"profile_id": p.profile_id, "identity_id": p.identity_id,
            "stable_traits": p.stable_traits or {}, "adaptable_tendencies": p.adaptable_tendencies or {},
            "behavioral_patterns": p.behavioral_patterns or {}, "preferences": p.preferences or {},
            "version": p.version, "updated_at": p.updated_at}


@router.patch("")
async def update_profile(identity_id: str = Query(...), payload: PersonalityUpdate = ..., session: AsyncSession = Depends(get_session)):
    try:
        p = await pers_service.update_profile(session, identity_id, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"profile_id": p.profile_id, "identity_id": p.identity_id,
            "stable_traits": p.stable_traits or {}, "adaptable_tendencies": p.adaptable_tendencies or {},
            "behavioral_patterns": p.behavioral_patterns or {}, "preferences": p.preferences or {},
            "version": p.version, "updated_at": p.updated_at}


@router.post("/drift")
async def drift(identity_id: str = Query(...), deltas: dict | None = None, bound: float = 0.1, actor: str = "system",
               session: AsyncSession = Depends(get_session)):
    deltas = deltas or {}
    p = await pers_service.apply_experience_drift(session, identity_id, deltas, bound=bound, actor=actor)
    return {"profile_id": p.profile_id, "adaptable_tendencies": p.adaptable_tendencies or {}, "version": p.version}
