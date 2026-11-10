"""Integrity verification helpers for identity manifests."""
from __future__ import annotations

import hashlib
import json
from typing import Any


def canonical_hash(payload: dict[str, Any]) -> str:
    """Deterministic SHA-256 over a JSON payload."""
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def manifest_payload(identity_id: str, version: int, status: str, profile: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "identity_id": identity_id,
        "version": version,
        "status": status,
        "profile": profile or {},
    }
