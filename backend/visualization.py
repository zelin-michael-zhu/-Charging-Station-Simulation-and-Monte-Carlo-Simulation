"""
visualization.py
Generate descriptive statistics and figures for BA3093 report.

Usage:
    /Users/zhuzelin/Desktop/sr/小组作业/.venv/bin/python visualization.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
BACKEND_DIR = ROOT / "backend"
OUT_DIR = ROOT / "report_assets"

# Import project classes/functions.
sys.path.insert(0, str(BACKEND_DIR))
from data_processor import load_baseline_data  # noqa: E402
from monte_carlo import MonteCarloSimulator  # noqa: E402
from queuing_model import QueuingSimulator  # noqa: E402


plt.style.use("seaborn-v0_8-whitegrid")


def ensure_out_dir() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)


def compute_session_duration() -> np.ndarray:
    df_dur = pd.read_csv(DATA_DIR / "duration.csv", index_col=0)
    df_occ = pd.read_csv(DATA_DIR / "occupancy.csv", index_col=0)

    common_cols = df_dur.columns.intersection(df_occ.columns)
    dur_vals = df_dur[common_cols].to_numpy().flatten().astype(float)
    occ_vals = df_occ[common_cols].to_numpy().flatten().astype(float)

    mask = (occ_vals > 0.5) & (dur_vals > 0) & np.isfinite(occ_vals) & np.isfinite(dur_vals)
    session_duration = dur_vals[mask] / occ_vals[mask]

    p95 = np.percentile(session_duration, 95)
    return session_duration[session_duration <= p95]


def descriptive_stats_table() -> pd.DataFrame:
    baseline = load_baseline_data()
    session_duration = compute_session_duration()
    df_inf = pd.read_csv(DATA_DIR / "inf.csv")

    table = pd.DataFrame(
        [
            {
                "Metric": "Number of stations",
                "Value": len(df_inf),
                "Note": "From inf.csv",
            },
            {
                "Metric": "Average charging piles per station (c)",
                "Value": round(float(df_inf["charge_count"].mean()), 3),
                "Note": "Queue capacity proxy",
            },
            {
                "Metric": "Service rate (mu, sessions/hour/pile)",
                "Value": round(float(baseline["mu"]), 4),
                "Note": "mu = 1 / mean(service time)",
            },
            {
                "Metric": "Arrival rate (lambda, sessions/hour/station)",
                "Value": round(float(baseline["lambda_rate"]), 4),
                "Note": "Estimated via Little's Law",
            },
            {
                "Metric": "Peak arrival rate (sessions/hour, 4h)",
                "Value": round(float(baseline["peak_lambda_rate"]), 4),
                "Note": "50% daily volume allocated to 4 peak hours",
            },
            {
                "Metric": "Off-peak arrival rate (sessions/hour, 20h)",
                "Value": round(float(baseline["offpeak_lambda_rate"]), 4),
                "Note": "50% daily volume allocated to 20 off-peak hours",
            },
            {
                "Metric": "Service-time CV",
                "Value": round(float(baseline["service_time_cv"]), 4),
                "Note": "Used for M/G/c correction",
            },
            {
                "Metric": "Mean service duration (hours)",
                "Value": round(float(np.mean(session_duration)), 4),
                "Note": "duration/occupancy",
            },
        ]
    )
    table.to_csv(OUT_DIR / "descriptive_statistics.csv", index=False)
    return table


def fig_charge_count_distribution() -> None:
    df_inf = pd.read_csv(DATA_DIR / "inf.csv")
    vals = df_inf["charge_count"].to_numpy()

    plt.figure(figsize=(8, 5))
    plt.hist(vals, bins=30, color="#4f9eff", alpha=0.85, edgecolor="white")
    plt.axvline(vals.mean(), color="#f87171", linestyle="--", linewidth=1.8, label=f"Mean={vals.mean():.2f}")
    plt.title("Distribution of Charging Piles per Station")
    plt.xlabel("Number of charging piles")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_01_charge_count_distribution.png", dpi=180)
    plt.close()


def fig_service_duration_distribution() -> None:
    x = compute_session_duration()
    mean_x = x.mean()
    cv_x = x.std() / mean_x

    plt.figure(figsize=(8, 5))
    plt.hist(x, bins=60, density=True, color="#34d399", alpha=0.72, edgecolor="white")

    grid = np.linspace(0.001, max(1.5, float(np.percentile(x, 99))), 500)
    exp_pdf = (1.0 / mean_x) * np.exp(-grid / mean_x)
    plt.plot(grid, exp_pdf, color="#ef4444", linewidth=2.0, label="Exponential benchmark")

    plt.title("Empirical Service Duration Distribution")
    plt.xlabel("Service duration (hours)")
    plt.ylabel("Density")
    plt.text(
        0.98,
        0.93,
        f"Mean={mean_x:.3f}h\nCV={cv_x:.3f}",
        transform=plt.gca().transAxes,
        ha="right",
        va="top",
        bbox=dict(boxstyle="round", fc="white", ec="#d1d5db"),
    )
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_02_service_duration_distribution.png", dpi=180)
    plt.close()


def run_single_scenario(occupancy_change: float, wait_cost_change: float = 0.0) -> dict:
    baseline = load_baseline_data()

    peak_lambda = baseline["peak_lambda_rate"] * (1.0 + occupancy_change)
    offpeak_lambda = baseline["offpeak_lambda_rate"] * (1.0 + occupancy_change)
    wait_cost = baseline["wait_cost_per_minute"] * (1.0 + wait_cost_change)

    q_peak = QueuingSimulator(
        lam=peak_lambda,
        mu=baseline["mu"],
        c=baseline["c"],
        service_time_cv=baseline["service_time_cv"],
    ).compute()
    q_offpeak = QueuingSimulator(
        lam=offpeak_lambda,
        mu=baseline["mu"],
        c=baseline["c"],
        service_time_cv=baseline["service_time_cv"],
    ).compute()

    total_hours = baseline["peak_hours"] + baseline["offpeak_hours"]
    avg_wait = (
        q_peak.wq_minutes * baseline["peak_hours"]
        + q_offpeak.wq_minutes * baseline["offpeak_hours"]
    ) / total_hours
    avg_wait_base = (
        q_peak.wq_mmc_minutes * baseline["peak_hours"]
        + q_offpeak.wq_mmc_minutes * baseline["offpeak_hours"]
    ) / total_hours
    avg_util = (
        q_peak.rho * baseline["peak_hours"]
        + q_offpeak.rho * baseline["offpeak_hours"]
    ) / total_hours

    mc = MonteCarloSimulator(
        peak_lambda_rate=peak_lambda,
        offpeak_lambda_rate=offpeak_lambda,
        peak_hours=baseline["peak_hours"],
        offpeak_hours=baseline["offpeak_hours"],
        mu=baseline["mu"],
        c=baseline["c"],
        service_time_cv=baseline["service_time_cv"],
        mean_kwh=baseline["mean_kwh"],
        std_kwh=baseline["std_kwh"],
        mean_e_price=baseline["mean_e_price"],
        mean_s_price=baseline["mean_s_price"],
        std_e_price=baseline["std_e_price"],
        std_s_price=baseline["std_s_price"],
        wholesale_price=baseline["wholesale_price"],
        daily_fixed_cost=baseline["daily_fixed_cost"],
        wait_cost_per_minute=wait_cost,
        service_fee_change=0.0,
        electricity_cost_change=0.0,
        n_iter=1000,
        seed=42,
    ).run()

    return {
        "utilization": avg_util,
        "wait_base": avg_wait_base,
        "wait_mgc": avg_wait,
        "mgc_factor": q_peak.mgc_correction_factor,
        "mean_profit": mc.mean_profit,
        "var_5pct": mc.var_5pct,
        "prob_loss": mc.prob_loss,
        "mean_wait_penalty": mc.mean_wait_penalty,
        "peak_utilization": mc.mean_peak_utilization,
        "peak_wait_minutes": mc.mean_peak_wait_minutes,
        "profits": np.array(mc.profits),
    }


def fig_monte_carlo_histogram() -> None:
    res = run_single_scenario(occupancy_change=0.0, wait_cost_change=0.0)
    profits = res["profits"]
    var5 = res["var_5pct"]
    cvar5 = profits[profits <= var5].mean()

    plt.figure(figsize=(8, 5))
    plt.hist(profits, bins=35, color="#60a5fa", alpha=0.84, edgecolor="white")
    plt.axvline(var5, color="#ef4444", linestyle="--", linewidth=2, label=f"VaR 5% = {var5:.2f}")
    plt.axvline(cvar5, color="#f59e0b", linestyle="-.", linewidth=2, label=f"CVaR 5% = {cvar5:.2f}")
    plt.title("Monte Carlo Profit Distribution (Baseline)")
    plt.xlabel("Daily profit (RMB)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_03_profit_distribution_var_cvar.png", dpi=180)
    plt.close()


def fig_queue_sensitivity_curve() -> None:
    b = load_baseline_data()
    multipliers = np.linspace(0.3, 5.5, 41)
    waits: list[float] = []
    util_arr: list[float] = []

    for m in multipliers:
        lam = b["lambda_rate"] * m
        q = QueuingSimulator(
            lam=lam, mu=b["mu"], c=b["c"], service_time_cv=b["service_time_cv"]
        ).compute()
        waits.append(min(float(q.wq_minutes), 120.0))  # cap display at 120 min
        util_arr.append(float(q.rho))

    waits_arr = np.array(waits)
    util_np = np.array(util_arr)

    fig, ax1 = plt.subplots(figsize=(9, 5))
    color_wait = "#2563eb"
    color_util = "#16a34a"

    (ln1,) = ax1.plot(multipliers, waits_arr, color=color_wait, linewidth=2.0,
                      label="Mean queue wait (M/G/c, min)")
    ax1.set_xlabel("Demand multiplier (× baseline λ)")
    ax1.set_ylabel("Mean queue wait time (min)", color=color_wait)
    ax1.tick_params(axis="y", labelcolor=color_wait)

    ax2 = ax1.twinx()
    (ln2,) = ax2.plot(multipliers, util_np, color=color_util, linewidth=1.8,
                      linestyle="--", label="Utilisation ρ")
    (ln3,) = ax2.plot([], [], color="#dc2626", linestyle=":", linewidth=1.5,
                      label="ρ = 0.8 congestion threshold")
    ax2.axhline(0.8, color="#dc2626", linestyle=":", linewidth=1.5)
    ax2.set_ylabel("Utilisation ρ", color=color_util)
    ax2.tick_params(axis="y", labelcolor=color_util)
    ax2.set_ylim(0, 1.05)

    (ln0,) = ax1.plot([], [], color="#6b7280", linestyle="--", linewidth=1.8,
                      label="Baseline λ (×1)")
    ax1.axvline(1.0, color="#6b7280", linestyle="--", linewidth=1.8)

    ax1.legend(handles=[ln1, ln0, ln2, ln3], loc="upper left", fontsize=8)
    plt.title("Queue Sensitivity to Demand Level")
    fig.tight_layout()
    plt.savefig(OUT_DIR / "fig_04_queue_sensitivity_curve.png", dpi=180)
    plt.close()


def fig_tornado_profit_sensitivity() -> None:
    from data_processor import load_baseline_data as _load  # noqa: E402

    b = _load()

    def _run(
        occ: float = 0.0,
        svc: float = 0.0,
        elec: float = 0.0,
        wait: float = 0.0,
        fixc: float = 0.0,
        kwh: float = 0.0,
    ) -> float:
        peak_lambda = b["peak_lambda_rate"] * (1.0 + occ)
        offpeak_lambda = b["offpeak_lambda_rate"] * (1.0 + occ)
        wc = b["wait_cost_per_minute"] * (1.0 + wait)
        mc = MonteCarloSimulator(
            peak_lambda_rate=peak_lambda,
            offpeak_lambda_rate=offpeak_lambda,
            peak_hours=b["peak_hours"],
            offpeak_hours=b["offpeak_hours"],
            mu=b["mu"],
            c=b["c"],
            service_time_cv=b["service_time_cv"],
            mean_kwh=b["mean_kwh"] * (1.0 + kwh),
            std_kwh=b["std_kwh"],
            mean_e_price=b["mean_e_price"],
            mean_s_price=b["mean_s_price"],
            std_e_price=b["std_e_price"],
            std_s_price=b["std_s_price"],
            wholesale_price=b["wholesale_price"],
            daily_fixed_cost=b["daily_fixed_cost"] * (1.0 + fixc),
            wait_cost_per_minute=wc,
            service_fee_change=svc,
            electricity_cost_change=elec,
            n_iter=1000,
            seed=42,
        ).run()
        return mc.mean_profit

    base_profit = _run()

    # Each tuple: (label, hi_kwargs, lo_kwargs)
    param_specs = [
        ("Occupancy (λ)",           dict(occ=+0.2),  dict(occ=-0.2)),
        ("Service fee (p_s)",       dict(svc=+0.2),  dict(svc=-0.2)),
        ("Wholesale cost (p_w)",    dict(elec=+0.2), dict(elec=-0.2)),
        ("Fixed cost (C_f)",        dict(fixc=+0.2), dict(fixc=-0.2)),
        ("kWh/session (Q\u0304)",   dict(kwh=+0.2),  dict(kwh=-0.2)),
        ("Wait cost (c_wait)",      dict(wait=+0.2), dict(wait=-0.2)),
    ]

    results = []
    for label, hi_kw, lo_kw in param_specs:
        hi_delta = _run(**hi_kw) - base_profit
        lo_delta = _run(**lo_kw) - base_profit
        results.append((label, lo_delta, hi_delta))

    # Sort by total swing (ascending so most impactful appears at top of chart)
    results.sort(key=lambda x: abs(x[2] - x[1]))

    labels   = [r[0] for r in results]
    lo_vals  = np.array([r[1] for r in results])
    hi_vals  = np.array([r[2] for r in results])

    fig, ax = plt.subplots(figsize=(9, 6))
    y_pos = np.arange(len(labels))

    for i, (lo, hi) in enumerate(zip(lo_vals, hi_vals)):
        down = min(lo, hi)
        up   = max(lo, hi)
        if down < 0:
            ax.barh(i, down, left=0, color="#dc2626", alpha=0.82, label="-20% shock" if i == 0 else "")
        if up > 0:
            ax.barh(i, up,   left=0, color="#16a34a", alpha=0.82, label="+20% shock" if i == 0 else "")

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.axvline(0, color="#374151", linewidth=1)
    ax.set_title("Tornado Chart: ±20% Sensitivity of Mean Daily Profit")
    ax.set_xlabel("Change in expected daily profit (RMB)")
    ax.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_05_tornado_sensitivity.png", dpi=180)
    plt.close()


def fig_wait_penalty_response() -> None:
    from data_processor import load_baseline_data as _load  # noqa: E402

    b = _load()

    # X-axis: demand multiplier relative to baseline λ
    demand_multipliers = np.linspace(0.5, 5.5, 40)
    wait_cost_scenarios = [
        (0.005, "#2563eb", "c_wait = 0.005 ¥/min"),
        (0.010, "#b45309", "c_wait = 0.010 ¥/min (baseline)"),
        (0.020, "#dc2626", "c_wait = 0.020 ¥/min"),
    ]

    plt.figure(figsize=(9, 5))
    for wc, color, lbl in wait_cost_scenarios:
        penalties = []
        for m in demand_multipliers:
            peak_lambda = b["peak_lambda_rate"] * m
            offpeak_lambda = b["offpeak_lambda_rate"] * m
            mc = MonteCarloSimulator(
                peak_lambda_rate=peak_lambda,
                offpeak_lambda_rate=offpeak_lambda,
                peak_hours=b["peak_hours"],
                offpeak_hours=b["offpeak_hours"],
                mu=b["mu"],
                c=b["c"],
                service_time_cv=b["service_time_cv"],
                mean_kwh=b["mean_kwh"],
                std_kwh=b["std_kwh"],
                mean_e_price=b["mean_e_price"],
                mean_s_price=b["mean_s_price"],
                std_e_price=b["std_e_price"],
                std_s_price=b["std_s_price"],
                wholesale_price=b["wholesale_price"],
                daily_fixed_cost=b["daily_fixed_cost"],
                wait_cost_per_minute=wc,
                n_iter=1000,
                seed=42,
            ).run()
            penalties.append(mc.mean_wait_penalty)
        plt.plot(demand_multipliers, penalties, color=color, linewidth=2.2, label=lbl)

    plt.axvline(1.0, color="#6b7280", linestyle="--", linewidth=1.8, label="Baseline λ")
    plt.title("Wait-Penalty Cost vs. Demand Multiplier")
    plt.xlabel("Demand multiplier (× baseline λ)")
    plt.ylabel("Expected wait-penalty cost (RMB/day)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_06_wait_penalty_response.png", dpi=180)
    plt.close()


def main() -> None:
    ensure_out_dir()

    stats = descriptive_stats_table()
    print("Descriptive statistics saved:")
    print(stats.to_string(index=False))

    fig_charge_count_distribution()
    fig_service_duration_distribution()
    fig_monte_carlo_histogram()
    fig_queue_sensitivity_curve()
    fig_tornado_profit_sensitivity()
    fig_wait_penalty_response()

    print(f"\nAll figures generated in: {OUT_DIR}")


if __name__ == "__main__":
    main()
