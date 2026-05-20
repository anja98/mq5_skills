# Contributing

## Principles

- Safety-first: never remove risk controls.
- Compile-ready: examples must follow valid MQL5 APIs.
- Measurable: new guidance should include validation criteria.
- Educational: no profit guarantees or financial advice.

## Workflow

1. Update `SKILL.md` for behavior changes.
2. Add or update `evals.json` cases for new capabilities.
3. Update docs/examples/templates as needed.
4. Run:

```bash
python tools/validate_repo.py
```

5. Document changes in `CHANGELOG.md`.
