from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import spearmanr


def add_elo(matches: pd.DataFrame, initial: float, k_factor: float, home_advantage: float, regression: float) -> pd.DataFrame:
    """Add strictly pre-match Elo ratings; ratings update only after recording a fixture."""
    output: list[pd.DataFrame] = []
    for league, league_frame in matches.groupby("league_name", sort=True):
        ratings: dict[str, float] = {}
        for season, frame in league_frame.groupby("season_year", sort=True):
            ratings = {team: initial + (rating - initial) * (1 - regression) for team, rating in ratings.items()}
            season_rows = []
            for row in frame.sort_values(["kickoff", "round", "match_id"]).itertuples(index=False):
                home = row.home_team_canonical
                away = row.away_team_canonical
                home_pre = ratings.get(home, initial)
                away_pre = ratings.get(away, initial)
                record = row._asdict()
                record["home_elo_pre"] = home_pre
                record["away_elo_pre"] = away_pre
                season_rows.append(record)
                if pd.isna(row.home_points):
                    continue
                expected_home = 1 / (1 + 10 ** ((away_pre - (home_pre + home_advantage)) / 400))
                actual_home = 1.0 if row.home_points == 3 else 0.5 if row.home_points == 1 else 0.0
                delta = k_factor * (actual_home - expected_home)
                ratings[home] = home_pre + delta
                ratings[away] = away_pre - delta
            output.append(pd.DataFrame(season_rows))
    return pd.concat(output, ignore_index=True)


def to_team_match(matches: pd.DataFrame) -> pd.DataFrame:
    common = ["match_id", "league_name", "season_year", "kickoff", "round", "audience"]
    home = matches[common + ["home_team_canonical", "away_team_canonical", "home_points", "home_elo_pre", "away_elo_pre"]].rename(
        columns={
            "home_team_canonical": "team_canonical",
            "away_team_canonical": "opponent_canonical",
            "home_points": "points",
            "home_elo_pre": "own_elo_pre",
            "away_elo_pre": "opponent_elo_pre",
        }
    )
    home["is_home"] = 1
    away = matches[common + ["away_team_canonical", "home_team_canonical", "away_points", "away_elo_pre", "home_elo_pre"]].rename(
        columns={
            "away_team_canonical": "team_canonical",
            "home_team_canonical": "opponent_canonical",
            "away_points": "points",
            "away_elo_pre": "own_elo_pre",
            "home_elo_pre": "opponent_elo_pre",
        }
    )
    away["is_home"] = 0
    long = pd.concat([home, away], ignore_index=True).sort_values(
        ["league_name", "season_year", "team_canonical", "kickoff", "match_id"]
    )
    groups = ["league_name", "season_year", "team_canonical"]
    long["match_number"] = long.groupby(groups).cumcount() + 1
    long["rest_days"] = long.groupby(groups)["kickoff"].diff().dt.total_seconds().div(86400)
    league_baseline = long.groupby(["league_name", "season_year"])["opponent_elo_pre"].transform("mean")
    for window in (2, 3, 5):
        strength = f"opponent_strength_lag{window}"
        shock = f"schedule_shock_lag{window}"
        long[strength] = (
            long.groupby(groups)["opponent_elo_pre"]
            .transform(lambda values, size=window: values.shift(1).rolling(size, min_periods=2).mean())
        )
        long[shock] = (long[strength] - league_baseline) / 100.0
    long["team_season_id"] = (
        long["league_name"].astype(str) + "|" + long["season_year"].astype(str) + "|" + long["team_canonical"]
    )
    return long.reset_index(drop=True)


def continuous_ssb(team_matches: pd.DataFrame) -> pd.DataFrame:
    rows = []
    key = ["league_name", "season_year", "team_canonical"]
    for values, frame in team_matches.groupby(key, sort=True):
        first = frame.sort_values(["kickoff", "match_id"]).drop_duplicates("opponent_canonical", keep="first")
        if len(first) < 4 or first["opponent_elo_pre"].nunique() < 2:
            ssb = np.nan
        else:
            order = np.arange(1, len(first) + 1)
            ssb = float(spearmanr(order, -first["opponent_elo_pre"]).statistic)
        rows.append((*values, ssb, len(first), float(first["opponent_elo_pre"].std(ddof=0))))
    return pd.DataFrame(rows, columns=key + ["ssb_continuous", "unique_opponents", "opponent_strength_sd"])


def gini(values: pd.Series) -> float:
    array = np.sort(values.dropna().to_numpy(dtype=float))
    array = array[array >= 0]
    if len(array) == 0 or array.sum() == 0:
        return float("nan")
    index = np.arange(1, len(array) + 1)
    return float((2 * (index * array).sum() / (len(array) * array.sum())) - (len(array) + 1) / len(array))
