# Privacy and Security Spec

## Threat model (summary)

- Unauthorized access to identity/memory data.
- Tampering with authoritative state.
- Replay/duplicate events.
- Stale replica writes (split-brain).
- Inference-provider exfiltration of personal data.
- Over-permissioned third-party data use.
- Erasure that leaves ghosts in backups.
- Social engineering / consent bypass.
- Denial of service / resource exhaustion corrupting identity data.

## Controls

- Explicit informed consent; granular data permissions.
- Data minimization.
- Encryption at rest and in transit.
- Strong authentication (argon2 password hashing, JWT access tokens).
- Role-based access control (owner, custodian, researcher, system).
- Audit logs (append-only, tamper-evident hashing).
- Revocable access.
- Data export.
- Data correction.
- Retention policies.
- Verified deletion.
- Secure backup management.
- Rate limiting.
- Idempotency keys.
- Input validation (Pydantic).

## Immune system independence

Security operates independently of the cognitive model. An AI model cannot disable
its own security controls via generated instructions. Security decisions are made
by deterministic policy code, never by LLM output.

## Audit log

Every important state transition: validated, logged, versioned, auditable,
recoverable where applicable. Append-only; hash-chained for tamper evidence.

## Key management

Secrets via environment; never committed. JWT secret rotatable. Per-identity
encryption keys planned for later phases.

## Third-party data

Special protections. No self-granted permissions. Consent recorded per data
subject.
