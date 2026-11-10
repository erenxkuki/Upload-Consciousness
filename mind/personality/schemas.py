"""Personality schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class PersonalityUpdate(BaseModel):
    stable_traits: dict[str, Any] | None = None
    adaptable_tendencies: dict[str, Any] | None = None
    behavioral_patterns: dict[str, Any] | None = None
    preferences: dict[str, Any] | None = None
    reason: str = "update"
    actor: str = "owner"


class PersonalityRead(BaseModel):
    profile_id: str
    identity_id: str
    stable_traits: dict[str, Any]
    adaptable_tendencies: dict[str, Any]
    behavioral_patterns: dict[str, Any]
    preferences: dict[str, Any]
    version: int
    updated_at: datetime
