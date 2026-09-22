# Robustness review after the second validation pass

## Purpose

This review stresses the two MVPs retained for continued analysis without starting
article drafting. It distinguishes directional replication, inferential precision,
temporal ordering and construct validity. Passing one dimension does not imply
passing the others.

## MVP 3: what survived

| Stress test | Result | Assessment |
|---|---:|---|
| Original league-season clustered model | -0.6401; 95% CI [-1.1954, -0.0849] | Negative and conventionally precise |
| Leave one league out | 20/20 negative; range [-0.797, -0.470] | Strong directional stability across leagues |
| Six safe outcome/SSB combinations | 6/6 negative | Direction survives outcome and schedule-strength choices |
| Fixed season-start Elo | -0.7631; 95% CI [-1.4285, -0.0976] | Not driven by within-season Elo updating |
| Fixed-start Elo, 20-league clustering | -0.7631; 95% CI [-1.4633, -0.0628] | Survives conservative clustering |
| 2018–2024 same-season holdout | -0.7340; 95% CI [-1.7828, 0.3149] | Direction replicates; precision does not |

These checks make a pure coding artifact, one-league artifact or dynamic-Elo artifact
less plausible. They do not establish causality.

## MVP 3: what did not survive cleanly

| Stress test | Result | Consequence |
|---|---:|---|
| Primary model, 20-league clustering | 95% CI [-1.3304, 0.0501], p=0.0672 | Inference depends on clustering level |
| Current values on lagged-eligible sample | -0.5597; 95% CI [-1.1903, 0.0709] | Sample restriction alone removes conventional precision |
| Preceding-season values | -0.4721; 95% CI [-1.0708, 0.1266] | Ordered exposure retains sign, not precision |
| Lagged-sample selection | log-value SMD 0.927 | Lagged coverage strongly favors higher-value clubs |
| Lagged 2004–2010 era | +0.9820; 95% CI [-0.1830, 2.1470] | Sign is not homogeneous across eras |
| Same-season era splits | all negative; every CI crosses zero | Era-level estimates are underpowered/imprecise |

The correct interpretation is a robust negative direction with fragile precision,
not a settled effect. The lagged model is informative about timing but is affected
by non-random availability.

## MVP 4: corrected and expanded null benchmark

The permutation implementation now ranks every strength vector internally. This is
required because SSB is a Spearman correlation and makes the null invariant to
monotonic transformations. An automated test protects that property.

| Strength proxy | League-seasons | Nominal source/null rows | FDR rows | Mean observed | Mean null |
|---|---:|---:|---:|---:|---:|
| Market-value rank | 289 | 22 | 0 | 0.1806 | about 0.1948 |
| Fixed season-start Elo rank | 286 | 42 | 4 | 0.1848 | about 0.1948 |

The four Elo FDR rows are LaLiga2 2016 and 2024 under both nulls. Neither season
survives FDR with market-value strength, so the number of source-consistent FDR
findings is zero. The median rank correlation between strength sources is 0.578;
43 of 286 correlations are below 0.30. Individual anomalies therefore depend on
the construct used for “strength.”

The stable finding is the aggregate null: observed average absolute SSB is below
the permutation mean for both proxies. The analysis does not show that real
calendars are systematically more imbalanced than the modeled alternatives.

## Updated evidence classification

- **MVP 1:** precise average null; retain as measurement and baseline evidence.
- **MVP 2:** tested short-run linear performance mechanism remains unsupported.
- **MVP 3:** retain as observational, hypothesis-generating heterogeneity. The
  direction is robust; precision, temporal homogeneity and financial timing are not.
- **MVP 4:** retain as a methodological benchmark and aggregate null. Do not promote
  proxy-specific season anomalies as replicated findings.
- **MVP 5:** tested linear attendance mechanism remains unsupported.

## Predeclared mechanism gate

The post-review mechanism plan was committed before execution. It tested four
three-match implications on 160,382 team-match rows with fixed season-start Elo,
preceding-season financial variables, team-season fixed effects, two-way clustered
inference and symmetric future-schedule controls.

No implication passes the directional Holm family. Short-rest fatigue and
long-recovery adaptation remain too imprecise for strong exclusion. Financial
buffering and its inequality attenuation are near zero with 95% intervals inside
the ±0.05 minimum-effect range; their future controls pass Holm-adjusted
equivalence. The same-season sensitivity is likewise null. The stable MVP 3 sign
therefore remains unexplained at a three-match horizon.

## Remaining threat hierarchy

1. **Mechanism ambiguity:** predeclared three-match fatigue, adaptation and depth
   implications fail; a cumulative season-path process remains untested.
2. **Financial timing:** no dated pre-season snapshots exist in the released data.
3. **Dependence and power:** 20 independent leagues make conservative inference
   materially wider than league-season clustering.
4. **Historical instability:** the earliest lagged era reverses direction.
5. **Counterfactual constraints:** round permutations omit broadcasting, policing,
   travel and stadium-sharing constraints.

## Recommended next gate

Before article writing, reconcile the season-level and match-level scales. Use a
fixed set of cumulative early-, middle- and late-season exposure paths, the existing
late temporal holdout and symmetric future-order controls. The goal is to determine
whether MVP 3 reflects a distributed seasonal path or residual schedule geometry,
not to search additional rolling-window specifications.
