"""Identity core service: authoritative identity operations."""
from __future__ import annotations

from datetime import UTC
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from autonomy.lifecycle.states import LifecycleState, can_transition
from core.identity_core.integrity import canonical_hash, manifest_payload
from core.identity_core.models import (
    ConsentRecord,
    Identity,
    IdentityVersion,
    Profile,
    ProvenanceRecord,
)
from core.identity_core.schemas import (
    ConsentCreate,
    IdentityCreate,
    IdentityUpdate,
    ProfileData,
)
from security.auditing.audit import record_audit


async def _next_version(identity: Identity) -> int:
    return identity.version + 1


async def create_identity(session: AsyncSession, data: IdentityCreate, actor: str = "system") -> Identity:
    identity = Identity(
        owner_user_id=data.owner_user_id,
        status=LifecycleState.CREATED.value,
    )
    session.add(identity)
    await session.flush()

    profile_data = (data.initial_profile or ProfileData()).model_dump()
    profile = Profile(identity_id=identity.identity_id, data=profile_data, version=1)
    session.add(profile)
    await session.flush()

    identity.version = 1
    identity.manifest_hash = canonical_hash(
        manifest_payload(identity.identity_id, identity.version, identity.status, profile_data)
    )

    # version record
    iv = IdentityVersion(
        identity_id=identity.identity_id,
        from_version=0,
        to_version=1,
        operation="create",
        actor=actor,
        authorization=data.consent_scope,
        reason="initial creation",
        diff={"created": True},
    )
    session.add(iv)

    # consent record
    cr = ConsentRecord(
        identity_id=identity.identity_id,
        scope=data.consent_scope,
        granted_by=data.granted_by,
        details={"initial": True},
    )
    session.add(cr)

    # provenance
    pr = ProvenanceRecord(
        identity_id=identity.identity_id,
        kind="identity",
        source="input",
        operation="create",
        actor=actor,
        input_refs=[],
        output_ref=identity.identity_id,
        confidence=1.0,
        meta={"consent_scope": data.consent_scope},
    )
    session.add(pr)

    await record_audit(
        session, actor=actor, action="identity.create", target_type="identity",
        target_id=identity.identity_id, details={"version": 1},
    )
    await session.commit()
    # reload with relationships
    identity = await get_identity(session, identity.identity_id)
    return identity  # type: ignore[return-value]


async def get_identity(session: AsyncSession, identity_id: str) -> Identity | None:
    res = await session.execute(
        select(Identity)
        .options(selectinload(Identity.profile))
        .where(Identity.identity_id == identity_id)
    )
    return res.scalar_one_or_none()


async def update_identity(
    session: AsyncSession, identity_id: str, update: IdentityUpdate, actor: str, authorization: str = ""
) -> Identity:
    identity = await get_identity(session, identity_id)
    if identity is None:
        raise ValueError("identity not found")
    if identity.status in (LifecycleState.DELETED.value, LifecycleState.DELETION_PROCESSING.value):
        raise PermissionError("identity is deleted or being deleted")

    old_version = identity.version
    new_version = old_version + 1

    profile = identity.profile
    old_profile_data = dict(profile.data) if profile else {}
    new_profile_data = old_profile_data
    if update.profile is not None:
        new_profile_data = update.profile.model_dump()

    diff: dict[str, Any] = {}
    if new_profile_data != old_profile_data:
        diff["profile"] = {"from": old_profile_data, "to": new_profile_data}

    if profile is None:
        profile = Profile(identity_id=identity.identity_id, data=new_profile_data, version=new_version)
        session.add(profile)
    else:
        profile.data = new_profile_data
        profile.version = new_version

    identity.version = new_version
    identity.manifest_hash = canonical_hash(
        manifest_payload(identity.identity_id, identity.version, identity.status, new_profile_data)
    )

    iv = IdentityVersion(
        identity_id=identity.identity_id,
        from_version=old_version,
        to_version=new_version,
        operation="update",
        actor=actor,
        authorization=authorization,
        reason=update.reason,
        diff=diff,
    )
    session.add(iv)

    pr = ProvenanceRecord(
        identity_id=identity.identity_id,
        kind="identity",
        source="input",
        operation="update",
        actor=actor,
        input_refs=[],
        output_ref=identity.identity_id,
        confidence=1.0,
        meta={"reason": update.reason, "diff_keys": list(diff.keys())},
    )
    session.add(pr)

    await record_audit(
        session, actor=actor, action="identity.update", target_type="identity",
        target_id=identity.identity_id, details={"from": old_version, "to": new_version},
    )
    await session.commit()
    identity = await get_identity(session, identity_id)
    return identity  # type: ignore[return-value]


