"""
visualization.py
Generate descriptive statistics and figures for BA3093 report.

Usage:
    /Users/zhuzelin/Desktop/sr/小组作业/.venv/bin/python visualization.py
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Polygon


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


def _lonlat_to_web_mercator(lon: np.ndarray, lat: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Convert lon/lat (EPSG:4326) to Web Mercator meters (EPSG:3857)."""
    x = lon * 20037508.34 / 180.0
    lat_clip = np.clip(lat, -85.05112878, 85.05112878)
    y = np.log(np.tan((90.0 + lat_clip) * np.pi / 360.0)) * 20037508.34 / np.pi
    return x, y


def _convex_hull(points: np.ndarray) -> np.ndarray:
    """Monotonic chain convex hull. Returns hull points in order."""
    pts = np.unique(points, axis=0)
    if len(pts) <= 2:
        return pts

    pts = pts[np.lexsort((pts[:, 1], pts[:, 0]))]

    def cross(o: np.ndarray, a: np.ndarray, b: np.ndarray) -> float:
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper = []
    for p in pts[::-1]:
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return np.array(lower[:-1] + upper[:-1])


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


def fig_shenzhen_station_distribution_map() -> None:
    """Shenzhen station KDE-density map (UrbanEV reference style).

    - White background + Shenzhen administrative boundary outline
    - Gaussian KDE heatmap weighted by charge_count (white → cyan → teal)
    - Black dots for each charging station
    - Scale bar, north arrow, piles/km² colourbar
    """
    import json as _json
    import urllib.request
    from matplotlib.colors import LinearSegmentedColormap
    from scipy.stats import gaussian_kde  # type: ignore

    # ── Data ──────────────────────────────────────────────────────────────
    df = pd.read_csv(DATA_DIR / "inf.csv")
    df = df.dropna(subset=["longitude", "latitude"])
    df = df[df["longitude"].between(113.72, 114.70) & df["latitude"].between(22.38, 22.87)]

    lon = df["longitude"].to_numpy(dtype=float)
    lat = df["latitude"].to_numpy(dtype=float)
    charge = df["charge_count"].fillna(1).to_numpy(dtype=float)
    total_piles = float(charge.sum())
    n_station = len(df)

    # ── KDE on a regular lon/lat grid ─────────────────────────────────────
    lon_min, lon_max = 113.72, 114.70
    lat_min, lat_max = 22.38, 22.87
    grid_res = 400

    lon_g = np.linspace(lon_min, lon_max, grid_res)
    lat_g = np.linspace(lat_min, lat_max, grid_res)
    LON, LAT = np.meshgrid(lon_g, lat_g)

    kernel = gaussian_kde(np.vstack([lon, lat]), weights=charge, bw_method=0.030)
    Z = kernel(np.vstack([LON.ravel(), LAT.ravel()])).reshape(grid_res, grid_res)

    # Convert probability density (per degree²) → piles / km²
    lat_c = float(np.mean(lat))
    km2_per_deg2 = 111.0 * 111.0 * np.cos(np.radians(lat_c))
    Z_km2 = Z * total_piles / km2_per_deg2

    # ── Colourmap: white → light-cyan → cyan → teal (reference style) ────
    cmap_kde = LinearSegmentedColormap.from_list(
        "kde_sz",
        ["#ffffff", "#e0f7fa", "#80deea", "#26c6da", "#00838f", "#004d40"],
        N=256,
    )

    # ── Figure ────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(12, 7))
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")

    # KDE heatmap
    im = ax.imshow(
        Z_km2,
        extent=[lon_min, lon_max, lat_min, lat_max],
        origin="lower",
        cmap=cmap_kde,
        alpha=0.82,
        aspect="auto",
        vmin=0,
        zorder=2,
    )

    # ── Shenzhen administrative boundary (Aliyun DataV open API) ─────────
    boundary_drawn = False
    try:
        url = "https://geo.datav.aliyun.com/areas_v3/bound/440300_full.json"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            geo = _json.loads(resp.read())
        for feature in geo.get("features", []):
            geom = feature.get("geometry", {})
            gtype = geom.get("type", "")
            rings: list = []
            if gtype == "Polygon":
                rings = geom["coordinates"]
            elif gtype == "MultiPolygon":
                for poly in geom["coordinates"]:
                    rings.extend(poly)
            for ring in rings:
                r = np.array(ring)
                ax.plot(r[:, 0], r[:, 1], color="#333333", linewidth=0.55, zorder=5)
        boundary_drawn = True
    except Exception:
        boundary_drawn = False

    if not boundary_drawn:
        # Convex hull as fallback outline
        hull = _convex_hull(np.column_stack([lon, lat]))
        closed = np.vstack([hull, hull[0]])
        ax.plot(closed[:, 0], closed[:, 1], color="#333333", linewidth=1.2, zorder=5)

    # ── Station dots ──────────────────────────────────────────────────────
    ax.scatter(lon, lat, s=5, c="black", linewidths=0, alpha=0.75, zorder=6)

    # ── Scale bar (bottom-centre, 0 – 7.5 – 15 km) ───────────────────────
    km_per_deg_lon = 111.0 * np.cos(np.radians(lat_c))
    bar_deg = 7.5 / km_per_deg_lon          # degrees lon for 7.5 km
    bx0 = lon_min + (lon_max - lon_min) * 0.35
    by0 = lat_min + (lat_max - lat_min) * 0.045
    bh = (lat_max - lat_min) * 0.010
    ax.add_patch(plt.Rectangle((bx0, by0), bar_deg, bh, fc="black", zorder=8))
    ax.add_patch(plt.Rectangle(
        (bx0 + bar_deg, by0), bar_deg, bh,
        fc="white", ec="black", lw=0.5, zorder=8,
    ))
    for label, xpos in [("0", bx0), ("7.5", bx0 + bar_deg), ("15 km", bx0 + 2 * bar_deg)]:
        ax.text(xpos, by0 - bh * 0.8, label, fontsize=7.5, ha="center", va="top", zorder=9)

    # ── North arrow (top-right) ───────────────────────────────────────────
    nx = lon_max - (lon_max - lon_min) * 0.055
    ny0 = lat_max - (lat_max - lat_min) * 0.16
    nlen = (lat_max - lat_min) * 0.08
    ax.annotate(
        "",
        xy=(nx, ny0 + nlen),
        xytext=(nx, ny0),
        arrowprops=dict(arrowstyle="-|>", color="black", lw=1.5, mutation_scale=14),
        zorder=8,
    )
    ax.text(
        nx, ny0 + nlen + (lat_max - lat_min) * 0.012,
        "N", fontsize=11, ha="center", va="bottom", fontweight="bold", zorder=9,
    )

    # ── Colourbar ─────────────────────────────────────────────────────────
    cbar = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.01, shrink=0.60, aspect=30)
    cbar.set_label("Kernel Density of Charging Piles\n(piles/km²)", fontsize=8.5)
    cbar.ax.tick_params(labelsize=8)

    # ── Axes clean-up ─────────────────────────────────────────────────────
    ax.set_xlim(lon_min, lon_max)
    ax.set_ylim(lat_min, lat_max)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)

    ax.set_title(
        f"Spatial Distribution of {n_station:,} Charging Stations in Shenzhen",
        fontsize=12, pad=8,
    )

    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_07_shenzhen_station_distribution_map.png", dpi=220, bbox_inches="tight")
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


