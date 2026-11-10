# Identity Continuity Spec

## Definition

Identity is a persistent, versioned record independent of any inference provider.
Changing the underlying LLM must not change stored identity, memories, or personal
history.

## Identity identifier

- Globally unique (UUIDv7 recommended for time-ordering).
- Immutable once issued.
- Never reused.

## Identity manifest (authoritative)

- Identity id.
- Created at / created by.
- Ownership & authorization boundaries.
- Current version number (monotonic).
- Profile (structured, versioned).
- Provenance (sources of information).
- Consent record reference.
- Integrity verification (hash of canonical manifest).
- Lineage (parent identity if derivative; derivatives get separate designation).

## Invariants

1. Identity id is immutable.
2. Version increments only via authority.
3. No two authoritative histories for one identity.
4. Derivative instances require explicit lineage + separate designation.
5. An identity identifier does not prove subjective continuity.
6. Avatar change does not create new identity.
7. Avatar deletion does not delete identity.

## Distinctions maintained

- Original person.
- Collected information.
- Computational representation.
- Currently executing instance.
- Replicated infrastructure.
- Independently created derivative representation.

## State transitions (versioned)

Each transition: {from_version, to_version, operation, actor, authorization,
timestamp, diff, reason}. Append-only. Reversible where policy allows.

## Migration

Source/destination verification, transfer authorization, integrity verification,
recovery, completion record. Fencing prevents stale source writes.

## Integrity verification

Canonical serialization + hash; recompute on load; mismatch => quarantine + alert.
Periodic re-verification; on restore from checkpoint.

## Continuity record

Tracks: checkpoints, migrations, restorations, suspensions, resumptions, archival,
erasure events. Links to audit log.

## What identity is NOT

- Not an LLM prompt.
- Not a bundle of personality traits.
- Not a behavioural benchmark score.
- Not subjective continuity proof.
