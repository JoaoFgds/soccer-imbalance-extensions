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


def schedule_balance_from_strength(
    team_matches: pd.DataFrame,
    opponent_strength: pd.Series,
    output_column: str,
) -> pd.DataFrame:
    """Correlate first-opponent order with negative strength for each team-season."""
    if not team_matches.index.equals(opponent_strength.index):
        raise ValueError("Opponent-strength index must match the team-match index")
    working = team_matches.assign(_opponent_strength=opponent_strength)
    rows = []
    key = ["league_name", "season_year", "team_canonical"]
    for values, frame in working.groupby(key, sort=True):
        first = frame.sort_values(["kickoff", "match_id"]).drop_duplicates("opponent_canonical", keep="first")
        strength = first["_opponent_strength"]
        if len(first) < 4 or strength.notna().sum() != len(first) or strength.nunique() < 2:
            ssb = np.nan
        else:
            order = np.arange(1, len(first) + 1)
            ssb = float(spearmanr(order, -strength).statistic)
        rows.append((*values, ssb, len(first), float(strength.std(ddof=0))))
    return pd.DataFrame(
        rows,
        columns=key + [output_column, "unique_opponents", f"{output_column}_strength_sd"],
    )


def continuous_ssb(team_matches: pd.DataFrame) -> pd.DataFrame:
    result = schedule_balance_from_strength(
        team_matches,
        team_matches["opponent_elo_pre"],
        "ssb_continuous",
    )
    return result.rename(columns={"ssb_continuous_strength_sd": "opponent_strength_sd"})


def season_start_elo_ssb(team_matches: pd.DataFrame) -> pd.DataFrame:
    """Calculate SSB from one fixed, strictly prior rating per team-season."""
    key = ["league_name", "season_year", "team_canonical"]
    initial = (
        team_matches.sort_values(key + ["kickoff", "match_id"])
        .groupby(key, as_index=False)
        .first()[key + ["own_elo_pre"]]
        .rename(
            columns={
                "team_canonical": "opponent_canonical",
                "own_elo_pre": "opponent_season_start_elo",
            }
        )
    )
    working = team_matches.merge(
        initial,
        on=["league_name", "season_year", "opponent_canonical"],
        how="left",
        validate="many_to_one",
    )
    return schedule_balance_from_strength(
        working,
        working["opponent_season_start_elo"],
        "ssb_preseason_elo",
    )


def fixed_elo_local_shocks(
    team_matches: pd.DataFrame,
    window: int = 3,
    minimum_periods: int = 3,
) -> pd.DataFrame:
    """Add symmetric past/future shocks from ratings fixed at season start."""
    if window < 1 or minimum_periods < 1 or minimum_periods > window:
        raise ValueError("Window must be positive and minimum_periods within window")
    key = ["league_name", "season_year", "team_canonical"]
    initial = (
        team_matches.sort_values(key + ["kickoff", "match_id"])
        .groupby(key, as_index=False)
        .first()[key + ["own_elo_pre"]]
        .rename(
            columns={
                "team_canonical": "opponent_canonical",
                "own_elo_pre": "opponent_season_start_elo",
            }
        )
    )
    league_mean = initial.groupby(["league_name", "season_year"])[
        "opponent_season_start_elo"
    ].mean()
    working = team_matches.copy()
    working["_original_order"] = np.arange(len(working))
    working = working.merge(
        initial,
        on=["league_name", "season_year", "opponent_canonical"],
        how="left",
        validate="many_to_one",
    ).sort_values(key + ["kickoff", "match_id"])
    working["season_start_elo_mean"] = pd.MultiIndex.from_frame(
        working[["league_name", "season_year"]]
    ).map(league_mean)

    groups = working.groupby(key)["opponent_season_start_elo"]
    lag_strength = f"fixed_elo_strength_lag{window}"
    lead_strength = f"fixed_elo_strength_lead{window}"
    lag_shock = f"fixed_elo_shock_lag{window}"
    lead_shock = f"fixed_elo_shock_lead{window}"
    working[lag_strength] = groups.transform(
        lambda values: values.shift(1).rolling(window, min_periods=minimum_periods).mean()
    )

    def future_mean(values: pd.Series) -> pd.Series:
        reversed_values = values.iloc[::-1]
        return (
            reversed_values.shift(1)
            .rolling(window, min_periods=minimum_periods)
            .mean()
            .iloc[::-1]
        )

    working[lead_strength] = groups.transform(future_mean)
    working[lag_shock] = (
        working[lag_strength] - working["season_start_elo_mean"]
    ) / 100.0
    working[lead_shock] = (
        working[lead_strength] - working["season_start_elo_mean"]
    ) / 100.0
    return working.sort_values("_original_order").drop(columns="_original_order").reset_index(
        drop=True
    )


def fixed_elo_cumulative_shocks(
    team_matches: pd.DataFrame,
    minimum_periods: int = 3,
) -> pd.DataFrame:
    """Add all-prior and all-future shocks using season-start opponent Elo."""
    if minimum_periods < 1:
        raise ValueError("minimum_periods must be positive")
    working = fixed_elo_local_shocks(
        team_matches,
        window=minimum_periods,
        minimum_periods=minimum_periods,
    )
    key = ["league_name", "season_year", "team_canonical"]
    groups = working.groupby(key)["opponent_season_start_elo"]
    working["cumulative_past_strength"] = groups.transform(
        lambda values: values.shift(1).expanding(min_periods=minimum_periods).mean()
    )

    def future_mean(values: pd.Series) -> pd.Series:
        reversed_values = values.iloc[::-1]
        return (
            reversed_values.shift(1)
            .expanding(min_periods=minimum_periods)
            .mean()
            .iloc[::-1]
        )

    working["cumulative_future_strength"] = groups.transform(future_mean)
    working["cumulative_past_shock"] = (
        working["cumulative_past_strength"] - working["season_start_elo_mean"]
    ) / 100.0
    working["cumulative_future_shock"] = (
        working["cumulative_future_strength"] - working["season_start_elo_mean"]
    ) / 100.0
    return working


def gini(values: pd.Series) -> float:
    array = np.sort(values.dropna().to_numpy(dtype=float))
    array = array[array >= 0]
    if len(array) == 0 or array.sum() == 0:
        return float("nan")
    index = np.arange(1, len(array) + 1)
    return float((2 * (index * array).sum() / (len(array) * array.sum())) - (len(array) + 1) / len(array))
