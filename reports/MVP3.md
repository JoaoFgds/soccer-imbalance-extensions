# MVP 3 — Economic inequality moderation

- **Data:** 5,942 team-seasons across 20 leagues; market-Gini SD 0.1102.
- **Primary model:** points per game on dynamic pre-match-Elo SSB, centered team
  market value, league-season market Gini and all interactions, with league/year
  effects and league-season clustered SE.
- **Primary result:** three-way interaction -0.6401, 95% CI [-1.1954, -0.0849],
  p=0.0238. The SSB × relative-value interaction is 0.3149, p=0.0043.
- **Marginal effects:** at low league inequality, the estimated SSB association is
  -0.123 PPG (95% CI [-0.222, -0.025]) for low-value clubs and +0.179
  (95% CI [0.059, 0.300]) for high-value clubs. At high inequality, both estimates
  are close to zero. These are conditional associations over one full SSB unit.
- **League sensitivity:** all 20 leave-one-league-out estimates retain the negative
  three-way sign; estimates range from -0.797 to -0.470. No single league creates
  the result, although three exclusions make the 95% interval include zero.
- **Schedule-strength timing:** replacing dynamic Elo with one fixed Elo rating
  observed at the start of each team-season gives -0.7631, 95% CI
  [-1.4285, -0.0976], p=0.0246. With conservative clustering by 20 leagues and a
  t reference, the fixed-start result remains negative with CI
  [-1.4633, -0.0628], p=0.0343. Across PPG, goal difference and win rate, all six
  temporally safe dynamic/fixed-Elo specifications retain the negative sign.
- **Inference stress test:** clustering the primary model by 20 leagues rather
  than 306 league-seasons leaves the point estimate unchanged but widens the CI
  to [-1.3304, 0.0501], p=0.0672. The headline result is therefore not decisive
  under the most conservative clustering choice.
- **Temporal validation:** the 2018–2024 holdout estimate is -0.7340, 95% CI
  [-1.7828, 0.3149], p=0.1702. Same-season estimates are negative in all three
  eras, but each era-specific interval crosses zero. The preceding-season model
  reverses sign in 2004–2010 (+0.9820) and is negative in 2011–2017 and 2018–2024,
  so temporal homogeneity is not established.
- **Lagged-value decomposition:** the preceding-season sensitivity retains 5,078
  observations (85.4%). Restricting the original current-value model to those
  observations changes the estimate from -0.6401 to -0.5597 and already makes
  the CI cross zero; replacing the exposure with preceding-season value then
  changes it to -0.4721, 95% CI [-1.0708, 0.1266], p=0.1222. Missing lagged values
  are selective: retained clubs have much higher current log market value than
  excluded clubs (standardized mean difference 0.927).
- **Functional form and support:** all nine resource-by-inequality tertile cells
  contain at least 429 team-seasons and SSB SDs between 0.211 and 0.234. A
  quadratic term is borderline (p=0.051), while a cubic spline does not improve
  AIC. The linear interaction is a compact summary, not proof of global linearity.
- **Predeclared mechanism gate:** zero of four three-match implications is
  supported after Holm correction. Fatigue and adaptation remain imprecise, while
  both resource-buffering coefficients are near zero with 95% intervals inside
  ±0.05 match points per 100-Elo shock. Same-season sensitivities are also null.
- **Final cumulative-path gate:** fixed-start SSB correlates 0.733 with the
  early-minus-late strength path across 5,576 team-seasons, so the measurement
  bridge passes. Nevertheless, 0/6 phase-specific cumulative implications pass;
  every directional Holm p is 1.000 and no future control is equivalent. Final
  classification: scale linked, mechanism not identified.
- **Decision:** **advance as observational, hypothesis-generating heterogeneity**.
  The sign survives unusually broad measurement and leave-one-league-out checks,
  but conservative clustering, holdout precision, early-era reversal in the
  lagged model, selective lagged coverage and failure of both mechanism gates
  prevent a definitive or causal claim.
