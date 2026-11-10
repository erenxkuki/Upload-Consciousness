"""Lifecycle states for digital existence."""
from __future__ import annotations

from enum import Enum


class LifecycleState(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    RESTORATION_PENDING = "restoration_pending"
    RESTORED = "restored"
    DELETION_REQUESTED = "deletion_requested"
    DELETION_PROCESSING = "deletion_processing"
    DELETED = "deleted"


ALLOWED_TRANSITIONS: dict[LifecycleState, set[LifecycleState]] = {
    LifecycleState.CREATED: {LifecycleState.ACTIVE},
    LifecycleState.ACTIVE: {LifecycleState.SUSPENDED, LifecycleState.ARCHIVED, LifecycleState.DELETION_REQUESTED},
    LifecycleState.SUSPENDED: {LifecycleState.ACTIVE, LifecycleState.ARCHIVED, LifecycleState.DELETION_REQUESTED},
    LifecycleState.ARCHIVED: {LifecycleState.RESTORATION_PENDING, LifecycleState.DELETION_REQUESTED},
    LifecycleState.RESTORATION_PENDING: {LifecycleState.RESTORED, LifecycleState.SUSPENDED},
    LifecycleState.RESTORED: {LifecycleState.ACTIVE},
    LifecycleState.DELETION_REQUESTED: {LifecycleState.DELETION_PROCESSING},
    LifecycleState.DELETION_PROCESSING: {LifecycleState.DELETED},
    LifecycleState.DELETED: set(),
}


def can_transition(src: LifecycleState, dst: LifecycleState) -> bool:
    return dst in ALLOWED_TRANSITIONS.get(src, set())