def run_single_scenario(
    occupancy_change: float,
    dwell_cost_change: float = 0.0,
    n_iter: int = 1000,
) -> dict:
    baseline = load_baseline_data()

    peak_lambda = baseline["peak_lambda_rate"] * (1.0 + occupancy_change)
    offpeak_lambda = baseline["offpeak_lambda_rate"] * (1.0 + occupancy_change)
    dwell_cost = baseline["dwell_cost_per_minute"] * (1.0 + dwell_cost_change)

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
        q_peak.queue_waiting_time_minutes * baseline["peak_hours"]
        + q_offpeak.queue_waiting_time_minutes * baseline["offpeak_hours"]
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
        dwell_cost_per_minute=dwell_cost,
        service_fee_change=0.0,
        electricity_cost_change=0.0,
        n_iter=n_iter,
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
        "mean_dwell_penalty": mc.mean_dwell_penalty,
        "peak_utilization": mc.mean_peak_utilization,
        "peak_wait_minutes": mc.mean_peak_wait_minutes,
        "profits": np.array(mc.profits),
    }


def fig_monte_carlo_histogram() -> None:
    res = run_single_scenario(occupancy_change=0.0, dwell_cost_change=0.0)
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
        waits.append(min(float(q.queue_waiting_time_minutes), 120.0))  # cap display at 120 min
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
        dwell: float = 0.0,
        fixc: float = 0.0,
        kwh: float = 0.0,
    ) -> float:
        peak_lambda = b["peak_lambda_rate"] * (1.0 + occ)
        offpeak_lambda = b["offpeak_lambda_rate"] * (1.0 + occ)
        dwell_cost = b["dwell_cost_per_minute"] * (1.0 + dwell)
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
            dwell_cost_per_minute=dwell_cost,
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
        ("Dwell cost (c_dwell)",    dict(dwell=+0.2), dict(dwell=-0.2)),
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


