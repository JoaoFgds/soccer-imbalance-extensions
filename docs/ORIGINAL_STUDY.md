# Original study and extension boundary

## Published content

The source of truth is *The Impact of Strength of Schedule Balance on Tournament
Efficacy* (Marchetti, Batista, and Vaz-de-Melo, ISACE 2026, LNCS 16610,
pp. 258–276, DOI: 10.1007/978-3-032-27272-0_18).

- **Research question:** whether the temporal ordering of opponent strength in a
  double round-robin football league is associated with tournament efficacy and
  final standings.
- **Central contribution:** Strength of Schedule Balance (SSB), defined as the
  Spearman correlation between the order in which a team first meets its
  opponents and the ideal ordering of those opponents from strongest to weakest.
- **Imbalance:** positive SSB represents a front-loaded difficult schedule;
  negative SSB represents a back-loaded difficult schedule. The paper primarily
  groups observations using magnitude thresholds such as 0.3.
- **Impact:** differences in final league position among hard-start, balanced,
  and easy-start schedules.
- **Data:** Transfermarkt final standings, match schedules, attendance fields,
  and squad market values; 5,944 team-seasons, 306 validated seasons, 20 leagues,
  11 countries, 2004–2024.
- **Observation unit:** team-season.
- **Methods:** Spearman correlation, Mann–Whitney U tests, and season-stratified
  Cliff's delta with threshold/significance sensitivity analyses.
- **Main result:** most schedules are classified as balanced; easy starts show
  more consistent favorable associations than hard starts, but effects are
  heterogeneous and usually negligible or statistically non-significant.
- **Limitations relevant here:** discretization of a continuous metric;
  non-linearity; unmodelled dependence and confounding; use of final standings
  as an oracle strength proxy; and outcomes other than final rank.

## Implemented in the reference project

The reference repository contains raw team schedules, validation and
normalization routines, market-value integration, SSB calculations, attendance
aggregation, non-parametric tests, and a consolidated team-season dataset.
These implementations were inspected but not copied: the repository has no
versioned `LICENSE` file, despite an MIT statement in its README.

## New content in this repository

This repository independently implements:

1. pre-match Elo ratings and tests preventing future-information leakage;
2. a continuous SSB based on first encounters and pre-match opponent ratings;
3. match-level local schedule shocks with two-, three-, and five-match windows;
4. market-inequality moderation models;
5. constraint-preserving round permutations;
6. within-team-season attendance models;
7. explicit minimum effects of scientific interest for triage decisions.

The analyses are screening MVPs. They do not replace or silently modify the
published results.
