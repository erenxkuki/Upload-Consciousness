# Security

## Reporting

Please report vulnerabilities privately to the maintainers before public disclosure.

## Scope

- Identity and memory data confidentiality and integrity.
- Consent and authorization bypass.
- Audit log tampering.
- Erasure completeness.

## Practices

- Argon2 password hashing.
- JWT access tokens with expiry.
- Hash-chained audit log.
- Input validation via Pydantic.
- Least-privilege roles.

## Out of scope (current)

- Production key management (planned).
- Multi-tenant isolation (planned).
- Formal verification (planned).