async def transition_lifecycle(
    session: AsyncSession, identity_id: str, new_state: LifecycleState, actor: str, authorization: str = ""
) -> Identity:
    identity = await get_identity(session, identity_id)
    if identity is None:
        raise ValueError("identity not found")
    current = LifecycleState(identity.status)
    if not can_transition(current, new_state):
        raise ValueError(f"illegal transition {current.value} -> {new_state.value}")
    old_version = identity.version
    new_version = old_version + 1
    identity.status = new_state.value
    identity.version = new_version
    identity.manifest_hash = canonical_hash(
        manifest_payload(identity.identity_id, identity.version, identity.status,
                        identity.profile.data if identity.profile else {})
    )
    iv = IdentityVersion(
        identity_id=identity.identity_id,
        from_version=old_version,
        to_version=new_version,
        operation=f"lifecycle:{new_state.value}",
        actor=actor,
        authorization=authorization,
        reason=f"lifecycle transition to {new_state.value}",
        diff={"status": {"from": current.value, "to": new_state.value}},
    )
    session.add(iv)
    await record_audit(
        session, actor=actor, action=f"identity.lifecycle.{new_state.value}",
        target_type="identity", target_id=identity.identity_id,
        details={"from": current.value, "to": new_state.value},
    )
    await session.commit()
    identity = await get_identity(session, identity_id)
    return identity  # type: ignore[return-value]


async def verify_integrity(session: AsyncSession, identity_id: str) -> Any:
    from core.identity_core.schemas import IntegrityResult

    identity = await get_identity(session, identity_id)
    if identity is None:
        raise ValueError("identity not found")
    profile_data = identity.profile.data if identity.profile else {}
    recomputed = canonical_hash(
        manifest_payload(identity.identity_id, identity.version, identity.status, profile_data)
    )
    return IntegrityResult(
        identity_id=identity.identity_id,
        version=identity.version,
        manifest_hash=identity.manifest_hash,
        recomputed_hash=recomputed,
        intact=(identity.manifest_hash == recomputed),
    )


async def list_versions(session: AsyncSession, identity_id: str) -> list[IdentityVersion]:
    res = await session.execute(
        select(IdentityVersion)
        .where(IdentityVersion.identity_id == identity_id)
        .order_by(IdentityVersion.created_at.asc())
    )
    return list(res.scalars().all())


async def create_consent(session: AsyncSession, identity_id: str, consent: ConsentCreate) -> ConsentRecord:
    identity = await get_identity(session, identity_id)
    if identity is None:
        raise ValueError("identity not found")
    cr = ConsentRecord(
        identity_id=identity_id,
        scope=consent.scope,
        granted_by=consent.granted_by,
        details=consent.details,
    )
    session.add(cr)
    await record_audit(
        session, actor=consent.granted_by, action="consent.grant", target_type="identity",
        target_id=identity_id, details={"scope": consent.scope},
    )
    await session.commit()
    await session.refresh(cr)
    return cr


async def revoke_consent(session: AsyncSession, consent_id: str, actor: str) -> ConsentRecord:
    res = await session.execute(select(ConsentRecord).where(ConsentRecord.id == consent_id))
    cr = res.scalar_one_or_none()
    if cr is None:
        raise ValueError("consent not found")
    if cr.revoked_at is None:
        from datetime import datetime

        cr.revoked_at = datetime.now(UTC)
    await record_audit(
        session, actor=actor, action="consent.revoke", target_type="consent",
        target_id=consent_id, details={"scope": cr.scope},
    )
    await session.commit()
    await session.refresh(cr)
    return cr
