# Main analysis: schedule imbalance and economic heterogeneity

## Research position

The evidence supports a paper centered on **heterogeneous observational
associations**, not a universal or causal effect of schedule order. MVP 1 supplies
the leakage-free measurement and average-effect baseline; MVP 3 provides the main
substantive result; MVP 4 supplies a counterfactual benchmark showing that the
observed schedules are not unusually imbalanced relative to constrained round
reorderings.

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
The negative sign appears in all 20 leave-one-league-out refits and in all three
outcomes when schedule strength is measured with verified pre-match Elo.

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

The conditional pattern remains recognizable. At low prior inequality, the
high-value estimate is +0.164 PPG (95% CI [0.034, 0.294]) and the low-value estimate
is -0.105 (95% CI [-0.235, 0.025]); at high inequality both are near zero. This
supports qualitative robustness while showing that the headline three-way estimate
is less precise under a strictly ordered exposure.

## Counterfactual benchmark

MVP 4 evaluates 289 league-seasons under two fixture-preserving nulls with 10,000
draws per league-season/null (5.78 million valid draws). There are 22 nominal
upper-tail findings and none after within-null false-discovery-rate correction.
Mean observed absolute SSB is 0.1806, compared with approximately 0.1948 under both
nulls. The observed schedules therefore do not show systematic excess imbalance
relative to the modeled round-order constraints.

## Claims supported by the evidence

The defensible main claim is:

> Schedule order has a near-zero average association with season performance, but
> its association varies with clubs' relative economic position and league
> inequality. This heterogeneity is qualitatively stable under preceding-season
> financial measures, while constrained schedule permutations show no systematic
> excess imbalance in observed calendars.

The analysis does **not** support claims that schedule order causes performance,
that the released values are independently verified pre-season snapshots, or that
poorer clubs are especially harmed in the most unequal leagues.

## Recommended paper structure

1. Leakage-free continuous SSB and the precise average null (MVP 1).
2. Economic heterogeneity, overlap and robustness (MVP 3).
3. Temporal provenance audit and preceding-season sensitivity.
4. Constraint-preserving schedule benchmark (MVP 4).
5. Null short-run and attendance mechanisms as bounded appendix results (MVPs 2
   and 5).
