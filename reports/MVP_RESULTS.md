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

- Evidence: `{"ci_high": 0.040153185914697576, "ci_low": -0.02790481223486517, "coverage": 0.9996635262449529, "estimate": 0.006124186839916203, "interpretation": "Association adjusted for market value and league/year fixed effects; not causal.", "mvp": 1, "n": 5942, "p_value": 0.7242878523550248, "ssb_sd": 0.22292516404430385, "status": "reformular"}`

### MVP 2: descartar

- Evidence: `{"ci_high": 0.029395836814550748, "ci_low": -0.005549364132650095, "estimate": 0.011923236340950326, "interpretation": "Within-team-season association of prior schedule shock with match points.", "mvp": 2, "n": 212262, "p_value": 0.181068617788536, "status": "descartar"}`

### MVP 3: avançar

- Evidence: `{"ci_high": -0.08491024971944494, "ci_low": -1.195383346991221, "gini_sd": 0.11016435453636962, "hierarchical_sign_compatible": true, "holdout_ci_high": 0.31485505431370564, "holdout_ci_low": -1.7828338848318626, "holdout_p_value": 0.17018866365829943, "holdout_triple_interaction": -0.7339894152590785, "interpretation": "Observational moderation with sign-compatible temporal holdout and fixed season-start Elo; conservative league-clustered and lagged-value intervals include zero. No predeclared three-match mechanism implication was supported.", "lagged_market_ci_high": 0.12659657834595095, "lagged_market_ci_low": -1.0708434572907315, "lagged_market_coverage": 0.854306864064603, "lagged_market_leave_one_league_out_sign_share": 1.0, "lagged_market_n": 5078, "lagged_market_p_value": 0.12221602379081425, "lagged_market_triple_interaction": -0.4721234394723903, "league_cluster_ci_high": 0.050133614437918306, "league_cluster_ci_low": -1.3304272111485842, "league_cluster_p_value": 0.06723919263659175, "leave_one_league_out_sign_share": 1.0, "market_timestamp_verified": false, "mechanism_primary_team_match_rows": 160382, "mechanism_resource_buffering_explanation_supported": false, "mechanism_supported_implications": 0, "mechanism_tested_implications": 4, "minimum_support_cell_n": 429, "mvp": 3, "n": 5942, "nonlinearity_p_value": 0.05112136112382202, "p_value": 0.023840252072785364, "preseason_elo_ci_high": -0.09761277972319338, "preseason_elo_ci_low": -1.4285273402572864, "preseason_elo_p_value": 0.024610527506683123, "preseason_elo_triple_interaction": -0.7630700599902399, "schedule_strength_safe_alternative_sign_share": 1.0, "status": "avançar", "triple_interaction": -0.640146798355333}`

### MVP 4: avançar

- Evidence: `{"interpretation": "Two pre-schedule strength proxies were tested under nulls that preserve fixtures and home/away assignments; the stricter null also preserves broad season phase. Cross-proxy agreement and source-consistent FDR findings are reported separately.", "league_season_nulls_fdr_q_lt_0_05": 4, "league_season_nulls_upper_tail_p_lt_0_05": 64, "league_seasons": 289, "median_strength_source_correlation": 0.5778773067331182, "minimum_strength_source_league_seasons": 286, "mvp": 4, "null_models": 2, "source_consistent_fdr_findings": 0, "status": "avançar", "strength_source_correlations_below_0_30": 43, "strength_sources": 2, "valid_permutation_draws": 11500000}`

### MVP 5: descartar

- Evidence: `{"attendance_rate": 0.9972146144243847, "ci_high": 0.002174195523718566, "ci_low": -0.01080280389178627, "estimate": -0.004314304184033852, "interpretation": "Within-home-team-season association; observed attendance only and COVID-era seasons excluded.", "mvp": 5, "n": 101076, "p_value": 0.19250291319199808, "status": "descartar"}`
