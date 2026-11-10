"""Embodiment models."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from storage.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


class Avatar(Base):
    __tablename__ = "avatars"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    avatar_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    name: Mapped[str] = mapped_column(String(128), default="")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    capabilities: Mapped[list] = mapped_column(JSON, default=list)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class MovementIntent(Base):
    __tablename__ = "movement_intents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    intent_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    avatar_id: Mapped[str] = mapped_column(String(36), ForeignKey("avatars.avatar_id"), index=True)
    intent: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class PerceptionEvent(Base):
    __tablename__ = "perception_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    event_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    avatar_id: Mapped[str] = mapped_column(String(36), ForeignKey("avatars.avatar_id"), index=True)
    modality: Mapped[str] = mapped_column(String(32))
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    source: Mapped[str] = mapped_column(String(128), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Expression(Base):
    __tablename__ = "expressions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    expression_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    avatar_id: Mapped[str] = mapped_column(String(36), ForeignKey("avatars.avatar_id"), index=True)
    expression_type: Mapped[str] = mapped_column(String(64))
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
