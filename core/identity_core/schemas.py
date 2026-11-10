"""Pydantic schemas for identity core."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ProfileData(BaseModel):
    display_name: str | None = None
    bio: str | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)
    traits: dict[str, Any] = Field(default_factory=dict)
    extra: dict[str, Any] = Field(default_factory=dict)


class IdentityCreate(BaseModel):
    display_name: str | None = None
    owner_user_id: str | None = None
    initial_profile: ProfileData | None = None
    consent_scope: str = "identity.create"
    granted_by: str = "system"


class IdentityUpdate(BaseModel):
    profile: ProfileData | None = None
    reason: str = "authorized update"
    actor: str = "owner"


class IdentityRead(BaseModel):
    identity_id: str
    version: int
    status: str
    owner_user_id: str | None
    manifest_hash: str
    is_derivative: bool
    lineage_parent_id: str | None
    created_at: datetime
    updated_at: datetime
    profile: dict[str, Any] | None = None


class IdentityVersionRead(BaseModel):
    id: str
    from_version: int
    to_version: int
    operation: str
    actor: str
    authorization: str
    reason: str
    diff: dict[str, Any]
    created_at: datetime


class ConsentCreate(BaseModel):
    scope: str
    granted_by: str
    details: dict[str, Any] = Field(default_factory=dict)


class ConsentRead(BaseModel):
    id: str
    scope: str
    granted_by: str
    granted_at: datetime
    revoked_at: datetime | None
    details: dict[str, Any]


class IntegrityResult(BaseModel):
    identity_id: str
    version: int
    manifest_hash: str
    recomputed_hash: str
    intact: bool
