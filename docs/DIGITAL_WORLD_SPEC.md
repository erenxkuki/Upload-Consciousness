# Digital World Spec

## Overview

Extensible simulation platform hosting multiple interacting digital entities.
Need not run on one server. Spatial partitioning, region ownership, replication,
migration.

## Subsystems

- `world_simulation/` — environment simulation, time progression, environmental
  state, world persistence.
- `physics/` — spatial coordinates, collision, movement, object interactions.
- `environment/` — buildings, landscapes, indoor/outdoor, custom locations.
- `social/` — communication, social interactions, relationship modelling, group
  activities, community systems.
- `multiplayer/` — multi-entity sessions, synchronization, presence, event
  distribution.
- `personal_spaces/` — private environments, customization, access permissions.
- `governance/` — community rules, consent, privacy, moderation, dispute
  resolution.

## Privacy boundary

Entities communicate via secure interfaces without exposing private memory stores.
World must not require all entities on one server.

## Governance

Consent-aware. Moderation with audit. Dispute resolution documented. No forced
participation.
