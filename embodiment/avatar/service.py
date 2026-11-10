"""Embodiment service."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from embodiment.avatar.models import Avatar, Expression, MovementIntent, PerceptionEvent
from security.auditing.audit import record_audit


async def create_avatar(session: AsyncSession, identity_id: str, name: str = "", config: dict | None = None,
                        capabilities: list[str] | None = None, actor: str = "owner") -> Avatar:
    av = Avatar(identity_id=identity_id, name=name, config=config or {},
                capabilities=capabilities or [])
    session.add(av)
    await session.flush()
    await record_audit(session, actor=actor, action="embodiment.avatar.create", target_type="avatar",
                      target_id=av.avatar_id, details={"identity_id": identity_id})
    await session.commit()
    await session.refresh(av)
    return av


async def list_avatars(session: AsyncSession, identity_id: str) -> list[Avatar]:
    res = await session.execute(select(Avatar).where(Avatar.identity_id == identity_id))
    return list(res.scalars().all())


async def get_avatar(session: AsyncSession, avatar_id: str) -> Avatar | None:
    res = await session.execute(select(Avatar).where(Avatar.avatar_id == avatar_id))
    return res.scalar_one_or_none()


async def record_movement(session: AsyncSession, avatar_id: str, intent: dict[str, Any], actor: str = "system") -> MovementIntent:
    mi = MovementIntent(avatar_id=avatar_id, intent=intent)
    session.add(mi)
    await session.flush()
    await record_audit(session, actor=actor, action="embodiment.movement", target_type="avatar",
                      target_id=avatar_id, details={"intent": intent})
    await session.commit()
    await session.refresh(mi)
    return mi


async def record_perception(session: AsyncSession, avatar_id: str, modality: str, data: dict[str, Any],
                            confidence: float = 1.0, source: str = "", actor: str = "system") -> PerceptionEvent:
    pe = PerceptionEvent(avatar_id=avatar_id, modality=modality, data=data, confidence=confidence, source=source)
    session.add(pe)
    await session.flush()
    await record_audit(session, actor=actor, action="embodiment.perception", target_type="avatar",
                      target_id=avatar_id, details={"modality": modality})
    await session.commit()
    await session.refresh(pe)
    return pe


async def record_expression(session: AsyncSession, avatar_id: str, expression_type: str, payload: dict[str, Any],
                            actor: str = "system") -> Expression:
    ex = Expression(avatar_id=avatar_id, expression_type=expression_type, payload=payload)
    session.add(ex)
    await session.flush()
    await record_audit(session, actor=actor, action="embodiment.expression", target_type="avatar",
                      target_id=avatar_id, details={"type": expression_type})
    await session.commit()
    await session.refresh(ex)
    return ex
