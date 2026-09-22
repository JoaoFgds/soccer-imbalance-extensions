# Traceability of the five MVPs

The interpretations below were fixed before the final decision pass. “Advance”
means that a full study is empirically justified; “reformulate” means that the
data support a narrower question; “discard” means that the MVP precisely excludes
the predeclared minimum effect for the tested mechanism.

| Rank | Research question | Main hypothesis | Continuity / contribution | Unit and initial scope |
|---:|---|---|---|---|
| 1 | Does continuous, leakage-free SSB predict final performance? | The association is non-linear and varies with initial team strength. | Replaces discrete/oracle SSB with pre-match Elo and continuous modelling. | Team-season; all 306 validated league-seasons. |
| 2 | Do recent difficult-opponent sequences change next-match points? | A difficult prior 3-match block reduces subsequent points. | Tests the dynamic mechanism hidden by the published final-rank outcome. | Team-match; all matches with at least two prior fixtures. |
| 3 | Does economic inequality moderate the SSB association? | Schedule order matters more for low-value clubs in unequal leagues. | Explains published cross-league heterogeneity with market structure. | Team-season; all observations with positive market value. |
| 4 | Are observed schedules more imbalanced than feasible counterfactuals? | Some real leagues lie in the upper tail of valid round-order permutations. | Gives SSB an operational null distribution instead of an arbitrary cutoff. | Team-season/permutation; latest usable season per league. |
| 5 | Does prior schedule difficulty alter home attendance? | Difficult recent sequences reduce later attendance beyond direct opponent appeal. | Adds a new match-level engagement outcome. | Home match; observed attendance, excluding 2020–2021. |

| Rank | Outcome | Exposure and controls | Data / integration key | Initial method and diagnostics | Predeclared decision rule |
|---:|---|---|---|---|---|
| 1 | Points per game | Continuous SSB; centered log market value; league/year effects | Release standings + schedules; `league, season, canonical team` | Cluster-robust OLS; coverage, support, CI, league distributions | Advance only if feasible and not a precise null inside ±0.10 PPG per SSB unit; otherwise reformulate. |
| 2 | Match points | Prior opponent-strength shock; own/opponent Elo, home, rest, season progress | Match ID and team-season ID | Within-team-season OLS; clustered SE; windows 2/3/5 | Discard tested mechanism if 95% CI lies inside ±0.05 points per 100 Elo; otherwise advance/reformulate. |
| 3 | Points per game | `SSB × relative market value × league Gini`; league/year effects | Team-season canonical key | Cluster-robust interaction model; Gini support and league sensitivity | Advance if coverage/variation pass and the primary interaction has p<0.05; otherwise reformulate. |
| 4 | Mean absolute SSB | Observed order versus global round permutations | League-season, round, fixture, team | Seeded Monte Carlo; collision-preserving validation and empirical tail probability | Advance if at least 10 leagues complete all requested valid permutations. |
| 5 | Log attendance | Prior shock; team/opponent Elo, opponent market value, rest, weekend, progress | Match ID plus home-team-season | Within-home-team-season OLS; coverage and COVID exclusion | Discard tested mechanism if 95% CI lies inside ±0.02 log points per 100 Elo; otherwise advance/reformulate. |

Secondary hypotheses are the interaction with team resources (MVPs 1 and 3),
window sensitivity (MVP 2), alternative null placement (MVP 4), and opponent
attractiveness versus accumulated sequence effects (MVP 5).
