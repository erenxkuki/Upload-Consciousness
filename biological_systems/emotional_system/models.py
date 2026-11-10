"""Emotional system models."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from storage.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


class EmotionalState(Base):
    __tablename__ = "emotional_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    state_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), unique=True, index=True)
    dimensions: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class EmotionalHistory(Base):
    __tablename__ = "emotional_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    trigger: Mapped[str] = mapped_column(String(256), default="")
    source_ref: Mapped[str] = mapped_column(String(128), default="")
    deltas: Mapped[dict] = mapped_column(JSON, default=dict)
    policy: Mapped[str] = mapped_column(String(64), default="experience_update")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    resulting_dimensions: Mapped[dict] = mapped_column(JSON, default=dict)
