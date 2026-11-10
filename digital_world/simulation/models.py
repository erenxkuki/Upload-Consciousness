"""Digital world models."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from storage.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


class Environment(Base):
    __tablename__ = "environments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    environment_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    name: Mapped[str] = mapped_column(String(128))
    env_type: Mapped[str] = mapped_column(String(32), default="indoor")  # indoor/outdoor/custom
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class WorldPresence(Base):
    __tablename__ = "world_presences"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    presence_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    avatar_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    environment_id: Mapped[str] = mapped_column(String(36), ForeignKey("environments.environment_id"), index=True)
    position: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)


class SocialMessage(Base):
    __tablename__ = "social_messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    message_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    sender_identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    recipient_identity_id: Mapped[str | None] = mapped_column(String(36), nullable=True, index=True)
    environment_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)


class GovernanceRule(Base):
    __tablename__ = "governance_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    rule_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    environment_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    rule_type: Mapped[str] = mapped_column(String(64))
    description: Mapped[str] = mapped_column(Text, default="")
    consent_required: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
