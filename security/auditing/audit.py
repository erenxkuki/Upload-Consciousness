"""Append-only, hash-chained audit log."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from core.identity_core.models import AuditLog


async def record_audit(
    session: AsyncSession,
    actor: str,
    action: str,
    target_type: str,
    target_id: str,
    details: dict[str, Any] | None = None,
) -> AuditLog:
    details = details or {}
    # fetch last hash
    from sqlalchemy import select

    res = await session.execute(
        select(AuditLog.hash).order_by(AuditLog.timestamp.desc()).limit(1)
    )
    last = res.scalar_one_or_none() or ""
    payload = {
        "actor": actor,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "details": details,
        "prev_hash": last,
    }
    blob = json.dumps(payload, sort_keys=True, default=str)
    h = hashlib.sha256((last + blob).encode("utf-8")).hexdigest()
    entry = AuditLog(
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
        prev_hash=last,
        hash=h,
    )
    session.add(entry)
    await session.flush()
    return entry
