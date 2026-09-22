# Data, provenance, and reuse conditions

## Inventory

| Source | URL / pattern | Access | Unit | Observed coverage | Missing / quality | Redistribution | MVPs |
|---|---|---|---|---|---|---|---|
| Published reproducibility release | `github.com/JoaoFgds/soccer-scraper/releases/tag/reproducibility-v1` | 2026-09-22 | team-season and team-match files | 5,944 standings rows; 306 league-seasons; 20 leagues; 2004–2024 | 2 unparsed dates and 1 unparsed result after fixture deduplication | Archives are downloaded to ignored local cache and are not republished | 1–5 |
| Transfermarkt team schedule pilot | `/fc-chelsea/spielplan/verein/631/saison_id/2024` | 2026-09-22 | team-match | Chelsea 2024/25 representative page | A page sample proves structure, not historical completeness | HTML cache ignored; URL, hash, size and checks only are published | 1, 2, 4, 5 |
| Transfermarkt competition-value pilot | `/premier-league/startseite/wettbewerb/GB1/plus/?saison_id=2024` | 2026-09-22 | club-season | Premier League 2024 representative page | A page sample proves structure, not historical completeness | HTML cache ignored; URL, hash, size and checks only are published | 1, 3, 4, 5 |

The executed full analysis read the already-downloaded public release from an
external temporary directory. It did not copy raw data into Git. The acquisition
command downloads the same two release assets, verifies the publisher-provided
SHA-256 values, and extracts them under ignored `data/raw/` storage.

## Reference-project licensing boundary

No `LICENSE`, `NOTICE`, or `COPYING` file is present in the inspected reference
commit `54b4625be98d9710fc41e72bade8f2e68049c920`. Its README states MIT, but the
missing license text leaves attribution and grant details incomplete. Therefore:

- no source code was copied;
- all algorithms here were independently implemented from the paper's methods;
- the original project and paper are credited;
- the new repository intentionally has no license until the owner makes an
  explicit compatible choice.

Transfermarkt is the original data source. Its raw pages and the release archives
are not redistributed here. Researchers must assess the source's current terms
before fresh collection.

## Dependency licenses

Installed package metadata was inspected locally: NumPy, pandas, SciPy and
statsmodels use BSD-family terms; Requests uses Apache-2.0; PyYAML, pytest and
Ruff use MIT; Matplotlib ships its own PSF-compatible license. `uv.lock` fixes
the resolved versions. This inventory is informational, not legal advice.
