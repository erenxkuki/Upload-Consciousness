"""Distributed continuity service."""
from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.identity_core import service as identity_service
from core.identity_core.integrity import canonical_hash
from distributed.nodes.models import Checkpoint, MigrationRecord, Node, Task
from security.auditing.audit import record_audit

# ---- Nodes ----

async def register_node(session: AsyncSession, node_id: str, role: str = "cognitive",
                        capabilities: list[str] | None = None, resources: dict | None = None) -> Node:
    res = await session.execute(select(Node).where(Node.node_id == node_id))
    node = res.scalar_one_or_none()
    if node is None:
        node = Node(node_id=node_id, role=role, capabilities=capabilities or [],
                    resources=resources or {}, status="healthy")
        session.add(node)
    else:
        node.role = role
        node.capabilities = capabilities or node.capabilities
        node.resources = resources or node.resources
        node.status = "healthy"
        node.last_heartbeat = datetime.now(UTC)
    await session.commit()
    await session.refresh(node)
    return node


async def heartbeat(session: AsyncSession, node_id: str, resources: dict | None = None) -> Node:
    res = await session.execute(select(Node).where(Node.node_id == node_id))
    node = res.scalar_one_or_none()
    if node is None:
        raise ValueError("node not registered")
    node.last_heartbeat = datetime.now(UTC)
    node.status = "healthy"
    if resources:
        node.resources = resources
    await session.commit()
    await session.refresh(node)
    return node


async def list_nodes(session: AsyncSession, role: str | None = None) -> list[Node]:
    stmt = select(Node)
    if role:
        stmt = stmt.where(Node.role == role)
    res = await session.execute(stmt)
    return list(res.scalars().all())


async def mark_node_down(session: AsyncSession, node_id: str) -> Node:
    res = await session.execute(select(Node).where(Node.node_id == node_id))
    node = res.scalar_one_or_none()
    if node is None:
        raise ValueError("node not found")
    node.status = "down"
    await session.commit()
    await session.refresh(node)
    return node


# ---- Task scheduling ----

async def schedule_task(session: AsyncSession, identity_id: str | None, kind: str, payload: dict,
                       idempotency_key: str = "", preferred_role: str = "cognitive") -> Task:
    # idempotency
    if idempotency_key:
        res = await session.execute(select(Task).where(Task.idempotency_key == idempotency_key))
        existing = res.scalar_one_or_none()
        if existing is not None:
            return existing
    # pick healthy node
    nodes = await list_nodes(session, role=preferred_role)
    healthy = [n for n in nodes if n.status == "healthy"]
    chosen = healthy[0].node_id if healthy else None
    task = Task(identity_id=identity_id, node_id=chosen, kind=kind, payload=payload,
                idempotency_key=idempotency_key, status="scheduled" if chosen else "queued")
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def complete_task(session: AsyncSession, task_id: str) -> Task:
    res = await session.execute(select(Task).where(Task.task_id == task_id))
    task = res.scalar_one_or_none()
    if task is None:
        raise ValueError("task not found")
    task.status = "completed"
    task.completed_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(task)
    return task


# ---- Checkpoints ----

async def create_checkpoint(session: AsyncSession, identity_id: str, node_id: str, actor: str = "system") -> Checkpoint:
    identity = await identity_service.get_identity(session, identity_id)
    if identity is None:
        raise ValueError("identity not found")
    profile_data = identity.profile.data if identity.profile else {}
    snapshot = {
        "identity_id": identity.identity_id,
        "version": identity.version,
        "status": identity.status,
        "profile": profile_data,
        "checkpointed_at": datetime.now(UTC).isoformat(),
    }
    h = canonical_hash(snapshot)
    cp = Checkpoint(
        identity_id=identity_id, node_id=node_id, identity_version=identity.version,
        snapshot=snapshot, snapshot_hash=h, verified=True,
    )
    session.add(cp)
    await session.flush()
    await record_audit(session, actor=actor, action="continuity.checkpoint", target_type="checkpoint",
                      target_id=cp.checkpoint_id, details={"identity_id": identity_id, "version": identity.version})
    await session.commit()
    await session.refresh(cp)
    return cp


async def verify_checkpoint(session: AsyncSession, checkpoint_id: str) -> Checkpoint:
    res = await session.execute(select(Checkpoint).where(Checkpoint.checkpoint_id == checkpoint_id))
    cp = res.scalar_one_or_none()
    if cp is None:
        raise ValueError("checkpoint not found")
    recomputed = canonical_hash(cp.snapshot)
    cp.verified = (recomputed == cp.snapshot_hash)
    await session.commit()
    await session.refresh(cp)
    return cp


async def latest_checkpoint(session: AsyncSession, identity_id: str) -> Checkpoint | None:
    res = await session.execute(
        select(Checkpoint).where(Checkpoint.identity_id == identity_id)
        .order_by(Checkpoint.created_at.desc()).limit(1)
    )
    return res.scalar_one_or_none()


# ---- Migration ----

async def migrate_identity(session: AsyncSession, identity_id: str, source_node: str, dest_node: str,
                          actor: str = "system") -> MigrationRecord:
    # verify source node exists & healthy? allow
    mr = MigrationRecord(identity_id=identity_id, source_node=source_node, dest_node=dest_node, status="in_progress")
    session.add(mr)
    await session.flush()

    # create checkpoint on source
    cp = await create_checkpoint(session, identity_id, source_node, actor=actor)

    # verify checkpoint
    await verify_checkpoint(session, cp.checkpoint_id)

    # mark migration complete with integrity
    mr.status = "completed"
    mr.integrity_verified = cp.verified
    mr.completed_at = datetime.now(UTC)
    mr.details = {"checkpoint_id": cp.checkpoint_id, "identity_version": cp.identity_version}

    await record_audit(session, actor=actor, action="continuity.migrate", target_type="migration",
                      target_id=mr.migration_id, details={"source": source_node, "dest": dest_node,
                                                          "integrity": cp.verified})
    await session.commit()
    await session.refresh(mr)
    return mr


# ---- Recovery ----

async def recover_identity_state(session: AsyncSession, identity_id: str, checkpoint_id: str | None = None,
                                actor: str = "system") -> dict[str, Any]:
    cp = None
    if checkpoint_id:
        res = await session.execute(select(Checkpoint).where(Checkpoint.checkpoint_id == checkpoint_id))
        cp = res.scalar_one_or_none()
    else:
        cp = await latest_checkpoint(session, identity_id)
    if cp is None:
        raise ValueError("no checkpoint available")
    await verify_checkpoint(session, cp.checkpoint_id)
    if not cp.verified:
        raise ValueError("checkpoint integrity verification failed")
    await record_audit(session, actor=actor, action="continuity.recover", target_type="checkpoint",
                      target_id=cp.checkpoint_id, details={"identity_id": identity_id})
    return {"identity_id": identity_id, "checkpoint_id": cp.checkpoint_id,
            "identity_version": cp.identity_version, "snapshot": cp.snapshot, "verified": cp.verified}


# ---- Consistency / conflict detection ----

async def detect_conflicts(session: AsyncSession, identity_id: str) -> dict[str, Any]:
    # compare latest checkpoint version vs identity version
    identity = await identity_service.get_identity(session, identity_id)
    cp = await latest_checkpoint(session, identity_id)
    conflicts = []
    if identity and cp and cp.identity_version != identity.version:
        conflicts.append({
            "type": "version_mismatch",
            "checkpoint_version": cp.identity_version,
            "identity_version": identity.version,
        })
    return {"identity_id": identity_id, "conflicts": conflicts, "has_conflicts": bool(conflicts)}
