"""Personality models."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from storage.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


class PersonalityProfile(Base):
    __tablename__ = "personality_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    profile_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), unique=True, index=True)
    stable_traits: Mapped[dict] = mapped_column(JSON, default=dict)
    adaptable_tendencies: Mapped[dict] = mapped_column(JSON, default=dict)
    behavioral_patterns: Mapped[dict] = mapped_column(JSON, default=dict)
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)
