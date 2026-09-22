# Temporal audit of market-value exposures

## Scope

This audit checks whether the market-value covariates used in MVP 3 can be
identified as observations available before the corresponding league season.
The source article describes the financial data as “pre-season”, while the
public reproducibility release provides 451 historical Bronze CSVs and the
analysis input provides only season-level values.

## Evidence

| Check | Finding | Consequence |
|---|---|---|
| Row schema | Bronze rows contain `league_name`, `season_year`, `club_name`, squad descriptors and total/average market value; no valuation date or capture timestamp | A row cannot be placed within the season from the released data alone |
| URL contract | The scraper checks the selected Transfermarkt `saison_id` and records the season URL | This identifies a season, not the date on which the displayed value was assessed |
| Release metadata | The 451 historical CSV entries in `market-values-bronze-v1.zip` are dated 2026-03-18; the covered seasons end in 2024 | The bulk collection happened after the seasons and cannot establish a pre-season snapshot |
| Article wording | The paper calls the financial data “pre-season” in its results discussion | This is a source interpretation, not independently reproducible row-level provenance |
| Public page semantics | Transfermarkt's season page lists a selectable season and total market values, but does not expose an intra-season valuation date in the captured schema | The page supports season selection, not temporal placement |
| Ordered sensitivity | Prior-season values cover 5,078 rows (85.4%) and retain a negative interaction in 20/20 league exclusions | The qualitative result is compatible with ordered information, but the confidence interval crosses zero |

The article and public page used for this check are available at the [author's
publication page](https://pedroolmo.github.io/research/publications.html) and the
[Transfermarkt Premier League 2024/25 season page](https://www.transfermarkt.de/premier-league/startseite/wettbewerb/GB1/saison_id/2024).
The frozen archive is the [`reproducibility-v1` release](https://github.com/JoaoFgds/soccer-scraper/releases/tag/reproducibility-v1).

## Decision

The pre-season interpretation is **not independently verified**. Same-season
market-value estimates remain useful descriptive covariates and the main MVP 3
interaction is robust in sign, but neither the same-season estimate nor the
article wording should be presented as causal evidence.

The preceding-season sensitivity is the appropriate temporal robustness check:

- estimate: `-0.4721`;
- 95% CI: `[-1.0708, 0.1266]`;
- p-value: `0.1222`;
- observations: `5,078`;
- league-exclusion sign share: `20/20`.

## What would change the decision

To upgrade the claim, the project would need either dated historical snapshots
captured before each season or an independently documented dataset whose values
are explicitly measured at that point. Without that evidence, the paper should
use “observational association” and report the lagged sensitivity in the main
text or as the primary temporal robustness result.
