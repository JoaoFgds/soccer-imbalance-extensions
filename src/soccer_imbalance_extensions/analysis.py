from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import spearmanr

from .features import continuous_ssb, gini


def _coefficient_table(model, terms: list[str]) -> pd.DataFrame:
    ci = model.conf_int()
    rows = []
    for term in terms:
        if term not in model.params.index:
            continue
        rows.append(
            {
                "term": term,
                "estimate": model.params[term],
                "std_error": model.bse[term],
                "ci_low": ci.loc[term, 0],
                "ci_high": ci.loc[term, 1],
                "p_value": model.pvalues[term],
                "nobs": int(model.nobs),
                "r_squared": getattr(model, "rsquared", np.nan),
            }
        )
    return pd.DataFrame(rows)


def _save_table(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)


def _save_figure(fig: plt.Figure, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


def _decision(viable: bool, stable: bool, blocked: bool = False) -> str:
    if blocked:
        return "descartar"
    if viable and stable:
        return "avançar"
    return "reformular"


def run_mvp1(
    standings: pd.DataFrame,
    team_matches: pd.DataFrame,
    tables: Path,
    figures: Path,
    criteria: dict,
) -> tuple[pd.DataFrame, dict]:
    ssb = continuous_ssb(team_matches)
    data = standings.merge(ssb, on=["league_name", "season_year", "team_canonical"], how="left", validate="one_to_one")
    data["league_season"] = data["league_name"] + "|" + data["season_year"].astype(str)
    data["relative_log_market"] = data["log_market_value"] - data.groupby("league_season")["log_market_value"].transform("mean")
    model_data = data.dropna(subset=["points_per_game", "ssb_continuous", "log_market_value"]).copy()
    model = smf.ols(
        "points_per_game ~ ssb_continuous + relative_log_market + ssb_continuous:relative_log_market + C(league_name) + C(season_year)",
        data=model_data,
    ).fit(cov_type="cluster", cov_kwds={"groups": model_data["league_season"]})
    coeff = _coefficient_table(model, ["ssb_continuous", "ssb_continuous:relative_log_market"])
    _save_table(coeff, tables / "mvp1_continuous_ssb_model.csv")
    summary = data.groupby("league_name").agg(
        team_seasons=("team_canonical", "size"),
        ssb_available=("ssb_continuous", "count"),
        ssb_mean=("ssb_continuous", "mean"),
        ssb_sd=("ssb_continuous", "std"),
        ppg_mean=("points_per_game", "mean"),
    ).reset_index()
    _save_table(summary, tables / "mvp1_coverage_by_league.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    sample = model_data.sample(min(3000, len(model_data)), random_state=20260922)
    ax.scatter(sample["ssb_continuous"], sample["points_per_game"], s=8, alpha=0.2)
    bins = pd.qcut(model_data["ssb_continuous"], 15, duplicates="drop")
    curve = model_data.assign(bin=bins).groupby("bin", observed=True).agg(x=("ssb_continuous", "mean"), y=("points_per_game", "mean"))
    ax.plot(curve["x"], curve["y"], color="black", marker="o", label="bin means")
    ax.set(xlabel="Continuous leakage-free SSB", ylabel="Points per game", title="MVP 1: schedule balance and final performance")
    ax.legend()
    _save_figure(fig, figures / "mvp1_ssb_vs_ppg.png")
    coverage = float(data["ssb_continuous"].notna().mean())
    viable = len(model_data) >= criteria["minimum_team_seasons"] and coverage >= criteria["minimum_join_rate"]
    main = coeff.loc[coeff["term"] == "ssb_continuous"].iloc[0]
    stable = np.isfinite(main["estimate"]) and (main["ci_high"] - main["ci_low"] < 0.5)
    precise_null = (
        main["ci_low"] > -criteria["sesoi_ppg_per_ssb_unit"]
        and main["ci_high"] < criteria["sesoi_ppg_per_ssb_unit"]
    )
    status = "reformular" if viable and stable and precise_null else _decision(viable, stable)
    result = {
        "mvp": 1,
        "status": status,
        "n": len(model_data),
        "coverage": coverage,
        "ssb_sd": float(model_data["ssb_continuous"].std()),
        "estimate": float(main["estimate"]),
        "ci_low": float(main["ci_low"]),
        "ci_high": float(main["ci_high"]),
        "p_value": float(main["p_value"]),
        "interpretation": "Association adjusted for market value and league/year fixed effects; not causal.",
    }
    return data, result


def _within_model(data: pd.DataFrame, outcome: str, variables: list[str], group: str):
    clean = data.dropna(subset=[outcome, group] + variables).copy()
    means = clean.groupby(group)[[outcome] + variables].transform("mean")
    demeaned = clean[[outcome] + variables] - means
    keep = demeaned[variables].std().loc[lambda values: values > 1e-10].index.tolist()
    model = sm.OLS(demeaned[outcome], demeaned[keep]).fit(
        cov_type="cluster", cov_kwds={"groups": clean[group]}
    )
    return clean, model, keep


def run_mvp2(team_matches: pd.DataFrame, tables: Path, figures: Path, criteria: dict) -> dict:
    data = team_matches.copy()
    data["own_elo_100"] = data["own_elo_pre"] / 100
    data["opponent_elo_100"] = data["opponent_elo_pre"] / 100
    max_match = data.groupby("team_season_id")["match_number"].transform("max")
    data["season_progress"] = data["match_number"] / max_match
    controls = ["own_elo_100", "opponent_elo_100", "is_home", "rest_days", "season_progress"]
    sensitivity = []
    clean = model = variables = None
    for window in (2, 3, 5):
        shock = f"schedule_shock_lag{window}"
        clean_window, model_window, variables_window = _within_model(
            data, "points", [shock] + controls, "team_season_id"
        )
        row = _coefficient_table(model_window, [shock]).iloc[0].to_dict()
        row["window"] = window
        sensitivity.append(row)
        if window == 3:
            clean, model, variables = clean_window, model_window, variables_window
    coeff = _coefficient_table(model, variables)
    _save_table(coeff, tables / "mvp2_local_shock_model.csv")
    _save_table(pd.DataFrame(sensitivity), tables / "mvp2_window_sensitivity.csv")
    plot_data = clean.dropna(subset=["schedule_shock_lag3", "points"]).copy()
    plot_data["shock_bin"] = pd.qcut(plot_data["schedule_shock_lag3"], 12, duplicates="drop")
    curve = plot_data.groupby("shock_bin", observed=True).agg(
        shock=("schedule_shock_lag3", "mean"), points=("points", "mean"), n=("points", "size")
    ).reset_index(drop=True)
    _save_table(curve, tables / "mvp2_shock_bins.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(curve["shock"], curve["points"], marker="o")
    ax.axhline(plot_data["points"].mean(), color="grey", linestyle="--")
    ax.set(xlabel="Prior 3-match opponent-strength shock (100 Elo)", ylabel="Next-match points", title="MVP 2: local schedule shock")
    _save_figure(fig, figures / "mvp2_local_shock.png")
    main = coeff.loc[coeff["term"] == "schedule_shock_lag3"].iloc[0]
    viable = len(clean) >= criteria["minimum_match_rows"] and plot_data["schedule_shock_lag3"].std() > 0.1
    stable = main["ci_high"] - main["ci_low"] < 0.2
    precise_null = (
        main["ci_low"] > -criteria["sesoi_points_per_100_elo_shock"]
        and main["ci_high"] < criteria["sesoi_points_per_100_elo_shock"]
    )
    status = "descartar" if viable and precise_null else _decision(viable, stable)
    return {
        "mvp": 2,
        "status": status,
        "n": len(clean),
        "estimate": float(main["estimate"]),
        "ci_low": float(main["ci_low"]),
        "ci_high": float(main["ci_high"]),
        "p_value": float(main["p_value"]),
        "interpretation": "Within-team-season association of prior schedule shock with match points.",
    }


def run_mvp3(team_seasons: pd.DataFrame, tables: Path, figures: Path, criteria: dict) -> dict:
    data = team_seasons.copy()
    group = ["league_name", "season_year"]
    data["market_gini"] = data.groupby(group)["total_market_value_euros"].transform(gini)
    data["relative_log_market"] = data["log_market_value"] - data.groupby(group)["log_market_value"].transform("mean")
    data["league_season"] = data["league_name"] + "|" + data["season_year"].astype(str)
    clean = data.dropna(subset=["points_per_game", "ssb_continuous", "relative_log_market", "market_gini"]).copy()
    model = smf.ols(
        "points_per_game ~ ssb_continuous * relative_log_market * market_gini + C(league_name) + C(season_year)",
        data=clean,
    ).fit(cov_type="cluster", cov_kwds={"groups": clean["league_season"]})
    terms = [
        "ssb_continuous",
        "ssb_continuous:relative_log_market",
        "ssb_continuous:market_gini",
        "ssb_continuous:relative_log_market:market_gini",
    ]
    coeff = _coefficient_table(model, terms)
    _save_table(coeff, tables / "mvp3_inequality_model.csv")
    summary = clean.groupby("league_name").agg(
        seasons=("season_year", "nunique"), market_gini_mean=("market_gini", "mean"), market_gini_sd=("market_gini", "std")
    ).reset_index()
    _save_table(summary, tables / "mvp3_market_inequality.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(summary["market_gini_mean"], summary["market_gini_sd"], s=30)
    for row in summary.itertuples(index=False):
        ax.annotate(row.league_name, (row.market_gini_mean, row.market_gini_sd), fontsize=6)
    ax.set(xlabel="Mean market-value Gini", ylabel="Within-league temporal SD", title="MVP 3: economic inequality support")
    _save_figure(fig, figures / "mvp3_inequality_support.png")
    main = coeff.loc[coeff["term"] == "ssb_continuous:relative_log_market:market_gini"].iloc[0]
    viable = len(clean) >= criteria["minimum_team_seasons"] and clean["market_gini"].std() > 0.02
    status = "avançar" if viable and main["p_value"] < 0.05 else "reformular"
    return {
        "mvp": 3,
        "status": status,
        "n": len(clean),
        "gini_sd": float(clean["market_gini"].std()),
        "triple_interaction": float(main["estimate"]),
        "ci_low": float(main["ci_low"]),
        "ci_high": float(main["ci_high"]),
        "p_value": float(main["p_value"]),
        "interpretation": "Exploratory moderation; market values follow the article's stated pre-season interpretation.",
    }


def _season_ssb(frame: pd.DataFrame, round_values: pd.Series, ranks: dict[str, float]) -> np.ndarray:
    working = frame.assign(_round=round_values.to_numpy()).sort_values(["_round", "kickoff", "match_id"])
    values = []
    teams = sorted(set(working["home_team_canonical"]) | set(working["away_team_canonical"]))
    for team in teams:
        fixtures = working[(working["home_team_canonical"] == team) | (working["away_team_canonical"] == team)].copy()
        fixtures["opponent"] = np.where(
            fixtures["home_team_canonical"] == team,
            fixtures["away_team_canonical"],
            fixtures["home_team_canonical"],
        )
        first = fixtures.drop_duplicates("opponent", keep="first")
        strengths = first["opponent"].map(ranks)
        if len(strengths) >= 4 and strengths.notna().all() and strengths.nunique() > 1:
            values.append(float(spearmanr(np.arange(len(strengths)), strengths).statistic))
    return np.asarray(values)


def run_mvp4(matches: pd.DataFrame, standings: pd.DataFrame, tables: Path, figures: Path, config: dict, seed: int) -> dict:
    rng = np.random.default_rng(seed)
    latest = standings.groupby("league_name")["season_year"].max().reset_index()
    selected = matches.merge(latest, on=["league_name", "season_year"], how="inner")
    rank_frame = standings.merge(latest, on=["league_name", "season_year"], how="inner").copy()
    rank_frame["market_rank"] = rank_frame.groupby(["league_name", "season_year"])["total_market_value_euros"].rank(ascending=False, method="first")
    rank_maps = {
        key: dict(zip(frame["team_canonical"], frame["market_rank"]))
        for key, frame in rank_frame.groupby(["league_name", "season_year"])
    }
    rows = []
    valid_draws = 0
    permutations = int(config["permutations"])
    for key, frame in selected.groupby(["league_name", "season_year"], sort=True):
        frame = frame.dropna(subset=["round"]).copy()
        actual = _season_ssb(frame, frame["round"], rank_maps[key])
        if len(actual) < 4:
            continue
        rounds = np.sort(frame["round"].unique())
        null = []
        for _ in range(permutations):
            shuffled = rng.permutation(rounds)
            mapping = dict(zip(rounds, shuffled))
            permuted_round = frame["round"].map(mapping)
            if permuted_round.isna().any() or permuted_round.nunique() != len(rounds):
                continue
            simulated = _season_ssb(frame, permuted_round, rank_maps[key])
            if len(simulated) == len(actual):
                null.append(float(np.mean(np.abs(simulated))))
                valid_draws += 1
        if not null:
            continue
        observed = float(np.mean(np.abs(actual)))
        rows.append(
            {
                "league_name": key[0],
                "season_year": key[1],
                "teams": len(actual),
                "observed_mean_abs_ssb": observed,
                "null_mean_abs_ssb": float(np.mean(null)),
                "null_sd": float(np.std(null, ddof=1)),
                "empirical_p_upper": float((1 + np.sum(np.asarray(null) >= observed)) / (1 + len(null))),
                "permutations": len(null),
            }
        )
    result_table = pd.DataFrame(rows)
    _save_table(result_table, tables / "mvp4_counterfactual_schedules.csv")
    fig, ax = plt.subplots(figsize=(9, 5))
    ordered = result_table.sort_values("observed_mean_abs_ssb")
    x = np.arange(len(ordered))
    ax.plot(x, ordered["observed_mean_abs_ssb"], marker="o", label="observed")
    ax.plot(x, ordered["null_mean_abs_ssb"], marker="o", label="permutation null")
    ax.set_xticks(x, ordered["league_name"], rotation=75, fontsize=7)
    ax.set(ylabel="Mean absolute SSB", title="MVP 4: observed vs constraint-preserving round permutations")
    ax.legend()
    _save_figure(fig, figures / "mvp4_counterfactual.png")
    viable = len(result_table) >= 10 and (result_table["permutations"] == permutations).mean() == 1
    stable = result_table["null_sd"].median() < 0.05
    return {
        "mvp": 4,
        "status": _decision(viable, stable),
        "league_seasons": len(result_table),
        "valid_permutation_draws": int(valid_draws),
        "leagues_upper_tail_p_lt_0_05": int((result_table["empirical_p_upper"] < 0.05).sum()),
        "interpretation": "Null preserves fixtures, home/away assignments and one global ordering of existing rounds.",
    }


def run_mvp5(
    matches: pd.DataFrame,
    team_matches: pd.DataFrame,
    standings: pd.DataFrame,
    tables: Path,
    figures: Path,
    config: dict,
    criteria: dict,
) -> dict:
    home_long = team_matches[team_matches["is_home"] == 1][
        ["match_id", "team_season_id", "schedule_shock_lag3", "rest_days", "match_number"]
    ]
    data = matches.merge(home_long, on="match_id", how="left", validate="one_to_one")
    opponent_market = standings[["league_name", "season_year", "team_canonical", "log_market_value"]].rename(
        columns={"team_canonical": "away_team_canonical", "log_market_value": "opponent_log_market"}
    )
    data = data.merge(opponent_market, on=["league_name", "season_year", "away_team_canonical"], how="left", validate="many_to_one")
    data = data[~data["season_year"].isin(config["excluded_seasons"])].copy()
    data["log_attendance"] = np.log(data["audience"].where(data["audience"] > 0))
    data["home_elo_100"] = data["home_elo_pre"] / 100
    data["away_elo_100"] = data["away_elo_pre"] / 100
    data["weekend"] = data["kickoff"].dt.dayofweek.isin([5, 6]).astype(float)
    max_round = data.groupby(["league_name", "season_year"])["round"].transform("max")
    data["season_progress"] = data["round"] / max_round
    variables = [
        "schedule_shock_lag3", "home_elo_100", "away_elo_100", "opponent_log_market",
        "rest_days", "weekend", "season_progress",
    ]
    clean, model, retained = _within_model(data, "log_attendance", variables, "team_season_id")
    coeff = _coefficient_table(model, retained)
    _save_table(coeff, tables / "mvp5_attendance_model.csv")
    coverage = data.groupby("league_name").agg(
        matches=("match_id", "size"), attendance_available=("audience", lambda values: int((values > 0).sum()))
    ).reset_index()
    coverage["attendance_rate"] = coverage["attendance_available"] / coverage["matches"]
    _save_table(coverage, tables / "mvp5_attendance_coverage.csv")
    plot = clean.dropna(subset=["schedule_shock_lag3", "log_attendance"]).copy()
    plot["demeaned_log_attendance"] = plot["log_attendance"] - plot.groupby("team_season_id")["log_attendance"].transform("mean")
    plot["shock_bin"] = pd.qcut(plot["schedule_shock_lag3"], 12, duplicates="drop")
    curve = plot.groupby("shock_bin", observed=True).agg(
        shock=("schedule_shock_lag3", "mean"), attendance=("demeaned_log_attendance", "mean"), n=("match_id", "size")
    ).reset_index(drop=True)
    _save_table(curve, tables / "mvp5_attendance_bins.csv")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(curve["shock"], curve["attendance"], marker="o")
    ax.axhline(0, color="grey", linestyle="--")
    ax.set(xlabel="Prior schedule shock (100 Elo)", ylabel="Within-team-season log attendance", title="MVP 5: schedule shock and stadium attendance")
    _save_figure(fig, figures / "mvp5_attendance.png")
    main = coeff.loc[coeff["term"] == "schedule_shock_lag3"].iloc[0]
    attendance_rate = float((data["audience"] > 0).mean())
    viable = len(clean) >= criteria["minimum_match_rows"] and attendance_rate >= criteria["minimum_attendance_rate"]
    stable = main["ci_high"] - main["ci_low"] < 0.1
    precise_null = (
        main["ci_low"] > -criteria["sesoi_log_attendance_per_100_elo_shock"]
        and main["ci_high"] < criteria["sesoi_log_attendance_per_100_elo_shock"]
    )
    status = "descartar" if viable and precise_null else _decision(viable, stable)
    return {
        "mvp": 5,
        "status": status,
        "n": len(clean),
        "attendance_rate": attendance_rate,
        "estimate": float(main["estimate"]),
        "ci_low": float(main["ci_low"]),
        "ci_high": float(main["ci_high"]),
        "p_value": float(main["p_value"]),
        "interpretation": "Within-home-team-season association; observed attendance only and COVID-era seasons excluded.",
    }


def save_summary(results: list[dict], tables: Path, reports: Path, diagnostics: dict) -> None:
    summary = pd.DataFrame(results)
    _save_table(summary, tables / "mvp_decisions.csv")
    lines = ["# MVP execution report", "", "All estimates are exploratory associations, not causal effects.", "", "## Data diagnostics", "", "```json", json.dumps(diagnostics, indent=2, sort_keys=True), "```", "", "## Decisions", ""]
    for result in results:
        lines.extend([
            f"### MVP {result['mvp']}: {result['status']}",
            "",
            f"- Evidence: `{json.dumps(result, sort_keys=True, ensure_ascii=False)}`",
            "",
        ])
    reports.mkdir(parents=True, exist_ok=True)
    (reports / "MVP_RESULTS.md").write_text("\n".join(lines), encoding="utf-8")
