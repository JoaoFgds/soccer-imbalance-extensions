# Main analysis: schedule imbalance and economic heterogeneity

## Research position

The evidence supports continued analysis of **heterogeneous observational
associations**, not yet a definitive article claim and not a universal or causal
effect of schedule order. MVP 1 supplies the leakage-free measurement and
average-effect baseline; MVP 3 provides a stable directional pattern whose
precision depends on inference and period; MVP 4 supplies a counterfactual
benchmark showing that observed schedules are not systematically more imbalanced
than constrained round reorderings.

## Baseline: the average association is a precise null

Across 5,942 usable team-seasons, continuous pre-match-Elo SSB has an adjusted
association of 0.0061 points per game per full SSB unit (95% CI [-0.0279, 0.0402],
p=0.7243). The interval lies inside the predeclared ±0.10 PPG effect of scientific
interest. Schedule order therefore has no substantively important average
association after adjustment for market value and league/year effects.

This null is the reason to study effect heterogeneity rather than continue searching
for a universal mean effect.

## Main result: resource position and league inequality jointly moderate SSB

The same-season MVP 3 model estimates an SSB × relative squad value × league
market-value Gini interaction of -0.6401 (95% CI [-1.1954, -0.0849], p=0.0238).
The negative sign appears in all 20 leave-one-league-out refits and in all six
outcome/measurement combinations using dynamic pre-match Elo or Elo fixed at the
start of the team-season.

The interpretable result is not that poorer clubs suffer more in highly unequal
leagues. The differentiation is strongest in relatively balanced leagues:

- at low inequality, low-value clubs have an estimated -0.123 PPG SSB association
  (95% CI [-0.222, -0.025]), while high-value clubs have +0.179
  (95% CI [0.059, 0.300]);
- at high inequality, both conditional estimates are near zero.

All nine resource-by-inequality support cells contain at least 429 observations, and
no single league creates the sign. A quadratic specification is borderline
(p=0.051), while a cubic spline does not improve AIC, so the linear interaction is a
compact summary rather than proof of a globally linear mechanism.

## Measurement and inference stress tests

Fixing every opponent's strength at its first pre-match Elo of the season removes
within-season rating updates from the schedule metric. The three-way estimate is
-0.7631 (95% CI [-1.4285, -0.0976], p=0.0246), and remains negative when standard
errors are clustered by only 20 leagues (95% CI [-1.4633, -0.0628], p=0.0343).
This strengthens the conclusion that the direction is not an artifact of Elo
updating after earlier results.

The same conservative league-level clustering is less favorable to the primary
dynamic-Elo model: its point estimate remains -0.6401, but the interval widens to
[-1.3304, 0.0501] (p=0.0672). Thus the signal is measurement-robust but its
statistical decisiveness is not invariant to the clustering unit.

The reserved 2018–2024 holdout also retains a negative estimate (-0.7340), while
its 95% interval is wide [-1.7828, 0.3149]. Same-season estimates are negative in
the early, middle and late eras, but no era alone is precise. The evidence is
compatible with a recurring directional pattern, not with a time-invariant effect
of known magnitude.

## Temporal audit and ordered sensitivity

The article describes market value as pre-season financial data, but the released
provenance cannot establish that timing. The 451 historical Bronze CSVs were
bulk-collected on 2026-03-18; their rows contain a season identifier but no valuation
timestamp. The scraper validates `saison_id`, which identifies the selected season,
not the point within that season at which values apply.

To avoid relying on the disputed timing, the sensitivity model uses each club's
preceding-season value and the preceding composition of its current league. It
retains 5,078 team-seasons (85.4%) across 288 league-seasons. The three-way estimate
remains negative at -0.4721 and stays negative in all 20 league exclusions, but its
95% interval crosses zero [-1.0708, 0.1266] (p=0.1222).

This loss of precision is partly a sample-composition effect. Restricting the
same-season model to the 5,078 observations with a lagged value changes the estimate
to -0.5597 with CI [-1.1903, 0.0709] before the value definition is changed. The
retained clubs have markedly higher same-season log market value than excluded
clubs (standardized mean difference 0.927). The lagged sample is therefore not a
neutral subset, especially for promoted or less-covered clubs.

The conditional pattern remains recognizable. At low prior inequality, the
high-value estimate is +0.164 PPG (95% CI [0.034, 0.294]) and the low-value estimate
is -0.105 (95% CI [-0.235, 0.025]); at high inequality both are near zero. This
supports qualitative robustness while showing that the headline three-way estimate
is less precise under a strictly ordered exposure.

Temporal homogeneity is also limited: the preceding-season estimate is positive in
2004–2010 (+0.9820) and negative in 2011–2017 (-0.8602) and 2018–2024 (-0.7368),
with all three intervals crossing zero. The full-period lagged sign should not be
presented as uniformly reproduced in every era.

## Counterfactual benchmark

MVP 4 evaluates two pre-schedule strength definitions under two fixture-preserving
nulls with 10,000 draws per league-season/source/null (11.50 million valid draws).
Market value covers 289 league-seasons and yields 22 nominal findings but none
after within-source/null FDR correction. Fixed season-start Elo covers 286, yields
42 nominal findings and four FDR rows corresponding to LaLiga2 2016 and 2024 under
both nulls.

None of those league-season/null findings survives FDR under both strength proxies.
The median within-season rank agreement between the proxies is 0.578, and 43 of 286
correlations are below 0.30. Mean observed absolute SSB is 0.1806 for market value
and 0.1848 for fixed Elo, versus null means near 0.1948. The robust aggregate result
is absence of systematic excess imbalance; individual anomalies are sensitive to
the definition of strength.

## Claims supported by the evidence

The defensible working conclusion is:

> Schedule order has a near-zero average association with season performance, but
> its association varies with clubs' relative economic position and league
> inequality. The heterogeneity sign is stable across schedule-strength measures,
> league exclusions and a late temporal holdout, but its precision weakens under
> conservative clustering and temporally ordered financial measures. Constrained
> permutations show no source-consistent excess imbalance in observed calendars.

The analysis does **not** support claims that schedule order causes performance,
that the released values are independently verified pre-season snapshots, or that
poorer clubs are especially harmed in the most unequal leagues. It also does not
support a homogeneous effect across eras or a replicated list of anomalous seasons.

## Mechanism-falsification result

The four match-level implications were committed before execution and evaluated in
one joint model on 160,382 ordered team-match observations. None survives the
predeclared directional Holm family:

- short-rest fatigue: +0.0099 points, 95% CI [-0.0742, 0.0939];
- long-recovery adaptation: +0.0001, 95% CI [-0.0612, 0.0613];
- financial resource buffering: -0.0007, 95% CI [-0.0323, 0.0309];
- attenuation of buffering with inequality: -0.0023, 95% CI
  [-0.0283, 0.0238].

The resource-related future controls pass multiplicity-adjusted equivalence, and
the past resource intervals are entirely inside the ±0.05 minimum-effect range.
The same-season sensitivity is also null. Thus the stable season-level MVP 3 sign
cannot currently be explained by a three-match fatigue, adaptation or financial
buffering process.

An exploratory hierarchy diagnostic finds that future schedule shock varies with
current performance by league inequality. This reinforces the need to model
calendar geometry before attaching a causal mechanism to SSB.

## Next analysis gate before article writing

The next highest-value step is scale reconciliation: predeclare cumulative early-,
middle- and late-season exposure-path tests rather than search over more rolling
windows. The temporal holdout and symmetric future-order controls should remain
mandatory. Article drafting should still wait because the heterogeneity is robust
in direction but mechanistically unresolved.
