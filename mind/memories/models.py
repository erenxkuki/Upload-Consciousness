"""Memory models."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from storage.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


class Memory(Base):
    __tablename__ = "memories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    memory_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    memory_type: Mapped[str] = mapped_column(String(32), index=True)  # episodic/semantic/procedural/autobiographical
    origin_class: Mapped[str] = mapped_column(String(32), index=True)  # actual_experience/imported/generated/uncertain
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    entities: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[str] = mapped_column(String(256), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    event_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    supersedes: Mapped[str | None] = mapped_column(String(36), nullable=True)
    retention_policy: Mapped[str] = mapped_column(String(64), default="standard")
    access_restrictions: Mapped[dict] = mapped_column(JSON, default=dict)
    is_deleted: Mapped[bool] = mapped_column(default=False, index=True)
    provenance: Mapped[list] = mapped_column(JSON, default=list)


class MemoryVersion(Base):
    __tablename__ = "memory_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    memory_id: Mapped[str] = mapped_column(String(36), ForeignKey("memories.memory_id"), index=True)
    version: Mapped[int] = mapped_column(Integer)
    operation: Mapped[str] = mapped_column(String(64))
    actor: Mapped[str] = mapped_column(String(128))
    reason: Mapped[str] = mapped_column(Text, default="")
    diff: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class Experience(Base):
    __tablename__ = "experiences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    experience_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    source: Mapped[str] = mapped_column(String(256), default="")
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    processed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class ConsolidationProposal(Base):
    __tablename__ = "consolidation_proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    proposal_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    source_memory_ids: Mapped[list] = mapped_column(JSON, default=list)
    proposed_memory: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(32), default="pending")  # pending/approved/rejected
    decided_by: Mapped[str | None] = mapped_column(String(128), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
