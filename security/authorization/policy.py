"""Authorization policy helpers."""
from __future__ import annotations

ROLE_RANK = {"system": 4, "owner": 3, "custodian": 2, "researcher": 1, "guest": 0}


def has_role(user_role: str, required: str) -> bool:
    return ROLE_RANK.get(user_role, 0) >= ROLE_RANK.get(required, 0)


def can_modify_identity(user_role: str, is_owner: bool) -> bool:
    if user_role in ("system", "owner"):
        return True
    return bool(is_owner)
