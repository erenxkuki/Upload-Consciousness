# Biological System Mapping

## Principle

Biological organs are **not** interchangeable with software modules. These names are
architectural metaphors, not claims that the implementation reproduces biological
functions. Every subsystem documents: responsibility, input/output contracts,
internal state, persistence, dependencies, error handling, testing, scientific
references, limitations.

## Mapping table

| Biological metaphor | Software subsystem | Primary responsibility |
|---|---|---|
| Brain (Cognitive Core) | `biological_systems/brain/` | Orchestration, reasoning, attention, planning, working memory, reflection, self-model |
| Hippocampus | `biological_systems/hippocampus/` | Experience indexing, episodic/semantic/procedural/autobiographical memory formation & retrieval |
| Heart (Emotional) | `biological_systems/emotional_system/` | Persistent, evolving multi-dimensional emotional state |
| Nervous System | `biological_systems/nervous_system/` | Internal event communication, coordination, routing |
| Endocrine System | `biological_systems/endocrine_system/` | Slow-changing regulatory variables (stress-like, energy, motivation, cognitive load) |
| Sensory System | `biological_systems/sensory_system/` | Perception interfaces (vision, audio, language, spatial, fusion) |
| Motor System | `biological_systems/motor_system/` | Movement, gesture, posture, avatar control |
| Immune System | `biological_systems/immune_system/` | Integrity, anomaly detection, security (independent of cognition) |
| Genetic Blueprint | `biological_systems/genetic_blueprint/` | Relatively stable originating characteristics (conceptual) |
| Circadian System | `biological_systems/circadian_system/` | Time awareness, temporal context, activity cycles |
| Metabolism | `biological_systems/metabolism/` | Resource management (CPU/GPU/memory/network/storage/inference) |
| Identity System | `core/identity_core/` | Personal continuity, manifests, provenance, migration |
| Autonomy/Existence | `autonomy/` | Consent, lifecycle, suspension, restoration, erasure |

## Cognitive core submodules

`reasoning/`, `attention/`, `planning/`, `working_memory/`, `reflection/`, `self_model/`.

The cognitive core **must not** directly modify authoritative memories; it passes
through memory governance.

## Memory types

Episodic, semantic, procedural, autobiographical, working. Every record carries:
unique id, source, creation timestamp, event timestamp (when known), context,
content, associated entities, confidence, provenance, access restrictions, version,
correction history, retention policy. Correction never silently rewrites history.
Distinguish actual experiences, imported info, generated interpretations, uncertain
recollections.

## Emotional dimensions

Valence, arousal, dominance, intensity, persistence, context, triggering experience,
confidence, duration, recovery dynamics. Immediate updates, experience-driven
development, time-based evolution, long-term patterns, contradictory associations.

## Security independence

Security (`immune_system/`) operates independently of the cognitive model. An AI
model must never disable its own security controls via generated instructions.
