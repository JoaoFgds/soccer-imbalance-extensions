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
- **Alternative specifications:** all six temporally safe combinations of three
  outcomes and two schedule-strength definitions retain the negative sign. The
  random-intercept league model converges and also retains the sign, but its league
  variance is effectively zero (7.8e-12), so it is only a sign check. A quadratic
  nonlinearity test is borderline (p=0.051; AIC 1768.7 versus 1775.1 linear), while
  the cubic spline does not improve AIC (1777.0). The linear interaction remains a
  useful summary, but not the only plausible functional form.
- **Support:** all nine resource-by-inequality tertile cells contain at least 429
  team-seasons and SSB SDs between 0.211 and 0.234.
- **Limitation:** the released input has no row-level market-value snapshot date.
  The article's pre-season interpretation is recorded, but independent temporal
  verification remains pending. Final-rank SSB is reported only as a post-season
  diagnostic and is excluded from temporal-robustness criteria.
- **Decision:** **advance**, with the timestamp audit as a prerequisite for a
  defensible temporal or causal interpretation.
