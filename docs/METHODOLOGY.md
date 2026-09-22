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
  market-value Gini, and their three-way interaction.
- MVP 4: 250 seeded global round-order permutations for the latest usable season
  in each league. This preserves fixtures, home/away assignments, and the fact
  that an existing round is moved as a unit. It does not encode commercial or
  policing constraints absent from the source.
- MVP 5: within-home-team-season OLS for log observed attendance, excluding
  2020–2021 and controlling for own/opponent Elo, opponent market value, rest,
  weekend, and season progress.

All estimates are associations. The MVPs do not justify causal claims.

## Assumptions

The user explicitly designated the article as the source of truth. Accordingly,
the market-value snapshot is interpreted as the article's pre-season strength
proxy. The repository nevertheless records the source and access limitations so
that a full analysis can perform a stricter timestamp audit.
