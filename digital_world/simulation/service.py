"""Digital world service."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from digital_world.simulation.models import (
    Environment,
    GovernanceRule,
    SocialMessage,
    WorldPresence,
)
from security.auditing.audit import record_audit


async def create_environment(session: AsyncSession, name: str, env_type: str = "indoor", config: dict | None = None,
                             actor: str = "system") -> Environment:
    env = Environment(name=name, env_type=env_type, config=config or {})
    session.add(env)
    await session.flush()
    await record_audit(session, actor=actor, action="world.environment.create", target_type="environment",
                      target_id=env.environment_id, details={"name": name})
    await session.commit()
    await session.refresh(env)
    return env


async def enter_environment(session: AsyncSession, identity_id: str, environment_id: str, avatar_id: str | None = None,
                            position: dict | None = None, actor: str = "system") -> WorldPresence:
    pres = WorldPresence(identity_id=identity_id, environment_id=environment_id, avatar_id=avatar_id,
                         position=position or {})
    session.add(pres)
    await session.flush()
    await record_audit(session, actor=actor, action="world.enter", target_type="presence",
                      target_id=pres.presence_id, details={"identity_id": identity_id, "environment_id": environment_id})
    await session.commit()
    await session.refresh(pres)
    return pres


async def list_presences(session: AsyncSession, environment_id: str) -> list[WorldPresence]:
    res = await session.execute(select(WorldPresence).where(WorldPresence.environment_id == environment_id))
    return list(res.scalars().all())


async def send_message(session: AsyncSession, sender_identity_id: str, content: dict[str, Any],
                      recipient_identity_id: str | None = None, environment_id: str | None = None,
                      actor: str = "system") -> SocialMessage:
    msg = SocialMessage(sender_identity_id=sender_identity_id, recipient_identity_id=recipient_identity_id,
                        environment_id=environment_id, content=content)
    session.add(msg)
    await session.flush()
    await record_audit(session, actor=actor, action="world.message.send", target_type="message",
                      target_id=msg.message_id, details={"sender": sender_identity_id})
    await session.commit()
    await session.refresh(msg)
    return msg


async def list_messages(session: AsyncSession, environment_id: str | None = None, identity_id: str | None = None,
                        limit: int = 50) -> list[SocialMessage]:
    stmt = select(SocialMessage)
    if environment_id:
        stmt = stmt.where(SocialMessage.environment_id == environment_id)
    if identity_id:
        stmt = stmt.where(SocialMessage.recipient_identity_id == identity_id)
    stmt = stmt.order_by(SocialMessage.created_at.desc()).limit(limit)
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def add_governance_rule(session: AsyncSession, environment_id: str | None, rule_type: str, description: str,
                             consent_required: bool = True, actor: str = "system") -> GovernanceRule:
    rule = GovernanceRule(environment_id=environment_id, rule_type=rule_type, description=description,
                          consent_required=consent_required)
    session.add(rule)
    await session.flush()
    await record_audit(session, actor=actor, action="world.governance.rule", target_type="rule",
                      target_id=rule.rule_id, details={"type": rule_type})
    await session.commit()
    await session.refresh(rule)
    return rule
