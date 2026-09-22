from datetime import timedelta

import numpy as np
import pandas as pd

from soccer_imbalance_extensions.analysis import _linear_combination, _permutation_null


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
