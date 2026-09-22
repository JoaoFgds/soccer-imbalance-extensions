# MVP 4 — Constraint-preserving counterfactual schedules

- **Data:** 289 usable league-seasons with market-value strength and 286 with
  fixed season-start Elo, across all 20 leagues.
- **Procedure:** 10,000 seeded permutations for each league-season, strength
  source and null. The global-round null moves complete rounds anywhere; the
  phase-preserving null moves rounds only within their season half. Both preserve
  fixtures and home/away assignments. SSB is computed on within-season strength
  ranks, so the implementation is invariant to monotonic transformations as
  required by Spearman correlation.
- **Computation:** all 11,500,000 requested draws were valid. Maximum Monte Carlo
  standard error remains within the predeclared 0.0051 threshold.
- **Market-value result:** each null has 11 of 289 nominal upper-tail p-values
  below 0.05 and zero after Benjamini-Hochberg correction. Mean observed absolute
  SSB is 0.1806 versus null means of about 0.1948.
- **Fixed-Elo result:** each null has 21 of 286 nominal findings and two FDR
  findings. These are the same two league-seasons under both nulls: LaLiga2 2016
  and 2024. Mean observed absolute SSB is 0.1848 versus null means of about 0.1948.
- **Cross-proxy stress test:** no league-season/null combination survives FDR
  under both strength definitions. The median Spearman agreement between market
  and fixed-Elo team strength is 0.578; 43 of 286 correlations are below 0.30.
  Agreement is only 0.161 in LaLiga2 2016 and 0.562 in LaLiga2 2024. The individual
  Elo findings are therefore proxy-dependent, not replicated anomalies.
- **Limitation:** the null excludes unobserved broadcasting, policing, travel and
  shared-stadium restrictions. Multiple-testing correction addresses screening,
  not missing real-world scheduling constraints.
- **Decision:** **advance as a methodological null benchmark**. Across both
  pre-schedule strength proxies, observed mean imbalance is below rather than
  above the permutation mean. There is no robust evidence of systematic excess
  imbalance and no individual-season finding is source-consistent.
