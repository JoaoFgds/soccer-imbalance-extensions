# MVP 1 — Continuous leakage-free SSB

- **Data:** 5,944 team-seasons; 5,942 model observations; SSB coverage 99.97%.
- **Model:** points per game on continuous pre-match-Elo SSB, centered log market
  value, their interaction, and league/year fixed effects; errors clustered by
  league-season.
- **Result:** average SSB coefficient 0.0061, 95% CI [-0.0279, 0.0402], p=0.7243.
  The resource interaction is 0.0619, 95% CI [-0.0032, 0.1270], p=0.0626.
- **Diagnostics:** SSB SD 0.2229; only two team-seasons lack a usable continuous
  SSB. The average-effect interval lies fully inside the ±0.10 PPG minimum effect.
- **Limitation:** Elo settings are screening choices and the linear average may
  hide league/resource heterogeneity.
- **Decision:** **reformulate** toward heterogeneity and non-linearity. Retain the
  leakage-free metric as infrastructure for MVP 3.
