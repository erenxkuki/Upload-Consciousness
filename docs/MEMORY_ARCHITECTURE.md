# Memory Architecture

## Memory types

- **Episodic** — specific events and experiences.
- **Semantic** — facts, knowledge, concepts, relationships.
- **Procedural** — learned skills and procedures.
- **Autobiographical** — personal history and identity-relevant experiences.
- **Working** — temporary active information.

## Memory record (minimum fields)

- Unique identifier.
- Source (who/what produced it).
- Creation timestamp.
- Event timestamp when known.
- Context.
- Content.
- Associated entities.
- Confidence.
- Provenance (chain of transformations).
- Access restrictions.
- Version.
- Correction history.
- Retention policy.

## Storage layers (separate)

1. Raw observations.
2. Processed experiences.
3. Consolidated memories.
4. Semantic knowledge.
5. Identity-relevant information.
6. Inferred interpretations.
7. Generated content.

Never automatically promote generated content into verified personal memories.
Preserve provenance throughout the retrieval pipeline.

## Correction without silent rewrite

Corrections append a new version with `supersedes` link; original retained.
Retrieval defaults to latest valid version; audit can view history.

## Provenance chain

Each transformation (ingest -> process -> consolidate -> retrieve) records
input ids, operation, actor, timestamp, confidence delta.

## Distinguish

Actual experiences vs imported information vs generated interpretations vs uncertain
recollections. Each record tagged with `origin_class`.

## Consolidation proposals

Memory consolidation (hippocampus) proposes; governance approves. No auto-promotion
of inferences.

## Retrieval

Semantic (vector) + structured filters + provenance-aware. Respect access
restrictions and consent. Return confidence + sources.

## Retention & deletion

Per-record retention policy; erasure cascades with verification; backups documented
with unavoidable limitations.
