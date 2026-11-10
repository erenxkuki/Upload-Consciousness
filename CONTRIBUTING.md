# Contributing

## Principles

- Scientific honesty over demo appeal.
- No fake implementations presented as finished.
- No placeholder functions without identification.
- Tests must actually run and pass before claiming.
- Document limitations.

## Development

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
cp .env.example .env
pytest -q
```

## Pull requests

- Describe change, tests added, and any ADR impact.
- Update STATUS.md.
- Keep modules small and boundaries clear.

## License

Pending formal selection; contributions under research/educational intent.
