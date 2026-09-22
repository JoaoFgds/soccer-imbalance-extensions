# Pre-analysis plan: mechanism-falsification gate

## Status and purpose

This plan is fixed before the mechanism models are executed. It does not alter the
five MVP decisions and is not an article outline. Its purpose is to test whether
observable match-level implications can explain the stable direction of the MVP 3
interaction while remaining compatible with the precise MVP 2 and MVP 5 nulls.

## Analysis population and timing

- Unit: one team in one league match.
- Outcome: points earned in the current match.
- Primary resource sample: teams with a market value from the preceding season and
  a preceding-season Gini for the current league.
- Schedule strength: each opponent's Elo immediately before its first match of the
  current season. This value is fixed for the entire season.
- Exposure: mean fixed-strength Elo of exactly the three preceding opponents,
  minus the league-season mean, divided by 100.
- Negative-control exposure: the identically defined mean for exactly the three
  future opponents. The current opponent is excluded from both windows.
- Same-season market values are a labelled coverage sensitivity only and cannot
  satisfy the primary mechanism gate.

## Fixed model

One joint linear model is estimated after within-team-season demeaning. It contains
both past and future schedule shocks, all mechanism interactions, and these fixed
controls:

- own and current-opponent pre-match Elo, each divided by 100;
- home indicator;
- rest days capped at 30;
- short rest (`rest_days <= 4`);
- long recovery (`rest_days >= 7`);
- season progress.

Relative log market value and league Gini are standardized within the primary
team-season sample before being merged to matches. Their time-invariant main effects
are absorbed by team-season fixed effects. The joint model includes shock × Gini so
the three-way resource coefficient is hierarchically specified.

Primary covariance is two-way clustered by team-season and fixture. A sensitivity
clusters by the 20 leagues with a small-sample t reference. The sensitivity may
qualify a finding but cannot rescue a failed primary gate.

## Directional implications

All four rows form one Holm family at alpha 0.05.

| ID | Mechanism implication | Target coefficient | Expected sign |
|---|---|---|---:|
| F1 | accumulated difficulty is more harmful under short rest | past shock × short rest | negative |
| A1 | accumulated difficulty produces adaptation after long recovery | past shock × long recovery | positive |
| R1 | financial resources buffer accumulated difficulty | past shock × standardized relative value | positive |
| R2 | resource buffering weakens as league inequality rises | past shock × standardized relative value × standardized Gini | negative |

Directional one-sided p-values are computed from the primary clustered estimate and
adjusted together with Holm's family-wise error control. The corresponding
league-clustered estimate must retain the predeclared sign.

## Negative controls and equivalence

Each implication has a future-shock counterpart. A negative control passes only if
its 90% confidence interval is inside `[-0.05, 0.05]` points for a one-unit shock
interaction. Equivalence p-values use two one-sided tests; the larger p-value is
used for the intersection-union test, and the four tests form a separate Holm
family. Merely obtaining p > 0.05 in a conventional difference test is insufficient.

The ±0.05 margin matches the predeclared smallest effect of scientific interest for
MVP 2. Market value and Gini are standardized so the same margin refers to a
100-Elo shock crossed with one standard deviation of the modifier.

## Classification rules

- **Supported:** directional Holm p < 0.05, expected sign retained with conservative
  league clustering, and the matching future control passes Holm-adjusted
  equivalence.
- **Signal but not identified:** directional Holm p < 0.05, but the league sign or
  future-control requirement fails.
- **Unsupported:** the directional Holm test fails.

The combined resource-buffering explanation for MVP 3 requires both R1 and R2 to be
supported. No mechanism is selected or redefined after results are observed.

