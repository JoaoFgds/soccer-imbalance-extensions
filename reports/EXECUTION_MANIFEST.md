# Execution manifest

- Execution date: 2026-09-22 (America/Sao_Paulo)
- Results-generating commit: `04be159`
- Python: 3.12.11
- Dependency resolution: `uv.lock`
- Random seed: `20260922`
- Source release: `reproducibility-v1`
- Standings rows: 5,944
- Valid league-seasons: 306
- Unique fixtures: 112,094
- Raw schedule views: 224,120
- Tests: 21 passed
- Lint: Ruff passed
- Git diff whitespace validation: passed
- Acquisition idempotence: rerun reused all three cached archives and revalidated
  their SHA-256 values
- Live pilot: two successful Transfermarkt requests; HTML retained only in ignored
  local cache
- Reference repository before and after: clean `master` at
  `54b4625be98d9710fc41e72bade8f2e68049c920`
- MVP 3 robustness: 20/20 same-season and 20/20 preceding-season
  leave-one-league-out estimates retained the negative interaction sign. All 6/6
  outcome specifications using dynamic pre-match or fixed season-start Elo retained
  it. The fixed-start estimate was -0.7631 (95% CI [-1.4285, -0.0976]); the late
  holdout retained the sign but not precision. Conservative 20-league clustering
  widened the primary CI across zero. The lagged model covered 5,078 rows and 288
  league-seasons, with material selection on club market value.
- MVP 4 robustness: 289 market-value and 286 fixed-start-Elo league-seasons, two
  nulls, 10,000 permutations per league-season/source/null and 11,500,000 valid
  draws. Four Elo rows survived within-source/null FDR correction, but zero
  findings survived with both strength sources.
- Mechanism gate: pre-analysis plan committed as `b30e3e1`; 160,382 ordered
  team-match rows, 5,078 team-seasons and 87,825 fixtures. Zero of four
  directional implications passed Holm correction. Resource-related future
  controls passed equivalence, while the corresponding past effects were bounded
  inside ±0.05 points.
- Final cumulative gate: pre-analysis plan committed as `e9726f0`; the measurement
  bridge passed at 0.733 across 5,576 team-seasons and in 18/20 leagues at the
  predeclared 0.60 threshold. Zero of six cumulative implications passed; no
  matched future control was equivalent. Final classification: scale linked,
  mechanism not identified.

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
