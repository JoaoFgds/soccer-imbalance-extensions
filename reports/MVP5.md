# MVP 5 — Schedule shocks and attendance

- **Data:** 101,076 home-match observations after excluding 2020–2021; positive
  observed attendance is available for 99.72% of candidate matches.
- **Model:** within-home-team-season log-attendance regression with prior schedule
  shock, own/opponent Elo, opponent market value, rest, weekend and season progress.
- **Result:** schedule-shock coefficient -0.0043 log points per 100 Elo, 95% CI
  [-0.0108, 0.0022], p=0.1925. Opponent market value and weekend indicators are
  positive and precisely estimated.
- **Diagnostics:** the schedule-shock interval lies inside the ±0.02 log-point
  minimum effect. Raw observed attendance is used; the reference project's
  pseudo-occupancy ratio is not used.
- **Limitation:** no historical capacity, ticket price, sell-out censoring or
  broadcast-slot data are available.
- **Decision:** **discard the tested linear sequence-demand mechanism**. The data
  remain useful for a separate opponent-attractiveness study, which is outside
  the five ranked proposals.
