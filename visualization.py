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

    lam = baseline["lambda_rate"] * (1.0 + occupancy_change)
    wait_cost = baseline["wait_cost_per_minute"] * (1.0 + wait_cost_change)

    q = QueuingSimulator(
        lam=lam,
        mu=baseline["mu"],
        c=baseline["c"],
        service_time_cv=baseline["service_time_cv"],
    ).compute()

    mc = MonteCarloSimulator(
        daily_sessions=q.daily_sessions,
        mean_kwh=baseline["mean_kwh"],
        std_kwh=baseline["std_kwh"],
        mean_e_price=baseline["mean_e_price"],
        mean_s_price=baseline["mean_s_price"],
        std_e_price=baseline["std_e_price"],
        std_s_price=baseline["std_s_price"],
        wholesale_price=baseline["wholesale_price"],
        daily_fixed_cost=baseline["daily_fixed_cost"],
        mean_wait_minutes=q.wq_minutes,
        wait_cost_per_minute=wait_cost,
        service_fee_change=0.0,
        electricity_cost_change=0.0,
        n_iter=1000,
        seed=42,
    ).run()

    return {
        "utilization": q.rho,
        "wait_base": q.wq_mmc_minutes,
        "wait_mgc": q.wq_minutes,
        "mgc_factor": q.mgc_correction_factor,
        "mean_profit": mc.mean_profit,
        "var_5pct": mc.var_5pct,
        "prob_loss": mc.prob_loss,
        "mean_wait_penalty": mc.mean_wait_penalty,
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
    occ_grid = np.linspace(-0.5, 2.0, 21)
    waits = []
    util = []

    for oc in occ_grid:
        r = run_single_scenario(occupancy_change=float(oc), wait_cost_change=0.0)
        waits.append(float(r["wait_mgc"]))
        util.append(float(r["utilization"]))

    plt.figure(figsize=(8, 5))
    plt.plot(occ_grid * 100, waits, marker="o", color="#2563eb", linewidth=2, label="Mean wait (M/G/c)")
    plt.plot(occ_grid * 100, np.array(util) * 10, marker="s", color="#16a34a", linewidth=1.8, label="Utilization x10")
    plt.title("Queue Sensitivity to Demand Shock")
    plt.xlabel("Occupancy change (%)")
    plt.ylabel("Minutes / Scaled utilization")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_04_queue_sensitivity_curve.png", dpi=180)
    plt.close()


def fig_tornado_profit_sensitivity() -> None:
    # Finite-difference sensitivity around baseline.
    baseline = run_single_scenario(occupancy_change=0.0, wait_cost_change=0.0)
    base_profit = baseline["mean_profit"]

    shocks = {
        "Service fee +20%": {"service_fee_change": 0.2, "electricity_cost_change": 0.0, "occupancy_change": 0.0, "wait_cost_change": 0.0},
        "Electricity cost +20%": {"service_fee_change": 0.0, "electricity_cost_change": 0.2, "occupancy_change": 0.0, "wait_cost_change": 0.0},
        "Occupancy +20%": {"service_fee_change": 0.0, "electricity_cost_change": 0.0, "occupancy_change": 0.2, "wait_cost_change": 0.0},
        "Wait cost +100%": {"service_fee_change": 0.0, "electricity_cost_change": 0.0, "occupancy_change": 0.0, "wait_cost_change": 1.0},
    }

    # Reuse model classes directly for flexible perturbation.
    from data_processor import load_baseline_data as _load  # noqa: E402

    b = _load()
    effects = {}
    for k, cfg in shocks.items():
        lam = b["lambda_rate"] * (1.0 + cfg["occupancy_change"])
        wait_cost = b["wait_cost_per_minute"] * (1.0 + cfg["wait_cost_change"])

        q = QueuingSimulator(lam=lam, mu=b["mu"], c=b["c"], service_time_cv=b["service_time_cv"]).compute()
        mc = MonteCarloSimulator(
            daily_sessions=q.daily_sessions,
            mean_kwh=b["mean_kwh"],
            std_kwh=b["std_kwh"],
            mean_e_price=b["mean_e_price"],
            mean_s_price=b["mean_s_price"],
            std_e_price=b["std_e_price"],
            std_s_price=b["std_s_price"],
            wholesale_price=b["wholesale_price"],
            daily_fixed_cost=b["daily_fixed_cost"],
            mean_wait_minutes=q.wq_minutes,
            wait_cost_per_minute=wait_cost,
            service_fee_change=cfg["service_fee_change"],
            electricity_cost_change=cfg["electricity_cost_change"],
            n_iter=1000,
            seed=42,
        ).run()
        effects[k] = mc.mean_profit - base_profit

    labels = list(effects.keys())
    values = np.array([effects[k] for k in labels])
    order = np.argsort(np.abs(values))
    labels = [labels[i] for i in order]
    values = values[order]

    colors = ["#16a34a" if v >= 0 else "#dc2626" for v in values]
    plt.figure(figsize=(8, 5))
    plt.barh(labels, values, color=colors, alpha=0.85)
    plt.axvline(0, color="#374151", linewidth=1)
    plt.title("Tornado-Style Sensitivity of Mean Profit")
    plt.xlabel("Change in expected daily profit (RMB)")
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_05_tornado_sensitivity.png", dpi=180)
    plt.close()


def fig_wait_penalty_response() -> None:
    wc_grid = np.linspace(-0.5, 2.0, 26)
    penalties = []

    for wc in wc_grid:
        r = run_single_scenario(occupancy_change=2.0, wait_cost_change=float(wc))
        penalties.append(float(r["mean_wait_penalty"]))

    plt.figure(figsize=(8, 5))
    plt.plot(wc_grid * 100, penalties, color="#b45309", linewidth=2.2, marker="o", markersize=3.5)
    plt.title("Wait-Penalty Cost Response (High-Demand Scenario)")
    plt.xlabel("Wait-cost change (%)")
    plt.ylabel("Expected wait-penalty cost (RMB/day)")
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
