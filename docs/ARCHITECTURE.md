# Architecture

## Overview

Hybrid Distributed Mind Architecture: independent identity instances backed by
distributed computational infrastructure. Identity ownership is **centralized and
authoritative**; computation, storage, and execution are **distributed**.

```
                    +---------------------------+
                    |   Identity Authority      |  <-- authoritative ownership
                    |  (single logical owner)   |     state-transition rules
                    +-------------+-------------+
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
  Cognitive Nodes           Memory Nodes              Continuity Nodes
  (reasoning, planning)     (episodic/semantic)       (checkpoints, recovery)
        |                         |                         |
        +-----------+-------------+-----------+-------------+
                    |                         |
              World Sim Nodes             Gateway Nodes
              (environments)             (auth, API, routing)
```

## Node types

| Node | Responsibility |
|---|---|
| Identity authority | Authoritative identity metadata, ownership, authorization boundaries, identity versions, state transitions |
| Cognitive execution | Reasoning workloads, experience processing, candidate memory updates, approved cognitive modules |
| Memory | Episodic/semantic/personal-history/relationship storage |
| Continuity | Checkpoints, consistency verification, recovery, migration coordination |
| World simulation | Virtual environments, physics, spatial interactions, multi-entity |
| Gateway | Authentication, access policies, secure APIs, routing |

## Distributed-system rules

- Versioned state.
- Explicit consistency guarantees.
- Idempotent operations.
- Transaction boundaries.
- Event ordering.
- Conflict detection.
- Replication policies.
- Checkpoint verification.
- Recovery procedures.
- Node health monitoring.
- Network partition handling.
- Resource allocation.
- Workload scheduling.

Never assume distributed replicas share identical state. Explicit rules for
concurrent updates, stale replicas, duplicate events, failed transactions, recovery.

## Consistency classification

| Component | Consistency requirement |
|---|---|
| Identity ownership | Strong |
| Authorization / consent | Strong |
| Destructive lifecycle (erase) | Strong |
| State-transition rules | Strong |
| Identity version increments | Strong |
| Memory writes (candidate) | Eventual (gated by governance) |
| Cognitive working memory | Eventual / local |
| World simulation state | Eventual (per region) |
| Telemetry / metrics | Eventual |
| Caches | Eventual |

**Never use eventual consistency for authorization, identity ownership, or
destructive lifecycle operations.**

## Split-brain prevention

Multiple machines must not independently create contradictory authoritative
histories. Mechanisms:

- Single logical identity authority per identity (lease/leader election).
- Monotonic identity-version counter, incremented only by authority.
- State transitions validated against current version (optimistic concurrency).
- Fencing tokens on migration to prevent stale-node writes.
- Quorum for destructive operations.
- Audit log of all authority decisions.

## Identity ownership model (key decision)

Computation, storage, execution are distributed. **Authoritative identity and
state-transition rules are not.** A network partition yields degraded availability,
not divergent identity histories. This is the central architectural commitment
recommended for the hybrid design.

## Module boundaries

Every module: strong typing, clear boundaries, small components, explicit
dependencies, structured errors, consistent naming, useful comments, no unnecessary
abstractions, no duplicated business logic, no hidden global state.

## Event communication (nervous system)

Typed events, message schemas, event versioning, correlation ids, delivery
guarantees, retry policies, dead-letter handling, distributed tracing,
permission-aware communication. No module silently bypasses communication or
governance layers.

## Storage architecture

See `docs/MEMORY_ARCHITECTURE.md`. PostgreSQL for structured authoritative records;
pgvector (optional) for semantic retrieval; object storage for large media and
checkpoint artifacts; Redis for temporary caches/coordination where appropriate;
append-only event storage for historical state transitions. Each dependency
documented with alternatives, trade-offs, reasons.

## API

Versioned `/api/v1/*`. OpenAPI, typed schemas, auth, authorization, validation,
rate limiting, idempotency, structured errors, auditability. WebSockets for
interactive environments. Provider-specific integrations behind replaceable
interfaces.

## Technology stack

Python + FastAPI + Pydantic (core backend); Rust for performance-sensitive modules
(later); PostgreSQL + pgvector; NATS (or equivalent) for events; React + TypeScript
(frontend); Godot/Unreal (evaluate) for 3D; llama.cpp / local + OpenAI-compatible
adapters for inference; Docker + Compose (dev); Kubernetes only when warranted;
OpenTelemetry for observability.

## Repository structure

See master spec section 14. Modular monorepo. Adjust when justified, preserve
modular boundaries.
