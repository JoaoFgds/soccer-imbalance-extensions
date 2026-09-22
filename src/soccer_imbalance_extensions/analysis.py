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
from scipy.stats import rankdata, spearmanr
from statsmodels.stats.multitest import multipletests

from .features import (
    continuous_ssb,
    gini,
    schedule_balance_from_strength,
    season_start_elo_ssb,
)


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


def _linear_combination(model, weights: dict[str, float]) -> dict[str, float]:
    """Return a delta-method estimate for a linear combination of coefficients."""
    vector = pd.Series(0.0, index=model.params.index)
    for term, weight in weights.items():
        if term not in vector.index:
            raise KeyError(f"Model does not contain required term: {term}")
        vector.loc[term] = weight
    estimate = float(vector @ model.params)
    std_error = float(np.sqrt(vector @ model.cov_params() @ vector))
    return {
        "estimate": estimate,
        "std_error": std_error,
        "ci_low": estimate - 1.96 * std_error,
        "ci_high": estimate + 1.96 * std_error,
    }


def _fit_mvp3_model(
    data: pd.DataFrame,
    outcome: str,
    ssb: str,
    cluster_column: str = "league_season",
    use_t: bool = False,
):
    formula = (
        f"{outcome} ~ {ssb} * relative_log_market * market_gini "
        "+ C(league_name) + C(season_year)"
    )
    return smf.ols(formula, data=data).fit(
        cov_type="cluster",
        cov_kwds={
            "groups": data[cluster_column],
            "use_correction": True,
            "df_correction": True,
        },
        use_t=use_t,
    )


def _build_lagged_market_data(
    team_seasons: pd.DataFrame, market_values: pd.DataFrame
) -> pd.DataFrame:
    """Replace same-season valuations with information from the preceding season."""
    if market_values.empty:
        return team_seasons.iloc[0:0].copy()

    history = market_values.copy()
    history["total_market_value_euros"] = history["total_market_value_euros"].where(
        history["total_market_value_euros"] > 0
    )
    prior_team = history[
        ["season_year", "team_canonical", "total_market_value_euros"]
    ].rename(columns={"total_market_value_euros": "lagged_market_value_euros"})
    prior_team["season_year"] = prior_team["season_year"] + 1
    prior_league = (
        history.groupby(["league_name", "season_year"])["total_market_value_euros"]
        .apply(gini)
        .rename("lagged_market_gini")
        .reset_index()
    )
    prior_league["season_year"] = prior_league["season_year"] + 1

    data = team_seasons.merge(
        prior_team,
        on=["season_year", "team_canonical"],
        how="left",
        validate="many_to_one",
    ).merge(
        prior_league,
        on=["league_name", "season_year"],
        how="left",
        validate="many_to_one",
    )
    data["lagged_log_market"] = np.log(
        data["lagged_market_value_euros"].where(lambda values: values > 0)
    )
    groups = ["league_name", "season_year"]
    data["relative_log_market"] = data["lagged_log_market"] - data.groupby(groups)[
        "lagged_log_market"
    ].transform("mean")
    data["market_gini"] = data["lagged_market_gini"]
    data["league_season"] = data["league_name"] + "|" + data["season_year"].astype(str)
    required = ["points_per_game", "ssb_continuous", "relative_log_market", "market_gini"]
    return data.dropna(subset=required).copy()


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


