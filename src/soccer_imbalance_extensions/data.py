from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


def canonicalize(value: object) -> str:
    """Create a deterministic, accent-insensitive identifier."""
    import unicodedata

    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", text.lower())


@dataclass(frozen=True)
class SourceLayout:
    root: Path
    standings: Path
    schedule_balance: Path
    occupancy: Path
    bronze: Path


def discover_source(root: Path) -> SourceLayout:
    root = root.expanduser().resolve()
    direct_analysis = root / "analysis/source"
    direct_bronze = root / "bronze/bronze/scraper"
    fetched_analysis = root / "extracted/analysis-inputs-v1/source"
    fetched_bronze = root / "extracted/soccer-scraper-bronze-v1/bronze/scraper"
    analysis = direct_analysis if direct_analysis.exists() else fetched_analysis
    bronze = direct_bronze if direct_bronze.exists() else fetched_bronze
    layout = SourceLayout(
        root=root,
        standings=analysis / "final_standings_valid_market_ranking.csv",
        schedule_balance=analysis / "strength_schedule_balance_ranking.csv",
        occupancy=analysis / "occupancy_audit_audience_filled_fb.csv",
        bronze=bronze,
    )
    missing = [str(path) for path in layout.__dict__.values() if isinstance(path, Path) and not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required source paths: " + ", ".join(missing))
    return layout


def load_standings(layout: SourceLayout) -> pd.DataFrame:
    frame = pd.read_csv(layout.standings)
    required = {
        "league_name", "season_year", "team_canonical", "position_old", "points",
        "played", "total_market_value_euros",
    }
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Standings missing columns: {sorted(missing)}")
    key = ["league_name", "season_year", "team_canonical"]
    if frame[key].isna().any().any() or frame.duplicated(key).any():
        raise ValueError("Standings key is null or duplicated")
    frame["season_year"] = frame["season_year"].astype(int)
    frame["points_per_game"] = frame["points"] / frame["played"]
    frame["log_market_value"] = np.log(frame["total_market_value_euros"].where(lambda x: x > 0))
    return frame


def _owner_name(frame: pd.DataFrame) -> str:
    values = pd.concat([frame["home_team"], frame["away_team"]], ignore_index=True)
    return str(values.value_counts(dropna=True).index[0])


def _parse_result(series: pd.Series) -> tuple[pd.Series, pd.Series]:
    extracted = series.astype(str).str.extract(r"(?P<home>\d+)\s*:\s*(?P<away>\d+)")
    return pd.to_numeric(extracted["home"], errors="coerce"), pd.to_numeric(
        extracted["away"], errors="coerce"
    )


def _parse_date(series: pd.Series) -> pd.Series:
    extracted = series.astype(str).str.extract(r"(\d{1,2}/\d{1,2}/\d{4})", expand=False)
    return pd.to_datetime(extracted, format="%d/%m/%Y", errors="coerce")


def load_matches(layout: SourceLayout, standings: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Load raw team schedules and collapse duplicate team views into fixtures."""
    valid = set(map(tuple, standings[["league_name", "season_year"]].drop_duplicates().to_numpy()))
    chunks: list[pd.DataFrame] = []
    aliases: dict[tuple[str, int, str], str] = {}
    files_seen = 0
    for league_dir in sorted(path for path in layout.bronze.iterdir() if path.is_dir()):
        league = league_dir.name
        for season_dir in sorted(path for path in league_dir.iterdir() if path.is_dir()):
            try:
                season = int(season_dir.name)
            except ValueError:
                continue
            if (league, season) not in valid:
                continue
            games_dir = season_dir / "team_games"
            if not games_dir.exists():
                continue
            prefix = f"{league}_{season}_"
            for path in sorted(games_dir.glob("*.csv")):
                frame = pd.read_csv(path)
                needed = {"round", "date", "time", "home_team", "away_team", "audience", "result", "match_link"}
                if not needed.issubset(frame.columns) or frame.empty:
                    continue
                owner = path.stem.removeprefix(prefix)
                owner_display = _owner_name(frame)
                aliases[(league, season, canonicalize(owner_display))] = owner
                frame = frame.copy()
                frame["league_name"] = league
                frame["season_year"] = season
                frame["source_file"] = path.name
                chunks.append(frame)
                files_seen += 1
    if not chunks:
        raise ValueError("No valid schedule files found")
    raw = pd.concat(chunks, ignore_index=True)
    raw["date_parsed"] = _parse_date(raw["date"])
    raw["time_parsed"] = pd.to_timedelta(
        raw["time"].fillna("00:00").astype(str).str.extract(r"(\d{1,2}:\d{2})", expand=False) + ":00",
        errors="coerce",
    )
    raw["kickoff"] = raw["date_parsed"] + raw["time_parsed"].fillna(pd.Timedelta(0))
    raw["home_goals"], raw["away_goals"] = _parse_result(raw["result"])
    raw["audience"] = pd.to_numeric(raw["audience"], errors="coerce")
    raw["round"] = pd.to_numeric(raw["round"], errors="coerce")

    def resolve(row: pd.Series, side: str) -> str:
        raw_name = canonicalize(row[f"{side}_team"])
        return aliases.get((row["league_name"], int(row["season_year"]), raw_name), raw_name)

    raw["home_team_canonical"] = raw.apply(resolve, axis=1, side="home")
    raw["away_team_canonical"] = raw.apply(resolve, axis=1, side="away")
    fallback = (
        raw["league_name"].astype(str)
        + "|" + raw["season_year"].astype(str)
        + "|" + raw["date_parsed"].astype(str)
        + "|" + raw["home_team_canonical"]
        + "|" + raw["away_team_canonical"]
    )
    link = raw["match_link"].fillna("").astype(str).str.strip()
    raw["match_id"] = np.where(link.ne(""), link.str.extract(r"(\d+)$", expand=False), fallback.map(
        lambda value: hashlib.sha256(value.encode()).hexdigest()[:20]
    ))
    raw = raw.sort_values(["match_id", "audience"], ascending=[True, False], na_position="last")
    duplicate_counts = raw.groupby("match_id").size()
    conflicts = raw.groupby("match_id").agg(
        home_names=("home_team_canonical", "nunique"),
        away_names=("away_team_canonical", "nunique"),
        results=("result", "nunique"),
    )
    unique = raw.drop_duplicates("match_id", keep="first").copy()
    unique["duplicate_views"] = unique["match_id"].map(duplicate_counts)
    unique["home_points"] = np.select(
        [unique["home_goals"] > unique["away_goals"], unique["home_goals"] == unique["away_goals"]],
        [3.0, 1.0],
        default=0.0,
    )
    unique["away_points"] = np.select(
        [unique["away_goals"] > unique["home_goals"], unique["home_goals"] == unique["away_goals"]],
        [3.0, 1.0],
        default=0.0,
    )
    unique.loc[unique[["home_goals", "away_goals"]].isna().any(axis=1), ["home_points", "away_points"]] = np.nan
    unique = unique.sort_values(["league_name", "season_year", "kickoff", "round", "match_id"]).reset_index(drop=True)
    diagnostics = {
        "source_files": files_seen,
        "raw_schedule_rows": len(raw),
        "unique_matches": len(unique),
        "blank_or_unparsed_dates": int(unique["date_parsed"].isna().sum()),
        "unparsed_results": int(unique[["home_goals", "away_goals"]].isna().any(axis=1).sum()),
        "attendance_missing_rate": float(unique["audience"].isna().mean()),
        "singleton_match_links": int((duplicate_counts == 1).sum()),
        "match_links_over_two_views": int((duplicate_counts > 2).sum()),
        "conflicting_duplicate_groups": int(((conflicts > 1).any(axis=1)).sum()),
    }
    return unique, diagnostics


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
