# Pre-analysis plan: cumulative-path final gate

## Status and objective

This is the final analytical gate before article writing. The plan is committed
before execution. It tests whether the season-level MVP 3 interaction can be
reconciled with a distributed path through the early, middle or late season after
the predeclared three-match mechanisms failed.

## Measurement bridge

Opponent strength is fixed at each opponent's first pre-match Elo of the season.
Every team-season is divided by relative match position into:

- early: progress at or below one third;
- middle: above one third and at or below two thirds;
- late: above two thirds.

The phase-path contrast is mean early opponent strength minus mean late opponent
strength. It should be positively associated with fixed-start-Elo SSB because both
represent harder opponents appearing earlier. The measurement bridge passes only
if their Spearman correlation is at least 0.60 among valid team-seasons.

## Match-level exposures and common sample

- Outcome: points in the current match.
- Past exposure: mean fixed-start Elo of every prior opponent, minus the
  league-season strength mean, divided by 100.
- Future negative control: the symmetric mean over every later opponent.
- At least three prior and three future matches are required. Past and future
  models use this identical common sample.
- Primary financial variables: preceding-season relative log market value and the
  preceding composition of the current league.
- Same-season financial variables are a labelled coverage sensitivity only.

Past and future exposures are fitted in separate models because, in a balanced
schedule, the remaining opponents are close to a deterministic complement of the
opponents already faced. A joint model would make their coefficients needlessly
collinear and would not provide a valid negative-control comparison.

## Fixed models

Within-team-season linear models include phase-specific shock, shock × standardized
relative value, shock × standardized Gini and their three-way interaction. The
hierarchy is retained for every phase. Fixed controls are:

- own and current-opponent dynamic pre-match Elo divided by 100;
- current-opponent fixed-start Elo divided by 100;
- home indicator;
- rest days capped at 30;
- season progress;
- middle- and late-phase indicators.

Primary covariance is two-way clustered by team-season and fixture. A conservative
sensitivity clusters by 20 leagues with a small-sample t reference. Models are fit
for the full 2004–2024 sample and a fixed 2018–2024 holdout.

## Directional family

Six implications form one Holm family at alpha 0.05:

| ID | Phase | Target | Expected sign |
|---|---|---|---:|
| E1 | early | past shock × relative value | positive |
| E2 | early | past shock × relative value × Gini | negative |
| M1 | middle | past shock × relative value | positive |
| M2 | middle | past shock × relative value × Gini | negative |
| L1 | late | past shock × relative value | positive |
| L2 | late | past shock × relative value × Gini | negative |

For one implication to be supported, all conditions must hold:

1. full-sample one-sided Holm p < 0.05;
2. conservative league-clustered one-sided p < 0.10;
3. holdout estimate retains the expected sign;
4. the matching future exposure passes equivalence.

## Future-control equivalence

The six phase-matched future coefficients form a separate Holm family. Equivalence
uses two one-sided normal tests and a 90% interval inside `[-0.05, 0.05]` match
points per 100-Elo shock interaction. A conventional p-value above 0.05 does not
count as a passed control.

## Final classification

- **Cumulative mechanism supported:** the measurement bridge passes and both the
  resource and inequality implications are supported in the same middle or late
  phase (`M1` + `M2`, or `L1` + `L2`).
- **Scale linked, mechanism not identified:** the measurement bridge passes but no
  middle/late pair passes the full gate.
- **Scale not reconciled:** the measurement bridge fails.

Early-phase results describe trajectory onset but cannot alone satisfy the final
mechanism gate. No phase, sign, threshold or family is changed after execution.

