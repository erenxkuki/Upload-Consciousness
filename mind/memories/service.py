"""Memory service."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mind.memories.models import ConsolidationProposal, Experience, Memory, MemoryVersion
from mind.memories.schemas import (
    ConsolidationProposalCreate,
    ExperienceCreate,
    MemoryCorrect,
    MemoryCreate,
)
from security.auditing.audit import record_audit


async def store_experience(
    session: AsyncSession, identity_id: str, data: ExperienceCreate, actor: str = "system"
) -> Experience:
    exp = Experience(
        identity_id=identity_id,
        content=data.content,
        context=data.context,
        source=data.source,
        occurred_at=data.occurred_at,
    )
    session.add(exp)
    await session.flush()
    await record_audit(
        session, actor=actor, action="experience.store", target_type="experience",
        target_id=exp.experience_id, details={"identity_id": identity_id},
    )
    await session.commit()
    await session.refresh(exp)
    return exp


async def store_memory(
    session: AsyncSession, identity_id: str, data: MemoryCreate, actor: str = "system"
) -> Memory:
    prov = list(data.provenance)
    prov.append({"operation": "store", "actor": actor, "timestamp": datetime.now(UTC).isoformat()})
    mem = Memory(
        identity_id=identity_id,
        memory_type=data.memory_type,
        origin_class=data.origin_class,
        content=data.content,
        context=data.context,
        entities=data.entities,
        tags=data.tags,
        confidence=data.confidence,
        source=data.source,
        event_at=data.event_at,
        retention_policy=data.retention_policy,
        access_restrictions=data.access_restrictions,
        provenance=prov,
    )
    session.add(mem)
    await session.flush()
    mv = MemoryVersion(
        memory_id=mem.memory_id, version=1, operation="create", actor=actor,
        reason="initial store", diff={"created": True},
    )
    session.add(mv)
    await record_audit(
        session, actor=actor, action="memory.store", target_type="memory",
        target_id=mem.memory_id, details={"type": data.memory_type, "origin": data.origin_class},
    )
    await session.commit()
    await session.refresh(mem)
    return mem


async def get_memory(session: AsyncSession, memory_id: str) -> Memory | None:
    res = await session.execute(select(Memory).where(Memory.memory_id == memory_id))
    return res.scalar_one_or_none()


async def retrieve_memories(
    session: AsyncSession,
    identity_id: str,
    memory_type: str | None = None,
    origin_class: str | None = None,
    tags: list[str] | None = None,
    min_confidence: float = 0.0,
    include_deleted: bool = False,
    limit: int = 50,
) -> list[Memory]:
    stmt = select(Memory).where(Memory.identity_id == identity_id)
    if not include_deleted:
        stmt = stmt.where(Memory.is_deleted.is_(False))
    if memory_type:
        stmt = stmt.where(Memory.memory_type == memory_type)
    if origin_class:
        stmt = stmt.where(Memory.origin_class == origin_class)
    if min_confidence > 0:
        stmt = stmt.where(Memory.confidence >= min_confidence)
    stmt = stmt.order_by(Memory.created_at.desc()).limit(limit)
    res = await session.execute(stmt)
    items = list(res.scalars().all())
    if tags:
        tagset = set(tags)
        items = [m for m in items if tagset.issubset(set(m.tags or []))]
    return items


async def correct_memory(
    session: AsyncSession, memory_id: str, data: MemoryCorrect, actor: str = "owner"
) -> Memory:
    actor = data.actor or actor
    mem = await get_memory(session, memory_id)
    if mem is None:
        raise ValueError("memory not found")
    if mem.is_deleted:
        raise PermissionError("memory is deleted")
    old_version = mem.version
    new_version = old_version + 1
    diff: dict[str, Any] = {}
    if data.content is not None and data.content != mem.content:
        diff["content"] = {"from": mem.content, "to": data.content}
        mem.content = data.content
    if data.context is not None and data.context != mem.context:
        diff["context"] = {"from": mem.context, "to": data.context}
        mem.context = data.context
    if data.confidence is not None and data.confidence != mem.confidence:
        diff["confidence"] = {"from": mem.confidence, "to": data.confidence}
        mem.confidence = data.confidence

    # create corrected copy as new memory with supersedes link? Spec: correction appends version, retain original.
    # We version in place but record correction history via MemoryVersion. Also create a new memory record? 
    # Per spec: "Memory must support correction without silently rewriting historical records."
    # We keep original content in version diff and append MemoryVersion. Additionally mark original as superseded by new version number.
    mem.version = new_version
    mv = MemoryVersion(
        memory_id=mem.memory_id, version=new_version, operation="correct", actor=actor,
        reason=data.reason, diff=diff,
    )
    session.add(mv)
    # append correction history to provenance
    mem.provenance = list(mem.provenance) + [{
        "operation": "correct", "actor": actor, "reason": data.reason,
        "timestamp": datetime.now(UTC).isoformat(), "diff_keys": list(diff.keys()),
    }]
    await record_audit(
        session, actor=actor, action="memory.correct", target_type="memory",
        target_id=mem.memory_id, details={"from": old_version, "to": new_version},
    )
    await session.commit()
    await session.refresh(mem)
    return mem


async def soft_delete_memory(session: AsyncSession, memory_id: str, actor: str) -> Memory:
    mem = await get_memory(session, memory_id)
    if mem is None:
        raise ValueError("memory not found")
    mem.is_deleted = True
    mem.version += 1
    mv = MemoryVersion(
        memory_id=mem.memory_id, version=mem.version, operation="delete", actor=actor,
        reason="soft delete", diff={"is_deleted": True},
    )
    session.add(mv)
    await record_audit(
        session, actor=actor, action="memory.delete", target_type="memory",
        target_id=mem.memory_id, details={},
    )
    await session.commit()
    await session.refresh(mem)
    return mem


async def propose_consolidation(
    session: AsyncSession, identity_id: str, data: ConsolidationProposalCreate, actor: str
) -> ConsolidationProposal:
    cp = ConsolidationProposal(
        identity_id=identity_id,
        source_memory_ids=data.source_memory_ids,
        proposed_memory=data.proposed_memory,
    )
    session.add(cp)
    await session.flush()
    await record_audit(
        session, actor=actor, action="memory.consolidation.propose", target_type="consolidation",
        target_id=cp.proposal_id, details={"sources": data.source_memory_ids},
    )
    await session.commit()
    await session.refresh(cp)
    return cp


async def decide_consolidation(
    session: AsyncSession, proposal_id: str, approved: bool, decided_by: str, reason: str
) -> ConsolidationProposal:
    res = await session.execute(
        select(ConsolidationProposal).where(ConsolidationProposal.proposal_id == proposal_id)
    )
    cp = res.scalar_one_or_none()
    if cp is None:
        raise ValueError("proposal not found")
    if cp.status != "pending":
        raise ValueError("proposal already decided")
    cp.status = "approved" if approved else "rejected"
    cp.decided_by = decided_by
    cp.decided_at = datetime.now(UTC)
    cp.reason = reason
    # if approved, create a consolidated memory (origin generated) with provenance
    if approved:
        mem = Memory(
            identity_id=cp.identity_id,
            memory_type="semantic",
            origin_class="generated",
            content=cp.proposed_memory,
            context={"consolidated_from": cp.source_memory_ids},
            confidence=0.7,
            source="consolidation",
            provenance=[{"operation": "consolidate", "actor": decided_by,
                        "source_memory_ids": cp.source_memory_ids,
                        "timestamp": datetime.now(UTC).isoformat()}],
        )
        session.add(mem)
    await record_audit(
        session, actor=decided_by, action=f"memory.consolidation.{'approve' if approved else 'reject'}",
        target_type="consolidation", target_id=cp.proposal_id, details={"approved": approved},
    )
    await session.commit()
    await session.refresh(cp)
    return cp


async def list_proposals(session: AsyncSession, identity_id: str) -> list[ConsolidationProposal]:
    res = await session.execute(
        select(ConsolidationProposal)
        .where(ConsolidationProposal.identity_id == identity_id)
        .order_by(ConsolidationProposal.created_at.desc())
    )
    return list(res.scalars().all())
