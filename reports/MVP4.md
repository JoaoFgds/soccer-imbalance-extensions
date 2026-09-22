# MVP 4 — Constraint-preserving counterfactual schedules

- **Data:** latest usable season for 19 leagues.
- **Procedure:** 250 seeded permutations per league-season, moving complete rounds
  as units while preserving fixtures and home/away assignments.
- **Result:** 4,750/4,750 requested draws were valid. No observed league-season
  fell in the upper 5% tail of mean absolute market-strength SSB.
- **Diagnostics:** median null SD is below 0.05; all reported simulations preserve
  the number and identity of rounds.
- **Limitation:** the null excludes unobserved broadcasting, policing, travel and
  shared-stadium restrictions. Liga Portugal did not satisfy the strict latest-
  season integration rules and was not silently substituted.
- **Decision:** **advance** as a methodological null benchmark. The strong null is
  informative: observed round ordering is not unusually imbalanced under this null.
