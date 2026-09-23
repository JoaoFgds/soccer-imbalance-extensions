# Methodology and operational assumptions

## Temporal safety

Elo ratings are recorded immediately before each match and updated only after
the match result. Across seasons, returning-team ratings regress 25% toward 1500.
The first encounter with each opponent defines the continuous schedule sequence.
Automated tests verify that changing a later result cannot alter an earlier
pre-match rating.

## Models

- MVP 1: cluster-robust OLS for points per game, using continuous SSB, centered
  log market value, their interaction, and league/year fixed effects.
- MVP 2: within-team-season OLS for match points. The primary exposure is the
  mean opponent Elo over the preceding three matches relative to the
  league-season mean; windows two and five are sensitivities.
- MVP 3: cluster-robust OLS with continuous SSB, relative market value, league
  market-value Gini, and their three-way interaction. Robustness checks include
  marginal effects at joint 10th/50th/90th percentiles, leave-one-league-out
  refits, quadratic and cubic-spline functional forms, a league random-intercept
  model, alternative outcomes, two temporally safe schedule-strength definitions
  (dynamic pre-match Elo and fixed season-start Elo), and two separately labelled
  timing diagnostics (same-season market value and post-season final rank). A
  preceding-season market-value sensitivity uses each team's prior value,
  including its prior league when covered, and the prior composition of the
  current league. Additional stress tests cluster at the league level with a
  small-sample t reference, reserve 2018–2024 as a temporal holdout, split the
  sample into eras, and decompose lagged-model changes into sample-selection and
  exposure-timing components.
- MVP 4: 10,000 seeded permutations under both global-round and phase-preserving
  nulls for every usable league-season and each of two pre-schedule strength
  proxies: market-value rank and fixed season-start Elo rank. Both nulls preserve
  fixtures, home/away assignments, and complete rounds; the second also retains
  each round within its season half. Empirical upper-tail probabilities receive
  Benjamini-Hochberg correction separately by strength proxy and null. Cross-proxy
  rank agreement and findings surviving FDR under both strength definitions are
  reported explicitly. These nulls do not encode commercial or policing
  constraints absent from the source.
- MVP 5: within-home-team-season OLS for log observed attendance, excluding
  2020–2021 and controlling for own/opponent Elo, opponent market value, rest,
  weekend, and season progress.

All estimates are associations. The MVPs do not justify causal claims.

## Post-MVP mechanism gate

The timestamped mechanism plan uses exactly three preceding opponents measured by
fixed season-start Elo and a symmetric three-future-opponent control. One joint
within-team-season model tests short-rest fatigue, long-recovery adaptation,
financial resource buffering and attenuation by inequality. Directional tests use
Holm family-wise correction. Future controls use two one-sided equivalence tests
inside ±0.05 points, also Holm-adjusted. Primary covariance is two-way clustered by
team-season and fixture; 20-league clustering is reported as a sensitivity.

## Final cumulative-path gate

The final gate maps fixed-start-Elo SSB to the early-minus-late strength path and
requires an overall Spearman correlation of at least 0.60. Match models use all
prior opponent strength separately from all future opponent strength on an
identical sample with at least three matches on each side. Early, middle and late
resource and inequality interactions form a six-test Holm family. Support also
requires conservative league-clustered directional p < 0.10, sign compatibility in
the 2018–2024 holdout and Holm-adjusted future-control equivalence inside ±0.05
points. A cumulative explanation requires both resource and inequality implications
to pass in the same middle or late phase.

## Assumptions

The article labels the financial data as pre-season, but this label is not
independently recoverable from the released provenance. The 451 Bronze CSVs have
ZIP timestamps of 2026-03-18, after the covered seasons, and neither they nor the
analysis input contains a valuation timestamp. The scraper's `saison_id` check
validates the selected season only. Consequently, same-season market-value models
are descriptive. The preceding-season sensitivity is temporally ordered but
selects materially higher-value clubs: the standardized mean difference in
same-season log market value between retained and excluded observations is 0.927.
It is therefore a useful timing stress test, not an unbiased replacement sample.
