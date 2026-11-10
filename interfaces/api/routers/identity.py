"""Identity router."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from autonomy.lifecycle.states import LifecycleState
from core.identity_core import service
from core.identity_core.schemas import (
    ConsentCreate,
    ConsentRead,
    IdentityCreate,
    IdentityRead,
    IdentityUpdate,
    IdentityVersionRead,
    IntegrityResult,
)
from storage.database import get_session

router = APIRouter(prefix="/identity", tags=["identity"])


def _to_read(identity) -> IdentityRead:
    profile = identity.profile.data if identity.profile else None
    return IdentityRead(
        identity_id=identity.identity_id,
        version=identity.version,
        status=identity.status,
        owner_user_id=identity.owner_user_id,
        manifest_hash=identity.manifest_hash,
        is_derivative=identity.is_derivative,
        lineage_parent_id=identity.lineage_parent_id,
        created_at=identity.created_at,
        updated_at=identity.updated_at,
        profile=profile,
    )


@router.post("", response_model=IdentityRead)
async def create_identity(payload: IdentityCreate, session: AsyncSession = Depends(get_session)) -> IdentityRead:
    identity = await service.create_identity(session, payload)
    return _to_read(identity)


@router.get("/{identity_id}", response_model=IdentityRead)
async def get_identity(identity_id: str, session: AsyncSession = Depends(get_session)) -> IdentityRead:
    identity = await service.get_identity(session, identity_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="identity not found")
    return _to_read(identity)


@router.patch("/{identity_id}", response_model=IdentityRead)
async def update_identity(
    identity_id: str, payload: IdentityUpdate, session: AsyncSession = Depends(get_session)
) -> IdentityRead:
    try:
        identity = await service.update_identity(session, identity_id, payload, actor=payload.actor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    return _to_read(identity)


@router.get("/{identity_id}/versions", response_model=list[IdentityVersionRead])
async def list_versions(identity_id: str, session: AsyncSession = Depends(get_session)) -> list[IdentityVersionRead]:
    identity = await service.get_identity(session, identity_id)
    if identity is None:
        raise HTTPException(status_code=404, detail="identity not found")
    versions = await service.list_versions(session, identity_id)
    return [
        IdentityVersionRead(
            id=v.id,
            from_version=v.from_version,
            to_version=v.to_version,
            operation=v.operation,
            actor=v.actor,
            authorization=v.authorization,
            reason=v.reason,
            diff=v.diff,
            created_at=v.created_at,
        )
        for v in versions
    ]


@router.get("/{identity_id}/integrity", response_model=IntegrityResult)
async def integrity(identity_id: str, session: AsyncSession = Depends(get_session)) -> IntegrityResult:
    try:
        return await service.verify_integrity(session, identity_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{identity_id}/lifecycle", response_model=IdentityRead)
async def lifecycle(
    identity_id: str, new_state: str, actor: str = "owner", authorization: str = "",
    session: AsyncSession = Depends(get_session),
) -> IdentityRead:
    try:
        ls = LifecycleState(new_state)
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid state")
    try:
        identity = await service.transition_lifecycle(session, identity_id, ls, actor=actor, authorization=authorization)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _to_read(identity)


@router.post("/{identity_id}/consent", response_model=ConsentRead)
async def grant_consent(
    identity_id: str, payload: ConsentCreate, session: AsyncSession = Depends(get_session)
) -> ConsentRead:
    try:
        cr = await service.create_consent(session, identity_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ConsentRead(
        id=cr.id, scope=cr.scope, granted_by=cr.granted_by,
        granted_at=cr.granted_at, revoked_at=cr.revoked_at, details=cr.details,
    )


@router.post("/consent/{consent_id}/revoke", response_model=ConsentRead)
async def revoke_consent(consent_id: str, actor: str = "owner", session: AsyncSession = Depends(get_session)) -> ConsentRead:
    try:
        cr = await service.revoke_consent(session, consent_id, actor=actor)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return ConsentRead(
        id=cr.id, scope=cr.scope, granted_by=cr.granted_by,
        granted_at=cr.granted_at, revoked_at=cr.revoked_at, details=cr.details,
    )
