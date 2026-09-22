# Mechanism-falsification gate

## Design integrity

The specification was committed as `b30e3e1` before these models were executed.
The primary sample contains 160,382 team-match rows, 5,078 team-seasons, 87,825
fixtures and all 20 leagues. It uses preceding-season financial variables and
opponent Elo fixed at season start.

The design has substantial support: 30,325 observations follow short rest and
83,856 follow long recovery. Past and future shocks have SDs of 0.222 units
(approximately 22 Elo) and correlate at -0.170. The standardized design condition
number is 4.30 and the largest absolute correlation among target interactions is
0.612, providing no indication that the null results are caused by near-collinearity.

## Predeclared gate results

| ID | Implication | Estimate | 95% CI | Holm directional p | Future-control result | Classification |
|---|---|---:|---:|---:|---|---|
| F1 | fatigue under short rest | +0.0099 | [-0.0742, 0.0939] | 1.000 | equivalence failed | unsupported |
| A1 | adaptation after long recovery | +0.0001 | [-0.0612, 0.0613] | 1.000 | equivalence failed | unsupported |
| R1 | financial resource buffering | -0.0007 | [-0.0323, 0.0309] | 1.000 | equivalent; Holm p=0.0038 | unsupported |
| R2 | buffering weakens with inequality | -0.0023 | [-0.0283, 0.0238] | 1.000 | equivalent; Holm p=0.0026 | unsupported |

The unit is match points for a 100-Elo three-opponent shock, crossed with the
listed binary indicator or one standardized modifier. None of the four
directional implications passes Holm correction. Conservative 20-league
clustered intervals also cross zero for every implication.

## Interpretation by mechanism

- **Short-rest fatigue:** the point estimate has the opposite sign from the
  hypothesis. Its interval remains wide enough that moderate harm cannot be ruled
  out, and the future control is not precise enough for equivalence.
- **Long-recovery adaptation:** the estimate is effectively zero, but its interval
  and future control are also too wide for a strong equivalence conclusion.
- **Resource buffering:** both resource coefficients are near zero and their 95%
  intervals lie entirely inside the predeclared ±0.05 minimum-effect range. The
  corresponding future controls pass multiplicity-adjusted equivalence. This is
  positive evidence against the tested three-match resource-buffering explanation.
- **Same-season sensitivity:** all four past estimates remain near zero, including
  resource buffering (-0.0002) and inequality attenuation (-0.0001). The primary
  conclusion is not created by selective preceding-season coverage.

## Additional negative-control diagnostic

The non-target hierarchy term future shock × Gini is positive in the ordered
sample (0.0562, 95% CI [0.0290, 0.0833]) and in the same-season sensitivity
(0.0718, 95% CI [0.0465, 0.0971]). This term was not one of the predeclared
mechanism implications and is not promoted as a finding. It indicates that future
schedule position contains systematic information related to league inequality,
which further cautions against a causal reading of calendar-order associations.

## Decision

**No tested mechanism explains MVP 3.** The three-match fatigue and adaptation
tests are unsupported but not sharply excluded. The three-match financial
buffering mechanism is both unsupported and bounded inside the minimum effect of
interest. MVP 3 therefore remains a season-level observational heterogeneity that
has not been connected to a validated short-run process.

The next analytical gate should reconcile scale: test a fixed set of cumulative
early-, middle- and late-season exposure paths rather than another local rolling
window. That gate should retain the same future-order controls and temporal
holdout, because the Gini-related negative-control diagnostic shows that schedule
geometry itself can carry predictive structure.

