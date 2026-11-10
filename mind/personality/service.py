"""Personality service."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mind.personality.models import PersonalityProfile
from mind.personality.schemas import PersonalityUpdate
from security.auditing.audit import record_audit


async def get_or_create_profile(session: AsyncSession, identity_id: str) -> PersonalityProfile:
    res = await session.execute(
        select(PersonalityProfile).where(PersonalityProfile.identity_id == identity_id)
    )
    p = res.scalar_one_or_none()
    if p is None:
        p = PersonalityProfile(identity_id=identity_id)
        session.add(p)
        await session.flush()
        await session.commit()
        await session.refresh(p)
    return p


async def update_profile(session: AsyncSession, identity_id: str, data: PersonalityUpdate) -> PersonalityProfile:
    p = await get_or_create_profile(session, identity_id)
    if data.stable_traits is not None:
        p.stable_traits = data.stable_traits
    if data.adaptable_tendencies is not None:
        p.adaptable_tendencies = data.adaptable_tendencies
    if data.behavioral_patterns is not None:
        p.behavioral_patterns = data.behavioral_patterns
    if data.preferences is not None:
        p.preferences = data.preferences
    p.version += 1
    await record_audit(
        session, actor=data.actor, action="personality.update", target_type="personality",
        target_id=p.profile_id, details={"reason": data.reason},
    )
    await session.commit()
    await session.refresh(p)
    return p


async def apply_experience_drift(
    session: AsyncSession, identity_id: str, deltas: dict[str, Any], bound: float = 0.1, actor: str = "system"
) -> PersonalityProfile:
    """Apply bounded drift to adaptable tendencies only (never stable traits)."""
    p = await get_or_create_profile(session, identity_id)
    stable = set((p.stable_traits or {}).keys())
    tendencies = dict(p.adaptable_tendencies or {})
    for k, v in (deltas or {}).items():
        if not isinstance(v, (int, float)):
            continue
        if k in stable:
            continue
        cur = tendencies.get(k, 0.0)
        if not isinstance(cur, (int, float)):
            cur = 0.0
        nv = cur + v
        # bound change per application
        if nv - cur > bound:
            nv = cur + bound
        if cur - nv > bound:
            nv = cur - bound
        tendencies[k] = nv
    p.adaptable_tendencies = tendencies
    p.version += 1
    await record_audit(
        session, actor=actor, action="personality.drift", target_type="personality",
        target_id=p.profile_id, details={"keys": list(deltas.keys()), "bound": bound},
    )
    await session.commit()
    await session.refresh(p)
    return p
