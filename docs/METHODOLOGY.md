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
  model, alternative outcomes, two temporally safe strength definitions, and a
  separately labelled post-season final-rank diagnostic.
- MVP 4: 10,000 seeded permutations under both global-round and phase-preserving
  nulls for every usable league-season. Both preserve fixtures, home/away
  assignments, and complete rounds; the second also retains each round within
  its season half. Empirical upper-tail probabilities receive Benjamini-Hochberg
  correction separately by null. These nulls do not encode commercial or policing
  constraints absent from the source.
- MVP 5: within-home-team-season OLS for log observed attendance, excluding
  2020–2021 and controlling for own/opponent Elo, opponent market value, rest,
  weekend, and season progress.

All estimates are associations. The MVPs do not justify causal claims.

## Assumptions

The user explicitly designated the article as the source of truth. Accordingly,
the market-value snapshot is interpreted as the article's pre-season strength
proxy for exploratory analysis. The released row-level input has no valuation
snapshot timestamp, so independent temporal verification remains a prerequisite
for stronger temporal or causal language.
