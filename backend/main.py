"""
main.py — FastAPI 主机与路由中枢
职责：接收前端请求 → 校验 → 调用排队模型 + 蒙特卡洛 → 返回 JSON 结果
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from data_processor import load_baseline_data
from queuing_model import QueuingSimulator
from monte_carlo import MonteCarloSimulator
from schemas import SimulationRequest, SimulationResponse

# ── 启动时预热数据缓存 ─────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    load_baseline_data()
    print("[INFO] 基准数据加载完毕，服务就绪。")
    yield


app = FastAPI(
    title="EV Charging Supply Chain Risk Simulator",
    description="从能源采购、站点容量到车队履约的充电供应链风险仿真 API（M/G/c + Monte Carlo）",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS：允许本地前端（5500 端口）访问 ──────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    return {"status": "ok", "message": "充电供应链风险仿真服务运行中"}


@app.post("/api/run-simulation", response_model=SimulationResponse)
def run_simulation(payload: SimulationRequest) -> SimulationResponse:
    """
    核心接口：接收用户参数 → 运行排队 + 蒙特卡洛 → 返回完整仿真结果。
    """
    baseline = load_baseline_data()

    # ── 1. 根据用户调参调整高峰/平峰到达率 λ ──────────────────────────────
    adj_peak_lambda = baseline["peak_lambda_rate"] * (1.0 + payload.occupancy_change)
    adj_offpeak_lambda = baseline["offpeak_lambda_rate"] * (1.0 + payload.occupancy_change)
    peak_hours = baseline["peak_hours"]
    offpeak_hours = baseline["offpeak_hours"]
    adj_lambda = (adj_peak_lambda * peak_hours + adj_offpeak_lambda * offpeak_hours) / 24.0
    adj_dwell_cost = baseline["dwell_cost_per_minute"] * (1.0 + payload.dwell_cost_change)

    # ── 2. 高峰/平峰分别计算 M/G/c（保留 M/M/c 基线）───────────────────────
    q_peak = QueuingSimulator(
        lam=adj_peak_lambda,
        mu=baseline["mu"],
        c=baseline["c"],
        service_time_cv=baseline["service_time_cv"],
    ).compute()
    q_offpeak = QueuingSimulator(
        lam=adj_offpeak_lambda,
        mu=baseline["mu"],
        c=baseline["c"],
        service_time_cv=baseline["service_time_cv"],
    ).compute()

    # 用时段加权的平均值保留现有字段兼容
    total_hours = peak_hours + offpeak_hours
    avg_utilization = (q_peak.rho * peak_hours + q_offpeak.rho * offpeak_hours) / total_hours
    avg_wait_minutes = (
        q_peak.queue_waiting_time_minutes * peak_hours
        + q_offpeak.queue_waiting_time_minutes * offpeak_hours
    ) / total_hours
    avg_wait_baseline = (
        q_peak.wq_mmc_minutes * peak_hours + q_offpeak.wq_mmc_minutes * offpeak_hours
    ) / total_hours
    avg_sojourn_minutes = (
        q_peak.dwell_time_minutes * peak_hours + q_offpeak.dwell_time_minutes * offpeak_hours
    ) / total_hours
    daily_sessions = adj_peak_lambda * peak_hours + adj_offpeak_lambda * offpeak_hours

    # ── 3. 蒙特卡洛财务仿真（双时段客流 + 双时段惩罚）──────────────────────
    mc = MonteCarloSimulator(
        peak_lambda_rate=adj_peak_lambda,
        offpeak_lambda_rate=adj_offpeak_lambda,
        peak_hours=peak_hours,
        offpeak_hours=offpeak_hours,
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
        dwell_cost_per_minute=adj_dwell_cost,
        service_fee_change=payload.service_fee_change,
        electricity_cost_change=payload.electricity_cost_change,
        n_iter=1000,
    )
    mc_result = mc.run()

    # ── 4. 打包返回 ───────────────────────────────────────────────────────
    return SimulationResponse(
        utilization=round(avg_utilization, 4),
        mean_wait_minutes=round(avg_wait_minutes, 2),
        mean_sojourn_minutes=round(avg_sojourn_minutes, 2),
        mean_wait_minutes_baseline=round(avg_wait_baseline, 2),
        mgc_correction_factor=round(q_peak.mgc_correction_factor, 4),
        daily_sessions=round(daily_sessions, 1),
        var_5pct=round(mc_result.var_5pct, 2),
        mean_profit=round(mc_result.mean_profit, 2),
        std_profit=round(mc_result.std_profit, 2),
        prob_loss=round(mc_result.prob_loss, 4),
        mean_dwell_penalty=round(mc_result.mean_dwell_penalty, 2),
        peak_utilization=round(mc_result.mean_peak_utilization, 4),
        peak_wait_minutes=round(mc_result.mean_peak_wait_minutes, 2),
        histogram_data=[round(p, 2) for p in mc_result.profits],
        lambda_rate=round(adj_lambda, 4),
        peak_lambda_rate=round(adj_peak_lambda, 4),
        offpeak_lambda_rate=round(adj_offpeak_lambda, 4),
        mu=round(baseline["mu"], 4),
        service_time_cv=round(baseline["service_time_cv"], 4),
        dwell_cost_per_minute=round(adj_dwell_cost, 3),
        c=baseline["c"],
    )
