# Distributed Mind Architecture

## Foundational decision

**Do not distribute identity ownership itself.** Distribute computation, storage
and execution while maintaining authoritative identity and state-transition rules.

Otherwise a network partition can result in two machines independently evolving
contradictory versions of the same digital identity — the hardest problem of the
hybrid architecture.

## Authority model

- One logical **identity authority** per identity, elected via lease (e.g. a
  coordination service or DB-backed lease).
- All state transitions (version increments, authorization decisions, destructive
  lifecycle) are validated and recorded by the authority.
- Cognitive/memory nodes propose updates; the authority commits or rejects.
- Fencing tokens prevent stale leaders from writing.

## Node lifecycle

1. Registration (capabilities, resources, health endpoint).
2. Heartbeat + resource reporting.
3. Task assignment by scheduler.
4. Graceful deregistration / failure detection.
5. Recovery (replay from checkpoint).

## Task scheduling

- Priority classes: critical (consistency/authority), high (user-facing cognition),
  normal (background consolidation), low (maintenance).
- Quotas per identity and per node.
- Affinity hints (data locality) but never authority bypass.

## Replication

- Policies per data class: authoritative records (strong, synchronous to quorum),
  memories (async with conflict detection), checkpoints (verified).
- Conflict detection via version vectors + identity version.
- Replica health monitoring; stale replicas quarantined and rebuilt.

## Migration procedure

1. Source-node verification (health, checkpoint freshness).
2. Destination-node validation (capacity, compatibility).
3. Transfer authorization (identity owner / authority).
4. Integrity verification (checksums, version match).
5. Cutover with fencing (old node fenced).
6. Completion record (auditable).
7. Recovery path if any step fails.

## Failure handling

- Network interruptions: retry with backoff, queue, resume.
- Node failures: detect via heartbeat, reassign, recover from checkpoint.
- Storage failures: failover to replica, alert.
- Incomplete migrations: resume or rollback to last verified checkpoint.
- Duplicate execution: idempotency keys.
- Conflicting updates: reject, surface to authority, never silently merge.

## Network partition handling

- Minority partition: read-only / degraded; no authoritative writes.
- Majority partition: continues with authority.
- Reconciliation on heal: version comparison, conflict report, human/authority
  resolution; never auto-merge identity history.

## Scalability notes

- Horizontal scaling of cognitive and world nodes.
- Identity authority is a bottleneck by design (correctness over throughput);
  mitigate with caching of read-only views and batching of non-authoritative work.
- Partition world simulation spatially; migrate regions independently.

## Open problems (research)

- Efficient strong-consistency identity authority across regions (latency).
- Verified continuity restoration as a measurable property.
- Quantifying "one coherent identity history" formally.
- Cost/latency of checkpoint verification at scale.