def fig_dwell_penalty_response(n_iter: int = 1000) -> None:
    from data_processor import load_baseline_data as _load  # noqa: E402

    b = _load()

    # X-axis: demand multiplier relative to baseline λ
    demand_multipliers = np.linspace(0.5, 5.5, 40)
    dwell_cost_scenarios = [
        (0.005, "#2563eb", "c_dwell = 0.005 ¥/veh-min"),
        (0.010, "#b45309", "c_dwell = 0.010 ¥/veh-min (baseline)"),
        (0.020, "#dc2626", "c_dwell = 0.020 ¥/veh-min"),
    ]

    plt.figure(figsize=(9, 5))
    for dwell_cost, color, lbl in dwell_cost_scenarios:
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
                dwell_cost_per_minute=dwell_cost,
                n_iter=n_iter,
                seed=42,
            ).run()
            penalties.append(mc.mean_dwell_penalty)
        plt.plot(demand_multipliers, penalties, color=color, linewidth=2.2, label=lbl)

    plt.axvline(1.0, color="#6b7280", linestyle="--", linewidth=1.8, label="Baseline λ")
    plt.title("Dwell-Time Penalty Cost vs. Demand Multiplier")
    plt.xlabel("Demand multiplier (× baseline λ)")
    plt.ylabel("Expected dwell-time penalty cost (RMB/day)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT_DIR / "fig_06_dwell_penalty_response.png", dpi=180)
    plt.close()


def run_lightweight_validation(n_iter: int = 200) -> None:
    ensure_out_dir()
    baseline = load_baseline_data()
    session_duration = compute_session_duration()

    print("Lightweight validation:")
    print(f"  baseline mu={baseline['mu']:.4f}, lambda={baseline['lambda_rate']:.4f}, c={baseline['c']}")
    print(f"  session duration count={len(session_duration)}, mean={float(session_duration.mean()):.4f} h")

    fig_dwell_penalty_response(n_iter=n_iter)
    print(f"  Saved lightweight figure: {OUT_DIR / 'fig_06_dwell_penalty_response.png'}")


def main(skip_map: bool = False) -> None:
    ensure_out_dir()

    stats = descriptive_stats_table()
    print("Descriptive statistics saved:")
    print(stats.to_string(index=False))

    fig_charge_count_distribution()
    if not skip_map:
        fig_shenzhen_station_distribution_map()
    fig_service_duration_distribution()
    fig_monte_carlo_histogram()
    fig_queue_sensitivity_curve()
    fig_tornado_profit_sensitivity()
    fig_dwell_penalty_response()

    print(f"\nAll figures generated in: {OUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate report figures from project data.")
    parser.add_argument("--fast", action="store_true", help="Run a lightweight core validation and generate only fig_06.")
    parser.add_argument("--skip-map", action="store_true", help="Skip Shenzhen station distribution map generation.")
    parser.add_argument("--only-fig6", action="store_true", help="Generate only the dwell penalty response chart.")
    parser.add_argument("--n-iter", type=int, default=1000, help="Monte Carlo iterations for fig_06 and validation.")
    args = parser.parse_args()

    if args.fast:
        run_lightweight_validation(n_iter=args.n_iter)
    elif args.only_fig6:
        ensure_out_dir()
        fig_dwell_penalty_response(n_iter=args.n_iter)
        print(f"Saved figure: {OUT_DIR / 'fig_06_dwell_penalty_response.png'}")
    else:
        main(skip_map=args.skip_map)
