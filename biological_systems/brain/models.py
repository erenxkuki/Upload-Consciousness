"""Brain / cognitive core models."""
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


class SelfModel(Base):
    __tablename__ = "self_models"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), unique=True, index=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class WorkingMemorySnapshot(Base):
    __tablename__ = "working_memory_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), unique=True, index=True)
    entries: Mapped[list] = mapped_column(JSON, default=list)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class Reflection(Base):
    __tablename__ = "reflections"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    reflection_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    kind: Mapped[str] = mapped_column(String(64))
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class DecisionRecord(Base):
    __tablename__ = "decision_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    decision_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    options: Mapped[list] = mapped_column(JSON, default=list)
    chosen: Mapped[str] = mapped_column(String(256), default="")
    rationale: Mapped[str] = mapped_column(Text, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    context: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class Goal(Base):
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    goal_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(32), default="active")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
