# MVP 3 — Economic inequality moderation

- **Data:** 5,942 team-seasons across 20 leagues; market-Gini SD 0.1102.
- **Model:** points per game on continuous SSB, centered team market value,
  league-season market Gini and all interactions, with league/year effects and
  league-season clustered SE.
- **Result:** three-way interaction -0.6401, 95% CI [-1.1954, -0.0849], p=0.0238.
  The SSB × relative-value interaction is 0.3149, p=0.0043.
- **Diagnostics:** inequality varies both across leagues and seasons; the model has
  5,942 observations and R² 0.4742.
- **Limitation:** the coefficient is exploratory, sensitive to scaling, and needs
  marginal-effect plots, leave-one-league-out checks, and a full timestamp audit
  of market-value snapshots.
- **Decision:** **advance**. This is the most promising full analysis.
