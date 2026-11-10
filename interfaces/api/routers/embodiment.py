"""Embodiment router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from embodiment.avatar import service as emb_service
from storage.database import get_session

router = APIRouter(prefix="/embodiment", tags=["embodiment"])


@router.post("/avatars")
async def create_avatar(identity_id: str = Query(...), name: str = "", session: AsyncSession = Depends(get_session)):
    av = await emb_service.create_avatar(session, identity_id, name=name)
    return {"avatar_id": av.avatar_id, "identity_id": av.identity_id, "name": av.name}


@router.get("/avatars")
async def list_avatars(identity_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    items = await emb_service.list_avatars(session, identity_id)
    return [{"avatar_id": a.avatar_id, "name": a.name, "is_active": a.is_active} for a in items]


@router.post("/avatars/{avatar_id}/movement")
async def movement(avatar_id: str, intent: dict | None = None, session: AsyncSession = Depends(get_session)):
    intent = intent or {}
    mi = await emb_service.record_movement(session, avatar_id, intent)
    return {"intent_id": mi.intent_id, "avatar_id": avatar_id}


@router.post("/avatars/{avatar_id}/perception")
async def perception(avatar_id: str, modality: str = Query(...), data: dict | None = None, confidence: float = 1.0,
                     source: str = "", session: AsyncSession = Depends(get_session)):
    data = data or {}
    pe = await emb_service.record_perception(session, avatar_id, modality, data, confidence=confidence, source=source)
    return {"event_id": pe.event_id, "modality": pe.modality}


@router.post("/avatars/{avatar_id}/expressions")
async def expression(avatar_id: str, expression_type: str = Query(...), payload: dict | None = None,
                     session: AsyncSession = Depends(get_session)):
    payload = payload or {}
    ex = await emb_service.record_expression(session, avatar_id, expression_type, payload)
    return {"expression_id": ex.expression_id, "type": ex.expression_type}
