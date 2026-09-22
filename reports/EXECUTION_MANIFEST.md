# Execution manifest

- Execution date: 2026-09-22 (America/Sao_Paulo)
- Results-generating commit: `cfdbc62553bb3770f8d9449677e96e87182a2b76`
- Python: 3.12.11
- Dependency resolution: `uv.lock`
- Random seed: `20260922`
- Source release: `reproducibility-v1`
- Standings rows: 5,944
- Valid league-seasons: 306
- Unique fixtures: 112,094
- Raw schedule views: 224,120
- Tests: 16 passed
- Lint: Ruff passed
- Git diff whitespace validation: passed
- Acquisition idempotence: rerun reused all three cached archives and revalidated
  their SHA-256 values
- Live pilot: two successful Transfermarkt requests; HTML retained only in ignored
  local cache
- Reference repository before and after: clean `master` at
  `54b4625be98d9710fc41e72bade8f2e68049c920`
- MVP 3 robustness: 20/20 same-season and 20/20 preceding-season
  leave-one-league-out estimates retained the negative interaction sign. All 3/3
  outcome specifications using verified pre-match Elo also retained it. The lagged
  model covered 5,078 rows and 288 league-seasons.
- MVP 4 robustness: 289 league-seasons, two nulls, 10,000 permutations per
  league-season/null and 5,780,000 valid draws; zero upper-tail findings after
  within-null FDR correction.

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
