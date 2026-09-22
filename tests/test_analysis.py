from datetime import timedelta

import numpy as np
import pandas as pd

from soccer_imbalance_extensions.analysis import (
    _build_lagged_market_data,
    _linear_combination,
    _permutation_null,
)
from soccer_imbalance_extensions.features import gini


class StubModel:
    params = pd.Series({"a": 2.0, "b": -1.0})

    @staticmethod
    def cov_params():
        return pd.DataFrame([[0.25, 0.0], [0.0, 1.0]], index=["a", "b"], columns=["a", "b"])


def test_linear_combination_uses_full_covariance_matrix():
    result = _linear_combination(StubModel(), {"a": 1.0, "b": 2.0})
    assert result["estimate"] == 0.0
    assert result["std_error"] == np.sqrt(4.25)


def round_robin_frame():
    teams = ["a", "b", "c", "d", "e", "bye"]
    rotating = teams[:]
    rows = []
    match_number = 0
    for round_number in range(1, len(teams)):
        for index in range(len(teams) // 2):
            home = rotating[index]
            away = rotating[-(index + 1)]
            if "bye" in (home, away):
                continue
            rows.append(
                {
                    "round": round_number,
                    "kickoff": pd.Timestamp("2024-01-01") + timedelta(days=round_number),
                    "match_id": str(match_number),
                    "home_team_canonical": home,
                    "away_team_canonical": away,
                }
            )
            match_number += 1
        rotating = [rotating[0], rotating[-1], *rotating[1:-1]]
    return pd.DataFrame(rows)


def test_permutation_null_is_seeded_and_complete():
    frame = round_robin_frame()
    ranks = {team: rank for rank, team in enumerate(["a", "b", "c", "d", "e"], 1)}
    first = _permutation_null(
        frame, ranks, 20, np.random.default_rng(7), "phase_preserving", batch_size=7
    )
    second = _permutation_null(
        frame, ranks, 20, np.random.default_rng(7), "phase_preserving", batch_size=7
    )
    assert len(first) == 20
    assert np.isfinite(first).all()
    np.testing.assert_array_equal(first, second)


def test_lagged_market_data_uses_only_preceding_season_values():
    team_seasons = pd.DataFrame(
        [
            {
                "league_name": "league",
                "season_year": 2021,
                "team_canonical": team,
                "points_per_game": points,
                "ssb_continuous": ssb,
            }
            for team, points, ssb in [("a", 2.0, -0.2), ("b", 1.0, 0.2)]
        ]
    )
    market_values = pd.DataFrame(
        [
            {
                "league_name": "league",
                "season_year": 2020,
                "team_canonical": "a",
                "total_market_value_euros": 100.0,
            },
            {
                "league_name": "league",
                "season_year": 2020,
                "team_canonical": "b",
                "total_market_value_euros": 300.0,
            },
            {
                "league_name": "league",
                "season_year": 2021,
                "team_canonical": "a",
                "total_market_value_euros": 9999.0,
            },
        ]
    )

    result = _build_lagged_market_data(team_seasons, market_values)

    assert result.set_index("team_canonical")["lagged_market_value_euros"].to_dict() == {
        "a": 100.0,
        "b": 300.0,
    }
    assert result["market_gini"].nunique() == 1
    assert result["market_gini"].iloc[0] == gini(pd.Series([100.0, 300.0]))
