# MVP execution report

All estimates are exploratory associations, not causal effects.

## Data diagnostics

```json
{
  "attendance_missing_rate": 0.003122379431548522,
  "blank_or_unparsed_dates": 2,
  "conflicting_duplicate_groups": 0,
  "leagues": 20,
  "match_links_over_two_views": 0,
  "raw_schedule_rows": 224120,
  "season_max": 2024,
  "season_min": 2004,
  "singleton_match_links": 68,
  "source_files": 5958,
  "standings_rows": 5944,
  "unique_matches": 112094,
  "unparsed_results": 1,
  "valid_league_seasons": 306
}
```

## Decisions

### MVP 1: reformular

- Evidence: `{"ci_high": 0.04015318591469818, "ci_low": -0.027904812234864566, "coverage": 0.9996635262449529, "estimate": 0.0061241868399168065, "interpretation": "Association adjusted for market value and league/year fixed effects; not causal.", "mvp": 1, "n": 5942, "p_value": 0.7242878523549988, "ssb_sd": 0.22292516404430385, "status": "reformular"}`

### MVP 2: descartar

- Evidence: `{"ci_high": 0.029395836814550946, "ci_low": -0.005549364132649833, "estimate": 0.011923236340950556, "interpretation": "Within-team-season association of prior schedule shock with match points.", "mvp": 2, "n": 212262, "p_value": 0.1810686177885268, "status": "descartar"}`

### MVP 3: avançar

- Evidence: `{"ci_high": -0.08491024971944383, "ci_low": -1.1953833469912285, "gini_sd": 0.11016435453636962, "hierarchical_sign_compatible": true, "interpretation": "Observational moderation with sign-compatible lagged-value sensitivity; same-season valuation timing is not independently verified.", "lagged_market_ci_high": 0.1265965783459565, "lagged_market_ci_low": -1.070843457290739, "lagged_market_coverage": 0.854306864064603, "lagged_market_leave_one_league_out_sign_share": 1.0, "lagged_market_n": 5078, "lagged_market_p_value": 0.12221602379081757, "lagged_market_triple_interaction": -0.4721234394723913, "leave_one_league_out_sign_share": 1.0, "market_timestamp_verified": false, "minimum_support_cell_n": 429, "mvp": 3, "n": 5942, "nonlinearity_p_value": 0.05112136112382411, "p_value": 0.023840252072785773, "schedule_strength_safe_alternative_sign_share": 1.0, "status": "avançar", "triple_interaction": -0.6401467983553362}`

### MVP 4: avançar

- Evidence: `{"interpretation": "Both nulls preserve fixtures and home/away assignments; the stricter null also preserves broad season phase.", "league_season_nulls_fdr_q_lt_0_05": 0, "league_season_nulls_upper_tail_p_lt_0_05": 22, "league_seasons": 289, "mvp": 4, "null_models": 2, "status": "avançar", "valid_permutation_draws": 5780000}`

### MVP 5: descartar

- Evidence: `{"attendance_rate": 0.9972146144243847, "ci_high": 0.002174195523718553, "ci_low": -0.010802803891786283, "estimate": -0.004314304184033865, "interpretation": "Within-home-team-season association; observed attendance only and COVID-era seasons excluded.", "mvp": 5, "n": 101076, "p_value": 0.19250291319199675, "status": "descartar"}`
