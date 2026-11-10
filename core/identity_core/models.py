"""SQLAlchemy models for the identity core."""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from storage.database import Base


def _now() -> datetime:
    return datetime.now(UTC)


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    username: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(256))
    role: Mapped[str] = mapped_column(String(32), default="owner")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)


class Identity(Base):
    __tablename__ = "identities"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), unique=True, index=True, default=_uuid)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="created", index=True)
    owner_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    manifest_hash: Mapped[str] = mapped_column(String(128), default="")
    lineage_parent_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    is_derivative: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    profile: Mapped[Profile | None] = relationship(back_populates="identity", uselist=False, cascade="all, delete-orphan")
    versions: Mapped[list[IdentityVersion]] = relationship(back_populates="identity", cascade="all, delete-orphan")
    consent_records: Mapped[list[ConsentRecord]] = relationship(back_populates="identity", cascade="all, delete-orphan")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), unique=True, index=True)
    data: Mapped[dict] = mapped_column(JSON, default=dict)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    identity: Mapped[Identity] = relationship(back_populates="profile")


class IdentityVersion(Base):
    __tablename__ = "identity_versions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    from_version: Mapped[int] = mapped_column(Integer)
    to_version: Mapped[int] = mapped_column(Integer)
    operation: Mapped[str] = mapped_column(String(64))
    actor: Mapped[str] = mapped_column(String(128))
    authorization: Mapped[str] = mapped_column(String(128), default="")
    reason: Mapped[str] = mapped_column(Text, default="")
    diff: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)

    identity: Mapped[Identity] = relationship(back_populates="versions")


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    scope: Mapped[str] = mapped_column(String(128))
    granted_by: Mapped[str] = mapped_column(String(128))
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)

    identity: Mapped[Identity] = relationship(back_populates="consent_records")


class AuditLog(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    actor: Mapped[str] = mapped_column(String(128))
    action: Mapped[str] = mapped_column(String(128), index=True)
    target_type: Mapped[str] = mapped_column(String(64))
    target_id: Mapped[str] = mapped_column(String(64), index=True)
    details: Mapped[dict] = mapped_column(JSON, default=dict)
    prev_hash: Mapped[str] = mapped_column(String(128), default="")
    hash: Mapped[str] = mapped_column(String(128), default="")


class ProvenanceRecord(Base):
    __tablename__ = "provenance_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    identity_id: Mapped[str] = mapped_column(String(36), ForeignKey("identities.identity_id"), index=True)
    kind: Mapped[str] = mapped_column(String(64))
    source: Mapped[str] = mapped_column(String(256))
    operation: Mapped[str] = mapped_column(String(128))
    actor: Mapped[str] = mapped_column(String(128))
    input_refs: Mapped[list] = mapped_column(JSON, default=list)
    output_ref: Mapped[str] = mapped_column(String(128), default="")
    confidence: Mapped[float] = mapped_column(default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, index=True)
    meta: Mapped[dict] = mapped_column("metadata", JSON, default=dict)
