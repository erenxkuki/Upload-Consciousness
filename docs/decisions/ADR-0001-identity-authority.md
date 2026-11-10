# ADR-0001: Centralized Identity Authority with Distributed Computation

## Status

Accepted.

## Context

A hybrid distributed architecture risks split-brain: two nodes independently
evolving contradictory authoritative histories of the same identity during a
network partition.

## Decision

Computation, storage, and execution are distributed. Authoritative identity and
state-transition rules are **not** distributed. One logical identity authority per
identity, elected via lease, validates and records all state transitions.

Cognitive/memory/world nodes propose updates; the authority commits or rejects.
Fencing tokens prevent stale nodes from writing.

## Consequences

- Correctness over throughput for identity operations.
- Identity authority is a scaling bottleneck; mitigated by read-only view caching
  and batching of non-authoritative work.
- Network partitions degrade availability rather than producing divergent histories.
- Migration requires explicit authorization and fencing.

## Alternatives considered

- Fully distributed identity (CRDT-based): rejected — cannot guarantee single
  coherent history under partition; conflicts in identity/personality state are
  not safely auto-mergeable.
- Single machine: rejected — single point of failure, hardware dependency.

## Open questions

- Cross-region latency for authority; possibly regional read replicas with
  authority in one region.
- Formal verification of "one coherent identity history".
