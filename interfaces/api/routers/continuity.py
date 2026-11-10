"""Distributed continuity router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from distributed.nodes import service as dist_service
from storage.database import get_session

router = APIRouter(prefix="/continuity", tags=["continuity"])


@router.post("/nodes")
async def register_node(node_id: str = Query(...), role: str = "cognitive", session: AsyncSession = Depends(get_session)):
    n = await dist_service.register_node(session, node_id, role=role)
    return {"node_id": n.node_id, "role": n.role, "status": n.status}


@router.get("/nodes")
async def list_nodes(role: str | None = None, session: AsyncSession = Depends(get_session)):
    nodes = await dist_service.list_nodes(session, role=role)
    return [{"node_id": n.node_id, "role": n.role, "status": n.status, "last_heartbeat": n.last_heartbeat} for n in nodes]


@router.post("/nodes/{node_id}/heartbeat")
async def heartbeat(node_id: str, session: AsyncSession = Depends(get_session)):
    try:
        n = await dist_service.heartbeat(session, node_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"node_id": n.node_id, "status": n.status, "last_heartbeat": n.last_heartbeat}


@router.post("/checkpoints")
async def create_checkpoint(identity_id: str = Query(...), node_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    cp = await dist_service.create_checkpoint(session, identity_id, node_id)
    return {"checkpoint_id": cp.checkpoint_id, "identity_version": cp.identity_version, "verified": cp.verified, "hash": cp.snapshot_hash}


@router.get("/checkpoints/verify/{checkpoint_id}")
async def verify_checkpoint(checkpoint_id: str, session: AsyncSession = Depends(get_session)):
    try:
        cp = await dist_service.verify_checkpoint(session, checkpoint_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"checkpoint_id": cp.checkpoint_id, "verified": cp.verified}


@router.post("/migrate")
async def migrate(identity_id: str = Query(...), source_node: str = Query(...), dest_node: str = Query(...),
                 session: AsyncSession = Depends(get_session)):
    mr = await dist_service.migrate_identity(session, identity_id, source_node, dest_node)
    return {"migration_id": mr.migration_id, "status": mr.status, "integrity_verified": mr.integrity_verified}


@router.post("/recover")
async def recover(identity_id: str = Query(...), checkpoint_id: str | None = None, session: AsyncSession = Depends(get_session)):
    try:
        return await dist_service.recover_identity_state(session, identity_id, checkpoint_id=checkpoint_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/conflicts")
async def conflicts(identity_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    return await dist_service.detect_conflicts(session, identity_id)


@router.post("/tasks")
async def schedule_task(identity_id: str | None = None, kind: str = Query(...), idempotency_key: str = "",
                        session: AsyncSession = Depends(get_session)):
    task = await dist_service.schedule_task(session, identity_id, kind, {}, idempotency_key=idempotency_key)
    return {"task_id": task.task_id, "node_id": task.node_id, "status": task.status}
