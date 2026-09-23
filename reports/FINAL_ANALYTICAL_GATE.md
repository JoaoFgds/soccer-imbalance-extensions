# Final analytical gate: cumulative season paths

## Pre-analysis status

The specification was committed as `e9726f0` before execution. This is the final
planned analysis before article writing. It tests whether the season-level MVP 3
interaction can be connected to cumulative match-level exposure after all four
three-match mechanisms failed.

## Measurement bridge passes

Across 5,576 team-seasons, the correlation between fixed-start-Elo SSB and the
early-minus-late opponent-strength contrast is 0.733, above the predeclared 0.60
threshold. Eighteen of 20 leagues independently exceed 0.60; J1 League is 0.595
and J2 League is 0.555.

This establishes that the phase-path contrast and SSB capture substantially the
same calendar-order construct. A failure of the outcome models cannot be attributed
to an unrelated cumulative exposure definition.

## Cumulative outcome gate

The primary model contains 160,382 team-match rows, 5,078 team-seasons, 87,825
fixtures and all 20 leagues. It uses fixed-start opponent Elo, preceding-season
financial variables, team-season fixed effects and two-way clustered inference.

| ID | Phase and implication | Past estimate | 95% CI | Holdout estimate | Future control | Result |
|---|---|---:|---:|---:|---|---|
| E1 | early resource buffering | -0.034 | [-0.148, 0.080] | +0.072 | not equivalent | unsupported |
| E2 | early attenuation by inequality | +0.002 | [-0.089, 0.093] | +0.000 | not equivalent | unsupported |
| M1 | middle resource buffering | +0.043 | [-0.235, 0.322] | +0.036 | not equivalent | unsupported |
| M2 | middle attenuation by inequality | -0.034 | [-0.246, 0.178] | +0.051 | not equivalent | unsupported |
| L1 | late resource buffering | -0.243 | [-0.699, 0.212] | -0.012 | not equivalent | unsupported |
| L2 | late attenuation by inequality | -0.082 | [-0.389, 0.225] | -0.044 | not equivalent | unsupported |

All six directional Holm p-values equal 1.000. None passes conservative
league-clustered inference, and none of the six future controls passes equivalence.
The predeclared combined middle/late requirement therefore fails.

Same-season financial sensitivities also provide no past cumulative signal. They
do, however, show a large early future-resource association, reinforcing that
remaining schedule order contains structure that should not be interpreted as a
causal exposure.

## Schedule geometry and precision

Past and future cumulative shocks correlate at -0.233 overall, -0.460 in the early
phase, -0.255 in the middle and -0.464 in the late phase. This is expected because
opponents remaining in a balanced schedule partly complement opponents already
faced. Separate past and future models avoid unstable joint estimation, while the
failed future equivalence prevents identification of a past-only mechanism.

Cumulative shock variation also narrows as the season progresses: past-shock SD is
about 14.2 Elo early, 4.8 Elo in the middle and 3.8 Elo late. The middle/late
intervals consequently remain broad. The result is absence of an identified
cumulative mechanism, not a precise exclusion of every possible cumulative effect.

## Final classification

**Scale linked, mechanism not identified.** SSB is demonstrably connected to the
early-versus-late path measure, but neither local nor cumulative outcome models
identify fatigue, adaptation or financial buffering. The stable MVP 3 direction
must remain an unexplained observational interaction.

## Analysis freeze

The planned analytical program is complete. Further searches over windows, phase
cutoffs, subgroups or alternative signs would add researcher degrees of freedom
without resolving the failed negative controls. The defensible next action is to
freeze the claims and begin writing. New analyses should be limited to correcting
errors, responding to external review or evaluating genuinely new data.

