import pandas as pd
import pytest

from soccer_imbalance_extensions.data import (
    SourceLayout,
    _parse_date,
    _parse_result,
    discover_source,
    load_market_values,
    load_standings,
)


def test_parse_transfermarkt_date_with_weekday_prefix():
    parsed = _parse_date(pd.Series(["sáb 17/08/2024", "01/09/2024"]))
    assert parsed.dt.strftime("%Y-%m-%d").tolist() == ["2024-08-17", "2024-09-01"]


def test_parse_result_accepts_suffix_and_missing():
    home, away = _parse_result(pd.Series(["2:1 AET", "0:0", None]))
    assert home.iloc[:2].tolist() == [2.0, 0.0]
    assert away.iloc[:2].tolist() == [1.0, 0.0]
    assert pd.isna(home.iloc[2])


def test_missing_source_fails_with_exact_paths(tmp_path):
    with pytest.raises(FileNotFoundError, match="Missing required source paths"):
        discover_source(tmp_path)


def test_duplicate_standings_key_fails(tmp_path):
    source = tmp_path / "standings.csv"
    row = {
        "league_name": "league",
        "season_year": 2024,
        "team_canonical": "a",
        "position_old": 1,
        "points": 10,
        "played": 4,
        "total_market_value_euros": 100,
    }
    pd.DataFrame([row, row]).to_csv(source, index=False)
    layout = SourceLayout(tmp_path, source, tmp_path / "ssb.csv", tmp_path / "attendance.csv", tmp_path / "bronze")
    with pytest.raises(ValueError, match="duplicated"):
        load_standings(layout)


def test_load_market_values_canonicalizes_and_skips_status(tmp_path):
    market_root = tmp_path / "market"
    market_root.mkdir()
    pd.DataFrame(
        [
            {
                "league_name": "league",
                "season_year": 2020,
                "club_name": "Clube Á",
                "total_market_value_euros": 123.0,
            }
        ]
    ).to_csv(market_root / "league_2020.csv", index=False)
    pd.DataFrame([{"status": "Success"}]).to_csv(
        market_root / "scraping_status.csv", index=False
    )
    layout = SourceLayout(
        tmp_path,
        tmp_path / "standings.csv",
        tmp_path / "ssb.csv",
        tmp_path / "attendance.csv",
        tmp_path / "bronze",
        market_root,
    )

    result = load_market_values(layout)

    assert result.to_dict(orient="records") == [
        {
            "league_name": "league",
            "season_year": 2020,
            "team_canonical": "clubea",
            "total_market_value_euros": 123.0,
        }
    ]
