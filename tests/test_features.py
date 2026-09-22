import pandas as pd
import pytest

from soccer_imbalance_extensions.data import canonicalize
from soccer_imbalance_extensions.features import (
    add_elo,
    continuous_ssb,
    gini,
    schedule_balance_from_strength,
    to_team_match,
)


def fixture_matches():
    return pd.DataFrame(
        {
            "match_id": ["1", "2"],
            "league_name": ["league", "league"],
            "season_year": [2024, 2024],
            "kickoff": pd.to_datetime(["2024-08-01", "2024-08-08"]),
            "round": [1, 2],
            "audience": [1000, 1100],
            "home_team_canonical": ["a", "b"],
            "away_team_canonical": ["b", "a"],
            "home_points": [3.0, 1.0],
            "away_points": [0.0, 1.0],
        }
    )


def test_canonicalize_is_deterministic_and_accent_insensitive():
    assert canonicalize("São Paulo F.C.") == "saopaulofc"


def test_elo_is_strictly_pre_match():
    rated = add_elo(fixture_matches(), 1500, 20, 0, 0)
    assert rated.loc[0, "home_elo_pre"] == 1500
    assert rated.loc[0, "away_elo_pre"] == 1500
    assert rated.loc[1, "away_elo_pre"] > 1500
    assert rated.loc[1, "home_elo_pre"] < 1500


def test_future_result_does_not_change_past_rating():
    first = add_elo(fixture_matches(), 1500, 20, 0, 0)
    changed = fixture_matches()
    changed.loc[1, ["home_points", "away_points"]] = [3.0, 0.0]
    second = add_elo(changed, 1500, 20, 0, 0)
    assert first.loc[1, "home_elo_pre"] == second.loc[1, "home_elo_pre"]
    assert first.loc[1, "away_elo_pre"] == second.loc[1, "away_elo_pre"]


def test_team_match_has_unique_team_fixture_key():
    rated = add_elo(fixture_matches(), 1500, 20, 0, 0)
    long = to_team_match(rated)
    assert len(long) == 4
    assert not long.duplicated(["match_id", "team_canonical"]).any()


def test_gini_boundaries():
    assert gini(pd.Series([1, 1, 1])) == pytest.approx(0)
    assert 0 < gini(pd.Series([1, 1, 10])) < 1


def test_elo_transformation_is_reproducible():
    first = add_elo(fixture_matches(), 1500, 20, 0, 0)
    second = add_elo(fixture_matches(), 1500, 20, 0, 0)
    pd.testing.assert_frame_equal(first, second)


def test_continuous_ssb_handles_insufficient_opponents_explicitly():
    long = to_team_match(add_elo(fixture_matches(), 1500, 20, 0, 0))
    result = continuous_ssb(long)
    assert result["ssb_continuous"].isna().all()


def test_generic_schedule_balance_rejects_misaligned_strength():
    long = to_team_match(add_elo(fixture_matches(), 1500, 20, 0, 0))
    strength = pd.Series([1.0] * len(long), index=range(10, 10 + len(long)))
    with pytest.raises(ValueError, match="index"):
        schedule_balance_from_strength(long, strength, "alternative_ssb")
