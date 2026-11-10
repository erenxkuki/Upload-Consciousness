"""Memory schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ExperienceCreate(BaseModel):
    content: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    source: str = ""
    occurred_at: datetime | None = None


class MemoryCreate(BaseModel):
    memory_type: str  # episodic/semantic/procedural/autobiographical
    origin_class: str = "actual_experience"  # actual_experience/imported/generated/uncertain
    content: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    entities: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    confidence: float = 1.0
    source: str = ""
    event_at: datetime | None = None
    retention_policy: str = "standard"
    access_restrictions: dict[str, Any] = Field(default_factory=dict)
    provenance: list[dict[str, Any]] = Field(default_factory=list)


class MemoryCorrect(BaseModel):
    content: dict[str, Any] | None = None
    context: dict[str, Any] | None = None
    confidence: float | None = None
    reason: str = "correction"
    actor: str = "owner"


class MemoryRead(BaseModel):
    memory_id: str
    identity_id: str
    memory_type: str
    origin_class: str
    content: dict[str, Any]
    context: dict[str, Any]
    entities: list[str]
    tags: list[str]
    confidence: float
    source: str
    created_at: datetime
    event_at: datetime | None
    version: int
    supersedes: str | None
    retention_policy: str
    access_restrictions: dict[str, Any]
    is_deleted: bool
    provenance: list[Any]


class ConsolidationProposalCreate(BaseModel):
    source_memory_ids: list[str] = Field(default_factory=list)
    proposed_memory: dict[str, Any] = Field(default_factory=dict)
    reason: str = ""


class ConsolidationDecision(BaseModel):
    approved: bool
    decided_by: str = "owner"
    reason: str = ""
