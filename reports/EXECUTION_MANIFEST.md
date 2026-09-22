# Execution manifest

- Execution date: 2026-09-22 (America/Sao_Paulo)
- Results-generating commit: `37cb008b5021ce74ef4b358987750a25b24e6d4b`
- Python: 3.12.11
- Dependency resolution: `uv.lock`
- Random seed: `20260922`
- Source release: `reproducibility-v1`
- Standings rows: 5,944
- Valid league-seasons: 306
- Unique fixtures: 112,094
- Raw schedule views: 224,120
- Tests: 11 passed
- Lint: Ruff passed
- Git diff whitespace validation: passed
- Acquisition idempotence: second run reused both cached archives and revalidated
  their SHA-256 values
- Live pilot: two successful Transfermarkt requests; HTML retained only in ignored
  local cache
- Reference repository before and after: clean `master` at
  `54b4625be98d9710fc41e72bade8f2e68049c920`

Commands executed for the final evidence:

```bash
uv run --locked sie fetch-reference
uv run --locked sie validate-source --source-root data/raw/reference
uv run --locked sie collect-pilot --delay-seconds 3
uv run --locked sie run-all --source-root data/raw/reference
uv run --locked --extra dev pytest -q
uv run --locked ruff check .
git diff --check
```
