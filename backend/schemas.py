"""
schemas.py — 接口安检员
职责：定义 FastAPI 请求与响应的 Pydantic 数据模型，确保数据格式合法。
"""

from pydantic import BaseModel, Field
from typing import Annotated


class SimulationRequest(BaseModel):
    """前端发来的用户调参请求。"""

    service_fee_change: Annotated[float, Field(
        ge=-0.9, le=2.0,
        description="服务费变动比例，如 -0.1 表示降低 10%"
    )] = 0.0

    electricity_cost_change: Annotated[float, Field(
        ge=-0.5, le=0.5,
        description="购电成本变动比例，如 0.1 表示上涨 10%"
    )] = 0.0

    occupancy_change: Annotated[float, Field(
        ge=-0.9, le=2.0,
        description="客流量变动比例，如 0.2 表示增加 20%"
    )] = 0.0

    wait_cost_change: Annotated[float, Field(
        ge=-0.9, le=2.0,
        description="等待惩罚成本变动比例，如 0.5 表示增加 50%"
    )] = 0.0


class SimulationResponse(BaseModel):
    """后端返回的仿真结果。"""

    # 排队模型指标
    utilization: float                 # 系统利用率 ρ
    mean_wait_minutes: float           # 纯排队等待时间（分钟，M/G/c 修正 Wq）
    mean_sojourn_minutes: float        # 总在站时长（分钟，W = Wq + 1/μ，含充电服务时间）
    mean_wait_minutes_baseline: float  # 纯排队等待时间（分钟，M/M/c 基线 Wq）
    mgc_correction_factor: float       # M/G/c 对 M/M/c 的修正系数
    daily_sessions: float              # 预计日服务次数

    # 蒙特卡洛财务指标
    var_5pct: float              # 5% VaR（日净利润，元）
    mean_profit: float           # 期望日净利润（元）
    std_profit: float            # 利润标准差（元）
    prob_loss: float             # 亏损概率（0~1）
    mean_wait_penalty: float     # 等待惩罚的期望成本（元/天）

    # 直方图原始数据（1000 个点）
    histogram_data: list[float]

    # 基准参数回显
    lambda_rate: float
    mu: float
    service_time_cv: float
    wait_cost_per_minute: float
    c: int
