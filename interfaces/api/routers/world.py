"""Digital world router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from digital_world.simulation import service as world_service
from storage.database import get_session

router = APIRouter(prefix="/world", tags=["world"])


@router.post("/environments")
async def create_environment(name: str = Query(...), env_type: str = "indoor", session: AsyncSession = Depends(get_session)):
    env = await world_service.create_environment(session, name, env_type=env_type)
    return {"environment_id": env.environment_id, "name": env.name, "env_type": env.env_type}


@router.post("/enter")
async def enter(identity_id: str = Query(...), environment_id: str = Query(...), avatar_id: str | None = None,
                session: AsyncSession = Depends(get_session)):
    pres = await world_service.enter_environment(session, identity_id, environment_id, avatar_id=avatar_id)
    return {"presence_id": pres.presence_id, "environment_id": pres.environment_id}


@router.get("/presences")
async def presences(environment_id: str = Query(...), session: AsyncSession = Depends(get_session)):
    items = await world_service.list_presences(session, environment_id)
    return [{"presence_id": p.presence_id, "identity_id": p.identity_id, "avatar_id": p.avatar_id,
             "position": p.position} for p in items]


@router.post("/messages")
async def send_message(sender_identity_id: str = Query(...), content: dict | None = None, recipient_identity_id: str | None = None,
                       environment_id: str | None = None, session: AsyncSession = Depends(get_session)):
    content = content or {}
    msg = await world_service.send_message(session, sender_identity_id, content,
                                          recipient_identity_id=recipient_identity_id, environment_id=environment_id)
    return {"message_id": msg.message_id, "sender": msg.sender_identity_id}


@router.get("/messages")
async def list_messages(environment_id: str | None = None, identity_id: str | None = None, limit: int = 50,
                        session: AsyncSession = Depends(get_session)):
    items = await world_service.list_messages(session, environment_id=environment_id, identity_id=identity_id, limit=limit)
    return [{"message_id": m.message_id, "sender": m.sender_identity_id, "recipient": m.recipient_identity_id,
             "content": m.content, "created_at": m.created_at} for m in items]


@router.post("/governance/rules")
async def add_rule(environment_id: str | None = None, rule_type: str = Query(...), description: str = "",
                   consent_required: bool = True, session: AsyncSession = Depends(get_session)):
    rule = await world_service.add_governance_rule(session, environment_id, rule_type, description,
                                                  consent_required=consent_required)
    return {"rule_id": rule.rule_id, "rule_type": rule.rule_type}
