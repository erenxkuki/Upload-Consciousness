# 🧠 Upload Consciousness

> **Project Codename:** UCC — Unified Continuity Core  
> **Architecture:** Hybrid Distributed Digital Mind Architecture  
> **Classification:** Experimental Cognitive Systems / Digital Human Continuity Research

[![Status](https://img.shields.io/badge/status-UCC--0.9%20foundation-blue)](#status)
[![Tests](https://img.shields.io/badge/tests-26%20passing-brightgreen)](#tests)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](#quick-start)
[![License](https://img.shields.io/badge/license-MIT-lightgrey)](LICENSE)
[![Scientific Honesty](https://img.shields.io/badge/scientific%20honesty-enforced-orange)](#scientific-boundaries)

## Founding Statement

> **Exploring the continuity of human identity beyond biological limitations.**

We are not building a digital prison.  
We are not assuming that endless existence is desirable.  
We are not pretending that a convincing simulation proves consciousness.

We are investigating whether the characteristics that make a human being who they are —
their memories, personality, cognitive patterns, emotional history, relationships,
and personal development — can be **computationally preserved, developed, and
potentially continued** beyond their original biological substrate.

**Human dignity, autonomy, privacy, and scientific integrity remain central to every
architectural decision. Technology must serve humanity — never the other way around.**

---

## 🌌 What is Upload Consciousness?

Upload Consciousness is an **experimental research platform** investigating whether
human identity characteristics can be computationally represented and preserved
across computational environments.

It is **not**:
- ❌ A chatbot or virtual companion
- ❌ A claim that consciousness has been transferred or uploaded
- ❌ A promise of digital immortality
- ❌ A behavioural benchmark dressed up as a consciousness detector

It **is**:
- ✅ A scientifically honest, modular research platform
- ✅ A hybrid distributed architecture for digital mind continuity
- ✅ An identity system that is independent of any inference provider (LLM)
- ✅ A foundation for studying memory provenance, emotional development, cognitive
  orchestration, distributed continuity, embodiment, and multi-entity worlds

---

## 🏗️ Architecture — Hybrid Distributed Mind

A single machine creates bottlenecks, hardware dependency, and a single point of
failure. Full distribution fragments identity. The answer is **hybrid**:

- **Distributed:** computation, storage, execution, world simulation.
- **Centralized (authoritative):** identity ownership and state-transition rules.

This prevents the hardest problem of distributed identity systems — a network
partition producing two machines independently evolving contradictory versions of
the same digital mind.

```
                    ┌───────────────────────────┐
                    │   Identity Authority      │  ← authoritative ownership
                    │  (single logical owner)   │     state-transition rules
                    └─────────────┬─────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
  Cognitive Nodes           Memory Nodes              Continuity Nodes
  (reasoning, planning)     (episodic/semantic)       (checkpoints, recovery)
        │                         │                         │
        └───────────┬─────────────┴─────────────┬─────────────┘
                    │                         │
              World Sim Nodes             Gateway Nodes
              (environments)             (auth, API, routing)
```

### Node types

| Node | Responsibility |
|---|---|
| Identity authority | Authoritative identity metadata, ownership, authorization, versions, transitions |
| Cognitive execution | Reasoning workloads, experience processing, candidate memory updates |
| Memory | Episodic / semantic / personal-history / relationship storage |
| Continuity | Checkpoints, consistency verification, recovery, migration |
| World simulation | Virtual environments, physics, spatial interactions, multi-entity |
| Gateway | Authentication, access policies, secure APIs, routing |

### Core invariants (non-negotiable)

1. **Identity ≠ inference provider.** Changing the underlying LLM must not change
   stored identity, memories, or personal history.
2. **No silent duplication.** Any derivative instance requires an explicit lineage
   record and a separate identity designation.
3. **No manufactured memories.** Generated content is never promoted to verified
   personal memory without evidence and provenance.
4. **Consent before data.** No personal data is collected before consent and
   autonomy design is in place.
5. **Scientific honesty.** Behavioural benchmarks are not consciousness detectors.
6. **No split-brain.** A network partition degrades availability — it never produces
   divergent authoritative identity histories.

---

## 🧬 Biological Architecture (metaphors, not biological claims)

The software architecture uses human anatomy as **conceptual inspiration**. Biological
organs are not interchangeable with software modules — these are architectural
metaphors, each with documented responsibility, contracts, state, persistence,
dependencies, error handling, testing, and limitations.

| Metaphor | Subsystem | Responsibility |
|---|---|---|
| Brain | `biological_systems/brain/` | Cognitive orchestration, reasoning, attention, planning, working memory, reflection, self-model |
| Hippocampus | `biological_systems/hippocampus/` | Memory formation, retrieval, consolidation proposals |
| Heart (Emotional) | `biological_systems/emotional_system/` | Persistent, evolving multi-dimensional emotional state |
| Nervous System | `biological_systems/nervous_system/` | Internal event communication, coordination, routing |
| Endocrine | `biological_systems/endocrine_system/` | Slow-changing regulatory variables |
| Sensory | `biological_systems/sensory_system/` | Perception interfaces (vision, audio, language, spatial, fusion) |
| Motor | `biological_systems/motor_system/` | Movement, gesture, posture, avatar control |
| Immune | `biological_systems/immune_system/` | Integrity, anomaly detection, security (independent of cognition) |
| Genetic Blueprint | `biological_systems/genetic_blueprint/` | Relatively stable originating characteristics (conceptual) |
| Circadian | `biological_systems/circadian_system/` | Time awareness, temporal context, activity cycles |
| Metabolism | `biological_systems/metabolism/` | Resource management (CPU/GPU/memory/network/storage/inference) |
| Identity | `core/identity_core/` | Personal continuity, manifests, provenance, migration |
| Autonomy | `autonomy/` | Consent, lifecycle, suspension, restoration, erasure |

---

## 🌍 Three Long-Term Platforms

1. **Digital Mind Platform** — identity, memories, personality, cognitive modelling,
   emotional modelling, learning, continuity.
2. **Digital Body Platform** — avatars, sensory interaction, movement, expression,
   environmental interaction.
3. **Digital Civilization Platform** — shared environments, social interaction,
   communities, virtual infrastructure, digital society, governance.

All three communicate through documented interfaces. The mind is independent of its
body and environment. The body is replaceable. The civilization can expand
independently of individual identity instances.

---

## 📊 Status

**Current release target:** UCC-0.9 — Hardening & Verification.

| Phase | Component | Status |
|---|---|---|
| 0 | Research & architecture | ✅ |
| 1 | Digital identity foundation | ✅ tested |
| 2 | Memory foundation | ✅ tested |
| 3 | Personality & emotional modelling | ✅ tested |
| 4 | Cognitive orchestration | ✅ tested |
| 5 | Distributed continuity | ✅ tested |
| 6 | Digital embodiment | ✅ tested |
| 7 | Digital world | ✅ tested |
| 8 | Advanced neuroscience research | ✅ docs |
| 9 | Hardening & verification | ✅ tested |

**Tests:** 26 passing. **Linter:** ruff clean.

See [`STATUS.md`](STATUS.md) for detailed component status.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- (Optional) PostgreSQL + pgvector for production storage
- (Optional) Redis for coordination

### Setup

```bash
git clone https://github.com/erenxkuki/Upload-Consciousness.git
cd Upload-Consciousness

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -e ".[dev]"
cp .env.example .env
```

### Run

```bash
# Initialize database
ucc initdb

# Start API server
ucc serve
# → http://127.0.0.1:8000
# → OpenAPI docs: http://127.0.0.1:8000/docs
```

### Test

```bash
pytest -q
```

---

## 📡 API Surface

All endpoints are versioned under `/api/v1`:

| Route | Description |
|---|---|
| `/health` | Liveness check |
| `/api/v1/auth` | Register / login (JWT) |
| `/api/v1/identity` | Create, retrieve, update, lifecycle, integrity, consent |
| `/api/v1/memory` | Experiences, memories, correction, consolidation |
| `/api/v1/emotions` | Multi-dimensional emotional state, history, decay |
| `/api/v1/personality` | Profiles, bounded drift |
| `/api/v1/cognition` | Cognitive steps, self-model, working memory, reflections, decisions, goals |
| `/api/v1/continuity` | Nodes, checkpoints, migration, recovery, conflicts, tasks |
| `/api/v1/embodiment` | Avatars, movement, perception, expressions |
| `/api/v1/world` | Environments, presence, messaging, governance |

---

## 🔬 Scientific Boundaries

This project maintains a strict, auditable distinction between:

1. What has been experimentally demonstrated
2. What is supported by established scientific research
3. What is a plausible engineering hypothesis
4. What remains speculative
5. What is currently impossible to verify

**No fabricated neuroscience. No fake consciousness tests. No misleading claims.**

Behavioural benchmarks are **not** consciousness detectors. The ability to discuss
consciousness is **not** evidence of consciousness. See
[`docs/SCIENTIFIC_BOUNDARIES.md`](docs/SCIENTIFIC_BOUNDARIES.md).

---

## 🔐 Privacy, Consent & Autonomy

- Digital continuation is **never compulsory**.
- Consent, suspension, archival, restoration, and verified erasure are first-class.
- No personal data is collected before consent design is in place.
- Access to someone's files, photos, or recordings does **not** grant permission to
  create a digital representation of them.
- Special protections for third-party information.

See [`docs/AUTONOMY_AND_EXISTENCE_POLICY.md`](docs/AUTONOMY_AND_EXISTENCE_POLICY.md)
and [`docs/PRIVACY_AND_SECURITY_SPEC.md`](docs/PRIVACY_AND_SECURITY_SPEC.md).

---

## 🛠️ Engineering Standards

- Strong typing (Pydantic + SQLAlchemy)
- Clear module boundaries, no hidden global state
- Structured error handling, consistent naming
- Hash-chained audit logs for every state transition
- Unit, integration, contract, security, and continuity tests
- `STATUS.md` tracks completed / in-progress / planned / known bugs / missing tests

---

## 📚 Documentation

| Document | Description |
|---|---|
| [`docs/VISION.md`](docs/VISION.md) | Project vision |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | System architecture |
| [`docs/SCIENTIFIC_BOUNDARIES.md`](docs/SCIENTIFIC_BOUNDARIES.md) | Epistemic tiers |
| [`docs/BIOLOGICAL_SYSTEM_MAPPING.md`](docs/BIOLOGICAL_SYSTEM_MAPPING.md) | Bio metaphors |
| [`docs/DISTRIBUTED_MIND_ARCHITECTURE.md`](docs/DISTRIBUTED_MIND_ARCHITECTURE.md) | Distributed design |
| [`docs/IDENTITY_CONTINUITY_SPEC.md`](docs/IDENTITY_CONTINUITY_SPEC.md) | Identity spec |
| [`docs/MEMORY_ARCHITECTURE.md`](docs/MEMORY_ARCHITECTURE.md) | Memory spec |
| [`docs/EMOTIONAL_DEVELOPMENT_SPEC.md`](docs/EMOTIONAL_DEVELOPMENT_SPEC.md) | Emotion spec |
| [`docs/DIGITAL_EMBODIMENT_SPEC.md`](docs/DIGITAL_EMBODIMENT_SPEC.md) | Embodiment spec |
| [`docs/DIGITAL_WORLD_SPEC.md`](docs/DIGITAL_WORLD_SPEC.md) | World spec |
| [`docs/AUTONOMY_AND_EXISTENCE_POLICY.md`](docs/AUTONOMY_AND_EXISTENCE_POLICY.md) | Autonomy policy |
| [`docs/PRIVACY_AND_SECURITY_SPEC.md`](docs/PRIVACY_AND_SECURITY_SPEC.md) | Privacy & security |
| [`docs/IMPLEMENTATION_ROADMAP.md`](docs/IMPLEMENTATION_ROADMAP.md) | Roadmap |
| [`research/feasibility.md`](research/feasibility.md) | Feasibility assessment |

---

## 🤝 Contributing

Contributions are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md).

Key principles:
- Scientific honesty over demo appeal
- No fake implementations presented as finished
- Tests must actually run and pass before claiming
- Document limitations

---

## 📜 License

This project is licensed under the **MIT License** — see [`LICENSE`](LICENSE).

---

## 🧭 Founding Statement (reminder)

> *Exploring the continuity of human identity beyond biological limitations.*  
> *We are not building a digital prison.*  
> *We are not assuming that endless existence is desirable.*  
> *We are not pretending that a convincing simulation proves consciousness.*  
> *Human dignity, autonomy, privacy and scientific integrity must remain central to
> every architectural decision.*  
> **Technology must serve humanity, never the other way around.**

---

_Built with scientific integrity. Open to research. Honest about its limits._
