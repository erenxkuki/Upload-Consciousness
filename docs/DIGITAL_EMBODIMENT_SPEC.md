# Digital Embodiment Spec

## Independence

The digital body is an independent subsystem. It does not own or contain the
authoritative identity. Identity, embodiment, and environment are distinguished.

## Body configuration

- Human-like body representation.
- Customizable configuration.
- Avatar identity binding (reference, not ownership).
- Body capability definitions.
- Animation configuration.

## Perception

- Virtual vision, audio, spatial awareness, environmental sensing.

## Movement

- Locomotion, navigation, collision handling, gesture control, posture, object
  manipulation.

## Expression

- Facial animation, voice, speech synchronization, body language.

## Invariants

- One identity may use multiple authorized avatars.
- Avatar change does not create new identity.
- Avatar deletion does not delete identity.
- Embodiment independent of identity model.

## Interfaces

High-level movement intentions separated from low-level physical simulation.
Avatar config serializable and versioned. Voice/speech behind replaceable adapters.
