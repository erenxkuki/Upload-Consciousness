"""Cognition router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from biological_systems.brain import service as brain_service
from core.cognitive_core.orchestrator import run_cognitive_step
from storage.database import get_session

router = APIRouter(prefix="/cognition", tags=["cognition"])


@router.post("/step")
async def cognitive_step(
    identity_id: str = Query(...),
    input_text: str = Query(...),
    actor: str = "system",
    session: AsyncSession = Depends(get_session),
):
    try:
        return await run_cognitive_step(session, identity_id, input_text, actor=actor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/self-model")
async def get_self_model(identity_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    sm = await brain_service.get_or_create_self_model(session, identity_id)
    return {"identity_id": identity_id, "data": sm.data, "version": sm.version, "updated_at": sm.updated_at}


@router.patch("/self-model")
async def update_self_model(identity_id: str = Query(...), data: dict | None = None, actor: str = "system",
                           session: AsyncSession = Depends(get_session)):
    data = data or {}
    sm = await brain_service.update_self_model(session, identity_id, data, actor=actor)
    return {"identity_id": identity_id, "data": sm.data, "version": sm.version}


@router.get("/working-memory")
async def get_wm(identity_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    entries = await brain_service.get_working_memory(session, identity_id)
    return {"identity_id": identity_id, "entries": entries}


@router.get("/reflections")
async def reflections(identity_id: str = Query(...), limit: int = 50, session: AsyncSession = Depends(get_session)):
    items = await brain_service.list_reflections(session, identity_id, limit=limit)
    return [{"reflection_id": r.reflection_id, "kind": r.kind, "content": r.content, "created_at": r.created_at} for r in items]


@router.post("/decisions")
async def decide(identity_id: str = Query(...), options: list[str] = Query(...), context: dict | None = None,
                session: AsyncSession = Depends(get_session)):
    context = context or {}
    rec = await brain_service.evaluate_decision(session, identity_id, options, context)
    return {"decision_id": rec.decision_id, "chosen": rec.chosen, "rationale": rec.rationale,
            "confidence": rec.confidence, "created_at": rec.created_at}


@router.post("/goals")
async def create_goal(identity_id: str = Query(...), description: str = Query(...), session: AsyncSession = Depends(get_session)):
    g = await brain_service.create_goal(session, identity_id, description)
    return {"goal_id": g.goal_id, "description": g.description, "status": g.status, "progress": g.progress}
