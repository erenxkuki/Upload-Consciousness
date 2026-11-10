"""Brain / cognitive core service."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from biological_systems.brain.models import (
    DecisionRecord,
    Goal,
    Reflection,
    SelfModel,
    WorkingMemorySnapshot,
)
from biological_systems.brain.reasoning.adapters import ReasoningAdapter, get_default_adapter
from security.auditing.audit import record_audit

# ---- Self model ----

async def get_or_create_self_model(session: AsyncSession, identity_id: str) -> SelfModel:
    res = await session.execute(select(SelfModel).where(SelfModel.identity_id == identity_id))
    sm = res.scalar_one_or_none()
    if sm is None:
        sm = SelfModel(identity_id=identity_id, data={
            "capabilities": [], "limitations": [], "known_history": [],
            "current_state": "initialized", "uncertainty": [],
        })
        session.add(sm)
        await session.flush()
        await session.commit()
        await session.refresh(sm)
    return sm


async def update_self_model(session: AsyncSession, identity_id: str, data: dict[str, Any], actor: str = "system") -> SelfModel:
    sm = await get_or_create_self_model(session, identity_id)
    merged = dict(sm.data or {})
    merged.update(data or {})
    sm.data = merged
    sm.version += 1
    await record_audit(session, actor=actor, action="self_model.update", target_type="self_model",
                      target_id=sm.id, details={"keys": list((data or {}).keys())})
    await session.commit()
    await session.refresh(sm)
    return sm


# ---- Working memory ----

async def get_working_memory(session: AsyncSession, identity_id: str) -> list[dict[str, Any]]:
    res = await session.execute(select(WorkingMemorySnapshot).where(WorkingMemorySnapshot.identity_id == identity_id))
    snap = res.scalar_one_or_none()
    return list(snap.entries) if snap else []


async def set_working_memory(session: AsyncSession, identity_id: str, entries: list[dict[str, Any]], actor: str = "system") -> WorkingMemorySnapshot:
    res = await session.execute(select(WorkingMemorySnapshot).where(WorkingMemorySnapshot.identity_id == identity_id))
    snap = res.scalar_one_or_none()
    if snap is None:
        snap = WorkingMemorySnapshot(identity_id=identity_id, entries=list(entries))
        session.add(snap)
    else:
        snap.entries = list(entries)
    await session.flush()
    await record_audit(session, actor=actor, action="working_memory.set", target_type="working_memory",
                      target_id=snap.id if snap.id else identity_id, details={"count": len(entries)})
    await session.commit()
    await session.refresh(snap)
    return snap


async def push_working_memory(session: AsyncSession, identity_id: str, entry: dict[str, Any], actor: str = "system") -> WorkingMemorySnapshot:
    entries = await get_working_memory(session, identity_id)
    entries.append({"added_at": datetime.now(UTC).isoformat(), **entry})
    # cap size
    if len(entries) > 50:
        entries = entries[-50:]
    return await set_working_memory(session, identity_id, entries, actor=actor)


# ---- Attention (context prioritization) ----

def prioritize_context(items: list[dict[str, Any]], key: str = "salience", top_k: int = 10) -> list[dict[str, Any]]:
    ranked = sorted(items, key=lambda x: float(x.get(key, 0.0)), reverse=True)
    return ranked[:top_k]


# ---- Reflection ----

async def record_reflection(session: AsyncSession, identity_id: str, kind: str, content: dict[str, Any], actor: str = "system") -> Reflection:
    r = Reflection(identity_id=identity_id, kind=kind, content=content)
    session.add(r)
    await session.flush()
    await record_audit(session, actor=actor, action="reflection.record", target_type="reflection",
                      target_id=r.reflection_id, details={"kind": kind})
    await session.commit()
    await session.refresh(r)
    return r


async def list_reflections(session: AsyncSession, identity_id: str, limit: int = 50) -> list[Reflection]:
    res = await session.execute(
        select(Reflection).where(Reflection.identity_id == identity_id)
        .order_by(Reflection.created_at.desc()).limit(limit)
    )
    return list(res.scalars().all())


# ---- Decision evaluation ----

async def evaluate_decision(
    session: AsyncSession, identity_id: str, options: list[str], context: dict[str, Any],
    adapter: ReasoningAdapter | None = None, actor: str = "system",
) -> DecisionRecord:
    adapter = adapter or get_default_adapter()
    prompt = f"Choose among options: {options}. Context: {context}"
    result = await adapter.generate(prompt, context=context)
    # naive selection: pick first option mentioned or first
    chosen = options[0] if options else ""
    for opt in options:
        if opt.lower() in result.text.lower():
            chosen = opt
            break
    rec = DecisionRecord(
        identity_id=identity_id, options=options, chosen=chosen,
        rationale=result.text, confidence=result.confidence, context=context,
    )
    session.add(rec)
    await session.flush()
    await record_audit(session, actor=actor, action="decision.evaluate", target_type="decision",
                      target_id=rec.decision_id, details={"chosen": chosen, "provider": result.provider})
    await session.commit()
    await session.refresh(rec)
    return rec


# ---- Goals / planning ----

async def create_goal(session: AsyncSession, identity_id: str, description: str, actor: str = "system") -> Goal:
    g = Goal(identity_id=identity_id, description=description)
    session.add(g)
    await session.flush()
    await record_audit(session, actor=actor, action="goal.create", target_type="goal",
                      target_id=g.goal_id, details={"description": description})
    await session.commit()
    await session.refresh(g)
    return g


async def update_goal_progress(session: AsyncSession, goal_id: str, progress: float, status: str | None = None, actor: str = "system") -> Goal:
    res = await session.execute(select(Goal).where(Goal.goal_id == goal_id))
    g = res.scalar_one_or_none()
    if g is None:
        raise ValueError("goal not found")
    g.progress = max(0.0, min(1.0, progress))
    if status:
        g.status = status
    await record_audit(session, actor=actor, action="goal.update", target_type="goal",
                      target_id=g.goal_id, details={"progress": g.progress, "status": g.status})
    await session.commit()
    await session.refresh(g)
    return g


async def list_goals(session: AsyncSession, identity_id: str) -> list[Goal]:
    res = await session.execute(select(Goal).where(Goal.identity_id == identity_id))
    return list(res.scalars().all())
