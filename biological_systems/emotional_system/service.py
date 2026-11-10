"""Emotional system service."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from biological_systems.emotional_system.models import EmotionalHistory, EmotionalState
from biological_systems.emotional_system.schemas import EmotionalUpdate
from security.auditing.audit import record_audit

DEFAULT_DIMS = {
    "valence": 0.0, "arousal": 0.0, "dominance": 0.0, "intensity": 0.0,
    "persistence": 0.0, "context": "", "triggering_experience": "",
    "confidence": 1.0, "duration": 0.0, "recovery_dynamics": 0.5,
}


async def get_or_create_state(session: AsyncSession, identity_id: str) -> EmotionalState:
    res = await session.execute(
        select(EmotionalState).where(EmotionalState.identity_id == identity_id)
    )
    st = res.scalar_one_or_none()
    if st is None:
        st = EmotionalState(identity_id=identity_id, dimensions=dict(DEFAULT_DIMS))
        session.add(st)
        await session.flush()
        await session.commit()
        await session.refresh(st)
    return st


async def update_state(session: AsyncSession, identity_id: str, data: EmotionalUpdate) -> EmotionalState:
    st = await get_or_create_state(session, identity_id)
    old_dims = dict(st.dimensions or {})
    new_dims = dict(old_dims)
    # apply deltas / overrides
    for k, v in (data.dimensions or {}).items():
        if k in new_dims and isinstance(v, (int, float)) and isinstance(new_dims.get(k), (int, float)):
            # treat as delta for numeric dims? We'll set absolute if key prefixed? Simpler: apply as delta for known numeric
            new_dims[k] = new_dims.get(k, 0) + v if False else v
        else:
            new_dims[k] = v
    # Actually apply as absolute override for provided keys (clearer contract)
    new_dims = dict(old_dims)
    for k, v in (data.dimensions or {}).items():
        new_dims[k] = v

    # compute deltas
    deltas = {}
    for k in set(old_dims) | set(new_dims):
        ov = old_dims.get(k)
        nv = new_dims.get(k)
        if ov != nv:
            deltas[k] = {"from": ov, "to": nv}

    st.dimensions = new_dims
    st.version += 1

    hist = EmotionalHistory(
        identity_id=identity_id,
        trigger=data.trigger,
        source_ref=data.source_ref,
        deltas=deltas,
        policy=data.policy,
        confidence=float(new_dims.get("confidence", 1.0)),
        resulting_dimensions=dict(new_dims),
    )
    session.add(hist)

    await record_audit(
        session, actor=data.actor, action="emotion.update", target_type="emotional_state",
        target_id=st.state_id, details={"trigger": data.trigger, "dims_changed": list(deltas.keys())},
    )
    await session.commit()
    await session.refresh(st)
    return st


async def apply_decay(session: AsyncSession, identity_id: str, factor: float = 0.9) -> EmotionalState:
    """Time-based decay toward baseline (0)."""
    st = await get_or_create_state(session, identity_id)
    dims = dict(st.dimensions or {})
    for k in ("valence", "arousal", "dominance", "intensity", "persistence"):
        if k in dims and isinstance(dims[k], (int, float)):
            dims[k] = dims[k] * factor
    st.dimensions = dims
    st.version += 1
    hist = EmotionalHistory(
        identity_id=identity_id, trigger="decay", source_ref="",
        deltas={"decay_factor": factor}, policy="time_decay",
        confidence=float(dims.get("confidence", 1.0)), resulting_dimensions=dict(dims),
    )
    session.add(hist)
    await session.commit()
    await session.refresh(st)
    return st


async def get_history(session: AsyncSession, identity_id: str, limit: int = 50) -> list[EmotionalHistory]:
    res = await session.execute(
        select(EmotionalHistory)
        .where(EmotionalHistory.identity_id == identity_id)
        .order_by(EmotionalHistory.timestamp.desc())
        .limit(limit)
    )
    return list(res.scalars().all())
