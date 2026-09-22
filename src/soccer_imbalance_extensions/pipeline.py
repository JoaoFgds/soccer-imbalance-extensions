from __future__ import annotations

import logging
from pathlib import Path

import yaml

from .analysis import run_mvp1, run_mvp2, run_mvp3, run_mvp4, run_mvp5, save_summary
from .data import discover_source, load_market_values, load_matches, load_standings, write_json
from .features import add_elo, to_team_match

LOGGER = logging.getLogger(__name__)


def run_pipeline(source_root: Path, project_root: Path, only: int | None = None) -> list[dict]:
    config = yaml.safe_load((project_root / "configs/mvps.yaml").read_text(encoding="utf-8"))
    tables = project_root / "results/tables"
    figures = project_root / "results/figures"
    reports = project_root / "reports"
    processed = project_root / "data/processed"
    layout = discover_source(source_root)
    LOGGER.info("Loading standings from %s", layout.standings)
    standings = load_standings(layout)
    market_values = load_market_values(layout)
    LOGGER.info("Loading and validating schedule files")
    matches, diagnostics = load_matches(layout, standings)
    diagnostics.update(
        {
            "standings_rows": len(standings),
            "leagues": int(standings["league_name"].nunique()),
            "valid_league_seasons": int(standings[["league_name", "season_year"]].drop_duplicates().shape[0]),
            "season_min": int(standings["season_year"].min()),
            "season_max": int(standings["season_year"].max()),
        }
    )
    write_json(reports / "data_diagnostics.json", diagnostics)
    elo = config["elo"]
    matches = add_elo(
        matches,
        initial=float(elo["initial"]),
        k_factor=float(elo["k_factor"]),
        home_advantage=float(elo["home_advantage"]),
        regression=float(elo["between_season_regression"]),
    )
    team_matches = to_team_match(matches)
    processed.mkdir(parents=True, exist_ok=True)
    matches.to_csv(processed / "matches_with_pre_match_elo.csv.gz", index=False, compression="gzip")
    team_matches.to_csv(processed / "team_matches.csv.gz", index=False, compression="gzip")
    results: list[dict] = []
    team_seasons = None
    if only in (None, 1, 3):
        team_seasons, result = run_mvp1(standings, team_matches, tables, figures, config["criteria"])
        if only in (None, 1):
            results.append(result)
        team_seasons.to_csv(processed / "team_seasons_continuous_ssb.csv.gz", index=False, compression="gzip")
    if only in (None, 2):
        results.append(run_mvp2(team_matches, tables, figures, config["criteria"]))
    if only in (None, 3):
        if team_seasons is None:
            team_seasons, _ = run_mvp1(standings, team_matches, tables, figures, config["criteria"])
        results.append(
            run_mvp3(
                team_seasons,
                team_matches,
                tables,
                figures,
                config["criteria"],
                market_values,
            )
        )
    if only in (None, 4):
        results.append(run_mvp4(matches, standings, tables, figures, config["mvp4"], int(config["seed"])))
    if only in (None, 5):
        results.append(run_mvp5(matches, team_matches, standings, tables, figures, config["mvp5"], config["criteria"]))
    save_summary(results, tables, reports, diagnostics)
    return results
