"""Memory router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from mind.memories import service
from mind.memories.schemas import (
    ConsolidationDecision,
    ConsolidationProposalCreate,
    ExperienceCreate,
    MemoryCorrect,
    MemoryCreate,
    MemoryRead,
)
from storage.database import get_session

router = APIRouter(prefix="/memory", tags=["memory"])


def _to_read(m) -> MemoryRead:
    return MemoryRead(
        memory_id=m.memory_id,
        identity_id=m.identity_id,
        memory_type=m.memory_type,
        origin_class=m.origin_class,
        content=m.content,
        context=m.context,
        entities=m.entities or [],
        tags=m.tags or [],
        confidence=m.confidence,
        source=m.source,
        created_at=m.created_at,
        event_at=m.event_at,
        version=m.version,
        supersedes=m.supersedes,
        retention_policy=m.retention_policy,
        access_restrictions=m.access_restrictions or {},
        is_deleted=m.is_deleted,
        provenance=m.provenance or [],
    )


@router.post("/experiences")
async def store_experience(
    identity_id: str = Query(...),
    payload: ExperienceCreate = ...,
    session: AsyncSession = Depends(get_session),
):
    exp = await service.store_experience(session, identity_id, payload)
    return {"experience_id": exp.experience_id, "identity_id": exp.identity_id, "created_at": exp.created_at}


@router.post("", response_model=MemoryRead)
async def store_memory(
    identity_id: str = Query(...),
    payload: MemoryCreate = ...,
    session: AsyncSession = Depends(get_session),
):
    mem = await service.store_memory(session, identity_id, payload)
    return _to_read(mem)


@router.get("", response_model=list[MemoryRead])
async def retrieve(
    identity_id: str = Query(...),
    memory_type: str | None = None,
    origin_class: str | None = None,
    tags: str | None = Query(None, description="comma-separated"),
    min_confidence: float = 0.0,
    limit: int = 50,
    session: AsyncSession = Depends(get_session),
):
    tag_list = [t.strip() for t in tags.split(",")] if tags else None
    items = await service.retrieve_memories(
        session, identity_id, memory_type=memory_type, origin_class=origin_class,
        tags=tag_list, min_confidence=min_confidence, limit=limit,
    )
    return [_to_read(m) for m in items]


@router.get("/{memory_id}", response_model=MemoryRead)
async def get_memory(memory_id: str, session: AsyncSession = Depends(get_session)):
    mem = await service.get_memory(session, memory_id)
    if mem is None:
        raise HTTPException(status_code=404, detail="memory not found")
    return _to_read(mem)


@router.patch("/{memory_id}", response_model=MemoryRead)
async def correct_memory(
    memory_id: str, payload: MemoryCorrect, session: AsyncSession = Depends(get_session)
):
    try:
        mem = await service.correct_memory(session, memory_id, payload, actor=payload.actor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return _to_read(mem)


@router.delete("/{memory_id}", response_model=MemoryRead)
async def delete_memory(memory_id: str, actor: str = "owner", session: AsyncSession = Depends(get_session)):
    try:
        mem = await service.soft_delete_memory(session, memory_id, actor=actor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return _to_read(mem)


@router.post("/consolidation", status_code=201)
async def propose(
    identity_id: str = Query(...),
    payload: ConsolidationProposalCreate = ...,
    actor: str = "system",
    session: AsyncSession = Depends(get_session),
):
    cp = await service.propose_consolidation(session, identity_id, payload, actor=actor)
    return {"proposal_id": cp.proposal_id, "status": cp.status, "created_at": cp.created_at}


@router.post("/consolidation/{proposal_id}/decide")
async def decide(
    proposal_id: str, payload: ConsolidationDecision, session: AsyncSession = Depends(get_session)
):
    try:
        cp = await service.decide_consolidation(
            session, proposal_id, payload.approved, payload.decided_by, payload.reason
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"proposal_id": cp.proposal_id, "status": cp.status, "decided_at": cp.decided_at}


@router.get("/consolidation")
async def list_proposals(identity_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    cps = await service.list_proposals(session, identity_id)
    return [{"proposal_id": c.proposal_id, "status": c.status, "created_at": c.created_at} for c in cps]
