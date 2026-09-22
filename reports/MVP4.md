# MVP 4 — Constraint-preserving counterfactual schedules

- **Data:** 289 usable league-seasons across all 20 leagues. Seventeen of the 306
  validated league-seasons are explicitly excluded because fewer than four teams
  could be joined to valid market-strength ranks.
- **Procedure:** 10,000 seeded permutations for each league-season under two nulls.
  The global-round null moves complete rounds anywhere; the phase-preserving null
  moves rounds only within their season half. Both preserve fixtures and home/away.
- **Result:** all 5,780,000 requested draws were valid. Each null has 11 of 289
  nominal upper-tail p-values below 0.05; the same 11 seasons appear under both.
  No result survives Benjamini-Hochberg correction within null (minimum q=0.318).
  Mean observed absolute SSB is 0.1806 versus null means of about 0.1948.
- **Diagnostics:** maximum Monte Carlo standard error is 0.0050; coverage and
  exclusions are published by league-season. The vectorized implementation is
  seed-reproducible and tested independently on a small round-robin schedule.
- **Limitation:** the null excludes unobserved broadcasting, policing, travel and
  shared-stadium restrictions. Multiple-testing correction addresses screening,
  not missing real-world scheduling constraints.
- **Decision:** **advance** as a methodological null benchmark. There is no evidence
  of a systematic excess of imbalance, and no individual season survives FDR control.
