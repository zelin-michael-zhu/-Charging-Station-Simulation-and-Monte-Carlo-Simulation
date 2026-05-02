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
    title="EV Charging Station Risk Simulator",
    description="充电站净利润风险仿真 API（M/G/c 修正 + Monte Carlo）",
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
    return {"status": "ok", "message": "充电站仿真服务运行中"}


@app.post("/api/run-simulation", response_model=SimulationResponse)
def run_simulation(payload: SimulationRequest) -> SimulationResponse:
    """
    核心接口：接收用户参数 → 运行排队 + 蒙特卡洛 → 返回完整仿真结果。
    """
    baseline = load_baseline_data()

    # ── 1. 根据用户调参调整到达率 λ ──────────────────────────────────────
    adj_lambda = baseline["lambda_rate"] * (1.0 + payload.occupancy_change)
    adj_wait_cost = baseline["wait_cost_per_minute"] * (1.0 + payload.wait_cost_change)

    # ── 2. M/G/c 排队模型（保留 M/M/c 基线）──────────────────────────────
    queuing = QueuingSimulator(
        lam=adj_lambda,
        mu=baseline["mu"],
        c=baseline["c"],
        service_time_cv=baseline["service_time_cv"],
    )
    q_result = queuing.compute()

    # ── 3. 蒙特卡洛财务仿真（使用 M/G/c 修正的总在站时长 W=Wq+1/μ）────────
    # 注：wq_minutes 是纯排队等待（低负载时≈0），w_mgc_minutes 含充电服务时间，
    #     是客户的真实时间成本，确保 wait_cost_change 滑块有效果。
    mc = MonteCarloSimulator(
        daily_sessions=q_result.daily_sessions,
        mean_kwh=baseline["mean_kwh"],
        std_kwh=baseline["std_kwh"],
        mean_e_price=baseline["mean_e_price"],
        mean_s_price=baseline["mean_s_price"],
        std_e_price=baseline["std_e_price"],
        std_s_price=baseline["std_s_price"],
        wholesale_price=baseline["wholesale_price"],
        daily_fixed_cost=baseline["daily_fixed_cost"],
        mean_wait_minutes=q_result.w_mgc_minutes,
        wait_cost_per_minute=adj_wait_cost,
        service_fee_change=payload.service_fee_change,
        electricity_cost_change=payload.electricity_cost_change,
        n_iter=1000,
    )
    mc_result = mc.run()

    # ── 4. 打包返回 ───────────────────────────────────────────────────────
    return SimulationResponse(
        utilization=round(q_result.rho, 4),
        mean_wait_minutes=round(q_result.wq_minutes, 2),
        mean_sojourn_minutes=round(q_result.w_mgc_minutes, 2),
        mean_wait_minutes_baseline=round(q_result.wq_mmc_minutes, 2),
        mgc_correction_factor=round(q_result.mgc_correction_factor, 4),
        daily_sessions=round(q_result.daily_sessions, 1),
        var_5pct=round(mc_result.var_5pct, 2),
        mean_profit=round(mc_result.mean_profit, 2),
        std_profit=round(mc_result.std_profit, 2),
        prob_loss=round(mc_result.prob_loss, 4),
        mean_wait_penalty=round(mc_result.mean_wait_penalty, 2),
        histogram_data=[round(p, 2) for p in mc_result.profits],
        lambda_rate=round(adj_lambda, 4),
        mu=round(baseline["mu"], 4),
        service_time_cv=round(baseline["service_time_cv"], 4),
        wait_cost_per_minute=round(adj_wait_cost, 3),
        c=baseline["c"],
    )
