# MVP 3 — Economic inequality moderation

- **Data:** 5,942 team-seasons across 20 leagues; market-Gini SD 0.1102.
- **Model:** points per game on continuous SSB, centered team market value,
  league-season market Gini and all interactions, with league/year effects and
  league-season clustered SE.
- **Result:** three-way interaction -0.6401, 95% CI [-1.1954, -0.0849], p=0.0238.
  The SSB × relative-value interaction is 0.3149, p=0.0043.
- **Marginal effects:** at low league inequality, the estimated SSB association is
  -0.123 PPG (95% CI [-0.222, -0.025]) for low-value clubs and +0.179
  (95% CI [0.059, 0.300]) for high-value clubs. At high inequality, both estimates
  are close to zero. These are conditional associations over one full SSB unit.
- **League sensitivity:** all 20 leave-one-league-out estimates retain the negative
  three-way sign; estimates range from -0.797 to -0.470. No single league creates
  the result, although three exclusions make the 95% interval include zero.
- **Alternative specifications:** all three outcome specifications using verified
  pre-match Elo schedule strength retain the negative sign. Same-season market
  value and final rank are retained as timing diagnostics, not classified as
  temporally verified. The
  random-intercept league model converges and also retains the sign, but its league
  variance is effectively zero (7.8e-12), so it is only a sign check. A quadratic
  nonlinearity test is borderline (p=0.051; AIC 1768.7 versus 1775.1 linear), while
  the cubic spline does not improve AIC (1777.0). The linear interaction remains a
  useful summary, but not the only plausible functional form.
- **Support:** all nine resource-by-inequality tertile cells contain at least 429
  team-seasons and SSB SDs between 0.211 and 0.234.
- **Temporal audit:** the article calls the financial data pre-season, but the 451
  released Bronze CSVs were bulk-collected on 2026-03-18 and contain no valuation
  timestamp. The URL's `saison_id` verifies the season only. A preceding-season
  sensitivity retains 5,078 observations (85.4% coverage) and the negative
  interaction in 20/20 league exclusions: -0.4721, 95% CI [-1.0708, 0.1266],
  p=0.1222. At low prior inequality, the marginal association is -0.105 PPG for
  low-value clubs (CI [-0.235, 0.025]) and +0.164 for high-value clubs
  (CI [0.034, 0.294]); at high inequality both remain near zero.
- **Decision:** **advance as observational heterogeneity**. The qualitative pattern
  survives a genuinely ordered sensitivity, but the three-way term loses precision.
  Do not describe the same-season model as pre-season or causal without a dated
  historical snapshot.
