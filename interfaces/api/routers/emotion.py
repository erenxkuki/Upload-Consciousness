"""Emotion router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from biological_systems.emotional_system import service as emo_service
from biological_systems.emotional_system.schemas import EmotionalUpdate
from storage.database import get_session

router = APIRouter(prefix="/emotions", tags=["emotions"])


@router.get("")
async def get_state(identity_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    st = await emo_service.get_or_create_state(session, identity_id)
    return {"state_id": st.state_id, "identity_id": st.identity_id, "dimensions": st.dimensions, "version": st.version, "updated_at": st.updated_at}


@router.patch("")
async def update_state(identity_id: str = Query(...), payload: EmotionalUpdate = ..., session: AsyncSession = Depends(get_session)):
    try:
        st = await emo_service.update_state(session, identity_id, payload)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"state_id": st.state_id, "identity_id": st.identity_id, "dimensions": st.dimensions, "version": st.version, "updated_at": st.updated_at}


@router.post("/decay")
async def decay(identity_id: str = Query(...), factor: float = 0.9, session: AsyncSession = Depends(get_session)):
    st = await emo_service.apply_decay(session, identity_id, factor=factor)
    return {"state_id": st.state_id, "dimensions": st.dimensions, "version": st.version}


@router.get("/history")
async def history(identity_id: str = Query(...), limit: int = 50, session: AsyncSession = Depends(get_session)):
    items = await emo_service.get_history(session, identity_id, limit=limit)
    return [{"id": h.id, "timestamp": h.timestamp, "trigger": h.trigger, "source_ref": h.source_ref,
             "deltas": h.deltas, "policy": h.policy, "confidence": h.confidence,
             "resulting_dimensions": h.resulting_dimensions} for h in items]
