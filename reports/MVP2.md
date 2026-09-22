# MVP 2 — Local opponent-strength shocks

- **Data:** 212,262 team-match observations with within-team-season variation.
- **Model:** next-match points on prior opponent-strength shock, own/opponent Elo,
  home status, rest, and season progress; team-season demeaning and clustered SE.
- **Result:** three-match coefficient 0.0119 points per 100 Elo, 95% CI
  [-0.0055, 0.0294], p=0.1811.
- **Sensitivity:** window 2 = -0.0062 [-0.0197, 0.0073]; window 5 = 0.0135
  [-0.0113, 0.0383]. No window supports the hypothesized negative mechanism.
- **Diagnostics:** all three intervals lie within the ±0.05-point minimum effect;
  temporal leakage tests pass.
- **Limitation:** a linear rolling mean may miss rare nonlinear clusters or effects
  mediated through injuries and lineup rotation.
- **Decision:** **discard the tested short-run linear mechanism**. A future study
  would need a substantively different exposure, not a larger sample of this model.
