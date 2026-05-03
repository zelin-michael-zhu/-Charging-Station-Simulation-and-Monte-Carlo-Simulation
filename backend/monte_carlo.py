"""
monte_carlo.py — 财务风险仿真器
职责：执行 1000 次净利润随机迭代，输出利润数组及 VaR 风险指标。
"""

import numpy as np
from dataclasses import dataclass

from queuing_model import QueuingSimulator


@dataclass
class MonteCarloResult:
    profits: list[float]   # 1000 次每日净利润（元）
    var_5pct: float        # 5% VaR（元）— 最坏 5% 情形下的日亏损下限
    mean_profit: float     # 均值（元/天）
    std_profit: float      # 标准差
    prob_loss: float       # 亏损概率（0~1）
    mean_wait_penalty: float  # 等待惩罚均值（元/天）
    mean_peak_utilization: float  # 高峰期平均利用率（1000次循环均值）
    mean_peak_wait_minutes: float  # 高峰期平均排队时间（分钟，Wq）


class MonteCarloSimulator:
    """
    基于 M/G/c 排队结果（总在站时长 W = Wq + 1/μ）与数据基准参数的蒙特卡洛财务仿真器。

    财务模型（单站·每日）：
        total_kwh    = sessions × kwh_per_session
        revenue      = total_kwh × (e_price + s_price_adj)     # 含客户侧电费+服务费
        cost         = total_kwh × wholesale_price + fixed_cost
        wait_penalty = sessions × W_mgc × wait_cost_per_minute  # M/G/c 总在站时长惩罚
        profit       = revenue - cost - wait_penalty
    """

    def __init__(
        self,
        peak_lambda_rate: float,
        offpeak_lambda_rate: float,
        peak_hours: float,
        offpeak_hours: float,
        mu: float,
        c: int,
        service_time_cv: float,
        mean_kwh: float,
        std_kwh: float,
        mean_e_price: float,
        mean_s_price: float,
        std_e_price: float,
        std_s_price: float,
        wholesale_price: float,
        daily_fixed_cost: float,
        wait_cost_per_minute: float,
        service_fee_change: float = 0.0,   # 服务费调整比例，如 -0.1 = -10%
        electricity_cost_change: float = 0.0,  # 购电成本调整比例
        n_iter: int = 1000,
        seed: int = 42,
    ):
        self.peak_lambda_rate     = max(peak_lambda_rate, 0.0)
        self.offpeak_lambda_rate  = max(offpeak_lambda_rate, 0.0)
        self.peak_hours           = max(peak_hours, 0.0)
        self.offpeak_hours        = max(offpeak_hours, 0.0)
        self.mu                   = mu
        self.c                    = c
        self.service_time_cv      = max(service_time_cv, 0.0)
        self.mean_kwh             = mean_kwh
        self.std_kwh              = std_kwh
        self.mean_e_price         = mean_e_price
        self.mean_s_price         = mean_s_price * (1.0 + service_fee_change)
        self.std_e_price          = std_e_price
        self.std_s_price          = std_s_price
        self.wholesale_price      = wholesale_price * (1.0 + electricity_cost_change)
        self.daily_fixed_cost     = daily_fixed_cost
        self.wait_cost_per_minute = max(wait_cost_per_minute, 0.0)
        self.n_iter               = n_iter
        self.rng                  = np.random.default_rng(seed)

    def run(self) -> MonteCarloResult:
        """执行蒙特卡洛模拟，返回 MonteCarloResult。"""
        n = self.n_iter

        # ── 随机采样 ─────────────────────────────────────────────────────────
        # 高峰4小时与平峰20小时分别抽样，合并为全天服务次数
        peak_sessions = self.rng.poisson(
            lam=self.peak_lambda_rate * self.peak_hours, size=n
        ).astype(float)
        offpeak_sessions = self.rng.poisson(
            lam=self.offpeak_lambda_rate * self.offpeak_hours, size=n
        ).astype(float)
        sessions = peak_sessions + offpeak_sessions

        # 每次循环分别代入高峰/平峰到达率计算排队时长，再分摊惩罚成本
        peak_wait_minutes = np.zeros(n, dtype=float)
        peak_utilization = np.zeros(n, dtype=float)
        peak_sojourn_minutes = np.zeros(n, dtype=float)
        offpeak_sojourn_minutes = np.zeros(n, dtype=float)

        for i in range(n):
            lam_peak_i = (peak_sessions[i] / self.peak_hours) if self.peak_hours > 0 else 0.0
            lam_off_i = (offpeak_sessions[i] / self.offpeak_hours) if self.offpeak_hours > 0 else 0.0

            q_peak = QueuingSimulator(
                lam=lam_peak_i,
                mu=self.mu,
                c=self.c,
                service_time_cv=self.service_time_cv,
            ).compute()
            q_off = QueuingSimulator(
                lam=lam_off_i,
                mu=self.mu,
                c=self.c,
                service_time_cv=self.service_time_cv,
            ).compute()

            peak_wait_minutes[i] = q_peak.wq_minutes
            peak_utilization[i] = q_peak.rho
            peak_sojourn_minutes[i] = q_peak.w_mgc_minutes
            offpeak_sojourn_minutes[i] = q_off.w_mgc_minutes

        # 单次充电电量（kWh）：正态分布，截断至 [1, 50]
        kwh = self.rng.normal(self.mean_kwh, self.std_kwh, size=n)
        kwh = np.clip(kwh, 1.0, 50.0)

        # 电价与服务费：正态分布，截断至合理范围
        e_price = self.rng.normal(self.mean_e_price, self.std_e_price * 0.3, size=n)
        e_price = np.clip(e_price, 0.3, 2.0)

        s_price = self.rng.normal(self.mean_s_price, self.std_s_price * 0.3, size=n)
        s_price = np.clip(s_price, 0.1, 2.0)

        # 购电批发价扰动（±10% 随机波动）
        wholesale = self.rng.normal(
            self.wholesale_price, self.wholesale_price * 0.10, size=n
        )
        wholesale = np.clip(wholesale, 0.2, 1.5)

        # ── 财务计算 ─────────────────────────────────────────────────────────
        total_kwh = sessions * kwh
        revenue   = total_kwh * (e_price + s_price)
        cost      = total_kwh * wholesale + self.daily_fixed_cost
        peak_penalty = peak_sessions * peak_sojourn_minutes * self.wait_cost_per_minute
        offpeak_penalty = offpeak_sessions * offpeak_sojourn_minutes * self.wait_cost_per_minute
        wait_penalty = peak_penalty + offpeak_penalty
        profits   = revenue - cost - wait_penalty

        var_5pct    = float(np.percentile(profits, 5))
        mean_profit = float(np.mean(profits))
        std_profit  = float(np.std(profits))
        prob_loss   = float(np.mean(profits < 0))
        mean_wait_penalty = float(np.mean(wait_penalty))
        mean_peak_utilization = float(np.mean(peak_utilization))
        mean_peak_wait_minutes = float(np.mean(peak_wait_minutes))

        return MonteCarloResult(
            profits=profits.tolist(),
            var_5pct=var_5pct,
            mean_profit=mean_profit,
            std_profit=std_profit,
            prob_loss=prob_loss,
            mean_wait_penalty=mean_wait_penalty,
            mean_peak_utilization=mean_peak_utilization,
            mean_peak_wait_minutes=mean_peak_wait_minutes,
        )
