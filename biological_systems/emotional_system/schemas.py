"""Emotional system schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EmotionalDimensions(BaseModel):
    valence: float = 0.0
    arousal: float = 0.0
    dominance: float = 0.0
    intensity: float = 0.0
    persistence: float = 0.0
    context: str = ""
    triggering_experience: str = ""
    confidence: float = 1.0
    duration: float = 0.0
    recovery_dynamics: float = 0.5


class EmotionalUpdate(BaseModel):
    dimensions: dict[str, Any] = Field(default_factory=dict)
    trigger: str = ""
    source_ref: str = ""
    policy: str = "experience_update"
    actor: str = "system"


class EmotionalStateRead(BaseModel):
    state_id: str
    identity_id: str
    dimensions: dict[str, Any]
    version: int
    updated_at: datetime


class EmotionalHistoryRead(BaseModel):
    id: str
    timestamp: datetime
    trigger: str
    source_ref: str
    deltas: dict[str, Any]
    policy: str
    confidence: float
    resulting_dimensions: dict[str, Any]
