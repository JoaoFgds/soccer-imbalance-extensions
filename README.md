# soccer-imbalance-extensions

Reproducible screening pipeline for five empirical extensions of
*The Impact of Strength of Schedule Balance on Tournament Efficacy* (ISACE 2026,
DOI: [10.1007/978-3-032-27272-0_18](https://doi.org/10.1007/978-3-032-27272-0_18)).

This repository is independent from
[`soccer-scraper`](https://github.com/JoaoFgds/soccer-scraper). The original
project is used only as a public data/provenance reference. No original source
code or raw Transfermarkt pages are versioned here. Results are exploratory MVP
evidence, not definitive results for an extended paper.

## What is implemented

1. Continuous schedule imbalance using strictly pre-match Elo ratings.
2. Local two-, three-, and five-match opponent-strength shocks.
3. Moderation by relative squad value and league market-value inequality.
4. Constraint-preserving Monte Carlo permutations of complete rounds under
   global-round and phase-preserving nulls.
5. Within-team-season models of schedule shocks and stadium attendance.

A timestamped post-MVP gate additionally tests short-rest fatigue, long-recovery
adaptation and resource buffering against symmetric future-schedule controls.

The pipeline validates source keys, deduplicates the two team views of a fixture,
records exclusions, prevents future-information leakage, fits cluster-robust or
within-panel models, and writes aggregate tables, figures, diagnostics, and an
MVP decision matrix.

## Installation

Python 3.12 and [`uv`](https://docs.astral.sh/uv/) are required.

```bash
uv sync --locked --extra dev
uv run --locked --extra dev pytest -q
```

## Data acquisition

Raw data are deliberately ignored by Git. Download and checksum the public
reference release locally:

```bash
uv run --locked sie fetch-reference
```

The command downloads `analysis-inputs-v1.zip`, `market-values-bronze-v1.zip`
and `soccer-scraper-bronze-v1.zip` from the public `reproducibility-v1`
release, verifies their SHA-256 digests, and extracts them under
`data/raw/reference/`.

Run the two-request live-source pilot:

```bash
uv run --locked sie collect-pilot --delay-seconds 3
```

The HTML remains in ignored local cache. Only provenance metadata is published.

## Reproduction

After `fetch-reference`:

```bash
uv run --locked sie validate-source --source-root data/raw/reference
uv run --locked sie run-mvp 3 --source-root data/raw/reference
uv run --locked sie run-all --source-root data/raw/reference
uv run --locked --extra dev pytest -q
uv run --locked ruff check .
```

All random behavior uses seed `20260922`. Cached acquisition is idempotent;
existing downloads are hashed and reused.

## Executed MVP results

The reference execution covered 5,944 team-seasons, 306 league-seasons and
112,094 unique matches.

| MVP | Evidence from the screening run | Decision |
|---:|---|---|
| 1 | Continuous SSB coefficient `0.0061`, 95% CI `[-0.0279, 0.0402]`; 99.97% team-season coverage | Reformulate toward heterogeneity; the average association is a precise null |
| 2 | Three-match shock coefficient `0.0119` points per 100 Elo, 95% CI `[-0.0055, 0.0294]`; windows 2 and 5 also null | Discard the tested short-run linear mechanism |
| 3 | Same-season interaction `-0.6401`, 95% CI `[-1.1954, -0.0849]`; fixed season-start Elo `-0.7631`, 95% CI `[-1.4285, -0.0976]`; holdout and preceding-season estimates retain the sign but are imprecise; 0/4 predeclared short-run mechanisms pass | Advance as unexplained observational heterogeneity with qualified inferential strength; no causal or verified pre-season claim |
| 4 | 286–289 league-seasons, two strength proxies, two nulls and 11.50 million valid draws; four Elo-based FDR findings but zero findings consistent across strength proxies | Advance as a null/benchmark contribution, not as evidence of systematic excess imbalance |
| 5 | Attendance effect `-0.0043` log points per 100 Elo, 95% CI `[-0.0108, 0.0022]`; 99.72% attendance availability | Discard the tested linear attendance mechanism |

The recommended full analysis is **MVP 3**, with MVP 1 retained as its
measurement and baseline layer. Statistical significance is not used as a
general success criterion: MVPs 2 and 5 are rejected because their confidence
intervals fall inside predeclared minimum effects of scientific interest; MVP 4
advances because its methodological null benchmark is the contribution.

## Repository map

- `src/soccer_imbalance_extensions/`: acquisition, validation, feature and model code.
- `configs/mvps.yaml`: seeds, Elo settings, exclusions and decision thresholds.
- `tests/`: parsing, key, temporal leakage and reproducibility tests.
- `results/tables/`: aggregate coefficients, coverage, sensitivities and decisions.
- `results/figures/`: one diagnostic visualization per MVP.
- `reports/`: data diagnostics, source pilot and analytical reports.
- `reports/TEMPORAL_AUDIT.md`: market-value timing audit and decision boundary.
- `reports/ROBUSTNESS_REVIEW.md`: second-pass stress tests and updated evidence
  classification.
- `reports/MECHANISM_FALSIFICATION.md`: results of the predeclared post-MVP
  mechanism gate.
- `docs/`: original-study boundary, traceability, methodology, and licensing.
- `docs/MECHANISM_FALSIFICATION_PLAN.md`: timestamped specification for the
  post-MVP mechanism gate.
- `docs/CUMULATIVE_PATH_GATE_PLAN.md`: timestamped specification for the final
  season-path reconciliation gate.
- `data/`: local raw/interim/processed files; contents are ignored by Git.

## Important limitations

- The Elo initialization and K-factor are MVP choices, not optimized estimates.
- Round permutations do not reproduce unobserved commercial, policing or
  stadium-sharing constraints. Coverage is 289 league-seasons with market value
  and 286 with fixed season-start Elo; the two strength rankings have only
  moderate median agreement and no FDR finding is common to both.
- The article calls the financial data pre-season, but the 451 released Bronze
  files were bulk-collected on 2026-03-18 and contain no valuation timestamp.
  The `saison_id` proves the selected season, not the within-season snapshot.
  Preceding-season values support the same qualitative pattern with lower
  precision, but their availability strongly selects higher-value clubs. MVP 3
  therefore remains observational rather than causal.
- Match points and attendance models remain observational.
- Two dates and one result could not be parsed; they are reported, not silently
  corrected.
- Some league-seasons lack enough joined or varying strengths for a valid
  counterfactual; exclusions are reported separately for each strength source.

## Citation and licensing

Please cite the published article above and this repository commit when using
the pipeline. The reference project contains no versioned license file in the
inspected commit, so no code was copied. This repository intentionally has no
license pending an explicit owner decision. See
[`docs/DATA_AND_LICENSES.md`](docs/DATA_AND_LICENSES.md).