def run_mvp3(
    team_seasons: pd.DataFrame,
    team_matches: pd.DataFrame,
    tables: Path,
    figures: Path,
    criteria: dict,
    market_values: pd.DataFrame | None = None,
) -> dict:
    data = team_seasons.copy()
    group = ["league_name", "season_year"]
    data["market_gini"] = data.groupby(group)["total_market_value_euros"].transform(gini)
    data["relative_log_market"] = data["log_market_value"] - data.groupby(group)["log_market_value"].transform("mean")
    data["league_season"] = data["league_name"] + "|" + data["season_year"].astype(str)
    strength_lookup = data[
        ["league_name", "season_year", "team_canonical", "log_market_value", "position_old"]
    ].rename(
        columns={
            "team_canonical": "opponent_canonical",
            "log_market_value": "opponent_log_market",
            "position_old": "opponent_final_position",
        }
    )
    strength_matches = team_matches.merge(
        strength_lookup,
        on=["league_name", "season_year", "opponent_canonical"],
        how="left",
        validate="many_to_one",
    )
    market_ssb = schedule_balance_from_strength(
        strength_matches,
        strength_matches["opponent_log_market"],
        "ssb_market_value",
    )
    final_rank_ssb = schedule_balance_from_strength(
        strength_matches,
        -strength_matches["opponent_final_position"],
        "ssb_final_rank",
    )
    preseason_elo_ssb = season_start_elo_ssb(team_matches)
    balance_keys = ["league_name", "season_year", "team_canonical"]
    data = data.merge(
        market_ssb[balance_keys + ["ssb_market_value"]],
        on=balance_keys,
        how="left",
        validate="one_to_one",
    ).merge(
        final_rank_ssb[balance_keys + ["ssb_final_rank"]],
        on=balance_keys,
        how="left",
        validate="one_to_one",
    ).merge(
        preseason_elo_ssb[balance_keys + ["ssb_preseason_elo"]],
        on=balance_keys,
        how="left",
        validate="one_to_one",
    )
    data["goal_difference_per_game"] = data["goal_difference"] / data["played"]
    data["win_rate"] = data["won"] / data["played"]
    required = ["points_per_game", "ssb_continuous", "relative_log_market", "market_gini"]
    clean = data.dropna(subset=required).copy()
    model = _fit_mvp3_model(clean, "points_per_game", "ssb_continuous")
    terms = [
        "ssb_continuous",
        "ssb_continuous:relative_log_market",
        "ssb_continuous:market_gini",
        "ssb_continuous:relative_log_market:market_gini",
    ]
    coeff = _coefficient_table(model, terms)
    _save_table(coeff, tables / "mvp3_inequality_model.csv")

    quantiles = clean[["relative_log_market", "market_gini"]].quantile([0.1, 0.5, 0.9])
    marginal_rows = []
    for market_label, market_value in quantiles["relative_log_market"].items():
        for gini_label, gini_value in quantiles["market_gini"].items():
            effect = _linear_combination(
                model,
                {
                    "ssb_continuous": 1.0,
                    "ssb_continuous:relative_log_market": float(market_value),
                    "ssb_continuous:market_gini": float(gini_value),
                    "ssb_continuous:relative_log_market:market_gini": float(
                        market_value * gini_value
                    ),
                },
            )
            marginal_rows.append(
                {
                    "relative_market_quantile": market_label,
                    "market_gini_quantile": gini_label,
                    "relative_log_market": market_value,
                    "market_gini": gini_value,
                    **effect,
                }
            )
    marginal = pd.DataFrame(marginal_rows)
    _save_table(marginal, tables / "mvp3_marginal_effects.csv")

    leave_one_out = []
    triple_term = "ssb_continuous:relative_log_market:market_gini"
    for league in sorted(clean["league_name"].unique()):
        subset = clean[clean["league_name"] != league]
        fitted = _fit_mvp3_model(subset, "points_per_game", "ssb_continuous")
        row = _coefficient_table(fitted, [triple_term]).iloc[0].to_dict()
        row["excluded_league"] = league
        leave_one_out.append(row)
    leave_one_out_frame = pd.DataFrame(leave_one_out)
    _save_table(leave_one_out_frame, tables / "mvp3_leave_one_league_out.csv")

    nonlinear = smf.ols(
        "points_per_game ~ ssb_continuous * relative_log_market * market_gini "
        "+ I(ssb_continuous ** 2) * relative_log_market * market_gini "
        "+ C(league_name) + C(season_year)",
        data=clean,
    ).fit(cov_type="cluster", cov_kwds={"groups": clean["league_season"]})
    nonlinear_terms = [name for name in nonlinear.params.index if "I(ssb_continuous ** 2)" in name]
    restriction = np.zeros((len(nonlinear_terms), len(nonlinear.params)))
    for row_number, term in enumerate(nonlinear_terms):
        restriction[row_number, nonlinear.params.index.get_loc(term)] = 1.0
    nonlinear_test = nonlinear.wald_test(restriction, scalar=True)
    spline = smf.ols(
        "points_per_game ~ bs(ssb_continuous, df=4, degree=3) "
        "* relative_log_market * market_gini + C(league_name) + C(season_year)",
        data=clean,
    ).fit(cov_type="cluster", cov_kwds={"groups": clean["league_season"]})
    nonlinear_result = pd.DataFrame(
        [
            {
                "terms_tested": len(nonlinear_terms),
                "wald_statistic": float(nonlinear_test.statistic),
                "p_value": float(nonlinear_test.pvalue),
                "linear_aic": model.aic,
                "quadratic_aic": nonlinear.aic,
                "spline_aic": spline.aic,
                "spline_delta_aic_vs_linear": spline.aic - model.aic,
            }
        ]
    )
    _save_table(nonlinear_result, tables / "mvp3_nonlinearity_test.csv")

    specification_rows = []
    for outcome in ("points_per_game", "goal_difference_per_game", "win_rate"):
        for balance in (
            "ssb_continuous",
            "ssb_preseason_elo",
            "ssb_market_value",
            "ssb_final_rank",
        ):
            specification = data.dropna(
                subset=[outcome, balance, "relative_log_market", "market_gini"]
            ).copy()
            fitted = _fit_mvp3_model(specification, outcome, balance)
            term = f"{balance}:relative_log_market:market_gini"
            row = _coefficient_table(fitted, [term]).iloc[0].to_dict()
            row.update(
                {
                    "outcome": outcome,
                    "schedule_balance": balance,
                    "schedule_strength_temporally_safe": balance
                    in {"ssb_continuous", "ssb_preseason_elo"},
                }
            )
            specification_rows.append(row)
    specifications = pd.DataFrame(specification_rows)
    _save_table(specifications, tables / "mvp3_alternative_specifications.csv")

    hierarchical = clean.copy()
    standardized = []
    for variable in ("ssb_continuous", "relative_log_market", "market_gini"):
        name = f"{variable}_z"
        hierarchical[name] = (hierarchical[variable] - hierarchical[variable].mean()) / hierarchical[
            variable
        ].std()
        standardized.append(name)
    hierarchical_model = smf.mixedlm(
        "points_per_game ~ ssb_continuous_z * relative_log_market_z * market_gini_z "
        "+ C(season_year)",
        data=hierarchical,
        groups=hierarchical["league_name"],
    ).fit(reml=False, method="powell", maxiter=1000, disp=False)
    hierarchical_term = "ssb_continuous_z:relative_log_market_z:market_gini_z"
    hierarchical_result = _coefficient_table(hierarchical_model, [hierarchical_term])
    hierarchical_result["converged"] = hierarchical_model.converged
    hierarchical_result["random_effect"] = "league_intercept"
    hierarchical_result["league_intercept_variance"] = hierarchical_model.cov_re.iloc[0, 0]
    hierarchical_result["standardized_predictors"] = ",".join(standardized)
    _save_table(hierarchical_result, tables / "mvp3_hierarchical_model.csv")

    support = clean.copy()
    support["relative_market_group"] = pd.qcut(
        support["relative_log_market"], 3, labels=["low", "middle", "high"]
    )
    support["inequality_group"] = pd.qcut(
        support["market_gini"], 3, labels=["low", "middle", "high"], duplicates="drop"
    )
    support_table = support.groupby(
        ["relative_market_group", "inequality_group"], observed=True
    ).agg(
        n=("team_canonical", "size"),
        leagues=("league_name", "nunique"),
        ssb_mean=("ssb_continuous", "mean"),
        ssb_sd=("ssb_continuous", "std"),
        ssb_min=("ssb_continuous", "min"),
        ssb_max=("ssb_continuous", "max"),
    ).reset_index()
    _save_table(support_table, tables / "mvp3_overlap_support.csv")

    lagged_market = _build_lagged_market_data(
        data,
        market_values if market_values is not None else pd.DataFrame(),
    )
    lagged_term = "ssb_continuous:relative_log_market:market_gini"
    lagged_result: dict[str, float | int] = {
        "estimate": np.nan,
        "ci_low": np.nan,
        "ci_high": np.nan,
        "p_value": np.nan,
        "nobs": 0,
    }
    lagged_sign_share = np.nan
    if not lagged_market.empty:
        lagged_model = _fit_mvp3_model(lagged_market, "points_per_game", "ssb_continuous")
        lagged_coefficient = _coefficient_table(lagged_model, [lagged_term])
        lagged_coefficient["row_coverage"] = len(lagged_market) / len(team_seasons)
        lagged_coefficient["league_seasons"] = lagged_market[
            ["league_name", "season_year"]
        ].drop_duplicates().shape[0]
        lagged_coefficient["team_value_source"] = "preceding season, any covered league"
        lagged_coefficient["inequality_source"] = "preceding season league composition"
        _save_table(lagged_coefficient, tables / "mvp3_lagged_market_model.csv")
        lagged_result = lagged_coefficient.iloc[0].to_dict()

        lagged_leave_one_out = []
        for league in sorted(lagged_market["league_name"].unique()):
            subset = lagged_market[lagged_market["league_name"] != league]
            fitted = _fit_mvp3_model(subset, "points_per_game", "ssb_continuous")
            row = _coefficient_table(fitted, [lagged_term]).iloc[0].to_dict()
            row["excluded_league"] = league
            lagged_leave_one_out.append(row)
        lagged_leave_one_out_frame = pd.DataFrame(lagged_leave_one_out)
        _save_table(
            lagged_leave_one_out_frame,
            tables / "mvp3_lagged_market_leave_one_league_out.csv",
        )
        lagged_sign = np.sign(lagged_result["estimate"])
        lagged_sign_share = float(
            (np.sign(lagged_leave_one_out_frame["estimate"]) == lagged_sign).mean()
        )

        lagged_quantiles = lagged_market[["relative_log_market", "market_gini"]].quantile(
            [0.1, 0.5, 0.9]
        )
        lagged_marginal_rows = []
        for market_label, market_value in lagged_quantiles["relative_log_market"].items():
            for gini_label, gini_value in lagged_quantiles["market_gini"].items():
                effect = _linear_combination(
                    lagged_model,
                    {
                        "ssb_continuous": 1.0,
                        "ssb_continuous:relative_log_market": float(market_value),
                        "ssb_continuous:market_gini": float(gini_value),
                        lagged_term: float(market_value * gini_value),
                    },
                )
                lagged_marginal_rows.append(
                    {
                        "relative_market_quantile": market_label,
                        "market_gini_quantile": gini_label,
                        "relative_log_market": market_value,
                        "market_gini": gini_value,
                        **effect,
                    }
                )
        _save_table(
            pd.DataFrame(lagged_marginal_rows),
            tables / "mvp3_lagged_market_marginal_effects.csv",
        )
        lagged_keys = ["league_name", "season_year", "team_canonical"]
        lagged_available = lagged_market[lagged_keys].assign(lagged_available=1)
        selection = data.merge(
            lagged_available,
            on=lagged_keys,
            how="left",
            validate="one_to_one",
        )
        selection["lagged_available"] = selection["lagged_available"].fillna(0).astype(int)

        coverage_by_league = (
            selection.groupby("league_name")
            .agg(
                total_team_seasons=("team_canonical", "size"),
                lagged_team_seasons=("lagged_available", "sum"),
                total_seasons=("season_year", "nunique"),
            )
            .reset_index()
        )
        coverage_by_league["coverage"] = (
            coverage_by_league["lagged_team_seasons"]
            / coverage_by_league["total_team_seasons"]
        )
        lagged_coverage = coverage_by_league
        _save_table(lagged_coverage, tables / "mvp3_lagged_market_coverage.csv")

        coverage_by_season = (
            selection.groupby("season_year")
            .agg(
                total_team_seasons=("team_canonical", "size"),
                lagged_team_seasons=("lagged_available", "sum"),
            )
            .reset_index()
        )
        coverage_by_season["coverage"] = (
            coverage_by_season["lagged_team_seasons"]
            / coverage_by_season["total_team_seasons"]
        )
        _save_table(
            coverage_by_season,
            tables / "mvp3_lagged_market_coverage_by_season.csv",
        )

        selection_rows = []
        for variable in (
            "points_per_game",
            "ssb_continuous",
            "log_market_value",
            "position_old",
        ):
            excluded = selection.loc[selection["lagged_available"] == 0, variable].dropna()
            included = selection.loc[selection["lagged_available"] == 1, variable].dropna()
            pooled_sd = np.sqrt((excluded.var() + included.var()) / 2)
            selection_rows.append(
                {
                    "variable": variable,
                    "excluded_n": len(excluded),
                    "excluded_mean": excluded.mean(),
                    "included_n": len(included),
                    "included_mean": included.mean(),
                    "standardized_mean_difference": (
                        (included.mean() - excluded.mean()) / pooled_sd
                        if pooled_sd > 0
                        else np.nan
                    ),
                }
            )
        _save_table(
            pd.DataFrame(selection_rows),
            tables / "mvp3_lagged_market_selection_profile.csv",
        )

        current_restricted = clean.merge(
            lagged_available[lagged_keys],
            on=lagged_keys,
            how="inner",
            validate="one_to_one",
        )
        decomposition_rows = []
        for label, frame in (
            ("current_value_full_sample", clean),
            ("current_value_lagged_sample", current_restricted),
            ("lagged_value_lagged_sample", lagged_market),
        ):
            fitted = _fit_mvp3_model(frame, "points_per_game", "ssb_continuous")
            row = _coefficient_table(fitted, [lagged_term]).iloc[0].to_dict()
            row["specification"] = label
            decomposition_rows.append(row)
        _save_table(
            pd.DataFrame(decomposition_rows),
            tables / "mvp3_lagged_market_decomposition.csv",
        )

    temporal_rows = []
    periods = (
        ("early", 2004, 2010),
        ("middle", 2011, 2017),
        ("late_holdout", 2018, 2024),
        ("pre_holdout", 2004, 2017),
        ("full", 2004, 2024),
    )
    for value_source, frame in (
        ("same_season", clean),
        ("preceding_season", lagged_market),
    ):
        if frame.empty:
            continue
        for period, first_year, last_year in periods:
            subset = frame[
                frame["season_year"].between(first_year, last_year, inclusive="both")
            ]
            if len(subset) < 500:
                continue
            fitted = _fit_mvp3_model(subset, "points_per_game", "ssb_continuous")
            row = _coefficient_table(fitted, [triple_term]).iloc[0].to_dict()
            row.update(
                {
                    "value_source": value_source,
                    "period": period,
                    "first_year": first_year,
                    "last_year": last_year,
                }
            )
            temporal_rows.append(row)
    temporal_validation = pd.DataFrame(temporal_rows)
    _save_table(temporal_validation, tables / "mvp3_temporal_validation.csv")

    preseason_clean = data.dropna(
        subset=[
            "points_per_game",
            "ssb_preseason_elo",
            "relative_log_market",
            "market_gini",
        ]
    ).copy()
    cluster_rows = []
    cluster_scenarios = [
        ("same_season_dynamic_elo", clean, "ssb_continuous"),
        ("same_season_fixed_start_elo", preseason_clean, "ssb_preseason_elo"),
    ]
    if not lagged_market.empty:
        cluster_scenarios.extend(
            [
                ("same_season_lagged_sample", current_restricted, "ssb_continuous"),
                ("preceding_season_dynamic_elo", lagged_market, "ssb_continuous"),
            ]
        )
    for specification, frame, balance in cluster_scenarios:
        term = f"{balance}:relative_log_market:market_gini"
        for cluster_label, cluster_column, use_t in (
            ("league_season", "league_season", False),
            ("league_small_sample_t", "league_name", True),
        ):
            fitted = _fit_mvp3_model(
                frame,
                "points_per_game",
                balance,
                cluster_column=cluster_column,
                use_t=use_t,
            )
            row = _coefficient_table(fitted, [term]).iloc[0].to_dict()
            row.update(
                {
                    "specification": specification,
                    "schedule_balance": balance,
                    "cluster": cluster_label,
                    "clusters": frame[cluster_column].nunique(),
                }
            )
            cluster_rows.append(row)
    cluster_sensitivity = pd.DataFrame(cluster_rows)
    _save_table(cluster_sensitivity, tables / "mvp3_cluster_sensitivity.csv")

    timing_audit = pd.DataFrame(
        [
            {
                "check": "article_wording",
                "status": "claimed_pre_season",
                "evidence": "The source article calls the financial data pre-season on PDF page 10.",
            },
            {
                "check": "row_level_snapshot_timestamp",
                "status": "not_available",
                "evidence": "Neither the released standings nor the 451 Bronze CSVs contains a valuation timestamp.",
            },
            {
                "check": "season_identifier",
                "status": "season_only",
                "evidence": "The scraper validates saison_id, which identifies a season but not an intra-season valuation date.",
            },
            {
                "check": "release_archive_collection",
                "status": "post_season_bulk_collection",
                "evidence": "ZIP metadata dates all 451 historical value CSVs to 2026-03-18; the covered seasons end in 2024.",
            },
            {
                "check": "lagged_market_sensitivity",
                "status": "sign_compatible_not_precise",
                "evidence": (
                    f"Preceding-season model estimate {lagged_result['estimate']:.4f}, "
                    f"95% CI [{lagged_result['ci_low']:.4f}, {lagged_result['ci_high']:.4f}], "
                    f"n={int(lagged_result['nobs'])}."
                ),
            },
            {
                "check": "independent_temporal_verification",
                "status": "not_verified",
                "evidence": "The pre-season label cannot be independently established from the released row-level provenance.",
            },
        ]
    )
    _save_table(timing_audit, tables / "mvp3_market_timing_audit.csv")
    summary = clean.groupby("league_name").agg(
        seasons=("season_year", "nunique"), market_gini_mean=("market_gini", "mean"), market_gini_sd=("market_gini", "std")
    ).reset_index()
    _save_table(summary, tables / "mvp3_market_inequality.csv")
    fig, ax = plt.subplots(figsize=(9, 5))
    for market_label, frame in marginal.groupby("relative_market_quantile"):
        frame = frame.sort_values("market_gini")
        ax.plot(
            frame["market_gini"],
            frame["estimate"],
            marker="o",
            label=f"relative value q={market_label:.1f}",
        )
        ax.fill_between(
            frame["market_gini"], frame["ci_low"], frame["ci_high"], alpha=0.12
        )
    ax.axhline(0, color="grey", linestyle="--")
    ax.set(
        xlabel="Market-value Gini",
        ylabel="Marginal SSB association with points per game",
        title="MVP 3: conditional association in supported regions",
    )
    ax.legend()
    _save_figure(fig, figures / "mvp3_inequality_support.png")
    main = coeff.loc[coeff["term"] == "ssb_continuous:relative_log_market:market_gini"].iloc[0]
    viable = len(clean) >= criteria["minimum_team_seasons"] and clean["market_gini"].std() > 0.02
    sign = np.sign(main["estimate"])
    loo_sign_share = float((np.sign(leave_one_out_frame["estimate"]) == sign).mean())
    safe_specs = specifications[specifications["schedule_strength_temporally_safe"]]
    alternative_sign_share = float((np.sign(safe_specs["estimate"]) == sign).mean())
    hierarchical_sign_compatible = bool(
        np.sign(hierarchical_result.iloc[0]["estimate"]) == sign
        and hierarchical_model.converged
    )
    holdout = temporal_validation[
        (temporal_validation["value_source"] == "same_season")
        & (temporal_validation["period"] == "late_holdout")
    ].iloc[0]
    league_cluster = cluster_sensitivity[
        (cluster_sensitivity["specification"] == "same_season_dynamic_elo")
        & (cluster_sensitivity["cluster"] == "league_small_sample_t")
    ].iloc[0]
    preseason_elo_result = cluster_sensitivity[
        (cluster_sensitivity["specification"] == "same_season_fixed_start_elo")
        & (cluster_sensitivity["cluster"] == "league_season")
    ].iloc[0]
    temporal_sign_compatible = bool(np.sign(holdout["estimate"]) == sign)
    conservative_cluster_sign_compatible = bool(
        np.sign(league_cluster["estimate"]) == sign
    )
    preseason_elo_sign_compatible = bool(
        np.sign(preseason_elo_result["estimate"]) == sign
    )
    minimum_cell_n = int(support_table["n"].min())
    meaningful = bool(marginal["estimate"].abs().max() >= criteria["sesoi_ppg_per_ssb_unit"])
    robust = (
        loo_sign_share >= 0.8
        and alternative_sign_share >= 0.5
        and hierarchical_sign_compatible
        and temporal_sign_compatible
        and conservative_cluster_sign_compatible
        and preseason_elo_sign_compatible
        and minimum_cell_n >= 100
    )
    status = "avançar" if viable and robust and meaningful else "reformular"
    return {
        "mvp": 3,
        "status": status,
        "n": len(clean),
        "gini_sd": float(clean["market_gini"].std()),
        "triple_interaction": float(main["estimate"]),
        "ci_low": float(main["ci_low"]),
        "ci_high": float(main["ci_high"]),
        "p_value": float(main["p_value"]),
        "leave_one_league_out_sign_share": loo_sign_share,
        "schedule_strength_safe_alternative_sign_share": alternative_sign_share,
        "hierarchical_sign_compatible": hierarchical_sign_compatible,
        "minimum_support_cell_n": minimum_cell_n,
        "nonlinearity_p_value": float(nonlinear_test.pvalue),
        "market_timestamp_verified": False,
        "lagged_market_n": int(lagged_result["nobs"]),
        "lagged_market_coverage": float(lagged_result.get("row_coverage", np.nan)),
        "lagged_market_triple_interaction": float(lagged_result["estimate"]),
        "lagged_market_ci_low": float(lagged_result["ci_low"]),
        "lagged_market_ci_high": float(lagged_result["ci_high"]),
        "lagged_market_p_value": float(lagged_result["p_value"]),
        "lagged_market_leave_one_league_out_sign_share": lagged_sign_share,
        "holdout_triple_interaction": float(holdout["estimate"]),
        "holdout_ci_low": float(holdout["ci_low"]),
        "holdout_ci_high": float(holdout["ci_high"]),
        "holdout_p_value": float(holdout["p_value"]),
        "league_cluster_ci_low": float(league_cluster["ci_low"]),
        "league_cluster_ci_high": float(league_cluster["ci_high"]),
        "league_cluster_p_value": float(league_cluster["p_value"]),
        "preseason_elo_triple_interaction": float(preseason_elo_result["estimate"]),
        "preseason_elo_ci_low": float(preseason_elo_result["ci_low"]),
        "preseason_elo_ci_high": float(preseason_elo_result["ci_high"]),
        "preseason_elo_p_value": float(preseason_elo_result["p_value"]),
        "interpretation": (
            "Observational moderation with sign-compatible temporal holdout and fixed "
            "season-start Elo; conservative league-clustered and lagged-value intervals "
            "include zero."
        ),
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


def _permutation_null(
    frame: pd.DataFrame,
    ranks: dict[str, float],
    permutations: int,
    rng: np.random.Generator,
    null_type: str,
    batch_size: int = 500,
) -> np.ndarray:
    """Simulate mean absolute SSB while moving each existing round as one unit."""
    rounds = np.sort(frame["round"].unique())
    round_index = {value: index for index, value in enumerate(rounds)}
    teams = sorted(set(frame["home_team_canonical"]) | set(frame["away_team_canonical"]))
    team_arrays = []
    for team in teams:
        fixtures = frame[
            (frame["home_team_canonical"] == team) | (frame["away_team_canonical"] == team)
        ].sort_values(["round", "kickoff", "match_id"])
        fixtures = fixtures.assign(
            opponent=np.where(
                fixtures["home_team_canonical"] == team,
                fixtures["away_team_canonical"],
                fixtures["home_team_canonical"],
            ),
            round_index=lambda values: values["round"].map(round_index),
        )
        fixtures["tie_breaker"] = (
            fixtures.groupby("round").cumcount() / (len(fixtures) + 1) / 100
        )
        opponents = sorted(fixtures["opponent"].unique())
        if len(opponents) < 4 or any(opponent not in ranks for opponent in opponents):
            continue
        max_occurrences = int(fixtures.groupby("opponent").size().max())
        occurrence_rounds = np.full((len(opponents), max_occurrences), len(rounds), dtype=int)
        tie_breakers = np.zeros((len(opponents), max_occurrences), dtype=float)
        for opponent_number, opponent in enumerate(opponents):
            opponent_fixtures = fixtures[fixtures["opponent"] == opponent]
            count = len(opponent_fixtures)
            occurrence_rounds[opponent_number, :count] = opponent_fixtures[
                "round_index"
            ].to_numpy(dtype=int)
            tie_breakers[opponent_number, :count] = opponent_fixtures[
                "tie_breaker"
            ].to_numpy(dtype=float)
        strength_ranks = rankdata(
            np.asarray([ranks[opponent] for opponent in opponents], dtype=float),
            method="average",
        )
        market_centered = strength_ranks - strength_ranks.mean()
        order_centered = np.arange(len(opponents), dtype=float)
        order_centered -= order_centered.mean()
        denominator = np.sqrt(
            np.sum(order_centered**2) * np.sum(market_centered**2)
        )
        if denominator <= 0:
            continue
        team_arrays.append((occurrence_rounds, tie_breakers, market_centered, denominator))
    if len(team_arrays) < 4:
        return np.asarray([])

    draws = np.empty(permutations, dtype=float)
    phase_groups = np.array_split(np.arange(len(rounds)), 2)
    for start in range(0, permutations, batch_size):
        size = min(batch_size, permutations - start)
        priorities = np.empty((size, len(rounds) + 1), dtype=float)
        for row in range(size):
            if null_type == "global_round":
                priorities[row, :-1] = rng.permutation(len(rounds))
            elif null_type == "phase_preserving":
                priority = np.arange(len(rounds), dtype=float)
                for phase in phase_groups:
                    priority[phase] = rng.permutation(phase)
                priorities[row, :-1] = priority
            else:
                raise ValueError(f"Unknown null type: {null_type}")
        priorities[:, -1] = len(rounds) + 1
        absolute_correlations = []
        for occurrence_rounds, tie_breakers, market_centered, denominator in team_arrays:
            occurrence_priority = priorities[:, occurrence_rounds] + tie_breakers
            earliest = occurrence_priority.min(axis=2)
            order = np.argsort(earliest, axis=1, kind="stable")
            positions = np.argsort(order, axis=1, kind="stable").astype(float)
            positions -= positions.mean(axis=1, keepdims=True)
            correlation = (positions @ market_centered) / denominator
            absolute_correlations.append(np.abs(correlation))
        draws[start : start + size] = np.mean(absolute_correlations, axis=0)
    return draws


def run_mvp4(
    matches: pd.DataFrame,
    standings: pd.DataFrame,
    tables: Path,
    figures: Path,
    config: dict,
    seed: int,
) -> dict:
    selected = matches.copy()
    rank_frame = standings.copy()
    rank_frame["market_rank"] = rank_frame.groupby(
        ["league_name", "season_year"]
    )["total_market_value_euros"].rank(ascending=False, method="first")
    market_maps = {
        key: dict(zip(frame["team_canonical"], frame["market_rank"]))
        for key, frame in rank_frame.groupby(["league_name", "season_year"])
    }

    home_start = selected[
        [
            "league_name",
            "season_year",
            "kickoff",
            "match_id",
            "home_team_canonical",
            "home_elo_pre",
        ]
    ].rename(columns={"home_team_canonical": "team_canonical", "home_elo_pre": "elo"})
    away_start = selected[
        [
            "league_name",
            "season_year",
            "kickoff",
            "match_id",
            "away_team_canonical",
            "away_elo_pre",
        ]
    ].rename(columns={"away_team_canonical": "team_canonical", "away_elo_pre": "elo"})
    season_start = (
        pd.concat([home_start, away_start], ignore_index=True)
        .sort_values(
            ["league_name", "season_year", "team_canonical", "kickoff", "match_id"]
        )
        .groupby(["league_name", "season_year", "team_canonical"], as_index=False)
        .first()
    )
    season_start_maps = {
        key: dict(zip(frame["team_canonical"], frame["elo"]))
        for key, frame in season_start.groupby(["league_name", "season_year"])
    }
    strength_maps = {
        "market_value": market_maps,
        "season_start_elo": season_start_maps,
    }
    agreement_rows = []
    for key in sorted(set(market_maps) & set(season_start_maps)):
        common_teams = sorted(set(market_maps[key]) & set(season_start_maps[key]))
        market_strength = np.asarray(
            [-market_maps[key][team] for team in common_teams], dtype=float
        )
        elo_strength = np.asarray(
            [season_start_maps[key][team] for team in common_teams], dtype=float
        )
        correlation = np.nan
        if (
            len(common_teams) >= 4
            and np.unique(market_strength).size > 1
            and np.unique(elo_strength).size > 1
        ):
            correlation = float(spearmanr(market_strength, elo_strength).statistic)
        agreement_rows.append(
            {
                "league_name": key[0],
                "season_year": key[1],
                "teams": len(common_teams),
                "spearman_strength_correlation": correlation,
            }
        )
    agreement_table = pd.DataFrame(agreement_rows)
    _save_table(agreement_table, tables / "mvp4_strength_agreement.csv")
    rows = []
    coverage_rows = []
    valid_draws = 0
    permutations = int(config["permutations"])
    grouped_seasons = list(
        selected.groupby(["league_name", "season_year"], sort=True)
    )
    for source_number, (strength_source, maps) in enumerate(strength_maps.items()):
        rng = np.random.default_rng(np.random.SeedSequence([seed, source_number]))
        for key, source_frame in grouped_seasons:
            total_matches = len(source_frame)
            frame = source_frame.dropna(subset=["round"]).copy()
            strengths = maps.get(key, {})
            actual = _season_ssb(frame, frame["round"], strengths)
            coverage_rows.append(
                {
                    "league_name": key[0],
                    "season_year": key[1],
                    "strength_source": strength_source,
                    "matches": total_matches,
                    "matches_with_round": len(frame),
                    "rounds": frame["round"].nunique(),
                    "teams_with_valid_ssb": len(actual),
                    "status": (
                        "included"
                        if len(actual) >= 4
                        else "excluded_insufficient_strength_join"
                    ),
                }
            )
            if len(actual) < 4:
                continue
            observed = float(np.mean(np.abs(actual)))
            for null_type in ("global_round", "phase_preserving"):
                null = _permutation_null(
                    frame,
                    strengths,
                    permutations,
                    rng,
                    null_type,
                    int(config.get("batch_size", 500)),
                )
                if len(null) != permutations:
                    continue
                valid_draws += len(null)
                empirical_p = float((1 + np.sum(null >= observed)) / (1 + len(null)))
                rows.append(
                    {
                        "league_name": key[0],
                        "season_year": key[1],
                        "strength_source": strength_source,
                        "null_type": null_type,
                        "teams": len(actual),
                        "observed_mean_abs_ssb": observed,
                        "null_mean_abs_ssb": float(np.mean(null)),
                        "null_sd": float(np.std(null, ddof=1)),
                        "null_q025": float(np.quantile(null, 0.025)),
                        "null_q975": float(np.quantile(null, 0.975)),
                        "empirical_p_upper": empirical_p,
                        "monte_carlo_se": float(
                            np.sqrt(empirical_p * (1 - empirical_p) / len(null))
                        ),
                        "permutations": len(null),
                    }
                )
    result_table = pd.DataFrame(rows)
    result_table["fdr_q_upper"] = np.nan
    for indexes in result_table.groupby(["strength_source", "null_type"]).groups.values():
        result_table.loc[indexes, "fdr_q_upper"] = multipletests(
            result_table.loc[indexes, "empirical_p_upper"], method="fdr_bh"
        )[1]
    _save_table(result_table, tables / "mvp4_counterfactual_schedules.csv")
    _save_table(pd.DataFrame(coverage_rows), tables / "mvp4_coverage.csv")
    fig, ax = plt.subplots(figsize=(8, 6))
    for (strength_source, null_type), frame in result_table.groupby(
        ["strength_source", "null_type"]
    ):
        ax.scatter(
            frame["null_mean_abs_ssb"],
            frame["observed_mean_abs_ssb"],
            s=16,
            alpha=0.55,
            label=f"{strength_source.replace('_', ' ')} / {null_type.replace('_', ' ')}",
        )
    limits = [
        min(result_table["null_mean_abs_ssb"].min(), result_table["observed_mean_abs_ssb"].min()),
        max(result_table["null_mean_abs_ssb"].max(), result_table["observed_mean_abs_ssb"].max()),
    ]
    ax.plot(limits, limits, color="black", linestyle="--", label="observed = null mean")
    ax.set(
        xlabel="Permutation-null mean absolute SSB",
        ylabel="Observed mean absolute SSB",
        title="MVP 4: all-season counterfactual calendar benchmark",
    )
    ax.legend()
    _save_figure(fig, figures / "mvp4_counterfactual.png")
    source_coverage = (
        result_table.groupby("strength_source")
        .apply(
            lambda values: values[["league_name", "season_year"]]
            .drop_duplicates()
            .shape[0],
            include_groups=False,
        )
        .rename("league_seasons")
    )
    league_seasons = int(source_coverage.max())
    viable = bool(
        source_coverage.min() >= 250
        and (result_table["permutations"] == permutations).all()
    )
    stable = result_table["monte_carlo_se"].max() <= 0.0051
    significant = result_table[result_table["fdr_q_upper"] < 0.05]
    source_consistent = (
        significant.groupby(["league_name", "season_year", "null_type"])[
            "strength_source"
        ].nunique()
        == len(strength_maps)
    )
    finite_agreement = agreement_table["spearman_strength_correlation"].dropna()
    return {
        "mvp": 4,
        "status": _decision(viable, stable),
        "league_seasons": league_seasons,
        "minimum_strength_source_league_seasons": int(source_coverage.min()),
        "strength_sources": int(result_table["strength_source"].nunique()),
        "null_models": int(result_table["null_type"].nunique()),
        "valid_permutation_draws": int(valid_draws),
        "league_season_nulls_upper_tail_p_lt_0_05": int(
            (result_table["empirical_p_upper"] < 0.05).sum()
        ),
        "league_season_nulls_fdr_q_lt_0_05": int(
            (result_table["fdr_q_upper"] < 0.05).sum()
        ),
        "source_consistent_fdr_findings": int(source_consistent.sum()),
        "median_strength_source_correlation": float(finite_agreement.median()),
        "strength_source_correlations_below_0_30": int((finite_agreement < 0.30).sum()),
        "interpretation": (
            "Two pre-schedule strength proxies were tested under nulls that preserve "
            "fixtures and home/away assignments; the stricter null also preserves broad "
            "season phase. Cross-proxy agreement and source-consistent FDR findings are "
            "reported separately."
        ),
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
